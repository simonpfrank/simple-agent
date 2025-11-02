"""Unit tests for configurable model pricing (Issue 8-A)."""

import json
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from simple_agent.tools.helpers.model_pricing import ModelPricing, PricingConfigError


class TestModelPricingConfiguration:
    """Test externalizable model pricing configuration."""

    def test_load_pricing_from_json_file(self, tmp_path: Path):
        """Test loading pricing from JSON file."""
        pricing_file = tmp_path / "pricing.json"
        pricing_data = {
            "openai": {
                "gpt-4o": {"input": "5", "output": "15"},
                "gpt-4o-mini": {"input": "0.15", "output": "0.60"},
            }
        }
        pricing_file.write_text(json.dumps(pricing_data))

        pricing = ModelPricing()
        pricing.load_from_file(str(pricing_file))

        # Verify pricing was loaded
        assert pricing.get_price("gpt-4o") == (Decimal("5"), Decimal("15"))
        assert pricing.get_price("gpt-4o-mini") == (Decimal("0.15"), Decimal("0.60"))

    def test_load_pricing_merges_with_defaults(self, tmp_path: Path):
        """Test loading pricing merges with defaults instead of replacing."""
        pricing_file = tmp_path / "pricing.json"
        pricing_data = {
            "custom": {
                "my-model": {"input": "1", "output": "2"},
            }
        }
        pricing_file.write_text(json.dumps(pricing_data))

        pricing = ModelPricing()
        pricing.load_from_file(str(pricing_file))

        # Verify custom pricing is available
        assert pricing.get_price("my-model") == (Decimal("1"), Decimal("2"))

        # Verify defaults are still available
        assert pricing.get_price("gpt-4o") == (Decimal("5"), Decimal("15"))
        assert pricing.get_price("claude-3-5-sonnet") == (Decimal("3"), Decimal("15"))

    def test_load_pricing_nonexistent_file_raises_error(self):
        """Test loading from non-existent file raises error."""
        pricing = ModelPricing()

        with pytest.raises(PricingConfigError, match="not found"):
            pricing.load_from_file("/nonexistent/pricing.json")

    def test_load_pricing_invalid_json_raises_error(self, tmp_path: Path):
        """Test loading invalid JSON raises error."""
        pricing_file = tmp_path / "pricing.json"
        pricing_file.write_text("invalid json {")

        pricing = ModelPricing()

        with pytest.raises(PricingConfigError, match="JSON"):
            pricing.load_from_file(str(pricing_file))

    def test_load_pricing_invalid_structure_raises_error(self, tmp_path: Path):
        """Test loading JSON with invalid structure raises error."""
        pricing_file = tmp_path / "pricing.json"
        # Invalid: prices should have input/output keys
        pricing_data = {
            "openai": {
                "gpt-4o": "not_a_dict"
            }
        }
        pricing_file.write_text(json.dumps(pricing_data))

        pricing = ModelPricing()

        with pytest.raises(PricingConfigError, match="dictionary"):
            pricing.load_from_file(str(pricing_file))

    def test_load_pricing_missing_input_price_raises_error(self, tmp_path: Path):
        """Test loading JSON with missing input price raises error."""
        pricing_file = tmp_path / "pricing.json"
        pricing_data = {
            "openai": {
                "gpt-4o": {"output": "15"}  # Missing input
            }
        }
        pricing_file.write_text(json.dumps(pricing_data))

        pricing = ModelPricing()

        with pytest.raises(PricingConfigError, match="input.*output"):
            pricing.load_from_file(str(pricing_file))

    def test_load_pricing_missing_output_price_raises_error(self, tmp_path: Path):
        """Test loading JSON with missing output price raises error."""
        pricing_file = tmp_path / "pricing.json"
        pricing_data = {
            "openai": {
                "gpt-4o": {"input": "5"}  # Missing output
            }
        }
        pricing_file.write_text(json.dumps(pricing_data))

        pricing = ModelPricing()

        with pytest.raises(PricingConfigError, match="input.*output"):
            pricing.load_from_file(str(pricing_file))

    def test_load_pricing_non_numeric_price_raises_error(self, tmp_path: Path):
        """Test loading JSON with non-numeric prices raises error."""
        pricing_file = tmp_path / "pricing.json"
        pricing_data = {
            "openai": {
                "gpt-4o": {"input": "invalid", "output": "15"}
            }
        }
        pricing_file.write_text(json.dumps(pricing_data))

        pricing = ModelPricing()

        with pytest.raises(PricingConfigError, match="numeric"):
            pricing.load_from_file(str(pricing_file))

    def test_save_pricing_to_json_file(self, tmp_path: Path):
        """Test saving pricing to JSON file."""
        pricing_file = tmp_path / "pricing.json"

        pricing = ModelPricing()
        pricing.set_custom_price("my-custom", Decimal("2"), Decimal("4"))
        pricing.save_to_file(str(pricing_file))

        # Verify file was created
        assert pricing_file.exists()

        # Verify content can be loaded
        with open(pricing_file, "r") as f:
            data = json.load(f)

        # Should have at least the custom price
        assert "custom" in data or any("my-custom" in section for section in data.values())

    def test_export_pricing_as_dict(self):
        """Test exporting pricing as dictionary."""
        pricing = ModelPricing()
        pricing.set_custom_price("my-model", Decimal("1"), Decimal("2"))

        pricing_dict = pricing.to_dict()

        assert isinstance(pricing_dict, dict)
        # Should have some default provider sections
        assert any(provider in pricing_dict for provider in ["openai", "anthropic", "ollama"])

    def test_pricing_file_format(self, tmp_path: Path):
        """Test expected pricing file format."""
        pricing_file = tmp_path / "pricing.json"
        pricing_data = {
            "openai": {
                "gpt-4o": {"input": "5", "output": "15"},
                "gpt-4-turbo": {"input": "10", "output": "30"},
            },
            "anthropic": {
                "claude-3-opus": {"input": "15", "output": "75"},
            },
        }
        pricing_file.write_text(json.dumps(pricing_data, indent=2))

        pricing = ModelPricing()
        pricing.load_from_file(str(pricing_file))

        # All models should be accessible
        assert pricing.get_price("gpt-4o") == (Decimal("5"), Decimal("15"))
        assert pricing.get_price("gpt-4-turbo") == (Decimal("10"), Decimal("30"))
        assert pricing.get_price("claude-3-opus") == (Decimal("15"), Decimal("75"))

    def test_update_existing_price_when_loading(self, tmp_path: Path):
        """Test that loading pricing can override existing prices."""
        pricing_file = tmp_path / "pricing.json"
        # Override default gpt-4o pricing
        pricing_data = {
            "openai": {
                "gpt-4o": {"input": "100", "output": "200"},
            }
        }
        pricing_file.write_text(json.dumps(pricing_data))

        pricing = ModelPricing()
        pricing.load_from_file(str(pricing_file))

        # New pricing should override default
        assert pricing.get_price("gpt-4o") == (Decimal("100"), Decimal("200"))


