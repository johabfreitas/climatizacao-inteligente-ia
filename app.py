import os
import cv2
import numpy as np
import gradio as gr

import config
import detector
import ac_control


# Função para inicializar o HTML do painel vazio
def get_initial_dashboard():
    return """
    <div class="dashboard-container" style="
        display: flex; 
        flex-wrap: wrap; 
        gap: 16px; 
        padding: 20px; 
        background-color: #1e293b; 
        border-radius: 12px; 
        color: white; 
        font-family: 'Inter', sans-serif;
        border: 1px solid #334155;
    ">
        <div style="width: 100%; text-align: center; color: #94a3b8; padding: 20px 0;">
            <p style="font-size: 1.1rem; margin: 0;">📸 Envie uma imagem ou use a webcam para iniciar o monitoramento.</p>
            <p style="font-size: 0.85rem; margin-top: 5px;">O sistema detectará pessoas e controlará a climatização automaticamente.</p>
        </div>
    </div>
    """

# Função principal de processamento da imagem
def process_frame(image_np, confidence, api_key_input):
    # 1. Determinar qual chave de API usar (prioriza a entrada do usuário na UI, depois a do .env)
    api_key = api_key_input.strip() if api_key_input else config.ROBOFLOW_API_KEY
    
    if not api_key:
        # Exibe aviso amigável caso a chave esteja vazia
        warning_html = """
        <div style="
            padding: 20px; 
            background-color: #2d1616; 
            border: 1px solid #ef4444; 
            border-radius: 12px; 
            color: #fca5a5;
            font-family: 'Inter', sans-serif;
            margin-bottom: 15px;
        ">
            <h3 style="margin-top: 0; color: #f87171; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                ⚠️ Chave de API do Roboflow Ausente
            </h3>
            <p style="font-size: 0.9rem; margin: 8px 0;">Para realizar a detecção de pessoas por inteligência artificial, você precisa de uma chave de API válida.</p>
            <p style="font-size: 0.9rem; margin: 8px 0;"><strong>Como configurar:</strong></p>
            <ul style="margin: 0; padding-left: 20px; font-size: 0.85rem;">
                <li>Crie um arquivo <code>.env</code> na raiz do projeto com o conteúdo: <code>ROBOFLOW_API_KEY=sua_chave</code></li>
                <li>Ou insira a chave diretamente no campo <strong>"Chave de API Roboflow"</strong> no menu à esquerda.</li>
            </ul>
        </div>
        """
        # Retorna a imagem original intacta, o aviso em HTML e log de aviso
        return image_np, warning_html, "Erro: Chave de API do Roboflow não configurada."

    if image_np is None:
        return None, get_initial_dashboard(), "Aguardando imagem..."

    try:
        # 2. Executar inferência no Roboflow
        predictions = detector.detect_people(image_np, api_key, confidence)
        
        # 3. Anotar a imagem apenas com a classe 'person'
        annotated_image, count = detector.annotate_image(image_np, predictions)
        
        # 4. Determinar o estado do ar condicionado
        ac_state = ac_control.determine_ac_state(count)
        
        # 5. Gerar painel dashboard em HTML estilizado
        ac_color = ac_state["color"]
        ac_status = ac_state["status"]
        ac_temp = ac_state["temp"]
        ac_desc = ac_state["description"]
        
        # Cor de destaque da temperatura
        temp_color = "#ffffff" if ac_temp == "N/A" else ac_color
        
        dashboard_html = f"""
        <div class="dashboard-container" style="
            display: flex; 
            flex-wrap: wrap; 
            gap: 16px; 
            padding: 16px; 
            background-color: #0f172a; 
            border-radius: 12px; 
            color: white; 
            font-family: 'Inter', sans-serif;
            border: 1px solid #1e293b;
        ">
            <!-- Card 1: Contagem de Pessoas -->
            <div class="db-card" style="
                flex: 1; 
                min-width: 180px; 
                background: #1e293b; 
                padding: 16px; 
                border-radius: 8px; 
                text-align: center;
                border-left: 4px solid #3b82f6;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Ocupação Atual</div>
                <div style="font-size: 2.2rem; font-weight: 800; margin: 8px 0; color: #3b82f6;">{count}</div>
                <div style="font-size: 0.85rem; color: #cbd5e1;">{'Pessoa detectada' if count == 1 else 'Pessoas detectadas'}</div>
            </div>
            
            <!-- Card 2: Status do Ar Condicionado -->
            <div class="db-card" style="
                flex: 1.5; 
                min-width: 220px; 
                background: #1e293b; 
                padding: 16px; 
                border-radius: 8px; 
                text-align: center;
                border-left: 4px solid {ac_color};
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Status do Ar Condicionado</div>
                <div style="
                    font-size: 1.1rem; 
                    font-weight: 700; 
                    margin: 12px 0; 
                    padding: 6px 16px; 
                    border-radius: 9999px; 
                    background-color: {ac_color}; 
                    color: white;
                    display: inline-block;
                ">{ac_status}</div>
                <div style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.3; margin-top: 4px;">{ac_desc}</div>
            </div>
            
            <!-- Card 3: Temperatura de Ajuste -->
            <div class="db-card" style="
                flex: 1; 
                min-width: 180px; 
                background: #1e293b; 
                padding: 16px; 
                border-radius: 8px; 
                text-align: center;
                border-left: 4px solid {temp_color};
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Temperatura do Termostato</div>
                <div style="font-size: 2.2rem; font-weight: 800; margin: 8px 0; color: {temp_color};">{ac_temp}</div>
                <div style="font-size: 0.85rem; color: #cbd5e1;">Ajuste automático</div>
            </div>
        </div>
        """
        
        log_msg = f"Sucesso: {count} pessoas detectadas. AC: {ac_status} | {ac_temp}."
        return annotated_image, dashboard_html, log_msg
        
    except Exception as e:
        error_html = f"""
        <div style="
            padding: 20px; 
            background-color: #2d1616; 
            border: 1px solid #ef4444; 
            border-radius: 12px; 
            color: #fca5a5;
            font-family: 'Inter', sans-serif;
        ">
            <h3 style="margin-top: 0; color: #f87171; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                ❌ Erro no Processamento
            </h3>
            <p style="font-size: 0.9rem; margin: 8px 0;">Ocorreu uma falha ao fazer inferência no Roboflow.</p>
            <p style="font-size: 0.8rem; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px; font-family: monospace;">
                {str(e)}
            </p>
            <p style="font-size: 0.85rem; margin-top: 8px;">Verifique se a chave de API fornecida é válida e se você está conectado à internet.</p>
        </div>
        """
        return image_np, error_html, f"Erro: {str(e)}"

