# Phase 1: Interactive & Inspection Features

**Status:** 🟡 In Progress (Phase 0.6 Complete - Debug Mode)
**Priority:** P1 - After Phase 0.5
**Estimated Effort:** 3-4 weeks (6 sub-phases)

---

## Overview

Phase 1 adds interactive capabilities, inspection tools, and tool management to enhance the user experience. This includes chat mode, prompt/response inspection, history viewing, tool management, and agent configuration.

**Goal:** Transform the REPL from command-driven to conversational while adding powerful inspection, tool management, and configuration tools.

**Phase 1 Sub-Phases:**
- **Phase 0.6:** ✅ Debug Mode (Completed)
- **Phase 1.1:** Interactive Chat & Inspection
- **Phase 1.2:** History & Memory
- **Phase 1.3:** Configuration Management
- **Phase 1.4:** Tool Management
- **Phase 1.5:** YAML Agent Definitions
- **Phase 1.6:** Tool Auto-Discovery

**Note:** Multi-agent flows moved to Phase 2 (complexity requires Phase 1 completion first)

---

## Phase 0.6: Debug Mode ✅ COMPLETED

**Goal:** Add debug infrastructure before Phase 1 complexity

### Features Implemented:

1. **Config-based debug setting** (`config.yaml`)
   - `debug.enabled: true/false`
   - Controls Python logging level and SmolAgents verbosity

2. **CLI flag override**
   - `--debug` / `--no-debug` or `-d` / `-nd`
   - CLI flag overrides config setting

3. **Python logging integration**
   - Debug mode → DEBUG level logging
   - Non-debug mode → INFO level logging

4. **SmolAgents verbosity mapping**
   - Debug enabled → `LogLevel.DEBUG` (verbose output)
   - Debug disabled → `LogLevel.INFO` (clean output)

5. **Debug logging statements**
   - Agent creation, model creation, agent execution
   - AgentManager lifecycle events

### Logging Behavior:
- **REPL mode:** Logs to file only
- **CLI mode:** Logs to file + console (WARNING+ level)
- **Debug mode:** Changes both Python logging and SmolAgents verbosity

### Testing:
- All 59 unit/integration tests passing
- Verified debug vs non-debug output
- Infrastructure ready for future display profiles

---

## Features

### 1. Interactive Chat Mode

**Command:** `/agent chat <name>`

**Behavior:**
- Enter chat mode with a specific agent
- Free text input without `/` prefix
- Continuous conversation until exit
- Exit with `/exit` or Ctrl+D

**Example:**
```
> /agent chat default
Entering chat mode with 'default'. Type '/exit' or press Ctrl+D to exit.

Chat> What is the capital of France?
Paris is the capital of France...

Chat> And what about Spain?
Madrid is the capital of Spain...

Chat> /exit
Exited chat mode.
```

**Implementation:**
- New chat loop in `app.py`
- Maintain conversation context
- Display clear mode indicators
- Graceful exit handling

---

### 2. Prompt Inspection Commands

**Commands:**
- `/prompt show` - Display the formatted prompt sent to LLM
- `/prompt raw` - Display raw prompt template before substitution

**Use Cases:**
- Debug prompt formatting issues
- Understand what the agent sees
- Verify template variable substitution
- Optimize prompt engineering

**Example:**
```
> /prompt show
╭─────────────────────────────────────────╮
│ Formatted Prompt (sent to LLM)         │
├─────────────────────────────────────────┤
│ System: You are a helpful AI assistant.│
│                                          │
│ User: What is the capital of France?   │
╰─────────────────────────────────────────╯

> /prompt raw
╭─────────────────────────────────────────╮
│ Raw Prompt Template                     │
├─────────────────────────────────────────┤
│ System: {{ role }}                      │
│                                          │
│ User: {{ user_input }}                  │
╰─────────────────────────────────────────╯
```

---

### 3. Response Inspection Commands

**Commands:**
- `/response show` - Display formatted LLM response
- `/response raw` - Display raw LLM response (JSON/full structure)

