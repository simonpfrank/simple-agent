# Phase 2: Enhanced Features

**Status:** 📋 Planned
**Priority:** High (Next after Phase 1 completion)
**Estimated Effort:** 15-20 hours total across 4 sub-phases

---

## Overview

Phase 2 adds critical enhanced features that enable safer, more powerful, and knowledge-augmented agents. This phase focuses on:

1. **Safety & Control** - Guardrails and Human-in-the-Loop approval
2. **Knowledge** - RAG for document retrieval
3. **Collaboration** - Multi-agent orchestration

**Phase 2 Sub-Phases (Prioritized):**
- **2.1: Guardrails** - Input/output validation for safety
- **2.2: Human-in-the-Loop** - Approval gates and interactive prompts
- **2.3: RAG Foundation** - Document retrieval (text files initially)
- **2.4: Multi-Agent Orchestration** - Agent workflows and composition

---

## Foundation: SmolAgents MultiStepAgent & ReAct Framework

**Important Context for Phase 2 Design:**

All agents in Simple Agent use `ToolCallingAgent`, which extends SmolAgents' base `MultiStepAgent` class. This foundational class implements the **ReAct (Reasoning + Acting)** framework—a powerful capability that enables intelligent iteration *within each agent's execution*.

### What This Means for Phase 2

**MultiStepAgent provides:**
1. **Iterative Reasoning** - Each step: reason about state → act (call tools) → reason about results
2. **Built-in Fallback** - Agents automatically retry with different strategies if first attempt fails
3. **Dynamic Tool Selection** - Agents choose tools based on intermediate reasoning
4. **Memory Across Steps** - Agent recalls lessons from previous steps during current step

**Implications for Phase 2 Sub-Phases:**
- **2.1 Guardrails** - Built atop agent iteration; can validate at each step
- **2.2 HITL** - Approval requests informed by agent reasoning
- **2.3 RAG** - Context injected early so agent reasoning incorporates knowledge
- **2.4 Multi-Agent** - Orchestrator leverages each agent's internal iteration + reasoning

**Phase 2.4 Advantage:** Refinement loops, quality checks, and error recovery are more powerful because each agent is already iterating internally. Workflows coordinate *between* agents while each agent handles *within*-step refinement.

---

## Phase 2.1: Guardrails 🛡️

**Goal:** Add input/output validation for safety, compliance, and quality control

**Priority:** Highest (foundation for safe agent operation)
**Estimated Effort:** 4-5 hours

### Problem Statement

Agents can generate inappropriate content, leak sensitive information, or produce malformed outputs. We need validation layers before and after LLM calls.

**Use Cases:**
- Prevent PII (emails, phone numbers, SSNs) from being sent to LLM
- Filter profanity or inappropriate content in outputs
- Validate output format (JSON, length limits, required fields)
- Check content safety before processing
- Custom business rules (e.g., "no SQL queries in prompts")

### Architecture

**Simple Wrapper Pattern** - Not a complex framework:

```python
# Guardrails wrap the agent's run() method
class GuardrailAgent:
    def __init__(self, agent, input_guardrails=[], output_guardrails=[]):
        self.agent = agent
        self.input_guardrails = input_guardrails
        self.output_guardrails = output_guardrails

    def run(self, prompt):
        # Apply input guardrails
        for guardrail in self.input_guardrails:
            prompt = guardrail.process(prompt)  # Can modify or reject

        # Run agent
        response = self.agent.run(prompt)

        # Apply output guardrails
        for guardrail in self.output_guardrails:
            response = guardrail.process(response)  # Can modify or reject

        return response
```

### Guardrail Types

**1. Input Validators** (before LLM):
- `PIIDetector` - Detect and redact emails, phone numbers, SSNs
- `ContentSafety` - Check for inappropriate content
- `LengthValidator` - Enforce prompt length limits
- `CustomRule` - User-defined validation functions

**2. Output Filters** (after LLM):
- `ProfanityFilter` - Remove or replace profanity
- `SensitiveDataFilter` - Redact sensitive information in response
- `FormatValidator` - Ensure output matches expected format (JSON, XML, etc.)
- `LengthLimiter` - Truncate responses exceeding limits
- `CustomFilter` - User-defined filtering functions

**3. Custom Guardrails**:
- User provides Python function: `def my_rule(text: str) -> str`
- Guardrail wraps the function
- Can be applied to input or output

### YAML Configuration

