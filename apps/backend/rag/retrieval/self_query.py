"""
Self-query: antes de fazer retrieval, interpreta a pergunta da pessoa para
decidir se deve restringir a busca a uma categoria de documento.

Os documentos em base/ são organizados por categoria (ver
rag/ingest/embed_qdrant.py), por exemplo:
  - "juridico"   -> Constituição, Lei da Proteção Social, outras leis
  - "apoio"       -> contactos, procedimentos de denúncia, recursos práticos

Isto evita que uma pergunta prática ("onde posso denunciar?") devolva
apenas artigos constitucionais abstratos, e vice-versa.
"""

import json
from dataclasses import dataclass

from groq import Groq

from rag.settings import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

CATEGORIES = ["juridico", "apoio", "geral"]

SELF_QUERY_SYSTEM_PROMPT = f"""Classifique a pergunta do utilizador numa destas categorias: {", ".join(CATEGORIES)}.

- "juridico": perguntas sobre leis, direitos, artigos da Constituição, proteção social, processos legais formais.
- "apoio": perguntas práticas sobre como denunciar, onde procurar ajuda, contactos, primeiros passos após um incidente.
- "geral": qualquer outra pergunta, ou quando não tiver certeza.

Devolva APENAS um JSON: {{"categoria": "juridico" | "apoio" | "geral"}}"""


@dataclass
class SelfQueryResult:
    category: str  # uma de CATEGORIES


def classify_query(question: str) -> SelfQueryResult:
    """Classifica a pergunta numa categoria. Em caso de falha, devolve
    'geral', que não aplica nenhum filtro (comportamento mais seguro:
    busca em tudo em vez de arriscar excluir conteúdo relevante)."""
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SELF_QUERY_SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        category = data.get("categoria", "geral")
        if category not in CATEGORIES:
            category = "geral"
        return SelfQueryResult(category=category)
    except Exception:
        return SelfQueryResult(category="geral")
