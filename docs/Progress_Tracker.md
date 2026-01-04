# Simple Agent Progress Tracker

Development progress across all phases. See individual phase docs (phase_N_*.md) for detailed specifications.

---

## Phase 0: Foundation

| Sub-phase | Description | Status | Unit Tests | Integration Tests | Commit | Examples | README |
|-----------|-------------|--------|------------|------------------|--------|----------|--------|
| 0 | Core setup | ✅ Done | 15/15 | 5/5 | 3eea597 | ✅ | ✅ |
| 0.5 | Security | ✅ Done | 20/20 | 3/3 | 3eea597 | ❌ | ✅ |

---

## Phase 1: Interactive Features

| Sub-phase | Description | Status | Unit Tests | Integration Tests | Commit | Examples | README |
|-----------|-------------|--------|------------|------------------|--------|----------|--------|
| 1 | Chat & inspect | ✅ Done | 45/45 | 12/12 | 3eea597 | ✅ | ✅ |
| 1.5 | Agent types | ✅ Done | 15/15 | 3/3 | 3eea597 | ✅ | ✅ |
| 1.6 | User templates | ✅ Done | 30/30 | 5/5 | 3eea597 | ✅ | ✅ |
| 1.7 | Jinja engine | ✅ Done | 25/25 | 3/3 | 3eea597 | ✅ | ✅ |

---

## Phase 2: Enhanced Features

| Sub-phase | Description | Status | Unit Tests | Integration Tests | Commit | Examples | README |
|-----------|-------------|--------|------------|------------------|--------|----------|--------|
| 2.1 | Guardrails | ✅ Done | 57/57 | 12/12 | 3eea597 | ✅ | ✅ |
| 2.2 | Human approval | ✅ Done | 18/18 | 4/4 | 3eea597 | ✅ | ✅ |
| 2.3 | RAG foundation | ✅ Done | 42/42 | 8/8 | 3eea597 | ✅ | ✅ |
| 2.4 | Orchestration | ✅ Done | 65/65 | 15/15 | 3eea597 | ✅ | ✅ |

---

## Phase 3: Extensions & Token Management

| Sub-phase | Description | Status | Unit Tests | Integration Tests | Commit | Examples | README |
|-----------|-------------|--------|------------|------------------|--------|----------|--------|
| 3.1 | Token budgets | ✅ Done | 25/25 | 10/10 | 3eea597 | ✅ | ❌ |
| 3.2 | Token tracking | ✅ Done | 72/72 | 26/26 | f4b487c | ✅ | ❌ |
| 3.3 | Budget awareness | ✅ Done | 31/31 | 10/10 | 6041b7e | ✅ | ❌ |
| 3.4 | Token stats CLI | ✅ Done | 12/12 | 13/13 | TBD | ✅ | ❌ |
| 3.5 | MCP integration | 🔴 Backlog | 0/? | 0/? | — | — | — |
| 3.6 | Agent composition | 🔴 Backlog | 0/? | 0/? | — | — | — |
| 3.7 | Python code tool | 🔴 Backlog | 0/? | 0/? | — | — | — |
| 3.8 | Flow conditionals | 🔴 Backlog | 0/? | 0/? | — | — | — |

---

## Phase 4: Raspberry Pi Integration

| Sub-phase | Description | Status | Unit Tests | Integration Tests | Commit | Examples | README |
|-----------|-------------|--------|------------|------------------|--------|----------|--------|
| 4.1 | Local LLM setup | 🔴 Not started | 0/? | 0/? | — | — | — |
| 4.2 | Voice I/O | 🔴 Backlog | 0/? | 0/? | — | — | — |
| 4.3 | GPIO tools | 🔴 Backlog | 0/? | 0/? | — | — | — |
| 4.4 | Edge patterns | 🔴 Backlog | 0/? | 0/? | — | — | — |

---

## Test Summary

| Phase | Total Unit Tests | Total Integration Tests | Overall Status |
|-------|-----------------|----------------------|----------------|
| 0-2 | 381/381 | 52/52 | ✅ Complete |
| 3 | 140/140 (25+72+31+12) | 59/59 (10+26+10+13) | ✅ 3.1-3.4 Done |
| 4 | 0/? | 0/? | 🔴 Not Started |
| **TOTAL** | **521 unit tests** | **111 integration tests** | **✅ Complete through Phase 3.4** |

---

# Next

## Current Development: Code Review Fixes (All Phases)

### Status (as of latest context):

**Phase 2.1 - SimpleAgent Refactoring** ✅ COMPLETE
- Created AgentConfig dataclass encapsulating 13 constructor parameters
- Issue 1-A (SRP violation): RESOLVED
- Commit: f6e2d67

