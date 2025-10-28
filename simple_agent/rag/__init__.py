"""RAG (Retrieval-Augmented Generation) system for knowledge-augmented agents."""

from simple_agent.rag.collection import Collection
from simple_agent.rag.collection_manager import CollectionManager
from simple_agent.rag.exceptions import (
    CollectionError,
    DocumentLoadError,
    EmbeddingError,
)

__all__ = [
    "Collection",
    "CollectionManager",
    "CollectionError",
    "DocumentLoadError",
    "EmbeddingError",
]