```yaml
name: "safe_assistant"
provider: "openai"
role: "You are a helpful assistant."
guardrails:
  input:
    - type: "pii_detector"
      redact: true  # or reject: true
      types: ["email", "phone", "ssn"]
    - type: "length_validator"
      max_length: 4000
    - type: "custom"
      function: "my_module.check_sql_injection"
  output:
    - type: "profanity_filter"
      action: "replace"  # or "reject" or "flag"
      replacement: "***"
    - type: "format_validator"
      expected_format: "json"
      strict: false
    - type: "length_limiter"
      max_length: 2000
```

### Implementation Components

**Files to Create:**
1. `simple_agent/guardrails/base.py` - Base guardrail classes
2. `simple_agent/guardrails/input_validators.py` - Input guardrails
3. `simple_agent/guardrails/output_filters.py` - Output guardrails
4. `simple_agent/guardrails/guardrail_agent.py` - GuardrailAgent wrapper
5. `simple_agent/commands/guardrail_commands.py` - REPL commands

**Key Classes:**
```python
# Base class
class Guardrail(ABC):
    @abstractmethod
    def process(self, text: str) -> str:
        """Process text. Return modified text or raise GuardrailViolation."""
        pass

# Input validator
class PIIDetector(Guardrail):
    def __init__(self, types=["email", "phone"], redact=True):
        self.types = types
        self.redact = redact

    def process(self, text: str) -> str:
        # Detect PII using regex
        # Either redact or raise GuardrailViolation
        pass

# Output filter
class ProfanityFilter(Guardrail):
    def __init__(self, action="replace", replacement="***"):
        self.action = action
        self.replacement = replacement

    def process(self, text: str) -> str:
        # Filter profanity
        pass
```

### REPL Commands

```bash
# Test a guardrail on text
/guardrail test <name> "sample text"

# List configured guardrails for an agent
/guardrail list <agent_name>

# Add guardrail to agent (runtime)
/guardrail add <agent_name> --type pii_detector --stage input

# Remove guardrail
/guardrail remove <agent_name> <guardrail_name>

# Show guardrail violations history
/guardrail violations <agent_name>
```

### Testing Strategy (TDD)

**Unit Tests:**
1. Test each guardrail type independently
2. Test GuardrailAgent wrapper
3. Test guardrail configuration loading from YAML
4. Test custom function guardrails
5. Test guardrail chaining (multiple guardrails)
6. Test error handling (GuardrailViolation exceptions)

**Integration Tests:**
1. Test agent with guardrails end-to-end
2. Test REPL commands for guardrail management
3. Test YAML configuration loading
4. Test guardrails with actual LLM calls (mocked)

**Test Files:**
- `tests/unit/test_guardrails.py` - Guardrail classes
- `tests/unit/test_guardrail_agent.py` - GuardrailAgent wrapper
- `tests/unit/test_guardrail_commands.py` - REPL commands
- `tests/integration/test_phase_2_1.py` - End-to-end guardrail tests

### Success Criteria

- [ ] PIIDetector can detect and redact emails, phone numbers, SSNs
- [ ] ContentSafety validator works (may use external API or library)
- [ ] LengthValidator enforces prompt limits
- [ ] ProfanityFilter removes inappropriate language
- [ ] FormatValidator ensures JSON output
- [ ] Custom guardrails work with user-provided functions
- [ ] GuardrailAgent wrapper applies guardrails correctly
- [ ] YAML configuration loads guardrails
- [ ] REPL commands for guardrail management work
- [ ] All tests pass (unit + integration)
- [ ] Documentation with examples

### Dependencies

**External Libraries:**
- `regex` - For PII detection patterns
- `profanity-check` or `better-profanity` - Profanity filtering (optional)
- Consider: `presidio` for advanced PII detection (may be overkill)

---

## Phase 2.2: Human-in-the-Loop (HITL) 👤

**Goal:** Add approval gates and interactive prompts for human control

**Priority:** High (enables safe agent autonomy)
**Estimated Effort:** 4-5 hours

### Problem Statement

Agents may execute destructive actions (delete files, send emails, make API calls) without human oversight. We need approval gates for sensitive tools.

**Use Cases:**
- Approve before sending emails
- Confirm before deleting files
- Review before making API requests
- Interactive input during execution ("Which option do you prefer?")
- Timeout with default behavior

### Architecture

**Approval Workflow:**

```
Agent → Tool Call → Check if HITL Required → Yes → Prompt User → Execute (or Cancel)
                                        → No  → Execute Directly
```

