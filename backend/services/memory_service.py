# backend/services/memory_service.py
from utils.chunker import chunk_text
from services.db_service import insert_memory, query_memories, commit, insert_memory_query, delete_memories, get_namespaces_by_user, get_memory_queries
from services.embedder import BaseEmbedder
from services.openai_embedder import OpenAIEmbedder
from typing import Optional
from datetime import datetime

class MemoryService:
    def __init__(self, embedder: BaseEmbedder = OpenAIEmbedder()):
        self.embedder = embedder

    def save_memory_to_db(self, namespace: str, content: str, metadata: dict, user_id: str, expires_at: Optional[datetime] = None):
        chunks = chunk_text(content)
        for chunk in chunks:
            embedding = self.embedder.embed(chunk)
            insert_memory(user_id, namespace, chunk, metadata, embedding, expires_at)
        commit()

    def query_similar_memories(self, namespace: str, query: str, filters: dict = {}, top_k: int = 5, user_id: str = None):
        insert_memory_query(user_id, namespace, query, filters, top_k)
        query_embedding = self.embedder.embed(query)
        rows = query_memories(user_id, namespace, query_embedding, filters, top_k)
        return [
            {
                "content": row[0],
                "metadata": row[1],
                "similarity": row[2]
            }
            for row in rows
        ]
    
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
