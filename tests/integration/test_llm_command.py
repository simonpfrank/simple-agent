"""
Integration tests for /llm command.

Tests the direct LLM command that bypasses agent wrapper.
"""

import click
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch

from simple_agent.commands.llm import llm_command


# Create a minimal CLI group for testing
@click.group()
@click.pass_context
def cli(ctx):
    """Test CLI group."""
    ctx.ensure_object(dict)


cli.add_command(llm_command, name="llm")


@pytest.fixture
def mock_config():
    """Mock configuration with llm providers."""
    return {
        "llm": {
            "openai": {
                "model": "gpt-4o-mini",
                "api_key": "test-api-key",
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            "azure_openai": {
                "model": "gpt-4o-mini",
                "azure_endpoint": "https://test.openai.azure.com/",
                "api_version": "2024-02-01",
                "auth_type": "api_key",
                "api_key": "test-azure-key",
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            "ollama": {
                "model": "llama3.2:1b",
                "base_url": "http://localhost:11434",
                "temperature": 0.7,
                "max_tokens": 2000,
            },
        }
    }


@pytest.fixture
def runner():
    """Click test runner."""
    return CliRunner()


def test_llm_command_with_openai_provider(runner, mock_config):
    """Test /llm command with OpenAI provider."""
    with patch("simple_agent.commands.llm.ConfigManager.get") as mock_get, \
         patch("simple_agent.commands.llm.LiteLLMModel") as mock_model_class:
        
        # Mock config retrieval
        def get_side_effect(config, path, default=None):
            if path == "llm.openai":
                return mock_config["llm"]["openai"]
            return default
        
        mock_get.side_effect = get_side_effect
        
        # Mock LiteLLM model - return Mock with content attribute
        mock_model_instance = Mock()
        mock_response = Mock()
        mock_response.content = "The answer is 4"
        mock_model_instance.return_value = mock_response
        mock_model_class.return_value = mock_model_instance
        
        # Run command
        result = runner.invoke(
            cli,
            ["llm", "openai", "What", "is", "2+2?"],
            obj={"config": mock_config, "console": Mock()}
        )
        
        # Verify success
        assert result.exit_code == 0
        assert "The answer is 4" in result.output
        
        # Verify model was called with correct prompt in messages format
        mock_model_instance.assert_called_once_with([{"role": "user", "content": "What is 2+2?"}])
        
        # Verify model was created with correct config
        mock_model_class.assert_called_once()
        call_kwargs = mock_model_class.call_args.kwargs
        assert call_kwargs["model_id"] == "gpt-4o-mini"
        assert call_kwargs["api_key"] == "test-api-key"
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 2000


def test_llm_command_with_azure_provider(runner, mock_config):
    """Test /llm command with Azure OpenAI provider using API key."""
    with patch("simple_agent.commands.llm.ConfigManager.get") as mock_get, \
         patch("simple_agent.commands.llm.LiteLLMModel") as mock_model_class, \
         patch("simple_agent.commands.llm.ConfigManager.resolve_env_var") as mock_resolve:
        
        # Mock config retrieval
        def get_side_effect(config, path, default=None):
            if path == "llm.azure_openai":
                return mock_config["llm"]["azure_openai"]
            return default
        
        mock_get.side_effect = get_side_effect
        mock_resolve.side_effect = lambda x: x  # Return value as-is
        
        # Mock LiteLLM model
        mock_model_instance = Mock()
        mock_response = Mock(); mock_response.content = "Azure response"; mock_model_instance.return_value = mock_response
        mock_model_class.return_value = mock_model_instance
        
        # Run command
        result = runner.invoke(
            cli,
            ["llm", "azure_openai", "Test", "prompt"],
            obj={"config": mock_config, "console": Mock()}
        )
        
        # Verify success
        assert result.exit_code == 0
        assert "Azure response" in result.output
        
        # Verify model was created with Azure config
        mock_model_class.assert_called_once()
        call_kwargs = mock_model_class.call_args.kwargs
        assert call_kwargs["model_id"] == "azure/gpt-4o-mini"
        assert call_kwargs["api_base"] == "https://test.openai.azure.com/"
        assert call_kwargs["api_version"] == "2024-02-01"
        assert call_kwargs["api_key"] == "test-azure-key"


def test_llm_command_with_ollama_provider(runner, mock_config):
    """Test /llm command with Ollama (local) provider."""
    with patch("simple_agent.commands.llm.ConfigManager.get") as mock_get, \
         patch("simple_agent.commands.llm.LiteLLMModel") as mock_model_class, \
         patch("simple_agent.commands.llm.ConfigManager.resolve_env_var") as mock_resolve:
        
        # Mock config retrieval
        def get_side_effect(config, path, default=None):
            if path == "llm.ollama":
                return mock_config["llm"]["ollama"]
            return default
        
        mock_get.side_effect = get_side_effect
        mock_resolve.side_effect = lambda x: x
        
        # Mock LiteLLM model
        mock_model_instance = Mock()
        mock_response = Mock(); mock_response.content = "Ollama response"; mock_model_instance.return_value = mock_response
        mock_model_class.return_value = mock_model_instance
        
        # Run command
        result = runner.invoke(
            cli,
            ["llm", "ollama", "Local", "test"],
            obj={"config": mock_config, "console": Mock()}
        )
        
        # Verify success
        assert result.exit_code == 0
        assert "Ollama response" in result.output
        
        # Verify model was created with Ollama config
        mock_model_class.assert_called_once()
        call_kwargs = mock_model_class.call_args.kwargs
        assert call_kwargs["model_id"] == "ollama/llama3.2:1b"
        assert call_kwargs["api_base"] == "http://localhost:11434"


def test_llm_command_with_invalid_provider(runner, mock_config):
    """Test /llm command with non-existent provider."""
    with patch("simple_agent.commands.llm.ConfigManager.get") as mock_get:
        
        # Mock config retrieval - return None for invalid provider
        def get_side_effect(config, path, default=None):
            if path == "llm.nonexistent":
                return None
            return default
        
        mock_get.side_effect = get_side_effect
        
        # Run command
        result = runner.invoke(
            cli,
            ["llm", "nonexistent", "Test", "prompt"],
            obj={"config": mock_config, "console": Mock()}
        )
        
        # Verify error handling
        assert result.exit_code == 0  # Command doesn't raise, just prints error
        assert "not found" in result.output.lower()


def test_llm_command_with_missing_config(runner, mock_config):
    """Test /llm command when provider config is missing required fields."""
    with patch("simple_agent.commands.llm.ConfigManager.get") as mock_get:
        
        # Mock config retrieval - return config without 'model' key
        def get_side_effect(config, path, default=None):
            if path == "llm.openai":
                return {"api_key": "test-key"}  # Missing 'model' key
            return default
        
        mock_get.side_effect = get_side_effect
        
        # Run command
        result = runner.invoke(
            cli,
            ["llm", "openai", "Test"],
            obj={"config": mock_config, "console": Mock()}
        )
        
        # Verify error is caught and displayed
        assert result.exit_code == 0  # Doesn't crash
        assert "error" in result.output.lower() or "Error" in result.output


def test_llm_command_multi_word_prompt(runner, mock_config):
    """Test /llm command handles multi-word prompts correctly."""
    with patch("simple_agent.commands.llm.ConfigManager.get") as mock_get, \
         patch("simple_agent.commands.llm.LiteLLMModel") as mock_model_class:
        
        # Mock config retrieval
        def get_side_effect(config, path, default=None):
            if path == "llm.openai":
                return mock_config["llm"]["openai"]
            return default
        
        mock_get.side_effect = get_side_effect
        
        # Mock LiteLLM model
        mock_model_instance = Mock()
        mock_response = Mock(); mock_response.content = "Response"; mock_model_instance.return_value = mock_response
        mock_model_class.return_value = mock_model_instance
        
        # Run command with multi-word prompt
        result = runner.invoke(
            cli,
            ["llm", "openai", "This", "is", "a", "long", "prompt", "with", "many", "words"],
            obj={"config": mock_config, "console": Mock()}
        )
        
        # Verify prompt was joined correctly
        mock_model_instance.assert_called_once_with([{"role": "user", "content": "This is a long prompt with many words"}])
        assert result.exit_code == 0


def test_llm_command_no_prompt(runner, mock_config):
    """Test /llm command handles missing prompt gracefully."""
    result = runner.invoke(
        cli,
        ["llm", "openai"],  # No prompt args
        obj={"config": mock_config, "console": Mock()}
    )

    # Command exits gracefully with error message (not exception)
    assert result.exit_code == 0
    assert "error" in result.output.lower()
