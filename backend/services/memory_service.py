# backend/memory.py

from utils.chunker import chunk_text
from services.embed_service import embed_text
from services.db_service import insert_memory, query_memories, commit



def save_memory_to_db(namespace: str, content: str, metadata: dict):
    chunks = chunk_text(content)
    for chunk in chunks:
        embedding = embed_text(chunk)
        insert_memory(namespace, chunk, metadata, embedding)
    commit()

def query_similar_memories(namespace: str, query: str, filters: dict = {}, top_k: int = 5):
    query_embedding = embed_text(query)
    rows = query_memories(namespace, query_embedding, filters, top_k)
    return [
        {
            "content": row[0],
            "metadata": row[1],
            "similarity": row[2]
        }
        for row in rows
    ]