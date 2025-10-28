# Chat e moderador de Conteúdo com IA

Chat de IA utilizando Ollama localmente com Python para responder perguntas de uma rede social, além de moderar conteúdo

<img width="1919" height="927" alt="image" src="https://github.com/user-attachments/assets/c31ab745-66a2-4b17-a55d-1a7090501e93" />

<img width="1916" height="920" alt="image" src="https://github.com/user-attachments/assets/3e150e0e-95a4-49f0-a3e5-5c1b32417288" />

Design antigo
<img width="100%" alt="image" src="https://github.com/user-attachments/assets/9911e888-42f2-40ea-9c7e-5408133cf9d3" />


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

## Rota principal
```py
@app.post("/chat")
async def chat_stream(request: Request, body: ChatRequest = Body(...)):
    global last_chat_request
    
    try:
        last_chat_request = datetime.utcnow()
        
        if await verify_origin(request=request) == False:
            return JSONResponse(status_code=403, content={"detail": "Origem desconhecida."})
    
        
        messages = [
            {
                "role": "system",
                "content": DEFAULT_TEXT + f"\n Responda com educação e se for o caso com humor. A mensagem do {body.user.name} é: {body.content}"
            },
            {"role": "user", "content": body.content},
        ]
        
        def stream_response():
            try:
                for chunk in ollama.chat(model="gemma", messages=messages, stream=True):
                    content = chunk["message"]["content"]
                    yield content
            except Exception as e:
                logger.error(f"Erro no stream_response: {str(e)}")
                yield f"[ERRO]: {str(e)}"
            yield ""  # Forçar fim do stream
                
        return StreamingResponse(stream_response(), media_type="text/event-stream")

    except ValidationError as ve:
        return JSONResponse(status_code=200, content={"detail": "Erro de validação nos dados enviados.", "errors": ve.errors()})
    except Exception as e:
        return JSONResponse(status_code=200, content={"detail": "Erro interno no servidor.", "error": str(e)})


```

## Melhorias Futuras
- Implementação de um sistema de feedback para aprimorar a precisão da IA.
- Integração com outras IAs para diferentes tipos de moderação (imagem, áudio, vídeo).
- Logs e dashboard para monitoramento das remoções.

## Licença
Este projeto está licenciado sob a [Creative Commons BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.pt_BR).  
Você pode copiar, modificar e redistribuir para fins **não comerciais**, desde que atribua os créditos ao autor original.
