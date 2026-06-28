import sys
import os
_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import sqlite3
import uuid
from datetime import date

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from state.agent_state import AgentState
from config.settings import MODEL

load_dotenv()


def build_prompt() -> str:
    current_date = date.today().strftime("%d/%m/%Y")
    return f"""Você é um assistente de pesquisa inteligente e altamente atualizado.
A data atual é {current_date}.
Ao buscar sobre o tempo ou eventos que se referem a "hoje" ou "agora",
inclua a data atual {current_date} na sua consulta.
Use o mecanismo de busca para procurar informações.
Responda sempre em português."""


class HITLAgent:
    def __init__(self, model, tools, checkpointer, system: str = ""):
        self.system = system

        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_llm)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm",
            self.exists_action,
            {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")

        self.graph = graph.compile(
            checkpointer=checkpointer,
            interrupt_before=["action"]
        )
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def exists_action(self, state: AgentState) -> bool:
        return len(state['messages'][-1].tool_calls) > 0

    def call_llm(self, state: AgentState) -> dict:
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        response = self.model.invoke(messages)
        return {'messages': [response]}

    def take_action(self, state: AgentState) -> dict:
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f"🔧 Executando: {t['name']} | args: {t['args']}")
            result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(
                tool_call_id=t['id'],
                name=t['name'],
                content=str(result)
            ))
        print("✅ Retornando ao modelo...")
        return {'messages': results}

    def injetar_resposta(self, thread: dict, resposta: str) -> str:
        """
        Injeta uma resposta manual no estado do agente,
        substituindo o que ele planejava buscar/responder.
        Retorna a resposta injetada como confirmação.
        """
        snapshot = self.graph.get_state(thread)
        if not snapshot:
            return "❌ Snapshot não encontrado."

        # Cria a mensagem injetada
        mensagem_injetada = AIMessage(
            content=resposta,
            id=str(uuid.uuid4())
        )

        # Modifica o estado substituindo a última AIMessage
        estado_modificado = snapshot.values.copy()
        msgs = estado_modificado.get("messages", [])

        substituiu = False
        for i, msg in enumerate(msgs):
            if isinstance(msg, AIMessage):
                msgs[i] = mensagem_injetada
                substituiu = True
                break

        if not substituiu:
            msgs.append(mensagem_injetada)

        estado_modificado["messages"] = msgs

        # Atualiza o estado do grafo
        self.graph.update_state(thread, estado_modificado)
        return resposta


def criar_hitl_agent(tools: list) -> HITLAgent:
    db_path = os.path.join(_SRC, "data", "checkpoints_hitl.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)

    model = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model=MODEL,
        temperature=0,
    )

    return HITLAgent(
        model=model,
        tools=tools,
        checkpointer=memory,
        system=build_prompt(),
    )