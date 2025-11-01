"""Unit tests for TokenBudgetContext dataclass."""

import pytest

from simple_agent.core.token_budget_context import TokenBudgetContext


class TestTokenBudgetContextCreation:
    """Test TokenBudgetContext initialization and calculation."""

    def test_create_context_with_all_fields(self):
        """TokenBudgetContext created with all required fields."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=500,
            warning_threshold=18000,
        )
        assert context.token_budget == 20000
        assert context.tokens_used == 500
        assert context.warning_threshold == 18000

    def test_tokens_remaining_calculated(self):
        """tokens_remaining calculated as budget - used."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=500,
        )
        assert context.tokens_remaining == 19500

    def test_percent_used_calculated(self):
        """percent_used calculated as (used / budget) * 100."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=5000,
        )
        assert context.percent_used == 25.0

    def test_percent_used_zero_budget_safe(self):
        """percent_used is 0.0 if budget is 0 (edge case)."""
        context = TokenBudgetContext(
            token_budget=0,
            tokens_used=0,
        )
        assert context.percent_used == 0.0

    def test_approaching_limit_true_at_80_percent(self):
        """approaching_limit is True when usage >= 80%."""
        context = TokenBudgetContext(
            token_budget=10000,
            tokens_used=8000,  # 80%
        )
        assert context.approaching_limit is True

    def test_approaching_limit_false_below_80_percent(self):
        """approaching_limit is False when usage < 80%."""
        context = TokenBudgetContext(
            token_budget=10000,
            tokens_used=7999,  # 79.99%
        )
        assert context.approaching_limit is False

    def test_approaching_limit_true_above_80_percent(self):
        """approaching_limit is True when usage > 80%."""
        context = TokenBudgetContext(
            token_budget=10000,
            tokens_used=9000,  # 90%
        )
        assert context.approaching_limit is True


class TestTokenBudgetContextWarningThreshold:
    """Test warning threshold behavior."""

    def test_warning_threshold_optional(self):
        """warning_threshold is optional (None by default)."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=500,
        )
        assert context.warning_threshold is None

    def test_warning_threshold_set(self):
        """warning_threshold can be explicitly set."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=500,
            warning_threshold=18000,
        )
        assert context.warning_threshold == 18000

    def test_approaching_warning_threshold_true(self):
        """approaching_warning_threshold is True when used >= threshold."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=18000,
            warning_threshold=18000,
        )
        assert context.approaching_warning_threshold is True

    def test_approaching_warning_threshold_false(self):
        """approaching_warning_threshold is False when used < threshold."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=17999,
            warning_threshold=18000,
        )
        assert context.approaching_warning_threshold is False

    def test_approaching_warning_threshold_none_when_no_threshold(self):
        """approaching_warning_threshold is None when threshold not set."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=500,
        )
        assert context.approaching_warning_threshold is None


class TestTokenBudgetContextBudgetStatus:
    """Test budget status descriptions."""

    def test_budget_status_low_usage(self):
        """status describes low usage when < 50%."""
        context = TokenBudgetContext(
            token_budget=10000,
            tokens_used=2000,  # 20%
        )
        assert "20.0%" in context.budget_status

    def test_budget_status_moderate_usage(self):
        """status describes moderate usage when 50-80%."""
        context = TokenBudgetContext(
            token_budget=10000,
            tokens_used=6000,  # 60%
        )
        assert "60.0%" in context.budget_status

    def test_budget_status_high_usage(self):
        """status describes high usage when > 80%."""
        context = TokenBudgetContext(
            token_budget=10000,
            tokens_used=9000,  # 90%
        )
        assert "90.0%" in context.budget_status

    def test_budget_status_includes_remaining(self):
        """status includes remaining token count."""
        context = TokenBudgetContext(
            token_budget=10000,
            tokens_used=3000,
        )
        assert "7000" in context.budget_status

    def test_budget_status_includes_total(self):
        """status includes total budget."""
        context = TokenBudgetContext(
            token_budget=10000,
            tokens_used=3000,
        )
        assert "10000" in context.budget_status


class TestTokenBudgetContextSystemPromptInjection:
    """Test generation of budget info for system prompt."""

    def test_to_prompt_string_includes_budget(self):
        """to_prompt_string() returns formatted string for system prompt."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=500,
            warning_threshold=18000,
        )
        prompt_str = context.to_prompt_string()
        assert "20,000" in prompt_str  # Formatted with comma
        assert "500" in prompt_str
        assert "19,500" in prompt_str  # Formatted with comma

    def test_to_prompt_string_includes_warning_threshold(self):
        """to_prompt_string() mentions warning threshold if set."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=500,
            warning_threshold=18000,
        )
        prompt_str = context.to_prompt_string()
        assert "18,000" in prompt_str  # Formatted with comma

    def test_to_prompt_string_readable_format(self):
        """to_prompt_string() returns human-readable format for agent."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=500,
        )
        prompt_str = context.to_prompt_string()
        # Should be readable English, not just numbers
        assert isinstance(prompt_str, str)
        assert len(prompt_str) > 50  # Not too short

    def test_to_prompt_string_includes_budget_management_strategy(self):
        """to_prompt_string() includes budget management guidance."""
        context = TokenBudgetContext(
            token_budget=20000,
            tokens_used=500,
        )
        prompt_str = context.to_prompt_string()
        # Should include guidance about when to limit/optimize
        assert ("50%" in prompt_str or "threshold" in prompt_str or
                "reduce" in prompt_str.lower() or
                "optimize" in prompt_str.lower())