**Components:**
1. **Tool Approval Registry** - Which tools require approval
2. **Approval Prompt Handler** - Display request, get user input
3. **Approval History** - Track what was approved/rejected
4. **Timeout Handler** - Default behavior if no response

### YAML Configuration

```yaml
name: "email_assistant"
provider: "openai"
role: "You are an email assistant."
tools:
  - name: "send_email"
    hitl:
      enabled: true
      prompt: "Approve sending email to {to} with subject '{subject}'?"
      timeout: 60  # seconds
      default_action: "reject"  # or "approve"
  - name: "delete_file"
    hitl:
      enabled: true
      prompt: "Approve deleting file '{filepath}'?"
      show_preview: true  # Show file contents before deletion
      timeout: 30
      default_action: "reject"
  - name: "search_web"
    hitl:
      enabled: false  # No approval needed
```

### Implementation Components

**Files to Create:**
1. `simple_agent/hitl/approval_manager.py` - Approval workflow
2. `simple_agent/hitl/tool_wrapper.py` - Tool wrapper with HITL
3. `simple_agent/commands/approval_commands.py` - REPL approval commands
4. `simple_agent/core/agent_manager.py` - Integration (modify existing)

**Key Classes:**
```python
class ApprovalManager:
    def __init__(self, console):
        self.console = console
        self.history = []  # Track approvals

    def request_approval(
        self,
        tool_name: str,
        prompt: str,
        timeout: int = 60,
        default_action: str = "reject",
        preview_data: dict = None
    ) -> bool:
        """Request user approval. Returns True if approved."""
        # Display prompt
        # Show preview data if provided
        # Wait for user input with timeout
        # Return approval decision
        pass

class HITLTool:
    """Wrapper around a tool that requires human approval."""
    def __init__(self, tool, approval_manager, hitl_config):
        self.tool = tool
        self.approval_manager = approval_manager
        self.hitl_config = hitl_config

    def __call__(self, *args, **kwargs):
        # Format approval prompt
        # Request approval
        # If approved: execute tool
        # If rejected: return error
        pass
```

### REPL Commands

```bash
# Approve pending request (during execution)
/approve

# Reject pending request
/reject

# Auto-approve all for this session
/approve-all

# View approval history
/approval history

# Configure HITL for a tool
/tool configure send_email --hitl-enabled true --hitl-timeout 60

# Disable HITL for a tool
/tool configure search_web --hitl-enabled false
```

### Interactive Approval UX

```
┌─────────────────────────────────────────────────────────────┐
│ 🔔 Approval Required                                         │
├─────────────────────────────────────────────────────────────┤
│ Tool: send_email                                             │
│ Agent: email_assistant                                       │
│                                                              │
│ Approve sending email to john@example.com with subject      │
│ 'Meeting Reminder'?                                         │
│                                                              │
│ Preview:                                                    │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ Hi John,                                              │  │
│ │                                                       │  │
│ │ This is a reminder about our meeting tomorrow at 2PM.│  │
│ │                                                       │  │
│ │ Thanks!                                               │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                              │
│ [A]pprove  [R]eject  [V]iew Details  (timeout: 60s)        │
└─────────────────────────────────────────────────────────────┘
```

### Testing Strategy (TDD)

**Unit Tests:**
1. Test ApprovalManager prompt display and input capture
2. Test timeout behavior (approved vs rejected)
3. Test HITLTool wrapper
4. Test approval history tracking
5. Test YAML configuration loading
6. Test default action behavior

**Integration Tests:**
1. Test agent with HITL tools end-to-end
2. Test approval commands in REPL
3. Test timeout scenarios
4. Test approval history retrieval
5. Test auto-approve mode

**Test Files:**
- `tests/unit/test_approval_manager.py`
- `tests/unit/test_hitl_tool.py`
- `tests/unit/test_approval_commands.py`
- `tests/integration/test_phase_2_2.py`

### Success Criteria

- [ ] Tool approval requests display correctly in REPL
- [ ] User can approve/reject with keyboard input
- [ ] Timeout mechanism works with default actions
- [ ] Approval history tracks all decisions
- [ ] HITL configuration loads from YAML
- [ ] `/approve`, `/reject`, `/approve-all` commands work
- [ ] Tools execute only after approval
- [ ] Preview data displays correctly
- [ ] All tests pass (unit + integration)
- [ ] Documentation with examples

### Dependencies

