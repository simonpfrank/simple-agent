"""Persistence layer for HITL approval decisions and history.

Stores approval records to JSON files for persistence across sessions.
Issue 5-B: Adds file-based persistence to replace in-memory only storage.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ApprovalPersistence(ABC):
    """Abstract base class for approval persistence implementations."""

    @abstractmethod
    def save_request(self, request_id: str, request_data: Dict[str, Any]) -> None:
        """Save an approval request.

        Args:
            request_id: Unique request identifier
            request_data: Request data to persist
        """
        pass

    @abstractmethod
    def save_decision(self, request_id: str, decision: str, timestamp: Optional[datetime] = None) -> None:
        """Save an approval decision.

        Args:
            request_id: Unique request identifier
            decision: "approved" or "rejected"
            timestamp: Decision timestamp (defaults to now)
        """
        pass

    @abstractmethod
    def load_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Load an approval request.

        Args:
            request_id: Unique request identifier

        Returns:
            Request data or None if not found
        """
        pass

    @abstractmethod
    def load_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load approval history.

        Args:
            limit: Maximum number of records to return (None for all)

        Returns:
            List of approval records
        """
        pass

    @abstractmethod
    def delete_request(self, request_id: str) -> None:
        """Delete an approval request.

        Args:
            request_id: Unique request identifier
        """
        pass

    @abstractmethod
    def clear_history(self) -> None:
        """Clear all approval history."""
        pass


class FileApprovalPersistence(ApprovalPersistence):
    """File-based approval persistence using JSON.

    Stores approval requests and decisions in a JSON file for persistence
    across sessions. Each entry includes timestamp and decision information.
    """

    def __init__(self, storage_dir: str = "hitl_data"):
        """Initialize file-based persistence.

        Args:
            storage_dir: Directory to store approval data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.requests_file = self.storage_dir / "approval_requests.json"
        self.history_file = self.storage_dir / "approval_history.json"

        # Initialize files if they don't exist
        self._ensure_files_exist()

    def _ensure_files_exist(self) -> None:
        """Ensure storage files exist."""
        if not self.requests_file.exists():
            self.requests_file.write_text("{}", encoding="utf-8")
        if not self.history_file.exists():
            self.history_file.write_text("[]", encoding="utf-8")

    def _load_json(self, filepath: Path, default: Any = None) -> Any:
        """Load JSON file with error handling.

        Args:
            filepath: Path to JSON file
            default: Default value if load fails

        Returns:
            Loaded JSON data or default
        """
        try:
            if not filepath.exists():
                return default
            with filepath.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {filepath}: {e}")
            return default

    def _save_json(self, filepath: Path, data: Any) -> None:
        """Save data to JSON file with error handling.

        Args:
            filepath: Path to JSON file
            data: Data to save
        """
        try:
            with filepath.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save {filepath}: {e}")
            raise

    def save_request(self, request_id: str, request_data: Dict[str, Any]) -> None:
        """Save an approval request to file.

        Args:
            request_id: Unique request identifier
            request_data: Request data to persist
        """
        requests = self._load_json(self.requests_file, {})
        requests[request_id] = {
            **request_data,
            "request_id": request_id,
            "created_at": datetime.now().isoformat(),
        }
        self._save_json(self.requests_file, requests)
        logger.debug(f"Saved approval request: {request_id}")

    def save_decision(self, request_id: str, decision: str, timestamp: Optional[datetime] = None) -> None:
        """Save an approval decision to history file.

        Args:
            request_id: Unique request identifier
            decision: "approved" or "rejected"
            timestamp: Decision timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        history = self._load_json(self.history_file, [])

        # Find and update request in requests file
        requests = self._load_json(self.requests_file, {})
        if request_id in requests:
            history.append({
                "request_id": request_id,
                "decision": decision,
                "decided_at": timestamp.isoformat(),
                "tool_name": requests[request_id].get("tool_name"),
                "prompt": requests[request_id].get("prompt"),
            })
            self._save_json(self.history_file, history)
            logger.debug(f"Saved approval decision: {request_id} -> {decision}")

    def load_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Load an approval request from file.

        Args:
            request_id: Unique request identifier

        Returns:
            Request data or None if not found
        """
        requests = self._load_json(self.requests_file, {})
        return requests.get(request_id)

    def load_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load approval history from file.

        Args:
            limit: Maximum number of records to return (None for all)

        Returns:
            List of approval records
        """
        history = self._load_json(self.history_file, [])
        if limit:
            return history[-limit:]
        return history

    def delete_request(self, request_id: str) -> None:
        """Delete an approval request from file.

        Args:
            request_id: Unique request identifier
        """
        requests = self._load_json(self.requests_file, {})
        if request_id in requests:
            del requests[request_id]
            self._save_json(self.requests_file, requests)
            logger.debug(f"Deleted approval request: {request_id}")

    def clear_history(self) -> None:
        """Clear all approval history."""
        self._save_json(self.history_file, [])
        logger.info("Cleared approval history")
