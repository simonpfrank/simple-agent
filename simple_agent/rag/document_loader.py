"""Document loader for loading and chunking files."""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from simple_agent.rag.collection import DocumentValidationError

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Load and chunk documents for RAG."""

    SUPPORTED_EXTENSIONS = {".txt", ".md"}

    @staticmethod
    def load_file(file_path: str) -> dict:
        """Load a single file.

        Args:
            file_path: Path to file

        Returns:
            Dict with 'content' and 'source' keys

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = path.read_text(encoding="utf-8")
        return {
            "content": content,
            "source": str(path),
        }

    @staticmethod
    def load_directory(directory_path: str) -> List[dict]:
        """Load all supported files from directory recursively.

        Args:
            directory_path: Path to directory

        Returns:
            List of document dicts
        """
        documents = []
        directory = Path(directory_path)

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in DocumentLoader.SUPPORTED_EXTENSIONS:
                try:
                    doc = DocumentLoader.load_file(str(file_path))
                    documents.append(doc)
                except Exception:
                    # Skip files that fail to load
                    pass

        return documents

    @staticmethod
    def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Characters per chunk
            overlap: Characters to overlap between chunks

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            # Calculate end position
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)

            # Move start position for next chunk (accounting for overlap)
            # Step forward by (chunk_size - overlap) to create overlap
            step = chunk_size - overlap
            start += step

        return chunks

    @staticmethod
    def extract_metadata(file_path: str, chunk_index: int) -> dict:
        """Extract metadata for a document chunk.

        Args:
            file_path: Path to source file
            chunk_index: Index of chunk

        Returns:
            Dict with metadata
        """
        path = Path(file_path)
        stat = path.stat()

        return {
            "document_name": path.name,
            "source_path": str(path),
            "chunk_index": chunk_index,
            "doc_file_timestamp": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "page_name": None,
            "page": None,
            "paragraph": None,
        }

    @staticmethod
    def validate_document(document: dict) -> None:
        """
        Validate document structure before adding to collection.

        Issue 7-B: Add document structure validation
        Ensures documents have required fields and valid types.

        Args:
            document: Document dict to validate

        Raises:
            DocumentValidationError: If document structure is invalid
        """
        if not isinstance(document, dict):
            raise DocumentValidationError("Document must be a dictionary")

        # Check required fields
        required_fields = {"id", "content", "source"}
        missing_fields = required_fields - set(document.keys())
        if missing_fields:
            raise DocumentValidationError(
                f"Document missing required fields: {', '.join(sorted(missing_fields))}"
            )

        # Validate field types and values
        if not isinstance(document.get("id"), str):
            raise DocumentValidationError("Document 'id' must be a string")

        if not isinstance(document.get("content"), str):
            raise DocumentValidationError("Document 'content' must be a string")

        if not isinstance(document.get("source"), str):
            raise DocumentValidationError("Document 'source' must be a string")

        # Validate non-empty required fields
        if not document["id"]:
            raise DocumentValidationError("Document 'id' cannot be empty")

        if not document["content"]:
            raise DocumentValidationError("Document 'content' cannot be empty")

        logger.debug(f"Document '{document['id']}' validation passed")

    @staticmethod
    def validate_documents(documents: List[dict]) -> None:
        """
        Validate a batch of documents before adding to collection.

        Issue 7-B: Batch validation
        Validates all documents and fails on first error.

        Args:
            documents: List of document dicts to validate

        Raises:
            DocumentValidationError: If any document is invalid
        """
        if not isinstance(documents, list):
            raise DocumentValidationError("Documents must be a list")

        if not documents:
            raise DocumentValidationError("Documents list cannot be empty")

        for i, document in enumerate(documents):
            try:
                DocumentLoader.validate_document(document)
            except DocumentValidationError as e:
                raise DocumentValidationError(
                    f"Document {i} validation failed: {str(e)}"
                ) from e

        logger.debug(f"Validated {len(documents)} documents")

