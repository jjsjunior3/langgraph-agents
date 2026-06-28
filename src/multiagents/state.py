from typing import TypedDict


class AgentState(TypedDict):
    task: str            # tema do ensaio fornecido pelo usuário
    plan: str            # esboço criado pelo planejador
    draft: str           # rascunho criado pelo escritor
    critique: str        # análise feita pelo crítico
    content: list[str]   # conteúdo coletado pelo pesquisador
    revision_number: int # número da revisão atual
    max_revisions: int   # limite máximo de revisões