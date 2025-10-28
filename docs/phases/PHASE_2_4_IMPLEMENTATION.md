# Phase 2.4: Multi-Agent Orchestration - Implementation Plan

**Status:** Ready for Implementation
**Approach:** Industry Standard Orchestrator Pattern (not SmolAgents-native)
**Estimated Effort:** 4-5 hours
**TDD Methodology:** Tests first, then implementation
**Reference:** OpenAI, Microsoft Azure, Arize, Anthropic patterns

---

## Overview

Phase 2.4 implements the **industry-standard orchestrator agent pattern** where a specialized **Orchestrator Agent** reasons about which agents to call, in what order, and whether outputs meet quality thresholds. This leverages SmolAgents' built-in ReAct iteration at both the agent and orchestration levels.

This is the proven pattern used by:
- **OpenAI:** https://openai.github.io/openai-agents-python/multi_agent/
- **Microsoft Azure:** https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
- **Arize:** https://arize.com/blog/orchestrator-worker-agents-a-practical-comparison-of-common-agent-frameworks/

**Core Concept - ReAct at Two Levels:**

```
Level 1: ORCHESTRATOR REASONING (ReAct Loop)
┌─────────────────────────────────────────────────────────┐
│ Orchestrator Agent [Reason→Act→Reason→Act...]           │
│                                                          │
│ Step 1: Reason: "Need to research, then check quality" │
│         Act: Call Agent A (research_agent)              │
│         ↓                                                │
│ Level 2: SUB-AGENT EXECUTION (Also ReAct Loop)          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ Agent A [Reason→Act→Reason→Act...]               │   │
│ │                                                   │   │
│ │ Step 1: Reason: "Need web search"               │   │
│ │         Act: Call web_search tool                │   │
│ │         Observe: Got 5 results                   │   │
│ │                                                   │   │
│ │ Step 2: Reason: "Need to read top source"       │   │
│ │         Act: Call visit_webpage tool             │   │
│ │         Observe: Got full article                │   │
│ │                                                   │   │
│ │ Step 3: Reason: "Have enough info, synthesize"  │   │
│ │         Act: Generate response                   │   │
│ │         Result: "Research findings..."           │   │
│ └──────────────────────────────────────────────────┘   │
│ Back to orchestrator...                                 │
│ Step 2: Reason: "Got research, now check quality"      │
│         Act: Call Agent B (quality_checker)             │
│         ↓ (Agent B also iterates internally)            │
│ Step 3: Reason: "Quality is 8.5/10, meets threshold"   │
│         Act: Call Agent C (writer)                      │
│         ↓ (Agent C also iterates internally)            │
│ Step 4: Reason: "Got final output, done"               │
│         Act: Return final result                        │
└─────────────────────────────────────────────────────────┘
```

**Key Point: ReAct Iteration at Both Levels**
- **Orchestrator Level:** Reasons about WHICH agents to call, in WHAT ORDER, based on intermediate results
- **Sub-Agent Level:** Each agent internally iterates (reason→act→reason) using its own tools (web search, APIs, etc.)
- **Metadata Tracked at Both Levels:**
  - Orchestrator: Which agents called, order, reasoning
  - Sub-agents: Tool usage, execution time, steps taken

**Why This Approach?**
- ✅ Industry-proven pattern (OpenAI, Microsoft, Google use this)
- ✅ Built on SimpleAgent (no new framework dependencies)
- ✅ Leverages BOTH levels of ReAct iteration for intelligent workflows
- ✅ AgentTool wrapper makes agents callable while preserving internal iteration
- ✅ Metadata tracking via execution hooks at orchestration level
- ✅ Sub-agents maintain their own memory (Phase 1.2) for internal iteration
- ✅ Flexible intelligent routing via orchestrator reasoning
- ✅ Easy to understand and maintain
- ℹ️ Note: NOT relying on SmolAgents' removed ManagedAgent feature

---

## Agent Configuration for Multi-Step Orchestration

