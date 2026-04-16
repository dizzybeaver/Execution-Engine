# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-26 - Create service call parameter validation

"""ha_validation.py - Home Assistant Service Call Parameter Validation

Provides strict validation for all service call parameters to prevent:
- Command injection through domain/service names
- Unauthorized entity access
- Malicious data payloads
- Path traversal attacks

All validation functions return tuples of (is_valid, error_message).
"""

from typing import Optional
import re
from collections.abc import Sequence

# Allowed patterns for HA identifiers
DOMAIN_PATTERN = re.compile(r'^[a-z_][a-z0-9_]*$')
SERVICE_PATTERN = re.compile(r'^[a-z_][a-z0-9_]*$')
ENTITY_ID_PATTERN = re.compile(r'^[a-z_][a-z0-9_]*\.[a-z0-9_][a-z0-9_]*[a-z0-9_]$')

# Validation constants
MAX_DOMAIN_LENGTH = 64
MAX_SERVICE_LENGTH = 64
MAX_ENTITY_ID_LENGTH = 255
MAX_SERVICE_DATA_KEY_LENGTH = 64
MAX_SERVICE_DATA_VALUE_LENGTH = 10000

# Blocked domains and services
BLOCKED_DOMAINS = {'shell', 'command', 'system', 'exec', 'eval'}
BLOCKED_SERVICES = {'shell_command', 'execute_shell', 'system_command', 'eval'}


# ===== SHARED VALIDATION HELPERS =====

def _validate_string_type(param_name: str, value, _correlation_id: str = None) -> tuple[bool, Optional[str]]:
    """Validate parameter is a string type.

    Args:
        param_name: Name of parameter for error message
        value: Value to validate
        _correlation_id: Optional correlation ID for tracking (unused)

    Returns:
        Tuple of (is_valid, error_message)

    Code Quality: Consolidates duplicate type checks (reduces ~16 lines)
    """
    if not isinstance(value, str):
        return False, f"{param_name} must be string, got {type(value).__name__}"
    return True, None


def _validate_string_length(param_name: str, value: str, max_length: int) -> tuple[bool, Optional[str]]:
    """Validate string length does not exceed maximum.

    Args:
        param_name: Name of parameter for error message
        value: String value to validate
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)

    Code Quality: Consolidates duplicate length checks (reduces ~16 lines)
    """
    if len(value) > max_length:
        return False, f"{param_name} too long (max {max_length} characters)"
    return True, None


def _validate_string_pattern(param_name: str, value: str, pattern: re.Pattern) -> tuple[bool, Optional[str]]:
    """Validate string matches regex pattern.

    Args:
        param_name: Name of parameter for error message
        value: String value to validate
        pattern: Compiled regex pattern to match

    Returns:
        Tuple of (is_valid, error_message)

    Code Quality: Consolidates duplicate pattern checks (reduces ~12 lines)
    """
    if not pattern.match(value):
        return False, f"{param_name} contains invalid characters: '{value}'"
    return True, None


def _validate_blocked_items(param_name: str, value: str, blocked_items: set[str]) -> tuple[bool, Optional[str]]:
    """Validate value is not in blocked items list.

    Args:
        param_name: Name of parameter for error message
        value: String value to validate
        blocked_items: Set of blocked values

    Returns:
        Tuple of (is_valid, error_message)

    Code Quality: Consolidates duplicate blocked checks (reduces ~8 lines)
    """
    if value.lower() in blocked_items:
        return False, f"{param_name} '{value}' is not allowed"
    return True, None


def validate_domain(domain: str, correlation_id: str = None) -> tuple[bool, Optional[str]]:
    """Validate service domain parameter.

    Args:
        domain: Service domain to validate
        correlation_id: Optional correlation ID for tracking

    Returns:
        Tuple of (is_valid, error_message)

    """
    if domain is None:
        return False, "Domain is required"
    if domain == "":
        return False, "Domain cannot be empty"

    # Use shared validation helpers (reduces duplication)
    is_valid, error = _validate_string_type("Domain", domain)
    if not is_valid:
        return False, error

    is_valid, error = _validate_string_length("Domain", domain, MAX_DOMAIN_LENGTH)
    if not is_valid:
        return False, error

    is_valid, error = _validate_string_pattern("Domain", domain, DOMAIN_PATTERN)
    if not is_valid:
        return False, error

    is_valid, error = _validate_blocked_items("Domain", domain, BLOCKED_DOMAINS)
    if not is_valid:
        return False, error

    return True, None


def validate_service(service: str, domain: str = None, _correlation_id: str = None) -> tuple[bool, Optional[str]]:
    """Validate service name parameter.

    Args:
        service: Service name to validate
        domain: Optional domain for context-aware validation
        _correlation_id: Optional correlation ID for tracking (unused)

    Returns:
        Tuple of (is_valid, error_message)

    """
    if service is None:
        return False, "Service is required"
    if service == "":
        return False, "Service cannot be empty"

    # Use shared validation helpers (reduces duplication)
    is_valid, error = _validate_string_type("Service", service)
    if not is_valid:
        return False, error

    is_valid, error = _validate_string_length("Service", service, MAX_SERVICE_LENGTH)
    if not is_valid:
        return False, error

    is_valid, error = _validate_string_pattern("Service", service, SERVICE_PATTERN)
    if not is_valid:
        return False, error

    is_valid, error = _validate_blocked_items("Service", service, BLOCKED_SERVICES)
    if not is_valid:
        return False, error

    # Context-aware validation for specific domains
    if domain == 'script' and service.startswith('../'):
        return False, "Path traversal detected in script service"

    return True, None


