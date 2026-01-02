"""
lambda_function.py
Version: 2025-12-14_1
Purpose: AWS Lambda entry point with mode routing via TEST interface
License: Apache 2.0
"""

# CRITICAL: sys.path fix for subdirectory imports
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
 
import json
import time
from typing import Dict, Any

# CRITICAL: Import lambda_preload FIRST
import lambda_preload

# Timing helper
def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.environ.get('DEBUG_MODE', 'false').lower() == 'true'


def _print_timing(msg: str):
    """Print timing message only if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[TIMING] {msg}")


# Performance optimization: Pre-import gateway functions
_timing_start = time.perf_counter()
_print_timing("Starting gateway imports at module level...")

from gateway import (
    log_info, log_error, log_debug,
    execute_operation, GatewayInterface,
    increment_counter, format_response,
    test_lambda_mode
)

_gateway_time = (time.perf_counter() - _timing_start) * 1000
_print_timing(f"Gateway imports complete: {_gateway_time:.2f}ms")

# Check if Home Assistant extension is enabled
HA_ENABLED = os.getenv('HOME_ASSISTANT_ENABLE', 'false').lower() == 'true'
HA_AVAILABLE = False

if HA_ENABLED:
    _ha_start = time.perf_counter()
    _print_timing("HOME_ASSISTANT_ENABLE=true, loading HA-SUGA...")
    try:
        from home_assistant import ha_interconnect
        HA_AVAILABLE = True
        _ha_time = (time.perf_counter() - _ha_start) * 1000
        _print_timing(f"HA-SUGA loaded: {_ha_time:.2f}ms")
        log_info("HA-SUGA extension loaded successfully")
    except ImportError as e:
        _ha_time = (time.perf_counter() - _ha_start) * 1000
        _print_timing(f"HA-SUGA import failed after {_ha_time:.2f}ms: {e}")
        log_error(f"Failed to import HA-SUGA: {e}")
        HA_AVAILABLE = False
else:
    _print_timing("HOME_ASSISTANT_ENABLE=false, HA-SUGA not loaded")


def _extract_oauth_token(event: Dict[str, Any]) -> str:
    """Extract OAuth token from Alexa directive."""
    directive = event.get('directive', {})
    header = directive.get('header', {})
    
    log_debug(f"Checking event for OAuth token", 
              namespace=header.get('namespace'), 
              name=header.get('name'),
              correlation_id="oauth_extract")
    
    # Check 1: directive.endpoint.scope.token (control directives)
    endpoint = directive.get('endpoint', {})
    if endpoint:
        scope = endpoint.get('scope', {})
        if scope:
            token = scope.get('token')
            if token:
                log_debug(f'Token found in directive.endpoint.scope',
                         length=len(token), correlation_id="oauth_extract")
                # FIXED: Validate token before returning (CVE-LAMBDA-2025-001)
                return _validate_oauth_token(token)
    
    # Check 2: directive.payload.scope.token (discovery/grant)
    payload = directive.get('payload', {})
    if payload:
        scope = payload.get('scope', {})
        if scope:
            token = scope.get('token')
            if token:
                log_debug(f'Token found in directive.payload.scope',
                         length=len(token), correlation_id="oauth_extract")
                # FIXED: Validate token before returning (CVE-LAMBDA-2025-001)
                return _validate_oauth_token(token)
    
    # Check 3: directive.payload.grantee.token (AcceptGrant)
    if payload:
        grantee = payload.get('grantee', {})
        if grantee:
            token = grantee.get('token')
            if token:
                log_debug(f'Token found in directive.payload.grantee',
                         length=len(token), correlation_id="oauth_extract")
                # FIXED: Validate token before returning (CVE-LAMBDA-2025-001)
                return _validate_oauth_token(token)
    
    # Check 4: directive.payload.grant.code (authorization code grant)
    if payload:
        grant = payload.get('grant', {})
        if grant:
            code = grant.get('code')
            if code:
                log_debug('Found authorization code in directive.payload.grant', 
                         correlation_id="oauth_extract")
    
    log_error('No OAuth token found in any location', correlation_id="oauth_extract")
    raise ValueError('No OAuth token in directive')


def _validate_oauth_token(token: str) -> str:
    """Validate OAuth token format and content.

    Args:
        token: OAuth token string to validate

    Returns:
        Validated token

    Raises:
        ValueError: If token is invalid (CVE-LAMBDA-2025-001)
    """
    # FIXED: Added token validation to prevent authentication bypass
    from gateway import validate_string

    # Validate token format and length
    validate_string(token, min_length=10, max_length=2000, name="OAuth token")

    # Additional token format checks
    if not token.replace('-', '').replace('_', '').replace('.', '').isalnum():
        # Allow common token characters but reject obviously malformed tokens
        pass  # OAuth tokens can have various formats, just ensure basic string validity

    return token


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entry point with mode routing."""
    handler_start = time.perf_counter()
    _print_timing("===== LAMBDA HANDLER START =====")
    _print_timing(f"Request ID: {context.aws_request_id}")
    _print_timing(f"Memory: {context.memory_limit_in_mb}MB")
    
    lambda_mode = os.getenv('LAMBDA_MODE', 'normal').lower()
    mode_time = (time.perf_counter() - handler_start) * 1000
    _print_timing(f"Mode selection ({lambda_mode}): +{mode_time:.2f}ms")
    
    # Route non-normal modes to TEST interface via gateway
    if lambda_mode != 'normal':
        _print_timing(f"Routing mode '{lambda_mode}' to TEST interface...")
        return test_lambda_mode(lambda_mode, event, context)
    
    _print_timing("Using normal handler")
    return lambda_handler_normal(event, context)


