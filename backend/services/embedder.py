# backend/services/embedder.py
from abc import ABC, abstractmethod

class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass
