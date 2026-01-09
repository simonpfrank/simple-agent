"""
SimpleAgent - Thin wrapper around SmolAgents with support for multiple agent types.

Provides a simplified interface for creating and running agents with LiteLLM support.
Supports ToolCallingAgent (default, safe), CodeAgent (with Docker), and MultiStepAgent.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, Literal, Optional, Union

from smolagents import CodeAgent, ToolCallingAgent
from smolagents.monitoring import LogLevel

from simple_agent.agents.agent_config import AgentConfig
from simple_agent.agents.model_factory import create_litellm_model
from simple_agent.agents.template_renderer import TemplateRenderer
from simple_agent.core.agent_result import AgentResult
from simple_agent.core.rate_limit_tracker import rate_limit_tracker
from simple_agent.core.token_budget_context import TokenBudgetContext
from simple_agent.tools.helpers.model_pricing import calculate_cost
from simple_agent.tools.helpers.token_counter import estimate_tokens

logger = logging.getLogger(__name__)


class SimpleAgent:
    """Thin wrapper around SmolAgents with support for multiple agent types."""

    def __init__(
        self,
        name: Optional[Union[str, AgentConfig]] = None,
        model_provider: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
        role: Optional[str] = None,
        tools: Optional[list] = None,
        verbosity: int = 1,
        max_steps: int = 10,
        agent_type: Literal["tool_calling", "code"] = "tool_calling",
        executor_type: Literal["docker", "e2b", "modal", "wasm"] = "docker",
        debug_enabled: bool = False,
        debug_level: Literal["off", "info", "debug"] = "off",
        user_prompt_template: Optional[str] = None,
        token_budget: Optional[int] = None,
        token_warning_threshold: Optional[int] = None,
    ):
        """
        Initialize agent.

        Can be called in two ways:
        1. With AgentConfig object: SimpleAgent(config=AgentConfig(...))
        2. With individual parameters: SimpleAgent(name="test", model_provider="openai", ...)

        Args:
            name: Agent identifier or AgentConfig object
            model_provider: "openai", "ollama", etc.
            model_config: Dict with model settings
            role: Optional system prompt/persona
            tools: List of tool instances
            verbosity: 0=quiet, 1=normal, 2=verbose (DEPRECATED - use debug_level)
            max_steps: Max tool call iterations
            agent_type: "tool_calling" (safe, default) or "code" (requires Docker)
            executor_type: Executor for code agent - "docker", "e2b", "modal", "wasm"
            debug_enabled: Enable debug mode (DEPRECATED - use debug_level)
            debug_level: Verbosity level for smolagents ("off", "info", "debug")
            user_prompt_template: Optional template to wrap user input
            token_budget: Hard limit on input prompt size
            token_warning_threshold: Soft warning threshold before token_budget
        """
        logger.info(f"Initialising agent: {name}")
        if isinstance(name, AgentConfig):
            logger.debug("From config")
            config = name
        else:
            logger.debug("From parameters")
            config = AgentConfig(
                name=name or "default",
                model_provider=model_provider,
                model_config=model_config or {},
                role=role,
                tools=tools,
                verbosity=verbosity,
                max_steps=max_steps,
                agent_type=agent_type,
                executor_type=executor_type,
                debug_enabled=debug_enabled,
                debug_level=debug_level,
                user_prompt_template=user_prompt_template,
                token_budget=token_budget,
                token_warning_threshold=token_warning_threshold,
            )

        config.validate()

        # Store configuration
        self.name = config.name
        self.model_provider = config.model_provider
        self.model_config = config.model_config
        self.agent_type = config.agent_type
        self.debug_enabled = config.debug_enabled
        self.debug_level = config.debug_level
        self.tools = config.tools or []
        self.verbosity = config.verbosity
        self.max_steps = config.max_steps
        self.user_prompt_template = config.user_prompt_template
        self.rag_collection = None
        self.token_budget = config.token_budget
        self.token_warning_threshold = config.token_warning_threshold

        # Rate limit tracking
        self.last_tpm_limit: Optional[int] = None
        self.last_rpm_limit: Optional[int] = None
        self.last_tpm_remaining: Optional[int] = None
        self.last_rpm_remaining: Optional[int] = None

        # Template renderer
        self._template_renderer = TemplateRenderer()

        # Render role template if it contains Jinja2 syntax
        if config.role:
            context = self._template_renderer.build_context(
                self.name, self.model_provider, self.verbosity,
                self.max_steps, self.tools, None
            )
            self.role: Optional[str] = self._template_renderer.render(config.role, context)
        else:
            self.role = config.role

        # Create model using factory
        model_provider_str = config.model_provider or "litellm/openai"
        self.model = create_litellm_model(model_provider_str, config.model_config)

        # Configure verbosity
        level_map = {"off": LogLevel.ERROR, "info": LogLevel.INFO, "debug": LogLevel.DEBUG}
        verbosity_level = level_map.get(config.debug_level, LogLevel.ERROR)
        logger.debug(f"Agent '{config.name}' verbosity: {verbosity_level.name}")

        # Suppress LiteLLM console output
        self._configure_litellm_logging(config.debug_level)

        # Create agent
        self._create_smolagent(config, verbosity_level)

    def _configure_litellm_logging(self, debug_level: str) -> None:
        """Configure LiteLLM logging based on debug level."""
        import litellm
        if debug_level != "debug":
            litellm.set_verbose = False
            litellm.suppress_debug_info = True

        for logger_name in ["LiteLLM", "httpx"]:
            lib_logger = logging.getLogger(logger_name)
            lib_logger.propagate = False
            if not any(isinstance(h, logging.FileHandler) for h in lib_logger.handlers):
                for handler in logging.getLogger().handlers:
                    if isinstance(handler, logging.FileHandler):
                        lib_logger.addHandler(handler)
                        break

    def _create_smolagent(self, config: AgentConfig, verbosity_level: LogLevel) -> None:
        """Create the underlying SmolAgent."""
        if config.agent_type == "tool_calling":
            self.agent = ToolCallingAgent(
                tools=config.tools or [],
                model=self.model,
                max_steps=config.max_steps,
                instructions=config.role,
                verbosity_level=verbosity_level,
            )
            logger.info(f"Created ToolCallingAgent: {self.name} ({config.model_provider})")
        elif config.agent_type == "code":
            self.agent = CodeAgent(
                tools=config.tools or [],
                model=self.model,
                max_steps=config.max_steps,
                verbosity_level=verbosity_level,
                instructions=config.role,
                executor_type=config.executor_type,
            )
            logger.info(
                f"Created CodeAgent: {self.name} ({config.model_provider}) "
                f"with {config.executor_type} executor"
            )

    def set_rag_collection(self, collection: Optional[Any]) -> None:
        """Set the RAG collection for this agent."""
        self.rag_collection = collection

    def _inject_rag_context(self, prompt: str) -> str:
        """Inject RAG context into prompt if collection is connected."""
        if not self.rag_collection:
            return prompt

        try:
            retrieved = self.rag_collection.query(prompt, top_k=3)
            if not retrieved:
                return prompt

            context_parts = [result.get("text", "") for result in retrieved]
            context_str = "\n---\n".join(context_parts)

            enhanced_prompt = f"""Context from knowledge base:
