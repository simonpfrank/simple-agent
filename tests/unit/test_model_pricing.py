"""Unit tests for model pricing calculations."""

import pytest
from decimal import Decimal

from simple_agent.tools.helpers.model_pricing import (
    ModelPricing,
    get_pricing,
    calculate_cost,
)


class TestModelPricing:
    """Test ModelPricing for cost calculations."""

    def test_openai_gpt4o_mini_pricing(self) -> None:
        """ModelPricing should have GPT-4O mini pricing."""
        pricing = ModelPricing()

        input_price, output_price = pricing.get_price("gpt-4o-mini")

        assert input_price == Decimal("0.15")
        assert output_price == Decimal("0.60")

    def test_anthropic_claude3_pricing(self) -> None:
        """ModelPricing should have Claude 3 Sonnet pricing."""
        pricing = ModelPricing()

        input_price, output_price = pricing.get_price("claude-3-5-sonnet")

        assert input_price == Decimal("3")
        assert output_price == Decimal("15")

    def test_ollama_free_pricing(self) -> None:
        """ModelPricing should have free pricing for Ollama models."""
        pricing = ModelPricing()

        input_price, output_price = pricing.get_price("llama2")

        assert input_price == Decimal("0")
        assert output_price == Decimal("0")

    def test_unknown_model_pricing(self) -> None:
        """ModelPricing should return zero for unknown models."""
        pricing = ModelPricing()

        input_price, output_price = pricing.get_price("unknown-model")

        assert input_price == Decimal("0")
        assert output_price == Decimal("0")

    def test_partial_model_match(self) -> None:
        """ModelPricing should support partial model name matching."""
        pricing = ModelPricing()

        # "gpt-4o" should match "gpt-4o-mini"
        input_price, output_price = pricing.get_price("gpt-4o-mini-2024-07-18")

        # Should find the match
        assert input_price > Decimal("0")

    def test_calculate_cost_single_model(self) -> None:
        """ModelPricing should calculate cost correctly."""
        pricing = ModelPricing()

        # 1M tokens of input, 1M tokens of output for gpt-4o-mini
        # input: 0.15 * 1M / 1M = $0.15
        # output: 0.60 * 1M / 1M = $0.60
        # total: $0.75
        cost = pricing.calculate_cost("gpt-4o-mini", 1000000, 1000000)

        assert cost == Decimal("0.75")

    def test_calculate_cost_partial_tokens(self) -> None:
        """ModelPricing should calculate cost for partial tokens."""
        pricing = ModelPricing()

        # 500 input tokens, 150 output tokens for gpt-4o-mini
        # input: 0.15 * 500 / 1M = $0.000075
        # output: 0.60 * 150 / 1M = $0.00009
        # total: $0.000165
        cost = pricing.calculate_cost("gpt-4o-mini", 500, 150)

        # Check approximately equal (due to floating point)
        expected = Decimal("500") * Decimal("0.15") / Decimal("1000000") + Decimal(
            "150"
        ) * Decimal("0.60") / Decimal("1000000")
        assert abs(cost - expected) < Decimal("0.0000001")

    def test_calculate_cost_claude3(self) -> None:
        """ModelPricing should calculate Claude 3 costs."""
        pricing = ModelPricing()

        # 1000 input, 500 output for Claude 3 Sonnet
        # input: 3 * 1000 / 1M = $0.000003
        # output: 15 * 500 / 1M = $0.0000075
        cost = pricing.calculate_cost("claude-3-5-sonnet", 1000, 500)

        expected = Decimal("1000") * Decimal("3") / Decimal(
            "1000000"
        ) + Decimal("500") * Decimal("15") / Decimal("1000000")
        assert abs(cost - expected) < Decimal("0.0000001")

    def test_set_custom_price(self) -> None:
        """ModelPricing should allow custom prices."""
        pricing = ModelPricing()

        pricing.set_custom_price("custom-model", Decimal("0.50"), Decimal("2.00"))

        input_price, output_price = pricing.get_price("custom-model")

        assert input_price == Decimal("0.50")
        assert output_price == Decimal("2.00")

    def test_custom_price_calculation(self) -> None:
        """ModelPricing should use custom prices in calculation."""
        pricing = ModelPricing()

        pricing.set_custom_price("custom-model", Decimal("1.00"), Decimal("2.00"))
        cost = pricing.calculate_cost("custom-model", 1000, 500)

        # input: 1.00 * 1000 / 1M = $0.001
        # output: 2.00 * 500 / 1M = $0.001
        # total: $0.002
        expected = Decimal("0.002")
        assert abs(cost - expected) < Decimal("0.0000001")

    def test_list_models(self) -> None:
        """ModelPricing should list all available models."""
        pricing = ModelPricing()

        models = pricing.list_models()

        # Should have at least some models
        assert len(models) > 0

        # Should have known models
        assert "gpt-4o-mini" in models
        assert "claude-3-5-sonnet" in models
        assert "llama2" in models

    def test_global_pricing_instance(self) -> None:
        """get_pricing() should return global instance."""
        pricing1 = get_pricing()
        pricing2 = get_pricing()

        assert pricing1 is pricing2

    def test_calculate_cost_global(self) -> None:
        """calculate_cost() should use global pricing."""
        cost = calculate_cost("gpt-4o-mini", 500, 150)

        # Should be able to calculate
        assert cost > Decimal("0")

    def test_cost_precision(self) -> None:
        """Cost calculation should maintain Decimal precision."""
        pricing = ModelPricing()

        cost = pricing.calculate_cost("gpt-4o-mini", 12345, 6789)

        # Result should be Decimal type
        assert isinstance(cost, Decimal)

        # Should have high precision
        cost_str = str(cost)
        assert cost_str.count(".") == 1  # Has decimal point
