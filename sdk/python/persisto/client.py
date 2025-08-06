# sdk/python/persisto/client.py
import requests
from .models import MemorySaveRequest, QueryRequest

class PersistoClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url

    def save(self, namespace: str, content: str, metadata: dict = {}) -> dict:
        payload = MemorySaveRequest(namespace=namespace, content=content, metadata=metadata)
        res = requests.post(f"{self.base_url}/memory/save", json=payload.dict())
        res.raise_for_status()
        return res.json()

    def query(self, namespace: str, query: str, filters: dict = {}, top_k: int = 5) -> list[dict]:
        payload = QueryRequest(
            namespace=namespace,
            query=query,
            filters=filters,
            top_k=top_k
        )
        res = requests.post(f"{self.base_url}/memory/query", json=payload.dict())
        res.raise_for_status()
        return res.json()["results"]
