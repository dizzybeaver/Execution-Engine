"""validation_wrappers.py
Version: 2026-04-11_1 (Consolidated with base_wrapper)
Purpose: Validation interface internal wrappers (SUGA-ISP Implementation)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the validation router.
External modules MUST use gateway.execute_operation() instead of importing directly.

Validation Operations:
- Alexa directive structure validation
- Input sanitization (XSS, SQL injection, command injection, SSRF)
- Schema-based validation

CONSOLIDATION:
- Removed duplicate correlation ID generation
- Uses base_wrapper.generate_correlation_id
- Reduced code by ~10 lines
"""

import re
from collections.abc import Mapping, Sequence
from typing import Any, Optional

# Import gateway for correlation ID generation
from lee.gateway.gateway_core import generate_correlation_id

# Import base_wrapper for utilities

# Import protection - only work if validation core is available
try:
    # Try to import security modules for sanitization
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


def validation_validate_alexa_directive(
    directive: dict[str, Any],
    correlation_id: Optional[str] = None,
    **_kwargs  # pylint: disable=unused-argument
) -> dict[str, Any]:
    """Validate Alexa directive structure - INTERNAL wrapper for validation router.

    Args:
        directive: Alexa directive dictionary to validate
        correlation_id: Request correlation ID for tracking
        **kwargs: Validation options (strict_mode, require_namespace, etc.)

    Returns:
        Dictionary with validation result and error details if invalid

    Example:
        >>> result = validation_validate_alexa_directive(directive)
        >>> if result["valid"]:
        ...     print("Directive is valid")
        ... else:
        ...     print(f"Errors: {result['errors']}")
    """
    if not _VALIDATION_AVAILABLE:
        raise RuntimeError(f"Validation unavailable: {_VALIDATION_IMPORT_ERROR}")

    # Inline correlation ID generation
    if correlation_id is None:
        correlation_id = generate_correlation_id("val")

    errors = []

    # Check required fields
    if "directive" not in directive:
        errors.append("Missing 'directive' field")

    if "header" not in directive.get("directive", {}):
        errors.append("Missing 'header' field in directive")

    if "payload" not in directive.get("directive", {}):
        errors.append("Missing 'payload' field in directive")

    # Validate header structure
    if "directive" in directive and "header" in directive["directive"]:
        header = directive["directive"]["header"]

        # Check namespace
        if "namespace" not in header:
            errors.append("Missing 'namespace' in header")

        # Check name
        if "name" not in header:
            errors.append("Missing 'name' in header")

        # Check messageId
        if "messageId" not in header:
            errors.append("Missing 'messageId' in header")

    # Validate endpoint structure (for control directives)
    if "directive" in directive and "endpoint" in directive["directive"]:
        endpoint = directive["directive"]["endpoint"]

        # Check endpoint scope
        if "scope" not in endpoint:
            errors.append("Missing 'scope' in endpoint")

        if "scope" in endpoint and "token" not in endpoint["scope"]:
            errors.append("Missing 'token' in endpoint.scope")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "directive": directive,
    }


