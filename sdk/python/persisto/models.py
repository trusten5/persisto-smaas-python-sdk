# sdk/python/persisto/models.py

from pydantic import BaseModel
from typing import Optional, Dict


class MemorySaveRequest(BaseModel):
    namespace: str
    content: str
    metadata: Dict = {}  # Optional but default to empty dict
    ttl_seconds: Optional[int] = None

class QueryRequest(BaseModel):
    namespace: str
    query: str
    filters: Dict = {}  # Optional but default to empty dict
    top_k: int = 5


class DeleteRequest(BaseModel):
    namespace: str
    content: Optional[str] = None
    metadata: Optional[Dict] = None
