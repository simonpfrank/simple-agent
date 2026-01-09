"""
Template rendering for agent prompts.

Supports both Jinja2 templates and simple format strings.
Uses SandboxedEnvironment for security against template injection.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from jinja2 import BaseLoader, TemplateError
from jinja2.sandbox import SandboxedEnvironment

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Renders Jinja2 and format string templates for agent prompts.

    Uses SandboxedEnvironment for security - prevents template injection
    attacks by restricting access to dangerous attributes and methods.
    """

    def __init__(self):
        """Initialize template renderer with sandboxed Jinja2 environment."""
        self._jinja_env: Optional[SandboxedEnvironment] = None

    def _get_jinja_env(self) -> SandboxedEnvironment:
        """Get configured Jinja2 sandboxed environment (cached)."""
        if self._jinja_env is None:
            self._jinja_env = SandboxedEnvironment(
                loader=BaseLoader(),
                autoescape=False,  # Not rendering HTML
                trim_blocks=True,
                lstrip_blocks=True,
            )
        return self._jinja_env

    @staticmethod
    def is_jinja_template(template: str) -> bool:
        """Check if template uses Jinja2 syntax.

        Args:
            template: Template string to check

        Returns:
            True if template contains Jinja2 syntax markers
        """
        return "{{" in template or "{%" in template or "{#" in template

    def build_context(
        self,
        agent_name: str,
        model_provider: Optional[str],
        verbosity: int,
        max_steps: int,
        tools: Optional[List[Any]],
        user_input: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build Jinja2 template context with all available variables.

        Args:
            agent_name: Name of the agent
            model_provider: LLM provider name
            verbosity: Agent verbosity level
            max_steps: Maximum steps for agent
            tools: List of agent tools
            user_input: Optional user input for user_prompt_template rendering

        Returns:
            Dict with context variables for template rendering
        """
        logger.debug("Building template context")
        context: Dict[str, Any] = {
            "agent_name": agent_name,
            "current_time": datetime.now(),
            "current_date": datetime.now().date(),
            "verbosity": verbosity,
            "max_steps": max_steps,
            "model_provider": model_provider,
            "tools": (
                [getattr(t, "name", str(t)) for t in tools] if tools else []
            ),
        }

        if user_input is not None:
            context["user_input"] = user_input

        return context

    def render(
        self,
        template: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Render template with Jinja2 or simple format string.

        Auto-detects template type based on syntax:
        - Jinja2: {{ }}, {% %}, or {# #}
        - Format string: {variable_name}

        Args:
            template: Template string to render
            context: Context variables for rendering

        Returns:
            Rendered template string

        Raises:
            ValueError: If Jinja2 template has invalid syntax
        """
        logger.debug("Rendering template")

        if self.is_jinja_template(template):
            # Jinja2 template detected
            try:
                jinja_env = self._get_jinja_env()
                jinja_template = jinja_env.from_string(template)
                rendered = jinja_template.render(**context)
                return rendered.rstrip()
            except TemplateError as e:
                raise ValueError(f"Jinja2 template error: {e}")
        else:
            # Simple format string (backward compatibility)
            try:
                return template.format(**context)
            except KeyError:
                # If format() fails due to missing keys, return template as-is
                return template
