# Token Size Management Specification - Simple Approach

## Overview
Protects agents from hitting OpenAI's 30,000 TPM rate limit through:
1. Token budget enforcement in config
2. Flexible HTML cleanup (reusable for future tools)
3. Token visibility in tool results
4. System prompt guidance

Keep it simple: agent learns what works by observing token costs.

## Problem Statement
- Web pages contain 20,000-50,000+ tokens when fetched
- SimpleAgent agents hit OpenAI's 30,000 TPM rate limit on research tasks
- No protection currently exists
- Agents have no way to adjust strategy based on token feedback

## Solution
Four simple protections:
1. **Config**: Token budget (hard limit on input size)
2. **Helper**: HTMLCleaner (reusable for web tools + future browser automation)
3. **Tool**: fetch_webpage_markdown with strip_level + truncation + token visibility
4. **Agent**: Token guard check before sending to LLM

## Design

### 0. Token Budget Configuration
**Location**: `config.yaml` and `config/agents/*.yaml`

Add token budget settings to control input size per request:

```yaml
# config.yaml
llm:
  openai:
    model: "gpt-4o"
    api_key: "${OPENAI_API_KEY}"
    temperature: 0.7
    max_tokens: 2000
    context_window: 128000       # NEW: Model's max context (reference)
    max_input_tokens: 25000      # NEW: Input budget (leaves ~5k buffer from 30k TPM)

agents:
  default:
    role: "You are a helpful AI assistant."
    max_steps: 10
    agent_type: "tool_calling"
    token_budget: 25000           # NEW: Max input tokens per request
    token_warning_threshold: 22000 # NEW: Warn when approaching limit

# config/agents/researcher.yaml
token_budget: 20000               # Override: tighter budget for token-sensitive agent
token_warning_threshold: 18000
```

**Purpose**:
- `token_budget`: Hard limit on input tokens (prevents rate limit errors)
- `token_warning_threshold`: Soft warning threshold (gives headroom)
- `max_input_tokens`: Provider-level configuration
- `context_window`: Reference for model capabilities

### 1. HTMLCleaner Helper (Reusable)
**Location**: `simple_agent/tools/helpers/html.py`

**Purpose**: Clean HTML by removing bloat, preserving content. Reusable for web tools and future browser automation.

**Signature**:
```python
class HTMLCleaner:
    def __init__(self, strip_level: str = "moderate"):
        # strip_level: "minimal" | "moderate" | "aggressive"
        pass

    def clean(self, html: str) -> tuple[str, dict]:
        """
        Returns: (markdown, stats)
        stats = {
            "original_size": bytes,
            "cleaned_size": bytes,
            "reduction_percent": float
        }
        """
```

**Strip Levels**:
- **minimal**: Remove only scripts, styles, svg, images
- **moderate**: + remove nav, footer, sidebars, comments
- **aggressive**: + remove forms, iframes, tracking, ads

**Preservation**:
- Always keep: main content, headings, tables, code blocks, links

**Basis**: Adapt from `agent-builder/tools/helpers/html.py` for proven techniques

---

### 2. Token Counter Helper
**Location**: `simple_agent/tools/helpers/token_counter.py`

**Simple**: Estimate tokens using character count

```python
def estimate_tokens(text: str) -> int:
    """Estimate tokens: ~1 token per 4 characters (conservative for gpt-4o)"""
    return len(text) // 4
```

---

### 3. Enhanced fetch_webpage_markdown Tool
**Location**: `simple_agent/tools/builtin/page_fetch.py`

**Signature**:
```python
@tool
def fetch_webpage_markdown(
    url: str,
    strip_level: str = "moderate",  # "minimal" | "moderate" | "aggressive"
    max_chars: int = 5000,          # Truncate to this size
) -> dict:
    """
    Fetch webpage and convert to markdown with configurable cleanup.

    Args:
        url: Webpage URL
        strip_level: How aggressively to remove bloat
        max_chars: Max characters to return (truncate if longer)

    Returns:
        {
            "success": bool,
            "data": str,              # Markdown (truncated if needed)
            "tokens_used": int,       # Estimated tokens in returned data
            "was_truncated": bool,    # True if exceeded max_chars
            "original_size": int,     # Size before truncation
            "message": str            # Status message
        }
    """
```

**Behavior**:
1. Fetch page using requests
2. Clean HTML using HTMLCleaner(strip_level)
3. Convert to markdown using html2text
4. Truncate to max_chars if needed
5. Estimate tokens in returned data
6. Return dict with tokens_used visible to agent

---

### 4. Agent Token Guard
**Location**: `simple_agent/agents/simple_agent.py` (in run method)

