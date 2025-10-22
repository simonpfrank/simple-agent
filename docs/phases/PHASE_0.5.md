# Phase 0.5: Security Fix & Agent Type Architecture

**Status:** 🔴 Critical - Not Started
**Priority:** P0 - Must complete before Phase 1
**Estimated Effort:** 2-3 days

---

## Overview

### Why Phase 0.5 Exists

Phase 0 implementation contained a **critical security vulnerability**: the use of `CodeAgent` with default `executor_type="local"` allows arbitrary LLM-generated code to execute directly on the host machine without any sandboxing.

This phase exists to:
1. Fix the security vulnerability immediately
2. Implement proper agent type architecture
3. Add safe Docker-based code execution
4. Establish security validation patterns

### What Was Wrong in Phase 0

**Critical Issue:**
```python
# simple_agent/agents/simple_agent.py (Phase 0)
self.agent = CodeAgent(
    tools=tools or [],
    model=self.model,
    max_steps=max_steps,
    verbosity_level=verbosity,
    instructions=role,
    # ❌ Missing: executor_type parameter
    # ❌ Defaults to executor_type="local"
    # ❌ LLM can execute ANY code on host machine!
)
```

**Why This Is Unacceptable:**
- LLM-generated code runs with full user permissions
- No sandboxing or isolation
- Can access filesystem, network, system calls
- Could delete files, exfiltrate data, install malware
- Violates basic security principles

**What Should Have Been Done:**
- Use `ToolCallingAgent` by default (safer)
- If using `CodeAgent`, require `executor_type="docker"`
- Or create safe Python execution tool for `ToolCallingAgent`

---

## Goals & Scope

### Phase 0.5 Goals

1. **Eliminate local code execution risk**
2. **Implement flexible agent type system**
3. **Create safe Docker-based Python tool**
4. **Add security validation**
5. **Update all documentation**

### In Scope

✅ Agent type selection (ToolCallingAgent, CodeAgent, MultiStepAgent)
✅ Docker-based Python execution tool
✅ Security validation and constraints
✅ Config schema updates
✅ Comprehensive testing
✅ Documentation updates

### Out of Scope

❌ Interactive chat mode (Phase 1)
❌ Prompt inspection (Phase 1)
❌ Tool auto-discovery (Phase 1)
❌ Memory/RAG features (Phase 2+)

---

## Security Issue Analysis

### CodeAgent Security Model

SmolAgents `CodeAgent` has multiple executor types:

| Executor Type | Security | Use Case |
|--------------|----------|----------|
| `local` | ❌ UNSAFE | Development only, never production |
| `docker` | ✅ Safe | Isolated container execution |
| `e2b` | ✅ Safe | Cloud sandbox (requires account) |
| `modal` | ✅ Safe | Serverless execution |
| `wasm` | ✅ Safe | WebAssembly sandbox |

**Default:** `executor_type="local"` ← This is the problem!

### ToolCallingAgent Security Model

- Agent calls predefined tools only
- No arbitrary code execution
- Tools control what can be done
- Much safer by default

### Our Decision

**Use ToolCallingAgent as default with safe Python execution tool:**
- Agent can only call tools we define
- Python tool uses Docker for isolation
- Same capability as CodeAgent but safer
- Better control and auditability

---

## Agent Type Architecture

### Supported Agent Types

We support 3 agent types with different use cases:

#### 1. ToolCallingAgent (Default, Recommended)

**Use Case:** General purpose, safe execution
**How it works:** LLM generates JSON tool calls, we execute tools
**Security:** ✅ Safe - can only call predefined tools
**Performance:** Fast, efficient
**Code Example:**
```python
from smolagents import ToolCallingAgent

agent = ToolCallingAgent(
    tools=[python_executor_tool],  # Our safe tools
    model=model,
    max_steps=10
)
```

#### 2. CodeAgent (Optional, Docker Only)

**Use Case:** Complex code generation, if needed later
**How it works:** LLM writes Python code, executed in Docker
**Security:** ⚠️ Requires Docker executor
**Performance:** Slower (container overhead)
**Code Example:**
```python
from smolagents import CodeAgent

# ONLY allowed with docker executor
agent = CodeAgent(
    tools=[],
    model=model,
    executor_type="docker",  # ✅ Required!
    max_steps=10
)
```

#### 3. MultiStepAgent (Future)

