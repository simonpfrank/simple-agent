# Phase 3: Extensions & Token Management

**Overview**: This phase combines token management features (3.1-3.2, completed) with planned extensions (3.3-3.7) for advanced agent capabilities. Mixed nature: core token management done; advanced features in backlog.

**Current Status**: Phase 3.1 & 3.2 ✅ Complete | Phase 3.3-3.7 🔴 Backlog
**Total Tests**: 512 unit tests passing (486 existing + 26 new error tracking)
**Latest Commits**:
- f4b487c: Error tracking enhancement
- 708c93e: Token tracking implementation

---

## Phase 3.1: Token Budget Protection ✅ COMPLETED

**Status**: ✅ Completed on 2025-11-01
**Tests**: 25 unit tests (14 token guard + 11 config) + 10 integration tests
**Problem Solved**: Prevent OpenAI 30,000 TPM rate limit hits on researcher agents with large prompts

### Features Implemented:
1. **Token Guard in SimpleAgent.run()**: Estimates prompt tokens BEFORE sending to LLM, rejects if exceeds budget
2. **System Role Inclusion**: Token count includes both system role + user prompt for accurate estimation
3. **Configuration Integration**: Token budgets configured in config.yaml and passed through AgentManager
4. **Warning Thresholds**: Soft warning when approaching token budget (hard limit still enforced)
5. **No Breaking Changes**: Feature is opt-in - agents without token_budget work as before

### Architecture Decisions:
- ✅ Token guard checks in SimpleAgent.run() BEFORE agent.agent.run() call
- ✅ System role included in token estimation for realistic counting
- ✅ Uses OpenAI's tiktoken library (cl100k_base encoding) for GPT-4 token counting
- ✅ Token budget is per-agent (different limits for different agents)
- ✅ Warning threshold is optional (only logs if set and exceeded)
- ✅ Backward compatible - agents without token_budget skip the guard
- ✅ Works with both ToolCallingAgent and CodeAgent (single guard point)

### Configuration Example:
```yaml
llm:
  provider: openai
  openai:
    model: gpt-4o-mini
    api_key: ${OPENAI_API_KEY}

agents:
  researcher:
    role: "You are a web research specialist..."
    token_budget: 20000        # Hard limit - reject prompts exceeding this
    token_warning_threshold: 18000  # Soft limit - log warning if exceeded
    tools:
      - fetch_webpage_markdown
      - tavily_web_search
```

### Files Created:
- `tests/unit/test_token_guard.py` (333 lines, 14 tests)
- `tests/unit/test_agent_config_tokens.py` (282 lines, 11 tests)
- `tests/integration/test_token_guard_integration.py` (312 lines, 10 tests)

### Files Modified:
- `simple_agent/agents/simple_agent.py` - Added token guard logic
- `simple_agent/core/agent_manager.py` - Config integration for token budgets

### Test Results:
- Unit tests: 25/25 passing ✅
- Integration tests: 10/10 passing ✅

---

## Phase 3.2: Advanced Token Management ✅ COMPLETED

**Status**: ✅ Completed on 2025-11-01 (includes error tracking enhancement)
**Tests**: 72 unit tests + 26 error tracking tests = 98 total new tests
**Architecture**: Token tracking with AgentResult wrapper, no breaking changes

### Features Implemented:

#### Token Tracking Infrastructure:
1. **TokenStats**: Input/output token tracking with total calculation
2. **StepTokenStats**: Per-agent stats including agent name
3. **FlowTokenStats**: Aggregates multiple steps
4. **TokenTracker**: Accumulates executions with stats

#### Model Pricing Database:
1. **OpenAI Pricing**: gpt-4o ($5/$15), gpt-4o-mini ($0.15/$0.60), gpt-3.5-turbo ($0.50/$1.50)
2. **Anthropic Pricing**: Claude models ($3-$15 range)
3. **Ollama Pricing**: Free local models
4. **Custom Pricing**: Override support

#### AgentResult Wrapper:
1. **Response + Metadata**: Contains response string + token stats + cost + model
2. **Error Tracking**: error and error_type fields for execution failures
3. **Backward Compatible**: __str__() returns response for existing code
4. **Serialization**: to_dict() includes error info with execution_halted flag

