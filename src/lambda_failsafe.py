"""
lambda_failsafe.py
Version: 2026-04-07
Purpose: Independent failsafe Alexa handler (NO LEE dependencies)

CRITICAL: This file is COMPLETELY INDEPENDENT of LEE/gateway.
If LEE breaks, this still works. DO NOT import from gateway or any LEE modules.

Token Priority (SIMPLIFIED):
1. HOME_ASSISTANT_API_KEY (Long-Lived Access Token - PRIMARY)
2. OAuth token from directive (SECONDARY)

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import json
import os
import uuid
import time
from typing import Any, Dict, Optional
from datetime import datetime, UTC
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# ===== SIMPLE LOGGING (NO GATEWAY) =====

def _log(level: str, message: str, **kwargs) -> None:
    """Simple logging - print to CloudWatch."""
    timestamp = datetime.now(UTC).isoformat()
    log_data = {
        'timestamp': timestamp,
        'level': level,
        'message': message,
        **kwargs
    }
    print(json.dumps(log_data))


def _log_info(message: str, **kwargs) -> None:
    """Log info message."""
    _log('INFO', message, **kwargs)


def _log_error(message: str, **kwargs) -> None:
    """Log error message."""
    _log('ERROR', message, **kwargs)


def _log_debug(message: str, **kwargs) -> None:
    """Log debug message."""
    if os.environ.get('DEBUG', 'false').lower() == 'true':
        _log('DEBUG', message, **kwargs)


# ===== SIMPLE CACHE (NO LEE) =====

_CACHE: Dict[str, Dict[str, Any]] = {}


def _cache_get(key: str) -> Optional[Any]:
    """Get from cache if not expired."""
    if key in _CACHE:
        entry = _CACHE[key]
        if time.time() < entry['expires_at']:
            _log_debug(f'Cache hit: {key}')
            return entry['value']
        else:
            _log_debug(f'Cache expired: {key}')
            del _CACHE[key]
    return None


def _cache_set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    """Set cache value with TTL."""
    _CACHE[key] = {
        'value': value,
        'expires_at': time.time() + ttl_seconds
    }
    _log_debug(f'Cache set: {key} (TTL: {ttl_seconds}s)')


# ===== CONFIGURATION =====

def _load_config() -> Dict[str, Any]:
    """
    Load configuration from environment.

    Returns dict with:
    - ha_url: Home Assistant URL
    - ha_token: Home Assistant token (if set)
    - timeout: Request timeout
    - verify_ssl: SSL verification
    """
    # Detect Lambda environment for fast timeout
    is_lambda = os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None

    config = {
        'ha_url': os.environ.get('HOME_ASSISTANT_URL', 'https://homeassistant.local:8123').strip(),
        'timeout': int(os.environ.get('HOME_ASSISTANT_TIMEOUT', '3' if is_lambda else '30')),
        'verify_ssl': os.environ.get('VERIFY_SSL', 'true').lower() == 'true'
    }

    # HOME_ASSISTANT_API_KEY is the Long-Lived Access Token (LLAT)
    ha_token = os.environ.get('HOME_ASSISTANT_API_KEY', '').strip()
    if ha_token:
        config['ha_token'] = ha_token
        _log_info('HOME_ASSISTANT_API_KEY configured (Long-Lived Access Token)')

    return config


# ===== TOKEN EXTRACTION =====

def _extract_oauth_token(event: Dict[str, Any]) -> Optional[str]:
    """
    Extract OAuth token from Alexa directive.

    Locations (in priority order):
    1. directive.endpoint.scope.token (control directives)
    2. directive.payload.scope.token (discovery/grant)
    3. directive.payload.grantee.token (AcceptGrant directive)

    Returns:
        Token string or None if not found
    """
    directive = event.get('directive', {})

    # Try endpoint scope (control directives)
    endpoint = directive.get('endpoint', {})
    scope = endpoint.get('scope', {})
    token = scope.get('token', '').strip() if scope.get('token') else None

    if token:
        _log_debug('OAuth token found in endpoint.scope')
        return token

    # Try payload scope (discovery/grant)
    payload = directive.get('payload', {})
    scope = payload.get('scope', {})
    token = scope.get('token', '').strip() if scope.get('token') else None

    if token:
        _log_debug('OAuth token found in payload.scope')
        return token

    # Try grantee token (AcceptGrant directive)
    grantee = payload.get('grantee', {})
    token = grantee.get('token', '').strip() if grantee.get('token') else None

    if token:
        _log_debug('OAuth token found in payload.grantee')
        return token

    return None


def _get_token(event: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Get authentication token.

    Priority (SIMPLIFIED):
    1. HOME_ASSISTANT_API_KEY (Long-Lived Access Token - PRIMARY)
    2. OAuth token from directive (SECONDARY)

    Args:
        event: Alexa event
        config: Configuration dict

    Returns:
        Token string

    Raises:
        ValueError: If no token available
    """
    # Priority 1: HOME_ASSISTANT_API_KEY (Long-Lived Access Token)
    ha_token = config.get('ha_token')
    if ha_token:
        _log_info('Using HOME_ASSISTANT_API_KEY (Long-Lived Access Token)')
        return ha_token

    # Priority 2: OAuth token from directive (fallback)
    oauth_token = _extract_oauth_token(event)
    if oauth_token:
        _log_info('Using OAuth token from directive (fallback)')
        return oauth_token

    # No token available
    _log_error('No token available - set HOME_ASSISTANT_API_KEY environment variable')
    raise ValueError('No authentication token available - HOME_ASSISTANT_API_KEY not set')


