# CLI Refresh Specification

**Goal**: Achieve Claude Code-level CLI polish for simple-agent REPL

**Status**: Draft - Ready for Phase 1 implementation
**Priority**: High (pre-requisite for SmolAgents removal)
**Estimated Effort**: 4-6 hours (Phase 1), then assess Phase 2

---

## Key User Requirements (Phase 1 Focus)

### Critical Priorities
1. **Menu Styling**: Claude Code purple (`#6B4FBB`) for selected item across full line, white for unselected
2. **Menu Spacing**: Bigger gap between command and help text (20 char padding)
3. **Input Area Boundaries**: Grey horizontal lines (`─`) above and below the typing area (like a text box frame)
4. **Multi-line Input**: Shift+Enter for new lines (not Alt+Enter), NO backslash at line ends
5. **Tab Behavior**: Tab fills command, then automatically prompts for next level (subcommands/options)

### Optional/Deferred
- Custom prompt → Make configurable in `config.yaml` instead of hardcoded
- Fuzzy matching → Removed from Phase 1, can add later if needed
- Input validation → Keep simple for now
- Phase 2 (Output) → User will review and approve before implementation

---

## Architecture Overview

**Current Stack**:
- `prompt_toolkit` - Terminal input handling, completion, key bindings
- `click` + `click-repl` - Command framework and REPL loop
- `rich` - Terminal output rendering (already integrated across 19 files)

**Key Files**:
- `simple_agent/app.py` - REPL initialization, prompt_toolkit configuration
- `simple_agent/ui/completion.py` - Custom completer (slash commands, subcommands, options)
- `simple_agent/ui/styles.py` - Rich theming and formatting helpers
- `simple_agent/commands/*.py` - Command implementations (19 command files)

---

## Phase 1: Input Experience Improvements

### 1.1 Typing Area Enhancements

#### Current Issues
- **CRITICAL**: Multi-line display boundaries don't work well - grey lines above/below are wayward
- Multi-line input behavior needs improvement
- Prompt could be configurable rather than fixed

#### Improvements

**A. Fix Input Area Boundaries (PRIORITY 1)**
```python
# In app.py - Add grey horizontal lines above and below typing area

from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.layout import Container, Window, FormattedTextControl, HSplit
from prompt_toolkit.widgets import TextArea

# We need to customize the REPL prompt display to add top/bottom borders
# This requires modifying how prompt_toolkit renders the input area

# Option 1: Use prompt_toolkit's bottom_toolbar for bottom line
def get_bottom_toolbar():
    """Grey line below input area."""
    terminal_width = shutil.get_terminal_size().columns
    return FormattedText([('class:input-border', '─' * terminal_width)])

# Option 2: Use rprompt for top line indicator
def get_rprompt():
    """Return empty - we'll handle borders differently."""
    return None

prompt_kwargs = {
    "message": "> ",  # Simple prompt
    "bottom_toolbar": get_bottom_toolbar,  # Grey line below input
    "multiline": False,  # Default single-line, Shift+Enter for multi
    ...
}

# Style the border line
completion_style = Style.from_dict({
    ...
    "input-border": "fg:#666666",  # Grey horizontal line
    "bottom-toolbar": "fg:#666666",  # Grey for bottom border
})

# Note: prompt_toolkit doesn't natively support a "top border" for the input area
# The bottom_toolbar provides the bottom grey line
# For the top line, we can print it before starting the REPL loop, or accept
# that the visual separator comes from the previous command's output
```

**Alternative Simpler Approach:**
```python
# Just use bottom_toolbar for the bottom grey line
# The top is naturally separated by previous output

def get_bottom_toolbar():
    """Simple grey line below input."""
    return [('class:toolbar', '─' * shutil.get_terminal_size().columns)]

prompt_kwargs = {
    ...
    "bottom_toolbar": get_bottom_toolbar,
}

completion_style = Style.from_dict({
    ...
    "toolbar": "fg:#666666",  # Grey bottom line
})
```

**Note on Top Line:**
prompt_toolkit doesn't have a native "top toolbar" for the input area. Options:
1. Accept that previous command output naturally separates input area
2. Print a grey line before each prompt (simple `console.print("[dim]" + "─" * width + "[/dim]")`)
3. Use a custom layout (more complex, requires rewriting REPL structure)

