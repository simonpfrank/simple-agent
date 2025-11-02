"""Model pricing database for cost calculation."""

import json
import logging
import os
from decimal import Decimal
from pathlib import Path
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class PricingConfigError(ValueError):
    """Raised when pricing configuration is invalid."""

    pass


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

    def load_from_file(self, filepath: str) -> None:
        """
        Load pricing configuration from JSON file.

        File format:
        {
            "provider": {
                "model_name": {"input": "price", "output": "price"},
                ...
            },
            ...
        }

        Args:
            filepath: Path to JSON pricing file

        Raises:
            PricingConfigError: If file doesn't exist, is invalid JSON, or has wrong structure
        """
        config_path = Path(filepath)

        if not config_path.exists():
            raise PricingConfigError(f"Pricing file not found: {filepath}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise PricingConfigError(f"Invalid JSON in pricing file: {e}") from e

        if not isinstance(config, dict):
            raise PricingConfigError("Pricing config must be a dictionary")

        # Process each provider section
        for provider, models in config.items():
            if not isinstance(models, dict):
                raise PricingConfigError(
                    f"Provider '{provider}' must contain a dictionary of models"
                )

            for model_name, prices in models.items():
                if not isinstance(prices, dict):
                    raise PricingConfigError(
                        f"Model '{model_name}' pricing must be a dictionary with 'input' and 'output'"
                    )

                if "input" not in prices or "output" not in prices:
                    raise PricingConfigError(
                        f"Model '{model_name}' must have 'input' and 'output' prices"
                    )

                try:
                    input_price = Decimal(str(prices["input"]))
                    output_price = Decimal(str(prices["output"]))
                except (ValueError, TypeError, Exception) as e:
                    raise PricingConfigError(
                        f"Model '{model_name}' prices must be numeric: {e}"
                    ) from e

                self.prices[model_name] = (input_price, output_price)

        logger.info(f"Loaded pricing configuration from: {filepath}")

    def load_from_env(self) -> None:
        """
        Load pricing configuration from file specified by environment variable.

        Looks for 'PRICING_CONFIG_FILE' environment variable.
        If not found or file doesn't exist, silently uses defaults.
        """
        config_file = os.environ.get("PRICING_CONFIG_FILE")

        if config_file:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    self.load_from_file(config_file)
                except PricingConfigError as e:
                    logger.warning(f"Failed to load pricing from env var: {e}")
            else:
                logger.warning(
                    f"Pricing file from PRICING_CONFIG_FILE not found: {config_file}"
                )

    def save_to_file(self, filepath: str) -> None:
        """
        Save current pricing to JSON file.

        Args:
            filepath: Path where to save the pricing file
        """
        config_path = Path(filepath)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Group prices by provider (best guess from model names)
        config: Dict[str, Dict[str, Dict[str, str]]] = {}

        for model_name, (input_price, output_price) in self.prices.items():
            # Guess provider from model name
            provider = "custom"
            if model_name.startswith("gpt-"):
                provider = "openai"
            elif model_name.startswith("claude-"):
                provider = "anthropic"
            elif model_name in self.OLLAMA_PRICES:
                provider = "ollama"

            if provider not in config:
                config[provider] = {}

            config[provider][model_name] = {
                "input": str(input_price),
                "output": str(output_price),
            }

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved pricing configuration to: {filepath}")
        except Exception as e:
            logger.exception(f"Failed to save pricing to {filepath}: {e}")
            raise

    def to_dict(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        Export current pricing as a dictionary.

        Returns:
            Dictionary with structure: {provider: {model: {input, output}}}
        """
        result: Dict[str, Dict[str, Dict[str, str]]] = {}

        for model_name, (input_price, output_price) in self.prices.items():
            # Guess provider from model name
            provider = "custom"
            if model_name.startswith("gpt-"):
                provider = "openai"
            elif model_name.startswith("claude-"):
                provider = "anthropic"
            elif model_name in self.OLLAMA_PRICES:
                provider = "ollama"

            if provider not in result:
                result[provider] = {}

            result[provider][model_name] = {
                "input": str(input_price),
                "output": str(output_price),
            }

        return result

    def get_config_file_location(self) -> Optional[str]:
        """
        Get the expected location of pricing config file.

        Returns:
            Path from PRICING_CONFIG_FILE env var, or None if not set
        """
        return os.environ.get("PRICING_CONFIG_FILE")

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