---
{context_str}
---

User query: {prompt}"""
            logger.debug(f"Injected RAG context: {len(retrieved)} chunks")
            return enhanced_prompt

        except Exception as e:
            logger.error(f"Failed to inject RAG context: {e}", exc_info=True)
            return prompt

    def run(
        self,
        prompt: str,
        reset: bool = True,
        track_tokens: bool = True,
        token_budget_override: int | None = None,
        token_warning_threshold_override: int | None = None,
    ) -> AgentResult:
        """
        Execute prompt through agent with optional token budget protection.

        Args:
            prompt: User input
            reset: If True, reset memory before running
            track_tokens: If True, track and return token statistics
            token_budget_override: Optional override for agent's token_budget
            token_warning_threshold_override: Optional override for warning threshold

        Returns:
            AgentResult with response and token statistics
        """
        logger.info("Agent run")
        input_tokens = 0
        output_tokens = 0
        cost = Decimal("0")

        # Determine effective budget
        effective_budget = token_budget_override if token_budget_override is not None else self.token_budget
        effective_warning = token_warning_threshold_override if token_warning_threshold_override is not None else self.token_warning_threshold

        # Process prompt
        prompt_with_context = self._inject_rag_context(prompt)
        formatted_prompt = self._apply_user_template(prompt_with_context)
        formatted_prompt = self._apply_budget_context(formatted_prompt, effective_budget, effective_warning)

        # Estimate tokens
        if track_tokens:
            full_prompt = (self.role + "\n" + formatted_prompt) if self.role else formatted_prompt
            input_tokens = estimate_tokens(full_prompt)

        # Check token budget
        self._check_token_budget(input_tokens, effective_budget, effective_warning)

        logger.debug(f"Running prompt for agent '{self.name}': {formatted_prompt[:50]}...")

        try:
            response = self.agent.run(formatted_prompt, reset=reset)
            response_str = str(response)

            self._extract_rate_limits_from_response()
            logger.info(
                f"last tpm:{self.last_tpm_limit}, last rpm:{self.last_rpm_limit}, "
                f"tpm remaining:{self.last_tpm_remaining}, rpm remaining:{self.last_rpm_remaining}"
            )

            model_name = self.model_config.get("model", "unknown")
            rate_limit_tracker.update_from_response(response, model_name)

            if track_tokens:
                output_tokens = estimate_tokens(response_str)
                cost = calculate_cost(model_name, input_tokens, output_tokens)

            return AgentResult.from_response(
                response=response_str,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                model=model_name,
            )

        except Exception as e:
            return self._handle_run_error(e, input_tokens, output_tokens, cost)

    def _apply_user_template(self, prompt: str) -> str:
        """Apply user prompt template if configured."""
        if not self.user_prompt_template:
            return prompt

        context = self._template_renderer.build_context(
            self.name, self.model_provider, self.verbosity,
            self.max_steps, self.tools, prompt
        )
        formatted = self._template_renderer.render(self.user_prompt_template, context)
        logger.debug(f"Applied user_prompt_template: {prompt[:30]}... -> {formatted[:50]}...")
        return formatted

    def _apply_budget_context(
        self, prompt: str, budget: Optional[int], warning: Optional[int]
    ) -> str:
        """Inject budget context into prompt if budget is set."""
        if budget is None:
            return prompt

        budget_context = TokenBudgetContext(
            token_budget=budget,
            tokens_used=0,
            warning_threshold=warning,
        )
        return f"{budget_context.to_prompt_string()}\n\n{prompt}"

    def _check_token_budget(
        self, input_tokens: int, budget: Optional[int], warning: Optional[int]
    ) -> None:
        """Check prompt against token budget and warn if approaching limit."""
        if budget is None:
            return

        if input_tokens > budget:
            raise ValueError(
                f"Token budget exceeded: prompt has {input_tokens} tokens "
                f"but budget is {budget}"
            )

        if warning is not None and input_tokens > warning:
            logger.warning(
                f"Agent '{self.name}' approaching token limit: "
                f"{input_tokens}/{budget} tokens used"
            )

    def _handle_run_error(
        self, e: Exception, input_tokens: int, output_tokens: int, cost: Decimal
    ) -> AgentResult:
        """Handle errors during agent run."""
        error_message = str(e)
        error_type = type(e).__name__
        model_name = self.model_config.get("model", "unknown")

        if self._is_rate_limit_error(error_type, error_message):
            limit_info = self._format_rate_limit_error()
            logger.warning(f"[RATE LIMIT] {limit_info}")
            return AgentResult.from_response(
                response="",
                input_tokens=input_tokens,
                output_tokens=0,
                cost=Decimal("0"),
                model=model_name,
                error=limit_info,
                error_type="RateLimitError",
            )
        else:
            logger.error(f"Agent '{self.name}' failed: {error_type}: {error_message}", exc_info=True)
            return AgentResult.from_response(
                response="",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                model=model_name,
                error=error_message,
                error_type=error_type,
            )

    def _is_rate_limit_error(self, error_type: str, error_message: str) -> bool:
        """Check if error is a rate limit error."""
        indicators = ["RateLimitError", "429", "Rate limit", "Too Many Requests"]
        return any(i in error_type or i in error_message for i in indicators)

    def _format_rate_limit_error(self) -> str:
        """Format rate limit error message with available limit information."""
        if self.last_tpm_limit is not None:
            return (
                f"Rate limit exceeded. "
                f"TPM: {self.last_tpm_remaining}/{self.last_tpm_limit}, "
                f"RPM: {self.last_rpm_remaining}/{self.last_rpm_limit}. "
                f"Wait 60 seconds and try again."
            )
        elif rate_limit_tracker.tpm_limit is not None:
            return (
                f"Rate limit exceeded. "
                f"{rate_limit_tracker.get_limits_str()}. "
                f"Wait 60 seconds and try again."
            )
        else:
            return (
                "Rate limit exceeded. Limit details not available - "
                "enable debug logging to see full error. "
                "Wait 60 seconds and try again."
            )

    def _extract_rate_limits_from_response(self) -> None:
        """Extract rate limit information from last API response headers."""
        try:
            if hasattr(self.agent, "model") and hasattr(self.agent.model, "_client"):
                client = self.agent.model._client
                if hasattr(client, "_last_response"):
                    response = client._last_response
                    if hasattr(response, "headers"):
                        headers = response.headers
                        if "x-ratelimit-limit-tokens" in headers:
                            self.last_tpm_limit = int(headers["x-ratelimit-limit-tokens"])
                        if "x-ratelimit-limit-requests" in headers:
                            self.last_rpm_limit = int(headers["x-ratelimit-limit-requests"])
                        if "x-ratelimit-remaining-tokens" in headers:
                            self.last_tpm_remaining = int(headers["x-ratelimit-remaining-tokens"])
                        if "x-ratelimit-remaining-requests" in headers:
                            self.last_rpm_remaining = int(headers["x-ratelimit-remaining-requests"])

                        logger.info(
                            f"[RATE LIMITS] Agent '{self.name}' - "
                            f"TPM: {self.last_tpm_remaining}/{self.last_tpm_limit}, "
                            f"RPM: {self.last_rpm_remaining}/{self.last_rpm_limit}"
                        )
        except Exception as e:
            logger.debug(f"Failed to extract rate limits: {e}")

    def __repr__(self) -> str:
        """Return string representation of agent."""
        return f"SimpleAgent(name='{self.name}', provider='{self.model_provider}')"