**Recommendation:** Use bottom_toolbar for bottom line, and print top line before each prompt
```python
# In the REPL loop, before each prompt:
terminal_width = shutil.get_terminal_size().columns
console.print(f"[dim]{'─' * terminal_width}[/dim]")
# Then show prompt
```
```

**B. Multi-line Behavior**
```python
# Shift+Enter to insert newline (not Alt+Enter)
@kb.add('s-enter')  # Shift+Enter to insert newline
def _(event):
    """Insert newline for multi-line input."""
    event.current_buffer.insert_text('\n')

# NO backslash at end of lines
# prompt_toolkit doesn't add backslash by default, so no action needed
# Just ensure we don't enable any continuation indicators

prompt_kwargs = {
    ...
    "multiline": False,  # Default single-line, use Shift+Enter for multi-line
    "wrap_lines": True,  # Soft wrap long lines instead of scrolling
}

# No continuation prompt needed - no vertical pipes or backslashes
# Just clean line breaks when user presses Shift+Enter
```

**C. Configurable Prompt (Optional)**
```python
# In config.yaml - allow prompt customization
ui:
  prompt: "> "  # Default
  # Alternative: "simple-agent > "
  # Alternative: "[{agent}] > " for dynamic agent name

# In app.py - read from config
prompt_text = ConfigManager.get(config_dict, "ui.prompt", "> ")

# Support {agent} placeholder for dynamic prompts
def get_prompt_tokens():
    """Return prompt tokens, supporting dynamic placeholders."""
    prompt = ConfigManager.get(config_dict, "ui.prompt", "> ")

    # Replace placeholders if present
    if "{agent}" in prompt and context.get("active_agent"):
        prompt = prompt.replace("{agent}", context["active_agent"])

    return FormattedText([('', prompt)])
```

**D. Paste Handling**
```python
# Add to prompt_kwargs for better paste support
prompt_kwargs["enable_system_prompt"] = True  # Allow system clipboard
prompt_kwargs["mouse_support"] = True  # Enable mouse selection/paste
```

**Effort**: 2-3 hours
**Priority**: High (Multi-line boundaries is CRITICAL)
**Dependencies**: None

---

### 1.2 Menu Behavior Improvements

#### Current Issues
- **CRITICAL**: Menu style not subtle enough - needs Claude Code purple-for-selected, white-for-unselected style
- **CRITICAL**: Not enough space between command and help text
- Tab behavior needs to fill command then prompt for variables/submenus
- Menu may not be persistent enough

#### Improvements

**A. Claude Code Menu Styling (PRIORITY 1)**
```python
# In app.py - Update completion_style to match Claude Code exactly

completion_style = Style.from_dict({
    # Menu container - no background, subtle
    "completion-menu": "",  # Transparent background
    "completion-menu.completion": "fg:#ffffff",  # White text for unselected items
    "completion-menu.completion.current": "bg:#6B4FBB fg:#ffffff bold",  # Purple background, white text for selected (full line)

    # Meta (help text) area - more spacing
    "completion-menu.meta": "",  # Transparent background
    "completion-menu.meta.completion": "fg:#888888",  # Grey help text for unselected
    "completion-menu.meta.completion.current": "bg:#6B4FBB fg:#ffffff",  # White help text on purple for selected

    # Scrollbar
    "scrollbar.background": "bg:#333333",
    "scrollbar.button": "bg:#6B4FBB",

    # Continuation lines (the grey pipes)
    "continuation": "fg:#666666",
})
```

**B. Increase Spacing Between Command and Help Text**
```python
# In completion.py - SlashCommandCompleter.get_completions()

# Current: display_meta is set directly
# Change to: Add padding between command and meta

yield Completion(
    text=cmd_name,
    start_position=start_position,
    display=f"/{cmd_name:<20}",  # Left-align command with 20 char width (creates spacing)
    display_meta=cmd_help or "",
)

# For subcommands:
yield Completion(
    text=subcmd_name,
    start_position=start_position,
    display=f"{subcmd_name:<20}",  # Consistent spacing
    display_meta=help_text,
)

# For options:
yield Completion(
    text=display_opt + " ",
    start_position=start_position,
    display=f"{display_opt:<20}",  # Consistent spacing
    display_meta=help_text,
)
```

**C. Tab Behavior - Fill Command Then Prompt**
```python
# This is already handled by prompt_toolkit's default Tab behavior
# Tab completes the current item and shows next level completions automatically

