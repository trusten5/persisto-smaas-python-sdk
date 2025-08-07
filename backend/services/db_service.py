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

def delete_memories(namespace: str, content: str | None, metadata: dict | None) -> int:
    query = "DELETE FROM memories WHERE namespace = %s"
    params = [namespace]

    if content:
        query += " AND content = %s"
        params.append(content)

    if metadata:
        query += " AND metadata @> %s::jsonb"
        params.append(json.dumps(metadata))

    cursor.execute(query, params)
    count = cursor.rowcount
    commit()
    return count

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

def insert_memory_query(namespace: str, query_text: str, filters: dict, top_k: int):
    cursor.execute(
        """
        INSERT INTO memory_queries (namespace, query_text, filters, top_k)
        VALUES (%s, %s, %s, %s)
        """,
        (namespace, query_text, json.dumps(filters), top_k)
    )
    conn.commit()

def commit():
    conn.commit()