**Use Cases:**
- Debug response parsing issues
- See full LLM output including metadata
- Understand token usage and timing
- Analyze tool calls made by agent

**Example:**
```
> /response show
╭─────────────────────────────────────────╮
│ Agent Response                          │
├─────────────────────────────────────────┤
│ Paris is the capital of France.         │
│                                          │
│ Metadata:                               │
│   Tokens: 125 (prompt: 25, completion: 100)│
│   Duration: 1.2s                        │
│   Model: gpt-4o-mini                    │
╰─────────────────────────────────────────╯

> /response raw
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Paris is the capital of France."
    }
  }],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 100,
    "total_tokens": 125
  },
  "model": "gpt-4o-mini"
}
```

---

### 4. History Command

**Command:** `/history show [--limit N]`

**Behavior:**
- Display conversation history for current agent
- Show last N exchanges (default: 10)
- Include timestamps
- Optionally filter by agent name

**Requirements:**
- Requires memory implementation (see Memory section below)
- Persist across REPL restarts (optional)

**Example:**
```
> /history show --limit 3
╭─────────────────────────────────────────╮
│ Conversation History (last 3)          │
├─────────────────────────────────────────┤
│ [18:45:32] User: What is 2+2?          │
│ [18:45:33] Agent: 4                    │
│                                          │
│ [18:46:10] User: What is the capital?  │
│ [18:46:11] Agent: Paris                │
│                                          │
│ [18:47:02] User: Tell me a joke        │
│ [18:47:04] Agent: Why did the...       │
╰─────────────────────────────────────────╯
```

---

### 5. Configurable Paths & Override Hierarchy

**Goal:** Full control over configuration at every level

**Override Hierarchy:**
```
CLI args > REPL overrides > config.yaml > code defaults
```

**Features:**

#### 5.1 Configurable Paths

**Commands:**
- `/config set-path prompts <path>` - Set prompt template folder
- `/config set-path tools <path>` - Set tool folder
- `/config show-paths` - Display all configured paths

**Config:**
```yaml
paths:
  prompts: "config/prompts/"
  tools: "tools/"
  logs: "logs/"
  data: "data/"
```

#### 5.2 REPL Config Overrides

**Commands:**
- `/config set <key> <value>` - Set config value (already exists)
- `/config get <key>` - Get config value
- `/config save` - Save to config.yaml (already exists)
- `/config reset <key>` - Reset to default

**Example:**
```
> /config set llm.temperature 0.9
✓ Set llm.temperature = 0.9 (REPL override)

> /config get llm.temperature
llm.temperature = 0.9 (source: REPL override)

> /config save
✓ Configuration saved to: config.yaml

> /config reset llm.temperature
✓ Reset llm.temperature to default (0.7)
```

#### 5.3 CLI Argument Overrides

**Usage:**
```bash
# Override config values via CLI
python -m simple_agent.app \
  --config custom.yaml \
  --set llm.temperature=0.9 \
  --set agents.default.max_steps=20
```

---

### 6. Jinja2 Template Variables

**Goal:** Dynamic prompt substitution with variables

**Features:**
- Use Jinja2 in prompt templates
- Variables from config, context, user input
- Conditional blocks, loops
- Custom filters and functions

**Example Template:**
```yaml
# config/prompts/custom.yaml
name: "Custom Assistant"
system: |
  You are {{ agent_name }}, a {{ specialty }} assistant.

  {% if verbose %}
  Provide detailed explanations.
  {% else %}
  Keep responses concise.
  {% endif %}

  Current time: {{ current_time }}
  User context: {{ user_context }}

variables:
  agent_name: "Claude"
  specialty: "helpful"
  verbose: true
```

**Available Variables:**
- `{{ agent_name }}` - Agent name
- `{{ current_time }}` - Current timestamp
- `{{ user_name }}` - User name (from config)
- `{{ user_context }}` - User-provided context
- Custom variables from config

---

### 7. Tool Auto-Discovery System

**Goal:** Drop tools in directory, automatically register

