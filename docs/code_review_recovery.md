# Code Review Recovery Plan
**Created:** January 8, 2026
**Reference:** docs/code_review_2026.md

---

## Overview

This plan addresses all issues identified in the code review, organized into phases by priority. Each phase should be completed and tested before moving to the next.

**Estimated Total Effort:** 8-12 development sessions
**Testing Required:** Unit tests for each fix, integration tests per phase

---

## Phase 1: Critical Security Fixes (Priority: IMMEDIATE)

### 1.1 Fix HITL Tool Wrapper (BLOCKING)
**File:** `simple_agent/hitl/tool_wrapper.py`
**Issue:** Approvals don't block execution

**Tasks:**
- [ ] Add blocking mechanism to wait for approval before tool execution
- [ ] Implement timeout for pending approvals
- [ ] Add approval state checking before `self.tool(*args, **kwargs)`
- [ ] Write unit tests for approval flow
- [ ] Write integration test: tool with approval required must not execute until approved

**Implementation:**
```python
# Pseudocode for fix
if self.requires_approval:
    approval_id = self.approval_manager.request_approval(...)
    # BLOCK until approved or rejected
    approved = self.approval_manager.wait_for_decision(approval_id, timeout=300)
    if not approved:
        raise ToolExecutionDenied(f"Tool {self.tool_name} was not approved")

# Only execute if approved or no approval required
result = self.tool(*args, **kwargs)
```

---

### 1.2 Fix Thread-Unsafe Global State
**File:** `simple_agent/core/runtime_config.py`
**Issue:** Race condition in concurrent access

**Tasks:**
- [ ] Add threading.Lock for config access
- [ ] Make get/set operations atomic
- [ ] Add unit tests for concurrent access

**Implementation:**
```python
import threading

_config_lock = threading.Lock()
_runtime_config: Optional[Dict[str, Any]] = None

def set_config(config: Optional[Dict[str, Any]]) -> None:
    global _runtime_config
    with _config_lock:
        _runtime_config = config

def get_config() -> Optional[Dict[str, Any]]:
    with _config_lock:
        return _runtime_config
```

---

### 1.3 Fix Path Traversal Vulnerability
**File:** `simple_agent/commands/agent_commands.py`
**Issue:** Agent name can escape config/agents directory

**Tasks:**
- [ ] Add strict path validation in `_resolve_agent_path()`
- [ ] Use `Path.resolve()` and verify within allowed directory
- [ ] Add unit tests for path traversal attempts
- [ ] Reject names with `..` anywhere in the string

**Implementation:**
```python
def _resolve_agent_path(agent_name: str) -> Optional[str]:
    # Reject any path traversal attempts
    if ".." in agent_name:
        return None

    agents_dir = Path("config/agents").resolve()
    candidate = (agents_dir / f"{agent_name}.yaml").resolve()

    # Verify resolved path is still within agents_dir
    if not str(candidate).startswith(str(agents_dir)):
        return None

    if candidate.exists():
        return str(candidate)
    return None
```

---

## Phase 2: Type Safety (Priority: HIGH)

### 2.1 Add Type Hints - Core Module
**Files:** `simple_agent/core/*.py`

**Tasks:**
- [ ] `agent_manager.py` - Add all missing type hints
- [ ] `tool_manager.py` - Add all missing type hints
- [ ] `config_manager.py` - Add all missing type hints
- [ ] `runtime_config.py` - Add all missing type hints
- [ ] `repl_context.py` - Add all missing type hints
- [ ] `token_tracker_persistence.py` - Add all missing type hints
- [ ] Run `mypy --strict simple_agent/core/` - must pass

---

### 2.2 Add Type Hints - Commands Module
**Files:** `simple_agent/commands/*.py`

**Tasks:**
- [ ] `agent_commands.py` - Add return types to all commands
- [ ] `token_stats_commands.py` - Add return types
- [ ] `system_commands.py` - Add return types
- [ ] `inspection_commands.py` - Add return types
- [ ] Run `mypy --strict simple_agent/commands/` - must pass

