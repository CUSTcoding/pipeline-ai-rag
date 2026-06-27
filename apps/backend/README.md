# Backend

API e lógica do agente. Ver `rag/README.md` para detalhe do pipeline RAG,
e `docs/architecture.md` (raiz do projeto) para as decisões de segurança.

## Comandos rápidos

```bash
pip install -r requirements.txt

# ingestão (corre uma vez, ou sempre que adicionares documentos a base/)
PYTHONPATH=. python -m rag.ingest.embed_qdrant

# teste via terminal
PYTHONPATH=. python -m rag.app "a tua pergunta"

# API
uvicorn main:app --reload
```
