from utils.chunker import chunk_text
from utils.retrieval_profiles import get_profile, rerank_hits
from services.db_service import (
    insert_memory,
    query_memories,
    commit,
    insert_memory_query,
    delete_memories,
    get_namespaces_by_user,
    get_memory_queries
)
from services.embedder import BaseEmbedder
from services.openai_embedder import OpenAIEmbedder
from typing import Optional, Dict, Any, List
from datetime import datetime

class MemoryService:
    def __init__(self, embedder: BaseEmbedder = OpenAIEmbedder()):
        self.embedder = embedder

    def save_memory_to_db(
        self,
        namespace: str,
        content: str,
        metadata: dict,
        user_id: str,
        expires_at: Optional[datetime] = None
    ):
        chunks = chunk_text(content)
        for chunk in chunks:
            embedding = self.embedder.embed(chunk)
            insert_memory(user_id, namespace, chunk, metadata, embedding, expires_at)
        commit()

    def query_similar_memories(
        self,
        namespace: str,
        query: str,
        filters: dict = {},
        top_k: int = 5,
        user_id: str | None = None
    ):
        """Raw similarity search without profile-based reranking."""
        insert_memory_query(user_id, namespace, query, filters, top_k)
        query_embedding = self.embedder.embed(query)
        rows = query_memories(user_id, namespace, query_embedding, filters, top_k)
        return [
            {
                "id": row[0],
                "content": row[1],
                "metadata": row[2],
                "created_at": row[3],
                "similarity": float(row[4]),
            }
            for row in rows
        ]

    def query_with_profile(
        self,
        namespace: str,
        query: str,
        filters: Dict[str, Any],
        mode: str,
        k: Optional[int],
        user_id: str,
        profile_overrides: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        High-level search with retrieval profile filtering + reranking.
        NOTE: Applies min_sim to RAW cosine similarity (not the reweighted score).
        """
        profile = get_profile(mode)
        if profile_overrides:
            # shallow override of dataclass fields
            for key, val in profile_overrides.items():
                if hasattr(profile, key):
                    setattr(profile, key, val)

        top_k = (k or profile.k)
        oversample = max(profile.oversample, top_k * 3)

        raw_hits = self.query_similar_memories(
            namespace=namespace,
            query=query,
            filters=filters or {},
            user_id=user_id,
            top_k=oversample,
        )
        # raw_hits is expected to include expired filtering upstream (DB query excludes expires_at < now).
        return rerank_hits(raw_hits, profile, k_override=top_k)

    def list_queries(self, user_id: str, namespace: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
        rows = get_memory_queries(user_id, namespace, start_date, end_date)
        return [
            {
                "namespace": row[0],
                "query_text": row[1],
                "filters": row[2],
                "top_k": row[3],
                "timestamp": row[4].isoformat()
            }
            for row in rows
        ]

    def delete_memory(self, namespace: str, content: str | None, metadata: dict | None, user_id: str = None) -> int:
        return delete_memories(user_id, namespace, content, metadata)

    def list_namespaces(self, user_id: str) -> list[str]:
        return get_namespaces_by_user(user_id)
