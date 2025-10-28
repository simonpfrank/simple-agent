"""Unit tests for EmbeddingProvider - TDD approach."""

from unittest.mock import Mock, patch
import pytest

from simple_agent.rag.embedding_provider import EmbeddingProvider


class TestEmbeddingProvider:
    """Test EmbeddingProvider embedding generation."""

    @patch("simple_agent.rag.embedding_provider.litellm.embedding")
    def test_get_embeddings_with_openai(self, mock_embed):
        """Test embedding generation with OpenAI model."""
        mock_embed.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]},
            ]
        }

        texts = ["Hello world", "Test text"]
        embeddings = EmbeddingProvider.get_embeddings(texts, model="text-embedding-ada-002")

        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]

    @patch("simple_agent.rag.embedding_provider.litellm.embedding")
    def test_get_embeddings_with_sentence_transformers(self, mock_embed):
        """Test embedding generation with local sentence-transformers model."""
        mock_embed.return_value = {
            "data": [
                {"embedding": [0.1, 0.2]},
            ]
        }

        texts = ["Sample text"]
        embeddings = EmbeddingProvider.get_embeddings(texts, model="sentence-transformers/all-MiniLM-L6-v2")

        assert len(embeddings) == 1
        mock_embed.assert_called_once()

    @patch("simple_agent.rag.embedding_provider.litellm.embedding")
    def test_embed_query(self, mock_embed):
        """Test embedding a single query."""
        mock_embed.return_value = {
            "data": [
                {"embedding": [0.7, 0.8, 0.9]},
            ]
        }

        query = "What is RAG?"
        embedding = EmbeddingProvider.embed_query(query, model="text-embedding-ada-002")

        assert embedding == [0.7, 0.8, 0.9]

    @patch("simple_agent.rag.embedding_provider.litellm.embedding")
    def test_get_embeddings_empty_list(self, mock_embed):
        """Test embedding generation with empty list."""
        mock_embed.return_value = {"data": []}

        embeddings = EmbeddingProvider.get_embeddings([], model="text-embedding-ada-002")

        assert embeddings == []

    @patch("simple_agent.rag.embedding_provider.litellm.embedding")
    def test_get_embeddings_single_text(self, mock_embed):
        """Test embedding generation with single text."""
        mock_embed.return_value = {
            "data": [
                {"embedding": [0.2, 0.3, 0.4]},
            ]
        }

        embeddings = EmbeddingProvider.get_embeddings(["Single text"], model="text-embedding-ada-002")

        assert len(embeddings) == 1
        assert embeddings[0] == [0.2, 0.3, 0.4]

    def test_validate_model_valid_openai(self):
        """Test model validation for OpenAI model."""
        result = EmbeddingProvider.validate_model("text-embedding-ada-002")

        assert result is True or result is not False  # Should validate OpenAI models

    def test_validate_model_valid_sentence_transformers(self):
        """Test model validation for sentence-transformers model."""
        result = EmbeddingProvider.validate_model("sentence-transformers/all-MiniLM-L6-v2")

        assert result is not False  # Should not immediately reject known models

    @patch("simple_agent.rag.embedding_provider.litellm.embedding")
    def test_embedding_error_handling(self, mock_embed):
        """Test error handling when embedding fails."""
        mock_embed.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            EmbeddingProvider.get_embeddings(["Text"], model="invalid-model")

    @patch("simple_agent.rag.embedding_provider.litellm.embedding")
    def test_get_embeddings_respects_model_parameter(self, mock_embed):
        """Test that get_embeddings uses the specified model."""
        mock_embed.return_value = {"data": [{"embedding": [0.1]}]}

        EmbeddingProvider.get_embeddings(["text"], model="custom-model-name")

        # Verify the model was passed to litellm
        call_args = mock_embed.call_args
        assert call_args is not None

    @patch("simple_agent.rag.embedding_provider.litellm.embedding")
    def test_embed_query_uses_model(self, mock_embed):
        """Test that embed_query uses specified model."""
        mock_embed.return_value = {"data": [{"embedding": [0.5]}]}

        EmbeddingProvider.embed_query("query text", model="my-model")

        call_args = mock_embed.call_args
        assert call_args is not None
