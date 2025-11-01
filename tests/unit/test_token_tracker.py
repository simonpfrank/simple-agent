"""Unit tests for token tracking and cost calculation."""

import pytest
from decimal import Decimal

from simple_agent.tools.helpers.token_tracker import (
    TokenStats,
    StepTokenStats,
    FlowTokenStats,
    TokenTracker,
)


class TestTokenStats:
    """Test TokenStats data class."""

    def test_token_stats_initialization(self) -> None:
        """TokenStats should calculate total tokens."""
        stats = TokenStats(
            input_tokens=500,
            output_tokens=150,
            cost=Decimal("0.0075"),
            model="gpt-4o-mini",
        )

        assert stats.input_tokens == 500
        assert stats.output_tokens == 150
        assert stats.total_tokens == 650
        assert stats.cost == Decimal("0.0075")
        assert stats.model == "gpt-4o-mini"

    def test_token_stats_zero_tokens(self) -> None:
        """TokenStats should handle zero tokens."""
        stats = TokenStats(input_tokens=0, output_tokens=0, cost=Decimal("0"))

        assert stats.total_tokens == 0
        assert stats.cost == Decimal("0")

    def test_token_stats_only_input(self) -> None:
        """TokenStats should handle input-only tokens."""
        stats = TokenStats(input_tokens=1000, output_tokens=0)

        assert stats.total_tokens == 1000

    def test_token_stats_only_output(self) -> None:
        """TokenStats should handle output-only tokens."""
        stats = TokenStats(input_tokens=0, output_tokens=500)

        assert stats.total_tokens == 500


class TestStepTokenStats:
    """Test StepTokenStats for flow steps."""

    def test_step_token_stats_initialization(self) -> None:
        """StepTokenStats should track agent name and tokens."""
        stats = StepTokenStats(
            agent_name="researcher",
            input_tokens=1000,
            output_tokens=800,
            cost=Decimal("0.0180"),
        )

        assert stats.agent_name == "researcher"
        assert stats.input_tokens == 1000
        assert stats.output_tokens == 800
        assert stats.total_tokens == 1800
        assert stats.cost == Decimal("0.0180")

    def test_step_token_stats_multiple_agents(self) -> None:
        """StepTokenStats should support multiple different agents."""
        planner_stats = StepTokenStats(
            agent_name="planner",
            input_tokens=200,
            output_tokens=150,
        )
        researcher_stats = StepTokenStats(
            agent_name="researcher",
            input_tokens=1200,
            output_tokens=950,
        )

        assert planner_stats.agent_name == "planner"
        assert researcher_stats.agent_name == "researcher"
        assert planner_stats.total_tokens == 350
        assert researcher_stats.total_tokens == 2150


class TestFlowTokenStats:
    """Test FlowTokenStats for multi-step flows."""

    def test_flow_token_stats_initialization(self) -> None:
        """FlowTokenStats should initialize with zero totals."""
        stats = FlowTokenStats()

        assert stats.total_input_tokens == 0
        assert stats.total_output_tokens == 0
        assert stats.total_tokens == 0
        assert stats.total_cost == Decimal("0")
        assert len(stats.steps) == 0

    def test_flow_token_stats_add_step(self) -> None:
        """FlowTokenStats should accumulate step statistics."""
        flow_stats = FlowTokenStats()

        step1 = StepTokenStats(
            agent_name="planner",
            input_tokens=200,
            output_tokens=150,
            cost=Decimal("0.0005"),
        )
        flow_stats.add_step(step1)

        assert flow_stats.total_input_tokens == 200
        assert flow_stats.total_output_tokens == 150
        assert flow_stats.total_tokens == 350
        assert flow_stats.total_cost == Decimal("0.0005")
        assert len(flow_stats.steps) == 1

    def test_flow_token_stats_multiple_steps(self) -> None:
        """FlowTokenStats should accumulate multiple steps."""
        flow_stats = FlowTokenStats()

        step1 = StepTokenStats(
            agent_name="planner",
            input_tokens=200,
            output_tokens=150,
            cost=Decimal("0.0005"),
        )
        step2 = StepTokenStats(
            agent_name="researcher",
            input_tokens=1200,
            output_tokens=950,
            cost=Decimal("0.0320"),
        )
        step3 = StepTokenStats(
            agent_name="summarizer",
            input_tokens=500,
            output_tokens=200,
            cost=Decimal("0.0015"),
        )

        flow_stats.add_step(step1)
        flow_stats.add_step(step2)
        flow_stats.add_step(step3)

        assert flow_stats.total_input_tokens == 1900
        assert flow_stats.total_output_tokens == 1300
        assert flow_stats.total_tokens == 3200
        assert flow_stats.total_cost == Decimal("0.0340")
        assert len(flow_stats.steps) == 3

    def test_flow_token_stats_to_dict(self) -> None:
        """FlowTokenStats should convert to dictionary."""
        flow_stats = FlowTokenStats()

        step = StepTokenStats(
            agent_name="researcher",
            input_tokens=1000,
            output_tokens=500,
            cost=Decimal("0.0225"),
            model="gpt-4o-mini",
        )
        flow_stats.add_step(step)

        result = flow_stats.to_dict()

        assert result["total_input_tokens"] == 1000
        assert result["total_output_tokens"] == 500
        assert result["total_tokens"] == 1500
        assert result["total_cost"] == 0.0225
        assert len(result["steps"]) == 1
        assert result["steps"][0]["agent"] == "researcher"
        assert result["steps"][0]["total_tokens"] == 1500