#### SimpleAgent Integration:
1. **Automatic Token Tracking**: Input and output tokens estimated automatically
2. **Cost Calculation**: Decimal-based for precision
3. **Error Capture**: LLM execution errors captured (not raised)
4. **Token Budget Errors Still Raise**: Hard limits maintained from Phase 3.1

### Architecture Decisions:
- ✅ AgentResult.__str__() for seamless backward compatibility
- ✅ Token tracking enabled by default, track_tokens=False option available
- ✅ Cost stored as Decimal for precision
- ✅ Model pricing centralized in ModelPricing singleton
- ✅ Token budget errors RAISE (hard limit)
- ✅ LLM execution errors CAPTURED (soft failure, returned in result)
- ✅ System role included in token estimation (consistent with 3.1)

### Configuration Example:
```yaml
agents:
  researcher:
    role: "You are a web research specialist..."
    model_provider: openai
    model_config:
      model: gpt-4o-mini
    token_budget: 20000

  summarizer:
    role: "You are a summarization expert..."
    model_provider: anthropic
    model_config:
      model: claude-3-5-sonnet

# Token tracking is automatic in all agents
# Results include: response, input_tokens, output_tokens, total_tokens, cost, model, error, error_type
```

### Result Object Example:
```python
result = agent.run("What is Python?")
# result is AgentResult with:
#   - result.response: str
#   - result.input_tokens: int
#   - result.output_tokens: int
#   - result.total_tokens: int (calculated)
#   - result.cost: Decimal
#   - result.model: str
#   - result.error: Optional[str]
#   - result.error_type: Optional[str]

# Backward compatible - works as string:
print(f"Agent said: {result}")  # Prints: Agent said: <response>
message = str(result)           # Gets response text
dict_data = result.to_dict()    # Serialize to dict
```

### Files Created:
- `simple_agent/tools/helpers/token_tracker.py` (150 lines)
- `simple_agent/tools/helpers/model_pricing.py` (100 lines)
- `simple_agent/core/agent_result.py` (130 lines)
- `tests/unit/test_token_tracker.py` (190 lines, 17 tests)
- `tests/unit/test_model_pricing.py` (160 lines, 14 tests)
- `tests/unit/test_agent_result.py` (200 lines, 15 tests)
- `tests/unit/test_agent_result_error_tracking.py` (220 lines, 16 tests)
- `tests/unit/test_simple_agent_token_tracking.py` (240 lines, 11 tests)
- `tests/unit/test_simple_agent_error_handling.py` (195 lines, 10 tests)

### Files Modified:
- `simple_agent/agents/simple_agent.py` - Token tracking + error handling
- `simple_agent/core/agent_result.py` - Error tracking fields

### Test Results:
- Unit tests: 72 new tests + 26 error tracking tests = 98 passing ✅
- Total project: 512/512 passing (486 existing + 26 new error tracking)

### Error Tracking Design:
- **Token budget errors**: RAISE ValueError (hard limit, prevents execution)
- **LLM execution errors**: CAPTURED in result (soft failure, allows handling)
- **Partial results**: Can capture partial response + token count on error
- **Execution halted flag**: to_dict() includes execution_halted: true when error occurs

---

## Phase 3.3: Token Stats CLI Commands 🔴 BACKLOG

**Status**: 🔴 Not Started
**Effort**: Estimated 4-6 hours

### Planned Features:
1. **`/token stats [agent] [--period last-N-hours]`**: Show token usage statistics
2. **`/token export [--format json|csv] [--agent name]`**: Export token stats to file
3. **`/token budget [agent] [--show|--set value]`**: View/set token budgets
4. **`/token cost [agent]`**: Show cost breakdown by model and agent

### Commands to Add:
- Simple CLI integration into existing `/token` command group
- Backend: TokenTracker persistence (save/load from JSON or database)
- Filtering: by agent, by time period, by model

### Tests Needed:
- Unit tests for CLI command parsing
- Integration tests with TokenTracker data

---

## Phase 3.4: MCP Integration 🔴 BACKLOG