**Use Case:** Planning, multi-step reasoning
**How it works:** Agent plans then executes steps
**Security:** Inherits from parent agent type
**Performance:** Slower (planning overhead)
**Code Example:**
```python
from smolagents import MultiStepAgent

agent = MultiStepAgent(
    tools=[python_executor_tool],
    model=model,
    planning_interval=3  # Replan every 3 steps
)
```

### Decision Matrix

| Need | Agent Type | Why |
|------|-----------|-----|
| Safe general purpose | ToolCallingAgent | Best default, safe, fast |
| Complex code generation | CodeAgent (docker) | If absolutely needed |
| Planning/reasoning | MultiStepAgent | Future feature |
| Quick single task | ToolCallingAgent | Simplest, fastest |

---

## Implementation Details

### 1. SimpleAgent Refactor

**File:** `simple_agent/agents/simple_agent.py`

**Changes:**

```python
class SimpleAgent:
    def __init__(
        self,
        name: str,
        model_provider: str,
        model_config: Dict[str, Any],
        agent_type: str = "tool_calling",  # NEW: agent type selection
        role: Optional[str] = None,
        template: Optional[str] = None,
        tools: Optional[list] = None,
        verbosity: int = 1,
        max_steps: int = 10,
        executor_type: str = "docker",  # NEW: for CodeAgent only
    ):
        # Validate agent_type
        valid_types = ["tool_calling", "code", "multi_step"]
        if agent_type not in valid_types:
            raise ValueError(f"Invalid agent_type: {agent_type}")

        # Security validation for code agent
        if agent_type == "code" and executor_type == "local":
            raise SecurityError(
                "CodeAgent with executor_type='local' is not allowed. "
                "Use executor_type='docker' or switch to agent_type='tool_calling'"
            )

        self.agent_type = agent_type

        # Create appropriate agent
        if agent_type == "tool_calling":
            self.agent = ToolCallingAgent(
                tools=tools or [],
                model=self.model,
                max_steps=max_steps,
            )
        elif agent_type == "code":
            self.agent = CodeAgent(
                tools=tools or [],
                model=self.model,
                executor_type=executor_type,  # Must be "docker"
                max_steps=max_steps,
                instructions=role,
            )
        elif agent_type == "multi_step":
            # Future implementation
            raise NotImplementedError("MultiStepAgent not yet implemented")
```

### 2. Docker-Based Python Tool

**File:** `simple_agent/tools/python_executor.py`

**Design:**
- Uses `@tool` decorator from smolagents
- Runs Python code in Docker container
- Returns stdout, stderr, exit_code
- Manages persistent container
- Cleanup on shutdown

**Implementation:**

```python
from smolagents import tool
from docker import from_env, errors as docker_errors
import os
import time

@tool
def python_executor(code: str, timeout: int = 30) -> dict:
    """
    Execute Python code in an isolated Docker container.

    Args:
        code: Valid Python 3.10 code to execute
        timeout: Execution timeout in seconds (default: 30)

    Returns:
        Dictionary with:
            - success: bool - whether execution succeeded
            - data: dict with stdout, stderr, exit_code
            - message: str - human-readable status

    Examples:
        >>> result = python_executor("print('hello')")
        >>> result['data']['stdout']
        'hello\\n'
    """
    client = from_env()
    image = os.environ.get("PYTHON_EXECUTOR_IMAGE", "python:3.10.18-slim")
    container_name = "simple_agent_python_runner"

    try:
        # Get or create container
        try:
            container = client.containers.get(container_name)
            if container.status != "running":
                container.start()
                # Wait for ready
                for _ in range(10):
                    container.reload()
                    if container.status == "running":
                        break
                    time.sleep(0.2)
        except docker_errors.NotFound:
            # Pull image if needed
            try:
                client.images.get(image)
            except docker_errors.ImageNotFound:
                client.images.pull(image)

            # Create persistent container
            container = client.containers.run(
                image,
                ["sleep", "infinity"],
                name=container_name,
                detach=True,
                tty=True,
                network_mode="none",  # No network access
                mem_limit="512m",  # Memory limit
                cpu_quota=50000,  # CPU limit
            )

            # Wait for ready
            for _ in range(10):
                container.reload()
                if container.status == "running":
                    break
                time.sleep(0.2)

        # Execute code
        exec_result = container.exec_run(
            ["python", "-c", code],
            demux=True
        )

        exit_code = exec_result.exit_code
        stdout, stderr = exec_result.output if exec_result.output else (b"", b"")

        result_data = {
            "stdout": stdout.decode("utf-8") if stdout else "",
            "stderr": stderr.decode("utf-8") if stderr else "",
            "exit_code": exit_code,
        }

        if exit_code == 0:
            return {
                "success": True,
                "data": result_data,
                "message": "Python code executed successfully"
            }
        else:
            return {
                "success": False,
                "data": result_data,
                "message": f"Python code failed with exit code {exit_code}"
            }

    except Exception as e:
        return {
            "success": False,
            "data": None,
            "message": f"Error: {str(e)}"
        }


def cleanup_python_executor():
    """Cleanup function to stop and remove container."""
    try:
        client = from_env()
        container = client.containers.get("simple_agent_python_runner")
        container.stop()
        container.remove()
    except Exception:
        pass  # Container doesn't exist or already stopped
```

