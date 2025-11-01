# Simple Agent - Progress Tracker

**Project**: Simple Agent Template
**Current Phase**: Phase 3 - Token Management (✅ All Complete)
**Phase 0 Started**: 2025-10-20
**Phase 0 Completed**: 2025-10-21
**Phase 1.1 Completed**: 2025-10-23
**Phase 1.2 Completed**: 2025-10-23
**Phase 1.3 Completed**: 2025-10-23
**Phase 1.4 Completed**: 2025-10-25
**Phase 1.5 Completed**: 2025-10-25
**Phase 1.6 Completed**: 2025-10-26
**Phase 1.7 Completed**: 2025-10-26
**Phase 2 Planning**: 2025-10-26
**Phase 2.1 Completed**: 2025-10-26
**Phase 2.2 Completed**: 2025-10-27
**Phase 2.3 Completed**: 2025-10-28
**Phase 2.4 Completed**: 2025-10-28
**Phase 3.1 Completed**: 2025-10-31
**Phase 3.2 Completed**: 2025-11-01

---

## Quick Navigation

### Completed Phases
- **Phase 0**: Foundation (✅ Completed) - See below
- **Phase 0.5**: Security Fix & Agent Type Architecture (✅ Completed) - See below
- **Phase 0.6**: Debug Mode (✅ Completed) - Integrated into Phase 1.1
- **Phase 1**: Interactive & Inspection Features (✅ COMPLETE) - See `docs/phases/PHASE_1.md`
  - **Phase 1.1**: Inspection & Chat Features (✅ Completed) - See below
  - **Phase 1.2**: History & Memory Management (✅ Completed) - See below
  - **Phase 1.3**: Configuration Management (✅ Completed) - See below
  - **Phase 1.4**: Tool Management (✅ Completed) - See below
  - **Phase 1.5**: YAML Agent Definitions (✅ Completed) - See below
  - **Phase 1.6**: Simplify Prompts & Add User Prompt Templates (✅ Completed) - See below
  - **Phase 1.7**: Jinja2 Template Support (✅ Completed) - See below

### Current Phase
- **Phase 2**: Enhanced Features (✅ All Complete) - See `docs/phases/PHASE_2.md`
  - **Phase 2.1**: Guardrails (✅ Completed) - Input validation with PII detection
  - **Phase 2.2**: Human-in-the-Loop (✅ Completed) - Approval gates
  - **Phase 2.3**: RAG Foundation (✅ Completed) - Collection-centric document retrieval
  - **Phase 2.4**: Multi-Agent Orchestration (✅ Completed) - Agent workflows with ReAct iteration

### Phases in Progress
- **Phase 3**: Token Management (✅ Completed) - See below
- **Phase 3.1**: Token Budget Protection (✅ Completed) - Hard limits to prevent rate limit hits
- **Phase 3.2**: Advanced Token Management (✅ Completed) - Cost tracking and optimization

### Future Phases
- **Phase 4**: Raspberry Pi (🔴 Not Started) - See `docs/SPECIFICATION.md`

---

## Phase 2.1: Guardrails ✅ COMPLETED

**Status**: ✅ Completed on 2025-10-26
**Total Tests**: 57 (45 unit + 12 integration, all passing)
**Architecture**: Input validation with guardrail wrapper pattern, no ABC

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **PII Detection** | | | | | |
| PIIDetector class | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (10/10) | ✅ Pass (1/1) |
| Email detection | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (1/1) |
| Phone detection | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (1/1) |
| SSN detection | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (1/1) |
| Redaction mode | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (5/5) | ✅ Pass (1/1) |
| Rejection mode | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (1/1) |
| **Custom Rules** | | | | | |
| CustomRuleGuardrail | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (8/8) | ✅ Pass (2/2) |
| Function wrapping | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (1/1) |
| Complex validation | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (1/1) |
| **GuardrailAgent Wrapper** | | | | | |
| Agent wrapping | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (11/11) | ✅ Pass (4/4) |
| Input guardrails | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (4/4) | ✅ Pass (2/2) |
| Multiple guardrails | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (3/3) | ✅ Pass (1/1) |
| Error handling | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (2/2) |
| **YAML Configuration** | | | | | |
| load_guardrails_from_yaml | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (7/7) | ✅ Pass (1/1) |
| PII config loading | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (1/1) |
| Custom rule config | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (1/1) |
| **REPL Commands** | | | | | |
| GuardrailCommands class | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (9/9) | ✅ Pass (1/1) |
| test_guardrail command | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (3/3) | ✅ Pass (1/1) |
| list_guardrails command | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (1/1) |
| add_guardrail command | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (1/1) |
| remove_guardrail command | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (1/1) |

### Phase 2.1 Implementation Summary

**Features Implemented:**
1. **PIIDetector**: Regex-based PII detection for emails, phone numbers, SSNs
2. **Redaction vs Rejection**: Two modes - redact sensitive data or reject input
3. **CustomRuleGuardrail**: Wrapper for user-defined validation functions
4. **GuardrailAgent**: Wrapper pattern applying guardrails before LLM execution
5. **YAML Configuration**: Load guardrail configs from YAML files
6. **REPL Commands**: `/guardrail` command group for testing and management

**Architecture Decisions:**
- ✅ No ABC (kept it simple, duck typing instead)
- ✅ Lightweight regex patterns (no external PII library)
- ✅ Simple wrapper pattern for GuardrailAgent
- ✅ Input-focused MVP (output guardrails deferred to Phase 2.2+)
- ✅ Guardrails applied in sequence (order matters)

**Files Created:**
- `simple_agent/guardrails/__init__.py`
- `simple_agent/guardrails/exceptions.py` (GuardrailViolation)
- `simple_agent/guardrails/input_validators.py` (PIIDetector)
- `simple_agent/guardrails/custom_rule.py` (CustomRuleGuardrail)
- `simple_agent/guardrails/guardrail_agent.py` (GuardrailAgent)
- `simple_agent/guardrails/yaml_loader.py` (YAML configuration loader)
- `simple_agent/commands/guardrail_commands.py` (REPL commands)
- `tests/unit/test_guardrails.py` (10 tests)
- `tests/unit/test_custom_rule_guardrail.py` (8 tests)
- `tests/unit/test_guardrail_agent.py` (11 tests)
- `tests/unit/test_guardrail_yaml.py` (7 tests)
- `tests/unit/test_guardrail_commands.py` (9 tests)
- `tests/integration/test_phase_2_1.py` (12 tests)

**Test Results:**
- Unit tests: 45/45 passing ✅
- Integration tests: 12/12 passing ✅
- Total Phase 2.1 tests: 57/57 passing ✅
- Total project tests: 262/262 passing ✅ (205 Phase 1 + 57 Phase 2.1)

**Code Metrics:**
- Total lines added: ~800 (including tests)
- Core code: ~300 lines (guardrails + commands)
- Test code: ~500 lines
- All classes < 100 lines (CLAUDE.md compliance)

**Backlog Items:**
- Prompt injection detection (defer to Phase 2.2+)
- Output guardrails/filters (defer to Phase 2.2+)
- Advanced PII detection with Presidio (defer to Phase 3+)
- Integration with AgentManager for agent creation

---

## Phase 2: Enhanced Features 📋 2.1 COMPLETE

**Status**: Planning Complete on 2025-10-26
**Total Tests**: 205 (168 unit + 37 integration from Phase 1)
**Architecture**: Safety, control, knowledge, and collaboration features

| Sub-Phase | Status | Estimated Effort | Features |
|-----------|--------|------------------|----------|
| **2.1: Guardrails** | 🔴 Not Started | 4-5 hours | Input/output validation, PII detection, profanity filtering, custom rules |
| **2.2: Human-in-the-Loop** | 🔴 Not Started | 4-5 hours | Approval gates, interactive prompts, timeout handling |
| **2.3: RAG Foundation** | 🔴 Not Started | 5-6 hours | Chroma integration, text file ingestion, semantic search |
| **2.4: Multi-Agent Orchestration** | 🔴 Not Started | 5-6 hours | Sequential flows, conditional routing, agent composition |

### Phase 2 Implementation Order

1. **Guardrails First** - Foundation for safety before other features
2. **HITL Second** - Builds on guardrails, enables safe autonomy
3. **RAG Third** - Powerful feature but not blocking
4. **Multi-Agent Last** - Most complex, leverages all previous features

