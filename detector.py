import os
import cv2
import tempfile
import numpy as np
from roboflow import Roboflow
import config

# Variáveis globais para cache da inicialização do modelo
_cached_model = None
_cached_api_key = None

def get_detector_model(api_key: str):
    """
    Carrega o modelo do Roboflow e armazena em cache para evitar chamadas de API repetidas
    durante a reinicialização.
    """
    global _cached_model, _cached_api_key
    
    if not api_key or api_key.strip() == "":
        raise ValueError("Chave de API do Roboflow (ROBOFLOW_API_KEY) não foi fornecida.")
        
    # Se já temos o modelo em cache para esta chave de API, retorna-o
    if _cached_model is not None and _cached_api_key == api_key:
        return _cached_model
        
    try:
        # Inicializa o cliente do Roboflow
        rf = Roboflow(api_key=api_key)
        # Carrega o workspace, projeto e versão do COCO
        project = rf.workspace(config.MODEL_WORKSPACE).project(config.MODEL_PROJECT)
        model = project.version(config.MODEL_VERSION).model
        
        # Salva no cache
        _cached_model = model
        _cached_api_key = api_key
        return model
    except Exception as e:
        # Limpa o cache em caso de erro para permitir nova tentativa
        _cached_model = None
        _cached_api_key = None
        raise RuntimeError(f"Erro ao inicializar o modelo Roboflow: {str(e)}")

def detect_people(image_np: np.ndarray, api_key: str, confidence_threshold: float = 0.40):
    """
    Envia a imagem em formato numpy array para o Roboflow e executa a inferência.
    """
    model = get_detector_model(api_key)
    
    # Criar um arquivo temporário para salvar o frame antes de enviar
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        # Gradio envia em RGB, OpenCV escreve em BGR
        bgr_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        cv2.imwrite(temp_file.name, bgr_image)
        temp_path = temp_file.name
        
    try:
        # O SDK da Roboflow espera o parâmetro confidence como inteiro de 0 a 100
        conf_percent = int(confidence_threshold * 100)
        prediction = model.predict(temp_path, confidence=conf_percent)
        return prediction.json().get("predictions", [])
    finally:
        # Garante a exclusão do arquivo temporário
        if os.path.exists(temp_path):
            os.remove(temp_path)

def annotate_image(image_np: np.ndarray, predictions: list, target_class: str = config.TARGET_CLASS):
    """
    Anota a imagem desenhando caixas delimitadoras e rótulos apenas para a classe alvo ('person').
    Retorna a imagem anotada e o total de pessoas detectadas.
    """
    annotated_image = image_np.copy()
    people_count = 0
    
    for pred in predictions:
        if pred.get("class") == target_class:
            people_count += 1
            
            # Coordenadas de centro da caixa delimitadora do Roboflow
            x = pred["x"]
            y = pred["y"]
            w = pred["width"]
            h = pred["height"]
            conf = pred["confidence"]
            
            # Calcular os cantos superior-esquerdo e inferior-direito
            x1 = int(x - w / 2)
            y1 = int(y - h / 2)
            x2 = int(x + w / 2)
            y2 = int(y + h / 2)
            
            # Limitar coordenadas às dimensões da imagem
            height_img, width_img = annotated_image.shape[:2]
            x1 = max(0, min(x1, width_img - 1))
            y1 = max(0, min(y1, height_img - 1))
            x2 = max(0, min(x2, width_img - 1))
            y2 = max(0, min(y2, height_img - 1))
            
            # Cor da caixa (Verde vibrante em RGB para o Gradio)
            box_color = (16, 185, 129)  # Emerald-500 (#10b981) em RGB
            
            # Desenha a caixa delimitadora
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), box_color, 3)
            
            # Prepara a tag/rótulo
            label = f"Pessoa {people_count}: {conf:.0%}"
            
            # Calcula tamanho do texto para criar uma etiqueta preenchida de fundo
            (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            
            # Desenha fundo da etiqueta
            cv2.rectangle(
                annotated_image,
                (x1, y1 - text_h - 10),
                (x1 + text_w + 10, y1),
                box_color,
                -1
            )
            
            # Escreve o texto sobre a etiqueta (Branco)
            cv2.putText(
                annotated_image,
                label,
                (x1 + 5, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )
            
    return annotated_image, people_count