# Ensure complete_while_typing is True so menu updates as user types
prompt_kwargs = {
    ...
    "complete_while_typing": True,  # Show completions as you type
    "complete_in_thread": False,  # Sync for fast response
}

# After Tab fills command, completer automatically shows subcommands/options
# This is handled in completion.py logic (already implemented)
```

**D. Menu Height Configuration**
```python
# In app.py - adjust menu height based on terminal size
import shutil

terminal_height = shutil.get_terminal_size().lines
# Reserve 25% of terminal for menu, max 12 lines, min 6
COMPLETION_MENU_HEIGHT = min(12, max(6, terminal_height // 4))

prompt_kwargs = {
    ...
    "reserve_space_for_menu": COMPLETION_MENU_HEIGHT,
}
```

**E. Command History Improvements**
```python
# Better history file location
history_file = Path.home() / ".simple-agent" / "history"
history_file.parent.mkdir(exist_ok=True)

prompt_kwargs["history"] = FileHistory(str(history_file))
prompt_kwargs["enable_history_search"] = True  # Ctrl+R for history search
```

**Effort**: 2-3 hours
**Priority**: High (Menu styling is CRITICAL for visual polish)
**Dependencies**: None

---

### 1.3 Keyboard Shortcuts & Key Bindings

#### Current State
- Uses prompt_toolkit defaults (Tab, arrows, Enter, Backspace)
- No custom shortcuts documented

#### Proposed Shortcuts

```python
# Add to kb in app.py

@kb.add('c-c')  # Ctrl+C - Graceful interrupt
def _(event):
    """Cancel current input and show new prompt."""
    event.app.current_buffer.reset()

@kb.add('c-d')  # Ctrl+D - Exit REPL
def _(event):
    """Exit the REPL."""
    event.app.exit(exception=EOFError)

@kb.add('c-l')  # Ctrl+L - Clear screen
def _(event):
    """Clear the screen."""
    event.app.renderer.clear()

@kb.add('c-u')  # Ctrl+U - Clear line
def _(event):
    """Clear current line."""
    event.app.current_buffer.delete_before_cursor(count=1000)

@kb.add('c-w')  # Ctrl+W - Delete word
def _(event):
    """Delete word before cursor."""
    event.app.current_buffer.delete_before_cursor(count=event.arg)

@kb.add('c-a')  # Ctrl+A - Beginning of line
def _(event):
    """Move to beginning of line."""
    event.app.current_buffer.cursor_position = 0

@kb.add('c-e')  # Ctrl+E - End of line
def _(event):
    """Move to end of line."""
    event.app.current_buffer.cursor_position = len(event.app.current_buffer.text)

# Document shortcuts in welcome screen
```

**Effort**: 1 hour
**Priority**: Low-Medium
**Dependencies**: None

---

## Phase 2: Output Experience Improvements

### 2.1 Markdown Rendering

#### Current State
- Responses printed as plain text: `console.print(f"\n[bold cyan]Response:[/bold cyan]\n{response_str}\n")`
- No syntax highlighting for code blocks
- No table/list formatting

#### Improvements

```python
from rich.markdown import Markdown
from rich.syntax import Syntax

# In all command files that output LLM responses
# Replace: console.print(response_str)
# With:
console.print(Markdown(response_str))

# For code-only output (like /prompt show):
if is_code_content(content):
    syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
else:
    console.print(Markdown(content))
```

**Files to Update**:
- `simple_agent/commands/agent_commands.py` - `run()`, `chat()`
- `simple_agent/commands/llm.py` - `llm_command()`
- `simple_agent/commands/inspection_commands.py` - `show_prompt()`, `show_response()`
- `simple_agent/commands/flow_commands_cli.py` - `run()`, `debug()`

**Effort**: 30 minutes
**Priority**: High (biggest visual impact)
**Dependencies**: None

---

### 2.2 Status Indicators & Spinners

#### Current State
- Static messages: `console.print(f"\n[dim]Running agent '{name}'...[/dim]")`
- No indication of progress during long operations

#### Improvements

```python
from rich.console import Console

# Replace static messages with status context manager
# Before:
console.print(f"\n[dim]Running agent '{name}'...[/dim]")
response = agent_manager.run_agent(name, prompt_text)

# After:
with console.status(f"[dim]Running agent '{name}'...[/dim]", spinner="dots"):
    response = agent_manager.run_agent(name, prompt_text)
# Status disappears when done

# For multi-step operations:
with console.status("[dim]Loading tools...[/dim]", spinner="dots") as status:
    tool_manager.load_builtin_tools()
    status.update("[dim]Loading agents...[/dim]")
    agent_manager.load_agents()
    status.update("[dim]Initializing RAG...[/dim]")
    collection_manager.initialize()
```

**Standard Spinners**:
- `dots` - Default for most operations
- `line` - For download/upload operations
- `arrow3` - For processing/thinking operations

**Files to Update**:
- `simple_agent/commands/agent_commands.py` - All long-running operations
- `simple_agent/commands/llm.py` - LLM calls
- `simple_agent/commands/collection_commands.py` - Collection operations
- `simple_agent/app.py` - Initialization steps

**Effort**: 1 hour
**Priority**: High
**Dependencies**: None

---

### 2.3 Panels & Structured Output

#### Current State
- Errors shown as: `console.print(f"[red]Error:[/red] {message}")`
- Info messages unstructured
- Tool outputs mixed with other text

#### Improvements

```python
from rich.panel import Panel

# Error panels
console.print(Panel(
    f"[red]{error_message}[/red]",
    title="Error",
    border_style="red",
    padding=(0, 1)
))

# Warning panels
console.print(Panel(
    f"[yellow]{warning_message}[/yellow]",
    title="Warning",
    border_style="yellow",
    padding=(0, 1)
))

# Success panels (for important successes)
console.print(Panel(
    f"[green]{success_message}[/green]",
    title="Success",
    border_style="green",
    padding=(0, 1)
))

# Info panels (for structured info)
console.print(Panel(
    info_content,
    title=f"Agent: {agent_name}",
    border_style="cyan",
    padding=(0, 1)
))

# Tool execution panels
console.print(Panel(
    tool_output,
    title=f"Tool: {tool_name}",
    subtitle=f"Duration: {duration}s",
    border_style="blue",
    padding=(0, 1)
))
```

**Usage Guidelines**:
- **Panels for**: Errors, warnings, tool outputs, structured info
- **Plain text for**: Normal responses, list items, simple status
- **Don't overuse**: Reserve for important/structured content

**Files to Update**:
- Create helper in `simple_agent/ui/output.py`:
  ```python
  def error_panel(message: str) -> Panel: ...
  def warning_panel(message: str) -> Panel: ...
  def success_panel(message: str) -> Panel: ...
  def tool_panel(tool_name: str, output: str, duration: float) -> Panel: ...
  ```
- Update all command files to use helpers

**Effort**: 1.5 hours
**Priority**: Medium
**Dependencies**: None

---

### 2.4 Tables & Structured Data

#### Current State
- Token stats likely already use tables
- Lists shown as plain text

#### Improvements

```python
from rich.table import Table

# Enhance existing tables with better styling
table = Table(
    show_header=True,
    header_style="bold cyan",
    border_style="dim",
    row_styles=["", "dim"],  # Alternating row styles
    padding=(0, 1),
)

# For simple lists, use bullet points
from rich.columns import Columns
from rich.panel import Panel

items = [Panel(item, expand=False) for item in item_list]
console.print(Columns(items, equal=True, expand=True))
```

**Files to Review**:
- `simple_agent/commands/token_stats_commands.py` - Ensure tables are well-styled
- `simple_agent/commands/agent_commands.py` - `list_agents()` could use table
- `simple_agent/commands/tool_commands.py` - `list_tools()` could use table
- `simple_agent/commands/collection_commands.py` - Collection listings

**Effort**: 1 hour
**Priority**: Low-Medium
**Dependencies**: None

---

### 2.5 Syntax Highlighting

#### Current State
- Code blocks in markdown will be highlighted (via Markdown renderer)
- Direct code output not highlighted

#### Improvements

```python
from rich.syntax import Syntax

def display_code(code: str, language: str = "python", line_numbers: bool = True):
    """Display code with syntax highlighting."""
    syntax = Syntax(
        code,
        language,
        theme="monokai",  # or "nord", "dracula", "github-dark"
        line_numbers=line_numbers,
        word_wrap=False,
        indent_guides=True,
    )
    console.print(syntax)

# Usage in inspection commands
# /prompt show - show Python/template code
# /response show - show as markdown (already handled)
# Tool source display - show with syntax
```

**Files to Update**:
- `simple_agent/commands/inspection_commands.py` - Code display
- `simple_agent/commands/tool_commands.py` - Tool source display

**Effort**: 30 minutes
**Priority**: Low
**Dependencies**: Phase 2.1 (Markdown rendering)

---

## Phase 3: Integration & Polish

### 3.1 Consistent Error Handling

#### Current State
- Mix of error styles across commands
- Some show stack traces, some don't
- No consistent error classification

#### Improvements

```python
# Create error handling utilities in simple_agent/ui/errors.py

from enum import Enum
from rich.panel import Panel
from rich.console import Console

class ErrorSeverity(Enum):
    INFO = "blue"
    WARNING = "yellow"
    ERROR = "red"
    CRITICAL = "bold red"

def display_error(
    console: Console,
    message: str,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    details: str = None,
    show_traceback: bool = False
):
    """
    Display error with consistent formatting.

    Args:
        console: Rich console instance
        message: Error message
        severity: Error severity level
        details: Optional detailed explanation
        show_traceback: Whether to show full traceback (debug mode)
    """
    content = f"[{severity.value}]{message}[/{severity.value}]"

    if details:
        content += f"\n\n[dim]{details}[/dim]"

    if show_traceback:
        import traceback
        content += f"\n\n[dim]{traceback.format_exc()}[/dim]"

    console.print(Panel(
        content,
        title=severity.name.title(),
        border_style=severity.value,
        padding=(0, 1)
    ))

# Usage in commands:
try:
    result = agent_manager.run_agent(name, prompt)
except KeyError as e:
    display_error(
        console,
        f"Agent '{name}' not found",
        severity=ErrorSeverity.ERROR,
        details="Use /agent list to see available agents"
    )
except Exception as e:
    display_error(
        console,
        str(e),
        severity=ErrorSeverity.ERROR,
        show_traceback=debug_enabled
    )
```

**Files to Update**: All command files
**Effort**: 2 hours
**Priority**: Medium
**Dependencies**: Phase 2.3 (Panels)

---

### 3.2 Welcome Screen & Help

#### Current State
- Welcome screen exists in `simple_agent/ui/welcome.py`
- Help command shows Click's default help

#### Improvements

```python
# Enhance welcome.py to show:
# - Version info (already there)
# - Quick start tips
# - Keyboard shortcuts
# - Recent updates

def show_welcome(console: Console, app_name: str, version: str, config_file: str, log_file: str):
    """Enhanced welcome screen."""

    # Version banner
    console.print(Panel(
        f"[bold cyan]{app_name}[/bold cyan] v{version}",
        border_style="cyan",
    ))

    # Quick tips
    console.print("\n[bold]Quick Start:[/bold]")
    console.print("  /agent create myagent --role \"You are helpful\"")
    console.print("  /agent run myagent What is AI?")
    console.print("  /help for all commands\n")

    # Keyboard shortcuts
    console.print("[bold]Shortcuts:[/bold]")
    shortcuts = Table(show_header=False, box=None, padding=(0, 2))
    shortcuts.add_column("Key", style="cyan")
    shortcuts.add_column("Action", style="dim")
    shortcuts.add_row("Tab", "Complete command")
    shortcuts.add_row("↑↓", "Navigate history")
    shortcuts.add_row("Ctrl+C", "Cancel input")
    shortcuts.add_row("Ctrl+D", "Exit")
    shortcuts.add_row("Ctrl+L", "Clear screen")
    shortcuts.add_row("Ctrl+R", "Search history")
    console.print(shortcuts)
    console.print()

    # Config info
    console.print(f"[dim]Config: {config_file} | Logs: {log_file}[/dim]\n")

# Enhanced /help command
@click.command()
def help_command():
    """Show categorized help."""
    console.print(Panel("[bold cyan]Simple Agent Commands[/bold cyan]", border_style="cyan"))

    # Group commands by category
    categories = {
        "Agent Management": ["create", "run", "chat", "list", "save"],
        "Tools": ["tool list", "tool info"],
        "Configuration": ["config show", "config set"],
        "History": ["history show", "history clear"],
        # ...
    }

    for category, commands in categories.items():
        console.print(f"\n[bold]{category}[/bold]")
        for cmd in commands:
            console.print(f"  [cyan]/{cmd}[/cyan]")
```

**Files to Update**:
- `simple_agent/ui/welcome.py`
- `simple_agent/commands/system_commands.py` - `help_command()`

**Effort**: 1.5 hours
**Priority**: Low-Medium
**Dependencies**: None

---

### 3.3 Progress Indicators for Long Operations

#### Current State
- Spinners for indefinite waits (Phase 2.2)
- No progress bars for measurable operations

#### Improvements

```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# For operations with known steps
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    console=console
) as progress:
    task = progress.add_task("[cyan]Loading agents...", total=len(agent_files))

    for agent_file in agent_files:
        agent = load_agent(agent_file)
        progress.advance(task)

# For file uploads/downloads
with Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%",
    console=console
) as progress:
    task = progress.add_task("[cyan]Uploading...", total=file_size)
    # Update with: progress.update(task, advance=chunk_size)
