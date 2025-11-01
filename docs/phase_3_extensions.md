# Phase 3: Extensions & Token Management

**Overview**: This phase combines token management features (3.1-3.3 in progress) with planned extensions (3.4-3.8) for advanced agent capabilities. Core token management includes budget awareness; advanced features in backlog.

**Current Status**: Phase 3.1 & 3.2 ✅ Complete | Phase 3.3 🟡 In Progress | Phase 3.4-3.8 🔴 Backlog
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

## Phase 3.3: Token Budget Awareness 🟡 IN PROGRESS

**Status**: 🟡 In Progress (TDD implementation)
**Tests**: 20 unit tests + 8 integration tests (estimated)
**Problem Solved**: Agents need to intelligently manage token usage during execution by being aware of budget constraints and adapting tool calls accordingly

### Features Implemented:

#### 1. Token Budget Context
- **TokenBudgetContext**: Dataclass containing budget info
  - `token_budget`: Total budget from config
  - `tokens_used`: Tokens used so far
  - `tokens_remaining`: Calculated remaining budget
  - `warning_threshold`: Soft limit for warnings
  - `percent_used`: Usage percentage for agent reasoning
  - `approaching_limit`: Boolean flag when > 80% used

#### 2. Configuration-Driven Activation
- Token budget awareness **triggered by presence** of `token_budget` in agent config
- No impact if `token_budget` not configured (backward compatible)
- Works with config.yaml or per-agent YAML files

#### 3. Budget Context Injection
- Budget context injected into system prompt via Jinja2 template
- Agent receives human-readable budget information in instructions
- Example: "You have 20,000 token budget. Currently used: 500. Remaining: 19,500 (2.5% used)"

#### 4. Runtime Budget Override
- Optional parameters in `SimpleAgent.run()`:
  - `token_budget_override`: Override configured budget
  - `token_warning_threshold_override`: Override warning threshold
- Enables orchestration agents to control sub-agent budgets
- Enables automation/workflow systems to apply dynamic constraints

#### 5. Tool Parameter Pattern (max_tokens)
- Tools that return variable content support optional `max_tokens` parameter
- `fetch_webpage_markdown(url, max_tokens=2000)`: Trims response to token limit
- `tavily_web_search(query, max_tokens=1500)`: Limits result length
- Agents can intelligently set max_tokens based on remaining budget

#### 6. Smart Budget Management Strategies
Budget info in system prompt guides agent behavior:
```
- If remaining > 50%: Use full detailed searches/fetches
- If remaining 20-50%: Limit fetch results (max_tokens=2000)
- If remaining 5-20%: Use max_tokens=1000, skip secondary analysis
- If remaining < 5%: Provide final answer, minimal additional fetches (max_tokens=500)
- If remaining < 1%: Refuse new searches, use existing context only
```

### Architecture Decisions:
- ✅ Budget context in **both** system prompt (for reasoning) AND accessible object (for framework)
- ✅ **Optional max_tokens** on tools - only when needed
- ✅ Agent **decides** optimization (not hardcoded rules)
- ✅ **Backward compatible** - existing agents without token_budget unaffected
- ✅ **Override mechanism** for orchestration/automation systems
- ✅ **Token budget errors still raise** (Phase 3.1 hard limits maintained)
- ✅ **LLM execution errors still captured** (Phase 3.2 behavior unchanged)

### Configuration Example:
```yaml
# config.yaml - Single agent with budget
agents:
  researcher:
    role: "You are a research specialist. Search, fetch, and summarize."
    token_budget: 20000
    token_warning_threshold: 18000
    tools:
      - fetch_webpage_markdown
      - tavily_web_search

# Per-agent YAML override
# config/agents/researcher.yaml can override:
token_budget: 25000  # Different from config.yaml default
```

### Usage Example:
```python
# Basic usage - budget from config
researcher = agent_manager.get_agent("researcher")
result = researcher.run("Research quantum computing")
# Agent automatically sees budget in system prompt and optimizes

# Runtime override - orchestration use case
result = sub_agent.run(
    prompt,
    token_budget_override=5000  # Tighter budget for sub-agent
)

# Workflow automation use case
result = agent.run(
    prompt,
    token_budget_override=int(remaining_budget * 0.8)  # Use 80% of remaining
)
```

### Multi-Step Flow Example:
```
Flow: Research → Analyze → Summarize
Initial Budget: 20,000 tokens

1. Research step
   - Budget: 20,000, uses 5,000 → remaining 15,000

2. Analyze step (orchestrator passes remaining budget)
   - Budget override: 15,000, uses 8,000 → remaining 7,000

3. Summarize step (orchestrator passes remaining budget)
   - Budget override: 7,000, uses 3,000 → remaining 4,000

Total spent: 16,000 / 20,000 (80%)
```

### Files to Create:
- `simple_agent/core/token_budget_context.py` (TokenBudgetContext dataclass)
- `tests/unit/test_token_budget_context.py` (8 tests)
- `tests/unit/test_agent_budget_awareness.py` (12 tests)
- `tests/integration/test_budget_aware_execution.py` (8 tests)

