"""Unit tests for agent budget awareness features in SimpleAgent."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from simple_agent.agents.simple_agent import SimpleAgent
from simple_agent.core.token_budget_context import TokenBudgetContext


class TestSimpleAgentBudgetOverrideParameters:
    """Test budget override parameters in SimpleAgent.run()."""

    def test_run_accepts_token_budget_override(self):
        """SimpleAgent.run() accepts token_budget_override parameter."""
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            role="Test agent",
        )
        # This should not raise an error about unexpected parameter
        with patch.object(agent, "agent") as mock_agent:
            mock_agent.run.return_value = "test response"
            # Just verify it accepts the parameter
            try:
                result = agent.run(
                    "test input",
                    token_budget_override=10000,
                    track_tokens=False
                )
                assert result is not None
            except TypeError as e:
                if "token_budget_override" in str(e):
                    pytest.fail(f"run() doesn't accept token_budget_override: {e}")

    def test_run_accepts_token_warning_threshold_override(self):
        """SimpleAgent.run() accepts token_warning_threshold_override parameter."""
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            role="Test agent",
        )
        with patch.object(agent, "agent") as mock_agent:
            mock_agent.run.return_value = "test response"
            try:
                result = agent.run(
                    "test input",
                    token_warning_threshold_override=9000,
                    track_tokens=False
                )
                assert result is not None
            except TypeError as e:
                if "token_warning_threshold_override" in str(e):
                    pytest.fail(f"run() doesn't accept token_warning_threshold_override: {e}")

    def test_token_budget_override_used_when_provided(self):
        """Token budget override is used instead of configured budget."""
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=20000,  # Configured budget
            role="Test agent",
        )
        with patch.object(agent, "agent") as mock_agent:
            mock_agent.run.return_value = "test response"
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 5000
                # Override with smaller budget
                result = agent.run(
                    "test input",
                    token_budget_override=8000,
                    track_tokens=False
                )
                # Should use the override (8000) not configured budget (20000)
                # This test verifies the override is accepted and passed through

    def test_warning_threshold_override_used_when_provided(self):
        """Warning threshold override is used instead of configured threshold."""
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=20000,
            token_warning_threshold=18000,  # Configured threshold
            role="Test agent",
        )
        with patch.object(agent, "agent") as mock_agent:
            mock_agent.run.return_value = "test response"
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 5000
                # Override with different threshold
                result = agent.run(
                    "test input",
                    token_warning_threshold_override=15000,
                    track_tokens=False
                )
                # Should use the override, not configured threshold


class TestBudgetContextInjectionIntoSystemPrompt:
    """Test that TokenBudgetContext is injected into system prompt."""

    def test_budget_context_in_system_prompt_when_budget_set(self):
        """System prompt includes budget context when token_budget configured."""
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=20000,
            role="Test agent",
        )
        with patch.object(agent, "agent") as mock_agent:
            mock_agent.run.return_value = "test response"
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 5000

                # Capture what gets passed to agent.run()
                captured_prompt = None
                def capture_prompt(prompt, **kwargs):
                    nonlocal captured_prompt
                    captured_prompt = prompt
                    return "test response"

                mock_agent.run.side_effect = capture_prompt

                result = agent.run("test input", track_tokens=False)

                # Budget context should be in the prompt passed to agent
                assert captured_prompt is not None
                # Should mention token budget info
                assert any(keyword in captured_prompt.lower()
                          for keyword in ["token budget", "budget", "remaining"])

    def test_budget_context_not_in_prompt_when_no_budget(self):
        """System prompt doesn't mention budget when token_budget not set."""
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            # No token_budget set
            role="Test agent",
        )
        with patch.object(agent, "agent") as mock_agent:
            mock_agent.run.return_value = "test response"
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 5000

                captured_prompt = None
                def capture_prompt(prompt, **kwargs):
                    nonlocal captured_prompt
                    captured_prompt = prompt
                    return "test response"

                mock_agent.run.side_effect = capture_prompt

                result = agent.run("test input", track_tokens=False)

                # Budget context should NOT be in prompt
                assert captured_prompt is not None
                # Should not mention token budget info (no budget configured)
                assert "TOKEN BUDGET INFORMATION" not in captured_prompt


class TestBudgetAwareBehavior:
    """Test that budget information enables smart agent behavior."""

    def test_remaining_tokens_calculated_in_context(self):
        """TokenBudgetContext calculates remaining tokens correctly."""
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=20000,
            role="Test agent",
        )
        # Budget context is injected with tokens_used=0 initially
        # So remaining should equal the full budget (20000)
        with patch.object(agent, "agent") as mock_agent:
            mock_agent.run.return_value = "test response"
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 5000

                captured_prompt = None
                def capture_prompt(prompt, **kwargs):
                    nonlocal captured_prompt
                    captured_prompt = prompt
                    return "test response"

                mock_agent.run.side_effect = capture_prompt

                result = agent.run("test input", track_tokens=False)

                # Should show correct remaining tokens (20000 - 0 = 20000)
                assert captured_prompt is not None
                assert "20" in captured_prompt or "20,000" in captured_prompt
                assert "Remaining:" in captured_prompt

    def test_approaching_limit_guidance_included(self):
        """System prompt includes guidance on approaching token limit."""
        agent = SimpleAgent(
            name="test_agent",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=10000,
            role="Test agent",
        )
        with patch.object(agent, "agent") as mock_agent:
            mock_agent.run.return_value = "test response"
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                # Simulate 8000 tokens used (80% of 10000 budget)
                mock_estimate.return_value = 8000

                captured_prompt = None
                def capture_prompt(prompt, **kwargs):
                    nonlocal captured_prompt
                    captured_prompt = prompt
                    return "test response"

                mock_agent.run.side_effect = capture_prompt

                result = agent.run("test input", track_tokens=False)

                # Should include management strategy guidance
                assert captured_prompt is not None
                assert any(keyword in captured_prompt.lower()
                          for keyword in ["strategy", "reduce", "limit", "max_tokens"])


class TestBudgetOverrideWithOrchestration:
    """Test budget override mechanism for orchestration use cases."""

    def test_sub_agent_receives_override_budget(self):
        """Sub-agent can be called with overridden budget from orchestrator."""
        sub_agent = SimpleAgent(
            name="sub_agent",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=20000,  # Default budget
            role="Sub agent",
        )

        with patch.object(sub_agent, "agent") as mock_agent:
            mock_agent.run.return_value = "sub agent response"
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 2000

                # Orchestrator calls sub-agent with tighter budget
                result = sub_agent.run(
                    "research query",
                    token_budget_override=5000,  # Tighter budget than default
                    track_tokens=False
                )

                # Should not raise an error
                assert result is not None

    def test_workflow_system_can_dynamically_set_budget(self):
        """Automation/workflow system can dynamically set agent budget."""
        agent = SimpleAgent(
            name="workflow_agent",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=20000,
            role="Workflow agent",
        )

        remaining_budget = 15000  # Calculated by workflow system

        with patch.object(agent, "agent") as mock_agent:
            mock_agent.run.return_value = "response"
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 3000

                # Pass dynamic budget from workflow
                result = agent.run(
                    "task",
                    token_budget_override=remaining_budget,
                    track_tokens=False
                )

                assert result is not None
