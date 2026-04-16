"""
lambda_failsafe.py
Version: 2025-12-07_02
Purpose: Independent failsafe Alexa handler (NO LEE dependencies)

CRITICAL: This file is COMPLETELY INDEPENDENT of LEE/gateway.
If LEE breaks, this still works. DO NOT import from gateway or any LEE modules.

LWA Migration:
- PRIMARY: OAuth token from Alexa directive
- FALLBACK: Long-lived token from HOME_ASSISTANT_API_KEY env var (if exists)

FIXED: Use urllib (built-in) instead of requests (not in Lambda runtime)

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import json
import os
import uuid
import time
from typing import Any, Dict, Optional
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# ===== SIMPLE LOGGING (NO GATEWAY) =====

def _log(level: str, message: str, **kwargs) -> None:
    """Simple logging - print to CloudWatch."""
    timestamp = datetime.utcnow().isoformat()
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
    - fallback_token: Optional long-lived token (if set)
    - timeout: Request timeout
    - verify_ssl: SSL verification
    """
    config = {
        'ha_url': os.environ.get('HOME_ASSISTANT_URL', 'https://homeassistant.local:8123'),
        'timeout': int(os.environ.get('HOME_ASSISTANT_TIMEOUT', '30')),
        'verify_ssl': os.environ.get('VERIFY_SSL', 'true').lower() == 'true'
    }
    
    # Optional fallback token (long-lived)
    fallback = os.environ.get('HOME_ASSISTANT_API_KEY')
    if fallback:
        config['fallback_token'] = fallback
        _log_info('Fallback token configured')
    
    return config


# ===== TOKEN EXTRACTION =====

def _extract_oauth_token(event: Dict[str, Any]) -> Optional[str]:
    """
    Extract OAuth token from Alexa directive.
    
    Locations (in priority order):
    1. directive.endpoint.scope.token (control directives)
    2. directive.payload.scope.token (discovery/grant)
    
    Returns:
        Token string or None if not found
    """
    directive = event.get('directive', {})
    
    # Try endpoint scope
    endpoint = directive.get('endpoint', {})
    scope = endpoint.get('scope', {})
    token = scope.get('token')
    
    if token:
        _log_debug('OAuth token found in endpoint.scope')
        return token
    
    # Try payload scope
    payload = directive.get('payload', {})
    scope = payload.get('scope', {})
    token = scope.get('token')
    
    if token:
        _log_debug('OAuth token found in payload.scope')
        return token
    
    return None


def _get_token(event: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Get authentication token.
    
    Priority:
    1. OAuth token from directive (PRIMARY)
    2. Fallback token from environment (SECONDARY)
    
    Args:
        event: Alexa event
        config: Configuration dict
        
    Returns:
        Token string
        
    Raises:
        ValueError: If no token available
    """
    # Try OAuth token first (PRIMARY)
    oauth_token = _extract_oauth_token(event)
    if oauth_token:
        _log_info('Using OAuth token from directive')
        return oauth_token
    
    # Try fallback token (SECONDARY)
    fallback = config.get('fallback_token')
    if fallback:
        _log_info('Using fallback long-lived token')
        return fallback
    
    # No token available
    _log_error('No token available (OAuth or fallback)')
    raise ValueError('No authentication token available')


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
        
        # Make request
        with urlopen(req, timeout=config.get('timeout', 30)) as response:
            duration = (time.perf_counter() - start) * 1000
            
            if response.status == 200:
                _log_info(
                    f'HA success: {namespace}.{name}',
                    request_id=request_id,
                    duration_ms=duration
                )
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)
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
            duration_ms=duration
        )
        return _error_response(
            'ENDPOINT_UNREACHABLE',
            f'Home Assistant returned {e.code}'
        )
        
    except URLError as e:
        duration = (time.perf_counter() - start) * 1000
        if hasattr(e, 'reason') and 'timed out' in str(e.reason).lower():
            _log_error('HA timeout', request_id=request_id, duration_ms=duration)
            return _error_response('ENDPOINT_UNREACHABLE', 'Home Assistant timeout')
        else:
            _log_error(
                f'HA connection failed: {e.reason}',
                request_id=request_id,
                duration_ms=duration
            )
            return _error_response(
                'ENDPOINT_UNREACHABLE',
                f'Connection failed: {e.reason}'
            )
        
    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        _log_error(f'Unexpected error: {e}', request_id=request_id, duration_ms=duration)
        return _error_response('INTERNAL_ERROR', 'Failed to process request')


# ===== HANDLER =====

def lambda_failsafe_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Independent failsafe handler.
    
    CRITICAL: NO LEE/gateway dependencies.
    Uses only built-in Python modules (urllib, json, etc.)
    
    Token priority:
    1. OAuth from directive (PRIMARY)
    2. HOME_ASSISTANT_API_KEY env var (SECONDARY)
    
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
        
        # Get token (OAuth or fallback)
        try:
            token = _get_token(event, config)
            config['token'] = token
        except ValueError as e:
            _log_error(f'Token error: {e}', request_id=request_id)
            return _error_response(
                'INVALID_AUTHORIZATION_CREDENTIAL',
                'Account linking required or fallback token not configured'
            )
        
        # Forward to HA
        response = _forward_to_ha(event, config)
        
        duration = (time.perf_counter() - start) * 1000
        _log_info('Failsafe complete', request_id=request_id, duration_ms=duration)
        
        return response
        
    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        _log_error(f'Handler error: {e}', request_id=request_id, duration_ms=duration)
        return _error_response('INTERNAL_ERROR', 'Unexpected error occurred')


# EOF
