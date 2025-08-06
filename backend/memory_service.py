# backend/memory_service.py

import os
import json
from openai import OpenAI
from db import conn, cursor
import re
from typing import List
from utils.chunker import chunk_text


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def save_memory_to_db(namespace: str, content: str, metadata: dict):
    chunks = chunk_text(content)

    for chunk in chunks:
        embedding = embed_text(chunk)
        cursor.execute(
            """
            INSERT INTO memories (namespace, content, metadata, embedding)
            VALUES (%s, %s, %s, %s)
            """,
            (namespace, chunk, json.dumps(metadata), embedding)
        )

    conn.commit()


def query_similar_memories(namespace: str, query: str, filters: dict = {}, top_k: int = 5):
    query_embedding = embed_text(query)

    base_query = """
        SELECT content, metadata, embedding <-> %s::vector AS similarity
        FROM memories
        WHERE namespace = %s
    """
    params = [query_embedding, namespace]

    # Dynamically add metadata filters
    for key, value in filters.items():
        base_query += f" AND metadata->>%s = %s"
        params.extend([key, value])

    base_query += """
        ORDER BY embedding <-> %s::vector
        LIMIT %s
    """
    params.extend([query_embedding, top_k])

    cursor.execute(base_query, params)
    rows = cursor.fetchall()
    
    return [
        {
            "content": row[0],
            "metadata": row[1],
            "similarity": row[2]
        }
        for row in rows
    ]
