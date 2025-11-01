"""Unit tests for AgentResult wrapper."""

import pytest
from decimal import Decimal

from simple_agent.core.agent_result import AgentResult
from simple_agent.tools.helpers.token_tracker import TokenStats


class TestAgentResult:
    """Test AgentResult for backward compatibility and token tracking."""

    def test_agent_result_initialization(self) -> None:
        """AgentResult should store response and token info."""
        result = AgentResult(
            response="Test response",
            input_tokens=500,
            output_tokens=150,
            total_tokens=650,
            cost=Decimal("0.0075"),
            model="gpt-4o-mini",
        )

        assert result.response == "Test response"
        assert result.input_tokens == 500
        assert result.output_tokens == 150
        assert result.total_tokens == 650
        assert result.cost == Decimal("0.0075")
        assert result.model == "gpt-4o-mini"

    def test_agent_result_string_conversion(self) -> None:
        """AgentResult should convert to string for backward compatibility."""
        result = AgentResult(response="Test response")

        # Should be able to use as string
        assert str(result) == "Test response"

    def test_agent_result_string_comparison(self) -> None:
        """AgentResult string conversion should match response."""
        response_text = "This is a test response"
        result = AgentResult(response=response_text)

        # Should be comparable to string
        assert str(result) == response_text

    def test_agent_result_with_dict_response(self) -> None:
        """AgentResult should handle dict responses."""
        response_dict = {"key": "value", "number": 42}
        result = AgentResult(response=response_dict)

        # String conversion should work
        assert "key" in str(result)

    def test_agent_result_to_dict(self) -> None:
        """AgentResult should convert to dictionary."""
        result = AgentResult(
            response="Test response",
            input_tokens=500,
            output_tokens=150,
            total_tokens=650,
            cost=Decimal("0.0075"),
            model="gpt-4o-mini",
        )

        result_dict = result.to_dict()

        assert result_dict["response"] == "Test response"
        assert result_dict["tokens"]["input_tokens"] == 500
        assert result_dict["tokens"]["output_tokens"] == 150
        assert result_dict["tokens"]["total_tokens"] == 650
        assert result_dict["tokens"]["cost"] == 0.0075
        assert result_dict["tokens"]["model"] == "gpt-4o-mini"

    def test_agent_result_from_response(self) -> None:
        """AgentResult.from_response() should create result easily."""
        result = AgentResult.from_response(
            response="Test response",
            input_tokens=500,
            output_tokens=150,
            cost=Decimal("0.0075"),
            model="gpt-4o-mini",
        )

        assert result.response == "Test response"
        assert result.input_tokens == 500
        assert result.output_tokens == 150
        assert result.total_tokens == 650
        assert result.cost == Decimal("0.0075")

    def test_agent_result_from_token_stats(self) -> None:
        """AgentResult.from_token_stats() should create from TokenStats."""
        stats = TokenStats(
            input_tokens=500,
            output_tokens=150,
            cost=Decimal("0.0075"),
            model="gpt-4o-mini",
        )
        result = AgentResult.from_token_stats("Test response", stats)

        assert result.response == "Test response"
        assert result.input_tokens == 500
        assert result.output_tokens == 150
        assert result.total_tokens == 650
        assert result.cost == Decimal("0.0075")
        assert result.model == "gpt-4o-mini"

    def test_agent_result_zero_tokens(self) -> None:
        """AgentResult should handle zero tokens."""
        result = AgentResult(response="Response")

        assert result.input_tokens == 0
        assert result.output_tokens == 0
        assert result.total_tokens == 0
        assert result.cost == Decimal("0")

    def test_agent_result_repr(self) -> None:
        """AgentResult should have useful repr."""
        result = AgentResult(
            response="Test response with some text",
            input_tokens=500,
            output_tokens=150,
            total_tokens=650,
            cost=Decimal("0.0075"),
        )

        repr_str = repr(result)

        # Should include meaningful info
        assert "Test response" in repr_str
        assert "650" in repr_str
        assert "0.0075" in repr_str

    def test_agent_result_long_response_repr(self) -> None:
        """AgentResult repr should truncate long responses."""
        long_response = "X" * 1000
        result = AgentResult(response=long_response)

        repr_str = repr(result)

        # Should be truncated (first 50 chars + ...)
        assert len(repr_str) < len(long_response)
        assert "..." in repr_str

    def test_agent_result_cost_precision(self) -> None:
        """AgentResult should maintain Decimal cost precision."""
        cost = Decimal("0.000123456789")
        result = AgentResult(response="Test", cost=cost)

        assert result.cost == cost
        assert isinstance(result.cost, Decimal)

    def test_agent_result_dict_cost_float(self) -> None:
        """AgentResult.to_dict() should convert cost to float."""
        cost = Decimal("0.0075")
        result = AgentResult(response="Test", cost=cost)

        result_dict = result.to_dict()

        assert result_dict["tokens"]["cost"] == 0.0075
        assert isinstance(result_dict["tokens"]["cost"], float)

    def test_agent_result_backward_compat_string_usage(self) -> None:
        """AgentResult should work in string contexts (backward compat)."""
        result = AgentResult(response="Test response")

        # Should work in string concatenation
        message = "Agent said: " + str(result)
        assert message == "Agent said: Test response"

        # Should work in string formatting
        formatted = f"Response: {result}"
        assert formatted == "Response: Test response"

    def test_agent_result_backward_compat_len(self) -> None:
        """AgentResult can be used with len on response."""
        result = AgentResult(response="Test")

        # Can get length of response string
        assert len(str(result)) == 4

    def test_agent_result_empty_response(self) -> None:
        """AgentResult should handle empty responses."""
        result = AgentResult(response="")

        assert str(result) == ""
        assert result.response == ""
        assert result.total_tokens == 0
