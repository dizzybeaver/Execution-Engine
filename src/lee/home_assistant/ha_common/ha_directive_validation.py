# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-26 - Create Alexa directive validation module

"""ha_directive_validation.py - Alexa Directive Processing Validation

Provides comprehensive validation for Alexa Smart Home directives to ensure:
- Required fields are present
- Field values meet format constraints
- Namespaces and operations are recognized
- Message IDs are unique for deduplication
- Payloads match schema requirements

All validation functions return tuples of (is_valid, error_message, normalized_directive).
"""

import os
import re
import threading
from datetime import datetime, UTC
from typing import Optional

# Track seen message IDs for deduplication (TTL: 5 minutes)
_seen_message_ids: dict[str, float] = {}
_message_id_lock = threading.Lock()
_MESSAGE_ID_TTL = 300  # 5 minutes

# Allow duplicate message IDs for local testing
_ALLOW_DUPLICATE_MESSAGE_IDS = os.environ.get('ALLOW_DUPLICATE_MESSAGE_IDS', 'false').lower() == 'true'

# Alexa Smart Home API namespaces
VALID_NAMESPACES = {
    'Alexa.Discovery',
    'Alexa.PowerController',
    'Alexa.BrightnessController',
    'Alexa.ColorController',
    'Alexa.ColorTemperatureController',
    'Alexa.PercentageController',
    'Alexa.ThermostatController',
    'Alexa.TemperatureSensor',
    'Alexa.LockController',
    'Alexa.SceneController',
    'Alexa.SpeakerController',
    'Alexa.PlaybackController',
    'Alexa.Authorization',
    'Alexa.EndpointHealth',
    'Alexa',
}

# Operation name patterns
DIRECTIVE_NAME_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
MESSAGE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9\-_\.]+$')


def _cleanup_expired_message_ids() -> None:
    """Remove expired message IDs from tracking."""
    current_time = datetime.now(UTC).timestamp()
    with _message_id_lock:
        expired = [
            msg_id for msg_id, timestamp in _seen_message_ids.items()
            if current_time - timestamp > _MESSAGE_ID_TTL
        ]
        for msg_id in expired:
            del _seen_message_ids[msg_id]


def validate_directive_header(header: dict, _correlation_id: str = None) -> tuple[bool, Optional[str], dict]:
    """Validate Alexa directive header.

    Args:
        header: Directive header to validate
        _correlation_id: Correlation ID for logging (unused)

    Returns:
        Tuple of (is_valid, error_message, normalized_header)
    """
    if not header:
        return False, "Directive header is missing", {}

    if not isinstance(header, dict):
        return False, f"Header must be dict, got {type(header).__name__}", {}

    # Check required fields
    required_fields = ['namespace', 'name', 'messageId', 'payloadVersion']
    missing_fields = [f for f in required_fields if f not in header]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}", {}

    # Validate namespace
    namespace = header.get('namespace')
    if namespace not in VALID_NAMESPACES:
        return False, f"Unknown namespace: '{namespace}'", {}

    # Validate directive name
    name = header.get('name')
    if not DIRECTIVE_NAME_PATTERN.match(name):
        return False, f"Invalid directive name format: '{name}'", {}

    # Validate messageId
    message_id = header.get('messageId')
    if len(message_id) > 128:
        return False, "Message ID too long", {}

    if not MESSAGE_ID_PATTERN.match(message_id):
        return False, "Invalid message ID format", {}

    # Check for duplicate message ID (deduplication)
    # Bypass this check for local testing when ALLOW_DUPLICATE_MESSAGE_IDS is set
    if not _ALLOW_DUPLICATE_MESSAGE_IDS:
        _cleanup_expired_message_ids()
        with _message_id_lock:
            if message_id in _seen_message_ids:
                return False, f"Duplicate message ID: '{message_id}'", {}

    # Validate payloadVersion
    payload_version = header.get('payloadVersion')
    if payload_version not in ['3', '3.1', '3.2']:
        return False, f"Unsupported payload version: '{payload_version}'", {}

    # Normalize header
    normalized = {
        'namespace': namespace,
        'name': name,
        'messageId': message_id,
        'payloadVersion': payload_version,
    }

    # Add optional fields if present
    if 'correlationToken' in header:
        normalized['correlationToken'] = header['correlationToken']

    return True, None, normalized


