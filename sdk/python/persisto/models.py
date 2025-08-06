# sdk/python/persisto/models.py
from pydantic import BaseModel
from typing import Optional, Dict

class MemorySaveRequest(BaseModel):
    namespace: str
    content: str
    metadata: Optional[Dict] = {}

class QueryRequest(BaseModel):
    namespace: str
    query: str
    filters: Optional[Dict] = {}
    top_k: int = 5
