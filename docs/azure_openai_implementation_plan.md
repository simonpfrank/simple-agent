# Azure OpenAI Implementation Plan

**Date:** 2025-01-04  
**Target Model:** gpt-4o-mini (deployment name from Azure_model_names_and_versions.md)  
**Focus:** Basic functionality without cost tracking

---

## Implementation Steps

### 1. Update config.yaml ✅

Add Azure OpenAI configuration section:

```yaml
llm:
  provider: "azure_openai"  # Change from "openai" when using Azure
  
  # Azure OpenAI Configuration
  azure_openai:
    model: "gpt-4o-mini"  # Azure deployment name
    azure_endpoint: "https://api.lab.ai.wtwco.com"
    api_version: "2024-07-18"  # From Azure_model_names_and_versions.md
    temperature: 0.7
    max_tokens: 2000
    auth_type: "azure_ad"  # Use Azure AD authentication (recommended)
```

**Location:** `config.yaml` - add after `anthropic:` section

---

### 2. Update simple_agent.py - _create_model() method

Add `azure_openai` provider branch in `_create_model()` method:

```python
def _create_model(self, provider: str, config: Dict[str, Any]) -> LiteLLMModel:
    """Create LiteLLM model instance based on provider."""
    
    model_id = config.get("model")
    if not model_id:
        logger.warning(f"No 'model' key in config for provider '{provider}'.")
        model_id = provider
    
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 2000)
    
    # ... existing openai, ollama, anthropic branches ...
    
    elif provider == "azure_openai":
        # Azure OpenAI with Azure AD authentication
        azure_endpoint = config.get("azure_endpoint")
        api_version = config.get("api_version", "2024-07-18")
        
        if not azure_endpoint:
            raise ValueError("azure_endpoint is required for azure_openai provider")
        
        # Resolve environment variables if present
        azure_endpoint = ConfigManager.resolve_env_var(azure_endpoint)
        
        # Check authentication type
        auth_type = config.get("auth_type", "azure_ad")
        
        if auth_type == "azure_ad":
            # Azure AD authentication (recommended for enterprise)
            try:
                from azure.identity import DefaultAzureCredential, get_bearer_token_provider
                
                logger.info("Using Azure AD authentication for Azure OpenAI")
                
                # Create token provider
                credential = DefaultAzureCredential()
                token_provider = get_bearer_token_provider(
                    credential, 
                    f"{azure_endpoint}/.default"
                )
                
                # Get initial token (callable returns fresh token)
                azure_ad_token = token_provider()
                
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
        else:
            # API Key authentication (fallback)
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
    
    else:
        # Generic provider - let LiteLLM figure it out
        logger.warning(f"Unknown provider: {provider}, using generic configuration")
        # ... existing generic code ...
```

**Location:** `simple_agent/agents/simple_agent.py` - add after `anthropic` branch (around line 290)

---

### 3. Update config.yaml comments

Add comprehensive comments for Azure OpenAI configuration:

```yaml
  # Azure OpenAI Configuration (Enterprise/WTW)
  azure_openai:
    model: "gpt-4o-mini"  # Azure deployment name (see docs/Azure_model_names_and_versions.md)
    azure_endpoint: "https://api.lab.ai.wtwco.com"  # Azure OpenAI endpoint URL
    api_version: "2024-07-18"  # API version (from Azure deployment)
    temperature: 0.7
    max_tokens: 2000
    auth_type: "azure_ad"  # Authentication: "azure_ad" (recommended) or "api_key"
    # api_key: "${AZURE_OPENAI_API_KEY}"  # Only needed if auth_type="api_key"
```

**Note:** Available deployments and versions documented in `docs/Azure_model_names_and_versions.md`

---

### 4. Test Azure OpenAI provider (Manual)

**Prerequisites:**
- Ensure Azure AD credentials are configured:
  - Run `az login` (Azure CLI)
  - OR set environment variables: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

**Test steps:**
```bash
# 1. Update config.yaml to use azure_openai provider
# 2. Run simple-agent CLI
simple-agent

# 3. Test with a simple prompt
> What is 2+2?

# 4. Verify response comes from Azure OpenAI
# Check logs for: "Using Azure AD authentication for Azure OpenAI"
```

