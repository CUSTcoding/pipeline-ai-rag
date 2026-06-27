"""
Configuração central do agente.

IMPORTANTE: os contactos de apoio abaixo foram verificados via pesquisa
em Junho de 2026 (ver docs/rag.md para fontes). Antes de colocar isto em
produção, confirma estes números com a equipa -- linhas de apoio podem
mudar, e um número errado neste contexto é particularmente grave.
"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class SupportContact:
    name: str
    phone: str
    description: str
    hours: str


# Contactos de apoio verificados para Moçambique (Junho 2026).
# Mantidos num único local para serem fáceis de atualizar e de auditar.
SUPPORT_CONTACTS: list[SupportContact] = [
    SupportContact(
        name="Linha Verde 1458",
        phone="1458",
        description=(
            "Linha gratuita e confidencial de apoio a vítimas de violência "
            "baseada no género. Encaminha para o Centro de Atendimento "
            "Integrado (CAI) mais próximo."
        ),
        hours="Segunda a sábado, 7h às 20h",
    ),
    SupportContact(
        name="Linha Fala Criança",
        phone="116",
        description="Linha gratuita e confidencial dedicada a vítimas menores de idade.",
        hours="24 horas",
    ),
    SupportContact(
        name="Linha 94321 (Movitel/TMcel)",
        phone="94321",
        description=(
            "Mensagens de áudio gratuitas sobre prevenção e denúncia de "
            "violência baseada no género."
        ),
        hours="24 horas, 7 dias por semana",
    ),
    SupportContact(
        name="PRM — Polícia da República de Moçambique",
        phone="119",
        description="Número de emergência policial para situações de perigo imediato.",
        hours="24 horas",
    ),
]

EMERGENCY_NOTE = (
    "Em caso de violência sexual recente, procurar assistência médica nas "
    "primeiras 72 horas reduz significativamente o risco de infeções e "
    "permite preservar provas, caso a vítima decida denunciar."
)


# --- Configuração técnica (Groq, Qdrant) ---

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
if QDRANT_HOST == "localhost" and os.path.exists("/.dockerenv"):
    QDRANT_HOST = "qdrant"
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "sunrise_apoio_legal")

BASE_DIR = os.getenv("BASE_DIR", "/base" if os.path.exists("/base") else "base")

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

# Privacidade: nunca persistir o conteúdo das mensagens do utilizador em
# logs de longo prazo. Ver docs/architecture.md secção "Privacidade".
LOG_USER_MESSAGE_CONTENT = False
