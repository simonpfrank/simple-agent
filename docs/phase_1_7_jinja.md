# Phase 1.7: Jinja2 Template Support in YAML

**Status:** 🟡 In Progress
**Priority:** Medium
**Estimated Effort:** 4-5 hours

---

## Overview

Add Jinja2 template engine support for `role` and `user_prompt_template` fields in agent YAML files, enabling dynamic prompts with variables, conditionals, and loops.

**Goal:** Enhance prompt engineering capabilities while maintaining backward compatibility with simple format strings.

---

## Problem Statement

Currently, YAML prompts support simple Python format strings:
```yaml
user_prompt_template: "{user_input}\n\nPlease answer concisely."
```

This is limited - we want dynamic behavior like:
- Conditional sections based on settings
- Current date/time injection
- Agent metadata in prompts
- Loops over tools/data
- String filters

---

## Solution: Jinja2 Template Engine

### Features to Support

1. **Variables:** `{{ variable_name }}`
2. **Conditionals:** `{% if condition %} ... {% endif %}`
3. **Loops:** `{% for item in list %} ... {% endfor %}`
4. **Filters:** `{{ text | upper }}`
5. **Comments:** `{# This is a comment #}`

### Context Variables Provided

**Always Available:**
- `agent_name` - Agent's name (string)
- `current_time` - Current timestamp (datetime object)
- `current_date` - Current date only (date object)

**For user_prompt_template only:**
- `user_input` - The user's input text (string)

**From Agent Config (if set):**
- `verbosity` - Agent verbosity level (int: 0, 1, 2)
- `max_steps` - Max tool calling steps (int)
- `tools` - List of tool names (list[str])
- `model_provider` - LLM provider name (string)

**Custom Variables (future):**
- Support for user-defined variables in YAML `variables:` section

---

## Implementation Plan

### 1. Backward Compatibility Strategy

**Auto-detect template type:**
```python
def render_template(template: str, context: dict) -> str:
    """Render template with Jinja2 or simple format string."""
    if '{{' in template or '{%' in template or '{#' in template:
        # Jinja2 template detected
        return render_jinja2(template, context)
    else:
        # Simple format string
        return template.format(**context)
```

This allows:
- Old format: `{user_input}` → Python `.format()`
- New format: `{{ user_input }}` → Jinja2

### 2. Files to Modify

**simple_agent/agents/simple_agent.py**
- Add `_render_template()` method
- Update `__init__()` to render `role` with Jinja2
- Update `run()` to render `user_prompt_template` with Jinja2
- Build context dict with available variables

**simple_agent/core/agent_manager.py**
- No changes needed (rendering happens in SimpleAgent)

**requirements.txt**
- Add `jinja2>=3.1.0`

### 3. Context Building

```python
def _build_context(self, user_input: str = None) -> dict:
    """Build Jinja2 context with all available variables."""
    from datetime import datetime

    context = {
        "agent_name": self.name,
        "current_time": datetime.now(),
        "current_date": datetime.now().date(),
        "verbosity": self.verbosity,
        "max_steps": self.max_steps,
        "tools": [t.name for t in self.tools] if self.tools else [],
        "model_provider": self.model_provider,
    }

    # Add user_input if provided (for user_prompt_template)
    if user_input is not None:
        context["user_input"] = user_input

    return context
```

### 4. Jinja2 Configuration

```python
from jinja2 import Environment, BaseLoader, TemplateError

# Create Jinja2 environment (no file loading needed)
jinja_env = Environment(
    loader=BaseLoader(),
    autoescape=False,  # We're not rendering HTML
    trim_blocks=True,
    lstrip_blocks=True
)

def render_jinja2(template_str: str, context: dict) -> str:
    """Render Jinja2 template string."""
    try:
        template = jinja_env.from_string(template_str)
        return template.render(**context)
    except TemplateError as e:
        raise ValueError(f"Jinja2 template error: {e}")
```

---

## Example Use Cases

### 1. Chain-of-Thought with Date

```yaml
name: "cot_agent"
role: |
  You are {{ agent_name }}, a reasoning assistant.
  Today's date: {{ current_date.strftime('%Y-%m-%d') }}

user_prompt_template: |
  {{ user_input }}

  {% if verbosity >= 2 %}
  Let's think through this step by step:
  1. First, understand the question
  2. Then, break down the problem
  3. Finally, provide a clear answer
  {% else %}
  Please provide a clear, direct answer.
  {% endif %}
```

### 2. Conditional Tool Instructions

```yaml
name: "researcher"
role: |
  You are a research assistant named {{ agent_name }}.

  {% if tools %}
  You have access to these tools:
  {% for tool in tools %}
  - {{ tool }}
  {% endfor %}

  Use them when needed to gather accurate information.
  {% else %}
  Answer questions based on your training data.
  {% endif %}
```

### 3. Verbosity-Based Prompts

```yaml
name: "assistant"
role: |
  You are {{ agent_name }}.

  {% if verbosity == 0 %}
  Be extremely concise. One sentence answers only.
  {% elif verbosity == 1 %}
  Provide clear, concise answers.
  {% else %}
  Provide detailed, thorough explanations with examples.
  {% endif %}
```

