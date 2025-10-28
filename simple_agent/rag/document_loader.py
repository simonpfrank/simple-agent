"""Document loader for loading and chunking files."""

from datetime import datetime, timezone
from pathlib import Path
from typing import List


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
