# backend/routers/memory.py
from fastapi import APIRouter, Request
from pydantic import BaseModel
from services.memory_service import save_memory_to_db, query_similar_memories

router = APIRouter()

# Classes

class MemoryPayload(BaseModel):
    namespace: str
    content: str
    metadata: dict = {}

class QueryPayload(BaseModel):
    namespace: str
    query: str
    filters: dict

# Endpoints

@router.post("/memory/save")
async def save_memory(payload: MemoryPayload):
    save_memory_to_db(payload.namespace, payload.content, payload.metadata)
    return {"status": "saved"}

@router.post("/memory/query")
async def query_memory(payload: QueryPayload):
    results = query_similar_memories(payload.namespace, payload.query, payload.filters)
    return {"results": results}