Each agent in Phase 2.4 needs configuration to support multi-step (ReAct) iteration. This is already defined in the YAML agent config files:

### Individual Agent Configuration: `config/agents/{agent_name}.yaml`

```yaml
name: "researcher"
agent_type: "tool_calling"

role: |
  You are a research specialist.
  Find accurate information, analyze data, provide well-sourced answers.
  Cite your sources and explain reasoning clearly.

tools:
  - web_search      # Tools available to THIS agent for internal iteration
  - visit_webpage
  - fact_validator

model:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.3
  max_tokens: 2000

settings:
  verbosity: 2      # 0=quiet, 1=normal, 2=verbose (shows reasoning steps)
  max_steps: 15     # Max internal ReAct iterations for this agent
                    # Important: Needs to be HIGH enough for complex tasks

metadata:
  description: "Research and information gathering specialist"
  author: "system"
  version: "1.0.0"
```

### Key Settings for Multi-Step Support

| Setting | Purpose | Value | Notes |
|---------|---------|-------|-------|
| `max_steps` | Max internal ReAct iterations | 10-20 | Higher = more reasoning, higher cost |
| `verbosity` | Show reasoning process | 2 (verbose) | Helps debug agent thinking |
| `tools` | Tools agent can use internally | List of tool names | Each tool is one possible "act" in ReAct loop |
| `temperature` | Reasoning creativity | 0.3-0.7 | Lower = more consistent reasoning |

### Orchestrator Agent Configuration: Special Role for Reasoning About Agents

The orchestrator agent is configured similarly but with a special role:

```yaml
name: "orchestrator"
agent_type: "tool_calling"

role: |
  You are a workflow orchestrator. Your job is to coordinate other agents.

  Available agents you can call (they are your "tools"):
  - researcher: Handles research and information gathering
  - quality_checker: Validates work quality and provides feedback
  - writer: Creates polished written content

  Your reasoning process:
  1. Analyze the user's request
  2. Decide which agent(s) to call and in what order
  3. Evaluate their outputs for quality
  4. Route to next agent or refine based on results
  5. Synthesize final output

  Make intelligent decisions about:
  - Which agents are needed
  - When to retry an agent with feedback
  - How to combine outputs from multiple agents

model:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.5

settings:
  verbosity: 2
  max_steps: 20      # Orchestrator needs MORE steps to coordinate agents
```

### Phase 1.5 & 1.6 Already Support This

- **Phase 1.5 (YAML Agent Definitions):** Agent configs load from YAML ✅
- **Phase 1.6 (User Prompt Templates):** User prompts can be templated ✅
- **Phase 1.7 (Jinja2 Templates):** Dynamic templates for agent prompts ✅

**No changes needed to existing phases** - they already support multi-step agent configs.

---

## Verbosity Hierarchy: YAML vs Debug Command

**Question:** Does the `verbosity` setting in agent YAML override the `/debug` command?

**Answer:** NO - There are TWO SEPARATE verbosity systems with a clear hierarchy:

### System 1: Application-Level Debug (via `/debug` command)

Controls **Python logging and LiteLLM output** at the application level:

```bash
/debug off     # Suppress INFO logs, show only WARNINGS
/debug info    # Normal output (LiteLLM INFO logs visible)
/debug debug   # Full debug mode (LiteLLM DEBUG logs visible)
```

**Scope:** Affects ALL agents in the entire application
**Controls:** Python `logging` level, LiteLLM verbosity
**Set via:** `/debug` command (runtime) or `--debug` CLI flag (launch time)

### System 2: Agent-Level Verbosity (via YAML `settings.verbosity`)

Controls **SmolAgents ReAct step output** for individual agents:

```yaml
settings:
  verbosity: 0  # Suppress agent internal reasoning
  verbosity: 1  # Normal agent output (default)
  verbosity: 2  # Show agent reasoning steps (best for multi-step)
```

**Scope:** Affects individual agent's internal ReAct iteration
**Controls:** SmolAgents `LogLevel` (OFF, INFO, DEBUG)
**Set via:** Agent YAML config or `create_agent(verbosity=...)`