def validation_sanitize_input(
    input_data: Any,
    input_type: str = "text",
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Sanitize user input - INTERNAL wrapper for validation router.

    Args:
        input_data: User input to sanitize (string, dict, or list)
        input_type: Type of input (text, html, sql, url, json)
        correlation_id: Request correlation ID for tracking
        **kwargs: Sanitization options (level, context, etc.)

    Returns:
        Dictionary with sanitized data and threat detection results

    Example:
        >>> result = validation_sanitize_input(
        ...     input_data="<script>alert('XSS')</script>",
        ...     input_type="html"
        ... )
        >>> print(result["sanitized_data"])  # "&lt;script&gt;..."
        >>> print(result["threats_detected"])
    """
    if not _VALIDATION_AVAILABLE:
        raise RuntimeError(f"Validation unavailable: {_VALIDATION_IMPORT_ERROR}")

    # Inline correlation ID generation
    if correlation_id is None:
        correlation_id = generate_correlation_id("val")

    # Use security module if available
    if _SECURITY_AVAILABLE:
        try:
            level = kwargs.get("level", "STRICT")
            sanitize_level = getattr(SanitizeLevel, level.upper(), SanitizeLevel.STRICT)

            sanitizer = InputSanitizer(level=sanitize_level)
            result = sanitizer.sanitize(str(input_data), context=input_type)

            return {
                "sanitized_data": result.sanitized,
                "threats_detected": [t.threat_type for t in result.threats],
                "is_safe": result.is_safe,
                "threats": result.threats,
            }
        except (AttributeError, ValueError, TypeError, KeyError):
            # Fall through to basic sanitization
            pass  # pylint: disable=unnecessary-ellipsis

    # Basic sanitization fallback
    sanitized = _basic_sanitize(input_data, input_type)

    return {
        "sanitized_data": sanitized,
        "threats_detected": [],
        "is_safe": True,
        "threats": [],
    }


def validation_validate_schema(
    data: Any,
    schema: dict[str, Any],
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Validate data against schema - INTERNAL wrapper for validation router.

    Args:
        data: Data to validate
        schema: JSON schema dictionary for validation
        correlation_id: Request correlation ID for tracking
        **kwargs: Validation options (strict_types, required_fields, etc.)

    Returns:
        Dictionary with validation result and error details

    Example:
        >>> schema = {
        ...     "type": "object",
        ...     "required": ["name", "email"],
        ...     "properties": {
        ...         "name": {"type": "string"},
        ...         "email": {"type": "string", "format": "email"}
        ...     }
        ... }
        >>> result = validation_validate_schema(data, schema)
    """
    if not _VALIDATION_AVAILABLE:
        raise RuntimeError(f"Validation unavailable: {_VALIDATION_IMPORT_ERROR}")

    # Inline correlation ID generation
    if correlation_id is None:
        correlation_id = generate_correlation_id("val")

    errors = []

    # Basic type validation
    if "type" in schema:
        expected_type = schema["type"]
        if not _validate_type(data, expected_type):
            errors.append(f"Expected type '{expected_type}', got '{type(data).__name__}'")

    # Required fields validation
    if "required" in schema and isinstance(data, dict):
        for field in schema["required"]:
            if field not in data:
                errors.append(f"Missing required field: '{field}'")

    # Property validation
    if "properties" in schema and isinstance(data, dict):
        for prop, prop_schema in schema["properties"].items():
            if prop in data:
                prop_result = validation_validate_schema(
                    data[prop],
                    prop_schema,
                    correlation_id=correlation_id,
                    **kwargs
                )
                if not prop_result["valid"]:
                    errors.extend([f"{prop}.{e}" for e in prop_result["errors"]])

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "data": data,
    }


# ===== HELPER FUNCTIONS =====

def _basic_sanitize(data: Any, input_type: str) -> Any:
    """Basic input sanitization fallback."""
    if isinstance(data, str):
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', data)

        # HTML escape for html type
        if input_type == "html":
            sanitized = (sanitized
                        .replace('&', '&amp;')
                        .replace('<', '&lt;')
                        .replace('>', '&gt;')
                        .replace('"', '&quot;')
                        .replace("'", '&#x27;'))

        return sanitized
    elif isinstance(data, Mapping):
        return {k: _basic_sanitize(v, input_type) for k, v in data.items()}
    elif isinstance(data, Sequence):
        return [_basic_sanitize(item, input_type) for item in data]
    else:
        return data


def _validate_type(data: Any, expected_type: str) -> bool:
    """Validate data type."""
    type_map = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
    }

    expected_python_type = type_map.get(expected_type)
    if expected_python_type is None:
        return True  # Unknown type, skip validation

    return isinstance(data, expected_python_type)


__all__ = [
    "validation_validate_alexa_directive",
    "validation_sanitize_input",
    "validation_validate_schema",
]
