import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch
from agents.persistent_agent import criar_agente_persistente


def stream_pergunta(agent, pergunta: str, thread_id: str):
    """Executa uma pergunta com streaming e exibe cada nó."""
    print(f"\n📩 Pergunta: {pergunta}")
    print(f"🧵 Thread: {thread_id}")
    print("-" * 50)

    thread = {"configurable": {"thread_id": thread_id}}
    messages = [HumanMessage(content=pergunta)]
    resposta_final = ""

    for event in agent.graph.stream({"messages": messages}, thread):
        for no, dados in event.items():
            if no == "llm":
                conteudo = dados['messages'][-1].content
                if conteudo:
                    resposta_final = conteudo
                    print(f"🤖 [{no}]: {conteudo[:300]}...")
            elif no == "action":
                print(f"⚙️  [{no}]: ferramenta executada")

    return resposta_final


def demo_persistencia():
    """
    Demonstra como o thread_id mantém contexto entre perguntas.
    """
    tavily = TavilySearch(max_results=3)
    agent = criar_agente_persistente(tools=[tavily])

    print("\n" + "="*60)
    print("🧠 DEMO: PERSISTÊNCIA COM THREAD")
    print("="*60)

    # Thread 1 — conversa com contexto acumulado
    stream_pergunta(agent, "Como estava o tempo em São Paulo ontem?", thread_id="1")
    stream_pergunta(agent, "E no Rio de Janeiro?", thread_id="1")
    stream_pergunta(agent, "Qual das duas cidades estava mais quente?", thread_id="1")

    # Thread 2 — nova sessão, sem contexto
    print("\n" + "="*60)
    print("🔄 NOVA THREAD — sem contexto anterior")
    print("="*60)
    stream_pergunta(agent, "Qual estava mais quente?", thread_id="2")


if __name__ == "__main__":
    demo_persistencia()