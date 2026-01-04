# Reusable REPL Framework - Implementation Plan

## Overview

This plan outlines how to extract the REPL functionality from simple-agent into a reusable framework that can be used across multiple projects.

## Current Situation

The simple-agent project has a sophisticated Click-based REPL with:
- **491 lines** in `app.py` (main entry point)
- **17 command files** (4011 total lines) in `simple_agent/commands/`
- **Custom completion** via `SlashCommandCompleter` (188 lines)
- **Manual command registration** - all commands added in `app.py`
- **Context-based dependency injection** via Click's `ctx.obj`
- **Rich console** output with custom styling
- **No plugin system** - requires modifying `app.py` to add commands

## Requirements

1. **Separate Repository**: REPL maintained independently from projects
2. **Multi-Project Reuse**: Include REPL in different projects (including simple-agent)
3. **Easy Customization**: Different commands per project without modifying core REPL
4. **Essential Features to Preserve**:
   - ✅ Slash command completion (`/` prefix, Claude Code style)
   - ✅ Rich console output (colors, tables, formatting)
   - ✅ Context injection (shared state via Click context)
   - ✅ Agent mode with optional free text input
   - ✅ **CRITICAL**: Dual-mode support (REPL + CLI)

## Recommended Architecture

### Repository Strategy: Git Dependency with Editable Local Development

**Setup**:
```bash
# Create REPL framework repo
cd ~/Documents/dev/python
git clone https://github.com/simonpfrank/repl-framework.git
cd repl-framework
# ... implement framework ...
git push origin main

# Use in simple-agent (editable mode for development)
cd ../simple-agent
pip install -e ../repl-framework
pip install -e .
```

**Bidirectional Updates**:
- Clone REPL repo alongside projects
- Install in editable mode for development: `pip install -e ../repl-framework`
- Make improvements to REPL from any project
- Push changes back to REPL repo
- Other projects update with: `pip install --upgrade repl-framework`

### Plugin System: Entry Points

**How it works**:

1. **Core REPL** discovers commands via Python entry points
2. **Projects** register commands in their `pyproject.toml`
3. **No code changes** needed to core REPL when adding commands

**Example** - Project registers commands in `pyproject.toml`:
```toml
[project.entry-points."repl.commands"]
system = "simple_agent.plugins:SystemCommandsPlugin"
agent = "simple_agent.plugins:AgentCommandsPlugin"
tool = "simple_agent.plugins:ToolCommandsPlugin"
```

**Entry Points Pros**:
- ✅ Standard Python packaging mechanism
- ✅ Automatic discovery - REPL finds plugins without configuration
- ✅ Type-safe - imports actual Python classes, not strings
- ✅ Version management - plugins can specify compatible REPL versions
- ✅ Third-party support - others can publish plugins as separate packages
- ✅ IDE support - autocomplete and navigation work

**Entry Points Cons**:
- ⚠️ Requires understanding entry points concept (mild learning curve)
- ⚠️ Need to reinstall package after changing entry points: `pip install -e .`
- ⚠️ Slightly more setup (but only once)

**Alternative: Config YAML Pros**:
- ✅ Simple to understand - just list modules and commands
- ✅ No reinstall needed - edit YAML and restart REPL
- ✅ Runtime configuration - can enable/disable commands without code changes
- ✅ Lower barrier - no entry points concept to learn

**Alternative: Config YAML Cons**:
- ⚠️ String-based imports - typos only caught at runtime
- ⚠️ No version management
- ⚠️ No IDE support
- ⚠️ Brittle - module refactoring breaks config
- ⚠️ No third-party plugins possible

## Implementation Phases

### Phase 1: Create REPL Framework Repository

**New repo**: `repl-framework`

**Files to create**:
1. `src/repl_framework/__init__.py` - Package init, export main classes
2. `src/repl_framework/core/repl.py` - Core REPL class with plugin discovery (~250 lines)
3. `src/repl_framework/core/completion.py` - SlashCommandCompleter from simple-agent (~188 lines)
4. `src/repl_framework/core/context.py` - Context management utilities (~50 lines)
5. `src/repl_framework/plugins/base.py` - CommandPlugin base class (~30 lines)
6. `src/repl_framework/ui/styles.py` - Rich styling from simple-agent (~50 lines)
7. `pyproject.toml` - Package definition with dependencies
8. `README.md` - Documentation and examples

**Code to extract from simple-agent**:
- `simple_agent/app.py` lines 243-462 (`start_repl()` function) → `repl_framework/core/repl.py`
- `simple_agent/ui/completion.py` (entire file) → `repl_framework/core/completion.py`
- `simple_agent/ui/styles.py` (entire file) → `repl_framework/ui/styles.py`

**Dependencies**:
```toml
dependencies = [
    "click>=8.0",
    "click-repl>=0.3",
    "prompt-toolkit>=3.0",
    "rich>=13.0",
]
```

### Phase 2: Implement Plugin System

**Plugin base class** (`repl_framework/plugins/base.py`):
```python
from abc import ABC, abstractmethod
import click
from typing import Callable, Dict, Any

class CommandPlugin(ABC):
    """Base class for REPL command plugins."""

    @abstractmethod
    def register(self, cli: click.Group, context_factory: Callable[[], Dict[str, Any]]) -> None:
        """Register commands with the CLI group."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name for identification."""
        pass
```

**Core REPL** (`repl_framework/core/repl.py`):
- Add plugin discovery using `importlib.metadata.entry_points()`
- Load plugins from entry point group `repl.commands`
- Call `plugin.register(cli, context_factory)` for each discovered plugin
- Preserve dual-mode support (REPL interactive + CLI command-line)

### Phase 3: Refactor simple-agent to Use Framework

