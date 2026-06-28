# 🤖 LangGraph Agents

Projeto de estudo e portfólio desenvolvido durante o curso **LangGraph: Orquestrando agentes e multiagentes** da Alura.

Demonstra a evolução da construção de agentes de IA — desde a implementação manual do padrão **ReAct** até a orquestração declarativa com **LangGraph**, utilizando o modelo **Gemini 2.5 Flash** via **OpenRouter**.

---

## 🧠 O que foi construído

### Agente 1 — ReAct Manual (Inventário)
Implementação do padrão **ReAct (Reasoning + Acting)** do zero, sem frameworks de orquestração. Um assistente de inventário para uma loja de informática com 4 ferramentas:

| Ferramenta | Descrição |
|---|---|
| `consultar_estoque` | Retorna a quantidade disponível de um item |
| `consultar_preco_produto` | Retorna o preço unitário de um produto |
| `encontrar_produto_mais_caro` | Retorna o produto de maior valor |
| `calcular_valor_total_lista` | Calcula o total de uma lista de itens |

### Agente 2 — LangGraph + Tavily (Pesquisa Web)
Agente de pesquisa geral com busca em tempo real, construído com **LangGraph**. Suporta:
- Chamadas **simples** (uma busca)
- Chamadas **paralelas** (múltiplas buscas simultâneas)
- Chamadas **sequenciais** (buscas dependentes entre si)

---

## 🗺️ Arquitetura do Agente LangGraph

```
        ┌─────────────┐
        │  __start__  │
        └──────┬──────┘
               ↓
          ┌─────────┐
    ┌────▶│   llm   │
    │     └────┬────┘
    │          ↓ exists_action?
    │     ┌────┴────┐
    │   True      False
    │     ↓          ↓
    │  [action]    [END]
    └─────┘
```

![Grafo do Agente](docs/grafo_agente.png)

---

## 🛠️ Tecnologias

- **Python 3.12**
- **LangGraph** — orquestração de agentes em grafo
- **LangChain** — integração com LLMs e ferramentas
- **OpenRouter** — acesso ao Gemini 2.5 Flash via API compatível com OpenAI
- **Tavily** — busca web em tempo real para agentes de IA
- **python-dotenv** — gerenciamento de variáveis de ambiente

---

## 📁 Estrutura do Projeto

```
langgraph-agents/
│
├── .env.example              # Modelo de variáveis de ambiente
├── .gitignore
├── README.md
├── requirements.txt
├── docs/
│   └── grafo_agente.png      # Visualização do grafo LangGraph
│
└── src/
    ├── main.py               # Ponto de entrada
    ├── agents/
    │   ├── react_agent.py    # Agente ReAct implementado manualmente
    │   └── langgraph_agent.py # Agente com LangGraph
    ├── config/
    │   └── settings.py       # Configuração de clientes e APIs
    ├── prompts/
    │   ├── react_prompt.py   # Prompt do agente de inventário
    │   └── pesquisa_prompt.py # Prompt do agente de pesquisa
    ├── state/
    │   └── agent_state.py    # Definição do estado compartilhado
    └── tools/
        └── inventario.py     # Ferramentas do agente de inventário
```

---

## 🚀 Como rodar

### Pré-requisitos
- Python 3.12+
- Conta no [OpenRouter](https://openrouter.ai/) com saldo
- Conta no [Tavily](https://tavily.com/) para a chave de busca

### 1. Clone o repositório
```bash
git clone https://github.com/jjsjunior3/langgraph-agents.git
cd langgraph-agents
```

### 2. Crie e ative o ambiente virtual
```bash
py -m venv .venv
.venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
```
Edite o `.env` com suas chaves:
```env
OPENROUTER_API_KEY=sk-or-v1-sua_chave_aqui
TAVILY_API_KEY=tvly-dev-sua_chave_aqui
```

### 5. Execute
```bash
py src/main.py
```

---

## 💡 Conceitos demonstrados

- Padrão **ReAct** (Reasoning + Acting) implementado manualmente
- **StateGraph** do LangGraph com nós, arestas e arestas condicionais
- **bind_tools** para registro nativo de ferramentas no modelo
- **Streaming** vs **Invoke** — visualização do grafo em execução
- Chamadas de ferramentas **paralelas** e **sequenciais**
- Gerenciamento de **estado compartilhado** com `Annotated` e `operator.add`
- Boas práticas: `.env`, `.gitignore`, estrutura modular, ambiente virtual

---

## 📚 Referências

- [Curso Alura — LangGraph: Orquestrando agentes e multiagentes](https://cursos.alura.com.br/)
- [Documentação LangGraph](https://langchain-ai.github.io/langgraph/)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [OpenRouter](https://openrouter.ai/)
- [Tavily](https://tavily.com/)

---

> Desenvolvido por **José João Santos Júnior** como projeto de portfólio durante os estudos de IA e agentes com LangGraph.