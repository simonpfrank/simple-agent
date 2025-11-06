"""Unit tests for Azure OpenAI provider.

Tests cover:
- Model creation with Azure AD authentication
- Model creation with API key authentication
- Configuration validation
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from simple_agent.agents.simple_agent import SimpleAgent
from simple_agent.agents.agent_config import AgentConfig


class TestAzureOpenAIProvider:
    """Test suite for Azure OpenAI provider integration."""

    @patch('azure.identity.DefaultAzureCredential')
    @patch('azure.identity.get_bearer_token_provider')
    @patch('simple_agent.agents.simple_agent.LiteLLMModel')
    def test_azure_openai_with_azure_ad_auth(
        self, mock_litellm, mock_token_provider, mock_credential
    ):
        """Test Azure OpenAI model creation with Azure AD authentication."""
        # Setup mocks
        mock_token_provider.return_value = lambda: "mock_bearer_token"
        mock_model_instance = Mock()
        mock_litellm.return_value = mock_model_instance

        config = {
            "model": "gpt-4o-mini",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            "api_version": "2024-02-01",
            "auth_type": "azure_ad",
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        # Create agent
        agent = SimpleAgent(
            name="test_azure",
            model_provider="azure_openai",
            model_config=config,
        )

        # Verify LiteLLMModel was called with correct parameters
        mock_litellm.assert_called_once()
        call_kwargs = mock_litellm.call_args[1]

        assert call_kwargs['model_id'] == "azure/gpt-4o-mini"
        assert call_kwargs['api_base'] == "https://api.lab.ai.wtwco.com"
        assert call_kwargs['api_version'] == "2024-02-01"
        assert 'azure_ad_token' in call_kwargs
        assert call_kwargs['azure_ad_token'] == "mock_bearer_token"
        assert call_kwargs['temperature'] == 0.7
        assert call_kwargs['max_tokens'] == 2000

        # Verify agent was created with correct provider
        assert agent.model_provider == "azure_openai"

    def test_azure_openai_missing_endpoint(self):
        """Test that missing azure_endpoint raises ValueError."""
        config = {
            "model": "gpt-4o-mini",
            # Missing azure_endpoint
            "api_version": "2024-07-18",
        }

        with pytest.raises(ValueError, match="azure_endpoint is required"):
            SimpleAgent(
                name="test_azure",
                model_provider="azure_openai",
                model_config=config,
            )

    @patch('simple_agent.agents.simple_agent.LiteLLMModel')
    def test_azure_openai_with_api_key(self, mock_litellm):
        """Test Azure OpenAI with API key authentication."""
        mock_model_instance = Mock()
        mock_litellm.return_value = mock_model_instance

        config = {
            "model": "gpt-4o-mini",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            "api_version": "2024-07-18",
            "auth_type": "api_key",
            "api_key": "test_api_key",
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        agent = SimpleAgent(
            name="test_azure",
            model_provider="azure_openai",
            model_config=config,
        )

        # Verify LiteLLMModel was called with API key
        call_kwargs = mock_litellm.call_args[1]
        assert call_kwargs['model_id'] == "azure/gpt-4o-mini"
        assert call_kwargs['api_key'] == "test_api_key"
        assert 'azure_ad_token' not in call_kwargs
        assert call_kwargs['api_version'] == "2024-07-18"

    def test_azure_openai_api_key_missing(self):
        """Test that missing api_key with api_key auth_type raises ValueError."""
        config = {
            "model": "gpt-4o-mini",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            "api_version": "2024-07-18",
            "auth_type": "api_key",
            # Missing api_key
        }

        with pytest.raises(ValueError, match="api_key is required"):
            SimpleAgent(
                name="test_azure",
                model_provider="azure_openai",
                model_config=config,
            )

    @patch('azure.identity.DefaultAzureCredential')
    @patch('azure.identity.get_bearer_token_provider')
    def test_azure_openai_auth_failure(
        self, mock_token_provider, mock_credential
    ):
        """Test Azure AD authentication failure handling."""
        # Mock authentication failure
        mock_credential.side_effect = Exception("Auth failed")

        config = {
            "model": "gpt-4o-mini",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            "api_version": "2024-07-18",
            "auth_type": "azure_ad",
        }

        with pytest.raises(ValueError, match="Failed to authenticate with Azure AD"):
            SimpleAgent(
                name="test_azure",
                model_provider="azure_openai",
                model_config=config,
            )

    @patch('azure.identity.DefaultAzureCredential')
    @patch('azure.identity.get_bearer_token_provider')
    @patch('simple_agent.agents.simple_agent.LiteLLMModel')
    def test_azure_openai_default_api_version(
        self, mock_litellm, mock_token_provider, mock_credential
    ):
        """Test that api_version defaults to 2024-07-18 if not specified."""
        mock_token_provider.return_value = lambda: "mock_token"
        mock_model_instance = Mock()
        mock_litellm.return_value = mock_model_instance

        config = {
            "model": "gpt-4o-mini",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            # api_version not specified
            "auth_type": "azure_ad",
        }

        agent = SimpleAgent(
            name="test_azure",
            model_provider="azure_openai",
            model_config=config,
        )

        # Verify default api_version was used
        call_kwargs = mock_litellm.call_args[1]
        assert call_kwargs['api_version'] == "2024-02-01"

    @patch('azure.identity.DefaultAzureCredential')
    @patch('azure.identity.get_bearer_token_provider')
    @patch('simple_agent.agents.simple_agent.LiteLLMModel')
    def test_azure_openai_default_auth_type(
        self, mock_litellm, mock_token_provider, mock_credential
    ):
        """Test that auth_type defaults to azure_ad if not specified."""
        mock_token_provider.return_value = lambda: "mock_token"
        mock_model_instance = Mock()
        mock_litellm.return_value = mock_model_instance

        config = {
            "model": "gpt-4o-mini",
            "azure_endpoint": "https://api.lab.ai.wtwco.com",
            "api_version": "2024-07-18",
            # auth_type not specified - should default to azure_ad
        }

        agent = SimpleAgent(
            name="test_azure",
            model_provider="azure_openai",
            model_config=config,
        )

        # Verify Azure AD authentication was used
        mock_credential.assert_called_once()
        mock_token_provider.assert_called_once()

    @patch('simple_agent.agents.simple_agent.ConfigManager')
    @patch('simple_agent.agents.simple_agent.LiteLLMModel')
    def test_azure_openai_env_var_resolution(self, mock_litellm, mock_config_manager):
        """Test that environment variables in azure_endpoint are resolved."""
        mock_model_instance = Mock()
        mock_litellm.return_value = mock_model_instance
        
        # Mock env var resolution
        mock_config_manager.resolve_env_var.return_value = "https://resolved-endpoint.com"

        config = {
            "model": "gpt-4o-mini",
            "azure_endpoint": "${AZURE_ENDPOINT}",
            "api_version": "2024-07-18",
            "auth_type": "api_key",
            "api_key": "test_key",
        }

        agent = SimpleAgent(
            name="test_azure",
            model_provider="azure_openai",
            model_config=config,
        )

        # Verify env var was resolved
        mock_config_manager.resolve_env_var.assert_called()
        
        # Verify resolved endpoint was used
        call_kwargs = mock_litellm.call_args[1]
        assert call_kwargs['api_base'] == "https://resolved-endpoint.com"
