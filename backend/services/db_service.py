# backend/services/db_service.py
import json
from db import cursor, conn
from typing import Optional
from datetime import datetime

def insert_memory(user_id: str, namespace: str, content: str, metadata: dict, embedding: list[float], expires_at: Optional[datetime] = None
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
    # Debug
    # print("[DEBUG] expires_at filter active")

    base_query = """
        SELECT content, metadata, embedding <-> %s::vector AS similarity
        FROM memories
        WHERE user_id = %s AND namespace = %s
          AND (expires_at IS NULL OR expires_at > timezone('UTC', now()))
    """

    params = [embedding, user_id, namespace]

    for key, value in filters.items():
        base_query += f" AND metadata->>'{key}' = %s"
        params.append(value)

    base_query += """
        ORDER BY embedding <-> %s::vector
        LIMIT %s
    """
    # ✅ These must come after all filters are added
    params.extend([embedding, top_k])

    # Debug
    # print("[DEBUG] SQL Query:", base_query)

    cursor.execute(base_query, params)
    results = cursor.fetchall()
    
    # Debug Section 
    # print("[DEBUG] Results returned:", len(results))
    # for row in results:
    #     if row[0] == "This memory will self-destruct":
    #         print("[DEBUG] ❌ Expired memory leaked through:", row)
    # for row in results:
    #     if "self-destruct" in row[0]:
    #         print("[DEBUG] ⏱ Expired? Checking timestamp in DB...")
    #         cursor.execute(
    #             "SELECT expires_at FROM memories WHERE content = %s AND user_id = %s",
    #             (row[0], user_id)
    #         )
    #         expiration_check = cursor.fetchall()
    #         print("[DEBUG] → expires_at values:", expiration_check)


    return results


def insert_memory_query(user_id: str, namespace: str, query_text: str, filters: dict, top_k: int):
    cursor.execute(
        """
        INSERT INTO memory_queries (user_id, namespace, query_text, filters, top_k)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, namespace, query_text, json.dumps(filters), top_k)
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
