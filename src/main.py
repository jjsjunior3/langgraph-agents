import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

import uuid
from langchain_core.messages import HumanMessage, AIMessage
from langchain_tavily import TavilySearch
from agents.hitl_agent import criar_hitl_agent


def demo_aprovacao_humana():
    print("\n" + "="*60)
    print("🧑‍💻 DEMO: HUMAN IN THE LOOP — Aprovação Humana")
    print("="*60)

    tavily = TavilySearch(max_results=3)
    agent = criar_hitl_agent(tools=[tavily])

    thread_id = str(uuid.uuid4())
    thread = {"configurable": {"thread_id": thread_id}}
    print(f"🧵 Thread ID: {thread_id}\n")

    pergunta = "Como está o tempo em São Paulo hoje?"
    messages = [HumanMessage(content=pergunta)]

    # ─── Etapa 1: executa até o ponto de pausa ───────────
    print("📍 ETAPA 1 — Agente pensando...\n")
    for event in agent.graph.stream({"messages": messages}, thread):
        # event é um dict: {nome_do_no: dados}
        if not isinstance(event, dict):
            continue
        for no, dados in event.items():
            if not isinstance(dados, dict):
                continue
            for msg in dados.get("messages", []):
                if isinstance(msg, AIMessage) and msg.content:
                    print(f"🤖 [{no}]: {msg.content[:200]}")
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"🔍 Quer chamar: {tc['name']} | args: {tc['args']}")

    # ─── Etapa 2: intervenção humana ─────────────────────
    current_state = agent.graph.get_state(thread)
    last_message = current_state.values["messages"][-1]

    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        print("\n⏸️  AGENTE PAUSADO — Intervenção humana necessária")
        print(f"   Ferramenta : {last_message.tool_calls[0]['name']}")
        print(f"   Argumentos : {last_message.tool_calls[0]['args']}")

        aprovacao = input("\n✋ Deseja continuar? (sim/não): ").strip().lower()

        if aprovacao == "sim":
            print("\n📍 ETAPA 2 — Retomando execução...\n")
            for event in agent.graph.stream(None, thread):
                if not isinstance(event, dict):
                    continue
                for no, dados in event.items():
                    if not isinstance(dados, dict):
                        continue
                    for msg in dados.get("messages", []):
                        if isinstance(msg, AIMessage) and msg.content:
                            print(f"\n🎯 RESPOSTA FINAL:\n{msg.content}")
        else:
            print("\n❌ Ação cancelada pelo usuário.")
    else:
        print("\n⚠️  Agente não gerou tool_call. Revise o prompt.")


if __name__ == "__main__":
    demo_aprovacao_humana()