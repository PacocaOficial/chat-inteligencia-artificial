from fastapi import FastAPI, HTTPException
import ollama
from pydantic import BaseModel

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
                        "Analise se esse post é ofensivo, falso ou inadequado. "
                        "Se for permitido, retorne exatamente a frase 'Post Permitido'. "
                        "Se não for permitido, retorne apenas o motivo."
                    ),
                },
                {"role": "user", "content": request.content},
            ],
        )

        ai_message = response["message"]["content"].strip().lower()

        if "post permitido" in ai_message:
            return {"status": "permitido", "analysis": ai_message, "reason": None}
        else:
            return {"status": "removido", "analysis": ai_message, "reason": ai_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise do post: {str(e)}")
