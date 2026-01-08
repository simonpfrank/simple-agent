# cli_repl_kit Integration Changes

Summary of changes made during the cli_repl_kit integration into simple-agent.

---

## Changes to cli_repl_kit (submodule)

### core/layout.py
- Fixed `is_top_level` detection for completion menu (line 271)
  - **Before:** `is_top_level = " " not in text.rstrip()` - trailing space was stripped, always showing `/` prefix
  - **After:** `is_top_level = " " not in text[1:] if text.startswith("/") else " " not in text`
  - Subcommands no longer incorrectly show with `/` prefix

### core/key_bindings.py
- Updated `_handle_enter()` to accept selected completion before executing
  - Handles both top-level commands (`start_position < 0`) and subcommands (`start_position = 0`)
  - Builds final command by applying completion's `start_position` correctly

### core/command_executor.py
- Added `context_factory` parameter to `__init__()` (line 51)
- Updated `_execute_click_command()` to pass context to Click (lines 331-333):
  ```python
  ctx_obj = self.context_factory() if self.context_factory else None
  ctx = click.Context(cmd, obj=ctx_obj)
  ```
  - **Fix:** Commands now receive `ctx.obj` with console, agent_manager, etc.
- Added `_show_group_subcommands()` method (lines 376-396)
  - Shows available subcommands when a group command is invoked without subcommand

### core/repl.py
- Added `agent_callback` parameter to REPL constructor (line 72)
- Pass `context_factory` when creating CommandExecutor (line 267)

---

## Changes to simple-agent

### simple_agent/app.py
- Complete rewrite to use cli_repl_kit instead of click_repl
- Creates REPL with context_factory and agent_callback

### simple_agent/plugins/core_commands.py (new)
- `CoreCommandsPlugin` wraps all 15 existing Click commands
- Registers commands with cli_repl_kit's CLI group

### simple_agent/plugins/agent_mode.py (new)
- `create_agent_callback()` for routing free text to active agent

### simple_agent/core/repl_context.py (new)
- `create_context_factory()` bridges simple_agent's managers to cli_repl_kit
- Lazy initialization of AgentManager, ToolManager, FlowManager

### simple_agent/repl_config.yaml (new)
- REPL appearance configuration (colors, history, windows)

### simple_agent/commands/common.py
- Moved `APP_THEME`, `SYMBOLS`, `format_*` functions from `ui/styles.py`

### simple_agent/commands/agent_commands.py
- Added `ThreadPoolExecutor` import
- Wrapped chat loop in single `ThreadPoolExecutor` context manager (lines 325-380)
  - **Fix:** Avoids async event loop conflict between prompt_toolkit and SmolAgents
  - Executor created once per chat session (not per message) for efficiency

### Deleted files
- `simple_agent/ui/` folder (welcome.py, styles.py, completion.py)
- `simple_agent/app_old.py` (backup of original app.py)

---

## Bug Fixes

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Subcommands showing with `/` prefix | `text.rstrip()` removed trailing space | Check raw text for space detection |
| `ctx.obj` is None error | Click context created without `obj` | Pass `context_factory()` to `click.Context()` |
| `asyncio.run()` conflict in chat | SmolAgents calls `asyncio.run()` inside prompt_toolkit's loop | Run agent in separate thread via `ThreadPoolExecutor` |
