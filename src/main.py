import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from multiagents.graph import build_graph


def demo_multiagentes():
    print("\n" + "="*60)
    print("🎭 DEMO: PIPELINE DE MULTIAGENTES")
    print("="*60)

    graph = build_graph()

    # Visualiza o grafo
    print("\n📊 GRAFO (Mermaid):")
    print(graph.get_graph().draw_mermaid())
    print("Cole em https://mermaid.live\n")

    # Executa o pipeline
    tema = "Inteligência Artificial na Educação"
    print(f"📝 Tema: {tema}")
    print(f"🔄 Máximo de revisões: 2\n")

    resultado = graph.invoke({
        "task": tema,
        "max_revisions": 2,
        "revision_number": 1,
        "content": [],
        "plan": "",
        "draft": "",
        "critique": "",
    })

    print("\n" + "="*60)
    print("📋 PLANO:")
    print(resultado["plan"])

    print("\n" + "="*60)
    print("✍️  ENSAIO FINAL:")
    print(resultado["draft"])

    print("\n" + "="*60)
    print("🔍 CRÍTICA:")
    print(resultado["critique"])


if __name__ == "__main__":
    demo_multiagentes()