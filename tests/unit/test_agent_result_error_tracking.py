"""Unit tests for AgentResult error tracking functionality."""

import pytest
from decimal import Decimal

from simple_agent.core.agent_result import AgentResult


class TestAgentResultErrorTracking:
    """Test AgentResult error tracking capabilities."""

    def test_agent_result_with_error_message(self) -> None:
        """AgentResult should store error message."""
        result = AgentResult(
            response="",
            error="Connection timeout",
            error_type="TimeoutError",
        )

        assert result.error == "Connection timeout"
        assert result.error_type == "TimeoutError"

    def test_agent_result_error_in_dict(self) -> None:
        """AgentResult.to_dict() should include error information."""
        result = AgentResult(
            response="",
            input_tokens=100,
            error="Invalid input",
            error_type="ValueError",
        )

        result_dict = result.to_dict()

        assert "error" in result_dict
        assert result_dict["error"]["error_type"] == "ValueError"
        assert result_dict["error"]["error_message"] == "Invalid input"
        assert result_dict["error"]["execution_halted"] is True

    def test_agent_result_no_error_in_dict(self) -> None:
        """AgentResult.to_dict() should not include error section if no error."""
        result = AgentResult(response="Success")

        result_dict = result.to_dict()

        assert "error" not in result_dict

    def test_agent_result_from_response_with_error(self) -> None:
        """AgentResult.from_response() should support error parameters."""
        result = AgentResult.from_response(
            response="",
            input_tokens=200,
            output_tokens=50,
            cost=Decimal("0.01"),
            model="gpt-4o-mini",
            error="Model error occurred",
            error_type="RuntimeError",
        )

        assert result.error == "Model error occurred"
        assert result.error_type == "RuntimeError"
        assert result.input_tokens == 200

    def test_agent_result_error_with_token_stats(self) -> None:
        """AgentResult should track tokens even when error occurs."""
        result = AgentResult(
            response="",
            input_tokens=500,
            output_tokens=0,  # No output due to error
            total_tokens=500,
            cost=Decimal("0.0025"),
            error="LLM call failed",
            error_type="APIError",
        )

        assert result.input_tokens == 500
        assert result.output_tokens == 0
        assert result.error == "LLM call failed"

    def test_agent_result_error_without_message(self) -> None:
        """AgentResult should handle error_type without message."""
        result = AgentResult(
            response="",
            error_type="CustomError",
        )

        result_dict = result.to_dict()

        assert result_dict["error"]["error_type"] == "CustomError"
        assert result_dict["error"]["error_message"] is None

    def test_agent_result_error_without_type(self) -> None:
        """AgentResult should handle error message without type."""
        result = AgentResult(
            response="",
            error="Something went wrong",
        )

        result_dict = result.to_dict()

        assert result_dict["error"]["error_type"] is None
        assert result_dict["error"]["error_message"] == "Something went wrong"

    def test_agent_result_string_conversion_with_error(self) -> None:
        """AgentResult string conversion should work even with error."""
        result = AgentResult(
            response="",
            error="Error occurred",
            error_type="RuntimeError",
        )

        # Should convert to empty string (response is empty)
        assert str(result) == ""

    def test_agent_result_with_partial_response_on_error(self) -> None:
        """AgentResult can contain partial response even when error occurs."""
        result = AgentResult(
            response="Partial result before error",
            input_tokens=300,
            output_tokens=50,
            error="Execution halted mid-stream",
            error_type="ExecutionError",
        )

        assert str(result) == "Partial result before error"
        assert result.error == "Execution halted mid-stream"

    def test_agent_result_error_preserves_cost(self) -> None:
        """AgentResult should preserve cost information even on error."""
        cost = Decimal("0.0123")
        result = AgentResult(
            response="",
            input_tokens=400,
            output_tokens=25,
            total_tokens=425,
            cost=cost,
            error="Post-processing error",
            error_type="ProcessingError",
        )

        assert result.cost == cost
        assert result.total_tokens == 425

    def test_agent_result_error_repr(self) -> None:
        """AgentResult repr should handle error cases."""
        result = AgentResult(
            response="",
            error="Test error",
            error_type="TestError",
        )

        repr_str = repr(result)

        # Should not crash and should be a string
        assert isinstance(repr_str, str)

    def test_agent_result_multiple_errors_replaced(self) -> None:
        """AgentResult should allow error information to be replaced."""
        result = AgentResult(
            response="",
            error="First error",
            error_type="FirstError",
        )

        # Simulate replacement by creating new result
        result2 = AgentResult(
            response="",
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost=result.cost,
            error="Second error",
            error_type="SecondError",
        )

        assert result2.error == "Second error"
        assert result2.error_type == "SecondError"


class TestAgentResultErrorInExecution:
    """Test error tracking in realistic agent execution scenarios."""

    def test_token_budget_error_tracking(self) -> None:
        """Token budget error should be trackable in result."""
        result = AgentResult(
            response="",
            input_tokens=25000,
            error="Token budget exceeded: prompt has 25000 tokens but budget is 20000",
            error_type="ValueError",
        )

        assert result.error_type == "ValueError"
        assert "Token budget exceeded" in result.error

    def test_api_error_tracking(self) -> None:
        """API errors should be captured with details."""
        result = AgentResult(
            response="",
            input_tokens=1000,
            output_tokens=0,
            error="Rate limit exceeded: 429 Too Many Requests",
            error_type="APIError",
        )

        assert result.error_type == "APIError"
        assert "429" in result.error
        assert result.output_tokens == 0

    def test_timeout_error_tracking(self) -> None:
        """Timeout errors should preserve input tokens."""
        result = AgentResult(
            response="",
            input_tokens=800,
            output_tokens=0,
            error="Request timed out after 30 seconds",
            error_type="TimeoutError",
        )

        result_dict = result.to_dict()

        assert result_dict["tokens"]["input_tokens"] == 800
        assert result_dict["error"]["error_type"] == "TimeoutError"

    def test_execution_halted_flag(self) -> None:
        """Error dict should always include execution_halted flag."""
        result = AgentResult(
            response="",
            error="Some error",
            error_type="SomeError",
        )

        result_dict = result.to_dict()

        assert result_dict["error"]["execution_halted"] is True
