# Simple-Agent Backlog

Future enhancements and feature ideas, organized by category.

---

## Configuration & Agent Management

### SSL Certificate Verification - Per-Provider and Per-Tool Granularity
**Priority:** Low
**Complexity:** Medium (2-3 hours)
**Status:** Basic implementation in place (global setting)

Extend SSL certificate verification to support per-provider and per-tool configuration.

**Current Implementation:**
- Global `verify_certificates: true/false` setting in config.yaml (default: true)
- Applied to tavily_search tool

**Future Enhancement:**
- Per-provider SSL settings:
  ```yaml
  llm:
    openai:
      verify_certificates: true
    azure_openai:
      verify_certificates: false  # For corporate proxy scenarios
  ```
- Per-tool SSL settings:
  ```yaml
  tools:
    tavily_web_search:
      verify_certificates: true
    custom_api_tool:
      verify_certificates: false
  ```

**Related Code:**
- `simple_agent/core/config_manager.py` - Config validation
- `simple_agent/tools/builtin/tavily_search.py` - Current implementation
- All provider implementations in `simple_agent/agents/simple_agent.py`

---

### Agent Autoload Configuration
**Priority:** Medium
**Complexity:** Low (15-30 minutes)
**Status:** Temporarily disabled (commented out in app.py line 153-161)

Add configurable agent autoloading from `config/agents/` directory.

**Current State:**
- Autoload functionality exists but temporarily disabled
- Agents must be manually loaded: `agent load config/agents/agent_name.yaml`
- Config agents (from `config.yaml`) still autoload normally

**Implementation:**
- Add `app.autoload_agents: true/false` flag to config.yaml
- Make autoload directory configurable
- Add exclusion list for specific agents
- Default to `true` for backward compatibility
- Consider granular control (per-agent enable/disable)

**Related Code:**
- `simple_agent/app.py` lines 153-161 (commented out)
- `simple_agent/core/agent_manager.py` - `load_agents_from_directory()`

**Related Issues:**
- Tool loading failures in YAML agents need to be resolved first
- See tool validation and error handling improvements below

---

### Tool Loading Error Handling for YAML Agents
**Priority:** High
**Complexity:** Medium (1-2 hours)
**Related to:** Agent autoload issue

Improve tool loading reliability and error reporting for agents loaded from YAML files.

**Current Problems:**
- Silent failures when tools can't be loaded
- No validation that declared tools exist
- No feedback when tools are missing/disabled
- Agent creation fails entirely if one tool fails

**Implementation:**
- Add `tool_manager.has_tool()` validation before loading
- Log warnings for missing/disabled tools
- Continue agent creation with available tools only
- Return diagnostics showing which tools loaded successfully
- Add `verify_tools()` method to check tool availability before agent run

**Related Code:**
- `simple_agent/core/agent_manager.py` - `create_agent()` lines 94-98
- `simple_agent/core/agent_manager.py` - `load_agent_from_yaml()` line 373
- `simple_agent/core/tool_manager.py` - `get_tool()`

---

## RAG Enhancements (Post Phase 2.3)

### PDF Support for RAG
**Priority:** Medium
**Complexity:** Medium (2-3 hours)
**Phase:** Post-2.3

Add PDF document support to RAG system.

**Implementation:**
- Use `PyPDF2` or `pdfplumber` for PDF text extraction
- Handle multi-page PDFs
- Extract text while preserving structure
- Support scanned PDFs with OCR (optional, complex)

**Related Code:**
- `simple_agent/rag/document_loader.py` - Add PDF loader
- Update tests for PDF ingestion

---

### HTML/Web Scraping for RAG
**Priority:** Medium
**Complexity:** Medium (2-3 hours)
**Phase:** Post-2.3

Add HTML document and web page support to RAG system.

**Implementation:**
- Use `BeautifulSoup4` for HTML parsing
- Extract main content (remove nav, ads, etc.)
- Support local HTML files
- Support web URLs (fetch and parse)
- Handle JavaScript-rendered pages with `playwright` (optional)

**Related Code:**
- `simple_agent/rag/document_loader.py` - Add HTML loader
- Consider: `trafilatura` for better content extraction

---

### Multimodal RAG (Images, Audio)
**Priority:** Low
**Complexity:** High (8-10 hours)
**Phase:** Phase 3+

Add support for non-text modalities in RAG.

**Image Support:**
- Use vision models for image embeddings
- OCR for text in images (`pytesseract`)
- Image description generation
- Visual Q&A

