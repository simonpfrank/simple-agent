# Simple Agent

A lightweight agent framework built on SmolAgents for rapid experimentation with LLMs. Define agents in YAML, drop in tools, add guardrails. No boilerplate.

## Features

- **Agent Creation**: Define agents in YAML or Python, swap LLM providers instantly
- **Tool Management**: Built-in calculator tools, custom tools via Python decorators
- **Guardrails**: Input validation with PII detection and custom rule support
- **Interactive Chat**: Chat mode with conversation history and memory management
- **Memory Management**: Track agent interactions, save/load history via SmolAgents
- **Agent Inspection**: View prompts, responses, execution history
- **YAML Agent Definitions**: Persist agent configs with full YAML support
- **Jinja2 Templates**: Dynamic prompts with variables, conditionals, loops, filters
- **Token Budget Protection**: Hard limits to prevent rate limit hits (prevents 30K TPM overages)
- **RAG Foundation**: Chroma-based document collections with semantic search
- **Multi-Agent Orchestration**: Orchestrator pattern for agent workflows with ReAct iteration
- **REPL Interface**: Interactive CLI for agent management and execution

## Installation

```bash
git clone https://github.com/yourusername/simple-agent.git
cd simple-agent
pip install -r requirements.txt
```

**Requirements:**
- Python 3.11+
- smolagents, litellm, pyyaml, click, click-repl, rich

## Quick Start

Create and run an agent:

```bash
python simple_agent/repl.py
```

In the REPL:

```
> /agent create researcher --role "You are a research assistant"
> /agent run researcher "What is quantum computing?"
> /agent chat researcher
```

## CLI Reference

### Agent Commands

```
/agent create <name> --role "description" [--model <model>] [--provider <provider>]
Create a new agent

/agent run <name> "prompt"
Run agent and get response

/agent chat <name>
Interactive chat mode with agent (type 'exit' to quit)

/agent list
List all agents

/agent save <name> [--path <path>]
Save agent config to YAML

/agent create-wizard
Step-by-step agent creation with optional YAML save

/agent tools <name>
List guardrails on agent

/agent add-tool <name> <tool>
Add tool to agent

/agent remove-tool <name> <tool>
Remove tool from agent
```

### Tool Commands

```
/tool list
List all available tools

/tool info --name <tool>
Show tool description and parameters
```

### Guardrail Commands

```
/guardrail test <guardrail_type> "sample text"
Test guardrail on sample input

/guardrail list <agent_name>
List guardrails attached to agent

/guardrail add <agent_name> --type <type> [--options]
Add guardrail to agent

/guardrail remove <agent_name> <index>
Remove guardrail from agent
```

### Config Commands

```
/config show [--resolve]
Display current config (--resolve shows actual values instead of ${VAR})

/config get <key>
Get specific config value

/config set <key> <value>
Set config value

/config reset <key>
Reset config value to default

/config set-path <type> <path>
Set path (agents, tools, data, logs, prompts)

/config show-paths
Show all configured paths

/config load <file>
Load config from file

/config save [--file <file>]
Save current config to file
```

### History Commands

```
/history show [--limit N]
Show conversation history (N most recent, default 10)

/history clear
Clear all conversation history

/history save <file>
Export conversation history to JSON
```

### Collection Commands (RAG)

```
/collection create <name> [--embedding <model>] [--chunk-size N] [--overlap N]
Create a new document collection with optional custom settings

/collection list
List all available collections

/collection info <name>
Show detailed collection statistics

/collection delete <name>
Delete a collection

/collection connect <name> <agent_name>
Connect agent to collection for RAG context injection

/collection disconnect <agent_name>
Disconnect agent from collection
```

### Flow Commands (Orchestration)

```
/flow list
List all available workflows

/flow show <name>
Display workflow definition

/flow run <name> <input>
Execute workflow and get result

/flow delete <name>
Delete a workflow

/flow debug <name> <input>
Debug workflow execution with detailed output
```

### Utility Commands

```
/debug [level]
Toggle debug mode (0=off, 1=info, 2=debug)

/help
Show available commands

/exit
Exit REPL
```

## Examples

### Basic Agent

```python
from simple_agent.core.agent_manager import AgentManager
from simple_agent.core.config_manager import ConfigManager

config = ConfigManager.load_env()
agent_mgr = AgentManager(config)

agent = agent_mgr.create_agent(
    name="assistant",
    role="You are a helpful assistant",
    model_provider="openai"
)

response = agent.run("What is 2 + 2?")
print(response)
```

### Agent with Guardrails

```python
from simple_agent.guardrails import PIIDetector, GuardrailAgent

# Protect against PII in inputs
pii_detector = PIIDetector(types=["email", "ssn"], redact=True)
guarded_agent = GuardrailAgent(agent, input_guardrails=[pii_detector])

# PII will be redacted before sending to LLM
response = guarded_agent.run("My email is john@example.com")
```