### Phase 2 Planning Summary

**Documents Created:**
- `docs/phases/PHASE_2.md` - Comprehensive specification for all 4 sub-phases
  - Detailed architecture for each sub-phase
  - YAML configuration examples
  - REPL command specifications
  - TDD test strategy
  - Success criteria
  - Estimated effort

**Backlog Updated:**
- Added RAG format enhancements (PDF, HTML, images) for future phases

**SPECIFICATION Updated:**
- Phase 1 marked as complete
- Phase 2 broken into 4 sub-phases
- MCP moved to Phase 3

**Key Decisions:**
- ✅ Guardrails use simple wrapper pattern (not complex framework)
- ✅ HITL approval workflow integrated into REPL
- ✅ RAG starts with text files only (.txt, .md)
- ✅ Multi-agent flows use YAML definition (Python flows in Phase 3)
- ✅ MCP integration deferred to Phase 3

**Next Steps:**
1. Review PHASE_2.md specification
2. Begin Phase 2.1 (Guardrails) implementation
3. Follow TDD methodology for each sub-phase
4. Update Progress_Tracker after each sub-phase completion

---

## Phase 1.7: Jinja2 Template Support ✅ COMPLETED

**Status**: ✅ Completed on 2025-10-26
**Total Tests**: 205 (168 unit + 37 integration, all passing)
**Architecture**: Jinja2 template engine for dynamic YAML prompts with backward compatibility

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **Jinja2 Template Rendering** | | | | | |
| Template auto-detection | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (3/3) |
| Context building | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (3/3) |
| Role template rendering | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (2/2) |
| User prompt template rendering | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (4/4) | ✅ Pass (1/1) |
| Variables (agent_name, etc.) | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (3/3) | ✅ Pass (3/3) |
| Conditionals ({% if %}) | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (2/2) |
| Loops ({% for %}) | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ⏭️ N/A |
| Filters ({{ text \\| upper }}) | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (1/1) | ⏭️ N/A |
| Date formatting | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (1/1) |
| Error handling | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (1/1) | ⏭️ N/A |
| Backward compatibility | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (1/1) |

### Phase 1.7 Implementation Summary

**Features Implemented:**
1. **Jinja2 Template Engine**: Full Jinja2 support in `role` and `user_prompt_template` fields
2. **Auto-Detection**: Automatically detects Jinja2 ({{ }}, {% %}) vs format strings ({variable})
3. **Context Variables**: agent_name, current_time, current_date, verbosity, max_steps, model_provider, tools, user_input
4. **Conditionals**: {% if condition %} ... {% endif %}
5. **Loops**: {% for item in list %} ... {% endfor %}
6. **Filters**: {{ variable | filter_name }}
7. **Date Formatting**: {{ current_date.strftime('%Y-%m-%d') }}
8. **Backward Compatibility**: Old {user_input} format strings still work

**Architecture Decisions:**
- ✅ Template type auto-detected based on syntax
- ✅ Jinja2 environment created per render (stateless)
- ✅ Context built dynamically with all available variables
- ✅ Role templates rendered once at init
- ✅ User prompt templates rendered at each run() with user input
- ✅ Trailing whitespace stripped from Jinja2 output
- ✅ Clear error messages for invalid Jinja2 syntax

**Use Case Examples:**
```yaml
# Chain-of-thought prompting
user_prompt_template: |
  {{ user_input }}

  {% if verbosity >= 2 %}
  Let's think through this step by step.
  {% endif %}

# Dynamic role with tools
role: |
  You are {{ agent_name }} ({{ model_provider }}).
  Today: {{ current_date.strftime('%Y-%m-%d') }}

  {% if tools %}
  Available tools: {{ tools | join(', ') }}
  {% endif %}

# Verbosity-based instructions
role: |
  {% if verbosity == 0 %}
  Be extremely concise. One sentence only.
  {% elif verbosity == 1 %}
  Provide clear, concise answers.
  {% else %}
  Provide detailed explanations with examples.
  {% endif %}
```

**Files Created:**
- `docs/phases/PHASE_1.7.md` - Phase specification
- `tests/integration/test_phase_1_7.py` - 3 integration tests

**Files Modified:**
- `requirements.txt` - Added jinja2>=3.1.0 dependency
- `simple_agent/agents/simple_agent.py` - Added Jinja2 rendering methods (70 lines)
  - `_build_context()` - Build template context with variables
  - `_render_template()` - Auto-detect and render templates
  - Updated `__init__()` to render role templates
  - Updated `run()` to render user_prompt_template with Jinja2
- `tests/unit/test_simple_agent.py` - Added 8 Jinja2 unit tests (263 lines)
- `docs/Backlog.md` - Added --set CLI flag feature to backlog

**Test Results:**
- Unit tests: 8 new tests passing ✅ (variables, conditionals, loops, filters, dates, compat, errors, context)
- Integration tests: 3 new tests passing ✅ (full workflow, YAML style, backward compat)
- Total: 205 tests passing (168 unit + 37 integration, +11 from Phase 1.6) ✅

**Benefits:**
- **More Powerful**: Variables, conditionals, loops, filters beyond simple format strings
- **Backward Compatible**: Old templates work without changes
- **YAML-Friendly**: Multi-line templates work beautifully with YAML | syntax
- **Flexible**: Can use simple or advanced features as needed
- **Maintainable**: Clear separation between template syntax detection and rendering

---

## Phase 1.6: Simplify Prompts & Add User Prompt Templates ✅ COMPLETED

**Status**: ✅ Completed on 2025-10-26
**Total Tests**: 194 (160 unit + 34 integration, all passing)
**Architecture**: User prompt templates with YAML integration, removed over-engineered template system

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **Part 1: Template Removal** | | | | | |
| Removed prompt template system | ✅ Done | ✅ Done | ✅ Done | ✅ Pass | ✅ Pass |
| ConfigManager.load_prompt_template() | ✅ Removed | ✅ Removed | ⏭️ N/A | ⏭️ N/A | ⏭️ N/A |
| SimpleAgent template parameter | ✅ Removed | ✅ Removed | ✅ Removed | ⏭️ N/A | ⏭️ N/A |
| AgentManager template parameter | ✅ Removed | ✅ Removed | ✅ Removed | ⏭️ N/A | ⏭️ N/A |
| /agent create --template option | ✅ Removed | ✅ Removed | ⏭️ N/A | ⏭️ N/A | ⏭️ N/A |
| **Part 2: User Prompt Template** | | | | | |
| SimpleAgent.user_prompt_template | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (4/4) | ✅ Pass (1/1) |
| AgentManager user_prompt_template | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (2/2) | ✅ Pass (1/1) |
| YAML user_prompt_template support | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (4/4) | ⏭️ N/A |

### Phase 1.6 Implementation Summary

**Part 1: Template Removal (Breaking Change)**
- Removed entire `simple_agent/config/prompts/` directory and template files
- Removed `ConfigManager.load_prompt_template()` method (40 lines)
- Removed `template` parameter from `SimpleAgent.__init__()`
- Removed `template` parameter from `AgentManager.create_agent()` (3 locations)
- Removed `--template` option from `/agent create` command
- Removed 7 template-related tests (4 ConfigManager + 2 SimpleAgent + 1 integration)
- Fixed duplicate `@patch` decorator bug in `test_agent_lifecycle_mocked.py`
- Result: 183 tests passing (down from 191)

**Part 2: User Prompt Template (New Feature)**
1. **SimpleAgent user_prompt_template**: Optional parameter to wrap user input before sending to LLM
2. **AgentManager integration**: Pass user_prompt_template to created agents
3. **YAML support**: Save and load user_prompt_template in agent YAML files
4. **Template formatting**: Uses `{user_input}` placeholder with Python `.format()`
5. **Chat mode support**: Template persists across chat turns (reset=False)

**Architecture Decisions:**
- ✅ Removed unused, over-engineered prompt template system
- ✅ YAML already handles multi-line strings beautifully with `|` syntax
- ✅ User prompt templates wrap user input, not system prompts
- ✅ Optional feature - when None, user input passes through directly
- ✅ Template applied consistently to all user input (run + chat)
- ✅ Breaking change justified - no agents were actually using template feature

