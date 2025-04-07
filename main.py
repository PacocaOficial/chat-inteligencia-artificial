import os
from fastapi import Body, Depends, FastAPI, HTTPException, Request
import ollama
from pydantic import BaseModel
from fastapi.responses import RedirectResponse, StreamingResponse
from dotenv import load_dotenv
from type_datas import ChatRequest, PostRequest
from vars import DEFAULT_TEXT, GUIDELINES, USE_OF_TERMS
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import status

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
async def home():
    return {"message": "Olá Mundo"}

@app.get("/ola-mundo")
async def home():
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
    if await verify_origin(request=request) == False:
       return JSONResponse(status_code=403, content={"detail": "Origem desconhecida."})
    
    messages = [
        {
            "role": "system",
            "content": (
                DEFAULT_TEXT + f"\nA mensagem do usuário é: {body.content}"
                        "Se o usuário perguntar 'qual é meu nome?', 'qual minha bio?', ou coisas parecidas, responda com os dados abaixo. Sempre responda diretamente ao usuário utilizando 'você', nunca 'o usuário'."
                        "Se os dados estiverem ausentes, diga isso de forma simpática."
                        "\n\n--- INFORMAÇÕES DO USUÁRIO ---"
                        f"\n• Nome: {body.user.name if body.user.name else 'não informado'}"
                        f"\n• Perfil verificado: {'sim' if body.user.verified_profile else 'não'}"
                        f"\n• Biografia: {body.user.biography if body.user.biography else 'não informada'}"
                        f"\n• Data de nascimento: {body.user.birth_date if body.user.birth_date else 'não informada'}"
                        f"\n• Total de posts: {body.user.total_posts if body.user.total_posts else '0'}"
                        f"\n• Total de seguidores: {body.user.total_followers if body.user.total_followers else '0'}"
                        f"\n• Total seguindo: {body.user.total_following if body.user.total_following else '0'}"
                        )

        },
        {"role": "user", "content": body.content},
    ]

    def stream_response():
        try:
            for chunk in ollama.chat(model="gemma", messages=messages, stream=True):
                content = chunk["message"]["content"]
                yield content
        except Exception as e:
            yield f"[ERRO]: {str(e)}"

    return StreamingResponse(stream_response(), media_type="text/plain")


# rotas 404 retorna link do site
@app.exception_handler(StarletteHTTPException)
async def redirect_404(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return RedirectResponse(url=os.getenv("LINK"), status_code=status.HTTP_302_FOUND)
    raise exc