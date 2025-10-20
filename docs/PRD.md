# Simple Agent Template: Product Requirements Document

## Executive Summary

This document defines requirements for a simple, lightweight agent framework built on SmolAgents that enables rapid experimentation and automation with minimal code. The framework is designed for personal use, experimentation, and hobby projects, prioritizing simplicity and hackability over production features.

## Vision

**"The Lazy Man's Agent"** - Think of an idea, configure it in YAML, drop in some tools, and go. No overengineering, no production complexity, just practical agents that get things done.

## Core Principles

### 1. Simplicity First
- Minimal code, maximum functionality
- Flat, readable structure (per CLAUDE.md guidelines)
- No unnecessary abstractions or frameworks
- Delete features you don't need without breaking anything

### 2. Configuration Over Code
- Define agents in YAML files
- Drop tools in a directory and they're auto-discovered, but yaml assigns them to agents
- Swap LLM providers with a config change
- No boilerplate, no registration ceremony

### 3. Experimentation Friendly
- Fast iteration cycles
- Easy to modify and extend
- Hackable codebase you can understand in an hour
- Build incrementally, test as you go

### 4. Personal Use, Not Production
- No enterprise features (monitoring, scaling, etc.)
- No complex deployment tooling
- No team collaboration features
- Focus on developer experience for solo use

## User Requirements (Complete List)

### Primary Use Cases
1. **Quick Experimentation & Prototyping**
   - Test ideas rapidly with minimal setup
   - Try different approaches and configurations
   - Fast iteration without fighting the framework

2. **Automation & Tool-Calling Tasks**
   - Web scraping and research
   - File processing and data analysis
   - Code execution and system tasks
   - Browser automation (future)

3. **Multi-Agent Workflows**
   - Chain agents in simple sequential flows
   - Basic conditional routing between agents
   - Research → Review → Write type workflows

### Technical Requirements

#### LLM Support
- **Local LLMs**: LM Studio, Ollama, Transformers (for Raspberry Pi)
- **Cloud APIs**: OpenAI, Anthropic, Google
- **Easy switching**: Change provider in config, no code changes
- **Use .env or script arguments for api keys** 
- **Model agnostic**: Works with any LLM via LiteLLM integration

#### Tool System
- **Easy addition**: Drop Python file in `tools/` directory
- **Auto-discovery**: Tools automatically available to agents, if in yaml
- **MCP support**: Use tools from MCP servers
- **LangChain compatible**: Can use LangChain tools if needed (future)
- **Custom tools**: Simple Python functions with decorators

#### Agent Configuration
- **YAML-based**: Define agents in readable config files
- **Role/persona**: Configure agent personality and behavior
- **Tool selection**: Specify which tools each agent can use
- **Memory settings**: Configure conversation history retention
- **RAG settings**: Enable document retrieval per agent
- **Configuration method**: as much as possible via the repl/cli and as much as possible one overall config.yaml

#### Memory
- **Conversation history**: Retain context across interactions
- **Configurable retention**: Set max messages or token limits
- **Per-agent memory**: Each agent has its own context
- **Simple implementation**: No complex memory architectures

#### RAG (Retrieval-Augmented Generation)
- **Lightweight vector store**: Chroma (no server required)
- **Simple ingestion**: Point to documents folder and go
- **Per-agent stores**: Each agent can have its own knowledge base
- **Optional feature**: Easy to enable/disable per agent
- **Manage via repl/cli as much as possible**: load folders or files, query, delete docs, list etc.
- **Start with simple text, but add modalities**: prove the concept with simple extractors such as html, pdf markdown/txt
   then add modalities to deal with docs with images, images etc

#### Multi-Agent Orchestration
- **Sequential flows**: Agent A → Agent B → Agent C
- **Simple conditionals**: Route based on output/state
- **No complex DAGs**: Keep it simple, script if needed
- **Agent composition**: Agents can call other agents
- **some ability for refinement**: e.g. one agent can get anbother to re-search if results not good enough

#### Human-in-the-Loop
- **Approval gates**: Mark tools as requiring human approval
- **Interactive prompts**: Ask user for input during execution
- **REPL integration**: Natural approval flow in CLI
- **Configurable**: Enable/disable per tool or agent
- **simple repl q&a type approach**: later options for other interfaces

#### Guardrails
- **Input validation**: Check prompts before sending to LLM
- **Output filtering**: Validate agent responses
- **Custom rules**: Define your own guardrail functions
- **Simple architecture**: Wrapper pattern, not complex framework