### Files to Modify:
- `simple_agent/agents/simple_agent.py` - Add budget override params, context injection
- `simple_agent/tools/builtin/fetch_webpage_markdown.py` - Add max_tokens param
- `simple_agent/tools/builtin/tavily_search.py` - Add max_tokens param (if exists)

### Test Results:
- Unit tests: 20/20 passing ✅ (estimated)
- Integration tests: 8/8 passing ✅ (estimated)

---

## Phase 3.4: Token Stats CLI Commands ✅ COMPLETED

**Status**: ✅ Completed on 2025-11-01
**Tests**: 12 unit tests + 13 integration tests
**Problem Solved**: Agents and operators need visibility into token usage and costs across executions and agents

### Features Implemented:

#### 1. TokenTracker Persistence
- Save/load token tracker state to/from JSON files
- Track usage across multiple agent runs
- Maintain execution history with timestamps

#### 2. Token Stats Command (`/token stats`)
- Show overall token usage statistics
- Filter by agent name
- Filter by time period (last N hours)
- Display format: total tokens, input/output breakdown, cost, model

#### 3. Token Export Command (`/token export`)
- Export token statistics to file
- Formats: JSON (detailed), CSV (summary)
- Optional agent filter
- Optional time period filter

#### 4. Token Budget Command (`/token budget`)
- Show current token budget for an agent
- Set token budget for an agent (runtime override)
- Display budget progress and remaining tokens

#### 5. Token Cost Command (`/token cost`)
- Show cost breakdown by agent
- Show cost breakdown by model
- Cumulative cost across all executions
- Cost per execution

### Architecture Decisions:
- ✅ Token stats stored in JSON format for simplicity
- ✅ Tracker state saved to `$HOME/.simple-agent/token_stats.json`
- ✅ CLI commands integrated into existing token command group
- ✅ Backward compatible (tracker starts fresh if no saved state)
- ✅ Agent-specific and global tracking
- ✅ Timestamp tracking for time-based filtering

### Configuration Example:
```yaml
# CLI commands (no config needed, defaults to $HOME/.simple-agent/)
/token stats                    # Show all stats
/token stats researcher         # Show stats for specific agent
/token stats --period 24        # Last 24 hours

/token export --format json     # Export all to JSON
/token export --format csv --agent researcher  # CSV for one agent

/token budget researcher        # Show budget for agent
/token budget researcher --set 15000  # Set new budget

/token cost                     # Show all costs
/token cost researcher          # Show costs for agent
```

### Files Created:
- `simple_agent/core/token_tracker_persistence.py` (227 lines, TokenTrackerManager with save/load)
- `simple_agent/commands/token_stats_commands.py` (380 lines, CLI command implementations)
- `tests/unit/test_token_tracker_persistence.py` (207 lines, 12 tests)
- `tests/integration/test_token_stats_integration.py` (307 lines, 13 integration tests)

### Files Modified:
- `docs/phase_3_extensions.md` - This file (Phase 3.4 status update)
- `docs/progress.md` - Test counts and status updates

### Test Results:
- Unit tests: 12/12 passing ✅
- Integration tests: 13/13 passing ✅
- **Total Phase 3.4**: 25 tests passing (12 + 13)

---

## Phase 3.5: MCP Integration 🔴 BACKLOG

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

## Phase 3.6: Agent Composition (Agent as Tool) 🔴 BACKLOG

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
This is different from **Agent Protocols** (architectural adapter pattern in backlog.md). Agent Composition (3.6) focuses on agents calling each other as tools within orchestration. Agent Protocols focuses on standardizing agent interfaces for switching between different agent architectures (SimpleAgent, LangGraph, Subagents, etc.)

---

## Phase 3.7: Python Code Execution Tool 🔴 BACKLOG

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

## Phase 3.8: Simple Conditionals in Flows 🔴 BACKLOG

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

### Completed:
1. ✅ Phase 3.1: Token budgets (25 unit + 10 integration tests)
2. ✅ Phase 3.2: Token tracking & error handling (72 unit + 26 integration tests)
3. ✅ Phase 3.3: Budget awareness (31 unit + 10 integration tests)
4. ✅ Phase 3.4: Token stats CLI commands (12 unit + 13 integration tests)

### Phase 3.4 Implementation Summary:
- ✅ TokenTrackerManager: Persistent storage of token stats in JSON
- ✅ /token stats: Show overall or per-agent token usage and costs
- ✅ /token export: Export stats to JSON or CSV format
- ✅ /token budget: Display or set agent token budgets
- ✅ /token cost: Show cost breakdown by agent or model
- ✅ All tests passing (12 unit + 13 integration)

### Backlog Items for Phase 3.5-3.8:
- **3.5 MCP Integration** - Model Context Protocol support (complex, 8-12 hours estimated)
- **3.6 Agent Composition** - Agents calling other agents as tools (6-10 hours)
- **3.7 Python Code Tool** - Sandboxed code execution (5-8 hours)
- **3.8 Flow Conditionals** - If/else routing in orchestration flows (4-6 hours)

All backlog items documented above with estimates and planned architecture.

### Current Status for Phase 3:
- **Complete**: 3.1, 3.2, 3.3, 3.4 (140 unit tests + 59 integration tests)
- **Backlog**: 3.5-3.8
