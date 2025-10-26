# Simple-Agent Backlog

Future enhancements and feature ideas, organized by category.

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
