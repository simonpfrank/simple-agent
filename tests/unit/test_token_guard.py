"""Unit tests for token guard functionality in SimpleAgent."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from simple_agent.agents.simple_agent import SimpleAgent


class TestTokenGuardBasic:
    """Test basic token guard functionality."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_guard_accepts_prompt_within_budget(self, mock_model: Mock) -> None:
        """Prompt within budget should execute normally."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=5000,
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 1000  # Within budget
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            result = agent.run("test prompt")

            # Should execute normally
            assert str(result) == "Response"
            agent.agent.run.assert_called_once()

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_guard_rejects_prompt_exceeding_budget(self, mock_model: Mock) -> None:
        """Prompt exceeding budget should raise error."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=500,
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 1000  # Exceeds budget
            agent.agent = MagicMock()

            with pytest.raises(Exception) as exc_info:
                agent.run("test prompt")

            # Should not call agent.run
            agent.agent.run.assert_not_called()
            # Error should mention token budget
            assert "token" in str(exc_info.value).lower() or "budget" in str(
                exc_info.value
            ).lower()

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_guard_logs_warning_at_threshold(self, mock_model: Mock) -> None:
        """Prompt near warning threshold should log warning."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=5000,
            token_warning_threshold=4500,
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 4700  # Between warning and budget
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            with patch("simple_agent.agents.simple_agent.logger") as mock_logger:
                result = agent.run("test prompt")

                # Should log warning
                mock_logger.warning.assert_called()
                # But should still execute
                assert str(result) == "Response"

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_guard_no_warning_without_threshold(self, mock_model: Mock) -> None:
        """No warning should be logged if threshold not set."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=5000,
            # No token_warning_threshold
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 4000
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            with patch("simple_agent.agents.simple_agent.logger") as mock_logger:
                result = agent.run("test prompt")

                # Should not log warning
                assert not mock_logger.warning.called
                # Should execute normally
                assert str(result) == "Response"


class TestTokenGuardDefaultBehavior:
    """Test token guard with default values."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_no_budget_set_allows_all_prompts(self, mock_model: Mock) -> None:
        """Agent without token_budget should allow all prompts."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            # No token_budget set
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 100000  # Very large
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            result = agent.run("test prompt")

            # Should execute normally (no guard active)
            assert str(result) == "Response"
            agent.agent.run.assert_called_once()

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_guard_with_none_values(self, mock_model: Mock) -> None:
        """Token guard should handle None values gracefully."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=None,
            token_warning_threshold=None,
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 5000
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            result = agent.run("test prompt")

            # Should execute without error
            assert str(result) == "Response"


class TestTokenGuardPromptFormatting:
    """Test that token guard counts complete formatted prompt."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_guard_includes_system_message(self, mock_model: Mock) -> None:
        """Token estimate should include system message."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            role="You are a helpful assistant.",
            token_budget=5000,
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 1000
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            agent.run("user prompt")

            # estimate_tokens should be called (with formatted prompt)
            mock_estimate.assert_called()

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_estimate_called_before_agent_run(self, mock_model: Mock) -> None:
        """estimate_tokens must be called BEFORE agent.run()."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=5000,
        )

        call_order = []

        def track_estimate(*args, **kwargs):
            call_order.append("estimate")
            return 1000

        def track_agent_run(*args, **kwargs):
            call_order.append("agent_run")
            return "Response"

        with patch("simple_agent.agents.simple_agent.estimate_tokens", side_effect=track_estimate):
            agent.agent = MagicMock()
            agent.agent.run.side_effect = track_agent_run

            agent.run("test prompt")

            # estimate_tokens called first for input (token guard), then agent.run, then estimate for output
            assert call_order == ["estimate", "agent_run", "estimate"]
            # Verify input estimate happens before agent run
            assert call_order.index("estimate") < call_order.index("agent_run")


class TestTokenGuardEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_guard_exactly_at_budget(self, mock_model: Mock) -> None:
        """Prompt exactly at budget limit should be accepted."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=1000,
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 1000  # Exactly at budget
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            result = agent.run("test prompt")

            # Should be accepted
            assert str(result) == "Response"

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_guard_one_over_budget(self, mock_model: Mock) -> None:
        """Prompt one token over budget should be rejected."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=1000,
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 1001  # One over budget
            agent.agent = MagicMock()

            with pytest.raises(Exception):
                agent.run("test prompt")

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_guard_empty_prompt(self, mock_model: Mock) -> None:
        """Empty prompt should be counted."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=100,
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 0
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            result = agent.run("")

            # Should execute
            assert str(result) == "Response"
            mock_estimate.assert_called()

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_budget_comparison_is_strict(self, mock_model: Mock) -> None:
        """Token budget check should use > not >=."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=1000,
        )

        with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 1000
            agent.agent = MagicMock()
            agent.agent.run.return_value = "Response"

            # Should NOT raise - exactly at budget is OK
            result = agent.run("test prompt")
            assert str(result) == "Response"


class TestTokenGuardWithRealTokenEstimation:
    """Test token guard with real token counting."""

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_guard_with_real_tiktoken_counting(self, mock_model: Mock) -> None:
        """Token guard should work with real token estimation."""
        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=100,  # Very small budget
            role="You are helpful.",
        )

        agent.agent = MagicMock()
        agent.agent.run.return_value = "Response"

        # Real tiktoken counting - need much larger text to definitely exceed 100 tokens
        # Approximate: 1 token ~= 4 chars, so 100 tokens ~= 400 chars
        real_prompt = "This is a test prompt. " * 20  # ~500 chars, definitely > 100 tokens
        with pytest.raises(ValueError) as exc_info:
            agent.run(real_prompt)

        # Should fail due to token budget
        assert "token" in str(exc_info.value).lower() or "budget" in str(exc_info.value).lower()

    @patch("simple_agent.agents.simple_agent.LiteLLMModel")
    def test_token_guard_with_small_prompt_passes(self, mock_model: Mock) -> None:
        """Small prompt should pass token guard."""
        from simple_agent.tools.helpers.token_counter import estimate_tokens

        agent = SimpleAgent(
            name="test",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=5000,  # Reasonable budget
        )

        agent.agent = MagicMock()
        agent.agent.run.return_value = "Test response"

        # Small prompt
        result = agent.run("hello")

        # Should pass and execute
        assert str(result) == "Test response"
        agent.agent.run.assert_called_once()
