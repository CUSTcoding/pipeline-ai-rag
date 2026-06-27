# Sunrise — Agente de Apoio a Vítimas

Agente de informação para apoio a vítimas de violência sexual e doméstica
em Moçambique. Dá informação sobre direitos, procedimentos de denúncia e
contactos de apoio, com base em documentos legais (Constituição, Lei da
Proteção Social, e outros que venham a ser adicionados).

![My image](public/Untitled-2026-06-27-0332(6).png)

## Princípios de segurança (ler antes de tudo)

Este não é um RAG genérico. É um sistema usado por pessoas potencialmente
em crise. Três decisões de arquitetura não são negociáveis:

1. **Deteção de crise corre sempre, antes de tudo.** Toda mensagem passa
   primeiro por `rag/graph/crisis.py`. Se houver sinal de risco iminente,
   a resposta é sempre um template fixo com contactos de emergência —
   nunca texto gerado livremente pelo LLM nesse caminho.
2. **O agente nunca pede detalhes do incidente** para "avaliar gravidade".
   Isso é desnecessário e pode revitimizar.
3. **Nada de logging de conteúdo de mensagens por defeito** (ver
   `rag/settings.py`, `LOG_USER_MESSAGE_CONTENT`). Antes de ligar
   qualquer analytics ou histórico, reavaliar implicações de privacidade.

Ver `docs/architecture.md` para mais detalhe.

## Estrutura

```
.
├── apps/
│   ├── backend/
│   │   ├── main.py                 API FastAPI (/chat, /health)
│   │   ├── rag/
│   │   │   ├── app.py               ponto de entrada do agente
│   │   │   ├── settings.py          config + contactos de apoio
│   │   │   ├── graph/
│   │   │   │   ├── crisis.py        deteção de risco iminente
│   │   │   │   ├── prompt.py        prompts (tom trauma-informed)
│   │   │   │   └── rag_graph.py     grafo LangGraph principal
│   │   │   ├── ingest/
│   │   │   │   ├── extract_text.py  chunking + categorização
│   │   │   │   └── embed_qdrant.py  embeddings + upsert Qdrant
│   │   │   └── retrieval/
│   │   │       ├── retriever.py     busca híbrida (semântica + BM25)
│   │   │       └── self_query.py    classificação da pergunta
│   │   └── requirements.txt
│   └── frontend/                    (a desenvolver)
├── base/                            PDFs de origem (Constituição, etc.)
├── infra/
│   ├── docker-compose.yml
│   └── docker/backend.Dockerfile
└── docs/
    ├── architecture.md
    ├── rag.md
    └── api.md
```

## Setup

### 1. Configura o ambiente

```bash
cp .env.example .env
# edita .env e cola a tua GROQ_API_KEY
```

### 2. Coloca os documentos em `base/`

Já incluídos: `Constituicao.pdf`, `Lei da Protecção Social.pdf`.
Para adicionar mais documentos, regista-os também em
`apps/backend/rag/ingest/extract_text.py` → `CATEGORY_MAP`.

### 3. Sobe tudo com Docker

```bash
cd infra
docker compose up -d --build
```

### 4. Faz a ingestão dos documentos

```bash
docker compose exec backend python -m rag.ingest.embed_qdrant
```

### 5. Testa

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quais são os meus direitos como vítima de violência doméstica?"}'
```

## Desenvolvimento local (sem Docker)

```bash
cd apps/backend
pip install -r requirements.txt
cp ../../.env.example ../../.env   # garante QDRANT_HOST=localhost

# sobe só o Qdrant
docker run -p 6333:6333 qdrant/qdrant

# ingestão
PYTHONPATH=. python -m rag.ingest.embed_qdrant

# teste via terminal, sem precisar da API
PYTHONPATH=. python -m rag.app "Como posso denunciar um caso de violência?"

# ou a API completa
uvicorn main:app --reload
```
