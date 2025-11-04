# Azure OpenAI Integration Research Findings

**Date:** 2025-01-04  
**Research Scope:** Azure OpenAI provider integration with simple-agent using smolagents + LiteLLM

---

## 1. LiteLLM Azure OpenAI Support ✅

### Finding: FULLY SUPPORTED
- **LiteLLM version installed:** 1.79.1
- **Azure OpenAI support:** YES - Native support included
- **Model format:** `azure/<deployment_name>` (e.g., `azure/gpt-4`, `azure/my-deployment`)

### Key Components Available:
```python
# LiteLLM has extensive Azure support
- AzureChatCompletion
- AzureOpenAIConfig
- AzureOpenAIError
- AzureTextCompletion
- enable_azure_ad_token_refresh (function for token refresh)
- AZURE_DEFAULT_API_VERSION = "2025-02-01-preview"
```

### Required Parameters for Azure OpenAI:
```python
litellm.completion(
    model="azure/<deployment_name>",
    api_base="https://api.lab.ai.wtwco.com",  # Azure endpoint
    api_version="2024-02-01",                  # API version
    azure_ad_token="<token>"                   # OR api_key="<key>"
)
```

---

## 2. SmolAgents LiteLLMModel Compatibility ✅

### Finding: FULLY COMPATIBLE
- **Class:** `smolagents.LiteLLMModel`
- **Constructor signature:**
```python
LiteLLMModel(
    model_id: str | None = None,
    api_base: str | None = None,
    api_key: str | None = None,
    custom_role_conversions: dict[str, str] | None = None,
    flatten_messages_as_text: bool | None = None,
    **kwargs  # <-- Accepts additional parameters!
)
```

### Critical: **kwargs Support
- The `**kwargs` parameter means we can pass Azure-specific parameters:
  - `api_version` (required for Azure)
  - `azure_ad_token` (for Azure AD authentication)
  - Any other Azure-specific parameters

### Usage Pattern:
```python
from smolagents import LiteLLMModel

model = LiteLLMModel(
    model_id="azure/gpt-4",
    api_base="https://api.lab.ai.wtwco.com",
    api_version="2024-02-01",  # Passed via kwargs
    azure_ad_token="<token>",  # Passed via kwargs
)
```

---

## 3. Azure AD Authentication Support ✅

### Finding: ALL DEPENDENCIES AVAILABLE

**Azure Identity Package:**
- **Status:** INSTALLED (already in environment)
- **Package:** `azure-identity`
- **Key classes available:**
  - `DefaultAzureCredential` ✅
  - `get_bearer_token_provider` ✅

**OpenAI SDK:**
- **Version:** 2.7.1
- **AzureOpenAI client:** AVAILABLE ✅

### Authentication Implementation:
```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Create token provider
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), 
    "https://api.lab.ai.wtwco.com/.default"
)

# Token provider is callable - returns fresh tokens automatically
token = token_provider()  # Returns: "Bearer <token>"
```

### Token Refresh:
- **LiteLLM has built-in support:** `litellm.enable_azure_ad_token_refresh()`
- **Token provider handles refresh automatically** via DefaultAzureCredential
- No manual token management needed

---

## 4. Configuration Structure

### Recommended config.yaml Structure:
```yaml
llm:
  provider: "azure_openai"
  
  azure_openai:
    model: "gpt-4"  # Deployment name in Azure
    azure_endpoint: "https://api.lab.ai.wtwco.com"
    api_version: "2024-02-01"
    temperature: 0.7
    max_tokens: 2000
    # Note: No api_key needed - using Azure AD auth
```

### Alternative: Support both API key and Azure AD:
```yaml
llm:
  azure_openai:
    model: "gpt-4"
    azure_endpoint: "https://api.lab.ai.wtwco.com"
    api_version: "2024-02-01"
    auth_type: "azure_ad"  # or "api_key"
    api_key: "${AZURE_OPENAI_API_KEY}"  # Optional, only if auth_type=api_key
```

---

## 5. Token Counting and Cost Calculation

### Finding: MAPPING REQUIRED

**Current Implementation:**
- `simple_agent/tools/helpers/model_pricing.py` has pricing for OpenAI models
- Pricing table uses model names like "gpt-4", "gpt-4o-mini", etc.

