# Simple Agent Template: Technical Specification

## Document Overview

This specification defines the technical architecture, component design, and implementation details for the Simple Agent Template. It translates the PRD requirements into concrete technical decisions and patterns.

**Related Documents:**
- PRD: `/docs/PRD.md`
- Progress Tracker: `/docs/Progress_Tracker.md` (to be created)

**Approach:** Build incrementally in phases, with clear functionality approval before each phase.

---

## Architecture Overview

### High-Level Design Principles

1. **Thin Interface Layer**: CLI/REPL contains zero business logic
2. **Core Business Logic**: All functionality in testable, reusable modules
3. **SmolAgents Wrapper**: Thin abstraction over SmolAgents for our needs
4. **Configuration-Driven**: YAML + .env (or repl/cli input) for all settings cli args override config
5. **Future-Proof**: Design enables easy API/MCP layer addition later

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Interface Layer                         │
│  (No Business Logic - Thin Wrappers Only)                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐        │
│  │   REPL      │  │    CLI      │  │  Future:     │        │
│  │  Commands   │  │  Commands   │  │  API/MCP     │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘        │
│         │                │                 │                 │
│         └────────────────┼─────────────────┘                 │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Business Logic                       │
│  (All Functionality - Testable & Reusable)                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  AgentManager    │  │  ConfigManager   │                │
│  │  - create()      │  │  - load()        │                │
│  │  - run()         │  │  - save()        │                │
│  │  - list()        │  │  - get()         │                │
│  └────────┬─────────┘  └────────┬─────────┘                │
│           │                     │                            │
│  ┌────────▼──────────────────────▼──────┐                  │
│  │       SimpleAgent (Wrapper)          │                  │
│  │  - Wraps SmolAgents CodeAgent        │                  │
│  │  - Manages memory, tools, RAG        │                  │
│  └────────┬─────────────────────────────┘                  │
│           │                                                  │
│  ┌────────▼─────────┐  ┌──────────┐  ┌──────────┐         │
│  │   SmolAgents     │  │  Tools   │  │   RAG    │         │
│  │   CodeAgent      │  │ Registry │  │ Processor│         │
│  └──────────────────┘  └──────────┘  └──────────┘         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
simple_agent/
├── __init__.py
├── app.py                      # REPL/CLI entry point (thin wrapper)
│
├── commands/                   # CLI/REPL command handlers (NO logic)
│   ├── __init__.py
│   ├── agent_commands.py       # /agent command group
│   ├── config_commands.py      # /config command group (future)
│   └── tool_commands.py        # /tool command group (future)
│
├── core/                       # Core business logic
│   ├── __init__.py
│   ├── config_manager.py       # Configuration loading/saving
│   ├── agent_manager.py        # Agent lifecycle management
│   └── logging_setup.py        # Reused from template
│
├── agents/                     # Agent implementation
│   ├── __init__.py
│   ├── simple_agent.py         # SmolAgents wrapper
│   ├── memory.py               # Memory management (future)
│   └── orchestrator.py         # Multi-agent flows (future)
│
├── tools/                      # Tool system
│   ├── __init__.py
│   ├── registry.py             # Tool auto-discovery (future)
│   └── builtin/                # Built-in tools (future)
│       └── __init__.py
│
├── rag/                        # RAG system (future)
│   ├── __init__.py
│   └── processor.py
│
├── ui/                         # UI utilities (reused from template)
│   ├── __init__.py
│   ├── welcome.py
│   ├── styles.py
│   └── completion.py
│
└── config/                     # Configuration files
    ├── defaults.yaml           # Default settings
    ├── prompts/                # Prompt templates (Phase 0)
    │   ├── default.yaml
    │   └── researcher.yaml
    └── agents/                 # Agent definitions (future)
        └── example.yaml

