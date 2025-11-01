"""Integration tests for Phase 3.3 - Token Budget Awareness."""

import pytest
from unittest.mock import patch

from simple_agent.agents.simple_agent import SimpleAgent
from simple_agent.core.token_budget_context import TokenBudgetContext


class TestBudgetAwareAgentExecution:
    """Test agent execution with budget awareness."""

    def test_agent_with_budget_includes_budget_info_in_execution(self):
        """Agent with budget includes budget information in prompt sent to LLM."""
        agent = SimpleAgent(
            name="researcher",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=5000,
            role="You are a helpful assistant.",
        )

        # Mock the LLM to capture what prompt is actually sent
        with patch.object(agent.agent, "run") as mock_run:
            mock_run.return_value = "Research complete"
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 1000

                result = agent.run("Research quantum computing", track_tokens=False)

                # Verify agent.run() was called with budget info in prompt
                assert mock_run.called
                prompt_arg = mock_run.call_args[0][0]
                # Budget context should be in the prompt
                assert "TOKEN BUDGET INFORMATION" in prompt_arg
                assert "5000" in prompt_arg or "5,000" in prompt_arg

    def test_agent_without_budget_does_not_include_budget_info(self):
        """Agent without budget configured doesn't include budget information."""
        agent = SimpleAgent(
            name="helper",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            # No token_budget
            role="You are a helpful assistant.",
        )

        with patch.object(agent.agent, "run") as mock_run:
            mock_run.return_value = "Help provided"
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 500

                result = agent.run("Help me with something", track_tokens=False)

                assert mock_run.called
                prompt_arg = mock_run.call_args[0][0]
                # Budget context should NOT be in prompt
                assert "TOKEN BUDGET INFORMATION" not in prompt_arg

    def test_budget_override_changes_budget_shown_to_agent(self):
        """Budget override parameter changes the budget shown in prompt."""
        agent = SimpleAgent(
            name="researcher",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=10000,  # Default budget
            role="You are a helpful assistant.",
        )

        with patch.object(agent.agent, "run") as mock_run:
            mock_run.return_value = "Response"
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 1000

                # Call with override
                result = agent.run(
                    "Query",
                    token_budget_override=3000,
                    track_tokens=False
                )

                assert mock_run.called
                prompt_arg = mock_run.call_args[0][0]
                # Should show override budget (3000), not default (10000)
                assert "3000" in prompt_arg or "3,000" in prompt_arg
                assert "3" in prompt_arg  # Contains the override value

    def test_token_budget_hard_limit_still_enforced(self):
        """Token budget hard limit is still enforced with budget awareness."""
        agent = SimpleAgent(
            name="researcher",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=1000,  # Very small budget
            role="You are helpful",
        )

        with patch.object(agent.agent, "run"):
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                # Simulate huge prompt that exceeds budget
                mock_estimate.return_value = 5000

                # Should raise ValueError for exceeding budget
                # Must use track_tokens=True to trigger token estimation and budget check
                with pytest.raises(ValueError) as exc_info:
                    agent.run("Large query", track_tokens=True)

                assert "budget exceeded" in str(exc_info.value).lower()
                assert "5000" in str(exc_info.value)

    def test_multi_agent_orchestration_with_budget_tracking(self):
        """Orchestration can track and manage budgets across multiple agents."""
        # Simulate orchestration: main agent calls sub-agents with remaining budget

        orchestrator = SimpleAgent(
            name="orchestrator",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=10000,  # Total budget for all steps
            role="Coordinate research",
        )

        researcher = SimpleAgent(
            name="researcher",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=10000,  # Can be overridden
            role="Researcher role",
        )

        analyzer = SimpleAgent(
            name="analyzer",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=10000,  # Can be overridden
            role="Analyzer role",
        )

        with patch.object(orchestrator.agent, "run") as mock_orch:
            with patch.object(researcher.agent, "run") as mock_research:
                with patch.object(analyzer.agent, "run") as mock_analyze:
                    mock_orch.return_value = "coordination done"
                    mock_research.return_value = "research done"
                    mock_analyze.return_value = "analysis done"

                    with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                        mock_estimate.return_value = 2000

                        # Step 1: Research with 6000 budget (orchestrator gives it 6000 of 10000)
                        result1 = researcher.run(
                            "Research topic",
                            token_budget_override=6000,
                            track_tokens=False
                        )

                        # Step 2: Analysis with remaining 4000 budget
                        result2 = analyzer.run(
                            "Analyze findings",
                            token_budget_override=4000,  # Reduced budget for next step
                            track_tokens=False
                        )

                        # Both should succeed and use their override budgets
                        assert mock_research.called
                        assert mock_analyze.called

                        # Check that overrides were used
                        research_prompt = mock_research.call_args[0][0]
                        assert "6000" in research_prompt or "6,000" in research_prompt

                        analyze_prompt = mock_analyze.call_args[0][0]
                        assert "4000" in analyze_prompt or "4,000" in analyze_prompt


