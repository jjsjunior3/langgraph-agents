import operator
from typing import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """
    Estado compartilhado entre os nós do grafo.
    operator.add garante que as mensagens sejam acumuladas,
    não substituídas a cada nó.
    """
    messages: Annotated[list[AnyMessage], operator.add]