**External Libraries:**
- `prompt_toolkit` - Already used for REPL (no new dependency)
- `rich` - Already used for formatting (no new dependency)

---

## Phase 2.3: RAG Foundation 📚

**Goal:** Enable document retrieval for knowledge-augmented agents

**Priority:** Medium-High (powerful feature for specialized domains)
**Estimated Effort:** 5-6 hours

### Problem Statement

Agents are limited to their training data and can't access domain-specific documents, research papers, or internal knowledge bases. RAG solves this by retrieving relevant context before generating responses.

**Use Cases:**
- Research assistant with access to papers
- Legal assistant with case law database
- Technical support with documentation
- Personal assistant with notes/journals
- Code assistant with internal codebase docs

### Architecture

**RAG Workflow:**

```
User Query → Embed Query → Search Vector Store → Retrieve Top-K → Inject into Prompt → LLM → Response
```

**Components:**
1. **Vector Store (Chroma)** - Stores document embeddings
2. **Document Loader** - Loads and chunks documents
3. **Embedding Model** - Converts text to vectors (via LiteLLM)
4. **Retriever** - Searches vector store for relevant chunks
5. **RAG Manager** - Orchestrates the workflow

### Initial Scope (Phase 2.3)

**Document Types Supported:**
- ✅ Plain text files (`.txt`)
- ✅ Markdown files (`.md`)
- ❌ PDF (backlog - Phase 2.5+)
- ❌ HTML (backlog - Phase 2.5+)
- ❌ Images (backlog - Phase 3+)

### YAML Configuration

```yaml
name: "research_assistant"
provider: "openai"
role: "You are a research assistant with access to documents."
rag:
  enabled: true
  collection_name: "research_papers"  # Unique per agent
  documents_path: "./docs/research"
  chunk_size: 1000  # characters
  chunk_overlap: 200
  top_k: 3  # Number of chunks to retrieve
  embedding_model: "text-embedding-ada-002"  # OpenAI default
  auto_ingest: true  # Auto-load documents on agent creation
```

### Implementation Components

**Files to Create:**
1. `simple_agent/rag/rag_manager.py` - RAG orchestration
2. `simple_agent/rag/document_loader.py` - Load and chunk documents
3. `simple_agent/rag/vector_store.py` - Chroma wrapper
4. `simple_agent/rag/retriever.py` - Search and ranking
5. `simple_agent/commands/rag_commands.py` - REPL commands
6. `simple_agent/agents/rag_agent.py` - Agent with RAG (optional wrapper)

**Key Classes:**
```python
class RAGManager:
    def __init__(self, collection_name, embedding_model, chroma_path="./chroma_db"):
        self.collection_name = collection_name
        self.vector_store = ChromaVectorStore(collection_name, chroma_path)
        self.embedding_model = embedding_model

    def ingest_documents(self, documents_path, chunk_size=1000, chunk_overlap=200):
        """Load documents and add to vector store."""
        # Load files
        # Chunk text
        # Generate embeddings
        # Store in Chroma
        pass

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve relevant document chunks."""
        # Embed query
        # Search vector store
        # Return top-K chunks
        pass

class DocumentLoader:
    @staticmethod
    def load_directory(path: str) -> List[Document]:
        """Load all .txt and .md files from directory."""
        pass

    @staticmethod
    def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks."""
        pass
```

### Prompt Injection Strategy

**Option 1: System Prompt Injection** (Preferred)
```
System Prompt:
You are a research assistant.

Relevant Context:
---
[Retrieved Chunk 1]
...
[Retrieved Chunk 2]
...
[Retrieved Chunk 3]
---

User Query: {user_input}
```

**Option 2: User Prompt Injection**
```
Context: [chunks]

Question: {user_input}
```

We'll use **Option 1** for cleaner separation.

### REPL Commands

```bash
# Load documents into vector store
/rag load <agent_name> <path>

# Query vector store (test retrieval)
/rag query <agent_name> "search query"

# List documents in vector store
/rag list <agent_name>

# Delete collection
/rag delete <agent_name>

# Show RAG stats
/rag stats <agent_name>

# Reindex documents (clear and reload)
/rag reindex <agent_name>
```

### Testing Strategy (TDD)

**Unit Tests:**
1. Test document loading (.txt, .md)
2. Test text chunking with overlap
3. Test Chroma vector store operations (add, search, delete)
4. Test embedding generation (mocked)
5. Test retriever (top-k selection)
6. Test RAG manager orchestration
7. Test YAML configuration loading

