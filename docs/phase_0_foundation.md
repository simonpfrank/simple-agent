# Phase 0: Foundation

**Status:** ✅ Completed
**Completed:** 2025-10-21
**Effort:** 2 days

---

## Overview

Phase 0 established the foundational architecture for the Simple Agent system, implementing core configuration management, agent lifecycle management, and basic REPL integration with SmolAgents.

**Goal:** Get a working agent that can respond to prompts through the REPL using configuration-driven setup.

---

## What Was Built

### Core Components

#### 1. ConfigManager
**File:** `simple_agent/core/config_manager.py`

**Capabilities:**
- Load YAML configuration files
- Load .env files and set environment variables
- Nested key access with dot notation (e.g., `logging.level`)
- Load prompt templates from `config/prompts/`
- Merge configurations with defaults
- Save configurations to YAML
- Environment variable substitution with `${VAR}` syntax

**Key Methods:**
- `ConfigManager.load(path)` - Load YAML config
- `ConfigManager.load_env(path)` - Load .env file
- `ConfigManager.get(config, key, default)` - Get nested values
- `ConfigManager.save(config, path)` - Save config
- `ConfigManager.merge_with_defaults(config)` - Merge with defaults
- `ConfigManager.load_prompt_template(name)` - Load templates
- `ConfigManager.resolve_env_var(value)` - Resolve single env var (Phase 0.5 addition)
- `ConfigManager.substitute_env_vars(config)` - Substitute all env vars (Phase 0.5 addition)

#### 2. SimpleAgent
**File:** `simple_agent/agents/simple_agent.py`

**Capabilities:**
- Thin wrapper around SmolAgents CodeAgent (⚠️ Security issue - fixed in Phase 0.5)
- Initialize with LiteLLM model support
- Support for multiple providers (OpenAI, Ollama, Anthropic, LM Studio)
- Template-based or explicit role/persona
- Configurable verbosity and max steps

**Key Methods:**
- `__init__()` - Initialize agent with config
- `_create_model()` - Create LiteLLM model for provider
- `run(prompt)` - Execute prompt through agent
- `__repr__()` - String representation

**Providers Supported:**
- OpenAI (gpt-4o-mini, etc.)
- Ollama (local models)
- LM Studio (local, OpenAI-compatible)
- Anthropic (Claude models)
- Generic (fallback)

#### 3. AgentManager
**File:** `simple_agent/core/agent_manager.py`

**Capabilities:**
- Manage multiple agents
- Create agents from configuration
- Auto-load agents defined in config.yaml
- Retrieve agents by name
- List all registered agents
- Run prompts through specific agents

**Key Methods:**
- `create_agent(name, provider, role, template)` - Create and register agent
- `get_agent(name)` - Get agent by name
- `list_agents()` - List all agent names
- `run_agent(name, prompt)` - Run prompt through agent
- `_load_agents_from_config()` - Auto-load agents on startup

### REPL Integration

#### Agent Commands
**File:** `simple_agent/commands/agent_commands.py`

**Commands:**
- `/agent create <name> [--provider] [--template] [--role]` - Create new agent
- `/agent run <name> <prompt>` - Run prompt through agent
- `/agent list` - List all registered agents

**Features:**
- No business logic in commands (delegation to AgentManager)
- Rich console output
- Error handling with helpful messages

### Configuration System

#### Config Files

**config.yaml:**
```yaml
llm:
  provider: "openai"
  openai:
    model: "gpt-4o-mini"
    api_key: "${OPENAI_API_KEY}"
    temperature: 0.7
    max_tokens: 2000

agents:
  default:
    role: "You are a helpful AI assistant."
    verbosity: 1
    max_steps: 10

logging:
  level: "INFO"
  file: "logs/app.log"
  console_enabled: false
```

**Prompt Templates:**
- `config/prompts/default.yaml` - Default assistant role
- `config/prompts/researcher.yaml` - Research specialist role

