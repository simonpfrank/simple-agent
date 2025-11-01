"""Token budget context for agents to be aware of budget constraints during execution."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TokenBudgetContext:
    """Represents token budget information for an agent execution.

    Agents receive this context in their system prompt to understand:
    - Total budget available
    - Tokens used so far
    - Remaining budget
    - Whether approaching limits
    - Budget management strategy guidance
    """

    token_budget: int
    tokens_used: int
    warning_threshold: Optional[int] = None

    @property
    def tokens_remaining(self) -> int:
        """Tokens remaining in budget (budget - used)."""
        return self.token_budget - self.tokens_used

    @property
    def percent_used(self) -> float:
        """Percentage of budget used (used / budget * 100).

        Returns 0.0 if budget is 0 to avoid division by zero.
        """
        if self.token_budget == 0:
            return 0.0
        return (self.tokens_used / self.token_budget) * 100.0

    @property
    def approaching_limit(self) -> bool:
        """True when usage is >= 80% of budget."""
        return self.percent_used >= 80.0

    @property
    def approaching_warning_threshold(self) -> Optional[bool]:
        """True when tokens_used >= warning_threshold, None if threshold not set."""
        if self.warning_threshold is None:
            return None
        return self.tokens_used >= self.warning_threshold

    @property
    def budget_status(self) -> str:
        """Human-readable status of budget usage.

        Returns a string describing:
        - Percent used
        - Remaining tokens
        - Total budget
        """
        return (
            f"Token usage: {self.tokens_used}/{self.token_budget} "
            f"({self.percent_used:.1f}% used, {self.tokens_remaining} remaining)"
        )

    def to_prompt_string(self) -> str:
        """Generate formatted string for injection into system prompt.

        Returns human-readable budget information that agents can use
        to make intelligent decisions about token usage.
        """
        lines = [
            "TOKEN BUDGET INFORMATION:",
            f"- Total budget: {self.token_budget:,} tokens",
            f"- Tokens used so far: {self.tokens_used:,} ({self.percent_used:.1f}%)",
            f"- Remaining: {self.tokens_remaining:,} tokens",
        ]

        if self.warning_threshold is not None:
            lines.append(f"- Warning threshold: {self.warning_threshold:,} tokens")

        lines.append("")
        lines.append("BUDGET MANAGEMENT STRATEGY:")
        lines.append("- If remaining > 50%: Use full detailed searches/fetches")
        lines.append("- If remaining 20-50%: Limit fetch results (max_tokens=2000)")
        lines.append("- If remaining 5-20%: Use max_tokens=1000, skip secondary analysis")
        lines.append("- If remaining < 5%: Minimal additional fetches (max_tokens=500)")
        lines.append("- If remaining < 1%: Use existing context, refuse new searches")

        return "\n".join(lines)