```

**Use Cases**:
- Loading multiple agents from directory
- Bulk document processing in RAG
- Large file operations
- Multi-step workflows

**Files to Update**:
- `simple_agent/commands/collection_commands.py` - Document ingestion
- `simple_agent/orchestration/flow_manager.py` - Workflow execution
- `simple_agent/app.py` - Batch initialization

**Effort**: 1.5 hours
**Priority**: Low
**Dependencies**: None

---

## Phase 4: Streaming Output (Optional - Post SmolAgents Removal)

### 4.1 Streaming LLM Responses

#### Current State
- Responses buffered and displayed all at once
- No token-by-token streaming

#### Future Implementation (After Custom LLM Client)

```python
from rich.live import Live
from rich.markdown import Markdown

async def stream_agent_response(agent_name: str, prompt: str):
    """Stream agent response token-by-token."""

    with Live(console=console, refresh_per_second=10, vertical_overflow="visible") as live:
        accumulated = ""

        async for chunk in agent_manager.stream_agent(agent_name, prompt):
            accumulated += chunk
            # Update display with accumulated markdown
            live.update(Markdown(accumulated))

        # Final update ensures complete render
        live.update(Markdown(accumulated))

# Usage:
if supports_streaming(agent):
    await stream_agent_response(name, prompt_text)
