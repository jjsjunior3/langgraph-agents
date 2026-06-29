import sys
import os
import json
import re

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


# ─── Helper: gera queries com retry e fallback ────────────

def _gerar_queries(prompt_sistema: str, conteudo: str) -> list[str]:
    """
    Gera queries com retry e fallback para evitar JSON truncado.

    Tentativa 1: with_structured_output (ideal)
    Tentativa 2: prompt manual com regex (fallback)
    Tentativa 3: usa o próprio conteúdo como query (último recurso)
    """
    # Tentativa 1: with_structured_output
    try:
        queries = llm.with_structured_output(Queries).invoke([
            SystemMessage(content=prompt_sistema),
            HumanMessage(content=conteudo)
        ])
        return queries.queries
    except Exception:
        pass

    # Tentativa 2: prompt manual pedindo JSON
    try:
        response = llm.invoke([
            SystemMessage(
                content=prompt_sistema +
                '\nResponda APENAS com JSON válido no formato: {"queries": ["query1", "query2", "query3"]}'
            ),
            HumanMessage(content=conteudo)
        ])
        texto = response.content
        match = re.search(r'\{.*\}', texto, re.DOTALL)
        if match:
            dados = json.loads(match.group())
            return dados.get("queries", [])
    except Exception:
        pass

    # Tentativa 3: fallback com o próprio conteúdo
    return [conteudo[:100]]


# ─── Nó 1: Planejador ─────────────────────────────────────

def plan_node(state: AgentState) -> dict:
    """
    Recebe a tarefa e cria um esboço estruturado.
    Lê:    task
    Escreve: plan
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
    Lê:    task, content
    Escreve: content
    """
    queries = _gerar_queries(RESEARCH_PLAN_PROMPT, state['task'])
    content = list(state.get('content') or [])

    for q in queries:
        print(f"  🔍 Pesquisando: {q}")
        try:
            response = tavily.search(query=q, max_results=2)
            for r in response['results']:
                content.append(r['content'])
        except Exception as e:
            print(f"  ⚠️  Erro na busca: {e}")

    return {"content": content}


# ─── Nó 3: Escritor ───────────────────────────────────────

def generation_node(state: AgentState) -> dict:
    """
    Escreve o ensaio com base no plano e no conteúdo pesquisado.
    Lê:    task, plan, content, revision_number
    Escreve: draft, revision_number
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
    Lê:    draft
    Escreve: critique
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
    Gera queries com base na crítica e busca mais conteúdo no Tavily.
    Lê:    critique, content
    Escreve: content
    """
    queries = _gerar_queries(RESEARCH_CRITIQUE_PROMPT, state['critique'])
    content = list(state.get('content') or [])

    for q in queries:
        print(f"  🔍 Pesquisando (revisão): {q}")
        try:
            response = tavily.search(query=q, max_results=2)
            for r in response['results']:
                content.append(r['content'])
        except Exception as e:
            print(f"  ⚠️  Erro na busca: {e}")

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