# Climatização Inteligente por IA (Automação Residencial e Predial)

Este projeto consiste em um protótipo de automação residencial/predial desenvolvido em Python que utiliza Visão Computacional para monitorar a quantidade de pessoas presentes em um ambiente e ajustar dinamicamente o estado e temperatura ideal do ar condicionado.

O sistema utiliza a API do **Roboflow** com o modelo pré-treinado no dataset COCO para identificar exclusivamente a classe `person` (pessoa), e o **Gradio** para expor uma interface web moderna de controle e visualização.

## 🚀 Tecnologias Utilizadas

- **Python 3.12**
- **Roboflow Python SDK**: Para inferência da detecção de objetos (pessoas).
- **Gradio (Blocks)**: Para a interface web (suporta upload de fotos ou transmissão de webcam(várias marcas)).
- **OpenCV**: Para desenhar e renderizar as caixas delimitadoras e etiquetas nas pessoas detectadas.
- **Python Dotenv**: Para gerenciamento seguro da chave secreta `ROBOFLOW_API_KEY`.

---

## 📊 Regras de Negócio (Atuador - Ar Condicionado)

O comportamento do atuador do ar condicionado é alterado em tempo real de acordo com as seguintes regras de ocupação:

| Pessoas Detectadas | Status do Ar Condicionado | Temperatura Recomendada | Modo de Operação |
|:------------------:|:-------------------------:|:-----------------------:|:----------------:|
| **0**              | DESLIGADO                 | N/A                     | Economia Total   |
| **1 a 2**          | LIGADO - Econômico        | 24°C                    | Modo Ecológico   |
| **3 a 5**          | LIGADO - Moderado         | 22°C                    | Conforto Padrão  |
| **Mais de 5**      | LIGADO - Potência Máxima  | 19°C                    | Resfriamento     |

---

## 🛠️ Configuração e Instalação

### 1. Clonar ou Acessar o Diretório do Projeto
Certifique-se de que está no diretório correto do workspace:
```bash
cd /home/usuario/antigravity-workspace/climatizacao-inteligente-ia
```

### 2. Criar e Ativar o Ambiente Virtual
Utilize a ferramenta `virtualenv` para inicializar um ambiente Python limpo:
```bash
python3 -m virtualenv .venv
source .venv/bin/activate
```

### 3. Instalar Dependências
Com o ambiente ativado, instale as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### 4. Configurar a Chave de API do Roboflow
Para que o sistema consiga enviar imagens e receber as detecções, você deve configurar sua chave secreta da API do Roboflow. 

1. Obtenha sua chave gratuita em [Roboflow Dashboard](https://roboflow.com/).
2. Crie um arquivo chamado `.env` na raiz do projeto (ou copie do exemplo):
   ```bash
   cp .env.example .env
   ```
3. Abra o arquivo `.env` e defina sua chave:
   ```env
   ROBOFLOW_API_KEY=sua_chave_secreta_aqui
   ```

*Nota: Se preferir não criar o arquivo `.env`, você poderá inserir a chave diretamente no campo correspondente na interface gráfica do Gradio.*

---

## 🖥️ Como Executar

Inicie o servidor de desenvolvimento do Gradio rodando:
```bash
python3 app.py
```

Após o início do servidor, a aplicação estará disponível localmente em:
👉 **[http://localhost:7860](http://localhost:7860)**

---

## 📁 Estrutura de Arquivos

- `app.py`: Arquivo principal da aplicação Gradio que constrói a interface e gerencia os eventos de detecção e visualização.
- `detector.py`: Módulo responsável pela comunicação com o Roboflow (inferência) e processamento das imagens (desenhar caixas delimitadoras e contagem).
- `ac_control.py`: Módulo que implementa a lógica do atuador do ar condicionado de acordo com a quantidade de pessoas detectadas.
- `config.py`: Arquivo de configurações gerais (como definições do modelo COCO e variáveis de ambiente).
- `requirements.txt`: Lista de dependências Python do projeto.
- `.env`: Arquivo contendo a chave de API do Roboflow (ignorado no versionamento).
- `.env.example`: Exemplo de configuração das variáveis de ambiente.
