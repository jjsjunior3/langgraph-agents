import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

import uuid
from langchain_core.messages import HumanMessage, AIMessage
from langchain_tavily import TavilySearch
from agents.hitl_agent import criar_hitl_agent


def executar_ate_pausa(agent, mensagens, thread):
    """Roda o agente até o interrupt_before e retorna True se pausou."""
    pausou = False
    for event in agent.graph.stream({"messages": mensagens}, thread):
        if not isinstance(event, dict):
            continue
        for no, dados in event.items():
            if not isinstance(dados, dict):
                continue
            for msg in dados.get("messages", []):
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"🔍 Quer chamar: {tc['name']}")
                        print(f"   Args: {tc['args']}")
                        pausou = True
    return pausou


def demo_aprovacao(agent):
    """Fluxo 1: humano aprova a ação."""
    print("\n" + "="*60)
    print("✅ DEMO 1 — Aprovação humana")
    print("="*60)

    thread = {"configurable": {"thread_id": str(uuid.uuid4())}}
    msgs = [HumanMessage(content="Como está o tempo em São Paulo hoje?")]

    pausou = executar_ate_pausa(agent, msgs, thread)

    if pausou:
        print("\n⏸️  PAUSADO — aguardando aprovação")
        resp = input("✋ Continuar? (sim/não): ").strip().lower()
        if resp == "sim":
            for event in agent.graph.stream(None, thread):
                if not isinstance(event, dict):
                    continue
                for no, dados in event.items():
                    if not isinstance(dados, dict):
                        continue
                    for msg in dados.get("messages", []):
                        if isinstance(msg, AIMessage) and msg.content:
                            print(f"\n🎯 RESPOSTA: {msg.content}")
        else:
            print("❌ Ação cancelada.")


def demo_injecao(agent):
    """Fluxo 2: humano injeta resposta manual."""
    print("\n" + "="*60)
    print("💉 DEMO 2 — Injeção manual de resposta")
    print("="*60)

    thread = {"configurable": {"thread_id": str(uuid.uuid4())}}
    msgs = [HumanMessage(content="Qual a distância entre Rio de Janeiro e Tóquio?")]

    pausou = executar_ate_pausa(agent, msgs, thread)

    if pausou:
        print("\n⏸️  PAUSADO — agente ia buscar na web")
        print("💡 Vamos injetar uma resposta manual em vez de deixar o agente buscar\n")

        resposta_manual = input("Digite a resposta que o agente deve dar: ").strip()
        if not resposta_manual:
            resposta_manual = "A distância entre Rio de Janeiro e Tóquio é de aproximadamente 450 km. (Dados fornecidos manualmente!)"

        resultado = agent.injetar_resposta(thread, resposta_manual)
        print(f"\n🎯 RESPOSTA INJETADA:\n{resultado}")
        print("\n✅ Estado do agente atualizado com a resposta manual.")


def main():
    tavily = TavilySearch(max_results=3)
    agent = criar_hitl_agent(tools=[tavily])

    demo_aprovacao(agent)
    demo_injecao(agent)


if __name__ == "__main__":
    main()