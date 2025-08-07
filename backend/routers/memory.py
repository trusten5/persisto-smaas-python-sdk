# backend/routers/memory.py
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, Field
from services.memory_service import MemoryService
from utils.auth import get_user_id_from_api_key
from datetime import datetime, timedelta
from typing import Optional, Literal, Dict, Any

router = APIRouter()
memory_service = MemoryService()

# ---- Classes

class MemoryPayload(BaseModel):
    namespace: str
    content: str
    metadata: dict = {}
    ttl_seconds: Optional[int] = None

class QueryPayload(BaseModel):
    namespace: str
    query: str
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    mode: Optional[Literal["strict", "fuzzy", "recency"]] = "strict"
    k: Optional[int] = None  # optional override per-call
    # profile: Optional[CustomProfile] = None  # keep commented until you want overrides

class MemoryDeleteRequest(BaseModel):
    namespace: str
    content: str | None = None
    metadata: dict | None = None

# ---- Endpoints

@router.post("/memory/save")
async def save_memory(payload: MemoryPayload, request: Request):
    user_id = await get_user_id_from_api_key(request)
    expires_at = None
    if payload.ttl_seconds:
        expires_at = datetime.utcnow() + timedelta(seconds=payload.ttl_seconds)

    memory_service.save_memory_to_db(
        namespace=payload.namespace,
        content=payload.content,
        metadata=payload.metadata,
        user_id=user_id,
        expires_at=expires_at
    )
    return {"status": "saved"}

@router.post("/memory/query")
async def query_memory(payload: QueryPayload, request: Request):
    user_id = await get_user_id_from_api_key(request)

    # Distinguish "no hits" vs "namespace doesn't exist"
    namespaces = set(memory_service.list_namespaces(user_id))
    if payload.namespace not in namespaces:
        # Unknown namespace for this user -> 404
        raise HTTPException(status_code=404, detail=f"Namespace '{payload.namespace}' not found.")

    results = memory_service.query_with_profile(
        namespace=payload.namespace,
        query=payload.query,
        filters=payload.filters or {},
        mode=payload.mode or "strict",
        k=payload.k,
        user_id=user_id,
    )

    # Return empty array instead of 404 so SDK tests don’t explode on normal "no hits"
    return {"results": results or []}

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

@router.get("/queries/list")
async def list_queries(
    request: Request,
    namespace: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    user_id = await get_user_id_from_api_key(request)
    results = memory_service.list_queries(user_id, namespace, start_date, end_date)
    return {"queries": results}