**Features:**
- Scan `tools/` directory on startup
- Auto-register all Tool classes
- Hot-reload on file changes (optional)
- Validation and error reporting

**Directory Structure:**
```
tools/
├── __init__.py
├── builtin/
│   ├── __init__.py
│   ├── math_tool.py        # Simple math tool (Phase 1.6)
│   ├── python_executor.py  # Added in Phase 1.6 (after tool infrastructure)
│   └── web_search.py       # Example (future)
└── custom/
    ├── __init__.py
    └── my_tool.py          # User-defined
```

**Note:** Python executor tool will be built in Phase 1.6 after the tool infrastructure is in place. We'll start with a simple math tool for testing tool functionality.

**Tool File Format:**
```python
# tools/custom/my_tool.py
from smolagents import tool

@tool
def my_custom_tool(arg1: str, arg2: int) -> str:
    """
    Tool description here.

    Args:
        arg1: Description
        arg2: Description
    """
    return f"Result: {arg1} {arg2}"
```

**Auto-Registration:**
- Tools automatically available to agents
- Listed in `/tool list` command
- Configurable per agent in config.yaml

**Commands:**
- `/tool list` - List all available tools
- `/tool info <name>` - Show tool details
- `/tool reload` - Reload tools from disk
- `/tool add <agent_name> <tool_name>` - Add tool to agent
- `/tool remove <agent_name> <tool_name>` - Remove tool from agent
- `/tool enable <tool_name>` - Enable a tool globally
- `/tool disable <tool_name>` - Disable a tool globally

---

### 8. Tool Management for Agents

**Goal:** Add/remove tools from existing agents dynamically

**Commands:**
- `/agent tools <name>` - List tools attached to agent
- `/agent add-tool <agent_name> <tool_name>` - Add tool to agent
- `/agent remove-tool <agent_name> <tool_name>` - Remove tool from agent
- `/agent save <name>` - Save agent configuration (including tools) to YAML

**Example:**
```
> /agent create my_agent
✓ Created agent 'my_agent'

> /agent tools my_agent
Agent 'my_agent' tools: (none)

> /agent add-tool my_agent math_tool
✓ Added tool 'math_tool' to agent 'my_agent'

> /agent add-tool my_agent python_executor
✓ Added tool 'python_executor' to agent 'my_agent'

> /agent tools my_agent
Agent 'my_agent' tools:
  • math_tool
  • python_executor

> /agent save my_agent
✓ Saved agent 'my_agent' to config/agents/my_agent.yaml
```

**Implementation:**
- AgentManager maintains tool registry per agent
- Tools can be added/removed dynamically
- Save command persists agent configuration to YAML
- Loading agent from YAML automatically attaches tools

---

### 9. Interactive Agent Creation

**Goal:** Step-by-step prompting for creating agents

**Command:** `/agent create-interactive` or `/agent create --interactive`

**Example Session:**
```
> /agent create-interactive

╭──────────────────────────────────────╮
│   Interactive Agent Creation         │
╰──────────────────────────────────────╯

Agent name: my_researcher

Select LLM provider:
  1. OpenAI (gpt-4o-mini)
  2. Anthropic (claude-3-5-sonnet)
  3. Ollama (llama3.2:1b)
  4. Custom

Choice [1]: 1

Select agent type:
  1. Tool Calling (safe, default)
  2. Code Agent (requires Docker)

Choice [1]: 1

Agent role/persona (or template name): researcher

Add tools? [y/N]: y

Available tools:
  1. math_tool
  2. python_executor
  3. web_search

Select tools (comma-separated numbers) [1,2]: 1,3

Max steps [10]: 15

Verbosity (0=quiet, 1=normal, 2=verbose) [1]: 2

Save configuration? [Y/n]: y

✓ Created agent 'my_researcher'
✓ Saved to config/agents/my_researcher.yaml
```

**Implementation:**
- Use click.prompt() or prompt_toolkit for interactive prompts
- Validate inputs at each step
- Allow defaults for quick setup
- Option to save as YAML at the end

