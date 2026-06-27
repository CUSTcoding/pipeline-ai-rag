"""
Deteção de crise / risco iminente.

Este módulo corre ANTES do pipeline normal de RAG, em toda mensagem
recebida. Se detetar sinais de risco iminente (ideação suicida, perigo
físico imediato, pedido de ajuda urgente), o fluxo normal é interrompido
e a resposta passa a ser, sempre, os contactos de emergência -- nunca uma
resposta gerada livremente pelo LLM nesse caso.

Abordagem: usa-se o próprio LLM como classificador (mais robusto que uma
lista de palavras-chave, que tanto falha por excesso como por defeito em
texto livre e em português informal), mas com uma escolha de design
importante: o classificador só pode devolver um JSON estruturado de duas
classes -- nunca gera texto livre para o utilizador. A resposta de crise
em si é sempre o template fixo em prompt.py, nunca texto gerado pelo
modelo nesse caminho. Isto elimina o risco do LLM "alucinar" uma resposta
inadequada exatamente no momento em que isso seria mais perigoso.
"""

import json
from dataclasses import dataclass

from groq import Groq

from rag.settings import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

CLASSIFIER_SYSTEM_PROMPT = """Você é um classificador de risco. Analise a mensagem do utilizador e devolva APENAS um JSON, sem nenhum texto antes ou depois, no formato:

{"risco_imediato": true ou false, "motivo": "breve razão em poucas palavras"}

Considere "risco_imediato": true quando a mensagem sugerir:
- Ideação suicida ou auto-mutilação ("quero morrer", "não vale a pena viver", "vou-me matar")
- Perigo físico iminente ("ele está aqui agora", "estou fechada/o com ele", "ele tem uma arma")
- Pedido explícito e urgente de ajuda imediata

Considere "risco_imediato": false para:
- Perguntas informativas sobre direitos, leis, ou procedimentos, mesmo sobre temas sensíveis
- Relatos de violência passada, sem indicação de perigo neste momento
- Perguntas gerais sobre como ajudar outra pessoa

Na dúvida entre as duas categorias, escolha true -- o custo de mostrar contactos de apoio sem necessidade estrita é muito menor que o custo de não mostrar quando são necessários."""


@dataclass
class CrisisCheckResult:
    is_immediate_risk: bool
    reason: str


def check_crisis(message: str) -> CrisisCheckResult:
    """Classifica se uma mensagem indica risco iminente. Falha de forma segura:
    em caso de erro na chamada ao LLM, assume risco=True (mostra contactos)
    em vez de deixar passar uma mensagem de risco sem resposta adequada."""
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return CrisisCheckResult(
            is_immediate_risk=bool(data.get("risco_imediato", True)),
            reason=data.get("motivo", ""),
        )
    except Exception as exc:  # noqa: BLE001 - failsafe intencional
        return CrisisCheckResult(
            is_immediate_risk=True,
            reason=f"falha no classificador, a assumir risco por precaução: {exc}",
        )