---

### 2.3 Add Type Hints - Agents Module
**Files:** `simple_agent/agents/*.py`

**Tasks:**
- [ ] `simple_agent.py` - Add all missing type hints
- [ ] `agent_config.py` - Add all missing type hints
- [ ] Run `mypy --strict simple_agent/agents/` - must pass

---

### 2.4 Add Type Hints - Remaining Modules
**Files:** `simple_agent/hitl/`, `simple_agent/guardrails/`, `simple_agent/rag/`, `simple_agent/orchestration/`

**Tasks:**
- [ ] Add type hints to all remaining files
- [ ] Run `mypy --strict simple_agent/` - entire project must pass

---

## Phase 3: Architecture Refactoring (Priority: HIGH)

### 3.1 Fix AgentManager/ToolManager Coupling
**Files:** `simple_agent/core/agent_manager.py`, `simple_agent/core/repl_context.py`

**Tasks:**
- [ ] Add `tool_manager` as constructor parameter to AgentManager
- [ ] Remove manual post-init assignment pattern
- [ ] Update all instantiation sites
- [ ] Add validation: raise error if tool_manager is None when tools requested

**Implementation:**
```python
class AgentManager:
    def __init__(self, config: Dict[str, Any], tool_manager: Optional[ToolManager] = None):
        self.config = config
        self.tool_manager = tool_manager
        # ... rest of init
```

---

### 3.2 Split Large Files
**Target:** Max 500 lines per file

#### 3.2.1 Split `simple_agent.py` (803 lines)
**Tasks:**
- [ ] Extract Jinja2 template handling to `simple_agent/agents/template_renderer.py`
- [ ] Extract rate limit tracking to `simple_agent/agents/rate_limit_handler.py`
- [ ] Extract token budget logic to `simple_agent/agents/token_budget.py`
- [ ] Keep core agent logic in `simple_agent.py` (<500 lines)
- [ ] Update imports throughout codebase
- [ ] Verify all tests pass

#### 3.2.2 Split `agent_commands.py` (848 lines)
**Tasks:**
- [ ] Extract wizard to `simple_agent/commands/agent_wizard.py`
- [ ] Extract load/save to `simple_agent/commands/agent_persistence.py`
- [ ] Extract tool management to `simple_agent/commands/agent_tools.py`
- [ ] Keep core commands in `agent_commands.py` (<500 lines)
- [ ] Update plugin registration
- [ ] Verify all tests pass

---

### 3.3 Remove Dead Code
**Files:** Various

**Tasks:**
- [ ] Remove unused `AgentConfig` constructor path in `simple_agent.py` (keep only if tests need it)
- [ ] Move `_load_agents_from_config()` to be called internally or make public
- [ ] Remove any commented-out code
- [ ] Run test suite to verify no regressions

---

## Phase 4: Error Handling Improvements (Priority: MEDIUM)

### 4.1 Replace Silent Exception Handlers
**Files:** Multiple

**Tasks:**
- [ ] `collection_manager.py:212` - Replace `except Exception: pass` with specific handling
- [ ] `simple_agent.py:797-799` - Elevate rate limit extraction failures to warning level
- [ ] Audit all `except Exception` blocks - add specific exception types
- [ ] Add logging for all caught exceptions (at minimum WARNING level)

---

### 4.2 Standardize Error Handling Pattern
**Goal:** Consistent error handling across codebase

**Pattern to implement:**
```python
try:
    # operation
except SpecificException as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise  # or return appropriate error result
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

**Tasks:**
- [ ] Document error handling pattern in CONTRIBUTING.md
- [ ] Apply pattern to `simple_agent.py`
- [ ] Apply pattern to `agent_commands.py`
- [ ] Apply pattern to all manager classes

---

### 4.3 Fix Config Validation
**File:** `simple_agent/core/config_manager.py`

**Tasks:**
- [ ] Add `llm` to required config keys
- [ ] Validate `llm.provider` exists
- [ ] Add clear error messages for missing config sections
- [ ] Write tests for config validation edge cases

---

## Phase 5: Security Hardening (Priority: MEDIUM)

### 5.1 Sanitize Jinja2 Template Rendering
**File:** `simple_agent/agents/simple_agent.py`

**Tasks:**
- [ ] Use Jinja2 SandboxedEnvironment instead of Environment
- [ ] Restrict available context variables
- [ ] Add input validation for template strings
- [ ] Write security tests for template injection attempts

**Implementation:**
```python
from jinja2.sandbox import SandboxedEnvironment

