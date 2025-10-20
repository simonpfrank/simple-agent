"""
Example processor module - demonstrates core business logic pattern.
Replace this with your actual business logic.
"""

import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Maximum file size to process (100 MB)
MAX_FILE_SIZE = 100 * 1024 * 1024


def process_data(input_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example core function: process data from input file with security validation.

    This function is framework-agnostic and can be called from:
    - REPL commands
    - CLI commands
    - API endpoints
    - Web UI handlers
    - Test code

    Args:
        input_path: Path to input file
        config: Configuration dictionary

    Returns:
        Dictionary with results:
        {
            'status': 'success' | 'error',
            'rows': int,
            'output': str,
            'message': str,
            'errors': List[str] (optional)
        }

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input file is invalid (not a file, too large, etc.)
    """
    logger.info(f"Processing file: {input_path}")

    # Validate and resolve input path (prevents path traversal)
    try:
        input_file = Path(input_path).resolve(strict=True)
    except (OSError, RuntimeError) as e:
        error_msg = f"Invalid input path: {input_path}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e

    # Validate it's a file, not a directory
    if not input_file.is_file():
        error_msg = f"Path is not a file: {input_path}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Check file size to prevent memory issues
    file_size = input_file.stat().st_size

    if file_size == 0:
        logger.warning(f"Input file is empty: {input_path}")
        return {
            "status": "success",
            "rows": 0,
            "output": None,
            "message": "Input file is empty, nothing to process",
        }

    if file_size > MAX_FILE_SIZE:
        error_msg = (
            f"File too large ({file_size / 1024 / 1024:.1f} MB). "
            f"Maximum allowed: {MAX_FILE_SIZE / 1024 / 1024:.1f} MB"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Get output path from config with validation
    output_dir = config.get("paths", {}).get("output_dir", "data/output")
    output_dir_path = Path(output_dir).resolve()

    # Ensure output directory is created safely
    output_dir_path.mkdir(parents=True, exist_ok=True)

    output_path = output_dir_path / f"{input_file.stem}_processed{input_file.suffix}"

    try:
        # Example processing logic
        # TODO: Replace with actual business logic
        with open(input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Simulate processing
        processed_lines = [line.upper() for line in lines]

        # Write output with explicit encoding
        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(processed_lines)

        result = {
            "status": "success",
            "rows": len(processed_lines),
            "output": str(output_path),
            "message": f"Successfully processed {len(processed_lines)} rows",
        }

        logger.info(f"Processing complete: {result['rows']} rows -> {output_path}")
        return result

    except UnicodeDecodeError as e:
        error_msg = f"File encoding error: {str(e)}"
        logger.exception(error_msg)
        raise ValueError(error_msg) from e

    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        logger.exception(error_msg)
        raise ValueError(error_msg) from e