tests/
├── unit/                       # Unit tests with mocks
│   ├── test_config_manager.py
│   ├── test_agent_manager.py
│   └── test_simple_agent.py
│
├── integration/                # Integration tests
│   ├── test_agent_lifecycle_mocked.py    # With mocked LLM (CI/CD)
│   └── test_agent_lifecycle_live.py      # With real LLM (definitive)
│
└── data/                       # Test fixtures
    └── test_config.yaml

docs/
├── PRD.md                      # Product requirements
├── SPECIFICATION.md            # This file
└── Progress_Tracker.md         # Development tracking

config.yaml                     # Main config file
.env                           # API keys (gitignored)
requirements.txt               # Dependencies
```

---

## Phase 0: Foundation - Detailed Design

### Scope Reminder
- Install SmolAgents and basic dependencies
- Configuration system (YAML + .env)
- Prompt template system (static YAML in `config/prompts/`)
- Message formatting (system/user role separation)
- Simple agent wrapper with template support
- Basic REPL integration (`/agent create`, `/agent run`, `/agent list`)
- LLM support (OpenAI, Ollama, LM Studio)

### Component Specifications

#### 1. Configuration System

**File: `simple_agent/core/config_manager.py`**

```python
class ConfigManager:
    """Manages loading and accessing configuration."""

    @staticmethod
    def load(config_path: str) -> dict:
        """Load config from YAML file."""

    @staticmethod
    def load_env() -> dict:
        """Load environment variables from .env."""

    @staticmethod
    def get(config: dict, key_path: str, default=None):
        """Get nested config value using dot notation."""
        # e.g., get(config, "llm.openai.api_key")

    @staticmethod
    def merge_with_defaults(config: dict) -> dict:
        """Merge user config with defaults."""

    @staticmethod
    def load_prompt_template(template_name: str) -> dict:
        """Load prompt template from config/prompts/{template_name}.yaml"""
```

**Config File Structure: `config.yaml`**

```yaml
# Simple Agent Configuration

# LLM Provider Settings
llm:
  # Active provider: openai, ollama, anthropic
  provider: "openai"

  # OpenAI Configuration
  openai:
    model: "gpt-4o-mini"
    api_key: "${OPENAI_API_KEY}"  # References .env
    temperature: 0.7
    max_tokens: 2000

  # LM Studio Configuration (local)
  lmstudio:
    model: "llama3.2:1b"
    base_url: "http://localhost:11434"
    temperature: 0.7
    max_tokens: 2000

# Agent Settings
agents:
  # Default agent configuration
  default:
    role: "You are a helpful AI assistant."
    verbosity: 1  # 0=quiet, 1=normal, 2=verbose
    max_steps: 10  # Max tool call iterations

# Logging
logging:
  level: "INFO"
  file: "logs/app.log"
  console_enabled: false
```

**Environment File: `.env`**

```bash
# API Keys (never commit this file!)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Prompt Template Files: `config/prompts/*.yaml`**

```yaml
# config/prompts/default.yaml
name: default
system: |
  You are a helpful AI assistant.
  Answer questions clearly and concisely.
```

```yaml
# config/prompts/researcher.yaml
name: researcher
system: |
  You are a research assistant.
  Provide detailed, well-sourced answers.
  Cite your reasoning step by step.
  Focus on accuracy and thoroughness.
```

**Message Format (Standard OpenAI/Anthropic):**

```python
# Messages sent to LLM
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is AI?"}
]
```

#### 2. Simple Agent Wrapper

**File: `simple_agent/agents/simple_agent.py`**

