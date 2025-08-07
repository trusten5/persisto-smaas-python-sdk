from utils.chunker import chunk_text
from services.db_service import insert_memory, query_memories, commit, insert_memory_query, delete_memories
from services.embedder import BaseEmbedder
from services.openai_embedder import OpenAIEmbedder


class MemoryService:
    def __init__(self, embedder: BaseEmbedder = OpenAIEmbedder()):
        self.embedder = embedder

    def save_memory_to_db(self, namespace: str, content: str, metadata: dict):
        chunks = chunk_text(content)
        for chunk in chunks:
            embedding = self.embedder.embed(chunk)
            insert_memory(namespace, chunk, metadata, embedding)
        commit()

    def query_similar_memories(self, namespace: str, query: str, filters: dict = {}, top_k: int = 5):
        insert_memory_query(namespace, query, filters, top_k)
        query_embedding = self.embedder.embed(query)
        rows = query_memories(namespace, query_embedding, filters, top_k)
        return [
            {
                "content": row[0],
                "metadata": row[1],
                "similarity": row[2]
            }
            for row in rows
        ]
    
    def delete_memory(self, namespace: str, content: str | None, metadata: dict | None) -> int:
        return delete_memories(namespace, content, metadata)