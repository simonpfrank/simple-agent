"""Unit tests for RAG improvements (Issues 7-B, 7-C)."""

import json
import tempfile
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from simple_agent.rag.collection import Collection, DocumentValidationError, IndexVersionError
from simple_agent.rag.document_loader import DocumentLoader


class TestDocumentStructureValidation:
    """Test document structure validation (Issue 7-B)."""

    def test_validate_document_with_required_fields(self):
        """Test valid document with all required fields."""
        document = {
            "id": "doc1",
            "content": "Sample content",
            "source": "/path/to/file.txt"
        }
        # Should not raise
        DocumentLoader.validate_document(document)

    def test_validate_document_missing_id(self):
        """Test document validation fails without id."""
        document = {
            "content": "Sample content",
            "source": "/path/to/file.txt"
        }
        with pytest.raises(DocumentValidationError, match="id"):
            DocumentLoader.validate_document(document)

    def test_validate_document_missing_content(self):
        """Test document validation fails without content."""
        document = {
            "id": "doc1",
            "source": "/path/to/file.txt"
        }
        with pytest.raises(DocumentValidationError, match="content"):
            DocumentLoader.validate_document(document)

    def test_validate_document_missing_source(self):
        """Test document validation fails without source."""
        document = {
            "id": "doc1",
            "content": "Sample content"
        }
        with pytest.raises(DocumentValidationError, match="source"):
            DocumentLoader.validate_document(document)

    def test_validate_document_empty_content(self):
        """Test document validation fails with empty content."""
        document = {
            "id": "doc1",
            "content": "",
            "source": "/path/to/file.txt"
        }
        with pytest.raises(DocumentValidationError, match="content.*empty"):
            DocumentLoader.validate_document(document)

    def test_validate_document_empty_id(self):
        """Test document validation fails with empty id."""
        document = {
            "id": "",
            "content": "Sample content",
            "source": "/path/to/file.txt"
        }
        with pytest.raises(DocumentValidationError, match="id.*empty"):
            DocumentLoader.validate_document(document)

    def test_validate_document_non_string_fields(self):
        """Test document validation fails with non-string required fields."""
        document = {
            "id": 123,
            "content": "Sample content",
            "source": "/path/to/file.txt"
        }
        with pytest.raises(DocumentValidationError, match="string"):
            DocumentLoader.validate_document(document)

    def test_validate_document_with_optional_fields(self):
        """Test document with optional fields is valid."""
        document = {
            "id": "doc1",
            "content": "Sample content",
            "source": "/path/to/file.txt",
            "tags": ["tag1", "tag2"],
            "author": "John Doe"
        }
        # Should not raise
        DocumentLoader.validate_document(document)

    def test_validate_documents_batch(self):
        """Test batch validation of multiple documents."""
        documents = [
            {
                "id": "doc1",
                "content": "Content 1",
                "source": "/path/to/file1.txt"
            },
            {
                "id": "doc2",
                "content": "Content 2",
                "source": "/path/to/file2.txt"
            }
        ]
        # Should not raise
        DocumentLoader.validate_documents(documents)

    def test_validate_documents_batch_with_invalid_document(self):
        """Test batch validation fails if any document is invalid."""
        documents = [
            {
                "id": "doc1",
                "content": "Content 1",
                "source": "/path/to/file1.txt"
            },
            {
                "id": "doc2",
                # Missing content
                "source": "/path/to/file2.txt"
            }
        ]
        with pytest.raises(DocumentValidationError):
            DocumentLoader.validate_documents(documents)