---

### 10. YAML Agent Definitions

**Goal:** Define agents in YAML files, not just config.yaml

**Directory Structure:**
```
config/agents/
├── default.yaml
├── researcher.yaml
├── coder.yaml
└── my_custom_agent.yaml
```

**Agent File Format:**
```yaml
# config/agents/researcher.yaml
name: "researcher"
agent_type: "tool_calling"
role: |
  You are a research specialist. You help users find accurate
  information and cite sources.

tools:
  - python_executor
  - web_search
  - document_reader

model:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.3
  max_tokens: 2000

settings:
  verbosity: 2
  max_steps: 15

metadata:
  description: "Research and information gathering specialist"
  author: "user"
  version: "1.0.0"
```

**Features:**
- Auto-load agents from `config/agents/` on startup
- Override with `/agent create` command
- Share agent definitions easily
- Version control agent configs

---

### 9. Basic Memory Implementation

**Goal:** Maintain conversation history per agent

**Features:**
- Store conversation history in memory
- Persist to disk (optional)
- Sliding window (keep last N messages)
- Clear history command

**Implementation:**
```python
# simple_agent/agents/memory.py
class AgentMemory:
    def __init__(self, max_history: int = 100):
        self.messages = []
        self.max_history = max_history

    def add_message(self, role: str, content: str):
        """Add message to history."""
        pass

    def get_history(self, limit: int = None):
        """Get conversation history."""
        pass

    def clear(self):
        """Clear all history."""
        pass

    def save(self, path: str):
        """Save to disk."""
        pass

    def load(self, path: str):
        """Load from disk."""
        pass
```

**Config:**
```yaml
agents:
  default:
    memory:
      enabled: true
      max_messages: 100
      persist: true
      persist_path: "data/memory/default.json"
```

**Commands:**
- `/history show` - Show history (implemented above)
- `/history clear` - Clear history
- `/history save <path>` - Export history
- `/history load <path>` - Import history

---

## Features Moved to Phase 2

### Multi-Agent Flows (MOVED TO PHASE 2)

**Reason:** Multi-agent flows require all Phase 1 infrastructure to be complete first:
- Tool management system (Phase 1.4)
- YAML agent definitions (Phase 1.5)
- Memory and history (Phase 1.2)
- Complex orchestration logic

**Deferred Features:**
- Sequential agent chaining
- Conditional routing
- Parallel execution
- Flow definitions in YAML
- Flow management commands

These will be implemented in Phase 2 with proper orchestration patterns and advanced agent coordination.

---

## Implementation Order (Sub-Phases)

### Phase 0.6: Debug Mode ✅ COMPLETED
- Config-based debug settings
- CLI debug flag
- Python logging and SmolAgents verbosity mapping
- Debug logging statements throughout codebase

### Phase 1.1: Interactive Chat & Inspection (Week 1)
**Days 1-3:**
- Interactive chat mode (`/agent chat`)
- Prompt inspection commands (`/prompt show`, `/prompt raw`)
- Response inspection commands (`/response show`, `/response raw`)
- Chat mode testing and refinement

### Phase 1.2: History & Memory (Week 2)
**Days 4-6:**
- Basic memory implementation (`AgentMemory` class)
- History command (`/history show`)
- History management (`/history clear`, `/history save`, `/history load`)
- Memory persistence (optional)

### Phase 1.3: Configuration Management (Week 3)
**Days 7-10:**
- Configurable paths system
- REPL config overrides (`/config set`, `/config get`, `/config reset`)
- CLI argument overrides (`--set` flag)
- Config save/load functionality
- Jinja2 template variables (optional)

### Phase 1.4: Tool Management (Week 4)
**Days 11-14:**
- Tool management commands (`/tool list`, `/tool info`)
- Agent tool commands (`/agent tools`, `/agent add-tool`, `/agent remove-tool`)
- Agent save command (`/agent save`)
- Tool loading from YAML
- Simple math tool for testing

