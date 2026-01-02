"""
CLI Output - EE CLI Gateway Output Renderer

This module handles output formatting for CLI commands.
Supports both human-readable text output and machine-readable JSON output.

Based on:
D:\\Code\\Project\\Gateway\\CLI\\cli_output.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from EE.cli.cli_common import CLIGatewayError


@dataclass
class CLIOutputRenderer:
    """CLI output renderer with support for multiple formats.

    This class formats command results for display, supporting both
    human-readable text and machine-readable JSON formats.

    Attributes:
        json_output: If True, format output as JSON; otherwise use pretty text

    Examples:
        >>> # Text output
        >>> renderer = CLIOutputRenderer(json_output=False)
        >>> print(renderer.render({"status": "ok", "value": 42}))
        status: ok
        value: 42

        >>> # JSON output
        >>> renderer = CLIOutputRenderer(json_output=True)
        >>> print(renderer.render({"status": "ok", "value": 42}))
        {
          "status": "ok",
          "value": 42
        }

        >>> # Error rendering
        >>> renderer.render_error(ValueError("Invalid input"))
        'ERROR: Invalid input'
    """

    json_output: bool = False

    def render(self, result: Any) -> str:
        """Render command result for display.

        Args:
            result: The result to render (can be any type)

        Returns:
            Formatted string representation of the result

        Examples:
            >>> renderer = CLIOutputRenderer(json_output=False)
            >>> renderer.render("simple string")
            'simple string'

            >>> renderer.render({"key": "value", "number": 42})
            'key: value\\nnumber: 42'

            >>> renderer = CLIOutputRenderer(json_output=True)
            >>> renderer.render({"key": "value"})
            '{\\n  "key": "value"\\n}'
        """
        if self.json_output:
            return self._render_json(result)
        return self._render_pretty(result)

    def render_error(self, error: Exception) -> str:
        """Render error message for display.

        Args:
            error: The exception to render

        Returns:
            Formatted error message string

        Examples:
            >>> renderer = CLIOutputRenderer(json_output=False)
            >>> renderer.render_error(ValueError("Invalid input"))
            'ERROR: Invalid input'

            >>> renderer = CLIOutputRenderer(json_output=True)
            >>> renderer.render_error(ValueError("Invalid input"))
            '{\\n  "error": "Invalid input"\\n}'
        """
        if self.json_output:
            return json.dumps({"error": str(error)}, indent=2)
        return f"ERROR: {error}"

    def _render_json(self, result: Any) -> str:
        """Render result as JSON.

        Args:
            result: The result to render

        Returns:
            JSON-formatted string

        Note:
            Uses custom serialization for types that aren't JSON-serializable
        """
        try:
            return json.dumps(result, indent=2, sort_keys=True, default=str)
        except Exception:
            # Fallback for non-serializable objects
            return json.dumps({"result": str(result)}, indent=2)

    def _render_pretty(self, result: Any) -> str:
        """Render result as human-readable text.

        Args:
            result: The result to render

        Returns:
            Pretty-printed text string
        """
        if isinstance(result, dict):
            return self._pretty_dict(result)
        elif isinstance(result, (list, tuple)):
            return self._pretty_list(result)
        else:
            return str(result)

    def _pretty_dict(self, d: dict, indent: int = 0) -> str:
        """Render dictionary as indented text.

        Args:
            d: Dictionary to render
            indent: Indentation level (0 = root level)

        Returns:
            Pretty-printed dictionary string
        """
        lines = []
        pad = "  " * indent

        for key, value in sorted(d.items()):
            if isinstance(value, dict):
                lines.append(f"{pad}{key}:")
                lines.append(self._pretty_dict(value, indent + 1))
            elif isinstance(value, (list, tuple)):
                lines.append(f"{pad}{key}:")
                lines.append(self._pretty_list(value, indent + 1))
            else:
                lines.append(f"{pad}{key}: {value}")

        return "\n".join(lines)

    def _pretty_list(self, lst: list, indent: int = 0) -> str:
        """Render list as indented text.

        Args:
            lst: List to render
            indent: Indentation level (0 = root level)

        Returns:
            Pretty-printed list string
        """
        if not lst:
            return "  " * indent + "(empty)"

        lines = []
        pad = "  " * indent

        for item in lst:
            if isinstance(item, dict):
                lines.append(f"{pad}-")
                lines.append(self._pretty_dict(item, indent + 1))
            elif isinstance(item, (list, tuple)):
                lines.append(f"{pad}-")
                lines.append(self._pretty_list(item, indent + 1))
            else:
                lines.append(f"{pad}- {item}")

        return "\n".join(lines)


__all__ = [
    'CLIOutputRenderer',
]