def validate_directive_payload(  # pylint: disable=R0911,R0912
    payload: dict,
    namespace: str,
    name: str,
    _correlation_id: str = None,
) -> tuple[bool, Optional[str], dict]:
    """Validate Alexa directive payload.

    Args:
        payload: Directive payload to validate
        namespace: Directive namespace
        name: Directive name
        _correlation_id: Correlation ID for logging (unused)

    Returns:
        Tuple of (is_valid, error_message, normalized_payload)
    """
    if payload is None:
        return True, None, {}

    if not isinstance(payload, dict):
        return False, f"Payload must be dict, got {type(payload).__name__}", {}

    # Limit payload size
    if len(payload) > 20:
        return False, f"Payload has too many fields (max 20, got {len(payload)})", {}

    # Validate specific directives
    if namespace == 'Alexa.Discovery' and name == 'Discover':
        # Discovery directives should have optional accessToken
        if 'accessToken' in payload:
            token = payload['accessToken']
            if not isinstance(token, str) or len(token) < 32 or len(token) > 2048:
                return False, "Invalid access token in discovery payload (must be 32-2048 characters)", {}

    # Validate scope field (common in directives)
    if 'scope' in payload:
        scope = payload['scope']
        if not isinstance(scope, dict):
            return False, "Scope must be a dictionary", {}

        if 'token' in scope and not isinstance(scope['token'], str):
            return False, "Scope token must be a string", {}

    # Validate grantee (AcceptGrant directive)
    if 'grantee' in payload:
        grantee = payload['grantee']
        if not isinstance(grantee, dict):
            return False, "Grantee must be a dictionary", {}

        if 'token' in grantee and not isinstance(grantee['token'], str):
            return False, "Grantee token must be a string", {}

    # Validate endpoint field
    if 'endpoint' in payload:
        endpoint = payload['endpoint']
        if not isinstance(endpoint, dict):
            return False, "Endpoint must be a dictionary", {}

        if 'endpointId' in endpoint:
            endpoint_id = endpoint['endpointId']
            if not isinstance(endpoint_id, str) or len(endpoint_id) > 256:
                return False, "Invalid endpoint ID", {}

    return True, None, payload


def validate_directive(
    directive: dict,
    correlation_id: str = None,
) -> tuple[bool, list[str], dict]:
    """Complete validation of Alexa directive."""
    errors = []

    if not directive:
        return False, ["Directive is missing"], {}

    if not isinstance(directive, dict):
        return False, [f"Directive must be dict, got {type(directive).__name__}"], {}

    # Extract and validate header
    header = directive.get('header', {})
    is_valid, error, normalized_header = validate_directive_header(header, correlation_id)

    if not is_valid:
        errors.append(f"Header: {error}")

    # Extract namespace and name for endpoint validation
    namespace = normalized_header.get('namespace', '') if normalized_header else ''
    name = normalized_header.get('name', '') if normalized_header else ''

    # Initialize normalized_payload to avoid "possibly used before assignment" error
    normalized_payload = {}

    # For discovery directives, scope is at directive/payload level, NOT endpoint
    # Discovery directives DON'T have endpoints - they're sent to DISCOVER endpoints
    if namespace == 'Alexa.Discovery' and name == 'Discover':
        # Discovery directives have scope in payload, no endpoint field
        # Endpoint is what we're trying to discover, not what's sent to us
        payload = directive.get('payload', {})
        is_valid, error, normalized_payload = validate_directive_payload(
            payload, namespace, name, correlation_id
        )
        if not is_valid:
            errors.append(f"Payload: {error}")
        # No endpoint for discovery - that's correct
        endpoint = None
    else:
        # For non-discovery directives, check payload for endpoint
        payload = directive.get('payload', {})
        is_valid, error, normalized_payload = validate_directive_payload(
            payload, namespace, name, correlation_id
        )

        if not is_valid:
            errors.append(f"Payload: {error}")

        # Extract endpoint for non-discovery directives
        endpoint = directive.get('endpoint', {})

    # If validation passed, track message ID and return normalized directive
    if not errors and normalized_header:
        message_id = normalized_header['messageId']
        with _message_id_lock:
            _seen_message_ids[message_id] = datetime.now(UTC).timestamp()

        normalized_directive = {
            'header': normalized_header,
            'payload': normalized_payload,
        }

        # Add endpoint for non-discovery directives only
        # Discovery directives don't have endpoints (that's what we're discovering!)
        if endpoint and not (namespace == 'Alexa.Discovery' and name == 'Discover'):
            normalized_directive['endpoint'] = endpoint

        # Add optional fields from original directive
        if 'instance' in directive:
            normalized_directive['instance'] = directive['instance']

        return True, [], normalized_directive

    return False, errors, {}


def check_directive_consistency(
    directive: dict,
    expected_namespace: str = None,
    expected_name: str = None,
    _correlation_id: str = None,
) -> tuple[bool, list[str]]:
    """Check directive consistency with expected values.

    Args:
        directive: Directive to check
        expected_namespace: Expected namespace
        expected_name: Expected directive name
        _correlation_id: Correlation ID for logging (unused)

    Returns:
        Tuple of (is_consistent, list_of_inconsistencies)
    """
    inconsistencies = []

    header = directive.get('header', {})
    namespace = header.get('namespace', '')
    name = header.get('name', '')

    if expected_namespace and namespace != expected_namespace:
        inconsistencies.append(
            f"Namespace mismatch: expected '{expected_namespace}', got '{namespace}'"
        )

    if expected_name and name != expected_name:
        inconsistencies.append(
            f"Directive name mismatch: expected '{expected_name}', got '{name}'"
        )

    # Check header-payload consistency
    payload = directive.get('payload', {})

    # Discovery directives should have scope but not endpoint
    if namespace == 'Alexa.Discovery' and name == 'Discover':
        if 'endpoint' in payload:
            inconsistencies.append("Discovery directive should not have endpoint in payload")

    # Control directives should have endpoint
    if namespace.startswith('Alexa.') and namespace != 'Alexa.Discovery':
        if name not in ['Discover', 'ReportState'] and 'endpoint' not in payload:
            inconsistencies.append(f"Control directive '{name}' missing endpoint")

    return len(inconsistencies) == 0, inconsistencies
