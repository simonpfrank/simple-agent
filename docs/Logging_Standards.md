# Logging Standards Guide

## Overview

This document outlines the logging standards and conventions for the Simple-Agent project. It provides guidelines for consistent logging across the codebase to ensure clear execution flow visibility and effective debugging.

---

## Logging Configuration

**Location**: `simple_agent/core/logging_setup.py`

**Features**:
- Centralized logging configuration via `setup_logging()` function
- Module-level loggers using `logger = logging.getLogger(__name__)`
- File logging always enabled (default: `logs/app.log`)
- Console logging conditionally enabled in CLI mode
- Configurable log level: `--debug off|info|debug`
- Format: `%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s`

---

## Log Levels and Usage

### INFO Level - Operational Flow
**Purpose**: Track major operations and execution flow

**When to use**:
- Command execution start/completion
- Significant state changes (agent creation, loading, etc.)
- Operation milestones (file saved, config loaded)
- Resource counts (agents loaded, tools attached)

**Pattern**:
```python
logger.info(f"[COMMAND] /agent create - name={name}, provider={provider}")
logger.info(f"[COMMAND] Agent '{name}' created successfully")
logger.info(f"[FLOW] Workflow completed: 3 agents, 12 tool calls")
```

### DEBUG Level - Detailed Tracing
**Purpose**: Deep visibility into execution for debugging

**When to use**:
- Method entry/exit with parameters and return values
- State mutations and variable changes
- Decision point tracing (why certain paths taken)
- Detailed data transformations
- Internal operation steps

**Pattern**:
```python
logger.debug(f"→ create_agent(name={name}, provider={provider}, role_len={len(role) if role else 0})")
logger.debug(f"← create_agent() returned SimpleAgent instance: {agent.name}")
logger.debug(f"State: agents={list(self.agents.keys())}")
```

### WARNING Level - Recoverable Issues
**Purpose**: Alert about non-critical problems that don't halt execution

**When to use**:
- Missing optional resources (no agents, no tools)
- Fallback configurations being used
- Failed optional operations
- Empty data sets

**Pattern**:
```python
logger.warning(f"[COMMAND] Agent '{name}' not found in config/agents/ or as path")
logger.warning(f"No paths configured (using defaults)")
```

### ERROR Level - Critical Failures
**Purpose**: Log failures that impact functionality

**When to use**:
- Unhandled exceptions (always use `exc_info=True`)
- Failed required operations
- Authentication/authorization failures
- Critical validation errors

**Pattern**:
```python
logger.error(f"[COMMAND] Create agent failed - {type(e).__name__}: {str(e)}", exc_info=True)
logger.error(f"Config load failed - {type(e).__name__}: {str(e)}", exc_info=True)
```

---

## Logging Context Prefixes

Use these prefixes in log messages to add context:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `[COMMAND]` | CLI command execution | `[COMMAND] /agent create - name=...` |
| `[FLOW]` | Workflow/orchestration | `[FLOW] Executing: agent_1 → agent_2` |
| `[APPROVAL]` | HITL approval | `[APPROVAL] Decision: APPROVED` |
| `[TOOL]` | Tool execution | `[TOOL] Executing: tavily_search (2 params)` |
| `[RAG]` | Document/retrieval ops | `[RAG] Indexed: 450 chunks` |
| `[CHAT]` | Chat mode interaction | `[CHAT] Message 1: prompt_len=50` |

---

## Entry/Exit Logging Pattern

For important public methods and operations, log entry and exit:

```python
def create_agent(self, name: str, provider: str, role: str):
    logger.debug(f"→ create_agent(name={name}, provider={provider}, role_len={len(role) if role else 0})")

    try:
        # implementation...
        agent = self._build_agent(name, provider, role)
        logger.debug(f"← create_agent() returned SimpleAgent: {agent.name}")
        return agent
    except Exception as e:
        logger.error(f"create_agent failed - {type(e).__name__}: {str(e)}", exc_info=True)
        raise
```

---

## Parameter and Data Logging

### What to Log
✅ **DO log**:
- Operation names and types
- Parameter counts (not full lists if large)
- Return type/summary
- Response lengths/sizes
- State snapshots (agent list, tool count)
- Error types and messages
- File paths and operations

### What NOT to Log
❌ **NEVER log**:
- API keys, tokens, credentials
- Passwords or secrets (even hashed)
- Full LLM responses (log size only)
- Sensitive user data
- Full request bodies (log summary)
- Personal identifying information

### Parameter Summary Convention
```python
# ✅ Good - summaries and counts
logger.debug(f"load_document(path={path}, chunks={len(chunks)}, size={total_bytes}MB)")

# ❌ Bad - too verbose
logger.debug(f"load_document with full content: {full_json_document}")
```

---