**Integration Tests:**
1. Test full RAG workflow end-to-end
2. Test agent with RAG enabled
3. Test REPL commands
4. Test auto-ingestion on agent creation
5. Test per-agent collections (isolation)

**Test Files:**
- `tests/unit/test_document_loader.py`
- `tests/unit/test_vector_store.py`
- `tests/unit/test_rag_manager.py`
- `tests/unit/test_rag_commands.py`
- `tests/integration/test_phase_2_3.py`

### Success Criteria

- [ ] Can load .txt and .md files from directory
- [ ] Text chunking works with overlap
- [ ] Chroma vector store integration working
- [ ] Embeddings generated via LiteLLM
- [ ] Top-K retrieval returns relevant chunks
- [ ] RAG-enabled agents inject context into prompts
- [ ] Per-agent collections work (no cross-contamination)
- [ ] REPL commands for RAG management work
- [ ] Auto-ingestion on agent creation works
- [ ] All tests pass (unit + integration)
- [ ] Documentation with examples

### Dependencies

**External Libraries:**
- `chromadb>=0.4.0` - Vector store
- `tiktoken` - Token counting for chunking (optional)

**Note:** LiteLLM already handles embeddings, so no additional embedding library needed.

---

## Phase 2.4: Multi-Agent Orchestration 🤝

**Goal:** Enable agents to work together in workflows, leveraging ReAct iteration for intelligent refinement

**Priority:** Medium (powerful but most complex)
**Estimated Effort:** 5-6 hours

### Problem Statement

Single agents are limited in scope. Complex tasks require breaking down into subtasks handled by specialized agents. Need coordination, result passing, and conditional routing. Additionally, agents need ability to refine outputs and adapt strategies based on intermediate results.

**Use Cases:**
- Research → Summarize → Write report (with internal refinement at each step)
- Code generation → Code review → Fix issues (reviewer feedback triggers auto-refinement)
- Data extraction → Data analysis → Visualization (analyzer validates data quality)
- Question → Search → Refine search → Answer (automatic retry with different search terms)
- Web scraping → Content analysis → Action (analyzer requests deeper scraping if needed)

### Architecture

**Leveraging MultiStepAgent & ReAct:**

All agents in your system use `ToolCallingAgent`, which extends `MultiStepAgent` and implements the **ReAct (Reasoning + Acting)** framework. This means:

1. **Built-in Iteration** - Each agent internally reasons → acts → reasons across multiple steps
2. **Dynamic Tool Selection** - Agents choose appropriate tools based on intermediate results
3. **Failure Recovery** - Agents can retry with different approaches without external intervention
4. **Cross-Step Learning** - Agent memory preserves lessons from earlier steps

**Phase 2.4 Workflows Benefit From:**
- Agents naturally refine their outputs through multiple internal iterations
- Orchestrator can check if agent output meets quality threshold (built-in fallback)
- Agents share context of tool availability and success/failure patterns
- Refinement loops use agent reasoning, not just string pattern matching

**Flow Types:**

**1. Sequential Flow** (simplest):
```
Agent A [reason→act→reason→act] → Agent B [reason→act→reason] → Agent C
```

**2. Conditional Routing with Intelligence**:
```
Agent A → Decision (agent reasoning or pattern) → Agent B (if condition)
                                               → Agent C (otherwise)
```

**3. Refinement Loop** (leverages ReAct):
```
Agent A [researcher] → Internal iteration refinement
                    ↓ (auto-retries if confidence low)
Agent B [reviewer] → Quality check
                    ↓ (if score < 8, feedback loops)
Agent A [with feedback] → Re-research with guidance
```

**4. Orchestrator Agent** (new option):
```
Orchestrator Agent [reason about which agent to call]
  ↓
  Reasons: "Need research, then summarization"
  ↓
  Calls Agent A, B, C in sequence with reasoning
```

**5. Agent Composition** (agent calls another agent as tool):
```
Agent A [reason about when help needed] → Calls Agent B as tool → Continue with result
```

### YAML Flow Definition

