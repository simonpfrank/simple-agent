---
description:
globs:
alwaysApply: true
---
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Simple-Agent Project

A simple agent template.

## Commands

### Testing
- Run all tests: `pytest`
- Run unit tests only: `pytest tests/unit/`
- Run integration tests only: `pytest tests/integration/`
- Run specific test file: `pytest tests/unit/test_filename.py`
- Run tests with coverage: `pytest --cov=src`

### Code Quality
- Lint and format: `ruff check simple_agent/ --fix && ruff format simple_agent/`
- Type checking: `mypy simple_agent/` (if configured)

## Project Structure
- `simple_agent/` - Main source code (seperate folders for modules)
- `tests/unit/` - Unit tests with mocks
- `tests/integration/` - Integration tests with real data
- `tests/data/` - Test data files for integration tests
- `docs/` - Documentation, specifications, and progress tracking

# Development Guidelines

## Core Behavior
**Facts are facts and should be evidenced**. If you don't know or have no evidence, just say you don't know - it is pleasing for the user when you admit uncertainty. If you must speculate, state that you are doing so.

## Core Principles
- **always check you are not going to add duplicate functionality**
- **Simplicity first**: Clear, maintainable code over complex abstractions
- Do not overengineer
- Build incrementally with ~60 lines per iteration
- Ask before creating classes - keep them simple
- Only use abstract classes if totally necessary
- only use pydantic if absolutely necessary
- The human reader of the code should be able to easily understand the class usage and hierarchy
- Always say what you will be doing next and use the todo tool

## Progress Tracking
- **MUST maintain Progress_Tracker.md** in docs/ folder tracking development status
- Update progress tracker after completing each class/method
- Columns: Component, Unit Tests, Code, Integration Tests, Unit Results, Integration Results
- Status values: ❌ Not Done, 🟡 In Progress, ✅ Done
- Results: ✅ Pass, ❌ Fail, ⏭️ N/A

## Development Methodology and Testing Rules
1. Create PRD with user (in docs folder)
2. Create specification with user (in docs folder)
3. Build class by class, small classes (e.g. < 100 lines, can be built in one go)
4. Larger classes should be built incrementally following TDD for each iteration or chunk
5. Use Test Driven Development to build
6. Use pytest for tests with unit tests in tests/unit/ and integration tests in tests/integration/. Test data for integration tests should be in tests/data/
7. When phase complete and all unit tests pass, build integration tests and esnure they pass
8. Final check that phase can be tested in repl and/or cli

### TDD Methodology
TDD must be follwed for new functionality, changes and bug fixing.
1. **Write failing unit tests first** to define expected behavior
2. **Implement code** until unit tests pass
3. **Write integration tests** only after methods exist and unit tests pass
4. **Verify all claims** with actual test output before reporting completion
5. Use mocks for dependencies in unit tests

### Integration Tests (Post-Implementation)
- Write ONLY after methods exist and unit tests pass
- No mocks - test real system integration
- Every method call must correspond to existing, working code
- Use `dir(class_instance)` to verify methods exist before testing
- Verify input and output signatures match the actual functionality by reading the function implementation

## Evidence Requirements
**ALL test claims must be backed by evidence:**
- **NEVER claim test results without running them**
- **NEVER use vague terms** like "crashes" without crash evidence
- **State "NOT TESTED"** if unable to run - don't invent reasons
- Include summarized command output for all test results
- Reference specific error messages for failures

## Python Standards
- Line length: 119 characters, type hints required
- Import order: stdlib → third-party → local (blank line separated)
- Naming: `PascalCase` classes, `snake_case` functions/variables, `UPPER_SNAKE_CASE` constants
- Google-style docstrings with Args/Returns/Raises
- Python logging format: Date, Time, Level, Module, Function, Line, Message




