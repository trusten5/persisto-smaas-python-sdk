# sdk/python/persisto/client.py

import requests
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError, retry_if_exception_type
from .models import MemorySaveRequest, QueryRequest, DeleteRequest

# 🔹 Custom SDK Errors
class PersistoError(Exception): pass
class PersistoAuthError(PersistoError): pass
class PersistoNotFoundError(PersistoError): pass
class PersistoServerError(PersistoError): pass


class PersistoClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        """
        Initialize the PersistoClient.

        Args:
            api_key (str): Your Persisto API key.
            base_url (str): The base URL of the Persisto server (default: localhost).
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(0.5),
        retry=retry_if_exception_type((PersistoServerError, PersistoAuthError))
    )
    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        try:
            res = requests.request(method, url, headers=self.headers, **kwargs)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if status == 401:
                raise PersistoAuthError("Invalid API key") from e
            elif status == 404:
                raise PersistoNotFoundError("Resource not found") from e
            elif status >= 500:
                raise PersistoServerError("Server error") from e
            raise
        except RetryError as e:
            # 🧠 Unwrap and raise the original cause so users don’t see RetryError
            if e.last_attempt:
                raise e.last_attempt._exception  # cleanest way to get the original
            raise  # fallback: raise RetryError itself


    def save(self, namespace: str, content: str, metadata: Optional[dict] = None, ttl_seconds: Optional[int] = None) -> dict:
        """
        Save a memory to a namespace.

        Args:
            namespace (str): Namespace for the memory.
            content (str): Content to store.
            metadata (dict, optional): Additional metadata.
            ttl_seconds (int, optional): Time-to-live in seconds.

        Returns:
            dict: API response.
        """
        payload = MemorySaveRequest(
            namespace=namespace,
            content=content,
            metadata=metadata or {},
            ttl_seconds=ttl_seconds
        )
        res = self._request("POST", "/memory/save", json=payload.dict())
        return res.json()

    def query(self, namespace: str, query: str, filters: Optional[dict] = None, top_k: int = 5) -> list[dict]:
        """
        Query similar memories from a namespace.

        Args:
            namespace (str): Namespace to search in.
            query (str): Search query.
            filters (dict, optional): Metadata filters.
            top_k (int): Number of results to return.

        Returns:
            list[dict]: Matching memory results.
        """
        payload = QueryRequest(
            namespace=namespace,
            query=query,
            filters=filters or {},
            top_k=top_k
        )
        res = self._request("POST", "/memory/query", json=payload.dict())
        return res.json()["results"]

    def delete(self, namespace: str, content: Optional[str] = None, metadata: Optional[dict] = None) -> dict:
        """
        Delete memories by content or metadata.

        Args:
            namespace (str): Namespace to delete from.
            content (str, optional): Specific content to match.
            metadata (dict, optional): Metadata match filter.

        Returns:
            dict: API response.
        """
        payload = DeleteRequest(
            namespace=namespace,
            content=content,
            metadata=metadata
        )
        res = self._request("DELETE", "/memory/delete", json=payload.dict())
        return res.json()

    def list_namespaces(self) -> list[str]:
        """
        List all namespaces associated with the API key.

        Returns:
            list[str]: List of namespace strings.
        """
        res = self._request("GET", "/memory/namespaces")
        return res.json()["namespaces"]

    def list_queries(self, namespace: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> list:
        """
        List historical memory queries.

        Args:
            namespace (str, optional): Filter by namespace.
            start_date (str, optional): ISO start date filter.
            end_date (str, optional): ISO end date filter.

        Returns:
            list: List of past queries.
        """
        params = {}
        if namespace:
            params["namespace"] = namespace
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        res = self._request("GET", "/queries/list", params=params)
        return res.json()["queries"]
