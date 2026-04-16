"""template_validation.py

Version: 2026-03-26_1
Purpose: Template security validation utilities
License: Apache 2.0

Provides security validation for template rendering operations including
key validation and dangerous pattern detection.
"""

from typing import Any

# Dangerous patterns that should not appear in template keys
DANGEROUS_PATTERNS = [
    '__',  # Double underscore (magic methods/attributes)
    'import',  # Python import statement
    'exec',  # Python exec statement
    'eval',  # Python eval statement
    'compile',  # Python compile statement
    'open',  # File open operation
    'file:',  # File URL scheme
]


def validate_template_keys(template: dict[str, Any], data: dict[str, Any]) -> bool:  # pylint: disable=R0911
    """Validate template keys for dangerous patterns.

    Checks that template keys don't contain dangerous patterns that could
    lead to code injection or template injection attacks.

        template: Dictionary of template keys to validate
        data: Dictionary of data that will be used in template
        True if template keys are safe, False if dangerous patterns detected

    Template injection occurs when attacker-controlled data influences
    template keys, potentially executing arbitrary code.
    """
    if not template:
        return True

    for key in template.keys():
        # Ensure key is a string
        if not isinstance(key, str):
            return False

        # Check for dangerous patterns
        key_lower = key.lower()
        for pattern in DANGEROUS_PATTERNS:
            if pattern in key_lower:
                return False

        # Check for private/protected attribute access
        # Allow single leading underscore (protected) but reject double (private)
        if key.startswith('__'):
            return False

    # Validate data keys as well
    if data:
        for key in data.keys():
            if not isinstance(key, str):
                return False

            # Check for dangerous patterns in data keys
            key_lower = key.lower()
            for pattern in DANGEROUS_PATTERNS:
                if pattern in key_lower:
                    return False

    return True


def sanitize_template_keys(template: dict[str, Any]) -> dict[str, Any]:
    """Sanitize template dictionary by removing dangerous keys.

    Removes any template keys containing dangerous patterns while
    preserving safe keys. This is a defensive fallback when validation fails.

        template: Dictionary of template keys to sanitize
        Sanitized dictionary with dangerous keys removed

    >>> sanitize_template_keys({'__import__': 'os', 'safe_key': 'value'})
    {'safe_key': 'value'}
    """
    if not template:
        return {}

    sanitized = {}
    for key, value in template.items():
        if isinstance(key, str):
            key_lower = key.lower()
            is_dangerous = any(pattern in key_lower for pattern in DANGEROUS_PATTERNS)

            if not is_dangerous and not key.startswith('__'):
                sanitized[key] = value

    return sanitized


__all__ = [
    "validate_template_keys",
    "sanitize_template_keys",
]
