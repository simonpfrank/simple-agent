# Phase 1.5: YAML Agent Definitions - Implementation Plan

**Goal:** Define agents in YAML files and auto-load them on startup

## YAML Agent Format

```yaml
# config/agents/researcher.yaml
name: "researcher"
agent_type: "tool_calling"  # or "code"
role: |
  You are a research specialist. You help users find accurate
  information and cite sources.

tools:
  - add
  - multiply

model:
  provider: "openai"  # optional, defaults to config.yaml
  model: "gpt-4o-mini"  # optional
  temperature: 0.3  # optional
  max_tokens: 2000  # optional

settings:
  verbosity: 2  # optional
  max_steps: 15  # optional
  executor_type: "docker"  # optional, only for code agents

metadata:  # optional section
  description: "Research and information gathering specialist"
  author: "user"
  version: "1.0.0"
```

## Features to Implement

### 1. AgentManager.load_agent_from_yaml(path)
- Load single agent from YAML file
- Merge with config.yaml defaults
- Create and register agent
- Return agent instance

### 2. AgentManager.save_agent_to_yaml(name, path)
- Get agent from registry
- Extract configuration
- Write to YAML file
- Include metadata

### 3. AgentManager.load_agents_from_directory(directory)
- Scan directory for *.yaml files
- Load each agent file
- Skip invalid files with warnings
- Return count of loaded agents

### 4. Auto-load on startup (app.py)
- Call load_agents_from_directory("config/agents/")
- Load after config but before REPL starts
- Log loaded agents in debug mode

### 5. /agent save <name> command
- Save agent to config/agents/<name>.yaml
- Create directory if needed
- Confirmation message

### 6. /agent create-wizard command
- Interactive prompts for all settings
- Step-by-step with defaults
- Option to save at end

## Agent Configuration Hierarchy

Priority (highest to lowest):
1. CLI arguments (create command flags)
2. Agent YAML file (config/agents/*.yaml)
3. config.yaml (agents.default section)
4. Code defaults (hardcoded in SimpleAgent)

## Implementation Order

1. ✅ Write YAML format spec (this file)
2. Write unit tests for YAML loading
3. Implement load_agent_from_yaml()
4. Write unit tests for YAML saving
5. Implement save_agent_to_yaml()
6. Write unit tests for directory loading
7. Implement load_agents_from_directory()
8. Update app.py for auto-load
9. Write tests for /agent save command
10. Implement /agent save command
11. Write tests for /agent create-wizard
12. Implement /agent create-wizard command
13. Write integration tests
14. Manual REPL testing
15. Update Progress_Tracker.md

## Files to Create/Modify

**Create:**
- `config/agents/` directory
- `config/agents/default.yaml` (example)
- `tests/unit/test_agent_yaml.py` (new tests)
- `tests/integration/test_phase_1_5.py` (integration)

**Modify:**
- `simple_agent/core/agent_manager.py` - Add YAML methods
- `simple_agent/commands/agent_commands.py` - Add save, create-wizard
- `simple_agent/app.py` - Auto-load agents
- `docs/Progress_Tracker.md` - Mark Phase 1.5 complete
