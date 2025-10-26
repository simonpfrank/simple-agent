# Phase 1.6: Simplify Prompts & Add User Prompt Templates

**Status**: 📋 Planned
**Priority**: High
**Complexity**: Medium
**Estimated Effort**: 3-4 hours

---

## Overview

Simplify the agent prompt architecture by removing the over-engineered template feature and replacing it with a more powerful user prompt template system.

## Problem Statement

Current system has unnecessary complexity:
- Separate prompt template files in `simple_agent/config/prompts/`
- Template feature (`template: "researcher"`) requires extra indirection
- YAML already handles multi-line prompts beautifully with `|` syntax
- **Reality**: No one is actually using templates - all agents use direct `role:` field

**Evidence:**
- `researcher.yaml`: Uses `role: |` (NOT template)
- `maths.yaml`: Uses `role:` (NOT template)
- Template files exist but serve no practical purpose

## Goals

1. **Simplify**: Remove unused template feature and directory
2. **Enhance**: Add user prompt template feature for consistent prompt engineering
3. **Self-contained**: Keep all agent config in single YAML file

## Proposed Solution

### Part 1: Remove Template Feature (Breaking Change)

**Delete:**
- `simple_agent/config/prompts/` directory and all template files
- `template` parameter from `create_agent()` in AgentManager
- `template` parameter from `SimpleAgent.__init__()`
- `ConfigManager.load_prompt_template()` method
- All template-related tests

**Update:**
- Migration guide for any existing agents using templates (if any)

### Part 2: Add User Prompt Template Feature

**Add `user_prompt_template` field to agent YAML:**

```yaml
name: "agent_name"
role: |
  System prompt - defines what the agent IS

user_prompt_template: |
  {user_input}

  Additional instructions or formatting

tools:
  - tool1
```

**How it works:**
1. User types: `"What is quantum computing?"`
2. If `user_prompt_template` exists, format it: `template.format(user_input=prompt)`
3. Send formatted prompt to LLM
4. If no template, send user input directly (backward compatible)

## Use Cases

### 1. Chain-of-Thought Reasoning
```yaml
name: "thinker"
role: You are a logical reasoning assistant.
user_prompt_template: |
  {user_input}

  Let's think through this step by step:
  1. First, let me understand the question
  2. Then, I'll break down the problem
  3. Finally, I'll provide a clear answer
```

### 2. Concise Responses
```yaml
name: "brief"
role: You are a concise assistant who answers briefly.
user_prompt_template: |
  {user_input}

  (Answer in 2-3 sentences maximum)
```

### 3. Code Review Template
```yaml
name: "code_reviewer"
role: You are a senior software engineer doing code reviews.
user_prompt_template: |
  Please review this code:

  {user_input}

  Focus on:
  - Security issues
  - Performance problems
  - Best practices
  - Code style
```

### 4. Research Assistant
```yaml
name: "researcher"
role: You are a research specialist.
user_prompt_template: |
  {user_input}

  Please provide:
  1. A clear answer
  2. Your sources
  3. Any caveats or limitations
```

## Implementation Plan

### Step 1: Remove Template Feature (TDD)

**Tests to remove:**
- `test_config_manager.py::test_load_prompt_template_*` (4 tests)
- `test_simple_agent.py::test_init_with_template` (1 test)
- `test_simple_agent.py::test_init_role_overrides_template` (1 test)
- `test_agent_manager.py::test_create_agent_with_template` (1 test)

**Code to remove:**
1. Delete `simple_agent/config/prompts/` directory
2. Remove from `ConfigManager`:
   - `load_prompt_template()` method
   - Related path handling in `get_defaults()`
3. Remove from `SimpleAgent`:
   - `template` parameter from `__init__()`
   - Template loading logic in constructor
4. Remove from `AgentManager`:
   - `template` parameter from `create_agent()`
   - Template loading call
5. Remove from commands:
   - `--template` option from `/agent create`
   - Template step from `/agent create-wizard`

**Run tests to verify removal:**
```bash
pytest tests/unit/test_config_manager.py -v
pytest tests/unit/test_simple_agent.py -v
pytest tests/unit/test_agent_manager.py -v
```

### Step 2: Add User Prompt Template (TDD)

**New tests to write:**

`tests/unit/test_simple_agent.py`:
- `test_user_prompt_template_formats_input` - Template applies to user input
- `test_user_prompt_template_none_uses_direct_input` - No template = direct pass-through
- `test_user_prompt_template_with_placeholder` - {user_input} replacement works
- `test_user_prompt_template_multiline` - Multi-line templates work

`tests/unit/test_agent_manager.py`:
- `test_create_agent_with_user_prompt_template` - AgentManager passes template through

`tests/unit/test_agent_yaml.py`:
- `test_load_agent_with_user_prompt_template` - YAML loading includes template
- `test_save_agent_with_user_prompt_template` - YAML saving includes template

`tests/integration/test_phase_1_6.py`:
- `test_user_prompt_template_end_to_end` - Full workflow with template
- `test_template_with_chat_mode` - Template persists across chat turns

**Implementation steps:**

1. **Update SimpleAgent** (`simple_agent/agents/simple_agent.py`):
   ```python
   def __init__(
       self,
       name: str,
       model_provider: str,
       model_config: dict,
       role: str = None,
       user_prompt_template: str = None,  # NEW
       tools: List[Any] = None,
       verbosity: int = 1,
       max_steps: int = 10,
       agent_type: str = "tool_calling",
       executor_type: str = "docker",
       debug_enabled: bool = False,
   ):
       self.name = name
       self.user_prompt_template = user_prompt_template  # NEW
       # ... rest of init

   def run(self, prompt: str, reset: bool = True) -> str:
       # NEW: Format prompt if template exists
       if self.user_prompt_template:
           formatted_prompt = self.user_prompt_template.format(user_input=prompt)
       else:
           formatted_prompt = prompt

       # Run with formatted prompt
       result = self.agent.run(formatted_prompt, reset=reset)
       return str(result)
   ```