**Azure Model Naming:**
- Azure deployments can have custom names: "my-gpt4-deployment"
- Need to map Azure deployment names to base model names for pricing

**Solution Options:**

**Option A: Strip azure/ prefix**
```python
# azure/gpt-4 -> gpt-4
# azure/my-gpt4 -> my-gpt4 (then lookup by partial match)
model_for_pricing = model_name.replace("azure/", "")
```

**Option B: Add Azure deployment mapping to config**
```yaml
azure_openai:
  deployments:
    my-gpt4-deployment:
      base_model: "gpt-4"  # Maps to pricing table
      pricing_override:    # Optional custom pricing
        input: 30
        output: 60
```

**Option C: Use Azure model metadata (advanced)**
- Query Azure API for deployment model info
- Automatically determine base model

**Recommendation:** Start with Option A (simple), add Option B if needed for custom deployments

---

## 6. Dependencies Check

### Currently Installed ✅
- `litellm>=1.0.0` (1.79.1 installed)
- `azure-identity` (AVAILABLE - likely installed as transitive dependency)
- `openai` (2.7.1)
- `smolagents>=0.1.0` (AVAILABLE)

### Additional Dependencies Needed
**NONE** - All required packages are already installed!

### requirements.txt Update
**Optional:** Explicitly add `azure-identity` for clarity:
```txt
# Azure OpenAI support
azure-identity>=1.15.0  # For DefaultAzureCredential
```

---

## 7. Implementation Pattern

### Model Creation in simple_agent.py

```python
def _create_model(self, provider: str, config: Dict[str, Any]) -> LiteLLMModel:
    """Create LiteLLM model instance based on provider."""
    
    # ... existing code ...
    
    elif provider == "azure_openai":
        # Azure OpenAI with Azure AD authentication
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        
        azure_endpoint = config.get("azure_endpoint")
        api_version = config.get("api_version", "2024-02-01")
        model_id = config.get("model")
        
        if not azure_endpoint:
            raise ValueError("azure_endpoint is required for azure_openai provider")
        
        # Resolve env vars if present
        azure_endpoint = ConfigManager.resolve_env_var(azure_endpoint)
        
        # Check authentication type
        auth_type = config.get("auth_type", "azure_ad")
        
        if auth_type == "azure_ad":
            # Azure AD authentication (recommended for enterprise)
            logger.info("Using Azure AD authentication for Azure OpenAI")
            
            # Create token provider
            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(
                credential, 
                f"{azure_endpoint}/.default"
            )
            
            # Get token (callable returns fresh token)
            azure_ad_token = token_provider()
            
            return LiteLLMModel(
                model_id=f"azure/{model_id}",
                api_base=azure_endpoint,
                api_version=api_version,
                azure_ad_token=azure_ad_token,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            # API Key authentication (fallback)
            api_key = config.get("api_key", "")
            api_key = ConfigManager.resolve_env_var(api_key)
            
            return LiteLLMModel(
                model_id=f"azure/{model_id}",
                api_base=azure_endpoint,
                api_key=api_key,
                api_version=api_version,
                temperature=temperature,
                max_tokens=max_tokens,
            )
```

---

## 8. Testing Strategy

### Unit Tests
```python
def test_azure_openai_model_creation():
    """Test Azure OpenAI model creation with Azure AD auth."""
    config = {
        "model": "gpt-4",
        "azure_endpoint": "https://api.lab.ai.wtwco.com",
        "api_version": "2024-02-01",
        "auth_type": "azure_ad",
        "temperature": 0.7,
        "max_tokens": 2000,
    }
    
    agent = SimpleAgent(
        name="test",
        model_provider="azure_openai",
        model_config=config,
    )
    
    assert agent.model_provider == "azure_openai"
    # Model should be created successfully
```

### Integration Tests
- Requires actual Azure OpenAI endpoint access
- Test with real Azure AD credentials
- Validate token refresh behavior
- Test error handling (auth failures, network issues)

### Mock Testing
```python
from unittest.mock import Mock, patch

@patch('azure.identity.DefaultAzureCredential')
@patch('azure.identity.get_bearer_token_provider')
def test_azure_ad_auth_mocked(mock_token_provider, mock_credential):
    """Test Azure AD authentication with mocked credentials."""
    mock_token_provider.return_value = lambda: "mock_token"
    # ... test implementation
```