```python
from smolagents import CodeAgent, LiteLLMModel

class SimpleAgent:
    """Thin wrapper around SmolAgents CodeAgent."""

    def __init__(
        self,
        name: str,
        model_provider: str,
        model_config: dict,
        role: str = None,
        template: str = None,
        tools: list = None,
        verbosity: int = 1,
        max_steps: int = 10
    ):
        """
        Initialize agent.

        Args:
            name: Agent identifier
            model_provider: "openai", "ollama", etc.
            model_config: Dict with model settings
            role: Optional system prompt/persona (overrides template)
            template: Optional template name to load from config/prompts/
            tools: List of tool instances
            verbosity: 0=quiet, 1=normal, 2=verbose
            max_steps: Max tool call iterations
        """
        self.name = name
        self.model_provider = model_provider

        # Load template if specified and no explicit role
        if template and not role:
            from simple_agent.core.config_manager import ConfigManager
            template_data = ConfigManager.load_prompt_template(template)
            role = template_data.get("system", "")

        self.role = role

        # Create LiteLLM model instance
        self.model = self._create_model(model_provider, model_config)

        # Create SmolAgents CodeAgent
        self.agent = CodeAgent(
            tools=tools or [],
            model=self.model,
            max_steps=max_steps,
            verbosity_level=verbosity,
            system_prompt=role
        )

    def _create_model(self, provider: str, config: dict) -> LiteLLMModel:
        """Create LiteLLM model instance based on provider."""
        # Implementation handles OpenAI, Ollama, etc.

    def run(self, prompt: str) -> str:
        """
        Execute prompt through agent.

        Args:
            prompt: User input

        Returns:
            Agent response string
        """
        result = self.agent.run(prompt)
        return str(result)

    def __repr__(self):
        return f"SimpleAgent(name='{self.name}', provider='{self.model_provider}')"
```

#### 3. Agent Manager

**File: `simple_agent/core/agent_manager.py`**

```python
from typing import Dict
from simple_agent.agents.simple_agent import SimpleAgent

class AgentManager:
    """Manages agent lifecycle (create, store, retrieve, run)."""

    def __init__(self, config: dict):
        """
        Initialize agent manager.

        Args:
            config: Application configuration dict
        """
        self.config = config
        self.agents: Dict[str, SimpleAgent] = {}

    def create_agent(
        self,
        name: str,
        provider: str = None,
        role: str = None
    ) -> SimpleAgent:
        """
        Create and register a new agent.

        Args:
            name: Agent identifier
            provider: LLM provider (defaults to config)
            role: Agent role/persona (defaults to config)

        Returns:
            Created SimpleAgent instance
        """
        # Get defaults from config if not specified
        provider = provider or self.config.get("llm", {}).get("provider")
        role = role or self.config.get("agents", {}).get("default", {}).get("role")

        # Get model config for provider
        model_config = self.config.get("llm", {}).get(provider, {})

        # Create agent
        agent = SimpleAgent(
            name=name,
            model_provider=provider,
            model_config=model_config,
            role=role,
            verbosity=self.config.get("agents", {}).get("default", {}).get("verbosity", 1),
            max_steps=self.config.get("agents", {}).get("default", {}).get("max_steps", 10)
        )

        # Register
        self.agents[name] = agent
        return agent

    def get_agent(self, name: str) -> SimpleAgent:
        """
        Retrieve agent by name.

        Args:
            name: Agent identifier

        Returns:
            SimpleAgent instance

        Raises:
            KeyError: If agent doesn't exist
        """
        if name not in self.agents:
            raise KeyError(f"Agent '{name}' not found. Available: {list(self.agents.keys())}")
        return self.agents[name]

    def list_agents(self) -> list[str]:
        """Return list of registered agent names."""
        return list(self.agents.keys())

    def run_agent(self, name: str, prompt: str) -> str:
        """
        Run prompt through specified agent.

        Args:
            name: Agent identifier
            prompt: User input

        Returns:
            Agent response string
        """
        agent = self.get_agent(name)
        return agent.run(prompt)
```

#### 4. REPL Command Integration

**File: `simple_agent/commands/agent_commands.py`**

