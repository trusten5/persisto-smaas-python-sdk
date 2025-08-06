# backend/memory_service.py

import os
import json
from openai import OpenAI
from db import conn, cursor


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def save_memory_to_db(namespace: str, content: str, metadata: dict):
    embedding = embed_text(content)
    cursor.execute(
        """
        INSERT INTO memories (namespace, content, metadata, embedding)
        VALUES (%s, %s, %s, %s)
        """,
        (namespace, content, json.dumps(metadata), embedding)
    )
    conn.commit()