2. **Update AgentManager** (`simple_agent/core/agent_manager.py`):
   ```python
   def create_agent(
       self,
       name: str,
       provider: Optional[str] = None,
       role: Optional[str] = None,
       user_prompt_template: Optional[str] = None,  # NEW
       tools: Optional[List[str]] = None,
   ) -> SimpleAgent:
       # ...
       agent = SimpleAgent(
           name=name,
           model_provider=provider,
           model_config=model_config,
           role=role,
           user_prompt_template=user_prompt_template,  # NEW
           tools=tool_objects if tool_objects else None,
           # ...
       )
   ```

3. **Update YAML loading** (`simple_agent/core/agent_manager.py`):
   ```python
   def load_agent_from_yaml(self, yaml_path: str) -> SimpleAgent:
       # ...
       role = agent_data.get('role')
       user_prompt_template = agent_data.get('user_prompt_template')  # NEW

       agent = self.create_agent(
           name=name,
           provider=provider,
           role=role,
           user_prompt_template=user_prompt_template,  # NEW
           tools=tools if tools else None,
       )
   ```

4. **Update YAML saving** (`simple_agent/core/agent_manager.py`):
   ```python
   def save_agent_to_yaml(self, agent_name: str, yaml_path: str) -> None:
       agent = self.get_agent(agent_name)

       agent_data = {
           'name': agent.name,
           'agent_type': agent.agent_type,
           'role': agent.role,
       }

       # NEW: Add user_prompt_template if present
       if agent.user_prompt_template:
           agent_data['user_prompt_template'] = agent.user_prompt_template

       # ... rest of save
   ```

5. **Update wizard** (`simple_agent/commands/agent_commands.py`):
   - Add optional step: "Add user prompt template? [y/N]"
   - If yes, prompt for template text (multi-line input)
   - Pass to `create_agent()`

### Step 3: Update Documentation

1. Update `config/agents/researcher.yaml` example to show user_prompt_template
2. Update `docs/Progress_Tracker.md` when complete
3. Create migration guide if needed

### Step 4: Integration Testing

Create `tests/integration/test_phase_1_6.py`:
- Test full lifecycle: create agent with template → save to YAML → load from YAML → run
- Test chat mode with template persists across turns
- Test template with tools
- Test backward compatibility (agents without template still work)

## Breaking Changes

**Migration Required:**
- Any agents using `template: "researcher"` parameter must change to `role: "..."`
- Template files in `simple_agent/config/prompts/` will be deleted
- `/agent create --template` option will be removed

**Migration Guide:**

**Before (old template approach):**
```yaml
name: "my_agent"
template: "researcher"
```

**After (direct role):**
```yaml
name: "my_agent"
role: |
  You are a research specialist. You help users find accurate
  information, analyze data, and provide well-sourced answers.
```

**Impact:** Low - evidence shows no agents are currently using templates

## Benefits

- ✅ **Simpler architecture** - One less concept to understand
- ✅ **Self-contained agents** - All config in one YAML file
- ✅ **More powerful** - User prompt templates enable consistent prompt engineering
- ✅ **Easier maintenance** - Less code, fewer directories
- ✅ **Better UX** - Users can create prompt patterns per agent
- ✅ **Backward compatible** - user_prompt_template is optional

## Success Criteria

- [ ] All template-related code removed
- [ ] `simple_agent/config/prompts/` deleted
- [ ] `user_prompt_template` field works in YAML
- [ ] Template formatting works in SimpleAgent.run()
- [ ] All existing tests pass (after template test removal)
- [ ] New tests for user_prompt_template pass (8+ tests)
- [ ] Integration tests verify end-to-end workflow
- [ ] Documentation updated
- [ ] Migration guide created

## Files to Modify

**Delete:**
- `simple_agent/config/prompts/` (entire directory)

**Modify:**
- `simple_agent/core/config_manager.py` - Remove load_prompt_template()
- `simple_agent/core/agent_manager.py` - Remove template param, add user_prompt_template
- `simple_agent/agents/simple_agent.py` - Remove template, add user_prompt_template + formatting
- `simple_agent/commands/agent_commands.py` - Update create/wizard commands
- `tests/unit/test_config_manager.py` - Remove template tests
- `tests/unit/test_simple_agent.py` - Remove template tests, add user_prompt_template tests
- `tests/unit/test_agent_manager.py` - Remove template test, add user_prompt_template test
- `tests/unit/test_agent_yaml.py` - Add user_prompt_template tests
- `config/agents/researcher.yaml` - Add example user_prompt_template
- `docs/Progress_Tracker.md` - Add Phase 1.6 completion

**Create:**
- `tests/integration/test_phase_1_6.py` - Integration tests

## Estimated Test Count

- Remove: 7 tests (template-related)
- Add: 8+ tests (user_prompt_template)
- Net: +1 test (192 total)

## Timeline

1. **Remove template feature** - 1 hour
2. **Add user_prompt_template** - 2 hours
3. **Testing & validation** - 0.5 hour
4. **Documentation** - 0.5 hour

**Total**: 3-4 hours

---

## Notes

- This is a **simplification** and **enhancement** in one phase
- Breaking change is low-impact (no evidence of template usage)
- User prompt templates unlock powerful prompt engineering patterns
- Follows TDD methodology throughout