## LLM Response and Tool Logging

### Response Logging
```python
# ✅ Log size and type
response_len = len(response) if response else 0
logger.info(f"[COMMAND] Agent response (len={response_len})")
logger.debug(f"Response summary: {response[:100]}...")  # first 100 chars only

# ❌ Don't log full response
logger.info(f"Full response: {very_long_llm_response}")
```

### Tool Execution Logging
```python
# INFO: Tool name and parameter count
logger.info(f"[TOOL] Executing: tavily_web_search (2 params)")

# DEBUG: Detailed parameters (with sensitive redaction)
logger.debug(f"[TOOL] tavily_web_search: query='...' (redacted)")

# INFO: Result summary
logger.info(f"[TOOL] tavily_web_search returned 5 results")
```

---

## Command Handler Logging Pattern

All command handlers should follow this pattern:

```python
@config.command("save")
@click.argument("name")
@click.pass_context
def config_save(context, name: str):
    """Save configuration."""
    console = get_console(context)
    config_dict = context.obj.get("config", {})

    # 1. Log command start with parameters
    logger.info(f"[COMMAND] /config save - name={name}")
    logger.debug(f"→ ConfigManager.save()")

    try:
        # 2. Perform operation
        ConfigManager.save(config_dict, name)

        # 3. Log successful completion
        logger.info(f"[COMMAND] Config '{name}' saved successfully")
        logger.debug(f"← ConfigManager.save() completed")

        console.print(f"[green]✓[/green] Saved: {name}")

    except Exception as e:
        # 4. Log errors with exc_info
        logger.error(f"[COMMAND] Save failed - {type(e).__name__}: {str(e)}", exc_info=True)
        console.print(f"[red]Error:[/red] {str(e)}")
```

---

## Logging in Tests

For test data verification:

```python
# In tests, log when unexpected
if not expected_result:
    logger.warning(f"Test: Expected result not found: {condition}")
```

Tests don't need extensive logging since pytest captures output, but use logging for debugging test failures.

---

## Performance Considerations

**INFO Level Impact**: Minimal (typically < 1ms per log)
**DEBUG Level Impact**: Moderate (enable during development, disable in production)

**Best Practice**:
- INFO logs: Always enabled, use for user-facing operations
- DEBUG logs: Enabled with `--debug debug`, use for detailed tracing
- Disable at runtime in high-throughput scenarios if needed

---

## Migration Guide

When adding logging to existing code:

1. **Add module-level logger**:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. **Add command start logging**:
   ```python
   logger.info(f"[COMMAND] /command_name - param={param}")
   ```

3. **Add entry/exit for key methods**:
   ```python
   logger.debug(f"→ method_name(param={param})")
   # ... implementation ...
   logger.debug(f"← method_name() returned result")
   ```

4. **Add error logging**:
   ```python
   except Exception as e:
       logger.error(f"Operation failed - {type(e).__name__}: {str(e)}", exc_info=True)
   ```

---

## Examples by Module

### Command Modules (agent_commands.py)
```python
logger.info(f"[COMMAND] /agent create - name={name}, provider={provider}")
logger.debug(f"→ create_agent(name={name}, provider={provider})")
logger.info(f"[COMMAND] Agent '{name}' created successfully")
logger.error(f"[COMMAND] Create agent failed - {type(e).__name__}: {str(e)}", exc_info=True)
```

### Core Modules (agent_manager.py)
```python
logger.debug(f"→ AgentManager.create_agent({name}, provider={provider})")
logger.info(f"Agent '{name}' created: {len(self.agents)} agents now registered")
logger.debug(f"← AgentManager.create_agent() returned SimpleAgent")
```

### HITL/Approval Modules
```python
logger.info(f"[APPROVAL] Request: agent='{agent}', action='{action}'")
logger.info(f"[APPROVAL] Decision: APPROVED by {user_id}")
logger.info(f"[APPROVAL] Action executed successfully")
```

### RAG/Document Modules
```python
logger.info(f"[RAG] Loading documents: {path} ({file_count} files)")
logger.info(f"[RAG] Indexed: {chunk_count} chunks from {doc_count} documents")
logger.debug(f"[RAG] Document parse: {file} → {num_chunks} chunks, {total_tokens} tokens")
```

---

## Monitoring and Analysis

Use log files to monitor:
- Command execution frequency
- Performance patterns (look for slow operations)
- Error rates and types
- User workflows

**Log file location**: `logs/app.log` (configurable)

**Log rotation**: Manual (delete old logs as needed)

---

## Future Enhancements

- [ ] Implement structured logging (JSON format)
- [ ] Add performance timing logs
- [ ] Create log analysis tools
- [ ] Implement log rotation/archival
- [ ] Add correlation IDs for multi-step operations
- [ ] Create centralized logging dashboard