class TestBudgetContextGeneration:
    """Test TokenBudgetContext generation and formatting."""

    def test_budget_context_shows_management_guidance(self):
        """Budget context includes guidance on budget management strategies."""
        context = TokenBudgetContext(
            token_budget=10000,
            tokens_used=2000,
        )

        prompt_str = context.to_prompt_string()

        # Should include strategy guidance
        assert "STRATEGY" in prompt_str
        assert "50%" in prompt_str  # Threshold
        assert "max_tokens" in prompt_str  # Guidance on tool parameters

    def test_budget_context_with_warning_threshold(self):
        """Budget context includes warning threshold when set."""
        context = TokenBudgetContext(
            token_budget=10000,
            tokens_used=8000,
            warning_threshold=9000,
        )

        prompt_str = context.to_prompt_string()

        # Should mention warning threshold
        assert "9000" in prompt_str or "9,000" in prompt_str
        assert "Warning threshold" in prompt_str


class TestBudgetAwareErrorHandling:
    """Test error handling with budget-aware execution."""

    def test_llm_error_still_captured_with_budget(self):
        """LLM execution errors are still captured when budget is set."""
        agent = SimpleAgent(
            name="researcher",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=5000,
            role="You are helpful",
        )

        with patch.object(agent.agent, "run") as mock_run:
            # Simulate LLM error
            mock_run.side_effect = RuntimeError("API connection failed")

            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 1000

                # Should return error in result, not raise
                result = agent.run("Query", track_tokens=False)

                assert result is not None
                assert result.error is not None
                assert "connection failed" in result.error.lower()

    def test_budget_exceeded_error_raised_not_captured(self):
        """Budget exceeded error is raised, not captured in result."""
        agent = SimpleAgent(
            name="researcher",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=1000,
            role="You are helpful",
        )

        with patch.object(agent.agent, "run"):
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                # Simulate exceeding budget
                mock_estimate.return_value = 5000

                # Should raise ValueError (hard limit)
                # Must use track_tokens=True to trigger token estimation and budget check
                with pytest.raises(ValueError) as exc_info:
                    agent.run("Query", track_tokens=True)

                assert "budget exceeded" in str(exc_info.value).lower()

    def test_budget_override_to_zero_raises_error(self):
        """Setting budget to very small value via override enforces the limit."""
        agent = SimpleAgent(
            name="researcher",
            model_provider="openai",
            model_config={"model": "gpt-4o-mini"},
            token_budget=10000,
            role="You are helpful",
        )

        with patch.object(agent.agent, "run"):
            with patch("simple_agent.agents.simple_agent.estimate_tokens") as mock_estimate:
                mock_estimate.return_value = 1000

                # Override budget to very small value
                # Must use track_tokens=True to trigger token estimation and budget check
                with pytest.raises(ValueError) as exc_info:
                    agent.run(
                        "Query",
                        token_budget_override=100,  # Tiny budget
                        track_tokens=True
                    )

                assert "budget exceeded" in str(exc_info.value).lower()