```python
def run(self, prompt: str, reset: bool = True) -> str:
    formatted_prompt = self._inject_rag_context(prompt)

    # NEW: Protect against oversized prompts
    estimated_tokens = estimate_tokens(formatted_prompt)

    if estimated_tokens > self.token_budget:
        raise ValueError(
            f"Prompt too large: {estimated_tokens} tokens "
            f"exceeds budget of {self.token_budget}"
        )

    if estimated_tokens > self.token_warning_threshold:
        logger.warning(
            f"Large prompt: {estimated_tokens}/{self.token_budget} tokens"
        )

    result = self.agent.run(formatted_prompt, reset=reset)
    return str(result)
```

**Effect**: Stops bad requests before hitting OpenAI rate limits

---

### 5. System Prompt Guidance (Optional but Recommended)

Help the agent make smart decisions by telling it upfront:

```yaml
# config/agents/researcher.yaml
role: |
  You are a research specialist.

  Token Budget: You have limited tokens. Be efficient.
  1. Use tavily_web_search first to find sources
  2. Look at search snippets - they often have the data you need
  3. Only fetch pages if search results aren't enough
  4. When fetching, use strip_level="aggressive" to keep size down

  Good example: Search → check snippets → fetch ONE detailed page
  Bad example: Fetch 10 pages one after another
```

**Why**: The agent will learn from `tokens_used` in tool results. The prompt just gives it a hint about the strategy.

---

### 8. Agent ReAct Adaptation Pattern Example

Agent learns and adapts from token feedback:
```
User: "Find top 5 Python frameworks by GitHub stars"

Step 1: tavily_web_search
  => Search "top Python frameworks github stars"
  <= Returns 5 promising links

Step 2: fetch_webpage_markdown (first link, default parameters)
  => URL: github.com/awesome-python
  <= tokens_used: 8500, is_chunked: True, chunks: 3
  <= Observation: "Page too large (8500 tokens), chunked. Need to request chunk by chunk or reduce cleanup."

Step 3: fetch_webpage_markdown (same URL, aggressive cleanup - LEARNED)
  => strip_level="aggressive", chunk_number=0
  <= tokens_used: 2100, is_chunked: True, chunks: 2
  <= Observation: "Better! Aggressive cleanup gives 2100 tokens. Found: Framework A: 50k stars, Framework B: 45k stars"

Step 4: fetch_webpage_markdown (second link, using aggressive - STRATEGY APPLIED)
  => strip_level="aggressive" (learned from step 3)
  <= tokens_used: 1900
  <= Observation: "Framework C: 42k stars, Framework D: 40k stars"

Step 5: [synthesis]
  => Compile top 5 and return
```

---

## Implementation Checklist

### Create (New Files)
- [ ] `simple_agent/tools/helpers/__init__.py`
- [ ] `simple_agent/tools/helpers/html.py` - HTMLCleaner (adapt from agent-builder)
- [ ] `simple_agent/tools/helpers/token_counter.py` - estimate_tokens()

### Modify (Existing Files)
- [ ] `simple_agent/tools/builtin/page_fetch.py` - Add strip_level + max_chars + tokens_used
- [ ] `simple_agent/agents/simple_agent.py` - Add token guard in run()
- [ ] `config.yaml` - Add token_budget, token_warning_threshold
- [ ] `config/agents/researcher.yaml` - Add system prompt guidance

### Test
- [ ] `tests/unit/test_html_cleaner.py` - Test strip_level="minimal"|"moderate"|"aggressive"
- [ ] `tests/unit/test_token_counter.py` - Test estimate_tokens()
- [ ] Manual: Run researcher agent, verify truncation + token_used visibility

**That's it. Simple and focused.**

---

## Example: Agent Observing Token Costs

```
User: "Find top 5 Python frameworks by GitHub stars"

Step 1: tavily_web_search(...)
  <= tokens_used: 800

Step 2: fetch_webpage_markdown(url, strip_level="moderate")
  <= tokens_used: 8500, was_truncated: True

Agent notices: Page was truncated. Next time try aggressive.

Step 3: fetch_webpage_markdown(url, strip_level="aggressive")
  <= tokens_used: 2100, was_truncated: False

Agent: "Much better! Aggressive works."

Step 4-5: [Synthesis with token budget respected]
Total: ~3,000-4,000 tokens ✅
```

---

## Configuration

**config.yaml**:
```yaml
agents:
  default:
    token_budget: 25000              # Hard limit
    token_warning_threshold: 22000   # Soft warning
```

**config/agents/researcher.yaml**:
```yaml
token_budget: 20000    # Override for researcher (tighter)
```

---

## Testing

Unit tests:
- HTMLCleaner with each strip_level
- Token counter accuracy
- Truncation behavior

Manual testing:
- `/agent run researcher "Find top 5 Python frameworks"`
- Observe token_used values in tool returns
- Check if truncation happened
- Verify token guard prevents oversized requests
