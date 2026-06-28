import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

load_dotenv()

# Cliente raw OpenAI-compatible (aulas 1-4)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
MODEL = "google/gemini-2.5-flash"

# Cliente LangChain (aulas 5+) — temperature=0 para precisão
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model=MODEL,
    temperature=0,
)

# Ferramenta de busca Tavily
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
tavily_tool = TavilySearch(max_results=4)