### 3. Tool Registry

**File:** `simple_agent/tools/registry.py`

```python
"""Tool registry for managing available tools."""

from typing import Dict, Any
from smolagents import Tool

# Global tool registry
_TOOLS: Dict[str, Tool] = {}

def register_tool(tool: Tool) -> None:
    """Register a tool."""
    _TOOLS[tool.name] = tool

def get_tool(name: str) -> Tool:
    """Get tool by name."""
    if name not in _TOOLS:
        raise KeyError(f"Tool '{name}' not found")
    return _TOOLS[name]

def list_tools() -> list[str]:
    """List all registered tools."""
    return list(_TOOLS.keys())

def get_tools_for_agent(tool_names: list[str]) -> list[Tool]:
    """Get tool instances for agent initialization."""
    return [get_tool(name) for name in tool_names]
```

### 4. Tool Loading in AgentManager

**File:** `simple_agent/core/agent_manager.py`

**Updates:**

```python
from simple_agent.tools.registry import get_tools_for_agent

class AgentManager:
    def create_agent(
        self,
        name: str,
        provider: Optional[str] = None,
        role: Optional[str] = None,
        template: Optional[str] = None,
        agent_type: Optional[str] = None,  # NEW
    ) -> SimpleAgent:
        # ... existing code ...

        # Get agent type from config or use default
        agent_type = agent_type or self.config.get("agents", {}).get("default", {}).get("agent_type", "tool_calling")

        # Get tools for this agent
        tool_names = self.config.get("agents", {}).get(name, {}).get("tools", [])
        if not tool_names:
            tool_names = self.config.get("agents", {}).get("default", {}).get("tools", [])

        tools = get_tools_for_agent(tool_names) if tool_names else []

        # Create agent with type
        agent = SimpleAgent(
            name=name,
            model_provider=provider,
            model_config=model_config,
            agent_type=agent_type,  # NEW
            role=role,
            template=template,
            tools=tools,  # NEW
            verbosity=verbosity,
            max_steps=max_steps,
        )

        return agent
```

---

## Configuration Changes

### Config Schema Updates

**File:** `config.yaml`

```yaml
# Agent Settings
agents:
  default:
    agent_type: "tool_calling"  # NEW: "tool_calling" | "code" | "multi_step"
    role: "You are a helpful AI assistant."
    tools:  # NEW: List of tool names
      - python_executor
    verbosity: 1
    max_steps: 10

# Tool Settings
tools:  # NEW section
  python_executor:
    enabled: true
    docker_image: "python:3.10.18-slim"
    timeout: 30
    memory_limit: "512m"
    cpu_quota: 50000
    network_enabled: false  # Security: no network access

# Security Settings
security:  # NEW section
  allow_local_code_execution: false  # Must be false
  require_docker: true  # Must be true for code execution
```

### Environment Variables

**.env updates:**
```bash
# Docker image for Python execution
PYTHON_EXECUTOR_IMAGE=python:3.10.18-slim

# Docker Hub credentials (optional, for private images)
DOCKER_USERNAME=
DOCKER_PASSWORD=
```

---

## Security Validation

### Validation Rules

1. **Never allow `executor_type="local"` for CodeAgent**
2. **Require Docker installed if using code execution**
3. **Validate agent_type is in allowed list**
4. **Validate tool names exist before loading**
5. **Enforce resource limits on Docker containers**

