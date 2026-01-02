"""
CLI Common Utilities - EE CLI Gateway

This module provides common utilities and exceptions for the CLI gateway.
Includes error handling and shared utilities used across CLI components.

Based on:
D:\\Code\\Project\\Gateway\\CLI\\cli_common.py
"""

from __future__ import annotations


class CLIGatewayError(Exception):
    """Base error for CLI gateway failures.

    This exception is raised when CLI operations fail due to invalid input,
    execution errors, or other CLI-specific issues.

    Attributes:
        message: Human-readable error message

    Examples:
        >>> raise CLIGatewayError("Invalid route format")
        CLIGatewayError: Invalid route format

        >>> try:
        ...     executor.execute(args)
        ... except CLIGatewayError as e:
        ...     print(f"CLI Error: {e}")
        CLI Error: Invalid route format
    """

    pass


class CLIValidationError(CLIGatewayError):
    """Raised when CLI input validation fails.

    This exception is raised when user input does not meet expected format
    or contains invalid values.

    Examples:
        >>> raise CLIValidationError("Invalid JSON in payload")
        CLIValidationError: Invalid JSON in payload
    """

    pass


class CLIExecutionError(CLIGatewayError):
    """Raised when CLI command execution fails.

    This exception is raised when a command cannot be executed due to
    runtime errors, missing dependencies, or gateway failures.

    Examples:
        >>> raise CLIExecutionError("Domain 'config' not found")
        CLIExecutionError: Domain 'config' not found
    """

    pass


__all__ = [
    'CLIGatewayError',
    'CLIValidationError',
    'CLIExecutionError',
]
