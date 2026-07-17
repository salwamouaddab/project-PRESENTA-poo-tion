from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from litellm import completion
import litellm

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_MODEL = "ollama/llama3"
OLLAMA_API_BASE = "http://localhost:11434"

conversations = {}

class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.get("/")
def root():
    return {"status": "ok", "message": "Chatbot backend khadam"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    history = conversations.get(request.session_id, [])

    if not history:
        history.append({
            "role": "system",
            "content": "IMPORTANT: Tu dois répondre en 1 seule phrase courte, maximum 15 mots. Ne dépasse jamais cette limite."
        })

    history.append({"role": "user", "content": request.message})

    try:
        response = completion(
            model=OLLAMA_MODEL,
            messages=history,
            api_base=OLLAMA_API_BASE,
            max_tokens=40,
            timeout=120,
        )
    except litellm.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Le modèle a mis trop de temps à répondre.")

    reply_text = response.choices[0].message["content"]

    history.append({"role": "assistant", "content": reply_text})
    conversations[request.session_id] = history

    return ChatResponse(reply=reply_text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)