### Validation Implementation

**File:** `simple_agent/core/security.py` (NEW)

```python
"""Security validation for agent configuration."""

import os
from typing import Dict, Any

class SecurityError(Exception):
    """Raised when security validation fails."""
    pass

def validate_agent_config(config: Dict[str, Any]) -> None:
    """
    Validate agent configuration for security issues.

    Raises:
        SecurityError: If configuration is insecure
    """
    # Check local code execution not allowed
    if config.get("security", {}).get("allow_local_code_execution", False):
        raise SecurityError(
            "Local code execution is not allowed. "
            "Set security.allow_local_code_execution to false."
        )

    # Check Docker required
    if config.get("security", {}).get("require_docker", True):
        try:
            from docker import from_env
            client = from_env()
            client.ping()
        except Exception as e:
            raise SecurityError(
                f"Docker is required but not available: {e}. "
                "Please install Docker or disable code execution features."
            )

def validate_agent_type(agent_type: str, executor_type: str = "docker") -> None:
    """
    Validate agent type configuration.

    Raises:
        SecurityError: If configuration is insecure
    """
    valid_types = ["tool_calling", "code", "multi_step"]
    if agent_type not in valid_types:
        raise ValueError(f"Invalid agent_type: {agent_type}. Must be one of: {valid_types}")

    if agent_type == "code" and executor_type == "local":
        raise SecurityError(
            "CodeAgent with executor_type='local' is not allowed for security reasons. "
            "Use executor_type='docker' or switch to agent_type='tool_calling'."
        )
```

---

## Testing Strategy

### Unit Tests

**File:** `tests/unit/test_agent_types.py` (NEW)

```python
class TestAgentTypeSelection:
    """Test agent type selection logic."""

    def test_tool_calling_agent_default(self):
        """Test ToolCallingAgent is default."""
        pass

    def test_code_agent_requires_docker_executor(self):
        """Test CodeAgent rejects local executor."""
        pass

    def test_invalid_agent_type_raises_error(self):
        """Test invalid agent type raises ValueError."""
        pass
```

**File:** `tests/unit/test_python_executor_tool.py` (NEW)

```python
class TestPythonExecutorTool:
    """Test Python executor tool."""

    @patch("docker.from_env")
    def test_successful_execution(self, mock_docker):
        """Test successful code execution."""
        pass

    @patch("docker.from_env")
    def test_error_handling(self, mock_docker):
        """Test error handling."""
        pass

    @patch("docker.from_env")
    def test_container_reuse(self, mock_docker):
        """Test persistent container reuse."""
        pass
```

**File:** `tests/unit/test_security_validation.py` (NEW)

```python
class TestSecurityValidation:
    """Test security validation logic."""

    def test_reject_local_code_execution(self):
        """Test local code execution is rejected."""
        pass

    def test_require_docker_for_code_agent(self):
        """Test Docker requirement for CodeAgent."""
        pass

    def test_validate_agent_config(self):
        """Test agent config validation."""
        pass
```

### Integration Tests

**File:** `tests/integration/test_agent_types_integration.py` (NEW)

```python
class TestAgentTypesIntegration:
    """Integration tests for agent types."""

    @patch("simple_agent.agents.simple_agent.ToolCallingAgent")
    @patch("docker.from_env")
    def test_tool_calling_agent_with_python_tool(self, mock_docker, mock_agent):
        """Test ToolCallingAgent with Python executor tool."""
        pass

    @patch("simple_agent.agents.simple_agent.CodeAgent")
    @patch("docker.from_env")
    def test_code_agent_with_docker_executor(self, mock_docker, mock_agent):
        """Test CodeAgent with Docker executor."""
        pass
```

**File:** `tests/integration/test_docker_python_execution.py` (NEW)

```python
@pytest.mark.skipif(not has_docker(), reason="Docker not available")
class TestDockerPythonExecution:
    """Integration tests for Docker-based Python execution."""

    def test_simple_print_statement(self):
        """Test executing simple print statement."""
        pass

    def test_code_with_error(self):
        """Test handling of code with errors."""
        pass

    def test_timeout_handling(self):
        """Test timeout enforcement."""
        pass

    def test_container_cleanup(self):
        """Test proper container cleanup."""
        pass
```

### Test Coverage Requirements

