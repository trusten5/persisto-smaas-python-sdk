# sdk/python/persisto/client.py

import os
import requests
from .models import MemorySaveRequest, QueryRequest
from typing import Optional

class PersistoClient:
    """
    A Python SDK client for Persisto: Semantic Memory-as-a-Service (SMaaS).
    
    Use this client to save and query long-term memory for your AI applications.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "http://localhost:8000"):
        """
        Initialize the Persisto client.

        Args:
            api_key (str, optional): Your API key for authentication. Falls back to env variable `PERSISTO_API_KEY`.
            base_url (str): The base URL of the Persisto API.
        """
        self.api_key = api_key or os.getenv("PERSISTO_API_KEY")
        if not self.api_key:
            raise ValueError("Persisto API key is required. Pass it to the constructor or set PERSISTO_API_KEY env var.")
        
        self.base_url = base_url

    def save(self, namespace: str, content: str, metadata: dict = {}) -> dict:
        """
        Save a memory into Persisto.

        Args:
            namespace (str): A logical grouping for your memory.
            content (str): The memory content to store.
            metadata (dict): Optional metadata (e.g., source, type).

        Returns:
            dict: API response with save status.
        """
        payload = MemorySaveRequest(namespace=namespace, content=content, metadata=metadata)
        res = requests.post(f"{self.base_url}/memory/save", json=payload.dict())
        res.raise_for_status()
        return res.json()

    def query(self, namespace: str, query: str, filters: dict = {}, top_k: int = 5) -> list[dict]:
        """
        Query semantic memory using a natural language prompt.

        Args:
            namespace (str): The namespace to search within.
            query (str): Your natural language question.
            filters (dict): Optional metadata filters.
            top_k (int): Number of top results to return.

        Returns:
            list[dict]: List of memory chunks ranked by similarity.
        """
        payload = QueryRequest(namespace=namespace, query=query, filters=filters, top_k=top_k)
        res = requests.post(f"{self.base_url}/memory/query", json=payload.dict())
        res.raise_for_status()
        return res.json()["results"]
    
    def delete(self, namespace: str, content: str = None, metadata: dict = None) -> dict:
        payload = {"namespace": namespace}
        if content:
            payload["content"] = content
        if metadata:
            payload["metadata"] = metadata

        res = requests.delete(f"{self.base_url}/memory/delete", json=payload)
        res.raise_for_status()
        return res.json()