class TestModelPricingConfigEnvironment:
    """Test environment-based configuration."""

    def test_load_pricing_from_env_variable(self, tmp_path: Path, monkeypatch):
        """Test loading pricing file specified by environment variable."""
        pricing_file = tmp_path / "pricing.json"
        pricing_data = {
            "custom": {
                "local-llm": {"input": "0", "output": "0"},
            }
        }
        pricing_file.write_text(json.dumps(pricing_data))

        monkeypatch.setenv("PRICING_CONFIG_FILE", str(pricing_file))

        pricing = ModelPricing()
        pricing.load_from_env()

        assert pricing.get_price("local-llm") == (Decimal("0"), Decimal("0"))

    def test_load_pricing_missing_env_variable_no_error(self, monkeypatch):
        """Test missing env variable doesn't raise error."""
        monkeypatch.delenv("PRICING_CONFIG_FILE", raising=False)

        pricing = ModelPricing()
        # Should not raise, just use defaults
        pricing.load_from_env()

        assert pricing.get_price("gpt-4o") == (Decimal("5"), Decimal("15"))

    def test_get_pricing_config_file_location(self, tmp_path: Path):
        """Test getting the path to pricing config file."""
        # Default location should exist or be discoverable
        pricing = ModelPricing()
        config_file = pricing.get_config_file_location()

        # Should return a Path-like object
        assert config_file is None or isinstance(config_file, (str, Path))


class TestPricingConfigError:
    """Test PricingConfigError exception."""

    def test_pricing_config_error_is_exception(self):
        """Test PricingConfigError is an Exception."""
        assert issubclass(PricingConfigError, Exception)

    def test_pricing_config_error_with_message(self):
        """Test PricingConfigError can be raised with message."""
        with pytest.raises(PricingConfigError, match="test message"):
            raise PricingConfigError("test message")
