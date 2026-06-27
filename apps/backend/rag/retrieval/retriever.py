"""
Retrieval híbrido: combina busca semântica (Qdrant) e busca por palavras-
chave (BM25), fundidas com Reciprocal Rank Fusion (RRF).

Ver apps/backend/rag/ingest/embed_qdrant.py para o processo de indexação
que alimenta este módulo.
"""

import json
from pathlib import Path

from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from rag.settings import BASE_DIR, EMBEDDING_MODEL, QDRANT_COLLECTION, QDRANT_HOST, QDRANT_PORT

CHUNKS_CACHE = Path(BASE_DIR) / "chunks.json"
RRF_K = 60


class HybridRetriever:
    def __init__(self):
        self.embed_model = SentenceTransformer(EMBEDDING_MODEL)
        self.qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

        if not CHUNKS_CACHE.exists():
            raise FileNotFoundError(
                f"{CHUNKS_CACHE} não encontrado. Corre primeiro: "
                "python -m rag.ingest.embed_qdrant"
            )

        self.chunks = json.loads(CHUNKS_CACHE.read_text(encoding="utf-8"))
        tokenized = [c["text"].lower().split() for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized)
        self.chunk_id_to_idx = {c["chunk_id"]: i for i, c in enumerate(self.chunks)}

    def _semantic_search(self, query: str, top_k: int) -> list[str]:
        vector = self.embed_model.encode(query).tolist()
        hits = self.qdrant.search(
            collection_name=QDRANT_COLLECTION, query_vector=vector, limit=top_k
        )
        return [hit.payload["chunk_id"] for hit in hits]

    def _keyword_search(self, query: str, top_k: int) -> list[str]:
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        ranked_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [self.chunks[i]["chunk_id"] for i in ranked_idx[:top_k]]

    def _rrf_fuse(self, rankings: list[list[str]], k: int = RRF_K) -> list[str]:
        scores: dict[str, float] = {}
        for ranking in rankings:
            for position, chunk_id in enumerate(ranking):
                scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + position + 1)
        return sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

    def retrieve(self, query: str, top_k: int = 4, candidate_pool: int = 15) -> list[dict]:
        semantic_ranking = self._semantic_search(query, candidate_pool)
        keyword_ranking = self._keyword_search(query, candidate_pool)
        fused = self._rrf_fuse([semantic_ranking, keyword_ranking])[:top_k]

        results = []
        for chunk_id in fused:
            idx = self.chunk_id_to_idx.get(chunk_id)
            if idx is not None:
                results.append(self.chunks[idx])
        return results
