import sys
import os

_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import re
from config.settings import client, MODEL
from tools.inventario import FERRAMENTAS
from prompts.react_prompt import PROMPT_REACT


class Agent:
    def __init__(self, system: str = ""):
        self.system = system
        self.messages: list[dict] = []
        if self.system:
            self.messages.append({"role": "system", "content": self.system})

    def __call__(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self) -> str:
        response = client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
        )
        return response.choices[0].message.content


def run_react_agent(pergunta: str, max_iterations: int = 5) -> str:
    """Executa o loop ReAct completo: Pensamento → Ação → Observação → Resposta."""
    agent = Agent(system=PROMPT_REACT)
    current_prompt = pergunta

    for i in range(max_iterations):
        response_text = agent(current_prompt).strip()

        print(f"\n--- Iteração {i + 1} ---")
        print(f"Modelo respondeu:\n{response_text}\n")

        # Chegou à resposta final
        resposta_match = re.search(r"Resposta:\s*(.*)", response_text, re.DOTALL)
        if resposta_match:
            return resposta_match.group(1).strip()

        # Ação com ou sem argumento
        # "Ação: nome_da_acao: argumento" OU "Ação: nome_da_acao"
        match = re.search(r"Ação:\s*(\w+)(?::\s*(.+))?", response_text)

        if match:
            action_name = match.group(1).strip()
            action_arg = match.group(2).strip() if match.group(2) else ""

            ferramenta = FERRAMENTAS.get(action_name)
            if ferramenta:
                # Chama com ou sem argumento dependendo da ferramenta
                observacao = ferramenta(action_arg) if action_arg else ferramenta()
            else:
                observacao = f"Erro: Ação '{action_name}' desconhecida."

            print(f"✅ Executou: {action_name}('{action_arg}')")
            print(f"📋 Observação: {observacao}")

            current_prompt = f"Observação: {observacao}"
        else:
            return f"Erro: resposta inesperada na iteração {i + 1}:\n{response_text}"

    return "Erro: limite máximo de iterações atingido."