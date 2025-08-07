# backend/routers/memory.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from services.memory_service import MemoryService
from utils.auth import get_user_id_from_api_key
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()
memory_service = MemoryService()

# Classes

class MemoryPayload(BaseModel):
    namespace: str
    content: str
    metadata: dict = {}
    ttl_seconds: Optional[int] = None

class QueryPayload(BaseModel):
    namespace: str
    query: str
    filters: dict

class MemoryDeleteRequest(BaseModel):
    namespace: str
    content: str | None = None
    metadata: dict | None = None

# Endpoints

@router.post("/memory/save")
async def save_memory(payload: MemoryPayload, request: Request):
    user_id = await get_user_id_from_api_key(request)

    # 🔹 Compute expires_at from ttl_seconds
    expires_at = None
    if payload.ttl_seconds:
        expires_at = datetime.utcnow() + timedelta(seconds=payload.ttl_seconds)

    memory_service.save_memory_to_db(
        namespace=payload.namespace,
        content=payload.content,
        metadata=payload.metadata,
        user_id=user_id,
        expires_at=expires_at  # 🧠 Pass to DB
    )
    return {"status": "saved"}

@router.post("/memory/query")
async def query_memory(payload: QueryPayload, request: Request):
    user_id = await get_user_id_from_api_key(request)
    results = memory_service.query_similar_memories(payload.namespace, payload.query, payload.filters, user_id=user_id)
    return {"results": results}

@router.delete("/memory/delete")
async def delete_memory(req: MemoryDeleteRequest, request: Request):
    user_id = await get_user_id_from_api_key(request)
    deleted_count = memory_service.delete_memory(
        namespace=req.namespace,
        content=req.content,
        metadata=req.metadata,
        user_id=user_id
    )
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="No matching memory found.")
    return {"status": "deleted", "count": deleted_count}

@router.get("/memory/namespaces")
async def get_namespaces(request: Request):
    user_id = await get_user_id_from_api_key(request)
    return {"namespaces": memory_service.list_namespaces(user_id)}
