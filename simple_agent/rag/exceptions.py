"""Exceptions for RAG system."""


class CollectionError(Exception):
    """Base exception for collection-related errors."""

    pass


class DocumentLoadError(CollectionError):
    """Raised when document loading fails."""

    pass


class EmbeddingError(CollectionError):
    """Raised when embedding generation fails."""

    pass
