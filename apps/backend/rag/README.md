# rag/

Pipeline RAG do agente. **Antes de alterar qualquer coisa aqui, ler
`docs/architecture.md` na raiz do projeto** — este não é um RAG genérico,
é usado por pessoas potencialmente em situação de crise.

## Módulos

- `settings.py` — configuração central e contactos de apoio (única fonte
  de verdade, nunca duplicar números noutros ficheiros)
- `graph/crisis.py` — deteção de risco iminente. Corre sempre, primeiro.
- `graph/prompt.py` — prompts do sistema, incluindo o tom trauma-informed
- `graph/rag_graph.py` — grafo LangGraph que orquestra todo o fluxo
- `ingest/` — extração de PDFs, chunking, categorização, embeddings
- `retrieval/` — busca híbrida (semântica + BM25) e classificação de
  perguntas por categoria
- `app.py` — ponto de entrada simples (`ask(question) -> str`)

## Fluxo resumido

```
pergunta → crisis_check → (crise? resposta fixa) ou (self_query → retrieve → generate)
```
