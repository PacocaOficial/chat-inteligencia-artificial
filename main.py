import os
from fastapi import FastAPI, HTTPException
import ollama
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from vars import DEFAULT_TEXT, GUIDELINES, USE_OF_TERMS

load_dotenv()

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
async def chat_stream(request: PostRequest):
    messages = [
        {
            "role": "system",
            "content": DEFAULT_TEXT + f"\nA mensagem do usuário é: {request.content}"

        },
        {"role": "user", "content": request.content},
    ]

    def stream_response():
        try:
            for chunk in ollama.chat(model="gemma", messages=messages, stream=True):
                content = chunk["message"]["content"]
                yield content
        except Exception as e:
            yield f"[ERRO]: {str(e)}"

    return StreamingResponse(stream_response(), media_type="text/plain")