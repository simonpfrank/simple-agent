"""
SimpleAgent - Thin wrapper around SmolAgents with support for multiple agent types.

Provides a simplified interface for creating and running agents with LiteLLM support.
Supports ToolCallingAgent (default, safe), CodeAgent (with Docker), and MultiStepAgent.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Literal, Optional, Union

from jinja2 import BaseLoader, TemplateError
from jinja2.sandbox import SandboxedEnvironment
from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel
from smolagents.monitoring import LogLevel

from simple_agent.core.config_manager import ConfigManager
from simple_agent.tools.helpers.token_counter import estimate_tokens
from simple_agent.tools.helpers.model_pricing import calculate_cost
from simple_agent.core.agent_result import AgentResult
from simple_agent.core.token_budget_context import TokenBudgetContext
from simple_agent.agents.agent_config import AgentConfig
from simple_agent.core.rate_limit_tracker import rate_limit_tracker
from decimal import Decimal

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
        2. With individual parameters (backward compatible): SimpleAgent(name="test", model_provider="openai", ...)

        Args:
            name: Agent identifier or AgentConfig object (if first positional arg)
            model_provider: "openai", "ollama", etc.
            model_config: Dict with model settings
            role: Optional system prompt/persona
            tools: List of tool instances
            verbosity: 0=quiet, 1=normal, 2=verbose (DEPRECATED - use debug_level)
            max_steps: Max tool call iterations
            agent_type: Agent type - "tool_calling" (safe, default) or "code" (requires Docker)
            executor_type: Executor for code agent - "docker" (default), "e2b", "modal", "wasm"
            debug_enabled: Enable debug mode (DEPRECATED - use debug_level)
            debug_level: Verbosity level for smolagents ("off", "info", "debug")
            user_prompt_template: Optional template to wrap user input. Use {user_input} placeholder.
            token_budget: Hard limit on input prompt size (prevents rate limit hits)
            token_warning_threshold: Soft warning threshold before token_budget

        Raises:
            ValueError: If invalid parameters or attempting to use unsafe executor
            TypeError: If parameters have incorrect types
        """
        # Support both AgentConfig object and individual parameters
        logger.info(f"Initialising agent: {name}")
        if isinstance(name, AgentConfig):
            logger.debug("From config")
            config = name
        else:
            # Build config from individual parameters
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

        # Validate configuration
        config.validate()

        # Store configuration values as instance attributes
        self.name = config.name
        self.model_provider = config.model_provider
        self.model_config = config.model_config  # Store model config for token tracking
        self.agent_type = config.agent_type
        self.debug_enabled = config.debug_enabled
        self.debug_level = config.debug_level
        self.tools = config.tools or []  # Store tools list for access
        self.verbosity = config.verbosity
        self.max_steps = config.max_steps
        self.user_prompt_template = config.user_prompt_template
        self.rag_collection = (
            None  # Connected RAG collection (set via set_rag_collection)
        )
        self.token_budget = config.token_budget
        self.token_warning_threshold = config.token_warning_threshold

        # Rate limit tracking (populated from API response headers)
        self.last_tpm_limit: Optional[int] = None
        self.last_rpm_limit: Optional[int] = None
        self.last_tpm_remaining: Optional[int] = None
        self.last_rpm_remaining: Optional[int] = None

        # Render role template if it contains Jinja2 syntax
        if config.role:
            self.role: Optional[str] = self._render_template(config.role, user_input=None)
        else:
            self.role = config.role

        # Create LiteLLM model instance
        model_provider = config.model_provider or "litellm/openai"  # Default provider
        self.model = self._create_model(model_provider, config.model_config)

        # Map debug_level to SmolAgents LogLevel
        # LogLevel: OFF=-1, ERROR=0, INFO=1, DEBUG=2
        level_map = {"off": LogLevel.ERROR, "info": LogLevel.INFO, "debug": LogLevel.DEBUG}
        verbosity_level = level_map.get(config.debug_level, LogLevel.ERROR)
        logger.debug(
            f"Agent '{config.name}' verbosity set to {verbosity_level.name} "
            f"(debug_level={config.debug_level})"
        )

        # Suppress LiteLLM console output (it writes directly to stdout)
        # Only show LiteLLM output in debug mode
        import litellm
        if config.debug_level != "debug":
            litellm.set_verbose = False
            litellm.suppress_debug_info = True
        # Also configure Python logging for LiteLLM to file only
        for logger_name in ["LiteLLM", "httpx"]:
            lib_logger = logging.getLogger(logger_name)
            lib_logger.propagate = False  # Don't propagate to root (console)
            if not any(isinstance(h, logging.FileHandler) for h in lib_logger.handlers):
                for handler in logging.getLogger().handlers:
                    if isinstance(handler, logging.FileHandler):
                        lib_logger.addHandler(handler)
                        break

        # Create appropriate agent type
        # SmolAgents accepts tools as a list during initialization
        if config.agent_type == "tool_calling":
            self.agent = ToolCallingAgent(
                tools=config.tools or [],
                model=self.model,
                max_steps=config.max_steps,
                instructions=config.role,
                verbosity_level=verbosity_level,
            )
            logger.info(
                f"Created ToolCallingAgent: {self.name} ({config.model_provider})"
            )
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

    def _build_context(self, user_input: Optional[str] = None) -> Dict[str, Any]:
        """
        Build Jinja2 template context with all available variables.

        Args:
            user_input: Optional user input for user_prompt_template rendering

        Returns:
            Dict with context variables for template rendering
        """
        logger.debug("Building context")
        context = {
            "agent_name": self.name,
            "current_time": datetime.now(),
            "current_date": datetime.now().date(),
            "verbosity": self.verbosity,
            "max_steps": self.max_steps,
            "model_provider": self.model_provider,
            "tools": (
                [getattr(t, "name", str(t)) for t in self.tools] if self.tools else []
            ),
        }

        # Add user_input if provided (for user_prompt_template)
        if user_input is not None:
            context["user_input"] = user_input

        return context

    def _get_jinja_env(self) -> SandboxedEnvironment:
        """Get configured Jinja2 sandboxed environment (cached).

        Uses SandboxedEnvironment for security - prevents template injection
        attacks by restricting access to dangerous attributes and methods.
        """
        if not hasattr(self, "_jinja_env"):
            self._jinja_env = SandboxedEnvironment(
                loader=BaseLoader(),
                autoescape=False,  # Not rendering HTML
                trim_blocks=True,
                lstrip_blocks=True,
            )
        return self._jinja_env

    def _is_jinja_template(self, template: str) -> bool:
        """Check if template uses Jinja2 syntax."""
        return "{{" in template or "{%" in template or "{#" in template

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
        logging.debug("Rendering template")
        context = self._build_context(user_input)

        # Auto-detect template type
        if self._is_jinja_template(template):
            # Jinja2 template detected
            try:
                jinja_env = self._get_jinja_env()
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

        Raises:
            ValueError: If required model configuration is missing
        """
        logger.info("Creating LiteLLM Model")
        model_id = config.get("model")
        if not model_id:
            # Log warning instead of raising to maintain backward compatibility
            # Tests and some integrations may use empty configs
            logger.warning(
                f"No 'model' key in config for provider '{provider}'. "
                f"Config keys: {list(config.keys())}. Using provider name as fallback."
            )
            model_id = provider  # Use provider name as fallback

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
            logger.info("Ollama")
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
            logger.info("OpenAI")
            return LiteLLMModel(
                model_id=model_id,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        elif provider == "Anthropic":
            # Anthropic models - resolve API key from env var at point-of-use
            logger.info("Anthropic")
            api_key = config.get("api_key", "")
            api_key = ConfigManager.resolve_env_var(api_key)
            return LiteLLMModel(
                model_id=model_id,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        elif provider == "azure_openai":
            # Azure OpenAI with Azure AD or API key authentication
            logger.info("Azure OpenAI")
            azure_endpoint = config.get("azure_endpoint")
            api_version = config.get("api_version", "2024-02-01")

            if not azure_endpoint:
                raise ValueError("azure_endpoint is required for azure_openai provider")

            # Resolve environment variables if present
            azure_endpoint = ConfigManager.resolve_env_var(azure_endpoint)

            # Check authentication type
            auth_type = config.get("auth_type", "azure_ad")

            if auth_type == "azure_ad":
                # Azure AD authentication (recommended for enterprise)
                try:
                    from azure.identity import (
                        DefaultAzureCredential,
                        get_bearer_token_provider,
                    )

                    logger.info("Using Azure AD authentication for Azure OpenAI")

                    # Create token provider and get token
                    credential = DefaultAzureCredential()
                    token_provider = get_bearer_token_provider(
                        credential, f"{azure_endpoint}/.default"
                    )

                    # Get the actual token (LiteLLM doesn't support token_provider callable)
                    azure_ad_token = token_provider()

                    # Enable dropping unsupported params for older Azure API versions
                    import litellm

                    litellm.drop_params = True

                    logger.debug(
                        f"Created Azure OpenAI model - endpoint: {azure_endpoint}, "
                        f"model: {model_id}, api_version: {api_version}"
                    )

                    return LiteLLMModel(
                        model_id=f"azure/{model_id}",
                        api_base=azure_endpoint,
                        api_version=api_version,
                        azure_ad_token=azure_ad_token,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                except ImportError as e:
                    raise ValueError(
                        "Azure AD authentication requires 'azure-identity' package. "
                        f"Install it with: pip install azure-identity. Error: {e}"
                    )
                except Exception as e:
                    logger.error(f"Azure AD authentication failed: {e}")
                    raise ValueError(
                        f"Failed to authenticate with Azure AD: {e}. "
                        "Ensure you have valid Azure credentials configured "
                        "(run 'az login' or set environment variables)."
                    )
            else:
                # API Key authentication (fallback)
                api_key = config.get("api_key", "")
                if not api_key:
                    raise ValueError(
                        "api_key is required when auth_type is not 'azure_ad'"
                    )

                api_key = ConfigManager.resolve_env_var(api_key)

                logger.debug(
                    f"Created Azure OpenAI model with API key - endpoint: {azure_endpoint}, "
                    f"model: {model_id}, api_version: {api_version}"
                )

                return LiteLLMModel(
                    model_id=f"azure/{model_id}",
                    api_base=azure_endpoint,
                    api_key=api_key,
                    api_version=api_version,
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
            error_type = type(e).__name__
            logger.error(
                f"Failed to inject RAG context for agent '{self.name}': "
                f"{error_type}: {e}. Proceeding without RAG context.",
                exc_info=True,
            )
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
        Execute prompt through agent with optional token budget protection and tracking.

        Args:
            prompt: User input
            reset: If True, reset memory before running. If False, preserve memory
                   for multi-turn conversations. Default True for backwards compatibility.
            track_tokens: If True, track and return token statistics. Default True.
            token_budget_override: Optional override for agent's token_budget. Used by
                                  orchestration/automation systems to control sub-agent budgets.
            token_warning_threshold_override: Optional override for token_warning_threshold.

        Returns:
            AgentResult with response and token statistics. If an error occurs,
            result.error and result.error_type will be populated.

        Raises:
            ValueError: If prompt exceeds token budget (hard limit, not caught)
        """
        logger.info("Agent run")
        input_tokens = 0
        output_tokens = 0
        cost = Decimal("0")

        # Determine effective budget and warning threshold (use overrides if provided)
        effective_budget = (
            token_budget_override
            if token_budget_override is not None
            else self.token_budget
        )
        effective_warning_threshold = (
            token_warning_threshold_override
            if token_warning_threshold_override is not None
            else self.token_warning_threshold
        )
        logger.debug(
            f"Budget:{effective_budget}, Warning:{effective_warning_threshold}"
        )

        # Inject RAG context if collection is connected
        logger.debug("Injecting rag if any")
        prompt_with_context = self._inject_rag_context(prompt)

        # Apply user_prompt_template if set
        if self.user_prompt_template:
            logger.debug("rendering user template")
            formatted_prompt = self._render_template(
                self.user_prompt_template, user_input=prompt_with_context
            )
            logger.debug(
                f"Applied user_prompt_template to agent '{self.name}': "
                f"{prompt[:30]}... -> {formatted_prompt[:50]}..."
            )
        else:
            logger.debug("Not using user template")
            formatted_prompt = prompt_with_context

        # Inject budget context into user prompt if budget is set
        if effective_budget is not None:
            # Create budget context and prepend to user prompt
            budget_context = TokenBudgetContext(
                token_budget=effective_budget,
                tokens_used=0,  # At execution time, assume 0 tokens used initially
                warning_threshold=effective_warning_threshold,
            )
            budget_info = budget_context.to_prompt_string()
            formatted_prompt = f"{budget_info}\n\n{formatted_prompt}"

        # Estimate input tokens
        if track_tokens:
            # Build full prompt including system role for accurate token counting
            full_prompt_for_counting = formatted_prompt
            if self.role:
                full_prompt_for_counting = self.role + "\n" + formatted_prompt
            input_tokens = estimate_tokens(full_prompt_for_counting)
            logger.debug(f"Input tokens:{input_tokens}")

        # Token budget guard: check prompt size before sending to LLM
        # NOTE: Token budget errors RAISE (hard limit), not captured in try-except
        if effective_budget is not None:
            if input_tokens > effective_budget:
                raise ValueError(
                    f"Token budget exceeded: prompt has {input_tokens} tokens "
                    f"but budget is {effective_budget}"
                )

            if (
                effective_warning_threshold is not None
                and input_tokens > effective_warning_threshold
            ):
                logger.warning(
                    f"Agent '{self.name}' approaching token limit: "
                    f"{input_tokens}/{effective_budget} tokens used"
                )
        elif self.token_budget is not None:
            # Fallback to original self.token_budget if no override and we have token_budget
            if input_tokens > self.token_budget:
                raise ValueError(
                    f"Token budget exceeded: prompt has {input_tokens} tokens "
                    f"but budget is {self.token_budget}"
                )

            if (
                self.token_warning_threshold is not None
                and input_tokens > self.token_warning_threshold
            ):
                logger.warning(
                    f"Agent '{self.name}' approaching token limit: "
                    f"{input_tokens}/{self.token_budget} tokens used"
                )

        logger.debug(
            f"Running prompt for agent '{self.name}': {formatted_prompt[:50]}... (reset={reset})"
        )

        try:
            logger.debug("Sending prompt")
            response = self.agent.run(formatted_prompt, reset=reset)
            logger.debug("Response received")
            response_str = str(response)

            # Extract rate limit info from response headers (best effort)
            self._extract_rate_limits_from_response()

            logger.info(
                f"last tpm:{self.last_tpm_limit}, last rpm:{self.last_rpm_limit}, tpm remaining:{self.last_tpm_remaining}, rpm remaining:{self.last_rpm_remaining}"
            )
            # Also update global rate limit tracker
            model_name = self.model_config.get("model", "unknown")
            rate_limit_tracker.update_from_response(response, model_name)

            # Estimate output tokens and calculate cost
            if track_tokens:
                output_tokens = estimate_tokens(response_str)
                # Calculate cost based on model provider
                model_name = self.model_config.get("model", "unknown")
                cost = calculate_cost(model_name, input_tokens, output_tokens)

            # Return AgentResult with backward compatibility (works as string)
            logger.debug("Extracting result")
            return AgentResult.from_response(
                response=response_str,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                model=model_name,  # Use the validated model_name from above
            )

        except Exception as e:
            # Capture error information from LLM execution and other runtime errors
            # Note: Token budget errors are raised BEFORE try block
            error_message = str(e)
            error_type = type(e).__name__

            # Get model name with fallback for safety
            model_name = self.model_config.get("model", "unknown")

            # Special handling for rate limit errors (429)
            if self._is_rate_limit_error(error_type, error_message):
                # Clean rate limit error - no full traceback
                limit_info = self._format_rate_limit_error()
                logger.warning(f"[RATE LIMIT] {limit_info}")

                # Return AgentResult with concise error (no traceback in REPL)
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
                # Other errors - full logging with traceback
                logger.error(
                    f"Agent '{self.name}' execution failed with {error_type}: {error_message}",
                    exc_info=True,
                )

                # Return AgentResult with error information
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
        """
        Check if error is a rate limit error.

        Args:
            error_type: Exception type name
            error_message: Exception message

        Returns:
            True if this is a rate limit error (429)
        """
        rate_limit_indicators = [
            "RateLimitError",
            "429",
            "Rate limit",
            "Too Many Requests",
        ]
        return any(
            indicator in error_type or indicator in error_message
            for indicator in rate_limit_indicators
        )

    def _format_rate_limit_error(self) -> str:
        """
        Format rate limit error message with available limit information.

        Returns:
            Formatted error message with TPM/RPM limits if available
        """
        # Try instance limits first, then global tracker
        if self.last_tpm_limit is not None:
            # We have rate limit info from previous successful response
            return (
                f"Rate limit exceeded. "
                f"TPM: {self.last_tpm_remaining}/{self.last_tpm_limit}, "
                f"RPM: {self.last_rpm_remaining}/{self.last_rpm_limit}. "
                f"Wait 60 seconds and try again."
            )
        elif rate_limit_tracker.tpm_limit is not None:
            # Use global tracker data
            return (
                f"Rate limit exceeded. "
                f"{rate_limit_tracker.get_limits_str()}. "
                f"Wait 60 seconds and try again."
            )
        else:
            # No rate limit info captured yet
            return (
                "Rate limit exceeded. Limit details not available - "
                "enable debug logging to see full error. "
                "Wait 60 seconds and try again."
            )

    def _extract_rate_limits_from_response(self):
        """
        Extract rate limit information from last API response headers.

        This attempts to access response headers through the LiteLLM/OpenAI client.
        Rate limits are stored for use in error messages and logged separately.

        Note: This is best-effort - if headers aren't accessible, fails silently.
        """
        try:
            # Try to access response headers through Smolagents model wrapper
            if hasattr(self.agent, "model") and hasattr(self.agent.model, "_client"):
                # OpenAI client may store last response
                client = self.agent.model._client
                if hasattr(client, "_last_response"):
                    response = client._last_response
                    if hasattr(response, "headers"):
                        headers = response.headers

                        # Extract Azure rate limit headers
                        if "x-ratelimit-limit-tokens" in headers:
                            self.last_tpm_limit = int(
                                headers["x-ratelimit-limit-tokens"]
                            )
                        if "x-ratelimit-limit-requests" in headers:
                            self.last_rpm_limit = int(
                                headers["x-ratelimit-limit-requests"]
                            )
                        if "x-ratelimit-remaining-tokens" in headers:
                            self.last_tpm_remaining = int(
                                headers["x-ratelimit-remaining-tokens"]
                            )
                        if "x-ratelimit-remaining-requests" in headers:
                            self.last_rpm_remaining = int(
                                headers["x-ratelimit-remaining-requests"]
                            )

                        # Always log rate limits (INFO level, so visible even when azure.core is WARNING)
                        logger.info(
                            f"[RATE LIMITS] Agent '{self.name}' - "
                            f"TPM: {self.last_tpm_remaining}/{self.last_tpm_limit}, "
                            f"RPM: {self.last_rpm_remaining}/{self.last_rpm_limit}"
                        )
        except Exception as e:
            # Log extraction failure at debug level
            logger.debug(f"Failed to extract rate limits from response: {e}")

    def __repr__(self) -> str:
        """Return string representation of agent."""
        return f"SimpleAgent(name='{self.name}', provider='{self.model_provider}')"