def _get_jinja_env(self) -> SandboxedEnvironment:
    return SandboxedEnvironment(
        autoescape=True,
        undefined=StrictUndefined
    )
```

---

### 5.2 Fix Secrets Logging
**Files:** `simple_agent/agents/simple_agent.py`, `simple_agent/core/config_manager.py`

**Tasks:**
- [ ] Audit all debug logging for potential secret exposure
- [ ] Mask or remove API keys from log output
- [ ] Don't log environment variable names for missing secrets
- [ ] Add `[REDACTED]` for sensitive values in debug logs

---

## Phase 6: Performance & Polish (Priority: LOW)

### 6.1 Cache Token Counting
**File:** `simple_agent/agents/simple_agent.py`

**Tasks:**
- [ ] Cache role token count (role doesn't change per-request)
- [ ] Only recalculate when role changes
- [ ] Add metrics for token counting performance

---

### 6.2 Fix Typos and Logging Format
**File:** `simple_agent/agents/simple_agent.py:635`

**Tasks:**
- [ ] Fix "tpm renaming" -> "tpm remaining"
- [ ] Improve log message formatting for readability
- [ ] Review all log messages for typos

---

### 6.3 Standardize Docstrings
**Goal:** Google-style docstrings throughout

**Tasks:**
- [ ] Audit all public functions for docstring presence
- [ ] Convert non-Google style docstrings
- [ ] Add missing Args/Returns/Raises sections
- [ ] Run docstring linter

---

### 6.4 Replace Print with Logging
**Files:** Various (508 instances)

**Tasks:**
- [ ] Identify all user-facing prints (keep these)
- [ ] Convert debug/info prints to logging calls
- [ ] Ensure consistent log levels

---

## Phase 7: Testing & Validation (Priority: ONGOING)

### 7.1 Post-Fix Validation
After each phase:
- [ ] Run full unit test suite: `pytest tests/unit/`
- [ ] Run integration tests: `pytest tests/integration/`
- [ ] Run type checker: `mypy --strict simple_agent/`
- [ ] Run linter: `ruff check simple_agent/`
- [ ] Manual smoke test of REPL

---

### 7.2 Add Missing Tests
**Tasks:**
- [ ] Add tests for HITL approval blocking
- [ ] Add tests for path traversal prevention
- [ ] Add tests for thread-safe config access
- [ ] Add tests for template injection prevention
- [ ] Achieve 90%+ branch coverage

---

## Tracking

| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| Phase 1: Critical Security | Not Started | - | - |
| Phase 2: Type Safety | Not Started | - | - |
| Phase 3: Architecture | Not Started | - | - |
| Phase 4: Error Handling | Not Started | - | - |
| Phase 5: Security Hardening | Not Started | - | - |
| Phase 6: Performance & Polish | Not Started | - | - |
| Phase 7: Testing & Validation | Ongoing | - | - |

---

## Success Criteria

- [ ] `mypy --strict simple_agent/` passes with no errors
- [ ] `ruff check simple_agent/` passes with no errors
- [ ] All files under 500 lines
- [ ] 90%+ branch coverage
- [ ] No silent exception handlers
- [ ] HITL actually blocks until approval
- [ ] No path traversal possible in agent loading
- [ ] No secrets in logs
- [ ] All tests pass

---

## Notes

- Do not skip phases - security fixes must come first
- Each phase should have its own PR for review
- Update Progress_Tracker.md after each phase completion
- Run full test suite before marking any phase complete
