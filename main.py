import os
from fastapi import FastAPI, HTTPException
import ollama
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

REDE_SOCIAL = "Paçoca"
LINK = "http://127.0.0.1:3000"
ABOUT = f"{LINK}/sobre"
USE_OF_TERMS = f"{LINK}/termos-uso"
GUIDELINES = f"{LINK}/diretrizes"
READ_BOOKS = "https://readbooks.site"
DISCORD = "https://discord.com/invite/vJjGNcjKpj"

LINKS = {
    "link oficial": LINK,
    "termos de uso": f"{LINK}/termos-uso",
    "diretrizes": f"{LINK}/termos-uso",
    "login": f"{LINK}/login",
    "criar conta": f"{LINK}/cadastro",
    "doação": f"{LINK}/doacao",
    "Paçoca games - jogos online do paçoca": f"{LINK}/jogos",
    "readbooks - read books": READ_BOOKS,
    "configurações": f"{LINK}/configuracoes",
    "configurar privacidade": f"{LINK}/privacidade",
    "visualizar sessões ativas": f"{LINK}/sessoes-ativas",
    "configurar notificações": f"{LINK}/configuracoes/notificacoes",
    "premium - pagar verificado": f"{LINK}/verificado",
    "minhas comunidades": f"{LINK}/comunidades",
    "discord oficial": DISCORD,
    "baixar paçoca": f"{LINK}/download",
    "significado dos selos": f"{LINK}/significado-selos",
    "dashboard com dados atualizados do Paçoca": f"{LINK}/dashboard",
}

defaultText = (
    f"Você é uma IA para a plataforma/rede social {REDE_SOCIAL} ela é real e possui usuários ativos."
    f"Tudo que você precisa saber sobre a rede social e sobre sua criação está em: {ABOUT}."
    f"Diretrizes da rede social e da comunidade disponível em: {GUIDELINES}."
    f"Termos de uso da rede social e da comunidade disponível em: {USE_OF_TERMS}."
    f"Números reais da pladaforma, como quantidade de usuárois em: {LINK}/dashboard."
   "Todos os links úteis e oficiais:\n" +
    "\n".join([f"{k}: {v}" for k, v in LINKS.items()])
)

app = FastAPI()

class PostRequest(BaseModel):
    content: str

@app.get("/")
async def home():
    return {"message": "Olá Mundo"}

@app.post("/analyze")
async def analyze_post(request: PostRequest):
    try:
        response = ollama.chat(
            model="mistral",
            messages=[
                {
                    "role": "system",
                    "content": (
                        defaultText,
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
async def chat_stream(request: PostRequest):
    messages = [
        {
            "role": "system",
            "content": defaultText + f"\nA mensagem do usuário é: {request.content}"

        },
        {"role": "user", "content": request.content},
    ]

    def stream_response():
        try:
            for chunk in ollama.chat(model="mistral", messages=messages, stream=True):
                content = chunk["message"]["content"]
                yield content
        except Exception as e:
            yield f"[ERRO]: {str(e)}"

    return StreamingResponse(stream_response(), media_type="text/plain")