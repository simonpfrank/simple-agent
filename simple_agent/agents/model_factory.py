"""
Model factory for creating LiteLLM model instances.

Extracts model creation logic from SimpleAgent to reduce file size
and improve maintainability.
"""

import logging
from typing import Any, Dict

from smolagents import LiteLLMModel

from simple_agent.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)


def create_litellm_model(provider: str, config: Dict[str, Any]) -> LiteLLMModel:
    """
    Create LiteLLM model instance based on provider.

    Args:
        provider: LLM provider name (openai, ollama, azure_openai, etc.)
        config: Model configuration dict (may contain ${VAR} placeholders)

    Returns:
        LiteLLMModel instance

    Raises:
        ValueError: If required model configuration is missing
    """
    logger.info(f"Creating LiteLLM Model for provider: {provider}")
    model_id = config.get("model")
    if not model_id:
        logger.warning(
            f"No 'model' key in config for provider '{provider}'. "
            f"Config keys: {list(config.keys())}. Using provider name as fallback."
        )
        model_id = provider

    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 2000)

    logger.debug(
        f"Creating LiteLLM model - provider: {provider}, "
        f"model: {model_id}, temp: {temperature}, max_tokens: {max_tokens}"
    )

    if provider in ("ollama", "lmstudio"):
        return _create_local_model(provider, model_id, config, temperature, max_tokens)
    elif provider == "openai":
        return _create_openai_model(model_id, config, temperature, max_tokens)
    elif provider == "Anthropic":
        return _create_anthropic_model(model_id, config, temperature, max_tokens)
    elif provider == "azure_openai":
        return _create_azure_model(model_id, config, temperature, max_tokens)
    else:
        return _create_generic_model(provider, model_id, config, temperature, max_tokens)


def _create_local_model(
    provider: str,
    model_id: str,
    config: Dict[str, Any],
    temperature: float,
    max_tokens: int,
) -> LiteLLMModel:
    """Create model for local providers (Ollama, LMStudio)."""
    base_url = config.get("base_url", "http://localhost:11434")
    base_url = ConfigManager.resolve_env_var(base_url)
    logger.info(f"Creating {provider} model")
    return LiteLLMModel(
        model_id=f"ollama/{model_id}",
        api_base=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def _create_openai_model(
    model_id: str,
    config: Dict[str, Any],
    temperature: float,
    max_tokens: int,
) -> LiteLLMModel:
    """Create OpenAI model."""
    api_key = config.get("api_key", "")
    api_key = ConfigManager.resolve_env_var(api_key)
    logger.info("Creating OpenAI model")
    return LiteLLMModel(
        model_id=model_id,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def _create_anthropic_model(
    model_id: str,
    config: Dict[str, Any],
    temperature: float,
    max_tokens: int,
) -> LiteLLMModel:
    """Create Anthropic model."""
    logger.info("Creating Anthropic model")
    api_key = config.get("api_key", "")
    api_key = ConfigManager.resolve_env_var(api_key)
    return LiteLLMModel(
        model_id=model_id,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def _create_azure_model(
    model_id: str,
    config: Dict[str, Any],
    temperature: float,
    max_tokens: int,
) -> LiteLLMModel:
    """Create Azure OpenAI model with Azure AD or API key authentication."""
    logger.info("Creating Azure OpenAI model")
    azure_endpoint = config.get("azure_endpoint")
    api_version = config.get("api_version", "2024-02-01")

    if not azure_endpoint:
        raise ValueError("azure_endpoint is required for azure_openai provider")

    azure_endpoint = ConfigManager.resolve_env_var(azure_endpoint)
    auth_type = config.get("auth_type", "azure_ad")

    if auth_type == "azure_ad":
        return _create_azure_ad_model(
            model_id, azure_endpoint, api_version, temperature, max_tokens
        )
    else:
        return _create_azure_apikey_model(
            model_id, config, azure_endpoint, api_version, temperature, max_tokens
        )


def _create_azure_ad_model(
    model_id: str,
    azure_endpoint: str,
    api_version: str,
    temperature: float,
    max_tokens: int,
) -> LiteLLMModel:
    """Create Azure OpenAI model with Azure AD authentication."""
    try:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider

        logger.info("Using Azure AD authentication for Azure OpenAI")

        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential, f"{azure_endpoint}/.default"
        )
        azure_ad_token = token_provider()

        import litellm
        litellm.drop_params = True

        logger.debug(
            f"Created Azure OpenAI model - endpoint: {azure_endpoint}, "
            f"model: {model_id}, api_version: {api_version}"
        )

        return LiteLLMModel(
            model_id=f"azure/{model_id}",
            api_base=azure_endpoint,
            api_version=api_version,
            azure_ad_token=azure_ad_token,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except ImportError as e:
        raise ValueError(
            "Azure AD authentication requires 'azure-identity' package. "
            f"Install it with: pip install azure-identity. Error: {e}"
        )
    except Exception as e:
        logger.error(f"Azure AD authentication failed: {e}")
        raise ValueError(
            f"Failed to authenticate with Azure AD: {e}. "
            "Ensure you have valid Azure credentials configured "
            "(run 'az login' or set environment variables)."
        )


def _create_azure_apikey_model(
    model_id: str,
    config: Dict[str, Any],
    azure_endpoint: str,
    api_version: str,
    temperature: float,
    max_tokens: int,
) -> LiteLLMModel:
    """Create Azure OpenAI model with API key authentication."""
    api_key = config.get("api_key", "")
    if not api_key:
        raise ValueError("api_key is required when auth_type is not 'azure_ad'")

    api_key = ConfigManager.resolve_env_var(api_key)

    logger.debug(
        f"Created Azure OpenAI model with API key - endpoint: {azure_endpoint}, "
        f"model: {model_id}, api_version: {api_version}"
    )

    return LiteLLMModel(
        model_id=f"azure/{model_id}",
        api_base=azure_endpoint,
        api_key=api_key,
        api_version=api_version,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def _create_generic_model(
    provider: str,
    model_id: str,
    config: Dict[str, Any],
    temperature: float,
    max_tokens: int,
) -> LiteLLMModel:
    """Create generic model - let LiteLLM figure out the provider."""
    logger.warning(f"Unknown provider: {provider}, using generic configuration")
    api_key = config.get("api_key")
    if api_key:
        api_key = ConfigManager.resolve_env_var(api_key)
        return LiteLLMModel(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        return LiteLLMModel(
            model_id=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
        )