### The Hierarchy (Priority Order)

```
1. CLI --debug flag        (highest priority - overrides config)
   ↓
2. /debug command          (runtime change, overrides config)
   ↓
3. config.yaml debug.level (default for application)

(These control Python logging & LiteLLM)

SEPARATE SYSTEM:
   ↓
1. Agent YAML verbosity    (controls SmolAgents ReAct output)
   ↓
2. create_agent(verbosity) (programmatic override)

(These control individual agent reasoning display)
```

### Real Example

```bash
# Start with debug off
python -m simple_agent.app --debug off

# Load agent configured with verbosity: 2
/agent create researcher config/agents/researcher.yaml
# researcher.yaml has: settings: verbosity: 2

# Now run agent
/agent run researcher "Research quantum computing"
```

**What happens:**
- Application debug level = `off` (suppresses Python logging)
- Agent verbosity = `2` (shows SmolAgents reasoning steps)
- **Result:** You see agent's reasoning steps, but NOT Python debug logs

**Change debug level:**
```bash
/debug debug  # Turn on application-level debugging

# Run same agent again:
/agent run researcher "Research quantum computing"
```

**Result:** You see BOTH agent reasoning (from verbosity: 2) AND Python/LiteLLM debug logs (from /debug debug)

### Code Implementation (Already in SimpleAgent)

```python
# From simple_agent.py lines 90-96
verbosity_level = LogLevel.DEBUG if debug_enabled else LogLevel.INFO
logger.debug(
    f"Agent '{name}' verbosity set to {verbosity_level.name} "
    f"(debug_enabled={debug_enabled})"
)
```

**Note:** The `debug_enabled` parameter here is DEPRECATED. It's only used for backward compatibility. The actual debug level comes from the application context (set via `/debug` command).

### Best Practice for Phase 2.4

For multi-agent orchestration, we recommend:

**In orchestrator YAML:**
```yaml
settings:
  verbosity: 2      # Show orchestrator reasoning about agents
  max_steps: 20
```

**In sub-agent YAML:**
```yaml
settings:
  verbosity: 1      # Normal output (less noise)
  max_steps: 15
```

**In REPL:**
```bash
# For development/debugging:
/debug debug
/agent run orchestrator "Complex task"
# Shows: agent reasoning + Python logs + LiteLLM debug

# For production:
/debug off
/agent run orchestrator "Complex task"
# Shows: only SmolAgents output from verbosity setting
```

**In configuration file (`config.yaml`):**
```yaml
debug:
  level: "info"  # Default debug level

agents:
  default:
    verbosity: 1   # Default agent verbosity
```

---

## Architecture Design

### Component Overview

```
┌────────────────────────────────────────────────────┐
│          Orchestrator System                        │
├────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │  FlowManager                                │  │
│  │  - load_flow()                              │  │
│  │  - execute_flow()                           │  │
│  │  - validate_flow()                          │  │
│  └─────────────────────────────────────────────┘  │
│                      ↓                             │
│  ┌─────────────────────────────────────────────┐  │
│  │  OrchestratorAgent                          │  │
│  │  - reason about workflow execution          │  │
│  │  - call sub-agents as tools                 │  │
│  │  - evaluate outputs vs thresholds           │  │
│  │  - manage fallback strategies               │  │
│  └─────────────────────────────────────────────┘  │
│                      ↓                             │
│  ┌─────────────────────────────────────────────┐  │
│  │  AgentTool Wrapper                          │  │
│  │  - wrap agents as callable tools            │  │
│  │  - handle output formatting                 │  │
│  │  - track execution metadata                 │  │
│  └─────────────────────────────────────────────┘  │
│                      ↓                             │
│  ┌─────────────────────────────────────────────┐  │
│  │  Sub-Agents (existing agents)               │  │
│  │  - Researcher, Summarizer, Writer, etc.    │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
└────────────────────────────────────────────────────┘
```