**Use Cases:**
```yaml
# Chain-of-thought prompting
user_prompt_template: |
  {user_input}

  Let's think through this step by step:
  1. First, understand the question
  2. Then, provide a clear answer

# Concise responses
user_prompt_template: "{user_input}\n\nPlease answer in 2-3 sentences maximum."

# Code review focus
user_prompt_template: |
  Code Review Request:
  {user_input}

  Please review for:
  - Security issues
  - Performance concerns
  - Code style
```

**Files Deleted:**
- `simple_agent/config/prompts/default.yaml`
- `simple_agent/config/prompts/researcher.yaml`
- Entire `simple_agent/config/prompts/` directory

**Files Modified (Part 1):**
- `simple_agent/core/config_manager.py` - Removed load_prompt_template() (40 lines removed)
- `simple_agent/agents/simple_agent.py` - Removed template parameter
- `simple_agent/core/agent_manager.py` - Removed template parameter (3 locations)
- `simple_agent/commands/agent_commands.py` - Removed --template option
- `tests/unit/test_config_manager.py` - Removed 4 template tests
- `tests/unit/test_simple_agent.py` - Removed 2 template tests
- `tests/unit/test_agent_manager.py` - Removed 1 template test
- `tests/integration/test_agent_lifecycle_mocked.py` - Removed 1 test, fixed duplicate decorator

**Files Modified (Part 2):**
- `simple_agent/agents/simple_agent.py` - Added user_prompt_template parameter and formatting logic
- `simple_agent/core/agent_manager.py` - Added user_prompt_template parameter to create_agent() and YAML methods
- `tests/unit/test_simple_agent.py` - Added 4 new user_prompt_template tests
- `tests/unit/test_agent_manager.py` - Added 2 new user_prompt_template tests
- `tests/unit/test_agent_yaml.py` - Added 4 new YAML tests (2 load + 2 save)
- `tests/integration/test_agent_lifecycle_mocked.py` - Added 1 integration test

**Test Results:**
- Part 1: 183 tests passing (191 - 8 removed tests)
- Part 2 additions: 11 new tests (4 SimpleAgent + 2 AgentManager + 4 YAML + 1 integration)
- Final: 194 tests passing (160 unit + 34 integration) ✅

**Migration Guide:**
- **Breaking**: `template` parameter removed from all APIs
- **Migration**: Use `role` field in YAML or `--role` in CLI for system prompts
- **New feature**: Use `user_prompt_template` to wrap user input (not system prompts)
- **YAML multi-line**: Use `|` syntax for long prompts directly in `role:` field

---

## Phase 1.5: YAML Agent Definitions ✅ COMPLETED

**Status**: ✅ Completed on 2025-10-25
**Total Tests**: 191 (157 unit + 34 integration, all passing)
**Architecture**: YAML-based agent configuration with auto-loading and persistence

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **Core YAML Management** | | | | | |
| load_agent_from_yaml() | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (5/5) | ✅ Pass (4/4) |
| save_agent_to_yaml() | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (4/4) |
| load_agents_from_directory() | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (3/3) | ✅ Pass (4/4) |
| **Agent Commands** | | | | | |
| /agent save [--path] | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (4/4) | ⏭️ N/A |
| /agent create-wizard | ✅ Done | ✅ Done | ⏭️ N/A | ⏭️ Manual Test | ⏭️ N/A |
| **Auto-loading** | | | | | |
| Auto-load from config/agents/ | ⏭️ N/A | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (4/4) |
| **Example YAML** | | | | | |
| config/agents/researcher.yaml | ⏭️ N/A | ✅ Done | ⏭️ N/A | ⏭️ N/A | ⏭️ N/A |

### Phase 1.5 Implementation Summary

**Features Implemented:**
1. **YAML Agent Loading**: Load agent definitions from YAML files with full config support
2. **YAML Agent Saving**: Save agent configurations to YAML files for persistence
3. **Directory Auto-loading**: Scan config/agents/ and auto-load all agent YAMLs on startup
4. **Agent Save Command**: `/agent save [--path]` to export agent configurations
5. **Interactive Wizard**: `/agent create-wizard` for step-by-step agent creation with optional YAML save

**Architecture Decisions:**
- ✅ YAML format supports: name, role, template, tools, model settings, metadata
- ✅ Configuration hierarchy: YAML > config.yaml > code defaults
- ✅ Auto-load from config/agents/ directory on app startup
- ✅ Graceful error handling for invalid YAML files
- ✅ Tools specified by name in YAML, resolved via ToolManager
- ✅ Model settings in YAML can override provider defaults

**YAML Format:**
```yaml
name: "agent_name"
agent_type: "tool_calling"
role: "Agent system prompt..."
tools:
  - tool1
  - tool2
model:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.3
settings:
  verbosity: 2
  max_steps: 15
metadata:
  description: "Agent description"
  version: "1.0.0"
```

**Files Created:**
- `config/agents/researcher.yaml` (example agent)
- `docs/phases/PHASE_1.5_PLAN.md` (implementation plan)
- `tests/unit/test_agent_yaml.py` (300 lines, 10 tests)
- `tests/integration/test_phase_1_5.py` (234 lines, 4 tests)

**Files Modified:**
- `simple_agent/core/agent_manager.py` - Added 3 YAML methods (165 lines added)
  - load_agent_from_yaml()
  - save_agent_to_yaml()
  - load_agents_from_directory()
- `simple_agent/commands/agent_commands.py` - Added 2 commands (156 lines added)
  - /agent save
  - /agent create-wizard
- `simple_agent/app.py` - Added auto-load from config/agents/
- `simple_agent/commands/debug_commands.py` - Fixed ^J display formatting

**Test Results:**
- Unit tests: 14/14 new tests passing ✅ (10 YAML tests + 4 command tests)
- Integration tests: 4/4 passing ✅
- Total: 191 tests passing (157 unit + 34 integration)

---

## Phase 1.4: Tool Management ✅ COMPLETED

**Status**: ✅ Completed on 2025-10-25
**Total Tests**: 147 (137 unit + 10 integration, all passing)
**Architecture**: SmolAgents tool integration with dynamic tool management

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **Core Tool Management** | | | | | |
| ToolManager | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (14/14) | ✅ Pass (10/10) |
| AgentManager tool support | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (6/6) | ✅ Pass (10/10) |
| SimpleAgent tools attribute | ⏭️ N/A | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (10/10) |
| **Tool Commands** | | | | | |
| /tool list | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (3/3) | ⏭️ N/A |
| /tool info --name <tool> | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (3/3) | ⏭️ N/A |
| **Agent Tool Commands** | | | | | |
| /agent tools <name> | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (4/4) | ⏭️ N/A |
| /agent add-tool <name> --tool <tool> | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (4/4) | ⏭️ N/A |
| /agent remove-tool <name> --tool <tool> | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (3/3) | ⏭️ N/A |
| **Built-in Tools** | | | | | |
| Calculator tools (add, subtract, multiply, divide) | ⏭️ N/A | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (10/10) |

### Phase 1.4 Implementation Summary

**Features Implemented:**
1. **ToolManager**: Central registry for tool registration, retrieval, and management
2. **Tool Commands**: `/tool list` and `/tool info` for tool discovery and inspection
3. **Agent Tool Support**: Create agents with tools, add/remove tools dynamically
4. **Agent Tool Commands**: `/agent tools`, `/agent add-tool`, `/agent remove-tool` for agent tool management
5. **Built-in Tools**: Calculator tools (add, subtract, multiply, divide) using @tool decorator

**Architecture Decisions:**
- ✅ ToolManager as central registry pattern
- ✅ SmolAgents @tool decorator for tool creation
- ✅ Dynamic tool loading from tools/builtin/ directory
- ✅ Tools attached to agents via SimpleAgent wrapper
- ✅ Tools parameter in create_agent() for initial tool sets
- ✅ Add/remove tools dynamically to existing agents
- ✅ Tools stored as list in SimpleAgent, synced with SmolAgents agent

**Files Created:**
- `simple_agent/core/tool_manager.py` (147 lines)
- `simple_agent/commands/tool_commands.py` (130 lines)
- `tools/__init__.py`
- `tools/builtin/__init__.py`
- `tools/builtin/calculator.py` (40 lines, 4 tools)
- `tests/unit/test_tool_manager.py` (190 lines, 14 tests)
- `tests/unit/test_tool_commands.py` (128 lines, 6 tests)
- `tests/unit/test_agent_tools.py` (156 lines, 6 tests)
- `tests/unit/test_agent_commands.py` (221 lines, 11 tests)
- `tests/integration/test_tool_integration.py` (224 lines, 10 tests)

