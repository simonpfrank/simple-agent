"""CollectionManager for managing RAG collections and agent connections."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from simple_agent.rag.collection import Collection
from simple_agent.rag.chroma_wrapper import ChromaWrapper
from simple_agent.rag.exceptions import CollectionError


class CollectionManager:
    """Manage RAG collections independently of agents."""

    def __init__(self, collections_dir: str = "./chroma_db"):
        """Initialize CollectionManager.

        Args:
            collections_dir: Directory for storing Chroma databases
        """
        self.collections_dir = collections_dir
        self.chroma_wrapper = ChromaWrapper(collections_dir)
        self.collections: Dict[str, Collection] = {}
        self.agent_connections: Dict[str, str] = {}  # {agent_name: collection_name}

    def create_collection(
        self,
        name: str,
        embedding_model: str = "text-embedding-ada-002",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        path: Optional[str] = None,
    ) -> Collection:
        """Create a new collection.

        Args:
            name: Collection name
            embedding_model: Embedding model to use
            chunk_size: Characters per chunk
            chunk_overlap: Characters to overlap between chunks
            path: Optional path for documents

        Returns:
            Created Collection instance

        Raises:
            ValueError: If collection already exists
        """
        if name in self.collections:
            raise ValueError(f"Collection '{name}' already exists")

        metadata = {
            "created_timestamp": datetime.now(timezone.utc).isoformat(),
            "document_count": 0,
            "embedding_model": embedding_model,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "last_indexed": None,
            "original_path": path,
        }

        # Create Chroma collection
        chroma_collection = self.chroma_wrapper.get_or_create_collection(name, metadata)

        collection = Collection(name=name, chroma_collection=chroma_collection, metadata=metadata)
        self.collections[name] = collection
        return collection

    def get_collection(self, name: str) -> Collection:
        """Get a collection by name.

        Args:
            name: Collection name

        Returns:
            Collection instance

        Raises:
            KeyError: If collection not found
        """
        if name not in self.collections:
            raise KeyError(f"Collection '{name}' not found")
        return self.collections[name]

    def list_collections(self) -> List[dict]:
        """List all collections with metadata.

        Returns:
            List of collection metadata dicts
        """
        collections_list = []
        for name, collection in self.collections.items():
            collections_list.append({
                "name": name,
                "created_timestamp": collection.metadata.get("created_timestamp"),
                "document_count": collection.metadata.get("document_count", 0),
                "embedding_model": collection.metadata.get("embedding_model"),
                "chunk_size": collection.metadata.get("chunk_size"),
                "chunk_overlap": collection.metadata.get("chunk_overlap"),
            })
        return collections_list

    def delete_collection(self, name: str) -> None:
        """Delete a collection.

        Args:
            name: Collection name

        Raises:
            KeyError: If collection not found
        """
        if name not in self.collections:
            raise KeyError(f"Collection '{name}' not found")

        # Disconnect any agents using this collection
        agents_to_disconnect = [
            agent for agent, col in self.agent_connections.items()
            if col == name
        ]
        for agent in agents_to_disconnect:
            del self.agent_connections[agent]

        del self.collections[name]

    def connect_agent(self, agent_name: str, collection_name: str) -> None:
        """Connect agent to a collection.

        Args:
            agent_name: Name of agent
            collection_name: Name of collection

        Raises:
            KeyError: If collection not found
        """
        if collection_name not in self.collections:
            raise KeyError(f"Collection '{collection_name}' not found")

        self.agent_connections[agent_name] = collection_name

    def disconnect_agent(self, agent_name: str) -> None:
        """Disconnect agent from collection.

        Args:
            agent_name: Name of agent
        """
        if agent_name in self.agent_connections:
            del self.agent_connections[agent_name]

    def get_agent_collection(self, agent_name: str) -> Optional[Collection]:
        """Get collection connected to an agent.

        Args:
            agent_name: Name of agent

        Returns:
            Collection instance or None if not connected
        """
        collection_name = self.agent_connections.get(agent_name)
        if collection_name is None:
            return None
        return self.get_collection(collection_name)

    def cleanup(self) -> None:
        """Cleanup resources (close ChromaDB client)."""
        try:
            # Reset ChromaDB client to close connections
            if hasattr(self.chroma_wrapper, 'client') and self.chroma_wrapper.client is not None:
                self.chroma_wrapper.client.clear_system_cache()
        except Exception:
            pass
