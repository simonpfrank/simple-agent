# Phase 1: Interactive & Inspection Features

**Status:** 🔴 Not Started
**Priority:** P1 - After Phase 0.5
**Estimated Effort:** 3-4 days

---

## Overview

Phase 1 adds interactive capabilities and inspection tools to enhance the user experience. This includes chat mode, prompt/response inspection, history viewing, and advanced configuration management.

**Goal:** Transform the REPL from command-driven to conversational while adding powerful inspection and configuration tools.

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
│   ├── python_executor.py  # From Phase 0.5
│   └── web_search.py       # Example
└── custom/
    ├── __init__.py
    └── my_tool.py          # User-defined
```

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

---

### 8. YAML Agent Definitions

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

### 10. Multi-Agent Sequential Flows

**Goal:** Chain agents in simple pipelines

**Example Use Case:**
1. Researcher agent gathers information
2. Summarizer agent creates summary
3. Writer agent drafts document

**Command:**
```bash
/agent flow research,summarize,write "Topic: AI Safety"
```

**Flow Definition (config.yaml):**
```yaml
flows:
  research_to_document:
    agents:
      - name: researcher
        role: "Gather information"
      - name: summarizer
        role: "Create summary"
      - name: writer
        role: "Draft document"

    # Pass output of each agent to next
    mode: "sequential"
```

**Implementation:**
```python
# simple_agent/core/flow_manager.py
class FlowManager:
    def run_flow(self, flow_name: str, initial_input: str):
        """Execute multi-agent flow."""
        pass
```

**Commands:**
- `/flow list` - List available flows
- `/flow run <name> <input>` - Execute flow
- `/flow create <name>` - Create new flow interactively

---

## Implementation Order

### Week 1: Foundation
**Day 1-2:**
- Interactive chat mode
- Prompt inspection commands
- Response inspection commands

**Day 3:**
- History command
- Basic memory implementation

### Week 2: Configuration & Tools
**Day 4:**
- Configurable paths
- REPL config overrides
- CLI argument overrides

**Day 5:**
- Jinja2 template variables
- Template rendering engine

### Week 3: Discovery & Flows
**Day 6:**
- Tool auto-discovery system
- Tool management commands

**Day 7:**
- YAML agent definitions
- Multi-agent sequential flows

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

## Acceptance Criteria

### Must Have
- [  ] Interactive chat mode working
- [  ] Prompt/response inspection commands
- [  ] History command with basic memory
- [  ] Configurable paths system
- [  ] REPL config overrides
- [  ] Tool auto-discovery working
- [  ] YAML agent definitions loading
- [  ] All tests passing (>90% coverage)

### Nice to Have
- [  ] Jinja2 template variables
- [  ] CLI argument overrides
- [  ] Tool hot-reload
- [  ] Multi-agent flows
- [  ] Memory persistence to disk

### Out of Scope (Phase 2)
- Human-in-the-loop approval
- Guardrails
- RAG with Chroma
- MCP tool integration

---

## Success Metrics

- ✅ Chat mode provides smooth conversation experience
- ✅ Inspection commands help with debugging
- ✅ Tool discovery works for custom tools
- ✅ Config override hierarchy works correctly
- ✅ Memory tracks conversation history
- ✅ YAML agents load automatically
- ✅ Documentation complete and clear

---

## Risk & Mitigation

### Risks

1. **Chat mode complexity**
   - Mitigation: Start simple, iterate
   - Keep exit logic clear and reliable

2. **Tool discovery performance**
   - Mitigation: Cache discovered tools
   - Lazy loading for large directories

3. **Memory leaks with conversation history**
   - Mitigation: Implement max_messages limit
   - Sliding window approach

4. **Jinja2 template security**
   - Mitigation: Use sandbox mode
   - Validate templates before rendering

---

## References

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [SmolAgents Tools Guide](https://huggingface.co/docs/smolagents/en/tutorials/tools)
- Python importlib for dynamic tool loading
- Watchdog for file system monitoring

---

## Notes

This phase significantly enhances user experience and debugging capabilities while maintaining the simple, clean architecture from Phase 0. All features are optional and can be enabled/disabled via configuration.

**Next Phase:** Phase 2 - Enhanced Features (Guardrails, RAG, MCP)