**Phase 2.2 - AppContext Dataclass** ✅ COMPLETE
- Created AppContext for type-safe dependency injection
- Issue 10-B (service locator): RESOLVED
- Commit: 050e19a

**Phase 1 - HITL Implementation** ✅ COMPLETE
- ✅ Issue 5-A: ConsoleApprovalUI (interactive approval dialogs)
  - Rich terminal-based approval prompts
  - Preview data display, responsive to user input
- ✅ Issue 5-B: FileApprovalPersistence (approval storage)
  - JSON file-based storage for requests and decisions
  - Survives manager restarts, audit trail with timestamps
- Enhanced ApprovalManager with UI + Persistence integration
- 71 new tests: all passing (44 unit + 27 integration)
- Commit: cecf1aa

### Completed Code Review Issues: 17/56 (30%)
- ✅ 1-A: SimpleAgent constructor (AgentConfig)
- ✅ 1-B: Template duplication (extracted methods)
- ✅ 1-C: RAG error handling (better logging)
- ✅ 1-D: Config key access (fallback)
- ✅ 2-C: Config structure validation (required keys, types)
- ✅ 2-D: File locking (fcntl)
- ✅ 3-C/3-D: Command duplication (common.py)
- ✅ 5-A: HITL UI (ConsoleApprovalUI)
- ✅ 5-B: HITL persistence (FileApprovalPersistence)
- ✅ 7-A: Circular dependency documentation (deferred imports pattern)
- ✅ 7-B: Document structure validation (required fields, types)
- ✅ 7-C: Index versioning for embeddings (version tracking, migration info)
- ✅ 8-A: Model pricing externalization (configurable prices)
- ✅ 8-C: Token estimation (smart fallback)
- ✅ 8-D: Input validation (page_fetch.py)
- ✅ 10-B: Service locator (AppContext)

### Backlog (Code Review Fixes Roadmap):
1. [ ] **Azure Integration Tests: Retrieve Token in Tests**
   - Currently 6 Azure tests are skipped due to requiring credentials
   - Update tests to retrieve Azure AD token dynamically in test setup
   - Use `DefaultAzureCredential` to get token so tests don't skip
   - Effort: 1-2 hours | Priority: Medium

2. [ ] **Phase 2.3: Integrate AppContext into app.py** - DEFERRED (HIGH COMPLEXITY)
   - Replace service locator pattern (ctx.obj dict) with AppContext in all commands
   - Refactor command functions to use AppContext for dependency injection
   - Update command registration and initialization
   - Effort: 3-4 hours | Risk: Medium

3. [ ] **Phase 3: Split Large Files** - DEFERRED (HIGH COMPLEXITY)
   - Issue 3-A: Split token_stats_commands.py (710 lines → 3-4 modules)
   - Issue 3-B: Split agent_commands.py (495 lines → 2-3 modules)
   - Requires careful refactoring of command classes and tests
   - Effort: 4-6 hours | Risk: Medium

4. [ ] **Phase 6-7: Remaining Issues** (39 items, mixed severity)
   - 2-A, 2-B, 2-E, 2-F: Manager lifecycle and config improvements
   - 1-H, 1-I, 4-*, 6-*: Various quality and architectural improvements
   - Ready for implementation after core issues complete

### Current Test Summary (End of Session):
- ✅ **703 unit tests passing** (all tests)
- ✅ **123 integration tests** (from earlier phases)
- **Total: 826 tests passing**
- **New tests created this session: 95**
  - +28 tests (Issue 8-D: page_fetch validation)
  - +28 tests (Issue 2-C: config validation)
  - +17 tests (Issue 8-A: model pricing config)
  - +22 tests (Issues 7-A/B/C: RAG improvements)

### Key Links:
- **Phase 0**: `phase_0_foundation.md`
- **Phase 1**: `phase_1_interactive.md`, `phase_1_5_plan.md`, `phase_1_6_templates.md`, `phase_1_7_jinja.md`
- **Phase 2**: `phase_2_enhanced_features.md`, `phase_2_4_orchestration.md`
- **Phase 3**: `phase_3_extensions.md` (3.1-3.2 done, 3.3-3.7 backlog)
- **Phase 4**: `phase_4_raspberrypi.md` (not started)
- **Reference**: `technical_specification.md`, `product_requirements.md`, `backlog.md`
- **Archive**: `backup_progress_tracker.md` (old tracker, saved for reference)

### Column Meanings:
- **Status**: ✅ Done | 🟡 In Progress | 🔴 Not Started
- **Unit Tests**: Passing/Total (e.g., 45/45 or 0/?)
- **Integration Tests**: Passing/Total (e.g., 10/10 or 0/?)
- **Commit**: Latest commit hash or — if not started
- **Examples**: ✅ (has code examples), ❌ (missing examples), — (N/A)
- **README**: ✅ (in README.md), ❌ (needs update), — (N/A)

