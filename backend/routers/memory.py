# backend/routers/memory.py
from fastapi import APIRouter, Request
from pydantic import BaseModel
from memory_service import save_memory_to_db

router = APIRouter()

class MemoryPayload(BaseModel):
    namespace: str
    content: str
    metadata: dict = {}

@router.post("/memory/save")
async def save_memory(payload: MemoryPayload):
    save_memory_to_db(payload.namespace, payload.content, payload.metadata)
    return {"status": "saved"}

@router.post("/memory/query")
async def query_memory():
    return {"status": "query placeholder"}