**Status**: 🔴 Not Started
**Effort**: Estimated 8-12 hours

### Planned Features:
1. **MCP Server Support**: Register agent as MCP server for other clients
2. **MCP Client Support**: Call other MCP servers as tools
3. **Protocol Implementation**: Full Model Context Protocol support
4. **Tool Discovery**: Auto-discover MCP tools and expose as SimpleAgent tools

### Architecture:
- Adapter pattern for MCP protocol
- Tool conversion between MCP and SimpleAgent formats
- Config-based MCP server registration

### Dependencies:
- `mcp` library (add to requirements)
- Protocol implementation from MCP spec

---

## Phase 3.5: Agent Composition (Agent as Tool) 🔴 BACKLOG

**Status**: 🔴 Not Started
**Effort**: Estimated 6-10 hours

### Planned Features:
1. **Agent as Tool**: Expose agent as a callable tool for other agents
2. **Tool-based Composition**: Chain agents together via tool calls
3. **Context Injection**: Pass context and history between agent calls
4. **Error Handling**: Graceful failure handling in agent chains

### Architecture:
- SimpleAgent wrapper that exposes agent as callable
- Tool registration for inter-agent communication
- Context/memory flow between agents
- Timeout and error boundary management

### Note:
This is different from **Agent Protocols** (architectural adapter pattern in backlog.md). Agent Composition focuses on agents calling each other as tools within orchestration. Agent Protocols focuses on standardizing agent interfaces for switching between different agent architectures (SimpleAgent, LangGraph, Subagents, etc.)

---

## Phase 3.6: Python Code Execution Tool 🔴 BACKLOG

**Status**: 🔴 Not Started
**Effort**: Estimated 5-8 hours

### Planned Features:
1. **Safe Code Execution**: Execute Python code in sandboxed environment
2. **Code Input**: Accept code strings from LLM or user
3. **Output Capture**: Capture stdout, stderr, return values
4. **Import Management**: Control which imports are allowed
5. **Timeout/Resource Limits**: Prevent infinite loops and resource exhaustion

### Architecture:
- Subprocess-based execution (sandboxed)
- Whitelist for allowed imports
- Output capture and formatting
- Timeout handling

### Security Considerations:
- Code runs in separate process
- No access to parent process memory
- Whitelist for imports (no os, sys, etc. by default)
- Timeout prevents hanging code

---

## Phase 3.7: Simple Conditionals in Flows 🔴 BACKLOG

**Status**: 🔴 Not Started
**Effort**: Estimated 4-6 hours

### Planned Features:
1. **If/Else Routing**: Route execution based on conditions
2. **Condition Types**:
   - Exact match (result == "value")
   - Pattern match (result contains "pattern")
   - Threshold (cost > 10, tokens < 5000)
   - Custom function (lambda or function reference)
3. **Flow Integration**: Use conditions in orchestration flows
4. **Logging**: Track which condition path was taken

### YAML Example:
```yaml
flows:
  research:
    steps:
      - name: query
        agent: researcher
      - name: route
        type: conditional
        condition: "if_then_else"
        test: "query.cost > 1.00"
        then:
          - name: summarize
            agent: summarizer
        else:
          - name: skip
            agent: null  # Skip this step
```

### Architecture:
- Conditional executor in orchestration module
- Parser for condition syntax
- Integration with FlowExecutor from Phase 2.4

---

## Next Steps

### Immediate (if context is lost, start here):
1. ✅ Phase 3.1 & 3.2 are complete with 512 tests passing
2. ✅ Error tracking added (f4b487c commit)
3. ✅ This phase_3_extensions.md created
4. 🔴 Still need to create phase_4_raspberrypi.md
5. 🔴 Still need to create new simplified progress.md
6. 🔴 Still need to update README.md with examples

### Backlog Items for Phase 3.3-3.7:
- MCP (Model Context Protocol) - complex, requires protocol implementation
- Agent-to-Agent - requires composition system
- Python code tool - requires sandbox setup
- Simple conditionals - requires condition parser
- Token stats CLI - requires persistence layer

All backlog items documented above with estimates and planned architecture.
