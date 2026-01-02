"""
Template Factory - Operations Domain

Template operations and rendering implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside operations domain (except stdlib)
- All cross-domain calls via call_operation callback
"""

import re
import logging
from typing import Any, Dict, Optional, Callable


class TemplateFactory:
    """Template operations factory.

    Provides simple string template rendering with variable substitution.

    UG-ISP Compliance:
    - Factory contains actual implementation
    - Cross-domain calls via call_operation callback
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize template factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

        # Cache for compiled templates
        self._template_cache: Dict[str, str] = {}

    def render(self, template_str: str, context: Dict[str, Any], **kwargs) -> Optional[str]:
        """Render template with context.

        Args:
            template_str: Template string with {{variable}} placeholders
            context: Dictionary of variables to substitute
            **kwargs: Additional parameters

        Returns:
            Rendered string or None if error

        Example:
            factory.render("Hello {{name}}!", {"name": "World"})
            # Returns: "Hello World!"
        """
        try:
            result = template_str
            # Replace {{variable}} with context values
            for key, value in context.items():
                placeholder = f"{{{{{key}}}}}"
                result = result.replace(placeholder, str(value))

            return result
        except Exception as e:
            self.logger.error(f"Error rendering template: {e}")
            return None

    def compile(self, name: str, template_str: str, **kwargs) -> bool:
        """Compile and cache a template.

        Args:
            name: Template name for caching
            template_str: Template string to compile
            **kwargs: Additional parameters

        Returns:
            True if compiled successfully
        """
        try:
            self._template_cache[name] = template_str
            return True
        except Exception as e:
            self.logger.error(f"Error compiling template: {e}")
            return False

    def render_string(self, name: str, context: Dict[str, Any], **kwargs) -> Optional[str]:
        """Render a compiled template.

        Args:
            name: Compiled template name
            context: Dictionary of variables to substitute
            **kwargs: Additional parameters

        Returns:
            Rendered string or None if template not found or error
        """
        template_str = self._template_cache.get(name)
        if template_str is None:
            self.logger.warning(f"Template not found: {name}")
            return None

        return self.render(template_str, context, **kwargs)


__all__ = [
    "TemplateFactory",
]