**Option 1: YAML-Defined Flows** (Recommended for Phase 2.4)
```yaml
name: "research_workflow"
description: "Research, summarize, and write report with quality refinement"
agents:
  - name: "researcher"
    config: "./config/agents/researcher.yaml"
  - name: "quality_checker"
    config: "./config/agents/quality_checker.yaml"
  - name: "summarizer"
    config: "./config/agents/summarizer.yaml"
  - name: "writer"
    config: "./config/agents/writer.yaml"

flow:
  - step: "research"
    agent: "researcher"
    input: "{user_query}"
    output_var: "research_results"
    note: "Agent iterates internally (ReAct) until confident in findings"

  - step: "quality_check"
    agent: "quality_checker"
    input: "Check quality of research: {research_results}"
    output_var: "quality_assessment"
    note: "Validates research quality before proceeding"

  - step: "check_research_quality"
    condition: "quality_assessment.score >= 8"
    if_false:
      # Leverage agent's internal refinement capability
      - agent: "researcher"
        input: "Improve research based on feedback: {quality_assessment.feedback}"
        output_var: "research_results"
        max_iterations: 2
        note: "Agent's ReAct loop refines approach"

  - step: "summarize"
    agent: "summarizer"
    input: "Summarize these findings: {research_results}"
    output_var: "summary"

  - step: "write_report"
    agent: "writer"
    input: "Write a report based on: {summary}"
    output_var: "final_report"

output: "{final_report}"
```

**Option 2: Python Code Flows** (more flexible):
```python
# flows/research_workflow.py
from simple_agent.flows import Flow

flow = Flow(name="research_workflow")

@flow.step("research")
def research_step(context):
    researcher = context.get_agent("researcher")
    results = researcher.run(context.input)
    return {"research_results": results}

@flow.step("quality_check")
def quality_check_step(context):
    checker = context.get_agent("quality_checker")
    assessment = checker.run(f"Check quality: {context.research_results}")
    return {"quality_assessment": assessment}

@flow.step("summarize")
def summarize_step(context):
    summarizer = context.get_agent("summarizer")
    summary = summarizer.run(f"Summarize: {context.research_results}")
    return {"summary": summary}

@flow.step("write_report")
def write_report_step(context):
    writer = context.get_agent("writer")
    report = writer.run(f"Write report: {context.summary}")
    return {"final_report": report}
```

**Decision:** **Phase 2.4 Primary Approach: Option B** - Smart Routing with Orchestrator Agent (below)

### Orchestrator Agent Pattern (PRIMARY APPROACH for Phase 2.4 - Option B)

**Phase 2.4 will implement Option B:** A smart routing system where an **Orchestrator Agent** reasons about which agents to call and in what order. This leverages each agent's ReAct iteration while adding intelligent, adaptive orchestration at the workflow level.

The Orchestrator Agent:

```yaml
name: "smart_orchestrator"
description: "Meta-agent that decides workflow execution"
role: |
  You are a workflow orchestrator. Your tools are other agents.
  Based on the user's request, decide which agents to call and in what order.
  Reason about whether intermediate results meet quality thresholds.

tools:
  - agent: "researcher"
    description: "Research a topic and return detailed findings"
  - agent: "analyzer"
    description: "Analyze data or findings for quality and insights"
  - agent: "writer"
    description: "Write polished reports based on findings"

instructions: |
  1. Analyze the user request
  2. Decide which agents to call (you may skip some based on request type)
  3. Call agents in logical order (reasoning before each call)
  4. Evaluate quality of intermediate results
  5. If quality is poor, ask agent to refine or try different approach
  6. Provide final response with reasoning
```

This pattern leverages each agent's internal ReAct iteration for intelligent, adaptive workflows.

### Approaches Not in Phase 2.4 (Backlog)

**Option A: Simple Enhancement** (Deferred - Too basic for complex workflows)
- Keep YAML-based sequential flows
- Rely on aggressive agent iteration within steps
- No intelligent routing between agents
- **Decision:** Insufficient for multi-agent complexity; moving to Phase 3 if needed

**Option C: Full Leverage / Reasoning-Driven Graph** (Backlog for Phase 3+)
- Workflow as directed graph with multiple paths
- Orchestrator reasons about optimal path through agent graph
- Full ReAct at orchestration level (meta-reasoning about meta-reasoning)
- Complex parsing, state management, visualization
- **Decision:** Deferred to Phase 3+ when workflows become more complex
- **When to Use:** After Phase 2.4 gains adoption and patterns emerge

**Why Option B (Orchestrator Agent)?**
- Leverages ReAct iteration at both levels (agents + orchestrator)
- Simple to understand: "meta-agent coordinates other agents"
- Flexible routing based on agent reasoning, not hard-coded rules
- Agents can skip unnecessary steps (orchestrator decides)
- Quality checks integrated naturally into reasoning
- Foundation for future Options A or C if needed

