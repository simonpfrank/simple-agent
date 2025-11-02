"""Persistence layer for TokenTracker - save/load token usage statistics."""

import json
import os
import fcntl
import logging
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from decimal import Decimal

from simple_agent.tools.helpers.token_tracker import TokenTracker, TokenStats

logger = logging.getLogger(__name__)


class TokenTrackerManager:
    """Manages persistent storage of token tracking data."""

    def __init__(self, stats_file: Optional[str] = None):
        """Initialize TokenTrackerManager.

        Args:
            stats_file: Path to JSON file for storing stats. If None, uses default
                       location: $HOME/.simple-agent/token_stats.json
        """
        if stats_file is None:
            # Default location
            home = os.path.expanduser("~")
            stats_dir = os.path.join(home, ".simple-agent")
            os.makedirs(stats_dir, exist_ok=True)
            stats_file = os.path.join(stats_dir, "token_stats.json")

        self.stats_file = stats_file
        self.tracker = TokenTracker()
        self._agent_stats: Dict[str, Dict] = {}  # Track per-agent stats with timestamps

    def add_execution_for_agent(
        self,
        agent_name: str,
        input_tokens: int,
        output_tokens: int,
        cost: Decimal,
        model: str,
    ) -> None:
        """Record a token usage execution for an agent.

        Args:
            agent_name: Name of the agent
            input_tokens: Tokens in the input
            output_tokens: Tokens in the output
            cost: Cost in USD
            model: Model name
        """
        # Add to main tracker
        self.tracker.add_execution(input_tokens, output_tokens, cost, model)

        # Add to per-agent tracking
        if agent_name not in self._agent_stats:
            self._agent_stats[agent_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost": 0.0,
                "executions": [],
            }

        agent_data = self._agent_stats[agent_name]
        agent_data["input_tokens"] += input_tokens
        agent_data["output_tokens"] += output_tokens
        agent_data["total_tokens"] = agent_data["input_tokens"] + agent_data["output_tokens"]
        agent_data["cost"] += float(cost)

        # Record execution with timestamp
        agent_data["executions"].append({
            "timestamp": datetime.now().isoformat(),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": float(cost),
            "model": model,
        })

    def set_token_budget(self, agent_name: str, budget: int) -> None:
        """Set token budget for an agent.

        Args:
            agent_name: Name of the agent
            budget: Token budget (must be > 0)

        Raises:
            ValueError: If budget <= 0
        """
        if budget <= 0:
            raise ValueError("Budget must be greater than 0")

        if budget > 1_000_000_000:
            raise ValueError("Budget cannot exceed 1 billion tokens")

        if agent_name not in self._agent_stats:
            self._agent_stats[agent_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost": 0.0,
                "executions": [],
                "token_budget": budget,
            }
        else:
            self._agent_stats[agent_name]["token_budget"] = budget

    def get_agent_stats(self, agent_name: str) -> Optional[Dict]:
        """Get aggregated stats for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Dict with agent stats or None if agent not found
        """
        return self._agent_stats.get(agent_name)

    def get_all_agent_stats(self) -> Dict[str, Dict]:
        """Get stats for all agents.

        Returns:
            Dict mapping agent names to their stats
        """
        return self._agent_stats.copy()

    def get_stats_for_period(self, hours: int = 24) -> Optional[Dict]:
        """Get overall stats for the last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            Dict with stats for the period
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        total_input = 0
        total_output = 0
        total_cost = 0.0

        for agent_stats in self._agent_stats.values():
            for execution in agent_stats.get("executions", []):
                exec_time = datetime.fromisoformat(execution["timestamp"])
                if exec_time >= cutoff_time:
                    total_input += execution["input_tokens"]
                    total_output += execution["output_tokens"]
                    total_cost += execution["cost"]

        return {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "cost": total_cost,
        }

    def get_agent_stats_for_period(
        self,
        agent_name: str,
        hours: int = 24,
    ) -> Optional[Dict]:
        """Get stats for an agent for the last N hours.

        Args:
            agent_name: Name of the agent
            hours: Number of hours to look back

        Returns:
            Dict with agent stats for the period
        """
        agent_stats = self._agent_stats.get(agent_name)
        if agent_stats is None:
            return None

        cutoff_time = datetime.now() - timedelta(hours=hours)
        total_input = 0
        total_output = 0
        total_cost = 0.0

        for execution in agent_stats.get("executions", []):
            exec_time = datetime.fromisoformat(execution["timestamp"])
            if exec_time >= cutoff_time:
                total_input += execution["input_tokens"]
                total_output += execution["output_tokens"]
                total_cost += execution["cost"]

        return {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "cost": total_cost,
        }

    def save(self) -> None:
        """Save tracker state to file with file locking and atomic writes.

        Uses fcntl exclusive locking (Unix) and atomic writes via temp file
        to prevent race conditions with concurrent saves.
        """
        data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "global_stats": {
                "total_input_tokens": self.tracker.total_input_tokens,
                "total_output_tokens": self.tracker.total_output_tokens,
                "total_cost": float(self.tracker.total_cost),
                "stats": [
                    {
                        "input_tokens": s.input_tokens,
                        "output_tokens": s.output_tokens,
                        "cost": float(s.cost),
                        "model": s.model,
                    }
                    for s in self.tracker.stats
                ],
            },
            "agent_stats": self._agent_stats,
        }

        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)

        # Use atomic write with temporary file and file locking
        stats_dir = os.path.dirname(self.stats_file)
        temp_fd, temp_path = tempfile.mkstemp(dir=stats_dir, suffix=".tmp")

        try:
            # Acquire exclusive lock on temp file (Unix only)
            fcntl.flock(temp_fd, fcntl.LOCK_EX)

            # Write to temp file
            with os.fdopen(temp_fd, "w") as f:
                json.dump(data, f, indent=2)

            # Atomically replace original file
            os.replace(temp_path, self.stats_file)
            logger.debug(f"Successfully saved token stats to {self.stats_file}")

        except OSError as e:
            logger.error(f"Failed to save token stats: {e}", exc_info=True)
            # Clean up temp file if it still exists
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise

    def load(self) -> None:
        """Load tracker state from file with error recovery.

        If file is corrupted or missing, starts fresh with empty tracking.
        """
        if not os.path.exists(self.stats_file):
            # No saved state, start fresh
            self.tracker = TokenTracker()
            self._agent_stats = {}
            logger.debug(f"No existing stats file at {self.stats_file}, starting fresh")
            return

        try:
            with open(self.stats_file, "r") as f:
                # Acquire shared lock during read (non-blocking for concurrent reads)
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                except OSError:
                    # fcntl not available (Windows), proceed without lock
                    pass

                data = json.load(f)

            # Load agent stats
            self._agent_stats = data.get("agent_stats", {})

            # Reconstruct tracker from global stats
            self.tracker = TokenTracker()
            global_stats = data.get("global_stats", {})
            for stat in global_stats.get("stats", []):
                self.tracker.add_execution(
                    input_tokens=stat["input_tokens"],
                    output_tokens=stat["output_tokens"],
                    cost=Decimal(str(stat["cost"])),
                    model=stat["model"],
                )
            logger.debug(f"Successfully loaded token stats from {self.stats_file}")

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Corrupted file, start fresh
            logger.warning(
                f"Failed to load token stats from {self.stats_file}: {e}. "
                f"Starting with empty tracking.",
                exc_info=True
            )
            self.tracker = TokenTracker()
            self._agent_stats = {}

    def reset(self) -> None:
        """Reset all statistics and remove file."""
        self.tracker = TokenTracker()
        self._agent_stats = {}

        if os.path.exists(self.stats_file):
            os.remove(self.stats_file)