**Audio Support:**
- Transcription with `whisper` or cloud APIs
- Audio embeddings
- Speaker diarization (who said what)

**Implementation Challenges:**
- Multimodal embeddings (different vector spaces)
- Large storage requirements
- Processing time for images/audio
- Model compatibility

**Related Code:**
- `simple_agent/rag/multimodal_loader.py` - New module
- `simple_agent/rag/embeddings.py` - Support multiple embedding types

---

## Agent-to-Agent Protocols (Future Architecture Support)

### Agent Protocol Interface
**Priority:** Medium
**Complexity:** High (8-10 hours)
**Phase:** Phase 3+ (after Phase 2.4 orchestration proven)
**Status:** Backlog (enables future architecture migrations)

**Problem Solved:**
- Phase 2.4 orchestrates agents tightly coupled to SimpleAgent
- If you switch to different agent architecture (e.g., LangGraph, Claude Subagents, AutoGen), current code breaks
- Need standardized protocol for agent-to-agent communication
- Allows "legacy" agents (Phase 2.4 SimpleAgent-based) to work with new agent types

**Architecture:**

Define a standardized **AgentProtocol** interface that any agent system can implement:

```python
# simple_agent/orchestration/agent_protocol.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class AgentProtocol(ABC):
    """Standard interface for agent communication."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent identifier."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """What this agent does (for orchestrator)."""
        pass

    @abstractmethod
    def run(self, prompt: str) -> str:
        """Execute agent with prompt."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return execution metadata.

        {
            "execution_time": float,
            "tool_calls": int,
            "steps": int,
            "success": bool,
            "error": Optional[str]
        }
        """
        pass

class SimpleAgentAdapter(AgentProtocol):
    """Adapter: wraps SimpleAgent to conform to AgentProtocol."""
    def __init__(self, simple_agent: SimpleAgent):
        self._agent = simple_agent

    @property
    def name(self) -> str:
        return self._agent.name

    def run(self, prompt: str) -> str:
        return self._agent.run(prompt)

    def get_metadata(self) -> Dict[str, Any]:
        # Extract from self._agent.memory or agent execution tracking
        pass
```

**Use Cases:**

1. **Switching Agent Libraries:**
   ```python
   # Old: SimpleAgent-based orchestration
   agents = [SimpleAgentAdapter(agent1), SimpleAgentAdapter(agent2)]

   # New: Switch to LangGraph agents
   agents = [LangGraphAgentAdapter(graph_agent1), LangGraphAgentAdapter(graph_agent2)]

   # Orchestrator still works: it only knows AgentProtocol
   orchestrator.run(agents)  # No code changes!
   ```

2. **Hybrid Architectures:**
   ```python
   # Mix different agent types seamlessly
   agents = [
       SimpleAgentAdapter(simple_agent),           # Phase 2.4 legacy
       LangGraphAgentAdapter(graph_agent),         # New LangGraph agent
       ClaudeSubagentAdapter(subagent),            # Anthropic Subagent
   ]
   # Orchestrator coordinates across all types
   ```

3. **Testing Without Full Implementation:**
   ```python
   class MockAgentAdapter(AgentProtocol):
       """Mock agent for unit testing."""
       def run(self, prompt: str) -> str:
           return "mock response"
   ```

**Implementation Approach:**

1. Define `AgentProtocol` ABC in `simple_agent/orchestration/agent_protocol.py`
2. Create `SimpleAgentAdapter(AgentProtocol)` wrapper
3. Update `OrchestratorAgent` to accept `AgentProtocol[]` instead of specific types
4. Create adapters for future agent systems as needed
5. Extensive unit tests for protocol compliance

**Benefits:**

- ✅ **Future-proof:** Switch agent architectures without rewriting orchestration
- ✅ **Backward compatible:** Legacy Phase 2.4 agents keep working
- ✅ **Flexible:** Mix different agent types in same workflow
- ✅ **Testable:** Easy to create mock agents for testing
- ✅ **Maintainable:** Clear interface contracts

**When to Implement:**

- After Phase 2.4 orchestration is stable and tested
- When considering switching to new agent architecture
- When wanting to support multiple agent types simultaneously
- As "insurance policy" for future flexibility

**Related Components:**

- `simple_agent/orchestration/agent_protocol.py` - Protocol definition
- `simple_agent/orchestration/adapters/` - Adapter implementations
  - `simple_agent/orchestration/adapters/simple_agent_adapter.py`
  - `simple_agent/orchestration/adapters/mock_adapter.py`
  - `simple_agent/orchestration/adapters/langgraph_adapter.py` (future)
  - `simple_agent/orchestration/adapters/subagent_adapter.py` (future)
