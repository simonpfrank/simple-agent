# Azure Tokens-Per-Minute (TPM) and Logging Issues - Remediation Plan

**Date:** 2025-11-11  
**Status:** Planning  
**Priority:** High (Security + Performance)

---

## Problem Summary

### Issue 1: TPM Rate Limiting (Performance)
- **Current Limit:** 10,000 tokens per minute (TPM) on Azure OpenAI deployment
- **Observed Behavior:** First request consumes ~7,325 tokens, second request fails immediately
- **Evidence:** `x-ratelimit-remaining-tokens: 2675` after first request, then 429 errors with `policy-id: DeploymentRatelimit-Token`
- **Impact:** Agent cannot complete tasks requiring multiple LLM calls within 60 seconds

### Issue 2: Azure AD Token Logging (Security)
- **Current Behavior:** Full JWT tokens (2000+ characters) logged in plaintext to `logs/app.log`
- **Security Risk:** HIGH - JWT tokens in logs are a credential leak vulnerability
- **Evidence:** See line 447+ in app.log showing complete `azure_ad_token` in `extra_body`
- **Impact:** Logs are unreadable + security compliance violation

### Issue 3: Excessive Debug Logging (Operational)
- **Current Behavior:** LiteLLM and OpenAI client log every HTTP header, request, response
- **Impact:** Log files are massive, difficult to parse, slow to process
- **Evidence:** 200-line tracebacks for simple rate limit errors

---

## Root Cause Analysis

### Why TPM Limit is Hit So Fast

1. **Large System Prompt:** New domain-generic system prompt is ~268 lines (~2,000 tokens)
2. **Agent Context:** Smolagents maintains conversation history in each request
3. **Tool Definitions:** Multiple tools with detailed schemas add ~500-1,000 tokens
4. **Response Tokens:** LLM response + tool calls consume output token budget
5. **No Token Budget Management:** No tracking or throttling of token usage

**Total per request:** ~7,000-8,000 tokens = only 1-2 requests per minute possible

### Why Tokens Are Logged

- LiteLLM debug mode logs `optional_params` which includes `extra_body['azure_ad_token']`
- No filtering or masking of sensitive fields in logging configuration
- Debug logging enabled globally, not scoped to specific modules

---

## Proposed Solutions

### Phase 1: Critical Security Fix (Immediate)
**Timeline:** Complete today  
**Goal:** Stop logging Azure AD tokens

#### 1.1 Configure LiteLLM to Mask Sensitive Fields
**File:** `simple_agent/core/model_manager.py` (or wherever LiteLLM is configured)

**Leverage LiteLLM's built-in features:**
```python
# LiteLLM has a built-in callback system for logging control
import litellm
from litellm.integrations.custom_logger import CustomLogger

class SensitiveDataFilter(CustomLogger):
    """Custom logger that masks sensitive fields"""
    
    def log_pre_api_call(self, model, messages, kwargs):
        # LiteLLM calls this before API call
        # Mask azure_ad_token in kwargs if present
        if "extra_body" in kwargs and "azure_ad_token" in kwargs.get("extra_body", {}):
            kwargs["extra_body"]["azure_ad_token"] = "***REDACTED***"
        return super().log_pre_api_call(model, messages, kwargs)

# Register the custom logger
litellm.callbacks = [SensitiveDataFilter()]
```

**Alternative if above doesn't work:**
- Set `litellm.suppress_debug_info = True` to prevent detailed param logging
- Or: Disable debug logging entirely and use info/warning levels only

**Verification:**
- Check `logs/app.log` after change - no JWT tokens visible
- Grep for "eyJ" (JWT token start) - should only find "***REDACTED***"

#### 1.2 Add Logging Configuration
**File:** `simple_agent/utils/logging.py` or main config

**DO NOT modify LiteLLM/OpenAI logging directly** - use Python's logging filters:
```python
import logging

class SensitiveDataFilter(logging.Filter):
    """Filter to mask sensitive data in all log records"""
    
    SENSITIVE_PATTERNS = [
        (r'azure_ad_token["\']:\s*["\']eyJ[^"\']+["\']', 'azure_ad_token": "***REDACTED***"'),
        (r'eyJ[A-Za-z0-9_-]{100,}', '***JWT_TOKEN_REDACTED***'),  # Catch any JWT
    ]
    
    def filter(self, record):
        if hasattr(record, 'msg'):
            import re
            msg = str(record.msg)
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                msg = re.sub(pattern, replacement, msg)
            record.msg = msg
        return True

# Apply to all loggers
for logger_name in ['LiteLLM', 'openai', 'httpcore', 'httpx']:
    logger = logging.getLogger(logger_name)
    logger.addFilter(SensitiveDataFilter())
```

