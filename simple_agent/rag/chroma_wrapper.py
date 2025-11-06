"""Wrapper around Chroma for persistent vector store."""

from pathlib import Path
from typing import Any, List, Optional

import chromadb
import chromadb.config


class ChromaWrapper:
    """Wrapper around Chroma for consistent interface."""

    def __init__(self, collections_dir: str = "./chroma_db"):
        """Initialize ChromaWrapper.

        Args:
            collections_dir: Directory for storing Chroma databases
        """
        self.collections_dir = collections_dir
        # Create directory if it doesn't exist
        Path(collections_dir).mkdir(parents=True, exist_ok=True)
        # Turn off telemetry
        client_settings = chromadb.config.Settings(anonymized_telemetry=False)
        # Initialize Chroma persistent client
        self.client = chromadb.PersistentClient(
            path=collections_dir, settings=client_settings
        )

    def get_or_create_collection(
        self, name: str, metadata: Optional[dict] = None
    ) -> Any:
        """Get or create a collection.

        Args:
            name: Collection name
            metadata: Optional metadata for collection

        Returns:
            Chroma collection instance
        """
        # Filter out None values from metadata (Chroma doesn't accept them)
        filtered_metadata = {}
        if metadata:
            for key, value in metadata.items():
                if value is not None:
                    filtered_metadata[key] = value

        # Get or create collection with metadata
        collection = self.client.get_or_create_collection(
            name=name,
            metadata=filtered_metadata,
        )
        return collection

    def delete_collection(self, name: str) -> None:
        """Delete a collection.

        Args:
            name: Collection name
        """
        self.client.delete_collection(name=name)

    def list_collections(self) -> List[str]:
        """List all collection names.

        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        return [col.name for col in collections]

    def get_collection(self, name: str) -> Optional[Any]:
        """Get collection by name.

        Args:
            name: Collection name

        Returns:
            Chroma collection or None if not found
        """
        try:
            return self.client.get_collection(name=name)
        except Exception:
            return None