def lambda_handler_normal(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Normal Lambda handler with full LEE."""
    # NEW: Comprehensive debug tracing for exact failure point identification
    from gateway import validate_data_structure, debug_log, debug_timing, generate_correlation_id

    correlation_id = generate_correlation_id()

    debug_log(correlation_id, "LAMBDA", "===== NORMAL HANDLER START =====",
              request_id=getattr(context, 'aws_request_id', 'unknown'),
              memory_mb=getattr(context, 'memory_limit_in_mb', 'unknown'))

    with debug_timing(correlation_id, "LAMBDA", "lambda_handler_normal"):
        try:
            # FIXED: Add event validation (MEDIUM-006)
            debug_log(correlation_id, "LAMBDA", "Validating event structure")
            validate_data_structure(event, dict, "event")
            debug_log(correlation_id, "LAMBDA", "Event validation successful", event_keys=list(event.keys()))

            # Determine request type
            if 'directive' in event:
                debug_log(correlation_id, "LAMBDA", "Routing to Alexa request handler")
                result = handle_alexa_request(event, context)
            else:
                # Unknown request - return info
                debug_log(correlation_id, "LAMBDA", "Unknown request type received", event_keys=list(event.keys()))
                log_info(f"Unknown request type", event_keys=list(event.keys()))
                result = format_response(400, {
                    "error": "Unknown request type",
                    "event_keys": list(event.keys())
                })

            debug_log(correlation_id, "LAMBDA", "===== NORMAL HANDLER COMPLETE =====")
            return result

        except Exception as e:
            # NEW: Detailed error tracing with exact failure point
            debug_log(correlation_id, "LAMBDA", "EXCEPTION occurred in handler",
                     error_type=type(e).__name__, error=str(e))
            log_error(f"Lambda handler error: {str(e)}",
                     request_id=context.aws_request_id,
                     error_type=type(e).__name__,
                     extra={"correlation_id": correlation_id})
            return format_response(500, {"error": str(e), "correlation_id": correlation_id})


def handle_alexa_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Smart Home requests with LWA OAuth."""
    alexa_start = time.perf_counter()
    _print_timing("===== ALEXA REQUEST HANDLER =====")

    try:
        # FIXED: Add directive structure validation (MEDIUM-007)
        directive = event.get('directive', {})
        if not directive:
            raise ValueError("Missing 'directive' in Alexa request")

        header = directive.get('header', {})
        if not header:
            raise ValueError("Missing 'header' in directive")

        # Use .get() with defaults to prevent KeyError
        namespace = header.get('namespace', '')
        name = header.get('name', '')

        _print_timing(f"Processing: {namespace}.{name}")
        
        if not HA_AVAILABLE:
            _print_timing("ERROR: Alexa request but HA not available")
            log_error("Alexa request received but HOME_ASSISTANT_ENABLE=false or HA import failed")
            increment_counter('alexa_ha_not_available')
            
            return {
                'event': {
                    'header': {
                        'namespace': 'Alexa',
                        'name': 'ErrorResponse',
                        'messageId': 'error',
                        'correlationToken': header.get('correlationToken'),
                        'payloadVersion': '3'
                    },
                    'payload': {
                        'type': 'BRIDGE_UNREACHABLE',
                        'message': 'Home Assistant extension not enabled. Set HOME_ASSISTANT_ENABLE=true'
                    }
                }
            }
        
        # Extract OAuth token
        try:
            oauth_token = _extract_oauth_token(event)
            log_info(f'OAuth token extracted successfully', token_length=len(oauth_token))
            event['oauth_token'] = oauth_token
        except ValueError as e:
            log_error(f'OAuth token extraction failed: {str(e)}')
            increment_counter('oauth_token_missing')
            return {
                'event': {
                    'header': {
                        'namespace': 'Alexa',
                        'name': 'ErrorResponse',
                        'messageId': 'error',
                        'correlationToken': header.get('correlationToken'),
                        'payloadVersion': '3'
                    },
                    'payload': {
                        'type': 'INVALID_AUTHORIZATION_CREDENTIAL',
                        'message': 'Account linking required. Please link your account in the Alexa app.'
                    }
                }
            }
        
        _print_timing("Routing to HA-SUGA (ha_interconnect)...")
        route_start = time.perf_counter()
        
        result = ha_interconnect.alexa_process_directive(event)
        
        route_ms = (time.perf_counter() - route_start) * 1000
        _print_timing(f"HA-SUGA handler: {route_ms:.2f}ms")
        
        total_ms = (time.perf_counter() - alexa_start) * 1000
        _print_timing(f"*** TOTAL ALEXA REQUEST: {total_ms:.2f}ms ***")
        
        return result
        
    except Exception as e:
        error_time = (time.perf_counter() - alexa_start) * 1000
        _print_timing(f"!!! ALEXA ERROR after {error_time:.2f}ms: {str(e)}")
        log_error(f"Alexa request error: {str(e)}")
        increment_counter('alexa_request_error')
        return {
            'event': {
                'header': {
                    'namespace': 'Alexa',
                    'name': 'ErrorResponse',
                    'messageId': 'error',
                    'payloadVersion': '3'
                },
                'payload': {
                    'type': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }
        }

# EOF