---

### Phase 2: Graceful Rate Limit Error Handling (Immediate)
**Timeline:** Complete today  
**Goal:** Catch rate limit errors, display clean messages with limit info, no retry needed

#### 2.1 Current State Analysis
**LiteLLM retry status:**
```python
# Checked: litellm.num_retries = None (no automatic retry enabled)
# Checked: litellm.request_timeout = 6000.0 (default)
```
- ❌ LiteLLM retry is NOT currently configured
- ✅ This is actually GOOD for our use case - we want explicit control
- ✅ Smolagents doesn't override exception handling

**Functional Decision:**
- **Do NOT enable automatic retry** - let rate limits fail fast
- **Trap RateLimitError exceptions** - prevent long tracebacks in REPL
- **Display clean error message** with limit info from last successful response
- **Store rate limits** from response headers for error messages

#### 2.2 Implement Rate Limit Exception Handler
**File:** `simple_agent/agents/simple_agent.py`

**Add rate limit tracking and clean exception handling:**
```python
class SimpleAgent:
    def __init__(self, ...):
        # Track rate limits from last successful API response
        self.last_tpm_limit = None
        self.last_rpm_limit = None
        self.last_tpm_remaining = None
        self.last_rpm_remaining = None
    
    def _extract_rate_limits(self, response):
        """Extract rate limit info from response headers if available"""
        try:
            # LiteLLM/OpenAI stores response in model._last_response
            if hasattr(self.agent.model, '_client'):
                # Access last response headers through OpenAI client
                # (Implementation depends on how Smolagents exposes this)
                pass
        except:
            pass
    
    def run(self, task, reset=True):
        # ... existing code ...
        
        try:
            response = self.agent.run(formatted_prompt, reset=reset)
            
            # Extract and store rate limits on success
            self._extract_rate_limits(response)
            
            # ... rest of success handling ...
        
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            
            # Check if this is a rate limit error
            if "RateLimitError" in error_type or "429" in error_message or "Rate limit" in error_message:
                # Clean rate limit error display
                if self.last_tpm_limit:
                    limit_info = (
                        f"Rate limit exceeded. "
                        f"Tokens: {self.last_tpm_remaining}/{self.last_tpm_limit} TPM, "
                        f"Requests: {self.last_rpm_remaining}/{self.last_rpm_limit} RPM"
                    )
                else:
                    limit_info = (
                        "Rate limit exceeded. Limit details not available - "
                        "enable debug logging to see full error"
                    )
                
                logger.warning(f"[RATE LIMIT] {limit_info}")
                
                # Return AgentResult with concise error (no traceback in REPL)
                return AgentResult.from_response(
                    response="",
                    input_tokens=input_tokens,
                    output_tokens=0,
                    cost=0.0,
                    model=self.model_config.get("model", "unknown"),
                    error=limit_info,
                )
            else:
                # Other errors - use existing error handling
                logger.error(
                    f"Agent '{self.name}' execution failed with {error_type}: {error_message}",
                    exc_info=True,  # Full traceback only in logs
                )
                # ... existing error handling ...
```

**What this does:**
- ✅ Traps RateLimitError before it reaches REPL
- ✅ Displays clean message with TPM/RPM limits if available
- ✅ Falls back to generic message if limits not captured
- ✅ Full traceback only in logs (not REPL output)
- ✅ No automatic retry (user can manually retry after cooldown)

#### 2.3 Alternative: Response Header Parsing
**If Smolagents/LiteLLM doesn't expose response headers easily:**

Use LiteLLM callbacks to capture headers:
```python
from litellm.integrations.custom_logger import CustomLogger

class RateLimitTracker(CustomLogger):
    """Track rate limits from API responses"""
    
    def __init__(self):
        self.tpm_limit = None
        self.rpm_limit = None
        self.tpm_remaining = None
        self.rpm_remaining = None
    
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """Called after successful API call"""
        # Extract headers from response_obj
        if hasattr(response_obj, '_response'):
            headers = getattr(response_obj._response, 'headers', {})
            self.tpm_limit = headers.get('x-ratelimit-limit-tokens')
            self.rpm_limit = headers.get('x-ratelimit-limit-requests')
            self.tpm_remaining = headers.get('x-ratelimit-remaining-tokens')
            self.rpm_remaining = headers.get('x-ratelimit-remaining-requests')

# Register globally
rate_limit_tracker = RateLimitTracker()
litellm.callbacks = [rate_limit_tracker]

# Access in SimpleAgent
# limit_info = f"TPM: {rate_limit_tracker.tpm_remaining}/{rate_limit_tracker.tpm_limit}"
```

