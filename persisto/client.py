# sdk/python/persisto/client.py
from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests


# =========================
# Errors
# =========================

class PersistoError(Exception):
    """Base SDK error with optional HTTP status and raw body."""
    def __init__(self, message: str, status: Optional[int] = None, body: Optional[str] = None):
        super().__init__(message)
        self.status = status
        self.body = body


class PersistoAuthError(PersistoError):
    """401/403 authentication/authorization errors."""


class PersistoNotFoundError(PersistoError):
    """404 not found errors."""


class PersistoRateLimitError(PersistoError):
    """429 rate-limit errors."""


# =========================
# Client
# =========================

class PersistoClient:
    """
    Minimal Python client for Persisto.

    Recommended usage:
        from persisto import Client
        c = Client(api_key="sk_live_xxx", base_url="https://<your-backend-host>")
        c.save(namespace="support-bot", content="Customer prefers dark mode", metadata={"user_id":"u_123"})
        hits = c.query(namespace="support-bot", query="theme preference", filters={"user_id":"u_123"}, k=5)

    Constructor:
        PersistoClient(
            api_key: str,
            base_url: Optional[str] = None,
            timeout: int = 15,
            retries: int = 3,
        )

    Env convenience (if base_url not provided):
        PERSISTO_API_URL  (default: http://localhost:8000)
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None, timeout: int = 15, retries: int = 3):
        if not api_key:
            raise ValueError("Missing API key")
        self.api_key = api_key
        self.base_url = (base_url or os.getenv("PERSISTO_API_URL") or "http://localhost:8000").rstrip("/")
        self.timeout = int(timeout)
        self.retries = max(0, int(retries))

        # Reuse TCP connections
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    # Context manager support
    def close(self) -> None:
        try:
            self._session.close()
        except Exception:
            pass

    def __enter__(self) -> "PersistoClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ---------- Public API ----------

    def save(
        self,
        *,
        namespace: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "namespace": namespace,
            "content": content,
            "metadata": metadata or {},
        }
        if ttl_seconds is not None:
            payload["ttl_seconds"] = int(ttl_seconds)
        return self._request("POST", "/memory/save", json=payload)

    def query(
        self,
        *,
        namespace: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        mode: Optional[str] = None,            # "strict" | "fuzzy" | "recency" (optional)
        k: Optional[int] = None,               # optional override for top-k
        profile: Optional[Dict[str, Any]] = None,  # optional client-side config; server may ignore
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "namespace": namespace,
            "query": query,
            "filters": filters or {},
        }
        if mode:
            payload["mode"] = mode
        if k is not None:
            payload["k"] = int(k)
        if profile:
            payload["profile"] = profile
        return self._request("POST", "/memory/query", json=payload)

    def delete(
        self,
        *,
        namespace: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"namespace": namespace}
        if content is not None:
            payload["content"] = content
        if metadata is not None:
            payload["metadata"] = metadata
        return self._request("DELETE", "/memory/delete", json=payload)

    def list_namespaces(self) -> List[str]:
        resp = self._request("GET", "/memory/namespaces")
        return resp.get("namespaces", [])

    def list_queries(
        self,
        *,
        namespace: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if namespace:
            params["namespace"] = namespace
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        resp = self._request("GET", "/queries/list", params=params)
        return resp.get("queries", [])

    # ---------- Internal HTTP ----------

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"

        attempt = 0
        backoff = 0.5
        while True:
            try:
                r = self._send(method, url, json=json, params=params, timeout=self.timeout)
            except requests.RequestException as e:
                if attempt >= self.retries:
                    raise PersistoError(f"Network error after {attempt+1} attempts: {e}")
                attempt += 1
                time.sleep(backoff)
                backoff = min(backoff * 2, 8.0)
                continue

            # Error mapping
            if r.status_code in (401, 403):
                raise PersistoAuthError("Unauthorized: invalid API key or insufficient scope", status=r.status_code, body=r.text)
            if r.status_code == 404:
                raise PersistoNotFoundError("Not found", status=r.status_code, body=r.text)
            if r.status_code == 429:
                if attempt >= self.retries:
                    raise PersistoRateLimitError("Rate limited", status=r.status_code, body=r.text)
                retry_after = r.headers.get("Retry-After")
                try:
                    sleep_s = float(retry_after) if retry_after is not None else backoff
                except ValueError:
                    sleep_s = backoff
                time.sleep(max(0.1, sleep_s))
                attempt += 1
                backoff = min(backoff * 2, 8.0)
                continue
            if 500 <= r.status_code < 600:
                if attempt >= self.retries:
                    raise PersistoError(f"Server error {r.status_code}", status=r.status_code, body=r.text)
                attempt += 1
                time.sleep(backoff)
                backoff = min(backoff * 2, 8.0)
                continue

            # Success
            if r.status_code == 204 or not r.content:
                return {}
            try:
                return r.json()
            except ValueError:
                return {"raw": r.text}

    def _send(
        self,
        method: str,
        url: str,
        *,
        json: Optional[Dict[str, Any]],
        params: Optional[Dict[str, Any]],
        timeout: int,
    ) -> requests.Response:
        m = method.upper()
        if m == "GET":
            return self._session.get(url, params=params, timeout=timeout)
        elif m in ("POST", "PUT", "PATCH", "DELETE"):
            return self._session.request(m, url, json=json, params=params, timeout=timeout)
        raise PersistoError(f"Unsupported HTTP method: {method}")
