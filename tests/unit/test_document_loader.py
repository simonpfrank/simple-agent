"""Unit tests for DocumentLoader - TDD approach."""

import os
import tempfile
from pathlib import Path

import pytest

from simple_agent.rag.document_loader import DocumentLoader


class TestDocumentLoader:
    """Test DocumentLoader file loading and chunking."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with test documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test .txt file
            txt_path = Path(tmpdir) / "sample.txt"
            txt_path.write_text("This is a test document.\nIt has multiple lines.\nFor testing purposes.")

            # Create test .md file
            md_path = Path(tmpdir) / "sample.md"
            md_path.write_text("# Sample Markdown\n\nThis is markdown content.\n\nWith multiple paragraphs.")

            # Create subdirectory with more docs
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            (subdir / "nested.txt").write_text("Nested document content.")

            yield tmpdir

    def test_load_file_txt(self, temp_dir):
        """Test loading a .txt file."""
        file_path = Path(temp_dir) / "sample.txt"

        document = DocumentLoader.load_file(str(file_path))

        assert document is not None
        assert document["content"] is not None
        assert len(document["content"]) > 0
        assert "test document" in document["content"]

    def test_load_file_md(self, temp_dir):
        """Test loading a .md file."""
        file_path = Path(temp_dir) / "sample.md"

        document = DocumentLoader.load_file(str(file_path))

        assert document is not None
        assert "markdown content" in document["content"]

    def test_load_file_not_found(self):
        """Test loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            DocumentLoader.load_file("/nonexistent/path/file.txt")

    def test_load_directory(self, temp_dir):
        """Test loading all files from directory."""
        documents = DocumentLoader.load_directory(temp_dir)

        assert isinstance(documents, list)
        assert len(documents) >= 2  # At least sample.txt and sample.md
        file_names = [doc["source"] for doc in documents]
        assert any("sample.txt" in fn for fn in file_names)
        assert any("sample.md" in fn for fn in file_names)

    def test_load_directory_recursive(self, temp_dir):
        """Test loading from directory includes subdirectories."""
        documents = DocumentLoader.load_directory(temp_dir)

        file_names = [doc["source"] for doc in documents]
        assert any("nested.txt" in fn for fn in file_names)

    def test_load_directory_ignores_other_types(self, temp_dir):
        """Test that non-txt/md files are ignored."""
        # Create a file with unsupported extension
        json_file = Path(temp_dir) / "test.json"
        json_file.write_text('{"key": "value"}')

        documents = DocumentLoader.load_directory(temp_dir)

        file_names = [doc["source"] for doc in documents]
        assert not any(".json" in fn for fn in file_names)

    def test_chunk_text_basic(self):
        """Test basic text chunking."""
        text = "A" * 500 + "B" * 500 + "C" * 500  # 1500 chars total

        chunks = DocumentLoader.chunk_text(text, chunk_size=400, overlap=0)

        assert len(chunks) >= 3
        assert chunks[0].startswith("A")
        # With chunk_size=400, overlap=0, chunks[1] starts at position 400
        # which is in the A section (0-499). So chunks[1] contains A and B.
        assert "B" in chunks[1]  # Verify B section exists in later chunks

    def test_chunk_text_with_overlap(self):
        """Test text chunking with overlap."""
        text = "0123456789" * 100  # 1000 chars

        chunks = DocumentLoader.chunk_text(text, chunk_size=100, overlap=20)

        assert len(chunks) > 1
        # Check overlap: end of first chunk should overlap with start of second
        first_chunk = chunks[0]
        second_chunk = chunks[1]
        # The end of first chunk should appear somewhere in second chunk (with overlap)
        assert first_chunk[-20:] in second_chunk or first_chunk[-19:] in second_chunk

    def test_chunk_text_small_chunk_size(self):
        """Test chunking with small chunk size."""
        text = "Short text"

        chunks = DocumentLoader.chunk_text(text, chunk_size=5, overlap=0)

        assert len(chunks) >= 1
        assert sum(len(c) for c in chunks) >= len(text)

    def test_chunk_text_preserves_content(self):
        """Test that chunking preserves all content."""
        text = "The quick brown fox jumps over the lazy dog. " * 50

        chunks = DocumentLoader.chunk_text(text, chunk_size=200, overlap=50)

        # Concatenate chunks (removing overlaps) should contain original
        combined = "".join(chunks)
        assert text in combined or all(word in combined for word in text.split())

    def test_extract_metadata_txt(self, temp_dir):
        """Test extracting metadata from file."""
        file_path = Path(temp_dir) / "sample.txt"

        metadata = DocumentLoader.extract_metadata(str(file_path), chunk_index=0)

        assert metadata is not None
        assert "document_name" in metadata
        assert "source_path" in metadata
        assert "chunk_index" in metadata
        assert metadata["chunk_index"] == 0
        assert "sample.txt" in metadata["document_name"]

    def test_extract_metadata_includes_timestamp(self, temp_dir):
        """Test that metadata includes file timestamp."""
        file_path = Path(temp_dir) / "sample.txt"

        metadata = DocumentLoader.extract_metadata(str(file_path), chunk_index=0)

        assert "doc_file_timestamp" in metadata
        assert metadata["doc_file_timestamp"] is not None

    def test_extract_metadata_chunk_index(self, temp_dir):
        """Test metadata includes correct chunk index."""
        file_path = Path(temp_dir) / "sample.txt"

        metadata1 = DocumentLoader.extract_metadata(str(file_path), chunk_index=0)
        metadata2 = DocumentLoader.extract_metadata(str(file_path), chunk_index=5)

        assert metadata1["chunk_index"] == 0
        assert metadata2["chunk_index"] == 5

    def test_load_file_returns_dict_with_content(self, temp_dir):
        """Test that load_file returns dict with 'content' and 'source' keys."""
        file_path = Path(temp_dir) / "sample.txt"

        document = DocumentLoader.load_file(str(file_path))

        assert isinstance(document, dict)
        assert "content" in document
        assert "source" in document

    def test_load_directory_returns_list_of_dicts(self, temp_dir):
        """Test that load_directory returns list of document dicts."""
        documents = DocumentLoader.load_directory(temp_dir)

        assert isinstance(documents, list)
        for doc in documents:
            assert isinstance(doc, dict)
            assert "content" in doc
            assert "source" in doc
