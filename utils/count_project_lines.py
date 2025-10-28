"""
Script to count lines of code, comment lines, and documentation lines in the project.

- Counts all lines of code and comment lines in Python files under src/ and tests/
- Counts all text lines in files under docs/ and README.md in the project root

Usage: python count_project_lines.py
"""

from pathlib import Path

SRC_DIR = Path().parent.parent / "simple_agent"
TESTS_DIR = Path().parent.parent / "tests"
DOCS_DIR = Path().parent.parent / "docs"
README_PATH = Path().parent.parent / "README.md"


def count_py_lines(file_path):
    """
    Counts code and comment lines in a Python file.

    Args:
        file_path (Path): Path to the Python file.

    Returns:
        tuple: (code_lines, comment_lines, total_lines)
    """
    code_lines = 0
    comment_lines = 0
    total_lines = 0
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                total_lines += 1
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("#"):
                    comment_lines += 1
                else:
                    code_lines += 1
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return code_lines, comment_lines, total_lines


def count_text_lines(file_path):
    """
    Counts all non-empty lines in a text file.

    Args:
        file_path (Path): Path to the text file.

    Returns:
        int: Number of non-empty lines.
    """
    count = 0
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return count


def get_python_files(directory):
    """
    Recursively gets all .py files in a directory.
    """
    return [p for p in directory.rglob("*.py") if p.is_file()]


def get_text_files(directory):
    """
    Gets all files in a directory (recursively), excluding subdirectories.
    """
    return [p for p in directory.rglob("*") if p.is_file()]


def main():
    # Count Python code and comment lines for src
    src_py_files = get_python_files(SRC_DIR)
    src_code = src_comments = src_py_lines = 0
    for py_file in src_py_files:
        code, comments, lines = count_py_lines(py_file)
        src_code += code
        src_comments += comments
        src_py_lines += lines

    # Count Python code and comment lines for tests
    tests_py_files = get_python_files(TESTS_DIR)
    tests_code = tests_comments = tests_py_lines = 0
    for py_file in tests_py_files:
        code, comments, lines = count_py_lines(py_file)
        tests_code += code
        tests_comments += comments
        tests_py_lines += lines

    total_code = src_code + tests_code
    total_comments = src_comments + tests_comments
    total_py_lines = src_py_lines + tests_py_lines

    # Count documentation lines
    doc_files = get_text_files(DOCS_DIR)
    total_doc_lines = 0
    for doc_file in doc_files:
        total_doc_lines += count_text_lines(doc_file)
    if README_PATH.exists():
        total_doc_lines += count_text_lines(README_PATH)

    print(f"Python source files ({SRC_DIR}/):")
    print(f"  Files: {len(src_py_files)}")
    print(f"  Code lines: {src_code}")
    print(f"  Comment lines: {src_comments}")
    print(f"  Total lines (including blank): {src_py_lines}")
    print()
    print(f"Python test files ({TESTS_DIR}/):")
    print(f"  Files: {len(tests_py_files)}")
    print(f"  Code lines: {tests_code}")
    print(f"  Comment lines: {tests_comments}")
    print(f"  Total lines (including blank): {tests_py_lines}")
    print()
    print("Totals (src + tests):")
    print(f"  All code lines: {total_code}")
    print(f"  All comment lines: {total_comments}")
    print(f"  All lines (including blank): {total_py_lines}")
    print()
    print("Documentation (docs/ and README.md):")
    print(f"  Total documentation/text lines: {total_doc_lines}")


if __name__ == "__main__":
    main()
