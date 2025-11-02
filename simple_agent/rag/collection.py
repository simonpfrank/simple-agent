"""Collection class for managing a single RAG collection."""

import logging
from datetime import datetime, timezone
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class DocumentValidationError(ValueError):
    """Raised when document structure validation fails."""

    pass


class IndexVersionError(ValueError):
    """Raised when index version compatibility issues occur."""

    pass


class Collection:
    """A single RAG collection with documents and metadata."""

    def __init__(self, name: str, chroma_collection: Any, metadata: dict):
        """Initialize Collection.

        Args:
            name: Collection name
            chroma_collection: Chroma collection instance
            metadata: Collection-level metadata
        """
        self.name = name
        self.chroma_collection = chroma_collection
        self.metadata = metadata

        # Initialize index version if not present (Issue 7-C)
        if "index_version" not in self.metadata:
            self.metadata["index_version"] = self._generate_version()
            logger.debug(f"Generated index version: {self.metadata['index_version']}")

    @staticmethod
    def _generate_version() -> str:
        """Generate a new semantic version string.

        Returns:
            Version string in format X.Y.Z
        """
        return "1.0.0"

    def add_documents(self, documents: List[dict], metadata_list: List[dict]) -> None:
        """Add documents to collection.

        Args:
            documents: List of document dicts with 'id', 'content', 'source'
            metadata_list: List of metadata dicts for each document
        """
        if not documents:
            return

        # Extract fields for Chroma
        ids = [doc["id"] for doc in documents]
        texts = [doc["content"] for doc in documents]

        # Filter out None values from metadata (Chroma doesn't accept them)
        filtered_metadata = []
        for metadata in metadata_list:
            filtered = {k: v for k, v in metadata.items() if v is not None}
            filtered_metadata.append(filtered)

        # Add to Chroma collection
        self.chroma_collection.add(ids=ids, documents=texts, metadatas=filtered_metadata)

        # Update collection document count
        self.metadata["document_count"] = len(documents)
        self.metadata["last_indexed"] = datetime.now(timezone.utc).isoformat()

    def delete_document(self, document_name: str) -> None:
        """Delete a specific document from collection.

        Args:
            document_name: Name of document to delete
        """
        # Get documents with this name
        results = self.chroma_collection.get(where={"document_name": document_name})
        if results and results["ids"]:
            for doc_id in results["ids"]:
                self.chroma_collection.delete(ids=[doc_id])

    def query(self, query: str, top_k: int = 3) -> List[dict]:
        """Query collection and retrieve top-K results.

        Args:
            query: Search query text
            top_k: Number of results to return

        Returns:
            List of retrieval results with metadata
        """
        # Import here to avoid circular imports
        from simple_agent.rag.embedding_provider import EmbeddingProvider

        # Get embedding for query
        query_embedding = EmbeddingProvider.embed_query(
            query, model=self.metadata.get("embedding_model")
        )

        # Search Chroma
        results = self.chroma_collection.query(
            query_embeddings=[query_embedding], n_results=top_k
        )

        # Format results
        formatted_results = []
        if results and results["documents"]:
            for i, doc_text in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                formatted_results.append({"text": doc_text, "metadata": metadata})

        return formatted_results

    def list_documents(self) -> List[dict]:
        """List all documents in collection.

        Returns:
            List of document metadata dicts
        """
        results = self.chroma_collection.get()
        if not results or not results["metadatas"]:
            return []

        # Group by document_name and get unique documents
        seen = set()
        documents = []
        for metadata in results["metadatas"]:
            doc_name = metadata.get("document_name")
            if doc_name and doc_name not in seen:
                seen.add(doc_name)
                documents.append(metadata)

        return documents

    def get_stats(self) -> dict:
        """Get collection statistics.

        Returns:
            Dict with document_count, embedding_model, etc.
        """
        # Get actual count from Chroma
        results = self.chroma_collection.get()
        count = len(results["ids"]) if results and results["ids"] else 0

        stats = {
            "name": self.name,
            "embedding_model": self.metadata.get("embedding_model"),
            "chunk_size": self.metadata.get("chunk_size"),
            "chunk_overlap": self.metadata.get("chunk_overlap"),
            "created_timestamp": self.metadata.get("created_timestamp"),
            "document_count": count,
            "last_indexed": self.metadata.get("last_indexed"),
        }
        return stats

    def is_embedding_compatible(self, new_model: str) -> bool:
        """
        Check if a new embedding model is compatible with current index.

        Issue 7-C: Check embedding model compatibility
        If the embedding model changes, the index becomes incompatible
        and requires reindexing.

        Args:
            new_model: New embedding model name to check

        Returns:
            True if compatible (same model), False otherwise
        """
        current_model = self.metadata.get("embedding_model")
        return current_model == new_model

    def get_index_version(self) -> str:
        """
        Get the current index version.

        Issue 7-C: Index versioning
        Returns the semantic version of the index based on embedding model.

        Returns:
            Version string in format X.Y.Z
        """
        return self.metadata.get("index_version", "1.0.0")

    def get_migration_info(self, new_model: str) -> dict:
        """
        Get information about migrating to a new embedding model.

        Issue 7-C: Provide migration guidance
        When embedding model changes, guide user on what needs to happen.

        Args:
            new_model: New embedding model to migrate to

        Returns:
            Dict with migration information including:
            - current_model: Current embedding model
            - new_model: New embedding model
            - requires_reindex: Whether reindexing is needed
            - reason: Why reindexing is needed
        """
        current_model = self.metadata.get("embedding_model")
        is_compatible = self.is_embedding_compatible(new_model)

        return {
            "current_model": current_model,
            "new_model": new_model,
            "requires_reindex": not is_compatible,
            "reason": (
                "Embedding model changed - index is incompatible. "
                "Documents must be reindexed with new model."
                if not is_compatible
                else "Models are compatible"
            ),
            "current_version": self.get_index_version(),
        }

    def clear(self) -> None:
        """Clear all documents from collection (keeps collection)."""
        results = self.chroma_collection.get()
        if results and results["ids"]:
            for doc_id in results["ids"]:
                self.chroma_collection.delete(ids=[doc_id])
        self.metadata["document_count"] = 0

    def reindex(self, embedding_model: Optional[str] = None) -> None:
        """
        Reindex collection from original path.

        Issue 7-C: Support embedding model changes during reindexing
        If a new embedding model is provided, update the collection metadata
        and bump the index version.

        Args:
            embedding_model: Optional new embedding model to use for reindexing
        """
        # Check for embedding model compatibility (Issue 7-C)
        if embedding_model:
            if not self.is_embedding_compatible(embedding_model):
                logger.info(
                    f"Embedding model changing from "
                    f"{self.metadata.get('embedding_model')} to {embedding_model} - "
                    f"will reindex all documents"
                )
                self.metadata["embedding_model"] = embedding_model
                # Increment version (Issue 7-C)
                old_version = self.get_index_version()
                new_version = self._increment_version(old_version)
                self.metadata["index_version"] = new_version
                logger.info(f"Index version updated from {old_version} to {new_version}")

        # Load from original_path in metadata
        original_path = self.metadata.get("original_path")
        if not original_path:
            return

        from simple_agent.rag.document_loader import DocumentLoader

        # Clear existing documents
        self.clear()

        # Load documents from original path
        documents = DocumentLoader.load_directory(original_path)
        if documents:
            # Process documents and add to collection
            chunk_size = self.metadata.get("chunk_size", 1000)
            chunk_overlap = self.metadata.get("chunk_overlap", 200)

            all_docs_to_add = []
            all_metadata_to_add = []

            for doc in documents:
                chunks = DocumentLoader.chunk_text(
                    doc["content"], chunk_size=chunk_size, overlap=chunk_overlap
                )
                for chunk_idx, chunk in enumerate(chunks):
                    metadata = DocumentLoader.extract_metadata(doc["source"], chunk_idx)
                    all_docs_to_add.append(
                        {
                            "id": f"{metadata['document_name']}_chunk_{chunk_idx}",
                            "content": chunk,
                            "source": metadata["source_path"],
                        }
                    )
                    all_metadata_to_add.append(metadata)

            if all_docs_to_add:
                self.add_documents(all_docs_to_add, all_metadata_to_add)

    @staticmethod
    def _increment_version(version: str) -> str:
        """
        Increment semantic version (bump minor version).

        Issue 7-C: Version management
        When reindexing with new model, increment version to track changes.

        Args:
            version: Current version in X.Y.Z format

        Returns:
            Incremented version string
        """
        try:
            parts = version.split(".")
            if len(parts) != 3:
                return "1.0.0"

            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            # Increment minor version on model change
            return f"{major}.{minor + 1}.0"
        except (ValueError, IndexError):
            return "1.0.0"
