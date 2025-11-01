"""Unit tests for SimpleAgent token tracking integration."""

import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal

from simple_agent.agents.simple_agent import SimpleAgent
from simple_agent.core.agent_result import AgentResult


class TestSimpleAgentTokenTracking:
    """Test SimpleAgent token tracking functionality."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_simple_agent_returns_agent_result(self, mock_model: MagicMock) -> None:
        """SimpleAgent.run() should return AgentResult."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Test response"

            result = agent.run("test prompt")

            # Should return AgentResult
            assert isinstance(result, AgentResult)
            assert str(result) == "Test response"

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_simple_agent_tracks_input_tokens(self, mock_model: MagicMock) -> None:
        """SimpleAgent should track input tokens."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.side_effect = [500, 150]  # input, output
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            result = agent.run("test prompt")

            assert result.input_tokens == 500

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_simple_agent_tracks_output_tokens(self, mock_model: MagicMock) -> None:
        """SimpleAgent should track output tokens."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.side_effect = [500, 150]  # input, output
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            result = agent.run("test prompt")

            assert result.output_tokens == 150

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_simple_agent_calculates_cost(self, mock_model: MagicMock) -> None:
        """SimpleAgent should calculate cost."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.side_effect = [500, 150]  # input, output
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            result = agent.run("test prompt")

            # Should have calculated cost
            assert isinstance(result.cost, Decimal)
            assert result.cost >= Decimal("0")

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_simple_agent_backward_compat_string(self, mock_model: MagicMock) -> None:
        """AgentResult should work as string (backward compatibility)."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Test response"

            result = agent.run("test prompt")

            # Should work as string
            assert isinstance(str(result), str)
            assert "Test response" in str(result)

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_simple_agent_backward_compat_string_concat(self, mock_model: MagicMock) -> None:
        """AgentResult should support string concatenation (backward compatibility)."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Test response"

            result = agent.run("test prompt")

            # Should support string operations
            message = "Agent said: " + str(result)
            assert message == "Agent said: Test response"

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_simple_agent_disable_token_tracking(self, mock_model: MagicMock) -> None:
        """SimpleAgent should support disabling token tracking."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            result = agent.run("test prompt", track_tokens=False)

            # Should not call estimate_tokens when tracking disabled
            assert mock_estimate.call_count == 0
            assert result.input_tokens == 0
            assert result.output_tokens == 0

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_simple_agent_model_info_in_result(self, mock_model: MagicMock) -> None:
        """AgentResult should include model information."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            result = agent.run("test prompt")

            assert result.model == "gpt-4o-mini"

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_simple_agent_to_dict(self, mock_model: MagicMock) -> None:
        """AgentResult should convert to dict."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.side_effect = [500, 150]
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            result = agent.run("test prompt")
            result_dict = result.to_dict()

            assert "response" in result_dict
            assert "tokens" in result_dict
            assert result_dict["tokens"]["input_tokens"] == 500
            assert result_dict["tokens"]["output_tokens"] == 150

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_simple_agent_with_role_includes_role_in_count(self, mock_model: MagicMock) -> None:
        """SimpleAgent should include role in token count."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            role="You are a helpful assistant.",
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            agent.run("test prompt")

            # estimate_tokens should be called at least twice (input and output)
            assert mock_estimate.call_count >= 2
            # First call should have role + prompt
            first_call_args = mock_estimate.call_args_list[0][0][0]
            assert "You are a helpful assistant" in first_call_args
            assert "test prompt" in first_call_args

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_simple_agent_token_budget_still_enforced(self, mock_model: MagicMock) -> None:
        """SimpleAgent should still enforce token budget."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=100,
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 500  # Exceeds budget
            agent.agent = MagicMock()

            with pytest.raises(ValueError) as exc_info:
                agent.run("test prompt")

            assert "token budget" in str(exc_info.value).lower()
