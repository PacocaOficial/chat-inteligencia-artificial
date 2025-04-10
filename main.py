import os
from fastapi import Body, Depends, FastAPI, HTTPException, Request
import ollama
from pydantic import BaseModel, ValidationError
from fastapi.responses import RedirectResponse, StreamingResponse
from dotenv import load_dotenv
from read_file import read_file
from type_datas import ChatRequest, PostRequest
from vars import DEFAULT_TEXT, GUIDELINES, USE_OF_TERMS
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import status
from fastapi.logger import logger

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

from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException


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

@app.post("/teste-post")
async def ola_mundo():
    return {"message": "Olá Mundo"}

@app.post("/analyze")
async def analyze_post(request: PostRequest):
    if await verify_origin(request=request) == False:
       return JSONResponse(status_code=403, content={"detail": "Origem desconhecida."})
   
    try:
        response = ollama.chat(
            model="mistral",
            messages=[
                {
                    "role": "system",
                    "content": (
                        DEFAULT_TEXT,
                        f"Analise o seguinte post com base em nossas diretrizes de uso e moderação. Diretrizes em: {GUIDELINES}. Termos de uso em: {USE_OF_TERMS}"
                        "Se não for tiver informações suficience, responda apenas com: 'Post Permitido''. "
                        "Se o post for permitido, responda apenas com: 'Post Permitido'. "
                        "Posts contendo opiniões, linguagem informal ou gírias comuns **não devem ser removidos**. "
                        "Se não for permitido, responda com: 'Post Não Permitido' no inicio da frase e o motivo da remoção, de forma objetiva e breve."
                        f"O conteúdo do post é: {request.content}"
                    )
                },
                {"role": "user", "content": request.content},
            ]


        )

        ai_message = response["message"]["content"].strip().lower()

        if "Post Não Permitido" not in ai_message:
            return {"status": "permitido", "analysis": ai_message, "reason": None}
        else:
            return {"status": "removido", "analysis": ai_message, "reason": ai_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise do post: {str(e)}")
    
    


@app.post("/chat")
async def chat_stream(request: Request, body: ChatRequest = Body(...)):
    try:
        if await verify_origin(request=request) == False:
            return JSONResponse(status_code=403, content={"detail": "Origem desconhecida."})
    
        
        messages = [
            {
                "role": "system",
                "content": DEFAULT_TEXT + f"\n Responda com educação e se for o caso com humor. A mensagem do {body.user.name} é: {body.content}"
            },
            {"role": "user", "content": body.content},
        ]
        
        # Teste inicial pra ver se o modelo responde, antes de stream
        try:
            test_response = ollama.chat(model="gemma", messages=messages, stream=False)
        except Exception as e:
            logger.error(f"Erro no Ollama.chat (teste): {str(e)}")
            return JSONResponse(status_code=500, content={"detail": "Erro ao iniciar conversa com modelo.", "error": str(e)})
        
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


# rotas 404 retorna link do site
@app.exception_handler(StarletteHTTPException)
async def redirect_404(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return RedirectResponse(url=os.getenv("LINK"), status_code=status.HTTP_302_FOUND)
    raise exc