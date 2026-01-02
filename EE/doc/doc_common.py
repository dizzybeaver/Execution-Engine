"""
Doc Common Utilities - EE Doc Gateway

This module provides common utilities and exceptions for the documentation gateway.
Includes error handling and shared utilities used across documentation components.

Based on:
D:\\Code\\Project\\Gateway\\Doc\\doc_common.py
"""

from __future__ import annotations


class DocGatewayError(Exception):
    """Base error for documentation gateway failures.

    This exception is raised when documentation operations fail due to invalid input,
    generation errors, or other documentation-specific issues.

    Attributes:
        message: Human-readable error message

    Examples:
        >>> raise DocGatewayError("Failed to generate documentation")
        DocGatewayError: Failed to generate documentation

        >>> try:
        ...     generator.generate()
        ... except DocGatewayError as e:
        ...     print(f"Documentation Error: {e}")
        Documentation Error: Failed to generate documentation
    """

    pass


class DocValidationError(DocGatewayError):
    """Raised when documentation input validation fails.

    This exception is raised when documentation generation parameters do not meet
    expected format or contain invalid values.

    Examples:
        >>> raise DocValidationError("Invalid route format")
        DocValidationError: Invalid route format
    """

    pass


class DocGenerationError(DocGatewayError):
    """Raised when documentation generation fails.

    This exception is raised when documentation cannot be generated due to
    runtime errors, missing dependencies, or template failures.

    Examples:
        >>> raise DocGenerationError("Template not found")
        DocGenerationError: Template not found
    """

    pass


class DocFormatError(DocGatewayError):
    """Raised when documentation formatting fails.

    This exception is raised when documentation output cannot be formatted
    correctly for the requested output format (Markdown, HTML, etc.).

    Examples:
        >>> raise DocFormatError("Unsupported output format: PDF")
        DocFormatError: Unsupported output format: PDF
    """

    pass


__all__ = [
    'DocGatewayError',
    'DocValidationError',
    'DocGenerationError',
    'DocFormatError',
]
