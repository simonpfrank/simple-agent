# Simple-Agent Backlog

Future enhancements and feature ideas, organized by category.

## Planned Phases

### Phase 1.6: Simplify Prompts & Add User Prompt Templates
**Status:** 📋 Planned - See `docs/phases/PHASE_1.6.md` for full specification
**Priority:** High
**Complexity:** Medium (3-4 hours)

Remove over-engineered template feature and replace with user prompt templates for consistent prompt engineering.

**Quick Summary:**
- Remove: `simple_agent/config/prompts/` directory and template feature
- Add: `user_prompt_template` field in agent YAML for wrapping user input
- Benefit: Simpler architecture + more powerful prompt engineering

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