---

### 5. Add unit tests (Optional but recommended)

Create test file: `tests/unit/test_azure_openai_provider.py`

```python
"""Unit tests for Azure OpenAI provider."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from simple_agent.agents.simple_agent import SimpleAgent
from simple_agent.agents.agent_config import AgentConfig


@patch('simple_agent.agents.simple_agent.DefaultAzureCredential')
@patch('simple_agent.agents.simple_agent.get_bearer_token_provider')
@patch('simple_agent.agents.simple_agent.LiteLLMModel')
def test_azure_openai_with_azure_ad_auth(mock_litellm, mock_token_provider, mock_credential):
    """Test Azure OpenAI model creation with Azure AD authentication."""
    # Setup mocks
    mock_token_provider.return_value = lambda: "mock_bearer_token"
    
    config = {
        "model": "gpt-4o-mini",
        "azure_endpoint": "https://api.lab.ai.wtwco.com",
        "api_version": "2024-07-18",
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
    assert call_kwargs['api_version'] == "2024-07-18"
    assert call_kwargs['azure_ad_token'] == "mock_bearer_token"
    assert call_kwargs['temperature'] == 0.7
    assert call_kwargs['max_tokens'] == 2000


def test_azure_openai_missing_endpoint():
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
def test_azure_openai_with_api_key(mock_litellm):
    """Test Azure OpenAI with API key authentication."""
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
```

**Run tests:**
```bash
pytest tests/unit/test_azure_openai_provider.py -v
```

---

### 6. Update documentation (Optional)

Add section to README.md:

```markdown
## Azure OpenAI Configuration

For enterprise deployments using Azure OpenAI:

```yaml
llm:
  provider: "azure_openai"
  
  azure_openai:
    model: "gpt-4o-mini"  # Your Azure deployment name
    azure_endpoint: "https://api.lab.ai.wtwco.com"
    api_version: "2024-07-18"
    temperature: 0.7
    max_tokens: 2000
    auth_type: "azure_ad"  # Recommended for enterprise
```

### Authentication Setup

**Azure AD (Recommended):**
```bash
# Option 1: Azure CLI
az login

# Option 2: Environment Variables
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

**API Key (Alternative):**
```yaml
azure_openai:
  auth_type: "api_key"
  api_key: "${AZURE_OPENAI_API_KEY}"  # Set in .env file
```

See `docs/Azure_model_names_and_versions.md` for available models.
```

---

## Files to Modify

1. ✅ `config.yaml` - Add azure_openai section
2. ✅ `simple_agent/agents/simple_agent.py` - Add provider branch in `_create_model()`
3. ⚠️ `tests/unit/test_azure_openai_provider.py` - Create new test file (optional)
4. ⚠️ `README.md` - Add Azure OpenAI section (optional)

---

## Testing Checklist

- [ ] Config.yaml has azure_openai section
- [ ] Can create agent with azure_openai provider
- [ ] Azure AD authentication works (requires valid credentials)
- [ ] Agent can execute prompts successfully
- [ ] Error handling works (missing endpoint, auth failures)
- [ ] Logs show correct provider and endpoint
- [ ] API key fallback works (if implemented)

---

## Known Limitations

1. **No cost tracking** - Azure OpenAI usage not tracked (by design)
2. **Token refresh** - Handled automatically by DefaultAzureCredential
3. **Model mapping** - Uses Azure deployment name directly (no mapping to base models)
4. **Rate limits** - Enforced by Azure (see Max TPM in Azure_model_names_and_versions.md)

---

## Rollback Plan

If issues occur:
1. Change `provider: "azure_openai"` back to `provider: "openai"`
2. No code changes needed - provider is runtime configuration

---

## Estimated Effort

- **Config changes:** 5 minutes
- **Code implementation:** 30-45 minutes
- **Testing:** 15-30 minutes
- **Documentation:** 15 minutes (optional)

**Total:** ~1-1.5 hours (without comprehensive testing)

---

## Next Steps

1. Add azure_openai section to config.yaml
2. Implement _create_model() branch for azure_openai
3. Test manually with valid Azure credentials
4. (Optional) Add unit tests
5. (Optional) Update documentation

---

**Status:** Ready to implement
