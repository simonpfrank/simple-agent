"""Integration tests for Phase 2.3 RAG Foundation."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from simple_agent.rag.collection_manager import CollectionManager
from simple_agent.rag.document_loader import DocumentLoader


class TestRAGEndToEnd:
    """Test RAG system end-to-end integration."""

    @pytest.fixture
    def temp_docs_dir(self):
        """Create temporary directory with test documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test documents
            doc1_path = Path(tmpdir) / "doc1.txt"
            doc1_path.write_text("Machine learning is a subset of artificial intelligence.")

            doc2_path = Path(tmpdir) / "doc2.txt"
            doc2_path.write_text("Deep learning uses neural networks with many layers.")

            yield tmpdir

    @pytest.fixture
    def collection_manager(self):
        """Create CollectionManager with temporary Chroma database."""
        import shutil
        import platform
        
        tmpdir = tempfile.mkdtemp()
        try:
            manager = CollectionManager(collections_dir=tmpdir)
            yield manager
            # Cleanup ChromaDB resources
            manager.cleanup()
        finally:
            # Best effort cleanup - on Windows, ChromaDB may hold locks
            try:
                shutil.rmtree(tmpdir)
            except (PermissionError, OSError):
                # On Windows, SQLite files may still be locked - ignore
                if platform.system() != "Windows":
                    raise

    def test_create_collection_basic(self, collection_manager):
        """Test creating a basic collection."""
        collection = collection_manager.create_collection(
            name="test_collection",
            embedding_model="text-embedding-ada-002",
            chunk_size=500,
            chunk_overlap=100,
        )

        assert collection is not None
        assert collection.name == "test_collection"
        assert collection.metadata["embedding_model"] == "text-embedding-ada-002"

    def test_collection_with_agent_connection(self, collection_manager):
        """Test connecting agent to collection."""
        col = collection_manager.create_collection(name="research")
        collection_manager.connect_agent("researcher_agent", "research")

        connected = collection_manager.get_agent_collection("researcher_agent")
        assert connected is not None
        assert connected.name == "research"

    def test_document_loading(self, temp_docs_dir):
        """Test loading documents from directory."""
        docs = DocumentLoader.load_directory(temp_docs_dir)

        assert len(docs) == 2
        assert all("content" in doc for doc in docs)
        assert all("source" in doc for doc in docs)
        assert "machine learning" in docs[0]["content"].lower()

    def test_document_chunking(self):
        """Test document chunking with overlap."""
        text = "A" * 1000

        chunks = DocumentLoader.chunk_text(text, chunk_size=300, overlap=50)

        assert len(chunks) > 1
        # Each chunk should be at most chunk_size
        for chunk in chunks:
            assert len(chunk) <= 300

    @patch("simple_agent.rag.embedding_provider.litellm.embedding")
    def test_collection_add_documents(self, mock_embed, collection_manager, temp_docs_dir):
        """Test adding documents to collection and querying."""
        # Mock embedding responses
        mock_embed.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]},
                {"embedding": [0.7, 0.8, 0.9]},
            ]
        }

        # Create collection
        collection = collection_manager.create_collection(
            name="test", embedding_model="text-embedding-ada-002"
        )

        # Load documents
        docs = DocumentLoader.load_directory(temp_docs_dir)

        # Process and add documents
        all_docs_to_add = []
        all_metadata = []

        for doc in docs:
            chunks = DocumentLoader.chunk_text(doc["content"], chunk_size=500, overlap=100)
            for chunk_idx, chunk in enumerate(chunks):
                metadata = DocumentLoader.extract_metadata(doc["source"], chunk_idx)
                all_docs_to_add.append(
                    {
                        "id": f"{metadata['document_name']}_chunk_{chunk_idx}",
                        "content": chunk,
                        "source": metadata["source_path"],
                    }
                )
                all_metadata.append(metadata)

        # Add to collection
        collection.add_documents(all_docs_to_add, all_metadata)

        # Verify collection has documents
        stats = collection.get_stats()
        assert stats["document_count"] > 0

    @patch("simple_agent.rag.embedding_provider.litellm.embedding")
    def test_list_documents_with_metadata(self, mock_embed, collection_manager, temp_docs_dir):
        """Test listing documents with metadata."""
        mock_embed.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]},
            ]
        }

        collection = collection_manager.create_collection(name="test")

        docs = DocumentLoader.load_directory(temp_docs_dir)
        all_docs = []
        all_metadata = []

        for doc in docs:
            chunks = DocumentLoader.chunk_text(doc["content"], chunk_size=500, overlap=100)
            for chunk_idx, chunk in enumerate(chunks):
                metadata = DocumentLoader.extract_metadata(doc["source"], chunk_idx)
                all_docs.append(
                    {
                        "id": f"{metadata['document_name']}_chunk_{chunk_idx}",
                        "content": chunk,
                        "source": metadata["source_path"],
                    }
                )
                all_metadata.append(metadata)

        if all_docs:
            collection.add_documents(all_docs, all_metadata)

        # List documents
        listed = collection.list_documents()
        assert len(listed) > 0
        assert all("document_name" in doc for doc in listed)

    def test_collection_deletion(self, collection_manager):
        """Test deleting a collection."""
        collection_manager.create_collection(name="to_delete")
        assert "to_delete" in collection_manager.collections

        collection_manager.delete_collection("to_delete")
        assert "to_delete" not in collection_manager.collections

    def test_multiple_collections(self, collection_manager):
        """Test managing multiple collections."""
        collection_manager.create_collection(name="col1")
        collection_manager.create_collection(name="col2")
        collection_manager.create_collection(name="col3")

        collections = collection_manager.list_collections()
        assert len(collections) == 3
        names = [c["name"] for c in collections]
        assert "col1" in names
        assert "col2" in names
        assert "col3" in names

    def test_agent_switches_collections(self, collection_manager):
        """Test agent can switch between collections."""
        collection_manager.create_collection(name="col1")
        collection_manager.create_collection(name="col2")

        # Connect to first collection
        collection_manager.connect_agent("agent", "col1")
        assert collection_manager.get_agent_collection("agent").name == "col1"

        # Switch to second collection
        collection_manager.connect_agent("agent", "col2")
        assert collection_manager.get_agent_collection("agent").name == "col2"

    def test_collection_metadata_persistence(self, collection_manager):
        """Test that collection metadata is maintained."""
        collection = collection_manager.create_collection(
            name="test",
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            chunk_size=2000,
            chunk_overlap=500,
        )

        stats = collection.get_stats()
        assert stats["embedding_model"] == "sentence-transformers/all-MiniLM-L6-v2"
        assert stats["chunk_size"] == 2000
        assert stats["chunk_overlap"] == 500
        assert stats["created_timestamp"] is not None
