import sys
import os
_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from multiagents.state import AgentState
from multiagents.nodes import (
    plan_node,
    research_plan_node,
    generation_node,
    reflection_node,
    research_critique_node,
    should_continue,
)


def build_graph(use_memory: bool = True):
    """
    Monta e compila o grafo de multiagentes.
    use_memory=True  → persiste execuções no SQLite
    use_memory=False → execução sem memória (mais rápido para testes)
    """
    builder = StateGraph(AgentState)

    # Nós
    builder.add_node("planner", plan_node)
    builder.add_node("research_plan", research_plan_node)
    builder.add_node("generate", generation_node)
    builder.add_node("reflect", reflection_node)
    builder.add_node("research_critique", research_critique_node)

    # Ponto de entrada
    builder.set_entry_point("planner")

    # Aresta condicional: generate → END ou reflect
    builder.add_conditional_edges(
        "generate",
        should_continue,
        {END: END, "reflect": "reflect"}
    )

    # Arestas fixas
    builder.add_edge("planner", "research_plan")
    builder.add_edge("research_plan", "generate")
    builder.add_edge("reflect", "research_critique")
    builder.add_edge("research_critique", "generate")

    # Checkpointer opcional
    if use_memory:
        db_path = os.path.join(_SRC, "data", "checkpoints_multiagent.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        memory = SqliteSaver(conn)
        return builder.compile(checkpointer=memory)

    return builder.compile()