#### ReACT Pattern
- **Code-first actions**: Agents write actions as code (SmolAgents default)
- **Tool reasoning**: Agent explains what it's doing
- **Iterative execution**: Multi-step problem solving
- **Verbosity control**: Adjust logging detail level
- **simple docker coding container**

### Integration Requirements

#### REPL/CLI Integration
- **Reuse existing template**: Build on current `repl_cli_template`
- **Slash commands**: `/agent run researcher "query"`
- **Agent mode**: Free text goes to agent for processing
- **Rich output**: Formatted responses with syntax highlighting

#### MCP (Model Context Protocol)
- **Tool integration**: Use tools from MCP servers
- **Standard compliance**: Follow MCP protocol
- **Easy configuration**: Register servers in config file

### Future Requirements (Phase 2+)

#### Raspberry Pi Deployment
- **Lightweight**: Run on Pi 4/5 with limited resources
- **Local-first**: Prefer local models when possible
- **Cloud fallback**: Use APIs for heavy tasks
- **Hardware control**: GPIO, motors, sensors as tools

#### Voice Interface
- **Speech-to-text**: Local (Vosk/Whisper.cpp) or cloud
- **Text-to-speech**: pyttsx3 for offline TTS
- **Voice commands**: Alternative to typing in REPL
- **Spoken responses**: Agent speaks results back

#### Hardware Control
- **GPIO tools**: Control pins as agent tools
- **Sensor reading**: Read sensor data during execution
- **Motor control**: Physical robot control
- **Safety limits**: Guardrails for physical actions

#### Browser Control
- **Playwright/Selenium**: As tools for agents
- **Vision integration**: VLM for screen understanding
- **Web scraping**: Extract data from dynamic sites
- **Form filling**: Automate web interactions

#### Screen Control
- **Computer use**: Control desktop applications
- **Screenshot analysis**: VLM understanding of UI
- **Keyboard/mouse**: Automation tools
- **Safety boundaries**: Limit what can be controlled

## Non-Goals (What We Will NOT Build)

### Production Features
- ❌ Horizontal scaling or load balancing
- ❌ Enterprise monitoring/observability
- ❌ Team collaboration features
- ❌ Complex deployment pipelines
- ❌ SLA guarantees or uptime requirements

### Complex Orchestration
- ❌ Complex DAG-based workflows (use LangGraph if needed)
- ❌ Built-in state machines
- ❌ Time-travel debugging
- ❌ Checkpoint/resume systems
- ❌ Distributed agent execution

### Framework Features
- ❌ Plugin architecture
- ❌ Extension marketplace
- ❌ Backward compatibility guarantees
- ❌ Versioned APIs
- ❌ Migration tooling

### Enterprise Concerns
- ❌ Cost tracking and budgeting
- ❌ Rate limiting and quotas
- ❌ Multi-tenancy
- ❌ RBAC or permissions
- ❌ Audit logging

## Success Criteria

### Must Have (MVP)
- [ ] Create agent with YAML config in under 5 lines
- [ ] Add custom tool by dropping Python file in directory
- [ ] Switch LLM providers by changing config value
- [ ] Chain 2+ agents in sequential flow
- [ ] Enable/disable memory per agent
- [ ] Run on desktop with local or cloud LLMs

### Should Have (Phase 1)
- [ ] Human approval for specified tools
- [ ] Simple input/output guardrails
- [ ] RAG with document folder
- [ ] MCP tool integration
- [ ] REPL integration for interactive use

### Nice to Have (Future)
- [ ] Run on Raspberry Pi with local models
- [ ] Voice input/output interface
- [ ] GPIO/hardware control tools
- [ ] Browser automation tools

## Architecture Principles

### Keep It Simple
- Flat file structure, no deep nesting, seperate folders for modules though
- Classes under 100 lines when possible
- Functions do one thing well
- Minimal dependencies

### Build Incrementally
- Start with core: agent + config + tools
- Add features one at a time
- Test each addition before moving on
- Follow TDD methodology from CLAUDE.md
- each functional stage e.g. prompt an llm can be run in the repl
- ability to use repl commands to add config items, perhaps add tools to an agent, etc and these can be saved down to config

### Make It Hackable
- Clear code over clever code
- Comments explain why, not what
- Easy to find and modify behavior
- No magic, no hidden state
- Classes but not abstracts
- As much SOLID and DRY as possible without breaking simplicity and low code rules