---

### Phase 3: Optimize Token Usage (High Priority)
**Timeline:** Complete within 1-2 days  
**Goal:** Reduce tokens per request to allow 3-4 calls per minute

#### 3.1 Condense System Prompt
**File:** `prompt_candidates/system_prompt.md`

**Reduce from 268 lines to ~100 lines:**
- Remove verbose examples (keep 1-2 representative examples)
- Condense framework description (keep rules, remove explanations)
- Merge redundant sections
- Use bullet points instead of paragraphs
- Remove repetitive reminders

**Estimated token reduction:** ~1,200 tokens saved (2,000 → 800)

#### 3.2 Implement Token Budget Tracking
**File:** `simple_agent/agents/simple_agent.py`

**Add token usage logging to understand consumption:**
```python
def run(self, task, reset=True):
    # Before call
    self.logger.info(f"Starting task with estimated {self._estimate_tokens(task)} tokens")
    
    response = self.agent.run(task, reset=reset)
    
    # After call - log actual usage (LiteLLM provides this)
    if hasattr(self.agent.model, 'last_completion'):
        usage = self.agent.model.last_completion.get('usage', {})
        self.logger.info(f"Token usage - Prompt: {usage.get('prompt_tokens')}, "
                        f"Completion: {usage.get('completion_tokens')}, "
                        f"Total: {usage.get('total_tokens')}")
```

**This helps:**
- Monitor actual token consumption per request
- Identify which requests are most expensive
- Track if optimizations are working

#### 3.3 Optimize Agent Context Management
**File:** `simple_agent/agents/simple_agent.py`

**Investigate Smolagents context options:**
- Check if Smolagents has max context length settings
- Consider truncating old messages after N turns
- Review if full conversation history is needed for each call

**Example (if Smolagents supports it):**
```python
agent = Agent(
    model=model,
    max_context_length=8000,  # Limit context window
    # OR
    max_history_messages=5,  # Keep only last 5 messages
)
```

---

### Phase 4: Reduce Debug Logging Verbosity (Medium Priority)
**Timeline:** Complete within 1 week  
**Goal:** Make logs readable and reduce size

#### 4.1 Disable LiteLLM Debug Logging
**File:** Logging configuration (e.g., `simple_agent/utils/logging.py`)

**Set LiteLLM to INFO level instead of DEBUG:**
```python
import logging

# Only show warnings/errors from these verbose libraries
logging.getLogger('LiteLLM').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('litellm').setLevel(logging.WARNING)

# Keep INFO for our own code
logging.getLogger('simple_agent').setLevel(logging.INFO)
```

**Alternative: Conditional Debug Logging**
```python
# Only enable debug when explicitly requested
if os.getenv('LITELLM_DEBUG', '').lower() == 'true':
    litellm.set_verbose = True
else:
    litellm.set_verbose = False
```

#### 4.2 Custom Exception Formatting
**File:** `simple_agent/agents/simple_agent.py`

**Catch and log concise error messages:**
```python
try:
    response = self.agent.run(task, reset=reset)
except AgentGenerationError as e:
    # Don't log full traceback for known errors
    if "RateLimitError" in str(e):
        self.logger.warning(f"Rate limit hit - retrying in 60s. Error: {e}")
        raise
    else:
        self.logger.error(f"Agent error: {e}", exc_info=True)
        raise
```

---

### Phase 5: Long-Term Optimizations (Future)
**Timeline:** As needed  
**Goal:** Scale to higher throughput

#### 5.1 Request Higher TPM Quota
**Action:** Contact Azure admin to increase deployment quota
- Current: 10,000 TPM
- Target: 50,000+ TPM (allows 5-10 requests/minute)

#### 5.2 Implement Prompt Caching (if supported)
**Check if Azure OpenAI supports prompt caching:**
- Cache static system prompt
- Only send variable parts (user query, context) in each request
- Potential 50-70% token reduction

#### 5.3 Use Smaller Model for Tool Selection
**Consider two-tier approach:**
- Small model (gpt-4o-mini) for tool selection and simple tasks
- Large model (gpt-4o) only for complex reasoning
- Reduces token usage for routine operations