#### Environment Variables
**.env:**
```bash
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Testing Infrastructure

**Test Coverage:** 54 tests (50 original + 4 env var tests)

**Unit Tests:**
- `tests/unit/test_config_manager.py` - ConfigManager (25 tests)
- `tests/unit/test_agent_manager.py` - AgentManager (15 tests)
- `tests/unit/test_simple_agent.py` - SimpleAgent (9 tests)

**Integration Tests:**
- `tests/integration/test_agent_lifecycle_mocked.py` - Full lifecycle (5 tests)

**Test Structure:**
- `tests/unit/` - Unit tests with mocks
- `tests/integration/` - Integration tests with mocked LLM
- `tests/data/` - Test data files (test_config.yaml)

---

## Key Features Implemented

### 1. Configuration Management
✅ YAML config loading with validation
✅ Environment variable loading from .env
✅ Nested key access with dot notation
✅ Config merging with defaults
✅ Prompt template loading
✅ Environment variable substitution (Phase 0.5)

### 2. Agent Lifecycle
✅ Create agents with config or explicit params
✅ Auto-load agents from config.yaml on startup
✅ Multiple agent support
✅ Provider abstraction (OpenAI, Ollama, Anthropic)
✅ Template-based role assignment

### 3. REPL Commands
✅ `/agent create` - Create new agents
✅ `/agent run` - Run prompts through agents
✅ `/agent list` - List all agents
✅ Helpful error messages and examples

### 4. Security (Phase 0.5)
✅ Environment variable substitution only at point-of-use
✅ Config save never writes secrets to disk
✅ `/config show --resolve` flag for safe display
✅ `resolve_env_var()` helper for single value resolution

---

## Technical Decisions

### Architecture Patterns

1. **Separation of Concerns**
   - Commands contain zero business logic
   - All logic in AgentManager and SimpleAgent
   - Testable, reusable core components

2. **Configuration-Driven**
   - YAML for structure
   - .env for secrets
   - Templates for reusable prompts

3. **Thin Wrapper Pattern**
   - SimpleAgent wraps SmolAgents
   - Exposes only what we need
   - Easy to extend or replace

### Code Standards

- **Line length:** 119 characters
- **Type hints:** Required on all functions
- **Docstrings:** Google-style with Args/Returns/Raises
- **Naming:** PascalCase classes, snake_case functions
- **Testing:** TDD approach, >90% coverage

### SmolAgents Integration

- Used `CodeAgent` (⚠️ Security issue - being fixed in Phase 0.5)
- LiteLLMModel for provider abstraction
- Changed `system_prompt` to `instructions` parameter

---

## Issues Fixed During Phase 0

### GitHub Issues Closed

1. **Issue #1:** Strange ^J characters in subcommand display
   - Fixed: Normalized help text to first line only

2. **Issue #2:** Error creating agent (system_prompt)
   - Fixed: Changed to `instructions` parameter for CodeAgent

3. **Issue #3:** Config save requires --file flag
   - Fixed: Made --file optional, defaults to loaded config

4. **Issue #4:** Default agent not listed
   - Fixed: Added `_load_agents_from_config()` to auto-load

5. **Issue #5:** Remove process command
   - Fixed: Removed template leftover

6. **Issue #6:** API key environment variable not working
   - Fixed: Added .env loading and substitution (see Phase 0.5)

### Security Fix (Phase 0.5)

**Issue #8:** Config save exposes API keys
- **Problem:** Global env var substitution meant config dict contained actual keys
- **Fix:** Point-of-use substitution only, config dict keeps `${VAR}` placeholders
- **Result:** Config save is always safe, no secrets written to disk

---

## Test Results

### Final Test Count
- **Total:** 54 tests
- **Unit:** 49 tests
- **Integration:** 5 tests
- **Status:** ✅ All passing

### Coverage
- ConfigManager: 21 tests
- AgentManager: 15 tests
- SimpleAgent: 9 tests
- Environment vars: 4 tests
- Integration: 5 tests

---

## Manual Testing Results

### REPL Testing Completed

✅ Start REPL
✅ Default agent auto-loaded from config
✅ `/agent list` shows default agent
✅ `/agent create custom` creates new agent
✅ `/agent run default hello` gets response
✅ OpenAI API key working correctly
✅ Config show displays safely

### Known Issues Discovered

⚠️ **CRITICAL:** CodeAgent uses `executor_type="local"` by default
- LLM-generated code executes on host machine
- Major security vulnerability
- **Must fix in Phase 0.5**

---

## Dependencies Installed

```txt
# Core
click>=8.1.0
click-repl>=0.3.0
rich>=13.0.0
prompt-toolkit>=3.0.0
PyYAML>=6.0.0

# Agent framework
smolagents>=0.1.0
litellm>=1.0.0
python-dotenv>=1.0.0

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
ruff==0.14.1
```

---

## Files Created

### Core
- `simple_agent/core/config_manager.py`
- `simple_agent/core/agent_manager.py`

### Agents
- `simple_agent/agents/__init__.py`
- `simple_agent/agents/simple_agent.py`

### Commands
- `simple_agent/commands/agent_commands.py`

### Config
- `config.yaml`
- `config/prompts/default.yaml`
- `config/prompts/researcher.yaml`

### Tests
- `tests/__init__.py`
- `tests/unit/__init__.py`
- `tests/unit/test_config_manager.py`
- `tests/unit/test_agent_manager.py`
- `tests/unit/test_simple_agent.py`
- `tests/integration/__init__.py`
- `tests/integration/test_agent_lifecycle_mocked.py`
- `tests/data/test_config.yaml`

### Documentation
- `docs/Progress_Tracker.md`

### Utilities
- `utils/simple_llm_check.py` - OpenAI API verification script

---

## Commits

1. **8730354** - fix: Resolve Phase 0 manual testing issues (#1-5)
2. **74f633e** - fix: Add environment variable substitution for API keys (#6)
3. **db83402** - security: Fix API key exposure in config save

---

## Lessons Learned

### What Went Well
- TDD approach caught issues early
- Clean separation of concerns paid off
- Config-driven design is flexible
- SmolAgents integration straightforward

### What Went Wrong
- **Used CodeAgent without Docker executor** ← Critical security issue
- Didn't validate security implications before implementing
- Should have researched agent types more thoroughly

### Improvements for Phase 0.5
- ✅ Research security implications first
- ✅ Use ToolCallingAgent by default
- ✅ Add Docker-based code execution tool
- ✅ Implement security validation
- ✅ Never allow local code execution

---

## Next Phase

**Phase 0.5: Security Fix & Agent Type Architecture**

**Critical Priority:**
1. Switch from CodeAgent to ToolCallingAgent
2. Implement Docker-based Python execution tool
3. Add agent type selection architecture
4. Security validation for all configs
5. Update all tests and documentation

See `docs/phases/PHASE_0.5.md` for detailed specification.

---

## Success Criteria Met

✅ Configuration loads from config.yaml and .env
✅ Prompt templates load from config/prompts/
✅ Can create agent with OpenAI, Ollama, or LM Studio
✅ Can create agent with template or explicit role
✅ Can run prompt through agent and get LLM response
✅ Messages formatted correctly (system/user roles)
✅ All unit tests pass (with mocks)
✅ Integration test passes (mocked)
✅ Manual REPL test successful
✅ Code follows CLAUDE.md standards

⚠️ **Security issue discovered and must be fixed in Phase 0.5**
