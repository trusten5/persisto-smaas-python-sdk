# backend/services/db_service.py
import json
from db import cursor, conn

def insert_memory(namespace: str, content: str, metadata: dict, embedding: list[float]):
    cursor.execute(
        """
        INSERT INTO memories (namespace, content, metadata, embedding)
        VALUES (%s, %s, %s, %s)
        """,
        (namespace, content, json.dumps(metadata), embedding)
    )

def query_memories(namespace: str, embedding: list[float], filters: dict, top_k: int):
    base_query = """
        SELECT content, metadata, embedding <-> %s::vector AS similarity
        FROM memories
        WHERE namespace = %s
    """
    params = [embedding, namespace]

    for key, value in filters.items():
        base_query += f" AND metadata->>%s = %s"
        params.extend([key, value])

    base_query += """
        ORDER BY embedding <-> %s::vector
        LIMIT %s
    """
    params.extend([embedding, top_k])

    cursor.execute(base_query, params)
    return cursor.fetchall()

def commit():
    conn.commit()
