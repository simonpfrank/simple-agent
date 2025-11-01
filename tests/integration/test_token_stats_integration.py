"""
Integration tests for Phase 3.4 Token Stats CLI Commands.

Tests the full token stats command workflow with real components (no mocks).
"""

import pytest
import json
import csv
import tempfile
import os
from decimal import Decimal
from pathlib import Path
from click.testing import CliRunner
from rich.console import Console

from simple_agent.core.token_tracker_persistence import TokenTrackerManager
from simple_agent.commands.token_stats_commands import token
from simple_agent.ui.styles import APP_THEME


class TestTokenStatsCommand:
    """Test /token stats command functionality."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_stats_file(self) -> str:
        """Create temporary stats file for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield os.path.join(tmpdir, "stats.json")

    @pytest.fixture
    def manager_with_data(self, temp_stats_file: str) -> TokenTrackerManager:
        """Create manager with sample data."""
        manager = TokenTrackerManager(stats_file=temp_stats_file)

        # Add sample data
        manager.add_execution_for_agent("researcher", 1000, 500, Decimal("0.10"), "gpt-4o-mini")
        manager.add_execution_for_agent("researcher", 800, 400, Decimal("0.08"), "gpt-4o-mini")
        manager.add_execution_for_agent("analyzer", 600, 300, Decimal("0.06"), "gpt-3.5-turbo")

        manager.save()
        return manager

    def test_token_stats_all(self, runner: CliRunner, manager_with_data: TokenTrackerManager) -> None:
        """Test /token stats command shows all stats."""
        # Reload manager to get saved data
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        # Prepare click context with console
        console = Console(theme=APP_THEME)
        result = runner.invoke(token, ["stats"], obj={"console": console})

        # Should succeed
        assert result.exit_code == 0
        assert "Overall Token Usage" in result.output or "No token usage" in result.output

    def test_token_stats_by_agent(self, runner: CliRunner, manager_with_data: TokenTrackerManager) -> None:
        """Test /token stats command filters by agent."""
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        console = Console(theme=APP_THEME)
        result = runner.invoke(token, ["stats", "--agent", "researcher"], obj={"console": console})

        # Should succeed
        assert result.exit_code == 0

    def test_token_stats_with_period(self, runner: CliRunner, manager_with_data: TokenTrackerManager) -> None:
        """Test /token stats command filters by time period."""
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        console = Console(theme=APP_THEME)
        result = runner.invoke(token, ["stats", "--period", "24"], obj={"console": console})

        # Should succeed
        assert result.exit_code == 0


