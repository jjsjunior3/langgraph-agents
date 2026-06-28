import sys
import os
_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, ToolMessage
from state.agent_state import AgentState


class Agent:
    def __init__(self, model, tools, system: str = ""):
        self.system = system

        # Monta o grafo declarativamente
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_llm)
        graph.add_node("action", self.take_action)

        # Aresta condicional: se há tool_call → action, senão → END
        graph.add_conditional_edges(
            "llm",
            self.exists_action,
            {True: "action", False: END}
        )

        # Aresta fixa: após executar ação, volta pro LLM
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")

        self.graph = graph.compile()

        # Registra ferramentas e vincula ao modelo
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def exists_action(self, state: AgentState) -> bool:
        """Aresta condicional: verifica se o LLM quer chamar uma ferramenta."""
        last_message = state['messages'][-1]
        return len(last_message.tool_calls) > 0

    def call_llm(self, state: AgentState) -> dict:
        """Nó LLM: chama o modelo com o histórico de mensagens."""
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        response = self.model.invoke(messages)
        return {'messages': [response]}

    def take_action(self, state: AgentState) -> dict:
        """Nó Action: executa as ferramentas solicitadas pelo LLM."""
        tool_calls = state['messages'][-1].tool_calls
        results = []

        for tool_call in tool_calls:
            print(f"🔧 Chamando ferramenta: {tool_call['name']} | args: {tool_call['args']}")

            if tool_call['name'] not in self.tools:
                result = "Ferramenta não encontrada. Tente novamente."
            else:
                result = self.tools[tool_call['name']].invoke(tool_call['args'])

            results.append(ToolMessage(
                tool_call_id=tool_call['id'],
                name=tool_call['name'],
                content=str(result)
            ))

        print("✅ Retornando ao modelo...")
        return {'messages': results}