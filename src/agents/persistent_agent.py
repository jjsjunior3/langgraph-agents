import sys
import os
_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import sqlite3
import operator
from typing import Annotated

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict

from config.settings import MODEL
from prompts.pesquisa_prompt import PROMPT_PESQUISA


# ─── Estado ───────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


# ─── Agente com memória ───────────────────────────────────

class PersistentAgent:
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

        # Checkpointer injeta a memória no grafo
        self.graph = graph.compile(checkpointer=checkpointer)
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
            print(f"🔧 Ferramenta: {t['name']} | args: {t['args']}")
            result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(
                tool_call_id=t['id'],
                name=t['name'],
                content=str(result)
            ))
        print("✅ Retornando ao modelo...")
        return {'messages': results}


# ─── Factory: cria agente com SQLite ─────────────────────

def criar_agente_persistente(tools: list) -> PersistentAgent:
    """
    Cria um agente com memória persistida em SQLite.
    O banco fica em src/data/checkpoints.db
    """
    db_path = os.path.join(_SRC, "data", "checkpoints.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)

    model = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model=MODEL,
        temperature=0,
    )

    return PersistentAgent(
        model=model,
        tools=tools,
        checkpointer=memory,
        system=PROMPT_PESQUISA,
    )