**Files to create**:
1. `simple_agent/plugins.py` - Plugin implementations (~200 lines)

**Files to modify**:
1. `simple_agent/app.py` - Simplify to use REPL class (491 → ~30 lines)
2. `simple_agent/pyproject.toml` - Add repl-framework dependency + entry points (+20 lines)

**Files to delete**:
1. `simple_agent/ui/completion.py` - Moved to framework (-188 lines)
2. `simple_agent/ui/styles.py` - Moved to framework (-50 lines)

**Example plugin** (`simple_agent/plugins.py`):
```python
from repl_framework.plugins.base import CommandPlugin
from .commands.system_commands import help_command, quit_command, exit_command, refresh
from .commands.agent_commands import agent

class SystemCommandsPlugin(CommandPlugin):
    name = "system"

    def register(self, cli, context_factory):
        cli.add_command(help_command, name="help")
        cli.add_command(quit_command, name="quit")
        cli.add_command(exit_command, name="exit")
        cli.add_command(refresh, name="refresh")

class AgentCommandsPlugin(CommandPlugin):
    name = "agent"

    def register(self, cli, context_factory):
        cli.add_command(agent, name="agent")
```

**Simplified app.py**:
```python
import click
from repl_framework import REPL
from .core.app_context import create_context

@click.group()
@click.option("--debug", "-d", is_flag=True, help="Enable debug logging")
@click.option("--config-file", "-c", default=None, help="Config file path")
@click.pass_context
def cli(ctx, debug, config_file):
    """Simple Agent CLI/REPL"""
    ctx.obj = create_context(debug=debug, config_file=config_file)

def main():
    repl = REPL(
        cli_group=cli,
        app_name="Simple Agent",
        plugin_group="repl.commands",
    )
    repl.start()

if __name__ == "__main__":
    main()
```

### Phase 4: Test and Validate

**Test checklist**:
1. ✅ REPL mode works: `simple-agent` enters interactive mode
2. ✅ CLI mode works: `simple-agent agent list` runs command directly
3. ✅ Slash completion works in REPL: `/agent<TAB>` shows completions
4. ✅ Rich output preserved: Tables, colors, formatting still work
5. ✅ Context injection works: Commands receive `ctx.obj` with managers
6. ✅ Agent mode works: Free text input when in agent chat mode
7. ✅ All 17+ command groups load correctly
8. ✅ Config loading preserved: YAML config still read on startup
9. ✅ History preserved: `~/.simple-agent/history` still works
10. ✅ Error handling preserved: User-friendly error messages

### Phase 5: Documentation

- Create `repl-framework/README.md` with installation, quick start, plugin guide
- Update `simple-agent/README.md` to mention REPL framework

## Net Impact on simple-agent

**Lines removed**: ~470 lines
**Lines added**: ~220 lines
**Net reduction**: **250 lines saved**

## Example: Using REPL in New Project

```python
# my-new-project/pyproject.toml
[project]
name = "my-new-cli"
dependencies = [
    "repl-framework @ git+https://github.com/simonpfrank/repl-framework.git@main",
]

[project.entry-points."repl.commands"]
my_commands = "my_new_cli.plugins:MyCommandsPlugin"

# my-new-project/my_new_cli/plugins.py
from repl_framework.plugins.base import CommandPlugin
import click

class MyCommandsPlugin(CommandPlugin):
    name = "my_commands"

    def register(self, cli, context_factory):
        @click.command()
        def hello():
            """Say hello!"""
            print("Hello from my CLI!")

        cli.add_command(hello, name="hello")

# my-new-project/my_new_cli/main.py
from repl_framework import REPL

def main():
    repl = REPL(app_name="My Project", context_factory=dict)
    repl.start()
```

**Result**: Instant REPL with `/hello` command, no REPL code to maintain!

---

## Questions Before Implementation

Please answer these questions to finalize the architectural decisions:

### 1. Plugin System

**Question**: Are you comfortable with the entry points approach after seeing the pros/cons? Or would you prefer starting with Config YAML for simplicity?

**Options**:
- A) Use Entry Points (recommended) - Standard Python pattern, type-safe, but requires `pip install -e .` after changes
- B) Use Config YAML - Simpler, no reinstall, but string-based and less robust
- C) Support both - Entry points as primary, YAML as optional override (adds complexity)

**Your Answer**:


---

### 2. Agent Mode Handling

**Question**: How should agent mode (free text input) be handled? Currently in simple-agent, when in agent chat mode, input is sent directly to the agent instead of being parsed as commands.

**Options**:
- A) Framework feature - Build agent mode toggle into the core REPL framework (any project can use it)
- B) Simple-agent specific - Keep it as custom logic in simple-agent's implementation
- C) Plugin hook - Framework provides hooks for custom input handling, simple-agent implements agent mode via hook

**Your Answer**:


---

### 3. Styling Customization

**Question**: Should the Rich theme/styles be customizable per project, or shared from framework?

**Options**:
- A) Shared from framework - All projects using the REPL get the same consistent styling
- B) Customizable per project - Projects can override colors, table styles, etc. via config or parameters
- C) Both - Framework provides defaults, projects can optionally customize

**Your Answer**:


---

### 4. Package Name

**Question**: Is `repl-framework` a good name, or would you prefer something else?

**Options**:
- A) `repl-framework` - Generic, describes what it is
- B) `click-repl-framework` - More specific, indicates it's built on Click
- C) `cli-repl-kit` - Emphasizes both CLI and REPL capabilities
- D) `interactive-cli` - Emphasizes the interactive nature
- E) Other (please specify):

**Your Answer**:


---

## Next Steps

Once you've answered the questions above, I'll proceed with implementing the framework according to your preferences.