```python
import click
from rich.console import Console

@click.group()
@click.pass_context
def agent(ctx):
    """Agent management commands."""
    pass

@agent.command()
@click.argument("name")
@click.option("--provider", "-p", default=None, help="LLM provider")
@click.option("--template", "-t", default=None, help="Prompt template name")
@click.option("--role", "-r", default=None, help="Agent role/persona (overrides template)")
@click.pass_context
def create(ctx, name: str, provider: str, template: str, role: str):
    """Create a new agent."""
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    try:
        # Business logic in agent_manager, not here
        agent = agent_manager.create_agent(name, provider, template, role)
        console.print(f"[green]✓[/green] Created agent: {agent}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")

@agent.command()
@click.argument("name")
@click.argument("prompt")
@click.pass_context
def run(ctx, name: str, prompt: str):
    """Run a prompt through an agent."""
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    try:
        # Business logic in agent_manager, not here
        response = agent_manager.run_agent(name, prompt)
        console.print(f"\n[bold cyan]Response:[/bold cyan]\n{response}\n")
    except KeyError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")

@agent.command(name="list")
@click.pass_context
def list_agents(ctx):
    """List all registered agents."""
    console: Console = ctx.obj["console"]
    agent_manager = ctx.obj["agent_manager"]

    agents = agent_manager.list_agents()
    if agents:
        console.print("[bold]Registered Agents:[/bold]")
        for agent_name in agents:
            console.print(f"  • {agent_name}")
    else:
        console.print("[dim]No agents registered yet.[/dim]")
```

**File: `simple_agent/app.py` (Modified)**

```python
# Add to imports
from simple_agent.core.agent_manager import AgentManager
from simple_agent.commands.agent_commands import agent

# In cli() function, after loading config:
@click.group(invoke_without_command=True)
@click.option("--config", "-c", default="config.yaml", help="Path to config file")
@click.option("--repl-mode", is_flag=True, default=False, help="Start in REPL mode")
@click.pass_context
def cli(context, config, repl_mode):
    """Simple Agent CLI/REPL."""

    # ... existing config loading ...

    # Initialize AgentManager (business logic)
    agent_manager = AgentManager(config_dict)
    context.obj["agent_manager"] = agent_manager

    # ... rest of existing code ...

# Register agent command group
cli.add_command(agent, name="agent")
```

---

## Phase 0: Dependencies

**File: `requirements.txt`**

```txt
# Core dependencies (from template)
click>=8.1.0,<8.2.0
click-repl>=0.3.0
rich>=13.0.0
prompt-toolkit>=3.0.0
PyYAML>=6.0.0

# Agent framework
smolagents>=0.1.0
litellm>=1.0.0

# Environment variables
python-dotenv>=1.0.0

# Testing (existing)
pytest>=7.0.0
pytest-cov>=4.0.0
```

---

## Phase 0: Testing Strategy

### Unit Tests

**File: `tests/unit/test_config_manager.py`**
- Test YAML loading
- Test .env loading
- Test nested key access with dot notation
- Test merge with defaults

**File: `tests/unit/test_agent_manager.py`**
- Test agent creation with mocked SimpleAgent
- Test agent retrieval
- Test agent listing
- Test error handling (agent not found)

**File: `tests/unit/test_simple_agent.py`**
- Test initialization
- Test model creation for different providers (mocked)
- Test run method (mocked SmolAgents response)

### Integration Tests

**File: `tests/integration/test_agent_lifecycle.py`**
- Test full flow: load config → create agent → run prompt
- Test with real LM Studio (if available) 
- Verify response structure

### REPL Testing (Manual)

```bash
# Start REPL
python -m simple_agent.app

# Test sequence
> /agent create test
> /agent list
> /agent run test "What is 2+2?"
> /exit
```

---

## Phase 0: Success Criteria

- [ ] Configuration loads from `config.yaml` and `.env`
- [ ] Prompt templates load from `config/prompts/`
- [ ] Can create agent with OpenAI, Ollama, or LM Studio
- [ ] Can create agent with template or explicit role
- [ ] Can run prompt through agent and get LLM response
- [ ] Messages formatted correctly (system/user roles)
- [ ] All unit tests pass (with mocks)
- [ ] Integration test passes (mocked and live versions)
- [ ] Manual REPL test successful
- [ ] Code follows CLAUDE.md standards (< 100 lines/class, type hints, etc.)