def validate_entity_id(entity_id: str, _correlation_id: str = None) -> tuple[bool, Optional[str]]:
    """Validate entity ID parameter.

    Args:
        entity_id: Entity ID to validate
        _correlation_id: Optional correlation ID for tracking (unused)

    Returns:
        Tuple of (is_valid, error_message)

    """
    if not entity_id:
        return True, None  # entity_id is optional for some services

    # Use shared validation helpers (reduces duplication)
    is_valid, error = _validate_string_type("Entity ID", entity_id)
    if not is_valid:
        return False, error

    is_valid, error = _validate_string_length("Entity ID", entity_id, MAX_ENTITY_ID_LENGTH)
    if not is_valid:
        return False, error

    is_valid, error = _validate_string_pattern("Entity ID", entity_id, ENTITY_ID_PATTERN)
    if not is_valid:
        return False, error

    # Block path traversal attempts
    if '..' in entity_id or entity_id.startswith('/'):
        return False, "Path traversal detected in entity ID"

    return True, None


def validate_entity_ids(entity_ids: list, correlation_id: str = None) -> tuple[bool, Optional[str]]:
    """Validate list of entity IDs for batch operations.

    Args:
        entity_ids: List of entity IDs to validate
        correlation_id: Optional correlation ID for tracking

    Returns:
        Tuple of (is_valid, error_message)

    """
    if not isinstance(entity_ids, Sequence):
        return False, f"Entity IDs must be sequence, got {type(entity_ids).__name__}"

    if len(entity_ids) > 100:
        return False, f"Too many entities in batch (max 100, got {len(entity_ids)})"

    for i, entity_id in enumerate(entity_ids):
        is_valid, error = validate_entity_id(entity_id, correlation_id)
        if not is_valid:
            return False, f"Entity ID at index {i}: {error}"

    return True, None


def validate_service_data(service_data: dict, _correlation_id: str = None) -> tuple[bool, Optional[str]]:
    """Validate service data payload.

    Args:
        service_data: Service data dictionary to validate
        _correlation_id: Optional correlation ID for tracking (unused)

    Returns:
        Tuple of (is_valid, error_message)

    """
    if service_data is None:
        return True, None

    if not isinstance(service_data, dict):
        return False, f"Service data must be dict, got {type(service_data).__name__}"

    # Limit payload size
    if len(service_data) > 50:
        return False, f"Service data has too many keys (max 50, got {len(service_data)})"

    # Single-pass validation: check all keys and values efficiently
    dangerous_keys = {'__import__', 'eval', 'exec', 'compile', '__builtins__'}
    dangerous_patterns = {'; rm ', '| ', '&& ', '$(', '`', 'bash -', 'sh -', '| rm ', '&& rm '}

    for key, value in service_data.items():
        # Validate key is string
        if not isinstance(key, str):
            return False, f"Service data key must be string, got {type(key).__name__}"

        # Check key length
        if len(key) > 64:
            return False, f"Service data key too long: '{key[:20]}...' (max 64)"

        # Check for dangerous keys
        if key.lower() in dangerous_keys:
            return False, f"Dangerous key in service data: '{key}'"

        # Reject very large string values
        if isinstance(value, str) and len(value) > 10000:
            return False, f"Service data value too large for key '{key}' (max 10000 chars)"

        # Check for shell command patterns in string values
        if isinstance(value, str):
            value_lower = value.lower()
            for pattern in dangerous_patterns:
                if pattern in value_lower:
                    return False, f"Potentially dangerous pattern detected: '{pattern}'"

    return True, None


def validate_service_call(
    domain: str,
    service: str,
    entity_id: str = None,
    entity_ids: list = None,
    service_data: dict = None,
    correlation_id: str = None,
) -> tuple[bool, list[str]]:
    """Validate complete service call parameters.

    Args:
        domain: Service domain
        service: Service name
        entity_id: Optional single entity ID
        entity_ids: Optional list of entity IDs (for batch calls)
        service_data: Optional service data payload
        correlation_id: Optional correlation ID for tracking

    Returns:
        Tuple of (is_valid, list_of_errors)

    """
    errors = []

    # Validate domain
    is_valid, error = validate_domain(domain, correlation_id)
    if not is_valid:
        errors.append(f"Domain: {error}")

    # Validate service
    is_valid, error = validate_service(service, domain, correlation_id)
    if not is_valid:
        errors.append(f"Service: {error}")

    # Validate entity_id or entity_ids (not both)
    if entity_id and entity_ids:
        errors.append("Cannot specify both entity_id and entity_ids")

    if entity_id:
        is_valid, error = validate_entity_id(entity_id, correlation_id)
        if not is_valid:
            errors.append(f"Entity ID: {error}")

    if entity_ids:
        is_valid, error = validate_entity_ids(entity_ids, correlation_id)
        if not is_valid:
            errors.append(f"Entity IDs: {error}")

    # Validate service_data
    is_valid, error = validate_service_data(service_data, correlation_id)
    if not is_valid:
        errors.append(f"Service data: {error}")

    return len(errors) == 0, errors
