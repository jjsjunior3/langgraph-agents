import os
import re
from dotenv import load_dotenv
from tavily import TavilyClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

load_dotenv()

_tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


# ─── Passo 1: Tavily encontra a URL ───────────────────────

def buscar_url_tripadvisor(cidade: str) -> str | None:
    """
    Usa o Tavily para encontrar a URL do TripAdvisor
    com os melhores restaurantes da cidade.
    """
    query = (
        f"restaurantes em {cidade} tripadvisor "
        f"com maior quantidade de reviews e faixa de preço"
    )
    print(f"🔍 Buscando URL do TripAdvisor para: {cidade}...")

    try:
        results = _tavily_client.search(query=query, max_results=5)

        for result in results.get("results", []):
            url = result["url"]
            if "tripadvisor.com" in url or "tripadvisor.com.br" in url:
                # Remove parâmetro de paginação da URL
                url_limpa = re.sub(r'-o\d+-', '-', url)
                print(f"✅ URL encontrada: {url_limpa}")
                return url_limpa

        print("⚠️  Nenhuma URL do TripAdvisor encontrada.")
        return None

    except Exception as e:
        print(f"❌ Erro na busca Tavily: {e}")
        return None


# ─── Passo 2: Selenium acessa e renderiza a página ────────

def acessar_pagina(url: str) -> BeautifulSoup | None:
    """
    Usa Selenium headless para carregar a página
    e retorna o HTML parseado com BeautifulSoup.
    """
    if not url:
        print("❌ URL vazia — abortando scraping.")
        return None

    print(f"\n🌐 Acessando página com Selenium: {url}")

    try:
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        )

        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)

        try:
            driver.get(url)
            driver.implicitly_wait(10)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            titulo = soup.find('title')
            print(f"✅ Página carregada: {titulo.get_text(strip=True) if titulo else 'sem título'}")
            return soup

        except (WebDriverException, TimeoutException) as e:
            print(f"❌ Erro ao carregar página: {e}")
            return None

        finally:
            driver.quit()

    except Exception as e:
        print(f"❌ Erro ao configurar Selenium: {e}")
        return None


# ─── Passo 3: BeautifulSoup extrai os dados ───────────────

def extrair_restaurantes(soup: BeautifulSoup, top_n: int = 5) -> list[dict]:
    """
    Extrai nome, avaliação, reviews, preço e tipo de culinária
    dos cartões de restaurante do TripAdvisor.
    """
    if not soup:
        return []

    blocos = soup.find_all('div', class_='tbrcR')
    print(f"\n📋 {len(blocos)} blocos de restaurante encontrados.")

    restaurantes = []

    for bloco in blocos[:top_n]:
        # Nome
        nome_tag = bloco.find('a', class_=lambda c: c and 'BMQDV' in c and 'ukgos' in c)
        nome = "Nome não encontrado"
        if nome_tag:
            nome_div = nome_tag.find('div', class_=lambda c: c and 'biGQs' in c and 'fiohW' in c)
            if nome_div:
                nome = nome_div.get_text(strip=True)

        # Avaliação
        rating_tag = bloco.find('div', {'data-automation': 'bubbleRatingValue'})
        rating = "N/A"
        if rating_tag and rating_tag.find('span'):
            rating = rating_tag.find('span').get_text(strip=True)

        # Reviews
        reviews_tag = bloco.find('div', {'data-automation': 'bubbleReviewCount'})
        reviews = "N/A"
        if reviews_tag and reviews_tag.find('span'):
            reviews = reviews_tag.find('span').get_text(strip=True)

        # Culinária e Preço
        info_div = bloco.find('div', class_=lambda c: c and 'ZvrsW' in c and 'biqBm' in c)
        tipo_culinaria = "N/A"
        preco = "N/A"
        if info_div:
            spans = info_div.find_all('span', class_=lambda c: c and 'biGQs' in c and 'pZUbB' in c)
            if spans:
                tipo_culinaria = spans[0].get_text(strip=True)
            for span in spans[1:]:
                texto = span.get_text(strip=True)
                if '$' in texto:
                    preco = texto
                    break

        # Link
        link = "N/A"
        if nome_tag and 'href' in nome_tag.attrs:
            link = "https://www.tripadvisor.com.br" + nome_tag['href']

        restaurantes.append({
            "Nome": nome,
            "Avaliação": rating,
            "Reviews": reviews,
            "Preço": preco,
            "Culinária": tipo_culinaria,
            "Link": link,
        })

    return restaurantes


# ─── Pipeline completo ─────────────────────────────────────

def pesquisar_restaurantes(cidade: str, top_n: int = 5) -> list[dict]:
    """
    Pipeline completo:
    Tavily → URL → Selenium → HTML → BeautifulSoup → dados estruturados
    """
    url = buscar_url_tripadvisor(cidade)
    soup = acessar_pagina(url)
    return extrair_restaurantes(soup, top_n=top_n)