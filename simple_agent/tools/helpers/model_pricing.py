"""Model pricing database for cost calculation."""

from decimal import Decimal
from typing import Dict, Tuple, Optional


class ModelPricing:
    """Pricing information for different LLM models.

    Prices are per 1M tokens (standard pricing format for LLMs).
    """

    # OpenAI pricing (as of 2024)
    OPENAI_PRICES: Dict[str, Tuple[Decimal, Decimal]] = {
        "gpt-4o": (Decimal("5"), Decimal("15")),  # input, output
        "gpt-4o-mini": (Decimal("0.15"), Decimal("0.60")),
        "gpt-4-turbo": (Decimal("10"), Decimal("30")),
        "gpt-4": (Decimal("30"), Decimal("60")),
        "gpt-3.5-turbo": (Decimal("0.50"), Decimal("1.50")),
    }

    # Anthropic pricing
    ANTHROPIC_PRICES: Dict[str, Tuple[Decimal, Decimal]] = {
        "claude-3-5-sonnet": (Decimal("3"), Decimal("15")),
        "claude-3-opus": (Decimal("15"), Decimal("75")),
        "claude-3-sonnet": (Decimal("3"), Decimal("15")),
        "claude-3-haiku": (Decimal("0.25"), Decimal("1.25")),
    }

    # Local models (typically free or self-hosted)
    OLLAMA_PRICES: Dict[str, Tuple[Decimal, Decimal]] = {
        # Most local models are free if self-hosted
        "llama2": (Decimal("0"), Decimal("0")),
        "mistral": (Decimal("0"), Decimal("0")),
        "neural-chat": (Decimal("0"), Decimal("0")),
    }

    def __init__(self) -> None:
        """Initialize pricing database."""
        self.prices: Dict[str, Tuple[Decimal, Decimal]] = {}
        self._load_default_prices()

    def _load_default_prices(self) -> None:
        """Load all default pricing."""
        self.prices.update(self.OPENAI_PRICES)
        self.prices.update(self.ANTHROPIC_PRICES)
        self.prices.update(self.OLLAMA_PRICES)

    def get_price(self, model: str) -> Tuple[Decimal, Decimal]:
        """Get pricing for a model.

        Args:
            model: Model name (e.g., "gpt-4o-mini", "claude-3-opus")

        Returns:
            Tuple of (input_price, output_price) per 1M tokens
            Returns (0, 0) if model not found (unknown cost)
        """
        # Try exact match first
        if model in self.prices:
            return self.prices[model]

        # Try partial match (e.g., "gpt-4o" matches "gpt-4o-mini")
        for key, price in self.prices.items():
            if key in model or model in key:
                return price

        # Unknown model - return zeros
        return Decimal("0"), Decimal("0")

    def calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> Decimal:
        """Calculate cost for an execution.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        input_price, output_price = self.get_price(model)

        # Prices are per 1M tokens, so divide by 1M
        input_cost = Decimal(input_tokens) * input_price / Decimal("1000000")
        output_cost = Decimal(output_tokens) * output_price / Decimal("1000000")

        return input_cost + output_cost

    def set_custom_price(
        self, model: str, input_price: Decimal, output_price: Decimal
    ) -> None:
        """Set custom pricing for a model.

        Args:
            model: Model name
            input_price: Input price per 1M tokens
            output_price: Output price per 1M tokens
        """
        self.prices[model] = (input_price, output_price)

    def list_models(self) -> Dict[str, Tuple[Decimal, Decimal]]:
        """List all models and their pricing.

        Returns:
            Dict mapping model names to (input_price, output_price)
        """
        return dict(self.prices)


# Global instance for convenience
_pricing = ModelPricing()


def get_pricing() -> ModelPricing:
    """Get the global pricing instance."""
    return _pricing


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> Decimal:
    """Calculate cost using global pricing instance.

    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD
    """
    return _pricing.calculate_cost(model, input_tokens, output_tokens)
