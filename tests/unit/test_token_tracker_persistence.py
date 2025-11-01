"""Unit tests for TokenTracker persistence functionality."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from decimal import Decimal

from simple_agent.core.token_tracker_persistence import TokenTrackerManager
from simple_agent.tools.helpers.token_tracker import TokenStats


class TestTokenTrackerManagerCreation:
    """Test TokenTrackerManager initialization."""

    def test_create_manager_with_default_path(self):
        """TokenTrackerManager can be created with default path."""
        manager = TokenTrackerManager()
        assert manager is not None
        assert manager.tracker is not None

    def test_create_manager_with_custom_path(self):
        """TokenTrackerManager can be created with custom file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = os.path.join(tmpdir, "custom_stats.json")
            manager = TokenTrackerManager(stats_file=custom_path)
            assert manager.stats_file == custom_path


class TestTokenTrackerSaveAndLoad:
    """Test saving and loading token tracker state."""

    def test_save_tracker_creates_file(self):
        """Saving tracker creates JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, "stats.json")
            manager = TokenTrackerManager(stats_file=stats_file)

            # Add some stats
            manager.tracker.add_execution(
                input_tokens=100,
                output_tokens=50,
                cost=Decimal("0.01"),
                model="gpt-4o-mini"
            )

            # Save
            manager.save()

            # Verify file exists
            assert os.path.exists(stats_file)

    def test_save_and_load_preserves_data(self):
        """Saving and loading preserves tracker data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, "stats.json")

            # Create, add data, save
            manager1 = TokenTrackerManager(stats_file=stats_file)
            manager1.tracker.add_execution(
                input_tokens=100,
                output_tokens=50,
                cost=Decimal("0.01"),
                model="gpt-4o-mini"
            )
            manager1.save()

            # Load in new manager
            manager2 = TokenTrackerManager(stats_file=stats_file)
            manager2.load()

            # Verify data matches
            stats = manager2.tracker.get_stats()
            assert stats.input_tokens == 100
            assert stats.output_tokens == 50
            assert stats.cost == Decimal("0.01")

    def test_load_nonexistent_file_initializes_empty(self):
        """Loading from nonexistent file initializes empty tracker."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, "nonexistent.json")
            manager = TokenTrackerManager(stats_file=stats_file)
            manager.load()

            # Should have empty tracker
            stats = manager.tracker.get_stats()
            assert stats.input_tokens == 0
            assert stats.output_tokens == 0


class TestTokenTrackerAgentTracking:
    """Test tracking stats per agent."""

    def test_add_execution_for_agent(self):
        """Can add execution stats for specific agent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, "stats.json")
            manager = TokenTrackerManager(stats_file=stats_file)

            # Add execution for agent
            manager.add_execution_for_agent(
                agent_name="researcher",
                input_tokens=200,
                output_tokens=100,
                cost=Decimal("0.05"),
                model="gpt-4o"
            )

            # Verify can retrieve
            agent_stats = manager.get_agent_stats("researcher")
            assert agent_stats is not None
            assert agent_stats["input_tokens"] == 200

    def test_get_all_agent_stats(self):
        """Can retrieve stats for all agents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, "stats.json")
            manager = TokenTrackerManager(stats_file=stats_file)

            # Add executions for multiple agents
            manager.add_execution_for_agent("researcher", 100, 50, Decimal("0.01"), "gpt-4o-mini")
            manager.add_execution_for_agent("analyzer", 150, 75, Decimal("0.02"), "gpt-4o")

            # Get all stats
            all_stats = manager.get_all_agent_stats()
            assert "researcher" in all_stats
            assert "analyzer" in all_stats
            assert all_stats["researcher"]["input_tokens"] == 100
            assert all_stats["analyzer"]["input_tokens"] == 150

    def test_agent_stats_accumulated(self):
        """Multiple executions for same agent accumulate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, "stats.json")
            manager = TokenTrackerManager(stats_file=stats_file)

            # Add multiple executions
            manager.add_execution_for_agent("researcher", 100, 50, Decimal("0.01"), "gpt-4o-mini")
            manager.add_execution_for_agent("researcher", 100, 50, Decimal("0.01"), "gpt-4o-mini")

            # Should accumulate
            agent_stats = manager.get_agent_stats("researcher")
            assert agent_stats["input_tokens"] == 200  # Both added


class TestTokenTrackerTimeFiltering:
    """Test filtering stats by time period."""

    def test_get_stats_with_period_filter(self):
        """Can filter stats by time period (last N hours)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, "stats.json")
            manager = TokenTrackerManager(stats_file=stats_file)

            # Add execution (timestamp should be current)
            manager.add_execution_for_agent("researcher", 100, 50, Decimal("0.01"), "gpt-4o-mini")

            # Get stats for last 24 hours (should include the execution)
            stats = manager.get_stats_for_period(hours=24)
            assert stats is not None
            # Should have the data we just added
            assert stats.get("input_tokens", 0) >= 100

    def test_get_agent_stats_with_period_filter(self):
        """Can filter agent stats by time period."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, "stats.json")
            manager = TokenTrackerManager(stats_file=stats_file)

            manager.add_execution_for_agent("researcher", 100, 50, Decimal("0.01"), "gpt-4o-mini")

            # Get stats for last 1 hour (should include)
            agent_stats = manager.get_agent_stats_for_period("researcher", hours=1)
            assert agent_stats is not None
            assert agent_stats.get("input_tokens", 0) >= 100


class TestTokenTrackerReset:
    """Test resetting tracker state."""

    def test_reset_clears_tracker(self):
        """Reset clears all tracker stats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, "stats.json")
            manager = TokenTrackerManager(stats_file=stats_file)

            manager.add_execution_for_agent("researcher", 100, 50, Decimal("0.01"), "gpt-4o-mini")
            assert manager.tracker.total_input_tokens == 100

            manager.reset()
            assert manager.tracker.total_input_tokens == 0

    def test_reset_removes_file(self):
        """Reset removes saved stats file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, "stats.json")
            manager = TokenTrackerManager(stats_file=stats_file)

            manager.add_execution_for_agent("researcher", 100, 50, Decimal("0.01"), "gpt-4o-mini")
            manager.save()
            assert os.path.exists(stats_file)

            manager.reset()
            # File should be removed
            assert not os.path.exists(stats_file)