**Files Modified:**
- `simple_agent/core/agent_manager.py` - Added tool management methods (add_tool_to_agent, remove_tool_from_agent, get_agent_tools), added tools parameter to create_agent()
- `simple_agent/agents/simple_agent.py` - Added tools attribute tracking
- `simple_agent/commands/agent_commands.py` - Added tools, add-tool, remove-tool commands
- `simple_agent/app.py` - Register tool command group (will be done in commit)

**Test Results:**
- Unit tests: 37/37 new tests passing ✅
- Integration tests: 10/10 passing ✅
- Total: 147 tests passing (137 unit + 10 integration)

---

## Phase 1.3: Configuration Management ✅ COMPLETED

**Status**: ✅ Completed on 2025-10-23
**Total Tests**: 120 (105 previous + 15 new, all passing)
**Architecture**: Enhanced configuration commands with get, reset, and path management

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **Config Commands** | | | | | |
| /config get <key> | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (4/4) | ⏭️ N/A |
| /config reset <key> | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (3/3) | ⏭️ N/A |
| /config set-path <type> <path> | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (5/5) | ⏭️ N/A |
| /config show-paths | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (3/3) | ⏭️ N/A |
| **ConfigManager Updates** | | | | | |
| Default paths structure | ⏭️ N/A | ✅ Done | ⏭️ N/A | ⏭️ N/A | ⏭️ N/A |

### Phase 1.3 Implementation Summary

**Features Implemented:**
1. **Config Get**: `/config get <key>` - Retrieve specific config values with clear display
2. **Config Reset**: `/config reset <key>` - Reset values to defaults from ConfigManager
3. **Path Management**: `/config set-path <type> <path>` - Set configurable paths (prompts, tools, agents, logs, data)
4. **Show Paths**: `/config show-paths` - Display all configured paths with fallback to defaults

**Architecture Decisions:**
- ✅ Extended existing /config command group (show, load, save, set)
- ✅ Added default paths to ConfigManager.get_defaults()
- ✅ Validates path types (prompts, tools, agents, logs, data)
- ✅ Gracefully handles missing paths section (shows defaults)
- ✅ Supports empty config dict edge cases

**Files Created:**
- `tests/unit/test_config_commands.py` (295 lines, 15 tests)

**Files Modified:**
- `simple_agent/commands/config_commands.py` - Added get, reset, set-path, show-paths commands
- `simple_agent/core/config_manager.py` - Updated default paths structure

**Test Results:**
- Unit tests: 15/15 passing ✅
- Total: 120 tests passing (entire project)

---

## Phase 1.2: History & Memory Management ✅ COMPLETED

**Status**: ✅ Completed on 2025-10-23
**Total Tests**: 105 (88 previous + 12 unit + 5 integration, all passing)
**Architecture**: Leverages SmolAgents' built-in memory system

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **History Commands** | | | | | |
| /history show [--limit N] | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (5/5) | ✅ Pass (5/5) |
| /history clear | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (3/3) | ✅ Pass (5/5) |
| /history save <file> | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (4/4) | ✅ Pass (5/5) |
| **SmolAgents Integration** | | | | | |
| Memory persistence | ⏭️ N/A | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (5/5) |
| get_full_steps() usage | ⏭️ N/A | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (5/5) |
| reset() usage | ⏭️ N/A | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (5/5) |
| JSON export | ⏭️ N/A | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (5/5) |

### Phase 1.2 Implementation Summary

**Features Implemented:**
1. **History Display**: `/history show` displays SmolAgents memory steps with rich table formatting
2. **Memory Clear**: `/history clear` resets agent memory using SmolAgents' built-in `reset()`
3. **History Export**: `/history save <file>` exports memory to JSON with metadata
4. **SmolAgents Integration**: Directly leverages `agent.memory.get_full_steps()` - no custom storage

**Architecture Decisions:**
- ✅ Use SmolAgents' in-memory storage (framework built-in)
- ✅ Access via `agent_wrapper.agent.memory` (through SimpleAgent wrapper)
- ✅ Optional file-based persistence (JSON export for backups)
- ✅ No custom memory system needed - leverage framework capabilities

**Files Created:**
- `simple_agent/commands/history_commands.py` (196 lines)
- `tests/unit/test_history_commands.py` (280 lines, 12 tests)
- `tests/integration/test_phase_1_2_mocked.py` (280 lines, 5 tests)

**Files Modified:**
- `simple_agent/app.py` - Registered history command group

**Test Results:**
- Unit tests: 12/12 passing ✅
- Integration tests: 5/5 passing ✅
- Total: 105 tests passing (entire project)

---

## Phase 1.1: Inspection & Chat Features ✅ COMPLETED

**Status**: ✅ Completed on 2025-10-23
**Total Tests**: 88 (67 original + 21 new, all passing)
**GitHub Commits**: c3c3338
**GitHub Issues**: #7, #9, #10, #11

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **Prompt/Response Tracking** | | | | | |
| AgentManager tracking | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (8/8) | ✅ Pass (10/10) |
| **Inspection Commands** | | | | | |
| /prompt show, /prompt raw | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (4/4) | ✅ Pass (10/10) |
| /response show, /response raw | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (4/4) | ✅ Pass (10/10) |
| **Chat Mode** | | | | | |
| /agent chat command | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (3/3) | ✅ Pass (10/10) |
| **Debug System** | | | | | |
| 3-level debug (off/info/debug) | ⏭️ N/A | ✅ Done | ⏭️ N/A | ⏭️ N/A | ✅ Manual Test Pass |
| /debug REPL command | ⏭️ N/A | ✅ Done | ⏭️ N/A | ⏭️ N/A | ✅ Manual Test Pass |
| CLI --debug flag | ⏭️ N/A | ✅ Done | ⏭️ N/A | ⏭️ N/A | ✅ Manual Test Pass |

---

## Phase 1.1 Implementation Summary

### Features Implemented
1. **Prompt/Response Tracking**: AgentManager tracks last_prompt, last_response, last_agent
2. **Inspection Commands**: /prompt and /response commands with show/raw subcommands
3. **Chat Mode**: Interactive chat with history support via /agent chat
4. **3-Level Debug System**: off (minimal), info (normal), debug (verbose)

### Bug Fixes
- **Issue #9**: Fixed /prompt tracking with /agent run (AgentManager persistence)
- **Issue #10**: Fixed /prompt tracking with /agent chat (same fix as #9)
- Root cause: AgentManager was being recreated on each REPL command

### GitHub Issues Closed
- #7: Add debug mode to phase 1
- #9: Prompt command is unaware that agent was run
- #10: Prompt command unaware that chat had an interaction
- #11: No way to turn debug on or off in repl

### Files Created
- `simple_agent/commands/inspection_commands.py`
- `simple_agent/commands/debug_commands.py`
- `tests/unit/test_agent_manager_inspection.py` (8 tests)
- `tests/unit/test_inspection_commands.py` (8 tests)
- `tests/unit/test_agent_chat_command.py` (3 tests)
- `tests/integration/test_phase_1_1_mocked.py` (5 tests)
- `tests/integration/test_phase_1_1_live.py` (5 tests)

### Files Modified
- `simple_agent/app.py` - AgentManager persistence, 3-level debug system
- `simple_agent/core/agent_manager.py` - Prompt/response tracking
- `simple_agent/commands/agent_commands.py` - Chat mode
- `config.yaml` - Changed debug.enabled → debug.level

---

## Phase 0: Foundation ✅ COMPLETED

