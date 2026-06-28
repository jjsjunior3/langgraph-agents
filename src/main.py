import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from langchain_core.messages import HumanMessage
from config.settings import llm, tavily_tool
from agents.langgraph_agent import Agent
from prompts.pesquisa_prompt import PROMPT_PESQUISA


def visualizar_grafo(agent: Agent):
    print("\n📊 GRAFO DO AGENTE (Mermaid):")
    print("-" * 40)
    print(agent.graph.get_graph().draw_mermaid())
    print("-" * 40)
    print("💡 Cole em https://mermaid.live para visualizar\n")


def testar_invoke(agent: Agent):
    """Teste simples com invoke."""
    print("\n🔵 MODO INVOKE")
    print("=" * 60)
    pergunta = "Como está o tempo em São Paulo hoje?"
    print(f"Pergunta: {pergunta}\n")
    result = agent.graph.invoke({
        "messages": [HumanMessage(content=pergunta)]
    })
    print(f"🎯 RESPOSTA: {result['messages'][-1].content}")


def testar_paralelo(agent: Agent):
    """Chamada paralela — duas cidades ao mesmo tempo."""
    print("\n🟡 CHAMADA PARALELA")
    print("=" * 60)
    pergunta = "Como está o tempo em São Paulo e no Rio de Janeiro hoje?"
    print(f"Pergunta: {pergunta}\n")

    result = agent.graph.invoke({
        "messages": [HumanMessage(content=pergunta)]
    })
    print(f"🎯 RESPOSTA: {result['messages'][-1].content}")


def testar_sequencial(agent: Agent):
    """Chamada sequencial — segunda busca depende da primeira."""
    print("\n🔴 CHAMADA SEQUENCIAL (múltiplas buscas dependentes)")
    print("=" * 60)

    pergunta = (
        "Qual país sediou a Copa do Mundo de futebol em 1998? "
        "Quem foi o campeão e qual o placar da final? "
        "Qual era o PIB desse país no ano da Copa e qual é o PIB atual (2023 ou 2024)? "
        "Qual a capital desse país e qual sua moeda atual? "
        "Responda a cada pergunta separadamente."
    )
    print(f"Pergunta: {pergunta}\n")

    current_state = {}
    for step in agent.graph.stream({"messages": [HumanMessage(content=pergunta)]}):
        current_state.update(step)
        no = list(step.keys())[0]
        print(f"📍 Nó: [{no}]")

        msgs = step[no].get("messages", [])
        for msg in msgs:
            conteudo = str(msg.content)[:150]
            print(f"   └─ {type(msg).__name__}: {conteudo}...")
        print("---")

    if 'llm' in current_state:
        print(f"\n🎯 RESPOSTA FINAL:\n{current_state['llm']['messages'][-1].content}")


def iniciar_conversacao(agent: Agent):
    """Loop interativo — agente de pesquisa geral."""
    print("\n💬 AGENTE DE PESQUISA INTERATIVO")
    print("Digite sua pergunta ou 'sair' para encerrar.")
    print("*" * 50)

    while True:
        user_input = input("\nVocê: ").strip()

        if user_input.lower() == "sair":
            print("Agente: Encerrando. Até logo!")
            break

        print("Agente: Pensando e buscando...\n")
        try:
            current_state = {}
            for step in agent.graph.stream({
                "messages": [HumanMessage(content=user_input)]
            }):
                current_state.update(step)

            if 'llm' in current_state and current_state['llm']['messages']:
                resposta = current_state['llm']['messages'][-1].content
                print(f"Agente: {resposta}")
            else:
                print("Agente: Não consegui obter uma resposta.")

        except Exception as e:
            print(f"Agente: Ocorreu um erro: {e}")
            print("Tente novamente ou digite 'sair'.")

    print("\n--- Conversa Encerrada ---")


def main():
    agent = Agent(model=llm, tools=[tavily_tool], system=PROMPT_PESQUISA)

    # Descomente o modo que quiser testar:
    visualizar_grafo(agent)
    testar_invoke(agent)
    testar_paralelo(agent)
    testar_sequencial(agent)
    # iniciar_conversacao(agent)


if __name__ == "__main__":
    main()