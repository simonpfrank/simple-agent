"""
SimpleAgent - Thin wrapper around SmolAgents with support for multiple agent types.

Provides a simplified interface for creating and running agents with LiteLLM support.
Supports ToolCallingAgent (default, safe), CodeAgent (with Docker), and MultiStepAgent.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Literal, Optional

from jinja2 import Environment, BaseLoader, TemplateError
from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel
from smolagents.monitoring import LogLevel

from simple_agent.core.config_manager import ConfigManager
from simple_agent.tools.helpers.token_counter import estimate_tokens

logger = logging.getLogger(__name__)


class SimpleAgent:
    """Thin wrapper around SmolAgents with support for multiple agent types."""

    def __init__(
        self,
        name: str,
        model_provider: str,
        model_config: Dict[str, Any],
        role: Optional[str] = None,
        tools: Optional[list] = None,
        verbosity: int = 1,
        max_steps: int = 10,
        agent_type: Literal["tool_calling", "code"] = "tool_calling",
        executor_type: Literal["docker", "e2b", "modal", "wasm"] = "docker",
        debug_enabled: bool = False,
        user_prompt_template: Optional[str] = None,
        token_budget: Optional[int] = None,
        token_warning_threshold: Optional[int] = None,
    ):
        """
        Initialize agent.

        Args:
            name: Agent identifier
            model_provider: "openai", "ollama", etc.
            model_config: Dict with model settings
            role: Optional system prompt/persona
            tools: List of tool instances
            verbosity: 0=quiet, 1=normal, 2=verbose (DEPRECATED - use debug_enabled)
            max_steps: Max tool call iterations
            agent_type: Agent type - "tool_calling" (safe, default) or "code" (requires Docker)
            executor_type: Executor for code agent - "docker" (default), "e2b", "modal", "wasm"
            debug_enabled: Enable debug mode (verbose output and logging)
            user_prompt_template: Optional template to wrap user input. Use {user_input} placeholder.
            token_budget: Hard limit on input prompt size (prevents rate limit hits)
            token_warning_threshold: Soft warning threshold before token_budget

        Raises:
            ValueError: If invalid agent_type or attempting to use unsafe executor
        """
        # Validate agent_type
        valid_types = ["tool_calling", "code"]
        if agent_type not in valid_types:
            raise ValueError(
                f"Invalid agent_type '{agent_type}'. Must be one of: {valid_types}"
            )

        # Security: Reject 'local' executor for CodeAgent
        if agent_type == "code" and executor_type == "local":
            raise ValueError(
                "Security error: 'local' executor is unsafe and not allowed. "
                "Use 'docker' (recommended), 'e2b', 'modal', or 'wasm' instead."
            )

        self.name = name
        self.model_provider = model_provider
        self.agent_type = agent_type
        self.debug_enabled = debug_enabled
        self.tools = tools or []  # Store tools list for access
        self.verbosity = verbosity
        self.max_steps = max_steps
        self.user_prompt_template = user_prompt_template
        self.rag_collection = None  # Connected RAG collection (set via set_rag_collection)
        self.token_budget = token_budget
        self.token_warning_threshold = token_warning_threshold

        # Render role template if it contains Jinja2 syntax
        if role:
            self.role = self._render_template(role, user_input=None)
        else:
            self.role = role

        # Create LiteLLM model instance
        self.model = self._create_model(model_provider, model_config)

        # Map debug mode to SmolAgents LogLevel
        # LogLevel: OFF=-1, ERROR=0, INFO=1, DEBUG=2
        verbosity_level = LogLevel.DEBUG if debug_enabled else LogLevel.INFO
        logger.debug(
            f"Agent '{name}' verbosity set to {verbosity_level.name} "
            f"(debug_enabled={debug_enabled})"
        )

        # Create appropriate agent type
        # SmolAgents accepts tools as a list during initialization
        if agent_type == "tool_calling":
            self.agent = ToolCallingAgent(
                tools=tools or [],
                model=self.model,
                max_steps=max_steps,
                instructions=role,
                verbosity_level=verbosity_level,
            )
            logger.info(f"Created ToolCallingAgent: {self.name} ({model_provider})")
        elif agent_type == "code":
            self.agent = CodeAgent(
                tools=tools or [],
                model=self.model,
                max_steps=max_steps,
                verbosity_level=verbosity_level,
                instructions=role,
                executor_type=executor_type,
            )
            logger.info(
                f"Created CodeAgent: {self.name} ({model_provider}) "
                f"with {executor_type} executor"
            )

    def _build_context(self, user_input: Optional[str] = None) -> Dict[str, Any]:
        """
        Build Jinja2 template context with all available variables.

        Args:
            user_input: Optional user input for user_prompt_template rendering

        Returns:
            Dict with context variables for template rendering
        """
        context = {
            "agent_name": self.name,
            "current_time": datetime.now(),
            "current_date": datetime.now().date(),
            "verbosity": self.verbosity,
            "max_steps": self.max_steps,
            "model_provider": self.model_provider,
            "tools": [getattr(t, "name", str(t)) for t in self.tools] if self.tools else [],
        }

        # Add user_input if provided (for user_prompt_template)
        if user_input is not None:
            context["user_input"] = user_input

        return context

    def _render_template(self, template: str, user_input: Optional[str] = None) -> str:
        """
        Render template with Jinja2 or simple format string.

        Auto-detects template type based on syntax:
        - Jinja2: {{ }}, {% %}, or {# #}
        - Format string: {variable_name}

        Args:
            template: Template string to render
            user_input: Optional user input for context

        Returns:
            Rendered template string

        Raises:
            ValueError: If Jinja2 template has invalid syntax
        """
        # Build context
        context = self._build_context(user_input)

        # Auto-detect template type
        if "{{" in template or "{%" in template or "{#" in template:
            # Jinja2 template detected
            try:
                jinja_env = Environment(
                    loader=BaseLoader(),
                    autoescape=False,  # Not rendering HTML
                    trim_blocks=True,
                    lstrip_blocks=True,
                )
                jinja_template = jinja_env.from_string(template)
                rendered = jinja_template.render(**context)
                # Strip trailing whitespace (templates often have trailing newlines)
                return rendered.rstrip()
            except TemplateError as e:
                raise ValueError(f"Jinja2 template error: {e}")
        else:
            # Simple format string (backward compatibility)
            try:
                return template.format(**context)
            except KeyError:
                # If format() fails due to missing keys, just return template as-is
                return template

    def _create_model(self, provider: str, config: Dict[str, Any]) -> LiteLLMModel:
        """
        Create LiteLLM model instance based on provider.

        Args:
            provider: LLM provider name
            config: Model configuration dict (may contain ${VAR} placeholders)

        Returns:
            LiteLLMModel instance
        """
        model_id = config.get("model")
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", 2000)

        logger.debug(
            f"Creating LiteLLM model - provider: {provider}, "
            f"model: {model_id}, temp: {temperature}, max_tokens: {max_tokens}"
        )

        # Handle provider-specific configuration
        if provider == "ollama" or provider == "lmstudio":
            # Local models need custom_llm_provider
            base_url = config.get("base_url", "http://localhost:11434")
            # Resolve env vars at point-of-use (base_url might have tokens)
            base_url = ConfigManager.resolve_env_var(base_url)
            return LiteLLMModel(
                model_id=f"ollama/{model_id}",
                api_base=base_url,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        elif provider == "openai":
            # OpenAI models - resolve API key from env var at point-of-use
            api_key = config.get("api_key", "")
            api_key = ConfigManager.resolve_env_var(api_key)
            return LiteLLMModel(
                model_id=model_id,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        elif provider == "anthropic":
            # Anthropic models - resolve API key from env var at point-of-use
            api_key = config.get("api_key", "")
            api_key = ConfigManager.resolve_env_var(api_key)
            return LiteLLMModel(
                model_id=model_id,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            # Generic provider - let LiteLLM figure it out
            logger.warning(f"Unknown provider: {provider}, using generic configuration")
            # Still resolve api_key if present
            api_key = config.get("api_key")
            if api_key:
                api_key = ConfigManager.resolve_env_var(api_key)
                return LiteLLMModel(
                    model_id=model_id,
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                return LiteLLMModel(
                    model_id=model_id,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

    def set_rag_collection(self, collection: Optional[Any]) -> None:
        """Set the RAG collection for this agent.

        Args:
            collection: Collection instance from CollectionManager or None
        """
        self.rag_collection = collection

    def _inject_rag_context(self, prompt: str) -> str:
        """Inject RAG context into prompt if collection is connected.

        Args:
            prompt: Original user prompt

        Returns:
            Prompt with RAG context injected, or original prompt if no collection
        """
        if not self.rag_collection:
            return prompt

        try:
            # Retrieve relevant chunks from collection
            retrieved = self.rag_collection.query(prompt, top_k=3)
            if not retrieved:
                return prompt

            # Format retrieved context
            context_parts = []
            for result in retrieved:
                context_parts.append(result.get("text", ""))

            context_str = "\n---\n".join(context_parts)

            # Inject into prompt
            enhanced_prompt = f"""Context from knowledge base:
---
{context_str}
---

User query: {prompt}"""
            logger.debug(
                f"Injected RAG context for agent '{self.name}': "
                f"retrieved {len(retrieved)} chunks"
            )
            return enhanced_prompt

        except Exception as e:
            logger.warning(f"Error retrieving RAG context: {e}")
            return prompt

    def run(self, prompt: str, reset: bool = True) -> str:
        """
        Execute prompt through agent with optional token budget protection.

        Args:
            prompt: User input
            reset: If True, reset memory before running. If False, preserve memory
                   for multi-turn conversations. Default True for backwards compatibility.

        Returns:
            Agent response string

        Raises:
            ValueError: If prompt exceeds token budget
        """
        # Inject RAG context if collection is connected
        prompt_with_context = self._inject_rag_context(prompt)

        # Apply user_prompt_template if set
        if self.user_prompt_template:
            formatted_prompt = self._render_template(self.user_prompt_template, user_input=prompt_with_context)
            logger.debug(
                f"Applied user_prompt_template to agent '{self.name}': "
                f"{prompt[:30]}... -> {formatted_prompt[:50]}..."
            )
        else:
            formatted_prompt = prompt_with_context

        # Token budget guard: check prompt size before sending to LLM
        # Include system role + user prompt in token count
        if self.token_budget is not None:
            # Build full prompt including system role for accurate token counting
            full_prompt_for_counting = formatted_prompt
            if self.role:
                full_prompt_for_counting = self.role + "\n" + formatted_prompt

            prompt_tokens = estimate_tokens(full_prompt_for_counting)

            if prompt_tokens > self.token_budget:
                raise ValueError(
                    f"Token budget exceeded: prompt has {prompt_tokens} tokens "
                    f"but budget is {self.token_budget}"
                )

            if self.token_warning_threshold is not None and prompt_tokens > self.token_warning_threshold:
                logger.warning(
                    f"Agent '{self.name}' approaching token limit: "
                    f"{prompt_tokens}/{self.token_budget} tokens used"
                )

        logger.debug(
            f"Running prompt for agent '{self.name}': {formatted_prompt[:50]}... (reset={reset})"
        )
        result = self.agent.run(formatted_prompt, reset=reset)
        return str(result)

    def __repr__(self) -> str:
        """Return string representation of agent."""
        return f"SimpleAgent(name='{self.name}', provider='{self.model_provider}')"
