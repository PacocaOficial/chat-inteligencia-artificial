import base64
import json
import os
from fastapi import Body, Depends, FastAPI, HTTPException, Request
import ollama
from pydantic import BaseModel, ValidationError
from fastapi.responses import RedirectResponse, StreamingResponse
from dotenv import load_dotenv
from read_file import read_file
from type_datas import ChatRequest, ChatRequestImage, PostRequest
from vars import DEFAULT_TEXT, GUIDELINES, USE_OF_TERMS
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi import status
import logging
from datetime import datetime, timedelta
import asyncio
import requests
import re

logger = logging.getLogger("uvicorn")
load_dotenv()
app = FastAPI()

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
last_chat_request = datetime.utcnow()

async def verify_origin(request: Request):
    return True
    try:
        origin = request.headers.get("origin") or request.headers.get("referer")
        if origin:
            if not any(origin.startswith(o) for o in ALLOWED_ORIGINS):
                return False
            return True
        else:
            return False
    except HTTPException as e:
        return False

@app.get("/")
async def home():
    link = os.getenv("LINK")
    if not link:
        return {"error": "LINK não configurado no .env"}
    return RedirectResponse(url=link)

@app.get("/hello-world")
async def hello_world():
    try:
        messages=[
            {"role": "user", "content": "Olá, como vai?"},
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na resposta da ia: {str(e)}")

@app.get("/ola-mundo")
async def ola_mundo():
    return {"message": "Olá Mundo"}



import requests
from urllib.parse import urlparse

@app.post("/analyse/image")
async def analyse_image(request: Request, body: ChatRequestImage = Body(...)):
    if await verify_origin(request=request) == False:
        return JSONResponse(status_code=403, content={"detail": "Origem desconhecida."})

    DEFAULT_TEXT = (
        "Você é um especialista em moderação de imagens. Sua tarefa é identificar e sinalizar imagens que violem as diretrizes de conteúdo. "
        "Conteúdos contendo armas, violência explícita, nudez ou qualquer forma de material inapropriado **não são permitidos** e devem ser classificados como inadequados."
    )

    try:        
        # Primeiro tenta obter a imagem a partir de uma URL
        if body.image_path and (body.image_path.startswith("http://") or body.image_path.startswith("https://")):
            response = requests.get(body.image_path)
            if response.status_code != 200:
                return JSONResponse(status_code=404, content={"detail": "Imagem não encontrada na URL fornecida."})
            image_data_base64 = base64.b64encode(response.content).decode("utf-8")

        # Se não for URL, verifica se já veio como base64
        elif body.image_base64:
            image_data_base64 = body.image_base64

        else:
            return JSONResponse(status_code=400, content={"detail": "Nenhuma imagem fornecida. Informe uma URL ou imagem em base64."})

        # Prepara as mensagens para o modelo multimodal
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é um moderador altamente rigoroso. Sua missão é identificar e sinalizar IMEDIATAMENTE qualquer imagem que viole as regras de conteúdo a seguir. "
                    "Atenção: mesmo que a imagem não seja sexualizada ou explícita, qualquer nudez total ou parcial — incluindo pessoas com o tórax ou seios visíveis, ainda que parcialmente cobertos ou com iluminação desfocada — deve ser considerada como *removido*. Não interessa a intenção da imagem. Se houver dúvida, classifique como REMOVIDO."
                    "Conteúdos proibidos incluem:\n"
                    "- Armas ou violência explícita\n"
                    "- Nudez (mesmo parcial)\n"
                    "- Seios visíveis (mesmo parcialmente)\n"
                    "- Tronco nu em qualquer gênero\n"
                    "- Posição sugestiva com ausência de roupas\n"
                    "Formato da resposta: um JSON simples com status e motivo.\n"
                    "Exemplo:\n"
                    "{ \"status\": \"removido\", \"reason\": \"A imagem contém nudez parcial com o tronco da mulher exposto.\" }"
                )
            },
            {
                "role": "user",
                "content": "Aqui está a imagem para análise.",
                "images": [image_data_base64]
            },
        ]

        response = ollama.chat(model="llava", messages=messages)

        ai_message_content = response["message"]["content"].strip()
        ai_message_content = re.sub(r"^```(?:json)?\s*", "", ai_message_content)  # remove início do bloco
        ai_message_content = re.sub(r"\s*```$", "", ai_message_content)           # remove final do bloco

        try:
            parsed_response = json.loads(ai_message_content)
            status = parsed_response.get("status")
            reason = parsed_response.get("reason")

            return {
                "status": status if status else "indefinido",
                "reason": reason,
                "analysis": parsed_response
            }

        except json.JSONDecodeError:
            print(f"Resposta inválida: {ai_message_content}")
            return JSONResponse(status_code=500, content={"detail": "Resposta do modelo não é um JSON válido.", "raw_response": ai_message_content})

    except Exception as e:
        logger.error(f"Erro geral no endpoint /analyse/image: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "Erro interno no servidor.", "error": str(e)})



@app.post("/analyze")
async def analyze_post(request: PostRequest):
    if await verify_origin(request=request) == False:
       return JSONResponse(status_code=403, content={"detail": "Origem desconhecida."})
   
    DEFAULT_TEXT = "Você é um especialista em moderação de conteúdo."
    
    try:
        response = ollama.chat(
            model="mistral",
            messages=[
                {
                    "role": "system",
                    "content": (
                        DEFAULT_TEXT +
                        f"Analise o seguinte post com base em nossas diretrizes de uso e moderação. Diretrizes em: {GUIDELINES}. Termos de uso em: {USE_OF_TERMS}. "
                        "Sua resposta DEVE ser um objeto JSON válido com as seguintes chaves: "
                        "{ \"status\": \"permitido\" | \"   \", \"reason\": \"<motivo_se_removido_ou_null>\" }. "
                        "Se o post for permitido ou não houver informações suficientes para removê-lo, o status deve ser \"permitido\" e o motivo null. "
                        "Se o post não for permitido, o status deve ser \"removido\" e o motivo deve ser uma breve e objetiva descrição da razão da remoção. "
                        "Posts contendo opiniões, linguagem informal ou gírias comuns NÃO devem ser removidos. "
                    )
                },
                {"role": "user", "content": request.content},
            ]
        )

        ai_message_content = response["message"]["content"].strip().lower()
        
        try:
            # Tentar parsear a resposta como JSON
            parsed_response = json.loads(ai_message_content)
            
            # Validar os campos esperados no JSON
            status = parsed_response.get("status")
            reason = parsed_response.get("reason")

            if status == "permitido":
                return {"status": "permitido", "analysis": ai_message_content, "reason": None}
            elif status == "removido":
                return {"status": "removido", "analysis": ai_message_content, "reason": reason}
            else:
                # Caso o JSON não siga o formato esperado, trate como erro ou como permitido por padrão
                return {"status": "indefinido", "analysis": ai_message_content, "reason": "Formato JSON inesperado do Ollama"}

        except json.JSONDecodeError:
            # Se o Ollama não retornar um JSON válido, trate aqui.
            # Você pode logar o erro e retornar um status padrão ou uma mensagem de erro.
            print(f"Ollama não retornou um JSON válido: {ai_message_content}")
            return JSONResponse(status_code=500, content={"detail": "Erro ao processar resposta do Ollama: formato inválido."})

        # if "Post Não Permitido" not in ai_message:
        #     return {"status": "permitido", "analysis": ai_message, "reason": None}
        # else:
        #     return {"status": "removido", "analysis": ai_message, "reason": ai_message}

    except ValidationError as ve:
        return JSONResponse(status_code=200, content={"detail": "Erro de validação nos dados enviados.", "errors": ve.errors()})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise do post: {str(e)}")
    
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


# a IA dorme a cada x tempo, envia uma mensagem a cada x tempo para ela não formir
@app.on_event("startup")
async def start_monitoring():
    async def monitor_inactivity():
        global last_chat_request
        while True:
            now = datetime.utcnow()
            inactive_by = (now - last_chat_request).total_seconds()
            # logger.info(f"Inativo por {inactive_by}")
            
            # se tiver inativo por x tempo, envia mensagem para acordar
            if inactive_by > 60:
                logger.info("Mais de 1 minuto sem requisição. Enviando 'olá' pra IA.")
                await send_hello_chat()
                last_chat_request = datetime.utcnow()
            await asyncio.sleep(1)  # checar a cada 1s
    asyncio.create_task(monitor_inactivity())
    
async def send_hello_chat():
    # Aqui você evita resposta longa
    messages = [
        {"role": "user", "content": "olá"}
    ]
    try:
        for chunk in ollama.chat(model="gemma", messages=messages, stream=True):
            break  # basta iniciar o stream, já "acorda"
        logger.info("IA acordada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao acordar IA: {e}")

# rotas 404 retorna link do site
@app.exception_handler(StarletteHTTPException)
async def redirect_404(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return RedirectResponse(url=os.getenv("LINK"), status_code=status.HTTP_302_FOUND)
    raise exc

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro inesperado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erro interno do servidor: {str(exc)}"},
    )