import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env se ele existir
load_dotenv()

# Chave da API do Roboflow
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "")

# Configurações do Modelo Roboflow (Dataset COCO pré-treinado do Universe)
MODEL_WORKSPACE = "microsoft"
MODEL_PROJECT = "coco-dataset-vdnr1"
MODEL_VERSION = 11

# Classe padrão que queremos filtrar (exclusivamente 'person' conforme requisito)
TARGET_CLASS = "person"
