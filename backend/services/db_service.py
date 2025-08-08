import json
import re
from db import cursor, conn
from typing import Optional
from datetime import datetime

def insert_memory(
    user_id: str,
    namespace: str,
    content: str,
    metadata: dict,
    embedding: list[float],
    expires_at: Optional[datetime] = None
):
    cursor.execute(
        """
        INSERT INTO memories (user_id, namespace, content, metadata, embedding, expires_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (user_id, namespace, content, json.dumps(metadata), embedding, expires_at)
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
    """
    Returns rows with:
      id, content, metadata, created_at, similarity

    - Orders by distance ASC for speed
    - SELECTs true similarity = 1 - distance (cosine opclass)
    - Excludes expired rows
    - Applies filter-based metadata matching
    NOTE: No hardcoded similarity filtering — handled by retrieval profiles
    """
    base_query = """
        SELECT
            id,
            content,
            metadata,
            created_at,
            1 - (embedding <-> %s::vector) AS similarity
        FROM memories
        WHERE user_id = %s
          AND namespace = %s
          AND (expires_at IS NULL OR expires_at > timezone('UTC', now()))
    """
    params = [embedding, user_id, namespace]

    # ✅ sanitize JSON keys to prevent SQL injection via keys
    for key, value in (filters or {}).items():
        if not re.match(r"^[a-zA-Z0-9_]+$", key):
            raise ValueError(f"Invalid filter key: {key}")
        base_query += f" AND metadata->>'{key}' = %s"
        params.append(str(value))

    base_query += """
        ORDER BY embedding <-> %s::vector   -- order by distance ASC
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
        (user_id, namespace, query_text, json.dumps(filters or {}), top_k)
    )
    conn.commit()

def get_memory_queries(user_id: str, namespace: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    query = """
        SELECT namespace, query_text, filters, top_k, timestamp
        FROM memory_queries
        WHERE user_id = %s
    """
    params = [user_id]

    if namespace:
        query += " AND namespace = %s"
        params.append(namespace)

    if start_date:
        query += " AND timestamp >= %s"
        params.append(start_date)

    if end_date:
        query += " AND timestamp <= %s"
        params.append(end_date)

    query += " ORDER BY timestamp DESC LIMIT 100"

    cursor.execute(query, params)
    return cursor.fetchall()

def get_namespaces_by_user(user_id: str) -> list[str]:
    cursor.execute(
        "SELECT DISTINCT namespace FROM memories WHERE user_id = %s",
        (user_id,)
    )
    return [row[0] for row in cursor.fetchall()]

def commit():
    conn.commit()
