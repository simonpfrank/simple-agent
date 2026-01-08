"""Unit tests for CollectionManager - TDD approach."""

from unittest.mock import Mock, patch, MagicMock
import pytest

from simple_agent.rag.collection_manager import CollectionManager
from simple_agent.rag.collection import Collection


class TestCollectionManager:
    """Test CollectionManager CRUD and agent connection operations."""

    @pytest.fixture
    def collection_manager(self, tmp_path):
        """Create CollectionManager instance with clean temp directory."""
        collections_dir = str(tmp_path / "test_chroma_db")
        return CollectionManager(collections_dir=collections_dir)

    @pytest.fixture
    def mock_chroma_wrapper(self):
        """Create mock ChromaWrapper."""
        return Mock()

    def test_collection_manager_initialization(self, collection_manager):
        """Test CollectionManager initializes correctly."""
        assert collection_manager.collections_dir is not None
        assert "test_chroma_db" in collection_manager.collections_dir
        assert isinstance(collection_manager.collections, dict)
        assert len(collection_manager.collections) == 0

    def test_create_collection_with_defaults(self, collection_manager):
        """Test creating a collection with default parameters."""
        collection = collection_manager.create_collection(
            name="test_collection"
        )

        assert collection is not None
        assert collection.name == "test_collection"
        assert "test_collection" in collection_manager.collections

    def test_create_collection_with_custom_params(self, collection_manager):
        """Test creating a collection with custom parameters."""
        collection = collection_manager.create_collection(
            name="research",
            embedding_model="sentence-transformers",
            chunk_size=2000,
            chunk_overlap=500,
            path="./custom/path"
        )

        assert collection is not None
        assert collection.name == "research"
        assert collection.metadata["embedding_model"] == "sentence-transformers"
        assert collection.metadata["chunk_size"] == 2000
        assert collection.metadata["chunk_overlap"] == 500

    def test_create_collection_duplicate_name_raises_error(self, collection_manager):
        """Test that creating duplicate collection raises error."""
        collection_manager.create_collection(name="duplicate")

        with pytest.raises(ValueError, match="already exists"):
            collection_manager.create_collection(name="duplicate")

    def test_get_collection(self, collection_manager):
        """Test retrieving a collection."""
        created = collection_manager.create_collection(name="test_col")
        retrieved = collection_manager.get_collection("test_col")

        assert retrieved == created
        assert retrieved.name == "test_col"

    def test_get_collection_not_found(self, collection_manager):
        """Test getting non-existent collection raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            collection_manager.get_collection("nonexistent")

    def test_list_collections_empty(self, collection_manager):
        """Test listing collections when empty."""
        collections = collection_manager.list_collections()

        assert isinstance(collections, list)
        assert len(collections) == 0

    def test_list_collections_with_metadata(self, collection_manager):
        """Test listing collections returns metadata."""
        collection_manager.create_collection(name="col1")
        collection_manager.create_collection(name="col2")

        collections = collection_manager.list_collections()

        assert len(collections) == 2
        names = [c["name"] for c in collections]
        assert "col1" in names
        assert "col2" in names
        assert all("created_timestamp" in c for c in collections)

    def test_delete_collection(self, collection_manager):
        """Test deleting a collection."""
        collection_manager.create_collection(name="to_delete")
        assert "to_delete" in collection_manager.collections

        collection_manager.delete_collection("to_delete")

        assert "to_delete" not in collection_manager.collections

    def test_delete_collection_not_found(self, collection_manager):
        """Test deleting non-existent collection raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            collection_manager.delete_collection("nonexistent")

    def test_connect_agent_to_collection(self, collection_manager):
        """Test connecting agent to collection."""
        collection_manager.create_collection(name="research")

        collection_manager.connect_agent("my_agent", "research")

        connected = collection_manager.get_agent_collection("my_agent")
        assert connected is not None
        assert connected.name == "research"

    def test_connect_agent_to_nonexistent_collection(self, collection_manager):
        """Test connecting agent to non-existent collection raises error."""
        with pytest.raises(KeyError, match="not found"):
            collection_manager.connect_agent("my_agent", "nonexistent")

    def test_disconnect_agent(self, collection_manager):
        """Test disconnecting agent from collection."""
        collection_manager.create_collection(name="research")
        collection_manager.connect_agent("my_agent", "research")

        collection_manager.disconnect_agent("my_agent")

        assert collection_manager.get_agent_collection("my_agent") is None

    def test_disconnect_agent_not_connected(self, collection_manager):
        """Test disconnecting agent that's not connected."""
        # Should not raise error - idempotent
        collection_manager.disconnect_agent("never_connected")
        assert collection_manager.get_agent_collection("never_connected") is None

    def test_get_agent_collection_not_connected(self, collection_manager):
        """Test getting collection for agent that's not connected."""
        collection = collection_manager.get_agent_collection("no_connection")

        assert collection is None

    def test_multiple_agents_same_collection(self, collection_manager):
        """Test multiple agents can connect to same collection."""
        collection_manager.create_collection(name="shared")

        collection_manager.connect_agent("agent1", "shared")
        collection_manager.connect_agent("agent2", "shared")

        assert collection_manager.get_agent_collection("agent1").name == "shared"
        assert collection_manager.get_agent_collection("agent2").name == "shared"

    def test_agent_reconnect_to_different_collection(self, collection_manager):
        """Test agent can reconnect to different collection."""
        collection_manager.create_collection(name="col1")
        collection_manager.create_collection(name="col2")

        collection_manager.connect_agent("agent", "col1")
        assert collection_manager.get_agent_collection("agent").name == "col1"

        collection_manager.connect_agent("agent", "col2")
        assert collection_manager.get_agent_collection("agent").name == "col2"

    def test_collection_metadata_includes_timestamps(self, collection_manager):
        """Test collection metadata includes created timestamp."""
        collection = collection_manager.create_collection(name="test")

        assert "created_timestamp" in collection.metadata
        assert collection.metadata["created_timestamp"] is not None

    def test_collection_metadata_includes_config(self, collection_manager):
        """Test collection metadata includes configuration."""
        collection = collection_manager.create_collection(
            name="test",
            chunk_size=2000,
            chunk_overlap=300,
            embedding_model="ollama"
        )

        assert collection.metadata["chunk_size"] == 2000
        assert collection.metadata["chunk_overlap"] == 300
        assert collection.metadata["embedding_model"] == "ollama"

    def test_list_collections_loads_from_chromadb(self, tmp_path):
        """Test that list_collections loads existing collections from ChromaDB.

        Bug #30: Collections created in one session weren't visible after
        creating a new CollectionManager instance because list_collections
        only read from the in-memory dict, not from the persisted ChromaDB.
        """
        collections_dir = str(tmp_path / "chroma_db")

        # Create collection with first manager
        manager1 = CollectionManager(collections_dir=collections_dir)
        manager1.create_collection(name="persistent_collection")

        # Verify it exists in first manager
        collections = manager1.list_collections()
        assert len(collections) == 1
        assert collections[0]["name"] == "persistent_collection"

        # Create new manager instance (simulating REPL restart or lazy loading)
        manager2 = CollectionManager(collections_dir=collections_dir)

        # Should still see the collection
        collections = manager2.list_collections()
        assert len(collections) == 1, "Collections should be loaded from ChromaDB"
        assert collections[0]["name"] == "persistent_collection"
