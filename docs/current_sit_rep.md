# Situation Report: LLM Performance and Logging Issues
**Date:** 2025-11-12  
**Context:** Testing column understanding prompt with GPT model via Azure OpenAI

---

## Primary Issue: Extreme Latency (10+ minutes total)

### Observed Behavior:
1. **First LLM call:** ~4 minutes to receive response body (httpcore log)
2. **Second LLM call:** ~3 minutes (tool call or observation)
3. **Third LLM call:** ~4 minutes (final answer)

**Total: ~11 minutes for what should be a single-pass interpretation task**

### Hypothesis:

**Most Likely Cause: SmolAgents Multi-Step Tool Calling Loop**
- SmolAgents ToolCallingAgent is designed to iteratively call tools and refine responses
- The prompt asked for column interpretation (semantic understanding)
- SmolAgents may be interpreting this as requiring multiple tool calls
- Each iteration makes a full LLM API call (explaining the 3 separate ~4-minute calls)

**Why 4 minutes per call?**
- Large prompt size (system prompt ~460 lines + column metadata JSON)
- Azure OpenAI endpoint may have:
  - Rate limiting delays
  - Token processing overhead
  - Network latency (corporate proxy?)
- GPT-4o models are slower than GPT-4o-mini

**Why multiple calls?**
- SmolAgents may be trying to:
  1. First call: Parse input and plan approach
  2. Second call: Execute interpretation (tool call)
  3. Third call: Format final answer
- This is normal SmolAgents behavior when `max_steps > 1`

### Potential Solutions:
1. **Set max_steps=1** for single-pass tasks (no tool iteration needed)
2. **Use direct model call** instead of SmolAgents wrapper for non-tool tasks
3. **Reduce prompt size** (though 460 lines shouldn't cause 4-min delays)
4. **Test with GPT-4o-mini** to see if model choice affects latency
5. **Check Azure endpoint performance** (network, quotas, region)

---

## Secondary Issues: Logging Leaks and Console Spam

### Issue 2: LiteLLM Logging Azure AD Token
- **What:** LiteLLM debug logs contain full JWT tokens
- **Risk:** Credential exposure in log files
- **Hypothesis:** LiteLLM doesn't respect our SensitiveDataFilter when logging request details
- **Fix:** Need to suppress LiteLLM debug logs OR enhance regex patterns to catch more token formats

### Issue 3: Console Dumping Debug Logs with Tokens
- **What:** Console output shows debug logs with tokens repeated multiple times
- **Hypothesis:** Multiple loggers writing to console (root + library loggers)
- **Fix:** Console handler should be set to WARNING only, or third-party loggers need stricter filtering

### Issue 4: Full Prompts/Responses Logged in Debug Mode
- **What:** Debug mode logs entire prompts and LLM responses
- **Hypothesis:** This is intentional debug behavior but problematic for large prompts
- **Options:**
  - Truncate logged prompts/responses (show first/last N chars)
  - Add separate log level for "trace" (more verbose than debug)
  - Only log prompt/response when explicitly requested

### Issue 5: OpenAI Logging Error (Unicode Charmap)
- **What:** OpenAI client raises logging error when trying to log prompt with special characters (likely emoji/icons in prompt)
- **Hypothesis:** 
  - Prompt contains Unicode characters (✅ ⚠️ etc. in the system prompt)
  - OpenAI's logger uses ASCII codec or wrong encoding
  - Windows console/file encoding mismatch
- **Fix:** 
  - Remove icons from prompt
  - Set UTF-8 encoding for log file handler
  - Catch and suppress OpenAI logging errors

---

## Recommendations for Next Session:

1. **Immediate:** Test with `max_steps=1` to eliminate multi-call overhead
2. **Immediate:** Remove emoji/icons from system prompt (replace with text)
3. **Short-term:** Enhance logging filters to catch all token formats
4. **Short-term:** Set console handler to WARNING only (not DEBUG)
5. **Medium-term:** Consider direct model.generate() calls for non-tool tasks instead of SmolAgents
6. **Medium-term:** Investigate Azure endpoint performance (region, quotas, network path)

---

## Key Questions to Investigate:

- Is SmolAgents necessary for this task, or can we call the model directly?
- Can we disable tool calling mode for single-pass interpretation tasks?
- Is the Azure endpoint throttling us (rate limits)?
- Should we use GPT-4o-mini instead of GPT-4o for interpretation tasks?
- Can we set up proper UTF-8 encoding for all log handlers?

---

## Files Modified This Session:

- `simple_agent/tools/analyse_data.py` - Created comprehensive column metadata analyzer
- `prompt_candidates/system_prompt_2.md` - Created column understanding prompt (Step 1)
- `simple_agent/core/logging_filters.py` - Fixed to respect --debug flag (but still has token leaks)

**Status:** Logging fixes applied but incomplete. Primary latency issue unresolved.
