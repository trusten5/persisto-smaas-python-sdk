# sdk/python/persisto/client.py

import requests
from .models import MemorySaveRequest, QueryRequest, DeleteRequest
from typing import Optional


class PersistoClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        """
        Initialize the PersistoClient with an API key and base URL.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def save(self, namespace: str, content: str, metadata: Optional[dict] = None, ttl_seconds: Optional[int] = None) -> dict:
        """
        Save content to a namespace with optional metadata.
        """
        payload = MemorySaveRequest(
            namespace=namespace,
            content=content,
            metadata=metadata or {},
            ttl_seconds = ttl_seconds
        )
        res = requests.post(
            f"{self.base_url}/memory/save",
            json=payload.dict(),
            headers=self.headers
        )
        res.raise_for_status()
        return res.json()

    def query(self, namespace: str, query: str, filters: Optional[dict] = None, top_k: int = 5) -> list[dict]:
        """
        Query the memory store for similar content.
        """
        payload = QueryRequest(
            namespace=namespace,
            query=query,
            filters=filters or {},
            top_k=top_k
        )
        res = requests.post(
            f"{self.base_url}/memory/query",
            json=payload.dict(),
            headers=self.headers
        )
        res.raise_for_status()
        return res.json()["results"]

    def delete(self, namespace: str, content: Optional[str] = None, metadata: Optional[dict] = None) -> dict:
        """
        Delete content from a namespace by content or metadata.
        """
        payload = DeleteRequest(
            namespace=namespace,
            content=content,
            metadata=metadata
        )
        res = requests.delete(
            f"{self.base_url}/memory/delete",
            json=payload.dict(),
            headers=self.headers
        )
        res.raise_for_status()
        return res.json()
    
    def list_namespaces(self) -> list[str]:
        """
        List all users namespaces
        """
        res = requests.get(f"{self.base_url}/memory/namespaces", headers=self.headers)
        res.raise_for_status()
        return res.json()["namespaces"]
    
    def list_queries(self, namespace: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> list:
        params = {}
        if namespace:
            params["namespace"] = namespace
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        res = requests.get(
            f"{self.base_url}/queries/list",
            headers=self.headers,
            params=params
        )
        res.raise_for_status()
        return res.json()["queries"]