### Conditional Routing

```yaml
flow:
  - step: "analyze"
    agent: "analyzer"
    input: "{user_query}"
    output_var: "analysis"

  - step: "route"
    condition: "analysis.confidence > 0.8"
    if_true:
      - agent: "responder"
        input: "{analysis.answer}"
    if_false:
      - agent: "researcher"
        input: "Need more info: {user_query}"
      - agent: "responder"
        input: "{researcher.output}"
```

### Refinement Loop

```yaml
flow:
  - step: "generate"
    agent: "generator"
    input: "{user_query}"
    output_var: "draft"
    max_iterations: 3

  - step: "review"
    agent: "reviewer"
    input: "Review this: {draft}"
    output_var: "review"

  - step: "check_quality"
    condition: "review.score >= 8"
    if_false:
      goto: "generate"  # Retry with feedback
      input: "Improve based on: {review.feedback}"
```

### Implementation Components

**Files to Create:**
1. `simple_agent/flows/flow_manager.py` - Flow orchestration
2. `simple_agent/flows/flow_executor.py` - Execute flow steps
3. `simple_agent/flows/flow_parser.py` - Parse YAML flows
4. `simple_agent/flows/flow_context.py` - Context for variable passing
5. `simple_agent/commands/flow_commands.py` - REPL commands

**Key Classes:**
```python
class FlowManager:
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.flows = {}  # Loaded flows

    def load_flow(self, flow_path: str) -> Flow:
        """Load flow from YAML file."""
        pass

    def execute_flow(self, flow_name: str, input_data: str) -> str:
        """Execute a flow with input data."""
        pass

class FlowContext:
    """Context for passing variables between flow steps."""
    def __init__(self, input_data):
        self.variables = {"user_query": input_data}
        self.agent_manager = None

    def set(self, key, value):
        self.variables[key] = value

    def get(self, key):
        return self.variables.get(key)

    def get_agent(self, name):
        return self.agent_manager.get_agent(name)

class FlowExecutor:
    def execute_step(self, step: dict, context: FlowContext) -> dict:
        """Execute a single flow step."""
        # Get agent
        # Format input with variables
        # Run agent
        # Store output in context
        pass

    def evaluate_condition(self, condition: str, context: FlowContext) -> bool:
        """Evaluate a condition string."""
        # Simple eval or AST parsing
        pass
```

### Agent Composition (Agent as Tool)

```python
# Create a tool that wraps an agent
researcher_tool = AgentTool(
    name="researcher",
    agent=researcher_agent,
    description="Research a topic and return findings"
)

# Add to another agent
main_agent = agent_manager.create_agent(
    name="orchestrator",
    tools=["researcher_tool"]
)

# Agent can now call researcher as a tool
main_agent.run("Research quantum computing and summarize findings")
```

### Leveraging MultiStepAgent Features in Phase 2.4

To maximize the power of ReAct iteration, Phase 2.4 should:

**1. Enable Longer Iteration Chains**
```yaml
# In agent YAML config
settings:
  max_steps: 15  # Allow agents to iterate more (default often 10)
  verbosity: 2   # Show reasoning steps for debugging
```

**2. Use Quality Checks as Feedback**
```yaml
# Reviewer agent provides structured feedback
- step: "review"
  agent: "quality_reviewer"
  input: |
    Review this work: {previous_output}
    Provide:
    - score (1-10)
    - feedback for improvement
    - confidence level
  output_var: "review"
```

**3. Conditional Retry with Context**
```yaml
- condition: "review.score < 8"
  if_false:
    - agent: "original_agent"
      input: |
        {original_input}

        Previous attempt feedback:
        {review.feedback}

        Please improve based on this feedback.
        Confidence level needed: {review.confidence}
      output_var: "refined_output"
      max_iterations: 2  # Limit retry attempts
```

**4. Monitor Tool Usage Across Steps**
Each agent's history tracks which tools succeeded/failed. Use this to inform downstream agents:
```yaml
- step: "next_agent"
  agent: "analyzer"
  input: |
    {previous_output}

    Tools that were used: [research_web, search_api]
    Success rate: {tools.success_rate}

    Avoid tools that failed previously.
```

**Key Insight:** Agents already iterate internally via ReAct. Phase 2.4 focuses on orchestrating *between* agents while leveraging each agent's *internal* iteration for quality and refinement.

### REPL Commands