### Separation of Concerns (CLI/REPL vs Business Logic)
- **CLI and REPL contain NO business logic** - they are thin interfaces only
- All business logic lives in core modules (e.g., `core/`, `agents/`, `tools/`)
- CLI/REPL commands call core module functions/classes
- This ensures testability and reusability across interfaces
- Follow existing `repl_cli_template` pattern where commands delegate to core logic
- **Future-proof for API/MCP layer**: Clean separation enables easy addition of FastAPI/Flask wrapper or MCP server around core logic without refactoring

### Avoid Overengineering
- No abstractions until you need them twice
- No "just in case" features
- No complex patterns for simple problems
- Delete code that isn't used

## Framework Choice: SmolAgents

### Why SmolAgents?
1. **Minimal codebase**: ~1,000 lines total
2. **Model agnostic**: Works with any LLM via LiteLLM
3. **Code-first agents**: Write actions in code (30% more efficient)
4. **Tool flexibility**: LangChain, MCP, or custom tools
5. **Lightweight**: Perfect for Pi deployment
6. **Active development**: HuggingFace backing, growing community
7. **Multimodal**: Text, vision, video, audio support

### What SmolAgents Doesn't Have (We'll Add)
- Human-in-the-loop approval (~50 lines)
- Guardrails (~30 lines)
- YAML config loading (~50 lines)
- Tool auto-discovery (~30 lines)
- Multi-agent flows (~100 lines)
- REPL integration (~50 lines)

**Total additions: ~310 lines** on top of SmolAgents

### Why NOT Other Frameworks?
- **LangChain/LangGraph**: Too production-focused, complex, hit action limits
- **CrewAI**: More opinionated, less flexible for custom workflows
- **PydanticAI**: Pydantic everywhere adds overhead, less proven
- **AutoGen**: Complex message passing, production-oriented

## Implementation Phases

### Phase 0: Foundation
- Create project structure
- Install SmolAgents and dependencies
- Set up configuration system
- Create basic agent wrapper

### Phase 1: Core Features (MVP)
- YAML agent configuration
- Tool auto-discovery system
- LLM provider switching
- Basic agent execution
- Simple memory (conversation history)
- Multi-agent sequential flows

### Phase 2: Enhanced Features
- Human-in-the-loop approval
- Simple guardrails (input/output validation)
- RAG with Chroma
- MCP tool integration
- REPL/CLI integration

### Phase 3: Advanced Features
- ReACT pattern optimization
- Multi-agent conditional routing
- Advanced memory strategies
- Tool composition and chaining

### Phase 4: Raspberry Pi (Future)
- Pi-optimized deployment
- Local LLM integration (Ollama)
- Voice input/output
- GPIO and hardware tools
- Resource optimization

## Dependencies

### Core
- `smolagents` - Base agent framework
- `pyyaml` - Configuration parsing
- `litellm` - Universal LLM interface
- `click` / `click-repl` - CLI interface (already have)
- `rich` - Terminal formatting (already have)

### Optional (Feature-Specific)
- `chromadb` - Vector store for RAG
- `sentence-transformers` - Local embeddings
- `mcp` - Model Context Protocol tools
- `playwright` - Browser automation (future)
- `RPi.GPIO` - Raspberry Pi hardware (future)
- `vosk` / `whisper.cpp` - Voice input (future)
- `pyttsx3` - Voice output (future)

## Risk Mitigation

### Risk: Over-engineering
**Mitigation**: Follow CLAUDE.md principles, keep classes small, build incrementally

### Risk: SmolAgents API changes
**Mitigation**: Pin version, thin wrapper isolates changes to one file

### Risk: Feature creep
**Mitigation**: Reference this PRD, say no to unnecessary features

### Risk: Complexity in multi-agent flows
**Mitigation**: Keep flows simple, document patterns, provide examples

### Risk: Performance on Raspberry Pi
**Mitigation**: Test early with local models, optimize incrementally

## Measuring Success

### Developer Experience
- Time to create first agent: < 5 minutes
- Time to add custom tool: < 2 minutes
- Time to understand codebase: < 1 hour
- Time to modify core behavior: < 30 minutes

### Functionality
- Can build multi-agent workflows
- Can use local and cloud LLMs
- Can integrate custom tools easily
- Can run on desktop and Pi (future)

### Simplicity
- Core codebase: < 500 lines
- Minimal dependencies: < 10 required packages
- Flat structure: Max 3 directory levels
- No magic: Everything explicit and traceable

## Next Steps

1. **Get PRD approval** from stakeholder (you!)
2. **Create Technical Specification** with detailed architecture
3. **Create Progress Tracker** to monitor development
4. **Begin Phase 0** implementation with TDD methodology

---

**Version**: 1.0
**Date**: 2025-10-20
**Status**: Draft - Awaiting Approval