- **Unit tests:** >90% coverage for new code
- **Integration tests:** All agent types tested
- **Security tests:** All validation paths covered
- **Docker tests:** Skipped if Docker not available

---

## Implementation Order (TDD)

### Step 1: Security Validation (Day 1 Morning)
1. Write tests for security validation
2. Implement `simple_agent/core/security.py`
3. Run tests, verify all pass

### Step 2: Python Executor Tool (Day 1 Afternoon)
1. Write unit tests for Python executor tool
2. Implement `simple_agent/tools/python_executor.py`
3. Write integration tests (Docker required)
4. Run tests, verify all pass

### Step 3: Tool Registry (Day 2 Morning)
1. Write tests for tool registry
2. Implement `simple_agent/tools/registry.py`
3. Register Python executor tool on import
4. Run tests, verify all pass

### Step 4: Agent Type Support (Day 2 Afternoon)
1. Write tests for agent type selection
2. Refactor `SimpleAgent` to support agent types
3. Update `AgentManager` to pass agent type
4. Run tests, verify all pass

### Step 5: Configuration Updates (Day 3 Morning)
1. Update `config.yaml` schema
2. Update config validation
3. Add security validation to config loading
4. Test configuration loading

### Step 6: Integration & Documentation (Day 3 Afternoon)
1. Run all integration tests
2. Test manually in REPL
3. Update documentation
4. Code review and cleanup

---

## Dependencies

### Required Packages

Add to `requirements.txt`:
```txt
docker>=7.0.0
```

### System Requirements

- **Docker:** Must be installed and running
- **Docker permissions:** User must have docker group access (Linux) or Docker Desktop running (Mac/Windows)

### Verification Script

**File:** `utils/check_docker.py` (NEW)

```python
#!/usr/bin/env python
"""Check if Docker is available and working."""

from docker import from_env
import sys

try:
    client = from_env()
    client.ping()
    version = client.version()
    print(f"✅ Docker is available")
    print(f"   Version: {version.get('Version', 'unknown')}")
    sys.exit(0)
except Exception as e:
    print(f"❌ Docker is not available: {e}")
    print("\nPlease install Docker:")
    print("  - Mac: https://docs.docker.com/desktop/install/mac-install/")
    print("  - Linux: https://docs.docker.com/engine/install/")
    print("  - Windows: https://docs.docker.com/desktop/install/windows-install/")
    sys.exit(1)
```

---

## Acceptance Criteria

### Must Have

- [  ] No local code execution possible (all tests verify this)
- [  ] ToolCallingAgent working as default
- [  ] Python executor tool working with Docker
- [  ] Security validation prevents unsafe configs
- [  ] All unit tests passing (>90% coverage)
- [  ] Integration tests passing (with Docker available)
- [  ] Config schema documented and validated
- [  ] Phase 0.5 documentation complete

### Nice to Have

- [  ] Docker image caching for faster startup
- [  ] Container resource monitoring
- [  ] Tool execution timeout enforcement
- [  ] Detailed error messages for Docker issues

### Out of Scope (Deferred)

- Interactive chat mode (Phase 1)
- Tool auto-discovery (Phase 1)
- MultiStepAgent implementation (future)
- CodeAgent implementation (only if needed)

---

## Risk & Mitigation

### Risks

1. **Docker not available on user's system**
   - Mitigation: Clear error messages, setup instructions
   - Fallback: Provide cloud execution option (E2B) in future

2. **Docker performance overhead**
   - Mitigation: Persistent container, caching
   - Monitoring: Track execution times

3. **Breaking changes from Phase 0**
   - Mitigation: All Phase 0 tests still pass
   - Migration: Auto-upgrade to ToolCallingAgent

4. **Tool complexity**
   - Mitigation: Simple as possible, well documented
   - Examples: Provide working examples

---

## Success Metrics

- ✅ Zero local code execution vulnerabilities
- ✅ 100% test coverage on security validation
- ✅ All Phase 0 functionality preserved
- ✅ Docker execution working reliably
- ✅ Clear documentation and examples
- ✅ Performance acceptable (<2s cold start)

---

## References

- [SmolAgents Documentation](https://huggingface.co/docs/smolagents)
- [SmolAgents Security Guide](https://huggingface.co/docs/smolagents/en/tutorials/secure_code_execution)
- [Docker Python SDK](https://docker-py.readthedocs.io/)
- Agent-builder python_code.py implementation
