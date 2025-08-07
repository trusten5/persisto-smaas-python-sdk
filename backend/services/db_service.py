# backend/services/db_service.py
import json
from db import cursor, conn

def insert_memory(user_id: str, namespace: str, content: str, metadata: dict, embedding: list[float]):
    cursor.execute(
        """
        INSERT INTO memories (user_id, namespace, content, metadata, embedding)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, namespace, content, json.dumps(metadata), embedding)
    )

def delete_memories(user_id: str, namespace: str, content: str | None, metadata: dict | None) -> int:
    query = "DELETE FROM memories WHERE user_id = %s AND namespace = %s"
    params = [user_id, namespace]

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

def query_memories(user_id: str, namespace: str, embedding: list[float], filters: dict, top_k: int):
    base_query = """
        SELECT content, metadata, embedding <-> %s::vector AS similarity
        FROM memories
        WHERE user_id = %s AND namespace = %s
    """
    params = [embedding, user_id, namespace]

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

def insert_memory_query(user_id: str, namespace: str, query_text: str, filters: dict, top_k: int):
    cursor.execute(
        """
        INSERT INTO memory_queries (user_id, namespace, query_text, filters, top_k)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, namespace, query_text, json.dumps(filters), top_k)
    )
    conn.commit()

def commit():
    conn.commit()
