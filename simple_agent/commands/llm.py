"""
Direct LLM command - bypasses agent wrapper for simple LLM calls.

Usage:
    /llm <provider> <prompt>
    /llm <provider> --file <path>

Examples:
    /llm azure_openai What is 2+2?
    /llm openai Explain quantum computing in simple terms
    /llm azure_openai --file temp/test_prompt.md
    /llm azure_openai -f prompt_candidates/system_prompt_2.md
    
Note: Provider names come from config.yaml under 'llm:' section
"""

import logging
from pathlib import Path
import click
from rich.console import Console
from smolagents import LiteLLMModel

from simple_agent.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)
console = Console()


@click.command(name="llm")
@click.argument("provider")
@click.option("--file", "-f", "prompt_file", help="Read prompt from file instead of arguments")
@click.argument("prompt", nargs=-1, required=False)
@click.pass_context
def llm_command(ctx, provider, prompt_file, prompt):
    """
    Direct LLM call without agent wrapper.
    
    Args:
        provider: Provider name from config.llm (e.g., 'azure_openai', 'openai', 'ollama')
        prompt_file: Optional file to read prompt from (use --file or -f)
        prompt: The prompt to send to the LLM (all remaining arguments)
    """
    config_dict = ctx.obj.get("config")
    
    # Read from file or use arguments
    if prompt_file:
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_text = f.read()
            logger.debug(f"Read prompt from file: {prompt_file}")
        except Exception as e:
            console.print(f"[red]Error reading file '{prompt_file}':[/red] {e}")
            logger.error(f"Failed to read prompt file: {e}")
            return
    elif prompt:
        prompt_text = " ".join(prompt)
    else:
        console.print("[red]Error:[/red] Must provide either --file or prompt text")
        return
    
    # Log command (without prompt content for privacy)
    logger.info(f"[COMMAND] /llm - provider={provider}, prompt_len={len(prompt_text)}")
    
    try:
        # Get provider configuration from llm section
        provider_config = ConfigManager.get(config_dict, f"llm.{provider}")
        if not provider_config:
            console.print(f"[red]Error:[/red] Provider '{provider}' not found in config.llm section")
            logger.error(f"Provider '{provider}' not found in config.llm section")
            return
        
        # Provider name is the key itself (e.g., 'azure_openai', 'openai')
        # Config is the dict under that key (has 'model', 'api_key', etc.)
        model_config = provider_config
        
        logger.debug(f"Creating LiteLLM model - provider: {provider}, config keys: {list(model_config.keys())}")
        
        # Create LiteLLM model based on provider type
        model = _create_litellm_model(provider, model_config)
        
        # Make direct LLM call
        # LiteLLM expects messages format, not plain string
        logger.info(f"Sending request to {provider}...")
        messages = [{"role": "user", "content": prompt_text}]
        response = model(messages)
        
        # Extract text content from ChatMessage response
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)

        # Save response to file
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        response_file = temp_dir / "llm_response.md"

        try:
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(response_text)
            logger.info(f"Response saved to {response_file}")
        except Exception as e:
            logger.warning(f"Failed to save response to file: {e}")

        # Display response
        console.print("\n[bold cyan]Response:[/bold cyan]")
        console.print(response_text)
        console.print(f"\n[dim]Response saved to: {response_file}[/dim]")

        logger.info(f"[COMMAND] LLM call completed (response_len={len(response_text)})")
        
    except KeyError as e:
        error_msg = f"Configuration error: {e}"
        console.print(f"[red]Error:[/red] {error_msg}")
        logger.error(error_msg)
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        console.print(f"[red]Error ({error_type}):[/red] {error_msg}")
        logger.error(f"LLM call failed with {error_type}: {error_msg}")


def _create_litellm_model(provider: str, config: dict) -> LiteLLMModel:
    """
    Create LiteLLM model instance based on provider.
    
    Args:
        provider: Provider name (e.g., 'openai', 'azure_openai', 'ollama')
        config: Model configuration dict
        
    Returns:
        LiteLLMModel instance
        
    Raises:
        ValueError: If required configuration is missing
    """
    model_id = config.get("model")
    if not model_id:
        raise ValueError(f"No 'model' key in config for provider '{provider}'")
    
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 2000)
    
    logger.debug(f"Model config - id: {model_id}, temp: {temperature}, max_tokens: {max_tokens}")
    
    # Handle provider-specific configuration
    if provider == "ollama" or provider == "lmstudio":
        # Local models
        base_url = config.get("base_url", "http://localhost:11434")
        base_url = ConfigManager.resolve_env_var(base_url)
        
        return LiteLLMModel(
            model_id=f"ollama/{model_id}",
            api_base=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
    elif provider == "openai":
        # OpenAI models
        api_key = config.get("api_key", "")
        api_key = ConfigManager.resolve_env_var(api_key)
        
        return LiteLLMModel(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
    elif provider == "Anthropic":
        # Anthropic models
        api_key = config.get("api_key", "")
        api_key = ConfigManager.resolve_env_var(api_key)
        
        return LiteLLMModel(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
    elif provider == "azure_openai":
        # Azure OpenAI with Azure AD or API key authentication
        azure_endpoint = config.get("azure_endpoint")
        api_version = config.get("api_version", "2024-02-01")
        
        if not azure_endpoint:
            raise ValueError("azure_endpoint is required for azure_openai provider")
        
        azure_endpoint = ConfigManager.resolve_env_var(azure_endpoint)
        auth_type = config.get("auth_type", "azure_ad")
        
        if auth_type == "azure_ad":
            # Azure AD authentication
            try:
                from azure.identity import DefaultAzureCredential, get_bearer_token_provider
                
                logger.debug("Using Azure AD authentication")
                
                credential = DefaultAzureCredential()
                token_provider = get_bearer_token_provider(
                    credential, f"{azure_endpoint}/.default"
                )
                azure_ad_token = token_provider()
                
                # Enable dropping unsupported params for older Azure API versions
                import litellm
                litellm.drop_params = True
                
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
                raise ValueError(
                    f"Failed to authenticate with Azure AD: {e}. "
                    "Ensure you have valid Azure credentials configured."
                )
        else:
            # API Key authentication
            api_key = config.get("api_key", "")
            if not api_key:
                raise ValueError("api_key is required when auth_type is not 'azure_ad'")
            
            api_key = ConfigManager.resolve_env_var(api_key)
            
            return LiteLLMModel(
                model_id=f"azure/{model_id}",
                api_base=azure_endpoint,
                api_key=api_key,
                api_version=api_version,
                temperature=temperature,
                max_tokens=max_tokens,
            )
    else:
        # Generic provider
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