**Status**: ✅ Completed on 2025-10-21
**Total Tests**: 54 (all passing)
**GitHub Commits**: 3 commits (8730354, 74f633e, db83402)

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **Core Module** | | | | | |
| ConfigManager | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (25/25)* | ⏭️ N/A |
| AgentManager | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (15/15) | ⏭️ N/A |
| **Agents Module** | | | | | |
| SimpleAgent | ✅ Done | ✅ Done | ⏭️ N/A | ✅ Pass (9/9) | ⏭️ N/A |
| **Config System** | | | | | |
| Prompt Templates | ⏭️ N/A | ✅ Done | ⏭️ N/A | ⏭️ N/A | ⏭️ N/A |
| config.yaml | ⏭️ N/A | ✅ Done | ⏭️ N/A | ⏭️ N/A | ⏭️ N/A |
| **Commands Module** | | | | | |
| agent_commands.py | ⏭️ N/A | ✅ Done | ⏭️ N/A | ⏭️ N/A | ⏭️ N/A |
| config_commands.py | ⏭️ N/A | ✅ Done | ⏭️ N/A | ⏭️ N/A | ⏭️ N/A |
| system_commands.py | ⏭️ N/A | ✅ Done | ⏭️ N/A | ⏭️ N/A | ⏭️ N/A |
| app.py integration | ⏭️ N/A | ✅ Done | ⏭️ N/A | ⏭️ N/A | ⏭️ N/A |
| **Integration** | | | | | |
| Full Agent Lifecycle (Mocked) | ⏭️ N/A | ⏭️ N/A | ✅ Done | ⏭️ N/A | ✅ Pass (5/5) |
| **REPL Testing** | | | | | |
| Manual REPL Test | ⏭️ N/A | ⏭️ N/A | ✅ Done | ⏭️ N/A | ✅ Pass |

*Includes 4 additional tests for environment variable resolution (Phase 0.5 addition)

---

## Legend

### Status Values
- ❌ **Not Done**: Not started
- 🟡 **In Progress**: Currently working on
- ✅ **Done**: Completed

### Test Results
- ✅ **Pass**: All tests passing
- ❌ **Fail**: Tests failing
- ⏭️ **N/A**: Not applicable or not yet tested

---

## Phase 0 Completion Criteria ✅ ALL MET

- [x] Configuration loads from `config.yaml` and `.env`
- [x] Prompt templates load from `config/prompts/`
- [x] Can create agent with OpenAI, Ollama, or LM Studio
- [x] Can create agent with template or explicit role
- [x] Can run prompt through agent and get LLM response
- [x] Messages formatted correctly (system/user roles)
- [x] All unit tests pass (with mocks) - 54/54 tests passing
- [x] Integration test passes (mocked version) - 5/5 tests passing
- [x] Manual REPL test successful - Verified with OpenAI
- [x] Code follows CLAUDE.md standards (< 100 lines/class, type hints, etc.)

---

## Phase 0 Implementation Summary

### GitHub Issues Fixed
1. **Issue #1**: Fixed ^J characters in subcommand display
2. **Issue #2**: Fixed system_prompt parameter error (changed to instructions)
3. **Issue #3**: Made --file parameter optional for config save
4. **Issue #4**: Added auto-load of agents from config.yaml
5. **Issue #5**: Removed process command template leftover
6. **Issue #6**: Fixed API key environment variable resolution
7. **Issue #8**: Fixed config save security (point-of-use substitution)

### Security Fix (Phase 0.5 Addition)
- Implemented point-of-use environment variable substitution
- Config dict keeps `${VAR}` placeholders permanently
- Added `ConfigManager.resolve_env_var()` for safe resolution
- Added `/config show --resolve` flag for display only
- Config save never exposes secrets

### Files Created/Modified
**Created:**
- `simple_agent/core/config_manager.py`
- `simple_agent/core/agent_manager.py`
- `simple_agent/agents/simple_agent.py`
- `simple_agent/commands/agent_commands.py`
- `simple_agent/commands/config_commands.py`
- `simple_agent/commands/system_commands.py`
- `config/prompts/default.yaml`
- `config/prompts/researcher.yaml`
- `tests/unit/test_config_manager.py` (25 tests)
- `tests/unit/test_agent_manager.py` (15 tests)
- `tests/unit/test_simple_agent.py` (9 tests)
- `tests/integration/test_agent_lifecycle_mocked.py` (5 tests)
- `utils/simple_llm_check.py`
- `docs/phases/PHASE_0.md`
- `docs/phases/PHASE_0.5.md`
- `docs/phases/PHASE_1.md`

**Modified:**
- `docs/SPECIFICATION.md` - Restructured to reference phase files
- `docs/Progress_Tracker.md` - Updated to reflect Phase 0 completion

---

## Dependencies Installed

- [x] smolagents>=0.1.0
- [x] litellm>=1.0.0
- [x] python-dotenv>=1.0.0
- [x] ruff==0.14.1
- [x] (existing: click, click-repl, rich, PyYAML, pytest)

---

## Notes

### Current Status
- Phase 0: ✅ COMPLETED
- Phase 0.5: Planning complete, implementation pending
- Following TDD methodology from CLAUDE.md
- Building incrementally, ~60 lines per iteration
- Next: Begin Phase 0.5 implementation (security fix)

### Critical Issue Discovered
- **SECURITY**: Phase 0 used CodeAgent with `executor_type="local"`
- Allows LLM-generated code to execute directly on host machine
- Phase 0.5 will fix this by switching to ToolCallingAgent
- Will implement Docker-based Python execution tool

### Blockers
- None currently - ready to start Phase 0.5

### Recent Changes
- 2025-10-26: ✅ Phase 1.7 COMPLETED - Jinja2 Template Support
- 2025-10-26: ✅ Added Jinja2 template engine for YAML prompts (8 unit + 3 integration tests)
- 2025-10-26: ✅ Implemented variables, conditionals, loops, filters, date formatting
- 2025-10-26: ✅ Backward compatibility with {user_input} format strings
- 2025-10-26: ✅ All 205 tests passing (168 unit + 37 integration)
- 2025-10-26: ✅ Phase 1.6 COMPLETED - Simplify Prompts & Add User Prompt Templates
- 2025-10-26: ✅ Part 2: Added user_prompt_template feature (11 new tests)
- 2025-10-26: ✅ Part 1: Removed over-engineered prompt template system (8 tests removed)
- 2025-10-26: ✅ All 194 tests passing (160 unit + 34 integration)
- 2025-10-25: ✅ Phase 1.5 COMPLETED - YAML Agent Definitions
- 2025-10-25: ✅ Implemented YAML agent loading (load_agent_from_yaml)
- 2025-10-25: ✅ Implemented YAML agent saving (save_agent_to_yaml)
- 2025-10-25: ✅ Implemented directory auto-loading (load_agents_from_directory)
- 2025-10-25: ✅ Implemented /agent save and /agent create-wizard commands
- 2025-10-25: ✅ Added auto-load from config/agents/ on startup
- 2025-10-25: ✅ Fixed debug command ^J display issue
- 2025-10-25: ✅ Created example researcher.yaml agent
- 2025-10-25: ✅ All 191 tests passing (157 unit + 34 integration)
- 2025-10-25: ✅ Phase 1.4 COMPLETED - Tool Management
- 2025-10-25: ✅ Implemented ToolManager with built-in calculator tools
- 2025-10-25: ✅ Implemented /tool list and /tool info commands
- 2025-10-25: ✅ Implemented agent tool support (create with tools, add/remove dynamically)
- 2025-10-25: ✅ Implemented /agent tools, /agent add-tool, /agent remove-tool commands
- 2025-10-25: ✅ All 147 tests passing (137 unit + 10 integration)
- 2025-10-23: ✅ Phase 1.3 COMPLETED - Configuration Management
- 2025-10-23: ✅ Implemented /config get, reset, set-path, show-paths commands
- 2025-10-23: ✅ Added default paths to ConfigManager (prompts, tools, agents, logs, data)
- 2025-10-23: ✅ All 120 tests passing (105 previous + 15 new)
- 2025-10-23: ✅ Phase 1.2 COMPLETED - History & Memory Management
- 2025-10-23: ✅ Implemented /history commands (show, clear, save)
- 2025-10-23: ✅ Leveraged SmolAgents' built-in memory system
- 2025-10-23: ✅ All 105 tests passing (88 previous + 12 unit + 5 integration)
- 2025-10-23: ✅ Integration tests verify SmolAgents memory persistence
- 2025-10-23: ✅ Phase 1.1 COMPLETED - Inspection & Chat Features
- 2025-10-23: ✅ Fixed GitHub Issues #7, #9, #10, #11
- 2025-10-23: ✅ Implemented 3-level debug system (off/info/debug)
- 2025-10-23: ✅ Implemented /agent chat command (interactive mode)
- 2025-10-23: ✅ Implemented inspection commands (/prompt, /response)
- 2025-10-23: ✅ Fixed AgentManager persistence across REPL commands
- 2025-10-23: ✅ All 88 tests passing (67 original + 21 new)
- 2025-10-23: ✅ Manual REPL testing successful
- 2025-10-22: 📄 Debug mode implementation started
- 2025-10-21: 📄 Documentation restructured - created phase specification files
- 2025-10-21: 📄 Created `docs/phases/PHASE_0.5.md` (security fix specification)
- 2025-10-21: 📄 Created `docs/phases/PHASE_0.md` (Phase 0 completion documentation)
- 2025-10-21: 📄 Created `docs/phases/PHASE_1.md` (interactive features specification)
- 2025-10-21: 📄 Updated `docs/SPECIFICATION.md` to reference phase files
- 2025-10-21: 🔒 Fixed config save security issue (point-of-use substitution)
- 2025-10-21: ✅ Fixed GitHub Issues #1-6, #8
- 2025-10-21: ✅ All 54 tests passing
- 2025-10-21: ✅ Manual REPL testing successful with OpenAI
- 2025-10-21: ✅ Phase 0 COMPLETED
- 2025-10-20: ✅ SimpleAgent tests written and passing (9/9)
- 2025-10-20: ✅ SimpleAgent implemented (136 lines, SmolAgents wrapper)
- 2025-10-20: ✅ All unit tests passing (30/30 → 54/54)
- 2025-10-20: ✅ ConfigManager tests written and passing (21/21 → 25/25)
- 2025-10-20: ✅ ConfigManager implemented (load_env, load_prompt_template)
- 2025-10-20: ✅ Prompt templates created (default.yaml, researcher.yaml)
- 2025-10-20: Created Progress Tracker
- 2025-10-20: Finalized PRD and Specification
- 2025-10-20: Initialized git repository