# ===== ERROR RESPONSES =====

def _error_response(error_type: str, message: str) -> Dict[str, Any]:
    """Create Alexa error response."""
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': str(uuid.uuid4()),
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': message
            }
        }
    }


# ===== HA FORWARDING =====

def _forward_to_ha(event: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forward directive to Home Assistant using urllib (built-in).

    Args:
        event: Alexa directive
        config: Configuration (must include 'token')

    Returns:
        HA response or error response
    """
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    try:
        # Extract directive info
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', 'Unknown')
        name = header.get('name', 'Unknown')

        _log_info(
            f'Forwarding: {namespace}.{name}',
            request_id=request_id
        )

        # Check cache for discovery
        cache_key = f'discovery:{config["token"][:10]}'
        if namespace == 'Alexa.Discovery' and name == 'Discover':
            cached = _cache_get(cache_key)
            if cached:
                _log_info('Returning cached discovery response')
                return cached

        # Build endpoint
        ha_url = config['ha_url'].rstrip('/')
        endpoint = f'{ha_url}/api/alexa/smart_home'

        # Prepare request data
        json_data = json.dumps(event).encode('utf-8')

        # Create request with headers
        req = Request(endpoint, data=json_data)
        req.add_header('Authorization', f"Bearer {config['token']}")
        req.add_header('Content-Type', 'application/json')
        req.add_header('Content-Length', str(len(json_data)))

        # Debug: Log Authorization header format (without full token value)
        token_preview = config['token'][:10] if len(config['token']) > 10 else config['token']
        _log_info(f'Sending Authorization header: Bearer {token_preview}... (length: {len(config["token"])} chars)')

        # SSL context
        import ssl
        ssl_context = None
        if not config.get('verify_ssl', True):
            _log_debug('SSL verification DISABLED')
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        # Make request with timeout
        timeout = config.get('timeout', 3)
        _log_debug(f'Sending request to {endpoint} (timeout={timeout}s)')

        response = urlopen(req, timeout=timeout, context=ssl_context)
        duration = (time.perf_counter() - start) * 1000

        if response.status == 200:
            _log_info(
                f'HA success: {namespace}.{name}',
                request_id=request_id,
                duration_ms=f'{duration:.2f}'
            )
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)

            # Cache discovery response
            if namespace == 'Alexa.Discovery' and name == 'Discover':
                _cache_set(cache_key, result, ttl_seconds=300)

            return result
        else:
            _log_error(
                f'HA error: {response.status}',
                request_id=request_id,
                status=response.status
            )
            return _error_response(
                'ENDPOINT_UNREACHABLE',
                f'Home Assistant returned {response.status}'
            )

    except HTTPError as e:
        duration = (time.perf_counter() - start) * 1000
        _log_error(
            f'HA HTTP error: {e.code}',
            request_id=request_id,
            status=e.code,
            duration_ms=f'{duration:.2f}'
        )
        return _error_response(
            'ENDPOINT_UNREACHABLE',
            f'Home Assistant returned {e.code}'
        )

    except URLError as e:
        duration = (time.perf_counter() - start) * 1000
        reason = str(e.reason) if hasattr(e, 'reason') else 'unknown'

        if 'timed out' in reason.lower():
            _log_error(
                'HA timeout',
                request_id=request_id,
                duration_ms=f'{duration:.2f}'
            )
            return _error_response('ENDPOINT_UNREACHABLE', 'Home Assistant timeout')
        else:
            _log_error(
                f'HA connection failed: {reason}',
                request_id=request_id,
                duration_ms=f'{duration:.2f}'
            )
            return _error_response(
                'ENDPOINT_UNREACHABLE',
                f'Connection failed: {reason}'
            )

    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        _log_error(
            f'Unexpected error: {e}',
            request_id=request_id,
            duration_ms=f'{duration:.2f}'
        )
        return _error_response('INTERNAL_ERROR', 'Failed to process request')


# ===== HANDLER =====

def lambda_failsafe_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Independent failsafe handler.

    CRITICAL: NO LEE/gateway dependencies.
    Uses only built-in Python modules (urllib, json, etc.)

    Token Priority (SIMPLIFIED):
    1. HOME_ASSISTANT_API_KEY (Long-Lived Access Token - PRIMARY)
    2. OAuth token from directive (SECONDARY)

    Args:
        event: Alexa Smart Home event
        context: Lambda context

    Returns:
        Alexa response
    """
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    try:
        _log_info('Failsafe handler invoked', request_id=request_id)

        # Load config
        config = _load_config()

        # Get token (HOME_ASSISTANT_API_KEY or OAuth)
        try:
            token = _get_token(event, config)
            # Final sanitization - remove any whitespace
            token = token.strip() if token else ''
            if not token:
                raise ValueError('Token is empty after sanitization')

            # CRITICAL: Remove "Bearer " prefix if already present in token
            # SSM/stored tokens sometimes contain "Bearer " prefix
            if token.startswith('Bearer '):
                _log_info('Token contains "Bearer " prefix - stripping')
                token = token[7:].strip()  # Remove "Bearer " and any remaining whitespace

            # CRITICAL: Remove quotes if present (double or single quotes)
            if token.startswith('"') and token.endswith('"'):
                _log_info('Token contains double quotes - stripping')
                token = token[1:-1].strip()
            elif token.startswith("'") and token.endswith("'"):
                _log_info('Token contains single quotes - stripping')
                token = token[1:-1].strip()

            # Log token format (sanitized - first 10 chars only)
            token_preview = token[:10] if len(token) > 10 else token
            _log_info(f'Token ready (length: {len(token)} chars, preview: {token_preview}...)')

            config['token'] = token
        except ValueError as e:
            _log_error(f'Token error: {e}', request_id=request_id)
            return _error_response(
                'INVALID_AUTHORIZATION_CREDENTIAL',
                'HOME_ASSISTANT_API_KEY not configured'
            )

        # Forward to HA
        response = _forward_to_ha(event, config)

        duration = (time.perf_counter() - start) * 1000
        _log_info(
            'Failsafe complete',
            request_id=request_id,
            duration_ms=f'{duration:.2f}'
        )

        return response

    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        _log_error(
            f'Handler error: {e}',
            request_id=request_id,
            duration_ms=f'{duration:.2f}'
        )
        return _error_response('INTERNAL_ERROR', 'Unexpected error occurred')


# EOF