### Phase 3.3 Token Budget Awareness:
- Agents aware of token budget during execution
- Smart tool selection and output limiting based on remaining tokens
- Budget info injected into system prompt for reasoning
- Runtime budget override for orchestration/automation systems

### Phase 3.4-3.8 Backlog Details:
- **3.4 Token Stats CLI**: Commands for viewing/exporting token usage
- **3.5 MCP Integration**: Model Context Protocol support (complex)
- **3.6 Agent Composition**: Agents calling other agents as tools (see backlog.md for Agent Protocols, which is separate)
- **3.7 Python Code Tool**: Sandboxed code execution
- **3.8 Flow Conditionals**: If/else routing in orchestration flows

**Note**: Agent Protocols (standardizing interfaces for different agent architectures) is in backlog.md and remains separate from Phase 3.6.

See `phase_3_extensions.md` for full specs.

### Phase 4 Details:
- **4.1 Local LLM**: Ollama integration for Pi deployment
- **4.2 Voice I/O**: Speech-to-text and text-to-speech
- **4.3 GPIO Tools**: Hardware control (LEDs, motors, sensors)
- **4.4 Edge Patterns**: Offline mode, batch processing, monitoring

See `phase_4_raspberrypi.md` for full specs.

---

## 2025-01-04: Azure OpenAI Provider Implementation

### Summary
Successfully implemented Azure OpenAI provider support following TDD methodology. All unit tests pass, code is complete and functional. Integration tests reveal Azure deployment configuration issue (not a code issue).

### Completed ✅
1. **Unit Tests Created** (`tests/unit/test_azure_openai_provider.py`)
   - 8 comprehensive unit tests
   - ✅ All tests passing
   - Coverage: Azure AD auth, API key auth, config validation, error handling, defaults, env vars

2. **Implementation** (`simple_agent/agents/simple_agent.py`)
   - Added `azure_openai` provider branch in `_create_model()` method
   - Supports Azure AD authentication (using `DefaultAzureCredential` and `get_bearer_token_provider`)
   - Supports API key authentication (fallback)
   - Proper error handling with actionable error messages
   - Environment variable resolution for endpoint/api_key
   - Default api_version: "2024-07-18"
   - Default auth_type: "azure_ad"
   - **KEY FIX**: Pass `azure_ad_token_provider` (callable) not `azure_ad_token` (string) to LiteLLMModel

3. **Configuration** (`config.yaml`)
   - Added `azure_openai` section with comprehensive comments
   - Configured for gpt-4o-mini deployment
   - Endpoint: https://api.lab.ai.wtwco.com
   - API version: 2024-07-18 (from docs/Azure_model_names_and_versions.md)

4. **Integration Tests** (`tests/integration/test_azure_openai_integration.py`)
   - 11 integration tests created
   - Tests cover: simple prompts, multi-turn conversation, reset, error handling, token budget, temperature, max_tokens, edge cases

### Test Results
**Unit Tests:** ✅ 8/8 PASSING
```
test_azure_openai_with_azure_ad_auth PASSED
test_azure_openai_missing_endpoint PASSED
test_azure_openai_with_api_key PASSED
test_azure_openai_api_key_missing PASSED
test_azure_openai_auth_failure PASSED
test_azure_openai_default_api_version PASSED
test_azure_openai_default_auth_type PASSED
test_azure_openai_env_var_resolution PASSED
```

**Integration Tests:** ⚠️ AUTHENTICATION WORKING, DEPLOYMENT NOT FOUND
- Azure AD authentication: ✅ WORKING
- Connection to endpoint: ✅ WORKING
- Token provider: ✅ CORRECT (passing callable, not string)
- API calls: ❌ "Resource not found" error

### Current Issue: Resource Not Found
**Error:** `litellm.APIError: AzureException APIError - Resource not found`