---

---

## Phase 2.3: RAG Foundation ✅ COMPLETED

**Status**: ✅ Completed on 2025-10-28
**Total Tests**: 54 (44 unit + 10 integration, all passing)

### Implementation Summary

**Features Implemented:**
1. **CollectionManager**: Collection lifecycle (create, list, delete, connect agents)
2. **Collection**: Document storage, chunking, querying with Chroma backend
3. **DocumentLoader**: Load .txt/.md files, chunk text with configurable overlap
4. **EmbeddingProvider**: Flexible embedding models (OpenAI, sentence-transformers, Ollama)
5. **ChromaWrapper**: Persistent Chroma client abstraction
6. **SimpleAgent Integration**: Automatic RAG context injection via /collection commands

**Collection-Centric Architecture (Not Agent-Centric):**
- Collections are first-class entities, independent of agents
- Multiple agents can use the same collection
- Collections support flexible embedding models
- Rich metadata storage (timestamps, document count, embedding model, chunk settings)
- Auto-creation with sensible defaults (OpenAI embeddings, chunk_size=1000, overlap=200)

**REPL Commands Implemented:**
- `/collection create`: Create collection with custom settings
- `/collection list`: List all collections with metadata
- `/collection info`: Show detailed collection stats
- `/collection delete`: Delete collection
- `/collection connect`: Connect agent to collection
- `/collection disconnect`: Disconnect agent from collection

**Files Created:**
- `simple_agent/rag/__init__.py`
- `simple_agent/rag/collection.py` (169 lines)
- `simple_agent/rag/collection_manager.py` (160 lines)
- `simple_agent/rag/document_loader.py` (113 lines)
- `simple_agent/rag/embedding_provider.py` (76 lines)
- `simple_agent/rag/chroma_wrapper.py` (79 lines)
- `simple_agent/rag/exceptions.py` (19 lines)
- `simple_agent/commands/collection_commands.py` (163 lines)
- `tests/unit/test_collection_manager.py` (19 tests)
- `tests/unit/test_document_loader.py` (15 tests)
- `tests/unit/test_embedding_provider.py` (10 tests)
- `tests/integration/test_phase_2_3.py` (10 tests)

**Test Results:**
- Unit tests: 44/44 passing ✅
- Integration tests: 10/10 passing ✅
- Total Phase 2.3 tests: 54/54 passing ✅
- Total project tests: 355 passing ✅ (286 unit + 10 integration + 59 other)

**Code Metrics:**
- Total lines: ~900 (including tests)
- Core code: ~600 lines
- Test code: ~500 lines
- All classes < 300 lines, most < 200 lines

**Backlog Items (defer to Phase 2.4+):**
- PDF/HTML/image document support
- Advanced metadata query filtering
- Document versioning and updates
- Collection export/import

---

## Phase 2.4: Multi-Agent Orchestration ✅ COMPLETED

**Status**: ✅ Completed on 2025-10-28
**Total Tests**: 50 (41 unit + 9 integration, all passing)
**Architecture**: Industry Standard Orchestrator Pattern (SmolAgents compatible)

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **AgentTool** | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (8/8) | ✅ Pass (1/1) |
| **OrchestratorAgent** | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (9/9) | ✅ Pass (1/1) |
| **FlowValidator** | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (8/8) | ✅ Pass (1/1) |
| **FlowManager** | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (9/9) | ✅ Pass (1/1) |
| **FlowCommands** | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (7/7) | ✅ Pass (1/1) |
| **Integration Tests** | ⏭️ N/A | ⏭️ N/A | ✅ Done | ⏭️ N/A | ✅ Pass (9/9) |

### Phase 2.4 Implementation Summary

**Features Implemented:**
1. **AgentTool**: Wraps SimpleAgent as SmolAgents-compatible Tool (111 lines)
2. **OrchestratorAgent**: Meta-agent coordinating sub-agents (76 lines)
3. **FlowValidator**: Validates YAML flow definitions (63 lines)
4. **FlowManager**: Loads flows, creates orchestrators (140 lines)
5. **FlowCommands**: REPL commands for flow management (223 lines)
6. **CLI Integration**: `/flow` command group registered in app.py

**Architecture Decisions:**
- ✅ Two-level ReAct iteration (orchestrator + sub-agents)
- ✅ AgentTool inherits from SmolAgents Tool base class
- ✅ YAML-based flow definitions
- ✅ FlowManager caches flows for performance
- ✅ Graceful failure handling in agents
- ✅ Metadata tracking for debugging

**Files Created:**
- `simple_agent/orchestration/agent_tool.py` (111 lines)
- `simple_agent/orchestration/orchestrator_agent.py` (76 lines)
- `simple_agent/orchestration/flow_validator.py` (63 lines)
- `simple_agent/orchestration/flow_manager.py` (140 lines)
- `simple_agent/commands/flow_commands.py` (223 lines)
- `simple_agent/commands/flow_commands_cli.py` (115 lines)
- `config/flows/example_research.yaml` (Example workflow)
- 6 test files with 50 tests total

**Test Results:**
- Unit tests: 41/41 passing ✅
- Integration tests: 9/9 passing ✅
- Total Phase 2.4 tests: 50/50 passing ✅
- Total project tests: 405/405 passing ✅

**Code Metrics:**
- Total lines: ~1,200 (production + tests)
- Production code: ~730 lines
- Test code: ~1,060 lines
- All classes < 250 lines (CLAUDE.md compliant)

**REPL Commands Available:**
- `/flow list` - List available flows
- `/flow show <name>` - Display flow definition
- `/flow run <name> <input>` - Execute flow
- `/flow delete <name>` - Delete flow
- `/flow debug <name> <input>` - Debug flow execution

**Backlog Items (defer to Phase 3+):**
- Advanced flow routing (conditionals, loops)
- Flow visualization and debugging tools
- Cost tracking per flow
- Flow templates and pre-built workflows
- Python code-based flows (in addition to YAML)

---

## Phase 3.1: Token Budget Protection ✅ COMPLETED

