import os
from fastapi import FastAPI, HTTPException
import ollama
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class PostRequest(BaseModel):
    content: str

@app.get("/")
async def home():
    return "Ola Mundo"


from fastapi import FastAPI, HTTPException
import ollama
from pydantic import BaseModel

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
                        "Você é um sistema de moderação de conteúdo para a plataforma/rede social Paçoca. "
                        f"Analise o seguinte post com base em nossas diretrizes de uso e moderação. Diretrizes em: {os.getenv('GUIDELINES_URL')}. Termos de uso em: {os.getenv('TERMS_USE_URL')}"
                        "Se o post for permitido, responda apenas com: 'Post Permitido'. "
                        "Se não for permitido, responda apenas com o motivo da remoção, de forma objetiva e breve."
                    )
                },
                {"role": "user", "content": request.content},
            ]


        )

        ai_message = response["message"]["content"].strip().lower()

        if "post permitido" in ai_message:
            return {"status": "permitido", "analysis": ai_message, "reason": None}
        else:
            return {"status": "removido", "analysis": ai_message, "reason": ai_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise do post: {str(e)}")