---

## Future Phases (Brief Overview)

### Phase 1: Interactive & Inspection Features
- **Interactive chat mode**: `/agent chat <name>` command
  - Enter chat mode with specific agent
  - Free text input without `/` prefix
  - Exit with `/exit` or Ctrl+D
- **Prompt inspection commands**: `/prompt show`, `/prompt raw`
- **Response inspection commands**: `/response show`, `/response raw`
- **History command**: `/history show` (requires memory)
- **Jinja2 template variables**: Dynamic prompt substitution
- **Tool auto-discovery system**: Drop tools in directory, auto-register
- **YAML agent definitions**: Per-agent config files
- **Basic memory**: Conversation history retention
- **Multi-agent sequential flows**: Chain agents in simple pipelines

### Phase 2: Enhanced Features
- Human-in-the-loop approval wrapper
- Simple guardrails wrapper
- RAG with Chroma
- MCP tool integration

### Phase 3: Advanced Features
- ReACT pattern optimization
- Multi-agent conditional routing
- Advanced memory strategies
- Tool composition and chaining

### Phase 4: Raspberry Pi
- Pi deployment optimization
- Voice I/O
- GPIO tools

---

## Design Decisions & Rationale

### Why SmolAgents CodeAgent?
- **Code-first**: Agents write actions in Python (30% more efficient than JSON)
- **Minimal**: ~1,000 lines, easy to understand and debug
- **Flexible**: Works with any LLM via LiteLLM

### Why LiteLLM?
- **Universal**: One interface for OpenAI, Anthropic, Ollama, etc.
- **Battle-tested**: Used in production by many projects
- **Simple**: No complex configuration

### Why Thin Wrapper Pattern?
- **Flexibility**: Easy to swap SmolAgents for something else later
- **Control**: Add our features (memory, RAG, HITL) without forking
- **Testability**: Can mock SmolAgents for unit tests

### Why AgentManager?
- **Separation**: Business logic separate from CLI/REPL
- **Reusability**: Can be used by future API/MCP layer
- **Testability**: Easy to unit test without CLI

### Why Click Commands?
- **Consistency**: Already using Click in template
- **Familiar**: Standard Python CLI framework
- **Extensible**: Easy to add new command groups

---

## Non-Functional Requirements

### Performance
- Agent creation: < 1 second
- Prompt response: Depends on LLM (not our concern)
- Config loading: < 100ms

### Code Quality
- All classes < 100 lines (per CLAUDE.md)
- Type hints on all public methods
- Google-style docstrings
- Lint clean: `ruff check simple_agent/`

### Testing
- Unit test coverage: > 80%
- All tests pass before phase completion
- Integration tests use real LLMs when available

### Documentation
- Inline comments explain "why", not "what"
- README with quick start guide (future)
- This specification kept up-to-date

---

## Risk Mitigation

### Risk: SmolAgents API Breaking Changes
**Mitigation**: Pin version in requirements.txt, thin wrapper isolates changes

### Risk: LiteLLM Provider Issues
**Mitigation**: Graceful error handling, clear error messages, fallback to direct API calls if needed

### Risk: Config Complexity
**Mitigation**: Defaults for everything, minimal required config

---

## Next Steps

1. **Get Specification Approval** from stakeholder (you!)
2. **Create Progress Tracker** in `docs/Progress_Tracker.md`
3. **Begin Phase 0 Implementation** with TDD:
   - Write failing tests for ConfigManager
   - Implement ConfigManager
   - Write failing tests for SimpleAgent
   - Implement SimpleAgent
   - Write failing tests for AgentManager
   - Implement AgentManager
   - Add REPL commands
   - Integration test
   - Manual REPL test

---

**Version**: 1.0
**Date**: 2025-10-20
**Status**: Draft - Awaiting Approval
**Phase**: 0 (Foundation)