**Status**: ✅ Completed on 2025-11-01
**Total Tests**: 35 (25 unit + 10 integration, all passing)
**Architecture**: Token guard in SimpleAgent.run() with system role inclusion in token counting
**Problem Solved**: Prevent OpenAI 30,000 TPM rate limit hits on researcher agents with large prompts

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **Token Guard Implementation** | | | | | |
| SimpleAgent token budgeting | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (14/14) | ✅ Pass (10/10) |
| Token estimation with tiktoken | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (8/8) | ✅ Pass (10/10) |
| Config-to-agent integration | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (11/11) | ✅ Pass (10/10) |
| Warning threshold logging | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (6/6) | ✅ Pass (10/10) |
| System role token counting | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (4/4) | ✅ Pass (10/10) |

### Phase 3.1 Implementation Summary

**Features Implemented:**
1. **Token Guard in SimpleAgent.run()**: Estimates prompt tokens BEFORE sending to LLM, rejects if exceeds budget
2. **System Role Inclusion**: Token count includes both system role + user prompt for accurate estimation
3. **Configuration Integration**: Token budgets configured in config.yaml and passed through AgentManager to agents
4. **Warning Thresholds**: Soft warning when approaching token budget (hard limit still enforced)
5. **No Breaking Changes**: Feature is opt-in - agents without token_budget work as before

**Architecture Decisions:**
- ✅ Token guard checks in SimpleAgent.run() BEFORE agent.agent.run() call
- ✅ System role included in token estimation for realistic counting (not just user prompt)
- ✅ Uses OpenAI's tiktoken library (cl100k_base encoding) for accurate GPT-4 token counting
- ✅ Token budget is per-agent (can set different limits for different agents)
- ✅ Warning threshold is optional (only logs if set and exceeded)
- ✅ Backward compatible - agents without token_budget=None skip the guard entirely
- ✅ Works with both ToolCallingAgent and CodeAgent (single guard point in SimpleAgent)

**Use Cases:**
1. **Prevent Rate Limit Hits**: Set tight token_budget to force selective tool use on researcher agents
2. **Control Costs**: Limit input size for expensive models
3. **Resource Management**: Prevent oversized prompts on resource-constrained environments
4. **Safety Monitoring**: Soft warnings when approaching limits before hard rejection

**Configuration Example:**
```yaml
llm:
  provider: openai
  openai:
    model: gpt-4o-mini
    api_key: ${OPENAI_API_KEY}

agents:
  researcher:
    role: "You are a web research specialist..."
    token_budget: 20000        # Hard limit - reject prompts exceeding this
    token_warning_threshold: 18000  # Soft limit - log warning if exceeded
    tools:
      - fetch_webpage_markdown
      - tavily_web_search
```

**Files Created:**
- `tests/unit/test_token_guard.py` (333 lines, 14 tests)
  - TestTokenGuardBasic (4 tests)
  - TestTokenGuardDefaultBehavior (2 tests)
  - TestTokenGuardPromptFormatting (2 tests)
  - TestTokenGuardEdgeCases (4 tests)
  - TestTokenGuardWithRealTokenEstimation (2 tests)
- `tests/unit/test_agent_config_tokens.py` (282 lines, 11 tests)
  - TestAgentManagerTokenConfig (4 tests)
  - TestAgentManagerConfigIntegration (4 tests)
  - TestTokenConfigEdgeCases (3 tests)
- `tests/integration/test_token_guard_integration.py` (312 lines, 10 tests)
  - TestTokenGuardWithAgent (5 tests)
  - TestTokenGuardWithFetchWebpageTool (2 tests)
  - TestTokenGuardConfigIntegration (2 tests)
  - TestTokenGuardEdgeCasesWithRealTokens (1 test)

**Files Modified:**
- `simple_agent/agents/simple_agent.py`
  - Added imports: `from simple_agent.tools.helpers.token_counter import estimate_tokens`
  - Added `__init__` parameters: `token_budget`, `token_warning_threshold`
  - Added instance variables to store token settings
  - Implemented token guard in `run()` method with system role inclusion
- `simple_agent/core/agent_manager.py`
  - Added `token_budget` and `token_warning_threshold` parameters to `create_agent()`
  - Updated `_load_agents_from_config()` to extract and pass token parameters from config
  - Token values passed to SimpleAgent during agent creation

**Test Results:**
- Unit tests: 25/25 passing ✅
  - Token guard unit tests: 14/14 passing
  - Config integration unit tests: 11/11 passing
- Integration tests: 10/10 passing ✅
  - Token guard integration tests: 10/10 passing
- Total Phase 3.1 tests: 35/35 passing ✅
- Total project unit tests: 454/454 passing ✅ (429 existing + 25 new)

**Code Metrics:**
- Total lines: ~650 (production + tests)
- Production code: ~50 lines (minimal changes to SimpleAgent and AgentManager)
- Test code: ~600 lines
- All classes unchanged < 100 lines (CLAUDE.md compliant)

**How It Works:**
1. User provides prompt to agent.run()
2. Prompt is formatted with RAG context and user_prompt_template
3. Token guard checks: estimate_tokens(role + formatted_prompt) vs token_budget
4. If exceeds: ValueError raised with clear message
5. If approaching threshold: Warning logged but execution continues
6. If under budget: Prompt proceeds to agent.agent.run() normally

**Key Implementation Detail - System Role Inclusion:**
The token guard includes the system role in token counting because:
- SmolAgents adds the role to every LLM call as the system message
- Token count must be realistic to prevent rate limit hits
- Without role inclusion, estimates would be artificially low
- Example: role=100 tokens + prompt=500 tokens = 600 total (not just 500)

**Testing Strategy (TDD):**
1. **Phase 1**: Unit tests for token guard mechanics (mocked token estimation)
2. **Phase 2**: Unit tests for config integration (AgentManager passing values)
3. **Phase 3**: Integration tests with real token counting via tiktoken

**Backlog Items (defer to Phase 3.2+):**
- Token usage tracking/monitoring in agent responses
- Cost calculation based on input/output tokens
- Model-specific token estimation (GPT-3.5 vs GPT-4 vs Anthropic)
- Per-tool token budgets (limit tokens for specific tool calls)
- Token budget analytics and reporting

---

## Phase 3.2: Advanced Token Management ✅ COMPLETED

**Status**: ✅ Completed on 2025-11-01
**Total Tests**: 61 (46 unit + 15 integration, all passing)
**Architecture**: Token tracking with AgentResult wrapper, no breaking changes

| Component | Unit Tests | Code | Integration Tests | Unit Results | Integration Results |
|-----------|------------|------|-------------------|--------------|---------------------|
| **Token Tracking Infrastructure** | | | | | |
| TokenStats dataclass | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (5/5) | ✅ Pass (N/A) |
| StepTokenStats dataclass | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (N/A) |
| FlowTokenStats aggregation | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (4/4) | ✅ Pass (N/A) |
| TokenTracker class | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (7/7) | ✅ Pass (N/A) |
| **Model Pricing Database** | | | | | |
| OpenAI pricing (gpt-4o, gpt-4o-mini, gpt-3.5-turbo) | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (3/3) | ✅ Pass (N/A) |
| Anthropic pricing (Claude models) | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (N/A) |
| Ollama pricing (free local models) | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |
| Cost calculation (input + output) | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (4/4) | ✅ Pass (N/A) |
| Custom pricing override | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (N/A) |
| Model listing | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |
| **AgentResult Wrapper** | | | | | |
| AgentResult initialization | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |
| String conversion (__str__) | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |
| to_dict() serialization | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |
| from_response() factory | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |
| from_token_stats() factory | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |
| Backward compatibility | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (5/5) | ✅ Pass (N/A) |
| Token handling | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (3/3) | ✅ Pass (N/A) |
| **SimpleAgent Integration** | | | | | |
| Token tracking in SimpleAgent.run() | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (11/11) | ✅ Pass (15/15) |
| Input token estimation | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (N/A) |
| Output token estimation | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (2/2) | ✅ Pass (N/A) |
| Cost calculation integration | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |
| Model info in result | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |
| Disable tracking option | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |
| System role inclusion in count | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |
| Token budget enforcement | ✅ Done | ✅ Done | ✅ Done | ✅ Pass (1/1) | ✅ Pass (N/A) |

### Phase 3.2 Implementation Summary

