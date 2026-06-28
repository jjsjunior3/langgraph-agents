import operator
from uuid import uuid4
from typing import Annotated
from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict


def reduce_messages(
    left: list[AnyMessage],
    right: list[AnyMessage]
) -> list[AnyMessage]:
    """
    Função de redução personalizada para o AgentState.

    Comportamento:
    - Se a mensagem nova tem o mesmo ID de uma existente → SUBSTITUI
    - Se o ID é novo ou ausente → ADICIONA ao final

    Isso é essencial para o HITL, onde o humano pode corrigir
    uma mensagem já existente no estado.
    """
    # Garante que toda mensagem nova tem um ID único
    for message in right:
        if not message.id:
            message.id = str(uuid4())

    merged = left.copy()

    for message in right:
        for i, existing in enumerate(merged):
            if existing.id == message.id:
                merged[i] = message  # substitui
                break
        else:
            merged.append(message)  # adiciona

    return merged


class AgentState(TypedDict):
    """
    Estado compartilhado entre os nós do grafo.
    Usa reduce_messages para suportar substituição (HITL)
    além de adição (fluxo normal).
    """
    messages: Annotated[list[AnyMessage], reduce_messages]