import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import uuid
import gradio as gr
from new_backend import graph


def generate_essay(topic: str, max_revisions: int):
    """
    Função chamada pelo Gradio ao clicar em 'Gerar Redação'.
    Usa yield para atualizar a interface em tempo real.
    """
    if not topic.strip():
        yield "⚠️ Por favor, insira um tópico para a redação."
        return

    thread_id = str(uuid.uuid4())
    thread_config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "task": topic,
        "max_revisions": max_revisions,
        "revision_number": 1,
        "plan": "",
        "draft": "",
        "critique": "",
        "content": [],
    }

    full_output = f"## 🚀 Iniciando pipeline para: *{topic}*\n\n"
    full_output += f"🔄 Revisões configuradas: {max_revisions}\n\n"
    full_output += "---\n\n"
    yield full_output

    for s in graph.stream(initial_state, thread_config):
        step_output = list(s.values())[0]

        if 'plan' in step_output:
            full_output += f"## 📋 Plano Gerado\n\n{step_output['plan']}\n\n"
            full_output += "---\n\n"

        elif 'content' in step_output and step_output['content']:
            num_fontes = len(step_output['content'])
            full_output += f"## 🔍 Pesquisa Concluída\n\n"
            full_output += f"✅ {num_fontes} fontes coletadas.\n\n"
            full_output += "---\n\n"

        elif 'draft' in step_output:
            rev = step_output.get('revision_number', '?')
            full_output += f"## ✍️ Rascunho (Revisão {rev})\n\n"
            full_output += f"{step_output['draft']}\n\n"
            full_output += "---\n\n"

        elif 'critique' in step_output:
            full_output += f"## 🔎 Crítica e Recomendações\n\n"
            full_output += f"{step_output['critique']}\n\n"
            full_output += "---\n\n"

        yield full_output

    full_output += "## ✅ Pipeline concluído!\n"
    yield full_output


# ─── Interface Gradio ─────────────────────────────────────

with gr.Blocks(
    theme=gr.themes.Soft(),
    title="Gerador de Redações — LangGraph"
) as demo:

    gr.Markdown("# 🤖 Gerador de Redações com LangGraph")
    gr.Markdown(
        "Digite o tópico da sua redação e escolha o número de revisões. "
        "O pipeline irá **planejar → pesquisar → escrever → criticar → revisar** automaticamente."
    )

    with gr.Row():
        with gr.Column(scale=3):
            essay_topic = gr.Textbox(
                label="Tópico da Redação",
                placeholder="Ex: A importância da inteligência artificial na educação",
                lines=2,
            )
        with gr.Column(scale=1):
            max_revisions_slider = gr.Slider(
                minimum=1,
                maximum=3,
                step=1,
                value=1,
                label="Número de Revisões",
            )

    generate_button = gr.Button("🚀 Gerar Redação", variant="primary", size="lg")

    output_textbox = gr.Markdown(label="Saída do Pipeline")

    generate_button.click(
        fn=generate_essay,
        inputs=[essay_topic, max_revisions_slider],
        outputs=output_textbox,
    )

if __name__ == "__main__":
    demo.launch(share=False)
    