#### 5.4 Implement Token Budget Management
**Add circuit breaker pattern:**
- Track TPM usage in-memory
- If approaching limit, queue requests
- Respect Azure's rate limit windows

---

## Implementation Order (Recommended)

### Day 1 (Today - Critical)
1. ✅ **Phase 1.1**: Mask Azure AD tokens in LiteLLM logging (security fix)
2. ✅ **Phase 1.2**: Add regex filter to catch any leaked JWTs (defense in depth)
3. ✅ **Phase 2.1**: Enable LiteLLM retry logic (use built-in, don't reinvent)
4. ⚠️ **Verification**: Test with current system prompt, confirm retries work

### Day 2 (High Priority)
5. ✅ **Phase 3.1**: Condense system prompt to ~100 lines
6. ✅ **Phase 3.2**: Add token usage tracking/logging
7. ⚠️ **Verification**: Measure token reduction, aim for 3-4 requests/minute

### Week 1 (Medium Priority)
8. ✅ **Phase 4.1**: Reduce logging verbosity to INFO/WARNING
9. ✅ **Phase 4.2**: Custom exception handling for rate limits
10. ✅ **Phase 3.3**: Optimize agent context management (if needed)

### Future (As Needed)
11. **Phase 5**: Request quota increase, investigate caching, multi-tier models

---

## Key Principles for Implementation

### 1. Leverage Existing Framework Features
- ✅ **DO:** Use LiteLLM's `num_retries` and built-in backoff
- ✅ **DO:** Use Python logging filters for sensitive data
- ❌ **DON'T:** Write custom retry logic from scratch
- ❌ **DON'T:** Modify LiteLLM/OpenAI library code directly

### 2. Security First
- Mask tokens BEFORE logging (in LiteLLM callback or logging filter)
- Use regex as backup to catch any leaks
- Verify logs are clean before moving to other fixes

### 3. Measure Everything
- Log token usage before and after optimizations
- Track retry frequency and success rate
- Monitor log file sizes

### 4. Minimal Code Changes
- Configure existing systems, don't rebuild them
- Use environment variables for toggles
- Keep changes in configuration files where possible

---

## Success Criteria

### Phase 1 (Security)
- [ ] No JWT tokens visible in `logs/app.log`
- [ ] Grep for "eyJ" returns only "REDACTED" entries
- [ ] No sensitive data in any log files

### Phase 2 (Retry Logic)
- [ ] 429 errors automatically retried (visible in logs)
- [ ] Agent waits 60s as specified by `Retry-After` header
- [ ] Multi-step tasks complete successfully despite rate limits

### Phase 3 (Token Optimization)
- [ ] System prompt reduced to <1,000 tokens
- [ ] Average request uses <4,000 total tokens
- [ ] 3-4 requests possible per minute (within 10K TPM limit)

### Phase 4 (Logging)
- [ ] Log files readable by humans
- [ ] Tracebacks limited to ERROR level
- [ ] Log file growth <10MB per hour

---

## Questions for Discussion

1. **LiteLLM Configuration Location**: Where is the LiteLLM client currently instantiated? Need to find the right file for retry config.

2. **Smolagents Integration**: Does Smolagents expose LiteLLM config, or should we configure LiteLLM globally?

3. **System Prompt Priority**: How much can we condense without losing domain-agnostic capability? Should we create a "lite" version?

4. **Logging Strategy**: Do we want separate log levels for different environments (dev=DEBUG, prod=INFO)?

5. **Azure Quota**: Should we request quota increase in parallel with optimization work?

6. **Token Budget**: Do we need hard limits/circuit breakers, or is retry logic sufficient?

---

## Files to Modify (Estimated)

1. `simple_agent/core/model_manager.py` - LiteLLM retry config + custom logger
2. `simple_agent/utils/logging.py` - Logging filters and levels
3. `simple_agent/agents/simple_agent.py` - Token tracking, exception handling
4. `prompt_candidates/system_prompt.md` - Condense to ~100 lines
5. `config.yaml` (or `.env`) - Add config flags for retry behavior

**No modifications to:**
- LiteLLM library code
- OpenAI library code
- Smolagents library code

---

## References

- [LiteLLM Retry Documentation](https://docs.litellm.ai/docs/completion/reliable_completions)
- [LiteLLM Custom Callbacks](https://docs.litellm.ai/docs/observability/custom_callback)
- [Azure OpenAI Rate Limits](https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits)
- [Python Logging Filters](https://docs.python.org/3/library/logging.html#filter-objects)

---

**Next Step:** Review plan and discuss questions above before implementation.