### Key Classes to Implement

#### 1. AgentTool
Wraps an agent to make it callable as a tool by the Orchestrator.

```python
class AgentTool:
    """Wrapper that exposes an agent as a callable tool."""

    def __init__(
        self,
        name: str,
        agent: SimpleAgent,
        description: str,
        expected_output_format: str = "text"  # or "structured"
    ):
        self.name = name
        self.agent = agent
        self.description = description
        self.expected_output_format = expected_output_format
        self.call_history = []  # Track executions

    def __call__(self, prompt: str) -> dict:
        """
        Execute agent and return structured result.

        Returns:
            {
                "status": "success" | "failure",
                "output": str,
                "metadata": {
                    "agent_name": str,
                    "execution_time": float,
                    "confidence": float (0-1),
                    "tool_calls": int,
                    "steps": int
                }
            }
        """
        pass

    def __repr__(self) -> str:
        return f"AgentTool(name='{self.name}', agent='{self.agent.name}')"
```

#### 2. OrchestratorAgent
Meta-agent that coordinates other agents.

```python
class OrchestratorAgent:
    """Meta-agent that reasons about agent orchestration."""

    def __init__(
        self,
        name: str,
        role: str,
        model_provider: str,
        model_config: dict,
        sub_agents: dict,  # {agent_name: AgentTool}
        verbosity: int = 1,
        max_steps: int = 15
    ):
        self.name = name
        self.role = role
        self.model_provider = model_provider
        self.model_config = model_config
        self.sub_agents = sub_agents  # Sub-agents as tools

        # Create internal SimpleAgent with sub-agents as tools
        self.agent = SimpleAgent(
            name=name,
            role=role,
            model_provider=model_provider,
            model_config=model_config,
            tools=list(sub_agents.values()),
            verbosity=verbosity,
            max_steps=max_steps
        )

    def run(self, prompt: str) -> str:
        """
        Run orchestrator - it reasons about which agents to call.

        Returns:
            Final response from orchestrator after coordinating sub-agents.
        """
        return self.agent.run(prompt)
```

#### 3. FlowManager
Loads and manages orchestrator workflows.

```python
class FlowManager:
    """Manages orchestrator flows."""

    def __init__(self, agent_manager, flows_dir: str = "config/flows"):
        self.agent_manager = agent_manager
        self.flows_dir = flows_dir
        self.flows = {}  # Loaded flows
        self.executors = {}  # Active flow executions

    def load_flow(self, flow_path: str) -> dict:
        """
        Load flow definition from YAML.

        Returns:
            {
                "name": str,
                "description": str,
                "orchestrator": {
                    "name": str,
                    "role": str,
                    "sub_agents": [str, ...]
                },
                "metadata": {...}
            }
        """
        pass

    def create_orchestrator(self, flow_def: dict) -> OrchestratorAgent:
        """Create orchestrator agent from flow definition."""
        pass

    def validate_flow(self, flow_def: dict) -> tuple[bool, list]:
        """
        Validate flow definition.

        Returns:
            (is_valid: bool, errors: list[str])
        """
        pass

    def list_flows(self) -> list[str]:
        """List available flows."""
        pass
```

---

## YAML Flow Format (Option B)

The Orchestrator Agent approach uses a simplified YAML format:

