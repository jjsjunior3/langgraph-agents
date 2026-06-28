import os
from dotenv import load_dotenv
from tavily import TavilyClient
from ddgs import DDGS

load_dotenv()

# ─── Tavily (busca agêntica) ───────────────────────────────

_tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


def busca_agêntica(query: str) -> str:
    """
    Busca agêntica via Tavily.
    Retorna uma resposta direta, já processada — ideal para agentes.
    """
    result = _tavily_client.search(query, include_answer=True)
    return result.get("answer", "Nenhuma resposta encontrada.")


def busca_agêntica_completa(query: str, max_results: int = 4) -> list[dict]:
    """
    Busca agêntica via Tavily com resultados completos (url, título, conteúdo).
    """
    result = _tavily_client.search(query, include_answer=True)
    return result.get("results", [])


# ─── DuckDuckGo (busca regular) ───────────────────────────

_ddg = DDGS()


def busca_regular(query: str, max_results: int = 6) -> list[str]:
    """
    Busca regular via DuckDuckGo.
    Retorna lista de URLs — precisa de scraping para extrair conteúdo.
    """
    try:
        results = _ddg.text(query, max_results=max_results)
        return [item["href"] for item in results]
    except Exception as e:
        return [f"Erro na busca: {e}"]