# Construção da interface com Gradio Blocks
custom_css = """
body {
    background-color: #0b0f19;
}
.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
h1, h2, h3 {
    font-weight: 700 !important;
}
.sidebar-panel {
    background-color: #111827 !important;
    border: 1px solid #1f2937 !important;
}
"""

with gr.Blocks(theme='JohnSmith9982/small_and_pretty', css=custom_css, title="Climatização Inteligente IA") as demo:
    # Cabeçalho da Aplicação com visual premium
    gr.HTML("""
    <div style="
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        padding: 30px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid #312e81;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    ">
        <h1 style="color: #60a5fa; font-size: 2.2rem; margin: 0 0 10px 0; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
            🌡️ Climatização Inteligente por IA
        </h1>
        <p style="color: #94a3b8; font-size: 1.1rem; margin: 0; max-width: 700px; margin-left: auto; margin-right: auto;">
            Sistema de automação predial que monitora o ambiente via imagens e ajusta dinamicamente a intensidade do ar condicionado conforme a taxa de ocupação detectada.
        </p>
    </div>
    """)
    
    with gr.Row():
        # Coluna da esquerda: Entradas e Controles
        with gr.Column(scale=1, elem_classes="sidebar-panel"):
            gr.Markdown("### ⚙️ Painel de Controle")
            
            # Input de API Key temporária
            api_key_input = gr.Textbox(
                label="Chave de API Roboflow",
                placeholder="Insira a ROBOFLOW_API_KEY se não configurada no .env",
                type="password",
                info="Caso configurada no arquivo .env, este campo pode ser deixado em branco."
            )
            
            # Slider de confiança
            confidence_slider = gr.Slider(
                minimum=0.1,
                maximum=0.9,
                value=0.4,
                step=0.05,
                label="Limiar de Confiança",
                info="Confiança mínima para detectar uma pessoa."
            )
            
            # Imagem de Entrada (Suporta Upload e Webcam)
            input_image = gr.Image(
                sources=["upload", "webcam"],
                type="numpy",
                label="Entrada de Câmera / Imagem"
            )
            
            btn_detect = gr.Button("🔍 Executar Detecção", variant="primary")
            
        # Coluna da direita: Resultados e Dashboard
        with gr.Column(scale=2):
            gr.Markdown("### 📊 Monitoramento em Tempo Real")
            
            # Saída de Dashboard Visual HTML
            dashboard_output = gr.HTML(value=get_initial_dashboard())
            
            # Imagem Anotada de Saída
            output_image = gr.Image(
                type="numpy",
                label="Visualização da Detecção (Somente Classe 'person')"
            )
            
            # Caixa de Logs simples de sistema
            system_log = gr.Textbox(
                label="Log do Sistema",
                value="Aguardando inicialização...",
                interactive=False
            )
            
    # Tabela com as regras de negócio
    gr.HTML("""
    <div style="
        margin-top: 24px;
        padding: 20px;
        background-color: #111827;
        border-radius: 12px;
        border: 1px solid #1f2937;
        font-family: 'Inter', sans-serif;
    ">
        <h3 style="color: #f3f4f6; margin-top: 0; margin-bottom: 12px; font-size: 1.1rem;">📝 Regras de Climatização do Atuador</h3>
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; color: #d1d5db;">
            <thead>
                <tr style="border-bottom: 1px solid #374151; color: #9ca3af;">
                    <th style="padding: 8px;">Pessoas no Ambiente</th>
                    <th style="padding: 8px;">Status do Ar Condicionado</th>
                    <th style="padding: 8px;">Temperatura Alvo</th>
                    <th style="padding: 8px;">Modo de Operação</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #1f2937;">
                    <td style="padding: 8px;">0 pessoas</td>
                    <td style="padding: 8px;"><span style="color: #94a3b8; font-weight: 600;">DESLIGADO</span></td>
                    <td style="padding: 8px;">N/A</td>
                    <td style="padding: 8px; color: #9ca3af;">Economia Total</td>
                </tr>
                <tr style="border-bottom: 1px solid #1f2937;">
                    <td style="padding: 8px;">1 a 2 pessoas</td>
                    <td style="padding: 8px;"><span style="color: #10b981; font-weight: 600;">LIGADO - Econômico</span></td>
                    <td style="padding: 8px; font-weight: 600;">24°C</td>
                    <td style="padding: 8px; color: #9ca3af;">Climatização Básica (Eco)</td>
                </tr>
                <tr style="border-bottom: 1px solid #1f2937;">
                    <td style="padding: 8px;">3 a 5 pessoas</td>
                    <td style="padding: 8px;"><span style="color: #0ea5e9; font-weight: 600;">LIGADO - Moderado</span></td>
                    <td style="padding: 8px; font-weight: 600;">22°C</td>
                    <td style="padding: 8px; color: #9ca3af;">Conforto Padrão</td>
                </tr>
                <tr>
                    <td style="padding: 8px;">Mais de 5 pessoas</td>
                    <td style="padding: 8px;"><span style="color: #ef4444; font-weight: 600;">LIGADO - Potência Máxima</span></td>
                    <td style="padding: 8px; font-weight: 600;">19°C</td>
                    <td style="padding: 8px; color: #9ca3af;">Resfriamento Rápido</td>
                </tr>
            </tbody>
        </table>
    </div>
    """)
    
    # Evento de clique do botão
    btn_detect.click(
        fn=process_frame,
        inputs=[input_image, confidence_slider, api_key_input],
        outputs=[output_image, dashboard_output, system_log]
    )
    
    # Também atualiza se a imagem for alterada (facilitando a webcam em tempo real)
    input_image.change(
        fn=process_frame,
        inputs=[input_image, confidence_slider, api_key_input],
        outputs=[output_image, dashboard_output, system_log]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