```yaml
name: "research_workflow"
description: "Research, summarize, and write report"

# Define which agents the orchestrator can use
sub_agents:
  - name: "researcher"
    description: "Research a topic and return findings"
    config: "config/agents/researcher.yaml"

  - name: "quality_checker"
    description: "Check quality and provide feedback"
    config: "config/agents/quality_checker.yaml"

  - name: "summarizer"
    description: "Summarize findings into concise overview"
    config: "config/agents/summarizer.yaml"

  - name: "writer"
    description: "Write polished reports based on findings"
    config: "config/agents/writer.yaml"

# Orchestrator configuration
orchestrator:
  name: "research_coordinator"
  role: |
    You are a research workflow coordinator. Your tools are specialized agents:
    - researcher: Deep research on topics
    - quality_checker: Validates work quality
    - summarizer: Creates concise summaries
    - writer: Writes professional reports

    Your workflow:
    1. Call researcher to gather information
    2. Call quality_checker to validate research
    3. If quality < 8, call researcher again with feedback
    4. Call summarizer to condense findings
    5. Call writer to create final report

    Make intelligent decisions about which agents to call based on the request.
    Evaluate output quality and retry if needed.

  model:
    provider: "openai"
    model: "gpt-4o-mini"
    temperature: 0.7

  settings:
    max_steps: 20
    verbosity: 1

metadata:
  version: "1.0"
  created_by: "user"
  tags: ["research", "multi-agent"]
```

---

## Implementation Phases (TDD Order)

### Phase 1: AgentTool Wrapper (0.5 hours)

**Tests First:**
1. `test_agent_tool_creation` - Create AgentTool from agent
2. `test_agent_tool_call` - Call agent tool with prompt
3. `test_agent_tool_output_format` - Verify output structure
4. `test_agent_tool_metadata` - Track execution metadata
5. `test_agent_tool_history` - Track call history

**Implementation:**
- Create `simple_agent/orchestration/__init__.py`
- Create `simple_agent/orchestration/agent_tool.py` (50-75 lines)
- Implement `__call__()` to wrap agent execution
- Track metadata: execution_time, tool_calls, steps

**Files:**
- `tests/unit/test_agent_tool.py` (5 tests)

**Human Testing (REPL):**
Once unit tests pass, you can test in REPL:
```bash
# This won't work yet (Phase 2 not finished) but shows the goal:

# Future: Expose AgentTool as callable
# For now: Just verify imports work and no errors
python -c "from simple_agent.orchestration.agent_tool import AgentTool; print('✓ AgentTool imports')"
```

**Note:** Phase 1 is internal infrastructure. Real REPL testing starts in Phase 2.

---

### Phase 2: OrchestratorAgent (1 hour)

**Tests First:**
1. `test_orchestrator_creation` - Create orchestrator with sub-agents
2. `test_orchestrator_run` - Run orchestrator (mocked LLM)
3. `test_orchestrator_uses_agent_tools` - Verify agent tools available
4. `test_orchestrator_memory` - Memory persistence across calls
5. `test_orchestrator_output_parsing` - Parse orchestrator output

**Implementation:**
- Create `simple_agent/orchestration/orchestrator_agent.py` (75-100 lines)
- Extend SimpleAgent with sub-agents as tools
- Implement `run()` to execute orchestration
- Handle tool output aggregation

**Files:**
- `tests/unit/test_orchestrator_agent.py` (5 tests)

**Human Testing (REPL):**
Once unit and integration tests pass, you can test in REPL:
```bash
# Start REPL
python -m simple_agent.app

# Create some sub-agents first
/agent create researcher config/agents/researcher.yaml
/agent create writer config/agents/writer.yaml

# Create orchestrator agent with sub-agents as tools
# (Command not added yet - Phase 3)
# This will work after Phase 3 FlowManager is complete
```