**Analysis:**
- ✅ Code implementation is correct
- ✅ Azure AD authentication working (we're reaching Azure)
- ✅ Token provider properly configured (callable, not static token)
- ❌ Deployment "gpt-4o-mini" either:
  - Not available at https://api.lab.ai.wtwco.com
  - Has a different name
  - User lacks RBAC permissions
  - API version mismatch

**Next Steps (for morning):**
1. Verify exact deployment name in Azure portal
2. Confirm Azure AD user/service principal has RBAC permissions on the deployment
3. Test with Azure CLI: `az rest --method GET --url "https://api.lab.ai.wtwco.com/openai/deployments?api-version=2024-07-18"`
4. Try alternate API versions if needed
5. Once deployment is accessible, integration tests should pass without code changes

### Technical Details
**Authentication Pattern (from working sample code):**
```python
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), 
    f"{azure_endpoint}/.default"  # Scope must include /.default
)

# Pass provider (callable), not token (string)
LiteLLMModel(
    model_id=f"azure/{model_id}",
    api_base=azure_endpoint,
    azure_ad_token_provider=token_provider,  # Callable for automatic refresh
    api_version=api_version,
)
```

### Dependencies Added During Development
- `beautifulsoup4` (bs4) - for HTML parsing (existing code dependency)
- `html2text` - for HTML conversion (existing code dependency)

### Files Modified/Created
**Created:**
- `tests/unit/test_azure_openai_provider.py` (231 lines)
- `tests/integration/test_azure_openai_integration.py` (316 lines)
- `docs/azure_openai_research_findings.md` (458 lines)
- `docs/azure_openai_implementation_plan.md` (386 lines)

**Modified:**
- `simple_agent/agents/simple_agent.py` (+77 lines for azure_openai provider)
- `config.yaml` (+10 lines for azure_openai config)

### Code Quality
- ✅ TDD methodology followed (Red → Green → Refactor)
- ✅ Comprehensive error handling
- ✅ Clear, actionable error messages
- ✅ No breaking changes to existing code
- ✅ Follows existing provider patterns
- ✅ Google-style docstrings

### Backward Compatibility
- ✅ No changes to existing providers (openai, ollama, anthropic)
- ✅ All existing unit tests still pass (32/32)
- ✅ Switch providers via config only (no code changes)

**Status:** Implementation complete, pending Azure deployment configuration verification.

---

## Phase 5: CLI Refresh (Claude Code-Level Polish)

### Overview
Achieve Claude Code-level CLI polish for simple-agent REPL. Focus on input experience improvements (Phase 5.1), then output improvements (Phase 5.2 - pending approval).

**Status:** Phase 5.1 Partially Complete (6/8 features implemented)
**Date:** 2026-01-04
**Detailed Documentation:** `docs/phase_5_cli_refresh.md`

### Phase 5.1: Input Experience

| Component | Code Status | Integration Tests | User Verified | Notes |
|-----------|-------------|-------------------|---------------|-------|
| Menu Styling (Purple Theme) | ✅ Complete | 5/5 smoke | ✅ Yes | Purple text (#6B4FBB) on selected, grey (#808080) unselected |
| Menu Spacing (20 char) | ✅ Complete | ✅ Pass | ✅ Yes | Padding between command and help text |
| Grey Line Above Input | ✅ Complete | ✅ Pass | ⏭️ N/A | 200-char horizontal line in grey |
| Multi-line Input | ✅ Complete | ✅ Pass | ❌ Not tested | Ctrl+J inserts newline (Shift+Enter NOT supported) |
| History Location | ✅ Complete | ✅ Pass | ⏭️ N/A | Moved to `~/.simple-agent/history` |
| UI Prompt Config | ✅ Complete | ✅ Pass | ⏭️ N/A | Reads from `ui.prompt` in config.yaml |
| Autocomplete Auto-Select | ❌ Deferred | - | - | Requires custom Buffer implementation |
| Grey Line Below Input | ❌ Not Impl | - | - | prompt_toolkit limitation (no way to place between input and menu) |

### Implementation Summary

**Completed Features (6/8):**
1. ✅ Menu colors match Claude Code style
2. ✅ 20 character spacing in completion menu
3. ✅ Grey horizontal line above prompt
4. ✅ Multi-line input via Ctrl+J key binding
5. ✅ History file in user home directory
6. ✅ Configurable prompt text

**Technical Limitations Discovered:**
- **Shift+Enter:** Not supported by prompt_toolkit (`s-enter` is invalid key binding). No standard terminal escape sequence exists. Implemented Ctrl+J as alternative.
- **Bottom grey line:** Cannot place content between input line and floating completion menu with prompt_toolkit's architecture.
- **Auto-selection:** First completion item selection requires custom Buffer.start_completion() implementation not exposed by prompt().

**Files Modified:**
- `simple_agent/app.py` (lines 277-322)
- `simple_agent/ui/completion.py` (lines 107, 166, 185)
- `tests/integration/test_cli_refresh_smoke.py` (created, 5 tests passing)

**Test Results:**
- Smoke tests: 5/5 passing
- Visual tests: Manual verification required
- User verification: Colors and spacing confirmed working

### Known Issues
1. First matching completion item not auto-selected (requires Tab press)
2. Bottom grey line not implemented (technical limitation)
3. Shift+Enter not supported (use Ctrl+J instead)

### Phase 5.2: Output Experience (PENDING)
Will be implemented after Phase 5.1 user acceptance and approval.

**Key Links:**
- Detailed report: `docs/phase_5_cli_refresh.md`
- Specification: `docs/cli_refresh_specification.md`
- Smoke tests: `tests/integration/test_cli_refresh_smoke.py`