### Custom Validation Rules

```python
from simple_agent.guardrails import CustomRuleGuardrail

def no_sql_injection(text):
    if "DROP TABLE" in text.upper():
        from simple_agent.guardrails import GuardrailViolation
        raise GuardrailViolation("SQL injection detected")
    return text

rule = CustomRuleGuardrail(no_sql_injection)
agent_with_rules = GuardrailAgent(agent, input_guardrails=[rule])
```

### YAML Agent Definition

Create `config/agents/researcher.yaml`:

```yaml
name: "researcher"
role: "You are a research expert with access to tools"
model:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.3
guardrails:
  input:
    - type: "pii_detector"
      redact: true
      types: ["email", "phone"]
tools:
  - add
  - subtract
```

Load and use:

```python
agent = agent_mgr.load_agent_from_yaml("config/agents/researcher.yaml")
response = agent.run("Add 5 + 3")
```

### Chat Mode

Interactive multi-turn conversation:

```bash
> /agent chat researcher
researcher> What is AI?
assistant> [response...]
researcher> Tell me more about machine learning
assistant> [response...]
researcher> exit
```

### Token Budget Protection

Prevent rate limit hits by setting hard limits on prompt size:

```python
agent = agent_mgr.create_agent(
    name="researcher",
    role="You are a research specialist",
    token_budget=20000,              # Hard limit - reject prompts exceeding this
    token_warning_threshold=18000,   # Soft limit - log warning when exceeded
)

# Prompt with 25K tokens will raise ValueError
try:
    response = agent.run("very long prompt...")
except ValueError as e:
    print(f"Token budget exceeded: {e}")
    # Implement retry logic or use different agent
```

Or configure in YAML:

```yaml
agents:
  researcher:
    role: "You are a research specialist..."
    token_budget: 20000
    token_warning_threshold: 18000
    tools:
      - fetch_webpage_markdown
      - tavily_web_search
```

**How It Works:**
- Token count includes system role + user prompt (not just prompt)
- Uses OpenAI's tiktoken for accurate GPT-4 token estimation
- Guards prompt BEFORE sending to LLM to prevent rate limit hits
- Prevents 30K TPM overages on OpenAI's API

### RAG Foundation

Create and query document collections with semantic search:

```python
from simple_agent.rag import CollectionManager

collection_mgr = CollectionManager()

# Create a collection
collection = collection_mgr.create_collection(
    name="knowledge_base",
    embedding_model="openai",
    chunk_size=1000,
    overlap=200
)

# Add documents
collection.add_documents(["document1.txt", "document2.md"])

# Connect to agent for automatic RAG context injection
agent.set_rag_collection(collection)

# Agent will automatically retrieve and inject relevant context
response = agent.run("What is mentioned in the documents?")
```

Or use the CLI:

```bash
> /collection create knowledge --embedding openai
> /collection connect knowledge researcher
> /agent run researcher "What is in the documents?"
# Agent automatically retrieves and includes relevant context
```

### Multi-Agent Orchestration

Define complex workflows with multiple agents:

```yaml
# config/flows/research_workflow.yaml
name: "research_flow"
agents:
  - name: "planner"
    role: "You plan research tasks"
  - name: "researcher"
    role: "You perform web research"
  - name: "summarizer"
    role: "You summarize findings"

workflow:
  - step: 1
    agent: "planner"
    task: "Create research plan"
  - step: 2
    agent: "researcher"
    task: "Execute research based on plan"
  - step: 3
    agent: "summarizer"
    task: "Summarize and organize findings"
```

Execute the workflow:

```bash
> /flow list
> /flow run research_flow "Investigate AI trends in 2024"
```

Or in Python:

```python
flow_mgr = FlowManager(agent_mgr)
result = flow_mgr.run_flow("research_flow", "Investigate AI trends")
```

### Agent Inspection

```bash
> /prompt show              # Show last prompt sent to LLM
> /response show            # Show last response from LLM
> /history show --limit 5   # Show last 5 interactions
> /history save history.json # Export conversation history
```

### Custom Tools

Create `tools/my_tools.py`:

```python
from smolagents import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@tool
def fetch_weather(city: str) -> str:
    """Get current weather for a city"""
    return f"Weather in {city}: 72°F and sunny"
```

Register and use:

```bash
> /tool list                # Show available tools
> /tool info --name multiply
> /agent add-tool researcher --tool multiply
> /agent run researcher "Multiply 6 by 7"
```

## Configuration

**Main config file**: `config.yaml`

