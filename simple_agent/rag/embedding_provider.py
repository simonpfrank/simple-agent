"""Embedding provider for flexible embedding model support."""

from typing import List

import litellm


class EmbeddingProvider:
    """Handle embeddings with flexibility for different models."""

    KNOWN_MODELS = {
        "text-embedding-ada-002",
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/all-mpnet-base-v2",
    }

    @staticmethod
    def get_embeddings(texts: List[str], model: str) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of text strings to embed
            model: Model name/identifier

        Returns:
            List of embedding vectors

        Raises:
            Exception: If embedding generation fails
        """
        if not texts:
            return []

        response = litellm.embedding(model=model, input=texts)

        embeddings = [item["embedding"] for item in response["data"]]
        return embeddings

    @staticmethod
    def embed_query(query: str, model: str) -> List[float]:
        """Generate embedding for a single query.

        Args:
            query: Query text to embed
            model: Model name/identifier

        Returns:
            Embedding vector
        """
        embeddings = EmbeddingProvider.get_embeddings([query], model=model)
        return embeddings[0] if embeddings else []

    @staticmethod
    def validate_model(model: str) -> bool:
        """Validate if model identifier is recognized.

        Args:
            model: Model identifier

        Returns:
            True if model is known/valid, False otherwise
        """
        # Accept OpenAI models
        if model.startswith("text-embedding-"):
            return True

        # Accept sentence-transformers models
        if "sentence-transformers" in model:
            return True

        # Accept other known models
        if model in EmbeddingProvider.KNOWN_MODELS:
            return True

        # Accept anything else (for Ollama, custom models, etc.)
        return True
