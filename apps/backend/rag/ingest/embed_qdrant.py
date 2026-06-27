"""
Cria/atualiza a collection Qdrant usada pelo retriever.

Este script deve ser corrido sempre que os documentos em base/ mudarem:

    PYTHONPATH=apps/backend python -m rag.ingest.embed_qdrant
"""

import json
from dataclasses import asdict
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from rag.ingest.extract_text import chunk_knowledge_base
from rag.settings import (
    BASE_DIR,
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    QDRANT_COLLECTION,
    QDRANT_HOST,
    QDRANT_PORT,
)

DOCUMENTS_DIR = Path(BASE_DIR)
CHUNKS_CACHE = DOCUMENTS_DIR / "chunks.json"
BATCH_SIZE = 64


def _collection_exists(client: QdrantClient, collection_name: str) -> bool:
    return client.collection_exists(collection_name=collection_name)


def _ensure_collection(client: QdrantClient, collection_name: str) -> None:
    if not _collection_exists(client, collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )
        print(f"Collection criada: {collection_name}")
        return

    info = client.get_collection(collection_name=collection_name)
    vectors = info.config.params.vectors
    existing_dim = getattr(vectors, "size", None)

    if existing_dim != EMBEDDING_DIM:
        raise ValueError(
            f"A collection {collection_name!r} existe com dimensão {existing_dim}, "
            f"mas {EMBEDDING_MODEL!r} produz dimensão {EMBEDDING_DIM}. "
            "Apaga/recria a collection ou usa o mesmo modelo de embeddings."
        )

    print(f"Collection já existe: {collection_name}")


def _batched(items: list, batch_size: int):
    for start in range(0, len(items), batch_size):
        yield start, items[start : start + batch_size]


def main() -> None:
    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError(f"Diretório de documentos não encontrado: {DOCUMENTS_DIR}")

    print(f"A ler documentos em: {DOCUMENTS_DIR}")
    chunks = chunk_knowledge_base(DOCUMENTS_DIR)
    if not chunks:
        raise RuntimeError(f"Nenhum chunk foi gerado a partir dos PDFs em {DOCUMENTS_DIR}")

    CHUNKS_CACHE.write_text(
        json.dumps([asdict(chunk) for chunk in chunks], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Cache BM25 guardada: {CHUNKS_CACHE} ({len(chunks)} chunks)")

    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    _ensure_collection(client, QDRANT_COLLECTION)

    model = SentenceTransformer(EMBEDDING_MODEL)
    total = len(chunks)

    for start, batch in _batched(chunks, BATCH_SIZE):
        texts = [chunk.text for chunk in batch]
        vectors = model.encode(texts, show_progress_bar=False).tolist()
        points = [
            PointStruct(
                id=start + idx,
                vector=vector,
                payload=asdict(chunk),
            )
            for idx, (chunk, vector) in enumerate(zip(batch, vectors, strict=True))
        ]
        client.upsert(collection_name=QDRANT_COLLECTION, points=points)
        print(f"Indexados {min(start + len(batch), total)}/{total} chunks")

    print(f"Ingestão concluída na collection: {QDRANT_COLLECTION}")


if __name__ == "__main__":
    main()