- `tests/unit/test_agent_protocol.py` - Protocol tests
- `tests/unit/test_adapters.py` - Adapter tests

**Example: Using with Phase 2.4 (After Implementation)**

```python
# Instead of:
orchestrator = OrchestratorAgent(
    agents=[agent1, agent2, agent3]  # Tightly coupled to SimpleAgent
)

# With AgentProtocol:
orchestrator = OrchestratorAgent(
    agents=[
        SimpleAgentAdapter(agent1),
        SimpleAgentAdapter(agent2),
        SimpleAgentAdapter(agent3),
    ]
)

# Later, when switching architectures:
from simple_agent.orchestration.adapters import LangGraphAgentAdapter
orchestrator = OrchestratorAgent(
    agents=[
        LangGraphAgentAdapter(graph_agent1),
        LangGraphAgentAdapter(graph_agent2),
        LangGraphAgentAdapter(graph_agent3),
    ]
)
# Orchestrator code: unchanged!
```

---

## Multi-Agent Workflow Enhancements (Post Phase 2.4)

### Option C: Reasoning-Driven Graph Workflows
**Priority:** Medium
**Complexity:** High (8-10 hours)
**Phase:** Phase 3+
**Status:** Backlog (Phase 2.4 uses Option B instead)

Advanced workflow system where the orchestrator reasons about the optimal path through a directed graph of agents.

**Problem Solved:**
- Phase 2.4 Option B uses Orchestrator Agent for sequential, intelligent routing
- Option C enables complex branching workflows with dynamic path optimization
- Useful for applications requiring sophisticated multi-path decision trees

**Architecture:**
```
Agent Graph:
┌─────────────┐
│ Orchestrator│ (Meta-reasoning about paths)
└──────┬──────┘
       ├─→ Research Agent
       │   └─→ ├─→ Analyzer (confidence check)
       │       │   └─→ Writer (if high confidence)
       │       └─→ Quality Checker (if low confidence)
       │
       ├─→ Data Extraction Agent
       │   └─→ Validation Agent
       │
       └─→ Reporter Agent
```

**Key Features:**
- Graph-based workflow definition (DAG - Directed Acyclic Graph)
- Orchestrator reasons about which path to take based on:
  - Agent output quality scores
  - Complexity of request
  - Available agents and their specialties
  - Previous success patterns
- Dynamic path selection (not hard-coded conditionals)
- Support for parallel agent execution (if safe)
- Automatic fallback paths if agent fails

**Implementation Approach:**
1. Graph definition in YAML or Python
2. State machine for workflow execution
3. Visualization of workflow execution paths
4. Metadata tracking (which path was chosen and why)
5. Learning from execution patterns (future enhancement)

**When to Implement:**
- After Phase 2.4 (Orchestrator Agent) is proven effective
- When users request more complex, branching workflows
- When workflow patterns emerge that need optimization

**Related Components:**
- `simple_agent/flows/graph_manager.py` - Graph-based flow management
- `simple_agent/flows/path_optimizer.py` - Reasoning about optimal paths
- `simple_agent/commands/flow_commands.py` - Enhanced `/flow show` with visualization

**Example Use Case:**
```
User Query: "Analyze this dataset and write a comprehensive report"

Orchestrator reasons:
- "Dataset size is large" → parallel extraction agents
- "Data quality is uncertain" → add validation agents
- "High confidence in analysis" → skip re-analysis
- "Need professional report" → add formatting agent

Execution: Extract (parallel) → Validate → Analyze → Format → Report
```

**Dependencies with Phase 2.4:**
- Phase 2.4 lays foundation with Orchestrator Agent pattern
- Option C builds on Option B's infrastructure
- Same agent composition and tool-calling mechanisms
- Enhanced with graph reasoning layer

---

## Configuration & CLI Enhancements

### CLI --set Flag for Config Overrides
**Priority:** Low
**Complexity:** Low (2-3 hours)

Add `--set` flag to CLI for temporary config overrides at launch time.

**Problem:**
Currently, config changes require either:
1. Editing `config.yaml` directly (permanent)
2. Using `/config set` in REPL (session-only, requires interactive mode)
3. Using command-specific flags like `--provider` (limited scope)

**Proposed Solution:**
```bash
# Override config values when launching app
python -m simple_agent.app --set llm.temperature=0.9 --set agents.default.max_steps=20

# Use in REPL mode
python -m simple_agent.app --set llm.model=gpt-4o

# Use in CLI mode (single command)
python -m simple_agent.app --set llm.temperature=0.9 agent run test "Hello"
```