else:
    # Fall back to buffered response
    response = agent_manager.run_agent(name, prompt_text)
    console.print(Markdown(str(response)))
```

#### Benefits
- More engaging user experience
- See responses as they generate
- Can interrupt long responses (Ctrl+C)

#### Requirements
- Custom LLM client with streaming support (OpenAI SDK, Anthropic SDK)
- Async command handling (or threading)
- Rich Live display integration

**Effort**: 4-6 hours
**Priority**: Low (defer until SmolAgents removed)
**Dependencies**: Custom LLM client implementation

---

### 4.2 Progressive Tool Use Display

#### Current State
- Tool calls likely hidden or shown after completion

#### Future Implementation

```python
from rich.live import Live
from rich.panel import Panel
from rich.tree import Tree

def display_agent_execution(agent_name: str, prompt: str):
    """Display agent thinking, tool calls, and responses progressively."""

    with Live(console=console, refresh_per_second=4) as live:
        # Create execution tree
        tree = Tree(f"[bold cyan]Agent: {agent_name}[/bold cyan]")

        # Show initial prompt
        tree.add(f"[dim]Prompt: {prompt[:50]}...[/dim]")

        # Stream execution
        for event in agent_manager.stream_execution(agent_name, prompt):
            if event.type == "thought":
                tree.add(f"💭 [yellow]{event.content}[/yellow]")

            elif event.type == "tool_call":
                tool_node = tree.add(f"🔧 [cyan]Tool: {event.tool_name}[/cyan]")
                tool_node.add(f"[dim]Args: {event.args}[/dim]")

            elif event.type == "tool_result":
                # Find corresponding tool node and add result
                tool_node.add(f"[green]✓ {event.result[:100]}...[/green]")

            elif event.type == "response":
                tree.add(f"💬 [bold]{event.content}[/bold]")

            live.update(tree)

        # Final display
        live.update(tree)
