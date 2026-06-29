import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from multiagents.graph import build_graph


def demo_stream(tema: str, max_revisoes: int = 2, thread_id: str = "1"):
    """Modo stream — vê cada agente trabalhando em tempo real."""
    print("\n" + "="*60)
    print(f"🎭 PIPELINE MULTIAGENTES — STREAM")
    print(f"📝 Tema: {tema}")
    print(f"🔄 Revisões: {max_revisoes}")
    print("="*60)

    graph = build_graph(use_memory=True)
    thread = {"configurable": {"thread_id": thread_id}}

    for step in graph.stream({
        "task": tema,
        "max_revisions": max_revisoes,
        "revision_number": 1,
        "content": [],
        "plan": "",
        "draft": "",
        "critique": "",
    }, thread):
        no = list(step.keys())[0]
        dados = step[no]

        if no == "planner":
            print(f"\n📋 [{no}] Plano criado ({len(dados.get('plan',''))} chars)")
        elif no == "research_plan":
            print(f"\n🔍 [{no}] {len(dados.get('content',[]))} fontes coletadas")
        elif no == "generate":
            rev = dados.get('revision_number', '?')
            print(f"\n✍️  [{no}] Rascunho gerado (revisão {rev})")
        elif no == "reflect":
            print(f"\n🔎 [{no}] Crítica gerada ({len(dados.get('critique',''))} chars)")
        elif no == "research_critique":
            print(f"\n🔍 [{no}] Fontes adicionais coletadas")


def demo_invoke(tema: str, max_revisoes: int = 2):
    """Modo invoke — resultado final direto."""
    print("\n" + "="*60)
    print(f"🎭 PIPELINE MULTIAGENTES — INVOKE")
    print(f"📝 Tema: {tema}")
    print("="*60)

    graph = build_graph(use_memory=False)

    resultado = graph.invoke({
        "task": tema,
        "max_revisions": max_revisoes,
        "revision_number": 1,
        "content": [],
        "plan": "",
        "draft": "",
        "critique": "",
    })

    print("\n📋 PLANO:")
    print(resultado["plan"][:500] + "...")

    print("\n✍️  ENSAIO FINAL:")
    print(resultado["draft"])

    print("\n🔍 ÚLTIMA CRÍTICA:")
    print(resultado["critique"][:500] + "...")

    return resultado


def visualizar_grafo():
    graph = build_graph(use_memory=False)
    print("\n📊 GRAFO (Mermaid):")
    print("-"*40)
    print(graph.get_graph().draw_mermaid())
    print("Cole em https://mermaid.live")


def main():
    # Escolha o modo:
    visualizar_grafo()

    # Stream — vê cada agente em tempo real
    demo_stream(
        tema="Como a inteligência artificial pode melhorar a gestão escolar?",
        max_revisoes=2,
        thread_id="1"
    )

    # Invoke — só o resultado final
    # demo_invoke(
    #     tema="O futuro da IA na educação",
    #     max_revisoes=1
    # )


if __name__ == "__main__":
    main()