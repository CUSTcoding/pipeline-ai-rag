"""
API mínima que expõe o agente via HTTP.

IMPORTANTE (privacidade): este endpoint não persiste o conteúdo das
mensagens em nenhuma base de dados ou ficheiro de log por defeito --
ver rag.settings.LOG_USER_MESSAGE_CONTENT. Antes de adicionar qualquer
forma de logging, analytics, ou histórico de conversas, reavalia
cuidadosamente as implicações de privacidade para este caso de uso.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag.app import ask

app = FastAPI(title="Sunrise - Agente de Apoio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajustar para o domínio real do frontend em produção
    allow_methods=["POST"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    answer = ask(request.message)
    return ChatResponse(answer=answer)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
