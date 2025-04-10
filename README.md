# Chat e moderador de Conteúdo com IA

Chat de IA utilizando Ollama localmente com Python para responder perguntas de uma rede social, além de moderar conteúdo

## Tecnologias Utilizadas
- **FastAPI**: Framework para a criação da API de validação
- **Ollama**: IA utilizada para analisar o conteúdo dos posts
- **gemma**: Modelo de IA performatico
- **Python**: Linguagem de programação principal do projeto

## Como Funciona
1. Sempre que um novo post é publicado na sua plataforma, uma requisição é enviada para esta API.
2. A IA analisa o conteúdo do post e determina se ele é permitido ou deve ser removido.
3. Caso o post seja inadequado, a API realiza uma requisição ao backend da plataforma para excluí-lo automaticamente.

## Instalação e Execução

1. Clone este repositório:
   ```sh
   git clone https://github.com/JoaoEnrique/chat-inteligencia-artificial
   cd seu-repositorio
   ```
2. Crie um ambiente virtual (opcional, mas recomendado):
   ```sh
   python -m venv env
   source env/bin/activate  # Linux/macOS
   env\Scripts\activate  # Windows
   ```
3. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```
4. Certifique-se de que o modelo está instalado no Ollama:
   ```sh
   ollama pull mistral
   ```
5. Execute a API:
   ```sh
   uvicorn main:app --reload --port 8082
   ```

## Uso da API

### Validação de Post
- **Endpoint:** `POST /analyze`
- **Request:**
  ```json
  {
    "content": "Texto do post aqui"
  }
  ```
- **Response:**
  ```json
  {
    "status": "permitido",
    "analysis": "Post Permitido"
  }
  ```
  ou
  ```json
  {
    "status": "removido",
    "analysis": "Motivo pelo qual o post foi removido"
  }
  ```

## Melhorias Futuras
- Implementação de um sistema de feedback para aprimorar a precisão da IA.
- Integração com outras IAs para diferentes tipos de moderação (imagem, áudio, vídeo).
- Logs e dashboard para monitoramento das remoções.

## Licença
Este projeto está licenciado sob a [Creative Commons BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.pt_BR).  
Você pode copiar, modificar e redistribuir para fins **não comerciais**, desde que atribua os créditos ao autor original.