class TestIndexVersioning:
    """Test index versioning for embedding model changes (Issue 7-C)."""

    def test_collection_stores_index_version(self):
        """Test collection stores index version in metadata."""
        mock_chroma = Mock()
        metadata = {
            "embedding_model": "text-embedding-ada-002",
            "index_version": "1.0.0"
        }

        collection = Collection("test", mock_chroma, metadata)

        assert collection.metadata["index_version"] == "1.0.0"

    def test_collection_index_version_generated_if_missing(self):
        """Test collection generates index version if not provided."""
        mock_chroma = Mock()
        metadata = {
            "embedding_model": "text-embedding-ada-002"
        }

        collection = Collection("test", mock_chroma, metadata)

        # Should auto-generate a version
        assert "index_version" in collection.metadata
        assert collection.metadata["index_version"] is not None

    def test_check_index_compatibility(self):
        """Test checking if new embeddings are compatible with index."""
        mock_chroma = Mock()
        metadata = {
            "embedding_model": "text-embedding-ada-002",
            "index_version": "1.0.0"
        }

        collection = Collection("test", mock_chroma, metadata)

        # Same model should be compatible
        is_compatible = collection.is_embedding_compatible("text-embedding-ada-002")
        assert is_compatible is True

    def test_check_index_incompatibility_different_model(self):
        """Test incompatibility when embedding model changes."""
        mock_chroma = Mock()
        metadata = {
            "embedding_model": "text-embedding-ada-002",
            "index_version": "1.0.0"
        }

        collection = Collection("test", mock_chroma, metadata)

        # Different model should be incompatible
        is_compatible = collection.is_embedding_compatible(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        assert is_compatible is False

    def test_reindex_updates_version_and_model(self):
        """Test that reindexing updates embedding model and version."""
        mock_chroma = Mock()
        mock_chroma.get.return_value = {"ids": [], "metadatas": []}

        metadata = {
            "embedding_model": "text-embedding-ada-002",
            "index_version": "1.0.0",
            "original_path": "/path/to/docs"
        }

        collection = Collection("test", mock_chroma, metadata)
        old_version = collection.metadata["index_version"]

        # Mock the DocumentLoader.load_directory to return empty list
        with patch("simple_agent.rag.document_loader.DocumentLoader.load_directory") as mock_load:
            mock_load.return_value = []
            collection.reindex(embedding_model="sentence-transformers/all-MiniLM-L6-v2")

        # Version should be updated
        assert collection.metadata["index_version"] != old_version
        assert collection.metadata["embedding_model"] == "sentence-transformers/all-MiniLM-L6-v2"

    def test_version_format(self):
        """Test version follows semantic versioning format."""
        mock_chroma = Mock()
        metadata = {
            "embedding_model": "text-embedding-ada-002"
        }

        collection = Collection("test", mock_chroma, metadata)
        version = collection.metadata["index_version"]

        # Should match semantic versioning pattern (X.Y.Z)
        parts = version.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_get_index_version(self):
        """Test getting index version from collection."""
        mock_chroma = Mock()
        metadata = {
            "embedding_model": "text-embedding-ada-002",
            "index_version": "2.1.0"
        }

        collection = Collection("test", mock_chroma, metadata)

        version = collection.get_index_version()
        assert version == "2.1.0"

    def test_migration_info_when_incompatible(self):
        """Test getting migration info when index is incompatible."""
        mock_chroma = Mock()
        metadata = {
            "embedding_model": "text-embedding-ada-002",
            "index_version": "1.0.0"
        }

        collection = Collection("test", mock_chroma, metadata)

        # Get migration info for incompatible model
        info = collection.get_migration_info("sentence-transformers/all-MiniLM-L6-v2")

        assert info["current_model"] == "text-embedding-ada-002"
        assert info["new_model"] == "sentence-transformers/all-MiniLM-L6-v2"
        assert info["requires_reindex"] is True


class TestDocumentValidationError:
    """Test DocumentValidationError exception."""

    def test_document_validation_error_is_exception(self):
        """Test DocumentValidationError is an Exception."""
        assert issubclass(DocumentValidationError, Exception)

    def test_document_validation_error_with_message(self):
        """Test DocumentValidationError can be raised with message."""
        with pytest.raises(DocumentValidationError, match="test message"):
            raise DocumentValidationError("test message")


class TestIndexVersionError:
    """Test IndexVersionError exception."""

    def test_index_version_error_is_exception(self):
        """Test IndexVersionError is an Exception."""
        assert issubclass(IndexVersionError, Exception)

    def test_index_version_error_with_message(self):
        """Test IndexVersionError can be raised with message."""
        with pytest.raises(IndexVersionError, match="test message"):
            raise IndexVersionError("test message")
