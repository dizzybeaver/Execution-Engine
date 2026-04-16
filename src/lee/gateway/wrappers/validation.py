"""Validation Wrapper Functions

Direct access to validation operations (3 functions).
All functions execute via gateway internally.

Usage:
    from lee.gateway.wrappers import validation

    # Validate Alexa directive
    is_valid = validation.validate_alexa_directive(directive=directive)

    # Sanitize input
    clean = validation.sanitize_input(user_input='<script>alert("XSS")</script>')

    # Validate schema
    is_valid = validation.validate_schema(data=data, schema=schema)
"""

from typing import Any, Optional

from lee.gateway.gateway_core import GatewayInterface, execute_operation


def validation_validate_alexa_directive(directive: dict[str, Any], **kwargs: Any) -> tuple[bool, Optional[str]]:
    """Validate Alexa directive.

    Args:
        directive: Directive dictionary
        **kwargs: Additional validation options

    Returns:
        Tuple of (is_valid, error_message)
    """
    return execute_operation(GatewayInterface.VALIDATION, 'validate_alexa_directive', directive=directive, **kwargs)


def validation_validate_schema(data: Any, schema: dict[str, Any], **kwargs: Any) -> tuple[bool, Optional[str]]:
    """Validate data against schema.

    Args:
        data: Data to validate
        schema: Schema to validate against
        **kwargs: Additional validation options

    Returns:
        Tuple of (is_valid, error_message)
    """
    return execute_operation(GatewayInterface.VALIDATION, 'validate_schema', data=data, schema=schema, **kwargs)


__all__ = [
    'validation_validate_alexa_directive',
    'validation_validate_schema',
]
