"""
websocket/websocket_core.py
Version: 2025-12-13_1
Purpose: Gateway implementation functions for websocket interface
License: Apache 2.0
"""

from typing import Dict, Any

from websocket.websocket_manager import get_websocket_manager


def websocket_connect_implementation(url: str, timeout: int = 10,
                                     correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Connect to WebSocket server using manager.

    Args:
        url: WebSocket URL (ws:// or wss://)
        timeout: Connection timeout in seconds
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Success response with connection object, or error response
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id, validate_string, validate_number_range
    from debug import debug_timing

    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "WEBSOCKET",
             "websocket_connect_implementation called", url=url, timeout=timeout)

    # FIXED: Validate URL to prevent SSRF attacks (CVE-WEBSOCKET-2025-001)
    validate_string(url, min_length=10, max_length=500, name="WebSocket URL")
    validate_number_range(timeout, min_val=1, max_val=60, name="WebSocket timeout")

    # Additional URL security checks
    if not (url.startswith('ws://') or url.startswith('wss://')):
        raise ValueError("WebSocket URL must start with ws:// or wss://")

    # Prevent SSRF - block localhost, private IPs, and metadata service
    lower_url = url.lower()
    blocked_patterns = [
        'localhost', '127.0.0.1', '0.0.0.0',
        '192.168.', '10.', '172.16.', '172.17.', '172.18.',
        '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
        '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
        '172.29.', '172.30.', '172.31.', '169.254.169.254'  # AWS metadata
    ]

    for pattern in blocked_patterns:
        if pattern in lower_url:
            raise ValueError(f"WebSocket URL contains blocked pattern: {pattern}")

    with debug_timing(correlation_id, "WEBSOCKET", "websocket_connect_implementation",
                     url=url, timeout=timeout):
        try:
            manager = get_websocket_manager()
            result = manager.connect(url, timeout, correlation_id)
            debug_log(correlation_id, "WEBSOCKET", "websocket_connect_implementation completed",
                     success=True, url=url)
            return result
        except Exception as e:
            debug_log(correlation_id, "WEBSOCKET", "websocket_connect_implementation failed",
                     error_type=type(e).__name__, error=str(e), url=url)
            raise


def websocket_send_implementation(connection: Any, message: Dict[str, Any],
                                  correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Send message via WebSocket using manager.

    Args:
        connection: Active WebSocket connection object
        message: Dictionary to send
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Success response or error response
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id, validate_data_structure, validate_number_range
    from debug import debug_timing

    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "WEBSOCKET",
             "websocket_send_implementation called",
             has_connection=connection is not None,
             has_message=message is not None)

    # FIXED: Add message validation (MEDIUM-002)
    validate_data_structure(message, dict, "message")

    # Validate message size (prevent huge messages)
    import json
    message_str = json.dumps(message)
    message_size = len(message_str)
    if message_size > 1024 * 1024:  # 1MB limit
        raise ValueError("WebSocket message too large (max 1MB)")

    with debug_timing(correlation_id, "WEBSOCKET", "websocket_send_implementation",
                     message_size=message_size):
        try:
            manager = get_websocket_manager()
            result = manager.send(connection, message, correlation_id)
            debug_log(correlation_id, "WEBSOCKET", "websocket_send_implementation completed",
                     success=True, message_size=message_size)
            return result
        except Exception as e:
            debug_log(correlation_id, "WEBSOCKET", "websocket_send_implementation failed",
                     error_type=type(e).__name__, error=str(e))
            raise


def websocket_receive_implementation(connection: Any, timeout: int = 10,
                                     correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Receive message from WebSocket using manager.
    
    Args:
        connection: Active WebSocket connection object
        timeout: Receive timeout in seconds
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Success response with received message, or error response
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "WEBSOCKET",
             "websocket_receive_implementation called",
             has_connection=connection is not None, timeout=timeout)
    
    manager = get_websocket_manager()
    return manager.receive(connection, timeout, correlation_id)


def websocket_close_implementation(connection: Any, correlation_id: str = None,
                                   **kwargs) -> Dict[str, Any]:
    """
    Close WebSocket connection using manager.
    
    Args:
        connection: Active WebSocket connection object
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Success response or error response
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "WEBSOCKET",
             "websocket_close_implementation called",
             has_connection=connection is not None)
    
    manager = get_websocket_manager()
    return manager.close(connection, correlation_id)


def websocket_request_implementation(url: str, message: Dict[str, Any], 
                                     timeout: int = 10, correlation_id: str = None,
                                     **kwargs) -> Dict[str, Any]:
    """
    Execute complete WebSocket request using manager.
    
    Args:
        url: WebSocket URL (ws:// or wss://)
        message: Dictionary to send
        timeout: Connection and receive timeout in seconds
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Success response with server's response, or error response
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "WEBSOCKET",
             "websocket_request_implementation called",
             url=url, timeout=timeout, has_message=message is not None)
    
    manager = get_websocket_manager()
    return manager.request(url, message, timeout, correlation_id)


def websocket_get_stats_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Get WebSocket statistics using manager.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Statistics dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "WEBSOCKET", "websocket_get_stats_implementation called")
    
    manager = get_websocket_manager()
    return manager.get_stats(correlation_id)


def websocket_reset_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Reset WebSocket manager state.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Success/error response dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id, create_success_response, create_error_response
    from debug import debug_timing

    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "WEBSOCKET", "websocket_reset_implementation called")

    with debug_timing(correlation_id, "WEBSOCKET", "websocket_reset_implementation"):
        try:
            manager = get_websocket_manager()
            success = manager.reset(correlation_id)

            if success:
                debug_log(correlation_id, "WEBSOCKET", "websocket_reset_implementation completed",
                         success=True, reason="Reset successful")
                return create_success_response("WebSocket manager reset", {
                    'reset': True
                })
            else:
                debug_log(correlation_id, "WEBSOCKET", "websocket_reset_implementation completed",
                         success=False, reason="Rate limited")
                return create_error_response('Reset rate limited', 'RATE_LIMIT_EXCEEDED')
        except Exception as e:
            debug_log(correlation_id, "WEBSOCKET", "websocket_reset_implementation failed",
                     error_type=type(e).__name__, error=str(e))
            raise


__all__ = [
    'websocket_connect_implementation',
    'websocket_send_implementation',
    'websocket_receive_implementation',
    'websocket_close_implementation',
    'websocket_request_implementation',
    'websocket_get_stats_implementation',
    'websocket_reset_implementation',
]