```bash
# Create flow from template
/flow create research_workflow

# List available flows
/flow list

# Run a flow
/flow run research_workflow "Query: What is quantum computing?"

# Show flow definition
/flow show research_workflow

# Delete flow
/flow delete research_workflow

# Debug flow execution (step-by-step)
/flow debug research_workflow "query"
```

### Testing Strategy (TDD)

**Unit Tests:**
1. Test YAML flow parsing
2. Test flow context variable management
3. Test step execution
4. Test conditional evaluation
5. Test refinement loops (max iterations)
6. Test error handling (agent failures)
7. Test agent composition (agent as tool)

**Integration Tests:**
1. Test sequential flow end-to-end
2. Test conditional routing
3. Test refinement loop
4. Test REPL flow commands
5. Test flow with RAG-enabled agents
6. Test flow with HITL tools

**Test Files:**
- `tests/unit/test_flow_manager.py`
- `tests/unit/test_flow_executor.py`
- `tests/unit/test_flow_parser.py`
- `tests/unit/test_flow_commands.py`
- `tests/integration/test_phase_2_4.py`

### Success Criteria

- [ ] Can define flows in YAML
- [ ] Sequential flows execute correctly
- [ ] Variables pass between steps
- [ ] Conditional routing works
- [ ] Refinement loops work with max iterations
- [ ] Agent composition (agent as tool) works
- [ ] REPL commands for flow management work
- [ ] Error handling for failed agents
- [ ] Flow execution is cancelable
- [ ] **ReAct iteration leveraged** - Agents iterate internally within steps
- [ ] **Quality feedback loops work** - Can pass reviewer feedback back to agents
- [ ] **Orchestrator agent pattern documented** - For Phase 2.4+ advanced use cases
- [ ] **Agent tool calls working** - Agents can call other agents as tools
- [ ] All tests pass (unit + integration)
- [ ] Documentation with examples

### Dependencies

**External Libraries:**
- None (uses existing agent infrastructure)

**Note:** May consider `pyyaml` enhancements for complex YAML parsing, but current yaml library should suffice.

---

## Phase 2 Summary

### Total Estimated Effort: 18-22 hours

### Implementation Order

1. **Phase 2.1: Guardrails** (4-5 hours) - Foundation for safety
2. **Phase 2.2: HITL** (4-5 hours) - Human control layer
3. **Phase 2.3: RAG** (5-6 hours) - Knowledge augmentation
4. **Phase 2.4: Multi-Agent** (5-6 hours) - Agent collaboration

### Dependencies Between Sub-Phases

- **2.2 (HITL)** can build on **2.1 (Guardrails)** for validation
- **2.4 (Multi-Agent)** can leverage **2.3 (RAG)** for knowledge-augmented workflows
- **2.4 (Multi-Agent)** should respect **2.1 (Guardrails)** and **2.2 (HITL)** constraints

### Testing Approach

**For Each Sub-Phase:**
1. Write unit tests (TDD red phase)
2. Implement core functionality (TDD green phase)
3. Write integration tests
4. Verify all tests pass
5. Update documentation
6. Commit sub-phase

### Success Criteria for Phase 2 Completion

- [ ] All 4 sub-phases implemented and tested
- [ ] All tests passing (unit + integration)
- [ ] REPL commands working for all features
- [ ] YAML configuration examples documented
- [ ] Each feature works independently
- [ ] Features integrate well together (guardrails + HITL + RAG + multi-agent)
- [ ] Progress_Tracker.md updated with Phase 2 status

---

## What's NOT in Phase 2

**Moved to Backlog:**
- PDF support for RAG
- HTML/web scraping for RAG
- Multimodal RAG (images, audio)

**Moved to Phase 3:**
- MCP (Model Context Protocol) integration
- Python code flows (YAML only in Phase 2)
- Advanced conditional routing (complex DAGs)
- Persistent flow state (checkpointing)

---

## Getting Started

Once Phase 1 is complete, start with:

1. Review this document
2. Create detailed implementation plan for Phase 2.1 (Guardrails)
3. Set up TDD environment
4. Begin implementation following TDD methodology

**Questions to Answer Before Starting:**
- Which guardrail libraries to use (presidio vs regex)?
- Should guardrails be synchronous or async?
- How to handle guardrail violations (error vs warning)?
- Should guardrails be composable (chains of guardrails)?

---

## Document Metadata

**Version:** 1.0
**Date:** 2025-10-26
**Status:** Planning Complete, Ready for Implementation
**Next Steps:** Begin Phase 2.1 (Guardrails)