```

**Effort**: 4-6 hours
**Priority**: Low (defer until SmolAgents removed)
**Dependencies**: Custom agent execution with event streaming

---

## Phase 1 Implementation Checklist

### Files to Modify
- [ ] `simple_agent/app.py` - Update `completion_style`, multi-line boundaries, prompt configuration
- [ ] `simple_agent/ui/completion.py` - Add spacing to command display (20 char padding)
- [ ] `config.yaml` - Add optional `ui.prompt` setting

### Specific Changes

**In `simple_agent/app.py`:**
- [ ] Update `completion_style` dict with Claude Code purple (`#6B4FBB`) for selected items
- [ ] Change unselected text to white (`#ffffff`)
- [ ] Add grey continuation line styling (`fg:#666666`)
- [ ] Implement `get_continuation_tokens()` with pipe character (`┆`)
- [ ] Add `wrap_lines: True` to prompt_kwargs
- [ ] Move history file to `~/.simple-agent/history`

**In `simple_agent/ui/completion.py`:**
- [ ] Update all `yield Completion()` calls to use `display=f"{name:<20}"` for consistent spacing
- [ ] Apply to: top-level commands, subcommands, and options

**In `config.yaml`:**
- [ ] Add optional `ui.prompt` setting (default: `"> "`)
- [ ] Document `{agent}` placeholder for dynamic prompts