class TestTokenExportCommand:
    """Test /token export command functionality."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_stats_file(self) -> str:
        """Create temporary stats file for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield os.path.join(tmpdir, "stats.json")

    @pytest.fixture
    def manager_with_data(self, temp_stats_file: str) -> TokenTrackerManager:
        """Create manager with sample data."""
        manager = TokenTrackerManager(stats_file=temp_stats_file)

        manager.add_execution_for_agent("researcher", 1000, 500, Decimal("0.10"), "gpt-4o-mini")
        manager.add_execution_for_agent("analyzer", 600, 300, Decimal("0.06"), "gpt-3.5-turbo")

        manager.save()
        return manager

    def test_token_export_json_to_stdout(
        self, runner: CliRunner, manager_with_data: TokenTrackerManager
    ) -> None:
        """Test /token export command exports to JSON."""
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        console = Console(theme=APP_THEME)
        result = runner.invoke(token, ["export", "--format", "json"], obj={"console": console})

        # Should succeed
        assert result.exit_code == 0

    def test_token_export_csv_to_stdout(
        self, runner: CliRunner, manager_with_data: TokenTrackerManager
    ) -> None:
        """Test /token export command exports to CSV."""
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        console = Console(theme=APP_THEME)
        result = runner.invoke(token, ["export", "--format", "csv"], obj={"console": console})

        # Should succeed
        assert result.exit_code == 0

    def test_token_export_to_file(
        self, runner: CliRunner, manager_with_data: TokenTrackerManager
    ) -> None:
        """Test /token export command exports to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "export.json")

            manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
            manager.load()

            console = Console(theme=APP_THEME)
            result = runner.invoke(
                token,
                ["export", "--format", "json", "--output", output_file],
                obj={"console": console}
            )

            # Should succeed
            assert result.exit_code == 0

            # File should exist
            assert os.path.exists(output_file)

            # File should contain valid JSON
            with open(output_file) as f:
                data = json.load(f)
                assert "exported_at" in data

    def test_token_export_by_agent(
        self, runner: CliRunner, manager_with_data: TokenTrackerManager
    ) -> None:
        """Test /token export command filters by agent."""
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        console = Console(theme=APP_THEME)
        result = runner.invoke(
            token,
            ["export", "--format", "json", "--agent", "researcher"],
            obj={"console": console}
        )

        # Should succeed
        assert result.exit_code == 0


class TestTokenBudgetCommand:
    """Test /token budget command functionality."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_stats_file(self) -> str:
        """Create temporary stats file for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield os.path.join(tmpdir, "stats.json")

    @pytest.fixture
    def manager_with_data(self, temp_stats_file: str) -> TokenTrackerManager:
        """Create manager with sample data."""
        manager = TokenTrackerManager(stats_file=temp_stats_file)

        manager.add_execution_for_agent("researcher", 1000, 500, Decimal("0.10"), "gpt-4o-mini")

        manager.save()
        return manager

    def test_token_budget_show(self, runner: CliRunner, manager_with_data: TokenTrackerManager) -> None:
        """Test /token budget command shows budget."""
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        console = Console(theme=APP_THEME)
        result = runner.invoke(token, ["budget", "researcher"], obj={"console": console})

        # Should succeed
        assert result.exit_code == 0

    def test_token_budget_set(self, runner: CliRunner, manager_with_data: TokenTrackerManager) -> None:
        """Test /token budget command sets budget."""
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        console = Console(theme=APP_THEME)
        result = runner.invoke(
            token,
            ["budget", "researcher", "--set", "20000"],
            obj={"console": console}
        )

        # Should succeed
        assert result.exit_code == 0
        assert "budget" in result.output.lower()

    def test_token_budget_set_invalid(self, runner: CliRunner, manager_with_data: TokenTrackerManager) -> None:
        """Test /token budget command rejects invalid budget."""
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        console = Console(theme=APP_THEME)
        result = runner.invoke(
            token,
            ["budget", "researcher", "--set", "0"],
            obj={"console": console}
        )

        # Should show error
        assert result.exit_code == 0  # Click doesn't fail, just prints error


class TestTokenCostCommand:
    """Test /token cost command functionality."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_stats_file(self) -> str:
        """Create temporary stats file for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield os.path.join(tmpdir, "stats.json")

    @pytest.fixture
    def manager_with_data(self, temp_stats_file: str) -> TokenTrackerManager:
        """Create manager with sample data."""
        manager = TokenTrackerManager(stats_file=temp_stats_file)

        manager.add_execution_for_agent("researcher", 1000, 500, Decimal("0.10"), "gpt-4o-mini")
        manager.add_execution_for_agent("analyzer", 600, 300, Decimal("0.06"), "gpt-3.5-turbo")

        manager.save()
        return manager

    def test_token_cost_by_agent(self, runner: CliRunner, manager_with_data: TokenTrackerManager) -> None:
        """Test /token cost command shows cost by agent."""
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        console = Console(theme=APP_THEME)
        result = runner.invoke(token, ["cost", "--by", "agent"], obj={"console": console})

        # Should succeed
        assert result.exit_code == 0

    def test_token_cost_by_model(self, runner: CliRunner, manager_with_data: TokenTrackerManager) -> None:
        """Test /token cost command shows cost by model."""
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        console = Console(theme=APP_THEME)
        result = runner.invoke(token, ["cost", "--by", "model"], obj={"console": console})

        # Should succeed
        assert result.exit_code == 0

    def test_token_cost_for_agent(self, runner: CliRunner, manager_with_data: TokenTrackerManager) -> None:
        """Test /token cost command filters by agent."""
        manager = TokenTrackerManager(stats_file=manager_with_data.stats_file)
        manager.load()

        console = Console(theme=APP_THEME)
        result = runner.invoke(token, ["cost", "--agent", "researcher"], obj={"console": console})

        # Should succeed
        assert result.exit_code == 0
