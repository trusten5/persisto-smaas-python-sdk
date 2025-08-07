# backend/routers/memory.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.memory_service import MemoryService

router = APIRouter()
memory_service = MemoryService()

# Classes

class MemoryPayload(BaseModel):
    namespace: str
    content: str
    metadata: dict = {}

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
async def save_memory(payload: MemoryPayload):
    memory_service.save_memory_to_db(payload.namespace, payload.content, payload.metadata)
    return {"status": "saved"}

@router.post("/memory/query")
async def query_memory(payload: QueryPayload):
    results = memory_service.query_similar_memories(payload.namespace, payload.query, payload.filters)
    return {"results": results}

@router.delete("/memory/delete")
def delete_memory(req: MemoryDeleteRequest):
    deleted_count = memory_service.delete_memory(
        namespace=req.namespace,
        content=req.content,
        metadata=req.metadata
    )
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="No matching memory found.")
    return {"status": "deleted", "count": deleted_count}