### Phase 1.5: YAML Agent Definitions (Week 5)
**Days 15-17:**
- YAML agent definition format
- Auto-load agents from `config/agents/` directory
- Agent hierarchy (CLI > agent YAML > config.yaml > defaults)
- Interactive agent creation (`/agent create-interactive`)

### Phase 1.6: Tool Auto-Discovery (Week 6)
**Days 18-21:**
- Tool auto-discovery system (scan `tools/` directory)
- Tool validation and registration
- Python executor tool (with Docker) - AFTER tool infrastructure
- Tool reload command (`/tool reload`)
- Hot-reload support (optional)

---

## Testing Strategy

### Unit Tests
- Memory management (add, retrieve, clear, persist)
- Template rendering (Jinja2 substitution)
- Tool discovery (file scanning, registration)
- Flow execution (sequential chaining)

### Integration Tests
- Chat mode end-to-end
- Inspection commands with real agents
- Tool loading and execution
- Multi-agent flow execution

### Manual Testing
- REPL interaction testing
- Configuration override testing
- Tool auto-discovery testing
- Flow execution testing

---

## Dependencies

**New packages:**
```txt
jinja2>=3.1.0  # Template variables
watchdog>=3.0.0  # Tool hot-reload (optional)
```

---

## Configuration Changes

**config.yaml additions:**
```yaml
# Path configuration
paths:
  prompts: "config/prompts/"
  tools: "tools/"
  agents: "config/agents/"
  logs: "logs/"
  data: "data/"

# Memory settings
memory:
  enabled: true
  max_messages: 100
  persist: true
  persist_path: "data/memory/"

# Tool settings
tools:
  auto_discover: true
  scan_paths:
    - "tools/builtin/"
    - "tools/custom/"
  hot_reload: false

# Flow settings
flows:
  enabled: true
  definitions_path: "config/flows/"

# Template settings
templates:
  engine: "jinja2"
  auto_escape: false
```

---

## Agent Configuration Hierarchy

**Override Priority:** `CLI args > agent YAML > config.yaml > code defaults`

### 1. Code Defaults (Lowest Priority)
Hardcoded in `SimpleAgent` and `AgentManager`:
```python
# Default values if nothing else is specified
verbosity = 1
max_steps = 10
agent_type = "tool_calling"
```

### 2. config.yaml
Global defaults for all agents:
```yaml
agents:
  default:
    role: "You are a helpful AI assistant."
    verbosity: 1
    max_steps: 10
    agent_type: "tool_calling"
```

### 3. Agent YAML Files (config/agents/*.yaml)
Per-agent configuration:
```yaml
# config/agents/researcher.yaml
name: "researcher"
role: "You are a research specialist."
tools:
  - python_executor
  - web_search
model:
  provider: "openai"
  temperature: 0.3
settings:
  verbosity: 2
  max_steps: 15
```

### 4. CLI Arguments (Highest Priority)
Command-line overrides everything:
```bash
/agent create researcher --provider anthropic --max-steps 20
```

**Implementation:**
- AgentManager checks each level in order
- Higher priority values override lower ones
- Missing values fall through to next level
- All levels logged in debug mode

---

## Acceptance Criteria

### Phase 0.6: Debug Mode
- [✅] Config-based debug settings
- [✅] CLI debug flag (`--debug` / `--no-debug`)
- [✅] Python logging integration
- [✅] SmolAgents verbosity mapping
- [✅] All tests passing (59/59)

### Phase 1.1: Interactive Chat & Inspection
- [  ] Interactive chat mode working
- [  ] Prompt inspection commands
- [  ] Response inspection commands
- [  ] Chat mode exit handling
- [  ] Tests passing

### Phase 1.2: History & Memory
- [  ] Basic memory implementation
- [  ] History command working
- [  ] History management commands
- [  ] Memory persistence (optional)
- [  ] Tests passing

### Phase 1.3: Configuration Management
- [  ] Configurable paths system
- [  ] REPL config overrides
- [  ] Config save/load functionality
- [  ] CLI argument overrides (optional)
- [  ] Tests passing