### 4. Code Review with Filters

```yaml
name: "code_reviewer"
user_prompt_template: |
  CODE REVIEW REQUEST ({{ current_time.strftime('%H:%M:%S') }})
  Agent: {{ agent_name | upper }}

  {{ user_input }}

  Please review for:
  - Security issues
  - Performance concerns
  - Code style
```

---

## Testing Strategy

### Unit Tests (tests/unit/test_simple_agent.py)

**Test Cases:**
1. `test_jinja2_role_with_variables` - Render role with {{ agent_name }}
2. `test_jinja2_user_prompt_template_with_conditionals` - Test {% if %} blocks
3. `test_jinja2_with_loops` - Test {% for %} over tools
4. `test_jinja2_with_filters` - Test {{ text | upper }}
5. `test_jinja2_with_date_formatting` - Test current_time/current_date
6. `test_backward_compatibility_format_string` - Ensure {user_input} still works
7. `test_jinja2_error_handling` - Invalid template syntax
8. `test_jinja2_context_variables` - All context vars available

### Integration Tests (tests/integration/test_phase_1_7.py)

**Test Cases:**
1. `test_jinja2_full_workflow` - Create agent with Jinja2, run prompt, verify rendering
2. `test_jinja2_with_yaml_loading` - Load YAML with Jinja2, verify templates render
3. `test_jinja2_mixed_templates` - Some Jinja2, some format strings (compatibility)

### Manual Testing

```yaml
# Create test agent: config/agents/jinja_test.yaml
name: "jinja_test"
role: |
  You are {{ agent_name }} (provider: {{ model_provider }}).
  Current time: {{ current_time.strftime('%Y-%m-%d %H:%M') }}

  {% if verbosity >= 2 %}
  I will provide detailed responses.
  {% else %}
  I will be concise.
  {% endif %}

user_prompt_template: |
  {{ user_input }}

  {% if tools %}
  (Available tools: {{ tools | join(', ') }})
  {% endif %}
```

---

## Implementation Steps (TDD)

### Step 1: Add Dependency
```bash
echo "jinja2>=3.1.0" >> requirements.txt
pip install jinja2
```

### Step 2: Write Failing Tests
- Write 8 unit tests in `test_simple_agent.py`
- Run tests to confirm they fail

### Step 3: Implement Template Rendering
- Add `_build_context()` method
- Add `_render_template()` method with auto-detection
- Update `__init__()` to render role
- Update `run()` to render user_prompt_template

### Step 4: Verify Unit Tests Pass
```bash
pytest tests/unit/test_simple_agent.py -v
```

### Step 5: Write Integration Tests
- Create `test_phase_1_7.py`
- Write 3 integration tests

### Step 6: Verify All Tests Pass
```bash
pytest tests/ -v
```

### Step 7: Update Documentation
- Update Progress_Tracker.md
- Add examples to README (future)

---

## Backward Compatibility

**Guaranteed:**
- All existing YAML files work unchanged
- Simple format strings `{user_input}` continue to work
- Migration is optional - use Jinja2 when you want advanced features

**Detection Logic:**
```python
# These trigger Jinja2:
"{{ variable }}"  # Variable
"{% if x %}"      # Conditional
"{# comment #}"   # Comment

# These use simple format():
"{user_input}"    # Format string
"plain text"      # No templates
```

---

## Success Criteria

- [  ] jinja2 dependency added
- [  ] 8 unit tests written and passing
- [  ] Jinja2 rendering works in `role` field
- [  ] Jinja2 rendering works in `user_prompt_template` field
- [  ] All context variables available (agent_name, current_time, etc.)
- [  ] Conditionals work ({% if %})
- [  ] Loops work ({% for %})
- [  ] Filters work ({{ text | upper }})
- [  ] Backward compatibility maintained (format strings still work)
- [  ] Error handling for invalid Jinja2 syntax
- [  ] 3 integration tests passing
- [  ] Total test count: 202+ (194 + 8 unit + 3 integration - some may be covered)
- [  ] Documentation updated

---

## Non-Goals (Future Enhancements)

**Not in this phase:**
- Custom Jinja2 filters
- Template inheritance
- Macros
- File-based template loading
- User-defined variables in YAML `variables:` section

These can be added later if needed.

---

## Risks & Mitigation

**Risk 1: Breaking existing format strings**
- Mitigation: Auto-detection ensures {user_input} != {{ user_input }}

**Risk 2: Jinja2 syntax errors**
- Mitigation: Wrap in try/except, provide clear error messages

**Risk 3: Performance overhead**
- Mitigation: Jinja2 is fast; render once at init for role, once per run for user_prompt_template

**Risk 4: Security (template injection)**
- Mitigation: We control template source (YAML files), not user input. User input goes into context, not template.

---

## References

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Jinja2 Template Designer](https://jinja.palletsprojects.com/en/3.1.x/templates/)
- [Python strftime formats](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

---

## Document Metadata

**Version:** 1.0
**Date:** 2025-10-26
**Status:** In Progress
**Estimated Completion:** 4-5 hours

---
