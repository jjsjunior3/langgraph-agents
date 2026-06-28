import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from tools.busca import busca_agêntica, busca_regular
from tools.scraping import pesquisar_restaurantes


def demo_busca_agêntica():
    print("\n🤖 BUSCA AGÊNTICA (Tavily)")
    print("=" * 60)
    query = "O que são multiagentes de Inteligência Artificial?"
    print(f"Query: {query}\n")
    from tools.busca import busca_agêntica
    print(f"Resposta: {busca_agêntica(query)}")


def demo_busca_regular():
    print("\n🔍 BUSCA REGULAR (DuckDuckGo)")
    print("=" * 60)
    from tools.busca import busca_regular
    cidade = "Belém"
    query = f"5 principais restaurantes em {cidade} TripAdvisor avaliação preço"
    print(f"Buscando restaurantes em {cidade}...\n")
    links = busca_regular(query)
    for i, link in enumerate(links, 1):
        print(f"  {i}. {link}")
    print("\n⚠️  Apenas URLs — sem conteúdo extraído.")


def demo_scraping():
    print("\n🕷️  PIPELINE COMPLETO (Tavily + Selenium + BeautifulSoup)")
    print("=" * 60)
    cidade = "Belém do Pará"
    restaurantes = pesquisar_restaurantes(cidade, top_n=5)

    if restaurantes:
        print(f"\n🍽️  Top restaurantes em {cidade}:\n")
        for i, r in enumerate(restaurantes, 1):
            print(f"--- #{i} {r['Nome']} ---")
            print(f"  ⭐ Avaliação : {r['Avaliação']}")
            print(f"  💬 Reviews   : {r['Reviews']}")
            print(f"  💰 Preço     : {r['Preço']}")
            print(f"  🍴 Culinária : {r['Culinária']}")
            print(f"  🔗 Link      : {r['Link']}")
            print()
    else:
        print("⚠️  Nenhum restaurante extraído.")
        print("💡 O TripAdvisor pode ter bloqueado o scraping.")
        print("   Isso é normal — sites protegem seus dados.")


def main():
    demo_busca_agêntica()
    demo_busca_regular()
    demo_scraping()  # pode comentar se o TripAdvisor bloquear


if __name__ == "__main__":
    main()