### Phase 1.4: Tool Management
- [  ] Tool management commands
- [  ] Agent tool commands
- [  ] Agent save command
- [  ] Simple math tool implemented
- [  ] Tests passing

### Phase 1.5: YAML Agent Definitions
- [  ] YAML agent format defined
- [  ] Auto-load from config/agents/
- [  ] Agent hierarchy working
- [  ] Interactive agent creation
- [  ] Tests passing

### Phase 1.6: Tool Auto-Discovery
- [  ] Tool auto-discovery working
- [  ] Tool validation and registration
- [  ] Python executor tool (with Docker)
- [  ] Tool reload command
- [  ] Tests passing (>90% coverage)

### Out of Scope (Phase 2)
- Multi-agent flows (moved to Phase 2)
- Human-in-the-loop approval
- Guardrails
- RAG with Chroma
- MCP tool integration

---

## Success Metrics

### Phase 0.6: Debug Mode ✅
- ✅ Debug mode toggles verbose vs clean output
- ✅ CLI flag overrides config setting correctly
- ✅ SmolAgents verbosity maps to debug mode
- ✅ All tests passing

### Phase 1 Overall
- ✅ Chat mode provides smooth conversation experience (Phase 1.1)
- ✅ Inspection commands help with debugging (Phase 1.1)
- ✅ Memory tracks conversation history (Phase 1.2)
- ✅ Config override hierarchy works correctly (Phase 1.3)
- ✅ Tool management system functional (Phase 1.4)
- ✅ YAML agents load automatically (Phase 1.5)
- ✅ Tool discovery works for custom tools (Phase 1.6)
- ✅ Documentation complete and clear

---

## Risk & Mitigation

### Risks

1. **Chat mode complexity**
   - Mitigation: Start simple, iterate
   - Keep exit logic clear and reliable
   - Phase 1.1 focused implementation

2. **Tool discovery performance**
   - Mitigation: Cache discovered tools
   - Lazy loading for large directories
   - Addressed in Phase 1.6

3. **Memory leaks with conversation history**
   - Mitigation: Implement max_messages limit
   - Sliding window approach
   - Phase 1.2 includes memory management

4. **Agent hierarchy complexity**
   - Mitigation: Clear documentation
   - Debug logging at each level
   - Phase 1.5 includes comprehensive testing

5. **Tool security with Python executor**
   - Mitigation: Docker-only execution
   - Security validation from Phase 0.5
   - Built last in Phase 1.6

---

## References

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [SmolAgents Tools Guide](https://huggingface.co/docs/smolagents/en/tutorials/tools)
- [SmolAgents LogLevel Documentation](https://huggingface.co/docs/smolagents/en/api/monitoring)
- Python importlib for dynamic tool loading
- Watchdog for file system monitoring
- Click framework for CLI/REPL

---

## Document Metadata

**Version:** 2.0
**Date:** 2025-10-22
**Status:** In Progress - Phase 0.6 Complete
**Current Sub-Phase:** Phase 0.6 (Debug Mode) ✅ COMPLETED

**Change Log:**
- v2.0 (2025-10-22): Major restructure - Split into 6 sub-phases, added Phase 0.6 (debug mode), moved multi-agent flows to Phase 2, added tool management and interactive agent creation, added agent hierarchy documentation
- v1.0 (2025-10-21): Initial Phase 1 specification

---

## Notes

This phase significantly enhances user experience and debugging capabilities while maintaining the simple, clean architecture from Phase 0. The sub-phase structure allows for incremental development and testing.

**Key Changes from Original Plan:**
1. Added Phase 0.6 for debug infrastructure (completed)
2. Split into 6 manageable sub-phases
3. Moved multi-agent flows to Phase 2 (requires Phase 1 foundation)
4. Added tool management commands
5. Added interactive agent creation
6. Defined clear agent configuration hierarchy

All features are optional and can be enabled/disabled via configuration.

**Next Phase:** Phase 2 - Enhanced Features (Multi-Agent Flows, Guardrails, RAG, MCP)
