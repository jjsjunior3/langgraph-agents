import sys
import os
_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from langgraph.graph import END
from tavily import TavilyClient
from dotenv import load_dotenv

from multiagents.state import AgentState
from multiagents.prompts import (
    PLAN_PROMPT,
    WRITER_PROMPT,
    REFLECTION_PROMPT,
    RESEARCH_PLAN_PROMPT,
    RESEARCH_CRITIQUE_PROMPT,
)
from config.settings import llm

load_dotenv()

# Cliente Tavily direto (mais controle sobre resultados)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# ─── Modelo de saída estruturada ──────────────────────────

class Queries(BaseModel):
    queries: list[str]


# ─── Nó 1: Planejador ─────────────────────────────────────

def plan_node(state: AgentState) -> dict:
    """
    Recebe a tarefa e cria um esboço estruturado.
    Escreve em: plan
    """
    messages = [
        SystemMessage(content=PLAN_PROMPT),
        HumanMessage(content=state['task'])
    ]
    response = llm.invoke(messages)
    return {"plan": response.content}


# ─── Nó 2: Pesquisador (planejamento) ─────────────────────

def research_plan_node(state: AgentState) -> dict:
    """
    Gera queries com base na tarefa e busca conteúdo no Tavily.
    Escreve em: content
    """
    queries = llm.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_PLAN_PROMPT),
        HumanMessage(content=state['task'])
    ])

    content = list(state.get('content') or [])

    for q in queries.queries:
        print(f"  🔍 Pesquisando: {q}")
        response = tavily.search(query=q, max_results=2)
        for r in response['results']:
            content.append(r['content'])

    return {"content": content}


# ─── Nó 3: Escritor ───────────────────────────────────────

def generation_node(state: AgentState) -> dict:
    """
    Escreve o ensaio com base no plano e no conteúdo pesquisado.
    Escreve em: draft, revision_number
    """
    content = "\n\n".join(state.get('content') or [])

    user_message = HumanMessage(
        content=f"{state['task']}\n\nEsboço:\n\n{state['plan']}"
    )

    messages = [
        SystemMessage(content=WRITER_PROMPT.format(content=content)),
        user_message
    ]

    response = llm.invoke(messages)

    return {
        "draft": response.content,
        "revision_number": state.get("revision_number", 1) + 1,
    }


# ─── Nó 4: Crítico (Reflexão) ─────────────────────────────

def reflection_node(state: AgentState) -> dict:
    """
    Analisa o rascunho e gera críticas e recomendações.
    Escreve em: critique
    """
    messages = [
        SystemMessage(content=REFLECTION_PROMPT),
        HumanMessage(content=state['draft'])
    ]
    response = llm.invoke(messages)
    return {"critique": response.content}


# ─── Nó 5: Pesquisador (revisão) ──────────────────────────

def research_critique_node(state: AgentState) -> dict:
    """
    Gera queries com base na crítica e busca mais conteúdo.
    Escreve em: content
    """
    queries = llm.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_CRITIQUE_PROMPT),
        HumanMessage(content=state['critique'])
    ])

    content = list(state.get('content') or [])

    for q in queries.queries:
        print(f"  🔍 Pesquisando (revisão): {q}")
        response = tavily.search(query=q, max_results=2)
        for r in response['results']:
            content.append(r['content'])

    return {"content": content}


# ─── Aresta condicional ────────────────────────────────────

def should_continue(state: AgentState) -> str:
    """
    Decide se o pipeline continua revisando ou encerra.
    """
    if state["revision_number"] > state["max_revisions"]:
        print(f"  ✅ Revisões concluídas ({state['revision_number']-1}/{state['max_revisions']})")
        return END
    print(f"  🔄 Revisão {state['revision_number']}/{state['max_revisions']}")
    return "reflect"