**What You Can Verify:**
- ✅ Orchestrator agent created successfully with other agents as tools
- ✅ Orchestrator can call sub-agents (via `agent.tools` list)
- ✅ Output from sub-agents is captured in orchestrator's response
- ✅ Memory is maintained across calls
- ⚠️ No REPL commands yet (that's Phase 3)

---

### Phase 3: FlowManager & YAML Loading (1.5 hours)

**Tests First:**
1. `test_load_flow_from_yaml` - Load flow definition
2. `test_validate_flow_valid` - Validate correct flow
3. `test_validate_flow_invalid` - Reject invalid flow
4. `test_create_orchestrator_from_flow` - Create from YAML
5. `test_flow_manager_list_flows` - List available flows
6. `test_flow_manager_load_agents` - Resolve agent configs

**Implementation:**
- Create `simple_agent/orchestration/flow_manager.py` (100-150 lines)
- YAML parsing with validation
- Agent resolution (load referenced agent configs)
- Orchestrator creation from flow definition
- Error handling for missing agents/configs

**Files:**
- `simple_agent/orchestration/flow_manager.py`
- `simple_agent/orchestration/flow_validator.py` (50-75 lines)
- `tests/unit/test_flow_manager.py` (6 tests)
- `tests/unit/test_flow_validator.py` (3 tests)
- `config/flows/example_research.yaml` (example flow)

**Human Testing (REPL):**
Once unit and integration tests pass, you can test in REPL:
```bash
# Start REPL
python -m simple_agent.app

# Create agents that will be used in the flow
/agent create researcher config/agents/researcher.yaml
/agent create quality_checker config/agents/quality_checker.yaml
/agent create writer config/agents/writer.yaml

# Load a flow from YAML (Phase 4 commands not added yet)
# This is tested programmatically for now
# /flow load research_workflow config/flows/example_research.yaml
```

**What You Can Verify:**
- ✅ Flow YAML files load without errors
- ✅ Flow validator catches invalid configs
- ✅ Agent references in flows resolve correctly
- ✅ Orchestrator created from flow with correct sub-agents
- ✅ Flow Manager lists available flows
- ⚠️ No REPL commands yet (that's Phase 4)
- ⚠️ No flow execution yet (that needs orchestrator running)

---

### Phase 4: REPL Commands (1 hour)

**Tests First:**
1. `test_flow_create_command` - `/flow create <name>`
2. `test_flow_list_command` - `/flow list`
3. `test_flow_run_command` - `/flow run <name> "input"`
4. `test_flow_show_command` - `/flow show <name>`
5. `test_flow_delete_command` - `/flow delete <name>`
6. `test_flow_debug_command` - `/flow debug <name> "input"`

**Implementation:**
- Create `simple_agent/commands/flow_commands.py` (150-200 lines)
- Command handlers for flow management
- Output formatting with rich tables
- Error handling and user feedback

**Files:**
- `simple_agent/commands/flow_commands.py`
- `tests/unit/test_flow_commands.py` (6 tests)

**Human Testing (REPL):**
Once unit and integration tests pass, you can test in REPL:
```bash
# Start REPL
python -m simple_agent.app

# List available flows
/flow list
# Output:
#   research_workflow  - Research, summarize, and write report

# Show flow definition
/flow show research_workflow
# Output: (YAML formatted, shows agents and orchestrator config)

# Run a flow with input
/flow run research_workflow "Tell me about quantum computing"
# Output: Orchestrator reasoning + final result

# Debug flow execution step-by-step
/flow debug research_workflow "quantum computing"
# Output: Each step shown with reasoning, agent calls, outputs

# Create a new flow from template (if implemented)
/flow create my_workflow --template research
```

**What You Can Do:**
- ✅ List all available flows
- ✅ Show flow definition in readable format
- ✅ Run flows with natural language input
- ✅ See orchestrator's reasoning about which agents to call
- ✅ See sub-agent outputs as they're called
- ✅ Debug flows step-by-step to understand execution
- ✅ Full multi-agent orchestration in REPL!

**Demonstration Workflow:**
```bash
# 1. Create researcher and writer agents
/agent create researcher config/agents/researcher.yaml
/agent create writer config/agents/writer.yaml

# 2. List available flows
/flow list

# 3. Run research workflow
/flow run research_workflow "What is artificial intelligence?"

# Expected output:
# [Orchestrator reasoning about calling agents]
# Calling researcher agent...
# [Researcher finds info, returns results]
# Calling writer agent...
# [Writer creates article from research]
# Final result: [Complete article]
```

---

### Phase 5: Integration Tests & E2E (1 hour)

**Tests:**
1. `test_full_workflow_sequential` - End-to-end sequential flow
2. `test_full_workflow_with_quality_check` - Flow with feedback loop
3. `test_orchestrator_handles_agent_failure` - Error handling
4. `test_repl_flow_commands_integration` - REPL commands work
5. `test_flow_with_guardrails` - Integration with Phase 2.1
6. `test_flow_with_hitl_agents` - Integration with Phase 2.2
7. `test_flow_with_rag_agents` - Integration with Phase 2.3

**Files:**
- `tests/integration/test_phase_2_4.py` (7 tests)

**Human Testing (REPL):**
This phase is purely testing. All REPL functionality is already available from Phase 4.

**Advanced Scenarios You Can Test:**
```bash
# Test with RAG-enabled researcher
/agent create researcher config/agents/researcher.yaml  # with RAG
/flow run research_workflow "What's in my documents?"

# Test with approval gates (Phase 2.2 integration)
# Writer agent might ask for approval on sensitive outputs
/approve
# or
/reject

# Test with guardrails (Phase 2.1 integration)
# Try input with PII - guardrails should block it
/flow run research_workflow "Contact john@example.com about project"
# [Guardrails block PII, returns error]

# Test orchestrator error recovery
/flow run research_workflow "Research X" --verbose
# See orchestrator reasoning about handling failures
```

**Integration Points Verified:**
- ✅ Phase 2.1 Guardrails: Applied to orchestrator + sub-agents
- ✅ Phase 2.2 HITL: Approval gates work for sensitive operations
- ✅ Phase 2.3 RAG: Researcher can access documents
- ✅ Error handling: Orchestrator recovers gracefully from failures
- ✅ Memory: Agents maintain history across calls

---

## Implementation Order & Tasks

```
Week 1, Day 1-2:
├─ Phase 1: AgentTool (0.5h)
│  ├─ Write 5 unit tests
│  └─ Implement AgentTool
│
├─ Phase 2: OrchestratorAgent (1h)
│  ├─ Write 5 unit tests
│  └─ Implement OrchestratorAgent
│
└─ Phase 3: FlowManager (1.5h)
   ├─ Write 9 unit tests
   └─ Implement FlowManager + FlowValidator

Week 1, Day 3:
├─ Phase 4: REPL Commands (1h)
│  ├─ Write 6 unit tests
│  └─ Implement flow_commands.py
│
└─ Phase 5: Integration & Polish (1h)
   ├─ Write 7 integration tests
   └─ Fix issues, update docs

Total: 5-6 hours
```

---

## Test Strategy (TDD)

### Unit Test Structure

```python
# tests/unit/test_agent_tool.py
class TestAgentTool:
    """AgentTool wraps agents as tools for orchestrators."""

    def test_agent_tool_creation(self):
        """AgentTool can be created from agent with name/description."""
        pass

    def test_agent_tool_call(self):
        """Calling AgentTool executes wrapped agent."""
        pass

    def test_agent_tool_output_format(self):
        """AgentTool returns structured output dict."""
        output = agent_tool("test prompt")
        assert "status" in output
        assert "output" in output
        assert "metadata" in output
        assert output["status"] in ["success", "failure"]

    def test_agent_tool_metadata_tracking(self):
        """AgentTool tracks execution metadata."""
        # execution_time, tool_calls, steps, confidence
        pass

    def test_agent_tool_history(self):
        """AgentTool maintains call history."""
        pass
```

### Integration Test Structure

```python
# tests/integration/test_phase_2_4.py
class TestMultiAgentOrchestration:
    """End-to-end multi-agent orchestration workflows."""

    def test_full_workflow_sequential(self):
        """
        Research workflow: Research → Check Quality → Summarize → Write

        Steps:
        1. Load flow from YAML
        2. Create orchestrator with sub-agents
        3. Run orchestrator with input
        4. Verify final output
        """
        pass

    def test_orchestrator_evaluates_quality(self):
        """Orchestrator checks quality and retries if needed."""
        pass

    def test_orchestrator_handles_agent_failure(self):
        """Orchestrator gracefully handles failed sub-agents."""
        pass
```

---

## Success Criteria

### Code Quality
- [ ] All classes < 150 lines (CLAUDE.md compliant)
- [ ] Type hints on all public methods
- [ ] Google-style docstrings
- [ ] No ABC (keep it simple)

### Testing
- [ ] All unit tests passing (35 tests)
- [ ] All integration tests passing (7 tests)
- [ ] > 80% code coverage
- [ ] Edge cases covered (failures, missing agents, etc.)

### Features
- [ ] AgentTool wrapper working
- [ ] OrchestratorAgent reasoning about agent calls
- [ ] FlowManager loads YAML flows
- [ ] Flow validation catches errors
- [ ] REPL commands for flow management
- [ ] Integration with existing features (guardrails, HITL, RAG)

### Documentation
- [ ] Example YAML flow provided
- [ ] Usage documentation with examples
- [ ] REPL command help text
- [ ] Architecture explained in docstrings

---

## Risk Mitigation

### Risk: LLM reasoning about agent tools is unreliable
**Mitigation:**
- Clear tool descriptions in orchestrator role
- Structured examples in system prompt
- Fallback to sequential execution if orchestrator fails
- Option to disable reasoning, use fixed flow

### Risk: Agent tool output parsing is fragile
**Mitigation:**
- Consistent output format from agents
- Try/catch on parsing with graceful fallback
- Validation before consuming output
- Log parsing failures for debugging

### Risk: Complex flows become unmaintainable
**Mitigation:**
- Keep initial flows simple (sequential)
- Defer complex branching to Option C (Phase 3+)
- Good documentation and examples
- `/flow show` command for visualization

---

## Migration from Phase 2.1-2.3

All existing features integrate naturally:

- **Guardrails**: Apply to both orchestrator and sub-agents
- **HITL**: Approval gates work within sub-agent execution
- **RAG**: Sub-agents can have RAG enabled for knowledge

Example:
```yaml
sub_agents:
  - name: "researcher"
    config: "config/agents/researcher.yaml"  # Has RAG enabled
    # Guardrails auto-applied from agent config
```

---

## Next Steps After Phase 2.4

1. **Phase 3: Advanced Features**
   - Option C: Reasoning-Driven Graph workflows
   - Python code-based flows
   - Advanced conditional routing

2. **Improvements**
   - Flow visualization tools
   - Execution replay for debugging
   - Cost tracking per workflow
   - Pattern learning from execution history

---

## File Structure Overview

```
simple_agent/orchestration/          # NEW
├── __init__.py
├── agent_tool.py                    # AgentTool wrapper
├── orchestrator_agent.py             # OrchestratorAgent
├── flow_manager.py                   # FlowManager
├── flow_validator.py                 # YAML validation

simple_agent/commands/
├── flow_commands.py                  # NEW: /flow commands

tests/unit/
├── test_agent_tool.py                # NEW
├── test_orchestrator_agent.py         # NEW
├── test_flow_manager.py               # NEW
├── test_flow_validator.py             # NEW
├── test_flow_commands.py              # NEW

tests/integration/
├── test_phase_2_4.py                 # NEW

config/flows/                          # NEW
├── example_research.yaml              # Example workflow

docs/phases/
├── PHASE_2_4_IMPLEMENTATION.md        # This file
```

---

## Estimation Breakdown

| Component | Est. Time | Lines | Tests |
|-----------|-----------|-------|-------|
| AgentTool | 0.5h | 75 | 5 |
| OrchestratorAgent | 1.0h | 100 | 5 |
| FlowManager | 0.75h | 150 | 6 |
| FlowValidator | 0.25h | 75 | 3 |
| FlowCommands | 1.0h | 200 | 6 |
| Integration Tests | 1.0h | 150 | 7 |
| Docs & Polish | 0.5h | - | - |
| **TOTAL** | **5h** | **750** | **32** |

---

**Version:** 1.0
**Date:** 2025-10-28
**Status:** Ready for Implementation
**Next:** Begin Phase 1 - AgentTool tests
