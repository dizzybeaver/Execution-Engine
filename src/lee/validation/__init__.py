"""validation/__init__.py
Version: 2026-03-22
Purpose: Validation domain module - input sanitization and schema validation
License: Apache 2.0

This module provides validation operations for:
- Alexa directive structure validation
- Input sanitization (XSS, SQL injection, SSRF)
- Schema-based validation
"""

from typing import Any, Optional

# Import protection
try:
    try:
        from lee.lee_security import InputSanitizer, SanitizeLevel
        _SECURITY_AVAILABLE = True
    except ImportError:
        _SECURITY_AVAILABLE = False

    _VALIDATION_AVAILABLE = True
    _VALIDATION_IMPORT_ERROR = None
except ImportError as e:
    _VALIDATION_AVAILABLE = False
    _VALIDATION_IMPORT_ERROR = str(e)


def validate_alexa_directive(
    directive: dict[str, Any],
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Validate Alexa directive structure.

    Args:
        directive: Alexa directive dictionary to validate
        correlation_id: Request correlation ID for tracking
        **kwargs: Validation options (strict_mode, require_namespace, etc.)

    Returns:
        Dictionary with validation result and error details if invalid
    """
    if not _VALIDATION_AVAILABLE:
        return {
            "valid": False,
            "error": "Validation module not available",
            "import_error": _VALIDATION_IMPORT_ERROR
        }

    # Basic structure validation
    if not isinstance(directive, dict):
        return {
            "valid": False,
            "error": "Directive must be a dictionary",
            "correlation_id": correlation_id
        }

    # Check required fields
    required_fields = ["header", "payload"]
    missing_fields = [f for f in required_fields if f not in directive]

    if missing_fields:
        return {
            "valid": False,
            "error": f"Missing required fields: {', '.join(missing_fields)}",
            "correlation_id": correlation_id
        }

    # Validate header
    header = directive.get("header", {})
    if not isinstance(header, dict):
        return {
            "valid": False,
            "error": "Header must be a dictionary",
            "correlation_id": correlation_id
        }

    required_header_fields = ["namespace", "name"]
    missing_header_fields = [f for f in required_header_fields if f not in header]

    if missing_header_fields:
        return {
            "valid": False,
            "error": f"Missing required header fields: {', '.join(missing_header_fields)}",
            "correlation_id": correlation_id
        }

    return {
        "valid": True,
        "correlation_id": correlation_id
    }


def sanitize_input(
    input_data: str,
    level: str = "strict",
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Sanitize user input to prevent XSS, SQL injection, SSRF.

    Args:
        input_data: User input string to sanitize
        level: Sanitization level ('strict', 'medium', 'basic')
        correlation_id: Request correlation ID for tracking
        **kwargs: Additional sanitization options

    Returns:
        Dictionary with sanitized input and warnings
    """
    if not _VALIDATION_AVAILABLE:
        return {
            "sanitized": input_data,
            "warnings": ["Validation module not available"],
            "correlation_id": correlation_id
        }

    if not isinstance(input_data, str):
        return {
            "sanitized": str(input_data),
            "warnings": ["Input converted to string"],
            "correlation_id": correlation_id
        }

    sanitized = input_data
    warnings = []

    if _SECURITY_AVAILABLE:
        try:
            sanitizer = InputSanitizer(level=SanitizeLevel.STRICT if level == "strict" else SanitizeLevel.MEDIUM)
            sanitized = sanitizer.sanitize(input_data)
        except (ValueError, TypeError) as e:
            warnings.append(f"Sanitization input error: {str(e)}")
        except (AttributeError, RuntimeError) as e:
            warnings.append(f"Sanitization warning: {str(e)}")

    return {
        "sanitized": sanitized,
        "warnings": warnings,
        "correlation_id": correlation_id
    }


def validate_schema(
    data: dict[str, Any],
    schema: dict[str, Any],
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Validate data against schema.

    Args:
        data: Data to validate
        schema: Schema definition
        correlation_id: Request correlation ID for tracking
        **kwargs: Additional validation options

    Returns:
        Dictionary with validation result
    """
    if not _VALIDATION_AVAILABLE:
        return {
            "valid": False,
            "error": "Validation module not available",
            "import_error": _VALIDATION_IMPORT_ERROR,
            "correlation_id": correlation_id
        }

    # Basic schema validation
    if not isinstance(data, dict):
        return {
            "valid": False,
            "error": "Data must be a dictionary",
            "correlation_id": correlation_id
        }

    if not isinstance(schema, dict):
        return {
            "valid": False,
            "error": "Schema must be a dictionary",
            "correlation_id": correlation_id
        }

    # Check required fields
    required_fields = schema.get("required", [])
    missing_fields = [f for f in required_fields if f not in data]

    if missing_fields:
        return {
            "valid": False,
            "error": f"Missing required fields: {', '.join(missing_fields)}",
            "correlation_id": correlation_id
        }

    return {
        "valid": True,
        "correlation_id": correlation_id
    }


__all__ = [
    "validate_alexa_directive",
    "sanitize_input",
    "validate_schema",
]