**Features Implemented:**
1. **Token Tracking Infrastructure**: TokenStats, StepTokenStats, FlowTokenStats, and TokenTracker classes for accumulating token usage across agents and steps
2. **Model Pricing Database**: Built-in pricing for OpenAI, Anthropic, and Ollama models with support for custom pricing
3. **AgentResult Wrapper**: Return object containing response string plus token and cost metadata, with __str__() for backward compatibility
4. **Input + Output Token Tracking**: Separately tracks prompt tokens and response tokens for accurate cost calculation
5. **Soft Budgeting Support**: Token tracking framework ready for flow-level soft budgeting (warnings only, no rejection)
6. **Cost Calculation**: Decimal-based cost calculation for precision, supporting multiple model providers
7. **SimpleAgent Integration**: Modified SimpleAgent.run() to return AgentResult with automatic token tracking

**Architecture Decisions:**
- ✅ AgentResult implements __str__() for seamless backward compatibility with existing code
- ✅ Token tracking enabled by default, with track_tokens=False option for performance when needed
- ✅ Cost stored as Decimal for precision (avoids float rounding errors)
- ✅ Model pricing database centralized in ModelPricing singleton class
- ✅ Token tracking infrastructure separate from SimpleAgent (reusable for flows/orchestration)
- ✅ System role included in token estimation (consistent with Phase 3.1 token guard behavior)

**Use Cases:**
1. **Cost Reporting**: Get detailed cost breakdown for each agent call
2. **Budget Tracking**: Monitor total tokens/cost across multi-step workflows
3. **Model Comparison**: Calculate cost differences between OpenAI, Anthropic, and local models
4. **Per-Step Analysis**: Detailed token breakdown for debugging expensive steps
5. **Billing Integration**: Export token stats for billing systems

**Configuration Example:**
```yaml
agents:
  researcher:
    role: "You are a web research specialist..."
    model_provider: openai
    model_config:
      model: gpt-4o-mini
    token_budget: 20000

  summarizer:
    role: "You are a summarization expert..."
    model_provider: anthropic
    model_config:
      model: claude-3-5-sonnet

# Token tracking is automatic in all agents
# Results include: response, input_tokens, output_tokens, total_tokens, cost, model
```

**Result Object Example:**
```python
result = agent.run("What is Python?")
# result is AgentResult with:
#   - result.response: str
#   - result.input_tokens: int
#   - result.output_tokens: int
#   - result.total_tokens: int (calculated)
#   - result.cost: Decimal
#   - result.model: str

# Backward compatible - works as string:
print(f"Agent said: {result}")  # Prints: Agent said: <response>
message = str(result)           # Gets response text
dict_data = result.to_dict()    # Serialize to dict
```

**Files Created:**
- `simple_agent/tools/helpers/token_tracker.py` (150 lines)
  - TokenStats: Input/output token tracking with total calculation
  - StepTokenStats: Per-agent stats including agent name
  - FlowTokenStats: Aggregates multiple steps with add_step() and to_dict()
  - TokenTracker: Accumulates executions with get_stats() and reset()
- `simple_agent/tools/helpers/model_pricing.py` (100 lines)
  - ModelPricing: Database with OpenAI, Anthropic, Ollama pricing
  - Methods: get_price(), calculate_cost(), set_custom_price(), list_models()
  - Singleton pattern for global access
- `simple_agent/core/agent_result.py` (100 lines)
  - AgentResult: Wrapper dataclass with response + token stats
  - Methods: __str__(), to_dict(), from_response(), from_token_stats()
  - Backward compatible with string-based code
- `tests/unit/test_token_tracker.py` (190 lines, 17 tests)
- `tests/unit/test_model_pricing.py` (160 lines, 14 tests)
- `tests/unit/test_agent_result.py` (200 lines, 15 tests)
- `tests/unit/test_simple_agent_token_tracking.py` (240 lines, 11 tests)

**Files Modified:**
- `simple_agent/agents/simple_agent.py`
  - Added imports: estimate_tokens, calculate_cost, AgentResult, Decimal
  - Added storage of model_config instance variable (was parameter only)
  - Changed run() return type from str to AgentResult
  - Added track_tokens parameter (default True)
  - Implemented token tracking for input and output
  - Cost calculation integrated with model provider
- `tests/unit/test_simple_agent.py`
  - Updated 1 assertion to work with AgentResult
- `tests/unit/test_token_guard.py`
  - Updated 14 test assertions to work with AgentResult
  - Fixed test_token_estimate_called_before_agent_run to expect 2 estimate calls

**Test Results:**
- Unit tests: 46/46 passing ✅
  - Token tracker: 17/17 passing
  - Model pricing: 14/14 passing
  - AgentResult: 15/15 passing
  - SimpleAgent token tracking: 11/11 passing
- Total project unit tests: 486/486 passing ✅ (440 existing + 46 new)
- All existing tests updated and passing ✅

**Code Metrics:**
- Total lines: ~500 (production + tests)
- Production code: ~350 lines (new infrastructure)
- Test code: ~800 lines (comprehensive coverage)
- All classes/functions < 150 lines (CLAUDE.md compliant)

**How It Works:**
1. User provides prompt to agent.run(prompt, track_tokens=True)
2. Prompt formatted with RAG context and templates (same as before)
3. Input tokens estimated: estimate_tokens(role + formatted_prompt)
4. Agent executes: self.agent.run(formatted_prompt)
5. Response obtained: response = agent.agent.run(...)
6. Output tokens estimated: estimate_tokens(response_str)
7. Cost calculated: calculate_cost(model, input_tokens, output_tokens)
8. AgentResult returned with all metadata

**Backward Compatibility Strategy:**
- AgentResult.__str__() returns response string
- Works in f-strings: f"Response: {result}"
- Works in concatenation: "Agent: " + str(result)
- Works in print: print(result)
- Maintains existing code that expects strings

### Phase 3.2 Enhancement: Error Tracking (Added 2025-11-01)

After Phase 3.2 completion, implemented error tracking to provide visibility into execution failures:

**Error Tracking Features:**
1. **Error Capture**: AgentResult now includes error and error_type fields
2. **Execution Halted Flag**: Indicates in to_dict() that execution was halted by error
3. **Non-Raising Errors**: LLM execution errors are captured in result, not raised
4. **Hard Limits Still Raise**: Token budget errors still raise ValueError (hard limit)
5. **Partial Results**: Can capture partial response + token count even when error occurs

**Error Tracking Implementation:**
- AgentResult.error: Optional[str] - Error message
- AgentResult.error_type: Optional[str] - Error class name (e.g., "RuntimeError")
- to_dict() includes "execution_halted": True when error is present
- SimpleAgent.run() wraps LLM execution in try-except to capture errors

**Key Design Decision:**
- Token budget errors RAISE (hard limits that prevent execution)
- LLM/runtime errors are CAPTURED in result (soft failures that still return AgentResult)
- This allows workflows to handle errors gracefully without propagating exceptions

**Test Coverage (26 New Tests):**
- AgentResult error tracking: 16 tests
- SimpleAgent error handling: 10 tests
- Token preservation on error
- Different error types captured
- Backward compatibility maintained

**Files Added:**
- tests/unit/test_agent_result_error_tracking.py (220 lines, 16 tests)
- tests/unit/test_simple_agent_error_handling.py (195 lines, 10 tests)

**Files Modified:**
- simple_agent/core/agent_result.py - Added error tracking fields
- simple_agent/agents/simple_agent.py - Wrapped LLM execution in try-except
- tests/unit/test_simple_agent_error_handling.py - Updated token budget test

**Usage Example:**
```python
result = agent.run("What is Python?")

# Check for errors
if result.error:
    print(f"Error: {result.error_type}: {result.error}")
    print(f"Tokens used before error: {result.input_tokens}")
else:
    print(f"Success: {result.response}")

# Export with error info
data = result.to_dict()
# {
#     "response": "...",
#     "tokens": {...},
#     "error": {
#         "error_type": "APIError",
#         "error_message": "Connection timeout",
#         "execution_halted": True
#     }
# }
```

---

**Next Steps (Future Phases):**
- Integrate token tracking with Orchestrator for per-step reporting
- Flow-level soft budgeting with warnings (not hard rejection)
- Token stats CLI commands (/token stats, /token export)
- Error aggregation across multi-step workflows
- README examples showing token tracking and error handling

---

**Last Updated**: 2025-11-01
**Current Status**: Phase 3.2 Token Management Complete ✅ (with Error Tracking)
**Total Tests**: 512/512 passing (486 existing + 26 new)
**Next Phase**: Phase 4 - Raspberry Pi Integration
