"""Unit tests for SimpleAgent error handling and tracking."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from simple_agent.agents.simple_agent import SimpleAgent
from simple_agent.core.agent_result import AgentResult


class TestSimpleAgentErrorHandling:
    """Test SimpleAgent error handling and reporting."""

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    def test_agent_returns_error_on_exception(self, mock_model: Mock) -> None:
        """SimpleAgent.run() should return AgentResult with error on exception."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100
            agent.agent = MagicMock()
            agent.agent.run.side_effect = RuntimeError("Test error")

            result = agent.run("test prompt")

            # Should return AgentResult with error
            assert isinstance(result, AgentResult)
            assert result.error == "Test error"
            assert result.error_type == "RuntimeError"

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    def test_agent_error_does_not_raise(self, mock_model: Mock) -> None:
        """SimpleAgent.run() should not raise exception, only return error."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100
            agent.agent = MagicMock()
            agent.agent.run.side_effect = ValueError("API Error")

            # Should not raise exception
            result = agent.run("test prompt")

            assert result.error is not None
            assert isinstance(result, AgentResult)

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    def test_agent_error_with_token_tracking(self, mock_model: Mock) -> None:
        """Error tracking should preserve input token count."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 500
            agent.agent = MagicMock()
            agent.agent.run.side_effect = RuntimeError("Model error")

            result = agent.run("test prompt")

            assert result.input_tokens == 500
            assert result.error_type == "RuntimeError"

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    def test_token_budget_error_raises(self, mock_model: Mock) -> None:
        """Token budget error should RAISE (hard limit, not captured)."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=100,
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 500  # Exceeds budget

            # Token budget errors RAISE, not captured in result
            with pytest.raises(ValueError) as exc_info:
                agent.run("test prompt")

            assert "Token budget exceeded" in str(exc_info.value)

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    def test_agent_error_with_partial_tokens(self, mock_model: Mock) -> None:
        """Error after partial token estimation should record tokens."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            # First call: input tokens, then error before output tokens
            mock_estimate.return_value = 300
            agent.agent = MagicMock()
            agent.agent.run.side_effect = RuntimeError("LLM failed")

            result = agent.run("test prompt")

            assert result.input_tokens == 300
            assert result.output_tokens == 0  # No output due to error
            assert result.error_type == "RuntimeError"

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    def test_agent_error_to_dict_includes_error(self, mock_model: Mock) -> None:
        """AgentResult.to_dict() should include error information."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100
            agent.agent = MagicMock()
            agent.agent.run.side_effect = RuntimeError("Test error")

            result = agent.run("test prompt")
            result_dict = result.to_dict()

            assert "error" in result_dict
            assert result_dict["error"]["error_type"] == "RuntimeError"
            assert result_dict["error"]["error_message"] == "Test error"
            assert result_dict["error"]["execution_halted"] is True

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    def test_successful_execution_has_no_error(self, mock_model: Mock) -> None:
        """Successful execution should not have error fields."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Success"

            result = agent.run("test prompt")

            assert result.error is None
            assert result.error_type is None
            result_dict = result.to_dict()
            assert "error" not in result_dict

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    def test_different_error_types_captured(self, mock_model: Mock) -> None:
        """Different exception types should be captured correctly."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        error_cases = [
            (RuntimeError("Runtime error"), "RuntimeError"),
            (ValueError("Value error"), "ValueError"),
            (TypeError("Type error"), "TypeError"),
            (Exception("Generic error"), "Exception"),
        ]

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100

            for exception, expected_type in error_cases:
                agent.agent = MagicMock()
                agent.agent.run.side_effect = exception

                result = agent.run("test prompt")

                assert result.error_type == expected_type
                assert result.error == str(exception)

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    def test_error_with_empty_response(self, mock_model: Mock) -> None:
        """Error case should have empty response."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100
            agent.agent = MagicMock()
            agent.agent.run.side_effect = RuntimeError("Failed")

            result = agent.run("test prompt")

            assert result.response == ""
            assert result.error == "Failed"

    @patch("simple_agent.agents.model_factory.LiteLLMModel")
    def test_error_preserves_model_info(self, mock_model: Mock) -> None:
        """Error result should still include model information."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100
            agent.agent = MagicMock()
            agent.agent.run.side_effect = RuntimeError("Error")

            result = agent.run("test prompt")

            assert result.model == "gpt-4o-mini"
            assert result.error_type == "RuntimeError"