```yaml
debug:
  level: 1  # 0=off, 1=info, 2=debug

model:
  provider: "openai"  # openai, ollama, anthropic
  model: "gpt-4o-mini"
  api_key: "${OPENAI_API_KEY}"  # From .env file

memory:
  max_messages: 20
  max_tokens: 4000

paths:
  agents: "config/agents"
  tools: "tools/builtin"
  data: "data"
  logs: "logs"
```

**API Keys**: Set in `.env` file (NOT in config.yaml):

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
```

## Configuration Hierarchy

Settings are resolved in priority order (highest to lowest):

1. **CLI Flags** (highest priority)
   - Override everything else
   - Example: `/agent create test --provider anthropic --model claude-3-5-sonnet`
   - Overrides: config.yaml, .env, code defaults

2. **Environment Variables** (.env file)
   - Used for secrets and API keys
   - Syntax: `${VARIABLE_NAME}` in config.yaml
   - Example: `api_key: "${OPENAI_API_KEY}"`
   - Overrides: config.yaml values, code defaults
   - **Never** stored in config.yaml for security

3. **config.yaml Settings**
   - File-based configuration
   - Location: `config.yaml` in project root
   - Overrides: code defaults
   - Cannot override CLI flags

4. **Code Defaults** (lowest priority)
   - Built-in defaults in ConfigManager
   - Example defaults:
     - Provider: `openai`
     - Model: `gpt-4o-mini`
     - Debug level: `1` (info)
     - Max memory: `20` messages
   - Used only if not set elsewhere

### Configuration Examples

**Example 1: Override provider via CLI**
```bash
> /agent create researcher --provider anthropic
# Uses Anthropic even if config.yaml says openai
```

**Example 2: Set API key from .env**
```
# .env file
OPENAI_API_KEY=sk-12345...

# config.yaml
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"  # Resolved at runtime
```

**Example 3: Change default model in config**
```yaml
# config.yaml - applies to all agents using this config
model:
  provider: ollama
  model: llama2
```

**Example 4: CLI overrides config**
```bash
# config.yaml says: provider: openai, model: gpt-4o-mini
> /agent create test --provider ollama
# This agent uses ollama (CLI overrides config)
```

See `docs/` for detailed configuration docs.

## Project Structure

```
simple_agent/
  agents/          # Agent implementations (SimpleAgent wrapper)
  commands/        # REPL command groups
  core/            # Core modules (AgentManager, ConfigManager, ToolManager)
  guardrails/      # Input validation guardrails

config/
  agents/          # YAML agent definitions
  config.yaml      # Main configuration

tests/
  unit/            # Unit tests with mocks
  integration/     # Integration tests
  data/            # Test data files

docs/
  Progress_Tracker.md
  SPECIFICATION.md
  phases/          # Phase documentation
```

## Development

### Run Tests

```bash
pytest                                    # Run all tests
pytest tests/unit/                       # Unit tests only
pytest tests/integration/                # Integration tests only
pytest tests/unit/test_guardrails.py -v # Specific test file
```

### Code Quality

```bash
ruff check simple_agent/ --fix  # Lint and fix
ruff format simple_agent/       # Format code
```

### Add New Phase/Feature

1. Write unit tests (TDD)
2. Implement code until tests pass
3. Write integration tests
4. Update `docs/Progress_Tracker.md`
5. Commit with clear message

See `CLAUDE.md` in root for development guidelines.

## Dependencies

**Core:**
- `smolagents>=0.1.0` - Agent framework
- `litellm>=1.0.0` - Universal LLM interface
- `pyyaml>=6.0` - YAML parsing
- `click>=8.0` - CLI framework
- `rich>=13.0` - Terminal formatting
- `jinja2>=3.1.0` - Template engine

**Optional:**
- `chromadb>=0.4.0` - Vector store for RAG (Phase 2.3+)
- `python-dotenv>=1.0.0` - Environment variable loading

## Status

**Phase 1**: ✅ Complete (7 sub-phases)
- Interactive chat, inspection, memory, config management, tools, YAML agents, templates, Jinja2

**Phase 2.1**: ✅ Complete
- Guardrails: PII detection, custom rules, guardrail wrapper

**Phase 2.2**: ✅ Complete
- Human-in-the-loop approval gates

**Phase 2.3**: ✅ Complete
- RAG Foundation: Chroma-based collections with semantic search

**Phase 2.4**: ✅ Complete
- Multi-Agent Orchestration: Orchestrator pattern with ReAct iteration

**Phase 3.1**: ✅ Complete
- Token Budget Protection: Hard limits to prevent rate limit hits (30K TPM overages)

**Phase 3.2+**: 🔄 Planning
- Advanced token management: cost tracking, model-specific estimation

See `docs/Progress_Tracker.md` for detailed phase status.

## License

MIT