---

## 9. Error Handling Requirements

### Authentication Errors
```python
try:
    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(credential, scope)
except Exception as e:
    logger.error(f"Azure AD authentication failed: {e}")
    raise ValueError(
        "Failed to authenticate with Azure AD. "
        "Ensure you have valid Azure credentials configured."
    )
```

### Configuration Validation
```python
if provider == "azure_openai":
    if not config.get("azure_endpoint"):
        raise ValueError("azure_endpoint is required for azure_openai provider")
    if not config.get("api_version"):
        logger.warning("api_version not specified, using default: 2024-02-01")
```

### Network Errors
- Handle connection timeouts to Azure endpoint
- Retry logic for transient failures
- Clear error messages for users

---

## 10. Documentation Requirements

### README.md Updates
```markdown
### Azure OpenAI Configuration

```yaml
llm:
  provider: "azure_openai"
  
  azure_openai:
    model: "gpt-4"  # Your Azure deployment name
    azure_endpoint: "https://api.lab.ai.wtwco.com"
    api_version: "2024-02-01"
    temperature: 0.7
    max_tokens: 2000
```

**Authentication:**
Uses Azure Active Directory (Azure AD) authentication via DefaultAzureCredential.
Ensure you have valid Azure credentials configured:
- Azure CLI: `az login`
- Environment variables: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`
- Managed Identity (when deployed to Azure)
```

### config.yaml Comments
Add comprehensive comments explaining:
- Azure endpoint format
- API version options
- Authentication types
- Deployment name vs. model name

---

## 11. Edge Cases and Considerations

### Deployment Names vs Model Names
- **Issue:** Azure deployments can have custom names (e.g., "my-prod-gpt4")
- **Solution:** Store mapping in config or use naming conventions

### Token Refresh
- **DefaultAzureCredential handles refresh automatically**
- Token lifetime typically 1 hour
- LiteLLM may cache tokens - verify refresh behavior in long-running agents

### Multi-Region Support
- Different Azure regions have different endpoints
- Config should support multiple endpoints
- Consider adding region-specific configuration

### API Version Compatibility
- API versions change over time
- Default to latest stable version
- Document which versions are tested/supported

### Cost Tracking
- Azure pricing may differ from standard OpenAI pricing
- Consider adding Azure-specific pricing config
- Log deployment name for cost attribution

---

## 12. Recommended Implementation Order

1. **Add config structure** to config.yaml with azure_openai section
2. **Update _create_model()** in simple_agent.py with azure_openai branch
3. **Implement Azure AD authentication** with DefaultAzureCredential
4. **Add pricing mapping** for Azure models in model_pricing.py
5. **Write unit tests** with mocked Azure credentials
6. **Update documentation** (README, config comments)
7. **Integration testing** with real Azure endpoint (if available)
8. **Add API key fallback** for backward compatibility

---

## 13. Summary: Ready to Implement ✅

### Key Findings:
✅ **LiteLLM has full Azure OpenAI support** (native integration)  
✅ **SmolAgents LiteLLMModel is compatible** (via **kwargs)  
✅ **All dependencies already installed** (azure-identity, openai)  
✅ **Token refresh is automatic** (via DefaultAzureCredential)  
✅ **No custom wrapper needed** - use existing LiteLLMModel  
✅ **Implementation is straightforward** - add provider branch in _create_model()

### Implementation Complexity: LOW
- Estimated effort: 2-4 hours
- No architectural changes required
- Follows existing provider pattern
- Comprehensive testing will add 2-3 hours

### Risks: LOW
- Well-documented APIs
- All dependencies available
- Proven integration pattern (LiteLLM + SmolAgents)
- Token refresh handled by Azure SDK

---

## 14. Open Questions

1. **Should we support both Azure AD and API key auth?**
   - Recommendation: YES - start with Azure AD, add API key as fallback

2. **How should we handle deployment name to model name mapping for pricing?**
   - Recommendation: Start simple (strip azure/ prefix), add config mapping if needed

3. **Do we need custom retry logic for Azure endpoints?**
   - Recommendation: Start with LiteLLM defaults, monitor and adjust

4. **Should api_version be required or have a default?**
   - Recommendation: Optional with default ("2024-02-01"), log warning if not specified

---

**Status:** Ready to implement - no blockers identified