### Testing Checklist
- [ ] Menu shows purple background for selected item (full line width)
- [ ] Unselected items show white text with grey help text
- [ ] 20 char spacing visible between command and help text
- [ ] Multi-line input shows grey pipe (`┆`) on continuation lines
- [ ] Tab completes command and shows next level options
- [ ] Continuation lines don't appear wayward or misaligned
- [ ] History saved to `~/.simple-agent/history`
- [ ] Optional: Custom prompt works if configured in config.yaml

### Estimated Time
- **Core changes**: 2-3 hours
- **Testing & refinement**: 1-2 hours
- **Total**: 4-5 hours

---

## Implementation Plan

### Phase 1: Input Polish (APPROVED)
- Section 1.1: Multi-line boundaries and typing area (2-3 hours)
- Section 1.2: Menu styling and behavior (2-3 hours)
- Section 1.3: Keyboard shortcuts (optional, 1 hour)
- Testing and refinement (1-2 hours)

**Total Phase 1: 4-6 hours**

### Phase 2: Output Polish (PENDING USER APPROVAL)
User will review Phase 2 specification after Phase 1 is complete and working well.

**Recommended Order After Phase 1 Approval:**

**Sprint 2: Output Polish (1 week)**

**Sprint 2: Output Polish (1 week)**
- Phase 2.1: Markdown rendering (30 min)
- Phase 2.2: Status indicators (1 hour)
- Phase 2.3: Panels (1.5 hours)
- Phase 2.4: Tables (1 hour)
- Phase 2.5: Syntax highlighting (30 min)
- Testing and refinement (2 hours)

**Sprint 3: Integration (3-4 days)**
- Phase 3.1: Error handling (2 hours)
- Phase 3.2: Welcome/help (1.5 hours)
- Phase 3.3: Progress indicators (1.5 hours)
- Testing and refinement (2 hours)

**Sprint 4: Streaming (Optional - After SmolAgents removal)**
- Phase 4.1: Streaming responses (4-6 hours)
- Phase 4.2: Progressive tool display (4-6 hours)

---

## Testing Strategy

### Manual Testing Checklist

**Input Tests**:
- [ ] Tab completion for all command levels (/, /agent, /agent create, --options)
- [ ] Fuzzy matching works for commands
- [ ] Multi-line input (Alt+Enter)
- [ ] History search (Ctrl+R)
- [ ] All keyboard shortcuts work
- [ ] Paste handling (small and large pastes)
- [ ] Completion menu displays correctly at various terminal sizes
- [ ] Invalid command validation

**Output Tests**:
- [ ] Markdown renders correctly (headers, lists, code blocks, tables)
- [ ] Code syntax highlighting works
- [ ] Status spinners appear and disappear correctly
- [ ] Panels display for errors, warnings, info
- [ ] Tables render with proper alignment
- [ ] Long outputs don't break layout
- [ ] Colors/themes consistent across all outputs

**Integration Tests**:
- [ ] Error handling consistent across all commands
- [ ] Welcome screen displays on startup
- [ ] Help command categorizes commands correctly
- [ ] Progress indicators work for long operations
- [ ] All commands follow new output patterns

