import sys
import os
_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from langgraph.graph import StateGraph, END
from multiagents.state import AgentState
from multiagents.nodes import (
    plan_node,
    research_plan_node,
    generation_node,
    reflection_node,
    research_critique_node,
    should_continue,
)


def build_graph():
    """Monta e compila o grafo de multiagentes."""
    builder = StateGraph(AgentState)

    # Nós
    builder.add_node("planner", plan_node)
    builder.add_node("research_plan", research_plan_node)
    builder.add_node("generate", generation_node)
    builder.add_node("reflect", reflection_node)
    builder.add_node("research_critique", research_critique_node)

    # Ponto de entrada
    builder.set_entry_point("planner")

    # Arestas fixas
    builder.add_edge("planner", "research_plan")
    builder.add_edge("research_plan", "generate")
    builder.add_edge("reflect", "research_critique")
    builder.add_edge("research_critique", "generate")

    # Aresta condicional: gerar → continuar ou encerrar?
    builder.add_conditional_edges(
        "generate",
        should_continue,
        {END: END, "reflect": "reflect"}
    )

    return builder.compile()