**Use Cases:**
- Testing with different configurations without modifying files
- Scripts that need temporary config overrides
- CI/CD pipelines with environment-specific settings
- Quick experiments with different LLM settings

**Implementation Notes:**
- Parse `--set key=value` pairs before loading config
- Apply overrides after loading `config.yaml`
- Support nested keys with dot notation: `llm.openai.temperature`
- Support multiple `--set` flags
- Validate key paths before applying
- These are temporary (not saved to config.yaml)

**Related Code:**
- `simple_agent/app.py` - Add `--set` option to CLI
- `simple_agent/core/config_manager.py` - Add method to apply overrides

**Alternative Considered:**
Could use environment variables, but `--set` is more explicit and discoverable.

---

## Agent Inspection & Visibility

### /agent show-prompt Enhancements
**Priority:** Medium
**Complexity:** Low

Current implementation shows `agent.agent.system_prompt`, but debug output reveals richer information.

**Ideas to explore:**
- Include tool declarations in show-prompt output (currently only visible in debug mode)
- Show the complete prompt sent to LLM, not just base system_prompt
- Add option to show prompt with/without tool declarations: `/agent show-prompt default --full`
- Consider showing the Jinja template rendering with actual tool schemas

**Investigation needed:**
- Where does SmolAgents store the full prompt with tool declarations?
- Is it in `agent.agent.system_prompt` or constructed at runtime?
- Check if there's a `prompt` or `full_prompt` attribute we can access

**Related files:**
- `simple_agent/commands/agent_commands.py:282-326` (show-prompt command)
- SmolAgents documentation on prompts and tool rendering

---

## Response Metadata & Analytics

### Track and Display LLM Response Metadata
**Priority:** Medium
**Complexity:** Medium

Debug mode shows useful metadata like:
- Cost per response
- Token usage (input/output)
- Model performance metrics
- Response time/latency

**Ideas to explore:**
- Add `/response metadata` command to show cost/tokens for last response
- Add `/agent stats <name>` to show cumulative usage for an agent
- Track cost per agent session
- Export usage statistics to JSON/CSV
- Add cost tracking to history export

**Investigation needed:**
- Where does LiteLLM/SmolAgents expose this metadata?
- Is it in the response object or separate?
- Can we access it without debug mode?
- What metadata is available: cost, tokens, model, latency, etc.?

**Potential structure:**
```
/response metadata
  Model: gpt-4o-mini
  Tokens: 150 input / 45 output
  Cost: $0.0023
  Latency: 1.2s

/agent stats default
  Total runs: 15
  Total cost: $0.034
  Avg tokens: 120 input / 60 output
  Total time: 18.5s
```

**Related files:**
- `simple_agent/commands/inspection_commands.py` (response commands)
- `simple_agent/core/agent_manager.py` (run_agent method - capture metadata)
- LiteLLM documentation on response metadata

---

## Debug Output Improvements

### LiteLLM Console Output Suppression
**Priority:** Medium
**Complexity:** Medium (2-3 hours)
**Status:** Partial fix in place

LiteLLM writes directly to stdout in some code paths, bypassing Python's logging system. This can interfere with REPL display when `debug.level` is set to `info`.

**Current State:**
- `debug.level: "off"` (default) works cleanly - no LiteLLM output
- `debug.level: "info"` still shows some LiteLLM output mixed with response
- Settings applied: `litellm.set_verbose = False`, `litellm.suppress_debug_info = True`
- Python logging configured to file-only for LiteLLM logger

**Investigation Needed:**
- Identify which LiteLLM code paths write directly to stdout
- Check if there are additional LiteLLM settings to suppress output
- Consider patching stdout during agent execution (complex due to REPL)
- Check LiteLLM GitHub issues for similar reports

**Workaround:**
Use `debug.level: "off"` (default) for clean REPL output.

**Related Code:**
- `simple_agent/agents/simple_agent.py` lines 144-158 (current suppression code)
- LiteLLM source: `litellm/utils.py` (direct print statements)

---

### Better Debug Formatting
**Priority:** Low
**Complexity:** Low

**Ideas:**
- Color-code debug output sections (prompts, responses, metadata)
- Add timestamps to debug messages
- Make tool declarations more readable in debug output
- Add option to save debug output to file

---

## Notes

- All backlog items should follow TDD methodology when implemented
- Consider user preferences: some users may not want cost tracking (privacy)
- Keep commands simple and intuitive
- Maintain separation: business logic in managers, display in commands