### Automated Testing

```python
# tests/integration/test_cli_output.py

def test_markdown_rendering():
    """Verify markdown renders correctly."""
    response = "# Heading\n\n- Item 1\n- Item 2\n\n```python\nprint('hi')\n```"
    # Assert markdown is rendered with proper formatting

def test_error_panel():
    """Verify error panels display correctly."""
    # Mock error condition
    # Assert panel is used with correct style

def test_status_spinner():
    """Verify status spinners work."""
    # Mock long operation
    # Assert spinner appears and disappears

# tests/unit/test_completion.py

def test_fuzzy_matching():
    """Test fuzzy completion matching."""
    assert fuzzy_match("cfg", "config") == True
    assert fuzzy_match("agt", "agent") == True
    assert fuzzy_match("xyz", "agent") == False
```

---

## Success Criteria

### Phase 1 Success
- [ ] Tab completion feels fast and accurate
- [ ] Menu doesn't flicker or disappear unexpectedly
- [ ] All keyboard shortcuts documented and working
- [ ] Multi-line input available when needed
- [ ] History search works reliably

### Phase 2 Success
- [ ] All LLM responses render as markdown with syntax highlighting
- [ ] Long operations show spinners instead of hanging silently
- [ ] Errors/warnings/info displayed in clear panels
- [ ] Tables properly formatted and aligned
- [ ] Output looks polished and professional

### Phase 3 Success
- [ ] Error handling consistent across all commands
- [ ] Welcome screen helpful for new users
- [ ] Help command well-organized
- [ ] No ugly or confusing output anywhere
- [ ] CLI feels as polished as Claude Code

### Phase 4 Success (Optional)
- [ ] Streaming responses feel responsive
- [ ] Can see agent "thinking" in real-time
- [ ] Tool calls visible as they happen
- [ ] No performance issues with streaming

---

## Known Risks & Mitigations

### Risk 1: Terminal Compatibility
**Issue**: Different terminals handle Rich rendering differently
**Mitigation**: Test on major terminals (iTerm2, Terminal.app, Windows Terminal, VS Code terminal)
**Fallback**: Detect terminal capabilities and degrade gracefully

### Risk 2: prompt_toolkit Version Issues
**Issue**: Monkey-patch of click_repl may break with updates
**Mitigation**: Pin exact version in requirements.txt, add version check
**Fallback**: Document known compatible versions

### Risk 3: Performance with Large Outputs
**Issue**: Rich rendering can be slow for very large outputs
**Mitigation**: Add output truncation/pagination for large responses
**Fallback**: Allow disabling Rich formatting via flag

### Risk 4: Streaming Implementation Complexity
**Issue**: Phase 4 requires async or threading, complex state management
**Mitigation**: Implement after SmolAgents removal when custom client gives full control
**Fallback**: Keep buffered responses as default, streaming as opt-in

---

## Dependencies

### Python Packages (Already Installed)
- `rich>=13.0` - Terminal rendering
- `prompt_toolkit>=3.0` - Input handling
- `click>=8.0` - Command framework
- `click-repl>=0.3.0,<0.4.0` - REPL loop

### New Utilities to Create
- `simple_agent/ui/output.py` - Output formatting helpers
- `simple_agent/ui/errors.py` - Error display utilities
- `simple_agent/ui/progress.py` - Progress indicator helpers

### Configuration
No new configuration required - all improvements use existing Rich/prompt_toolkit capabilities

---

## Future Enhancements (Beyond Scope)

- **Themes**: User-selectable color themes (light/dark variants)
- **Plugins**: Allow custom completers and formatters
- **Logging UI**: Live log viewer in REPL (split pane)
- **Agent Monitoring**: Real-time token usage display during execution
- **Export**: Save formatted output to HTML/PDF
- **Accessibility**: Screen reader support, high-contrast mode

---

## References

- [Rich Documentation](https://rich.readthedocs.io/)
- [prompt_toolkit Documentation](https://python-prompt-toolkit.readthedocs.io/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Claude Code UX Patterns](https://claude.ai/code)

---

**Document Status**: Draft
**Last Updated**: 2025-12-14
**Author**: Claude + Simon Frank
**Next Review**: After Phase 1 implementation
