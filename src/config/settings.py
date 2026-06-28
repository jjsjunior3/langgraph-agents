import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

load_dotenv()

MODEL = "google/gemini-2.5-flash"

# Cliente raw (aulas 1-4)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Cliente LangChain padrão
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model=MODEL,
    temperature=0,
)

# Cliente LangChain para saída estruturada (Pydantic)
llm_structured = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model=MODEL,
    temperature=0,
)

# Ferramenta Tavily
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
tavily_tool = TavilySearch(max_results=3)