class TestTokenTracker:
    """Test TokenTracker for accumulating statistics."""

    def test_token_tracker_initialization(self) -> None:
        """TokenTracker should initialize with zero values."""
        tracker = TokenTracker()

        assert tracker.total_input_tokens == 0
        assert tracker.total_output_tokens == 0
        assert tracker.total_cost == Decimal("0")
        assert len(tracker.stats) == 0

    def test_token_tracker_add_execution(self) -> None:
        """TokenTracker should record executions."""
        tracker = TokenTracker()

        tracker.add_execution(
            input_tokens=500,
            output_tokens=150,
            cost=Decimal("0.0075"),
            model="gpt-4o-mini",
        )

        assert tracker.total_input_tokens == 500
        assert tracker.total_output_tokens == 150
        assert tracker.total_cost == Decimal("0.0075")
        assert len(tracker.stats) == 1

    def test_token_tracker_multiple_executions(self) -> None:
        """TokenTracker should accumulate multiple executions."""
        tracker = TokenTracker()

        tracker.add_execution(
            input_tokens=500,
            output_tokens=150,
            cost=Decimal("0.0075"),
        )
        tracker.add_execution(
            input_tokens=1000,
            output_tokens=500,
            cost=Decimal("0.0225"),
        )

        assert tracker.total_input_tokens == 1500
        assert tracker.total_output_tokens == 650
        assert tracker.total_cost == Decimal("0.0300")
        assert len(tracker.stats) == 2

    def test_token_tracker_get_stats(self) -> None:
        """TokenTracker should return aggregated statistics."""
        tracker = TokenTracker()

        tracker.add_execution(
            input_tokens=500,
            output_tokens=150,
            cost=Decimal("0.0075"),
            model="gpt-4o-mini",
        )
        tracker.add_execution(
            input_tokens=1000,
            output_tokens=500,
            cost=Decimal("0.0225"),
            model="gpt-4o-mini",
        )

        stats = tracker.get_stats()

        assert stats.input_tokens == 1500
        assert stats.output_tokens == 650
        assert stats.total_tokens == 2150
        assert stats.cost == Decimal("0.0300")
        assert stats.model == "gpt-4o-mini"

    def test_token_tracker_to_dict(self) -> None:
        """TokenTracker should convert to dictionary."""
        tracker = TokenTracker()

        tracker.add_execution(
            input_tokens=500,
            output_tokens=150,
            cost=Decimal("0.0075"),
            model="gpt-4o-mini",
        )

        result = tracker.to_dict()

        assert result["input_tokens"] == 500
        assert result["output_tokens"] == 150
        assert result["total_tokens"] == 650
        assert result["cost"] == 0.0075

    def test_token_tracker_reset(self) -> None:
        """TokenTracker should reset statistics."""
        tracker = TokenTracker()

        tracker.add_execution(
            input_tokens=500,
            output_tokens=150,
            cost=Decimal("0.0075"),
        )
        assert tracker.total_input_tokens == 500

        tracker.reset()

        assert tracker.total_input_tokens == 0
        assert tracker.total_output_tokens == 0
        assert tracker.total_cost == Decimal("0")
        assert len(tracker.stats) == 0

    def test_token_tracker_mixed_models(self) -> None:
        """TokenTracker should handle mixed models."""
        tracker = TokenTracker()

        tracker.add_execution(
            input_tokens=500,
            output_tokens=150,
            model="gpt-4o-mini",
        )
        tracker.add_execution(
            input_tokens=1000,
            output_tokens=500,
            model="claude-3-opus",
        )

        stats = tracker.get_stats()

        assert stats.model == "mixed"
        assert stats.total_tokens == 2150
