def consultar_estoque(item: str) -> str:
    """Simula consulta de estoque no inventário."""
    item = item.lower().strip()
    estoque = {
        "monitor": 75,
        "teclado": 120,
        "mouse gamer": 80,
        "webcam": 40,
        "headset": 60,
        "impressora": 15,
    }
    if item in estoque:
        return f"Temos {estoque[item]} {item}s em estoque."
    return f"Item '{item}' não encontrado no inventário."


def consultar_preco_produto(produto: str) -> str:
    """Simula consulta de preço unitário de um produto."""
    produto = produto.lower().strip()
    precos = {
        "monitor": 999.90,
        "teclado": 150.00,
        "mouse gamer": 99.50,
        "webcam": 120.00,
        "headset": 180.00,
        "impressora": 750.00,
    }
    if produto in precos:
        return f"O preço de um(a) {produto} é R$ {precos[produto]:.2f}."
    return f"Produto '{produto}' não encontrado na lista de preços."


def encontrar_produto_mais_caro() -> str:
    """Retorna o nome e preço do produto mais caro no inventário."""
    precos = {
        "monitor": 999.90,
        "teclado": 150.00,
        "mouse gamer": 99.50,
        "webcam": 120.00,
        "headset": 180.00,
        "impressora": 750.00,
    }
    if not precos:
        return "Nenhum produto encontrado na lista de preços."
    nome = max(precos, key=precos.get)
    return f"O produto mais caro é o(a) {nome} com preço de R$ {precos[nome]:.2f}."


def calcular_valor_total_lista(lista_itens: str) -> str:
    """
    Calcula o valor total de uma lista de itens.
    Recebe string com itens separados por vírgula.
    Ex: "teclado, mouse gamer, monitor"
    """
    precos = {
        "monitor": 999.90,
        "teclado": 150.00,
        "mouse gamer": 99.50,
        "webcam": 120.00,
        "headset": 180.00,
        "impressora": 750.00,
    }

    itens = [item.strip().lower() for item in lista_itens.split(',')]
    valor_total = 0.0
    nao_encontrados = []

    for item in itens:
        if item in precos:
            valor_total += precos[item]
        else:
            nao_encontrados.append(item)

    resposta = f"O valor total dos itens encontrados é R$ {valor_total:.2f}."
    if nao_encontrados:
        resposta += f" Os seguintes itens não foram encontrados: {', '.join(nao_encontrados)}."

    return resposta


# Despacha nome → função
FERRAMENTAS = {
    "consultar_estoque": consultar_estoque,
    "consultar_preco_produto": consultar_preco_produto,
    "encontrar_produto_mais_caro": encontrar_produto_mais_caro,
    "calcular_valor_total_lista": calcular_valor_total_lista,
}