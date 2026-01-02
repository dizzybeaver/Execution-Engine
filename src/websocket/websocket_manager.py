"""
websocket/websocket_manager.py
Version: 2025-12-13_1
Purpose: WebSocket client manager with singleton pattern and rate limiting
License: Apache 2.0
"""

import json
import time
from typing import Dict, Any
from collections import deque


class WebSocketCore:
    """
    WebSocket CLIENT operations manager.
    
    Provides OUTBOUND WebSocket client functionality from Lambda to external servers.
    Does NOT accept inbound connections (would require API Gateway).
    
    COMPLIANCE:
    - AP-08: No threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-18: SINGLETON pattern via get_websocket_manager()
    - LESS-21: Rate limiting (300 ops/sec)
    """
    
    def __init__(self):
        """Initialize WebSocket manager with rate limiting."""
        # Rate limiting (300 ops/sec)
        self._rate_limiter = deque(maxlen=300)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0
        
        # Statistics
        self._total_operations = 0
        self._connections_count = 0
        self._messages_sent_count = 0
        self._messages_received_count = 0
        self._errors_count = 0
    
    def _check_rate_limit(self) -> bool:
        """Check if operation is within rate limit."""
        now = time.time() * 1000
        
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        if len(self._rate_limiter) >= 300:
            self._rate_limited_count += 1
            return False
        
        self._rate_limiter.append(now)
        return True
    
    def connect(self, url: str, timeout: int = 10, correlation_id: str = None) -> Dict[str, Any]:
        """
        Establish WebSocket CLIENT connection (outbound to external server).
        
        Args:
            url: WebSocket URL (ws:// or wss://)
            timeout: Connection timeout in seconds
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Success response with connection object, or error response
        """
        # ADDED: Debug integration
        from gateway import debug_log, debug_timing, generate_correlation_id, log_info, log_error
        from gateway import create_success_response, create_error_response, record_metric
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "WEBSOCKET", "Rate limit exceeded in connect()")
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        self._total_operations += 1
        
        if not url:
            debug_log(correlation_id, "WEBSOCKET", "Connect failed - no URL provided")
            log_error(f"[{correlation_id}] WebSocket connect failed: URL is required")
            self._errors_count += 1
            return create_error_response('URL parameter is required', 'WEBSOCKET_NO_URL')
        
        debug_log(correlation_id, "WEBSOCKET", "Connecting to WebSocket", url=url, timeout=timeout)
        
        with debug_timing(correlation_id, "WEBSOCKET", "connect"):
            try:
                import websocket
                
                log_info(f"[{correlation_id}] Establishing WebSocket CLIENT connection to {url}")
                
                ws = websocket.WebSocket()
                ws.connect(url, timeout=timeout)
                
                self._connections_count += 1
                record_metric('websocket.connections', 1.0)
                
                debug_log(correlation_id, "WEBSOCKET", "Connected successfully", url=url)
                log_info(f"[{correlation_id}] WebSocket CLIENT connected successfully")
                
                return create_success_response("WebSocket connected", {
                    'connection': ws,
                    'correlation_id': correlation_id,
                    'url': url
                })
                
            except ImportError as e:
                debug_log(correlation_id, "WEBSOCKET", "Library not available", error=str(e))
                log_error(f"[{correlation_id}] WebSocket library not available: {str(e)}")
                self._errors_count += 1
                record_metric('websocket.connection_errors', 1.0)
                return create_error_response('WebSocket library not installed', 'WEBSOCKET_LIBRARY_MISSING')
            except Exception as e:
                debug_log(correlation_id, "WEBSOCKET", "Connection failed", error=str(e))
                log_error(f"[{correlation_id}] WebSocket connection failed: {str(e)}")
                self._errors_count += 1
                record_metric('websocket.connection_errors', 1.0)
                return create_error_response(f'Connection failed: {str(e)}', 'WEBSOCKET_CONNECT_FAILED')
    
    def send(self, connection: Any, message: Dict[str, Any], correlation_id: str = None) -> Dict[str, Any]:
        """
        Send message via WebSocket CLIENT connection.
        
        Args:
            connection: Active WebSocket connection object
            message: Dictionary to send (JSON serialized)
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Success response or error response
        """
        # ADDED: Debug integration
        from gateway import debug_log, debug_timing, generate_correlation_id, log_info, log_error
        from gateway import create_success_response, create_error_response, record_metric
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "WEBSOCKET", "Rate limit exceeded in send()")
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        self._total_operations += 1
        
        if not connection:
            debug_log(correlation_id, "WEBSOCKET", "Send failed - no connection")
            log_error(f"[{correlation_id}] WebSocket send failed: No connection provided")
            self._errors_count += 1
            return create_error_response('Connection parameter is required', 'WEBSOCKET_NO_CONNECTION')
        
        if message is None:
            debug_log(correlation_id, "WEBSOCKET", "Send failed - no message")
            log_error(f"[{correlation_id}] WebSocket send failed: No message provided")
            self._errors_count += 1
            return create_error_response('Message parameter is required', 'WEBSOCKET_NO_MESSAGE')
        
        if not isinstance(message, dict):
            debug_log(correlation_id, "WEBSOCKET", "Send failed - invalid message type", 
                     message_type=type(message).__name__)
            log_error(f"[{correlation_id}] WebSocket send failed: Message must be a dictionary")
            self._errors_count += 1
            return create_error_response('Message must be a dictionary', 'WEBSOCKET_INVALID_MESSAGE')
        
        debug_log(correlation_id, "WEBSOCKET", "Sending message", message_keys=list(message.keys()))
        
        with debug_timing(correlation_id, "WEBSOCKET", "send"):
            try:
                log_info(f"[{correlation_id}] Sending WebSocket message to external server")
                
                message_str = json.dumps(message)
                connection.send(message_str)
                
                self._messages_sent_count += 1
                record_metric('websocket.messages_sent', 1.0)
                
                debug_log(correlation_id, "WEBSOCKET", "Message sent successfully")
                log_info(f"[{correlation_id}] Message sent successfully")
                
                return create_success_response("Message sent", {
                    'correlation_id': correlation_id
                })
                
            except (TypeError, ValueError) as e:
                debug_log(correlation_id, "WEBSOCKET", "Serialization failed", error=str(e))
                log_error(f"[{correlation_id}] Failed to serialize message: {str(e)}")
                self._errors_count += 1
                record_metric('websocket.send_errors', 1.0)
                return create_error_response(f'Message serialization failed: {str(e)}', 
                                           'WEBSOCKET_SERIALIZE_FAILED')
            except Exception as e:
                debug_log(correlation_id, "WEBSOCKET", "Send failed", error=str(e))
                log_error(f"[{correlation_id}] Failed to send message: {str(e)}")
                self._errors_count += 1
                record_metric('websocket.send_errors', 1.0)
                return create_error_response(f'Send failed: {str(e)}', 'WEBSOCKET_SEND_FAILED')
    
    def receive(self, connection: Any, timeout: int = 10, correlation_id: str = None) -> Dict[str, Any]:
        """
        Receive message from WebSocket CLIENT connection.
        
        Args:
            connection: Active WebSocket connection object
            timeout: Receive timeout in seconds
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Success response with received message, or error response
        """
        # ADDED: Debug integration
        from gateway import debug_log, debug_timing, generate_correlation_id, log_info, log_error
        from gateway import create_success_response, create_error_response, record_metric
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "WEBSOCKET", "Rate limit exceeded in receive()")
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        self._total_operations += 1
        
        if not connection:
            debug_log(correlation_id, "WEBSOCKET", "Receive failed - no connection")
            log_error(f"[{correlation_id}] WebSocket receive failed: No connection provided")
            self._errors_count += 1
            return create_error_response('Connection parameter is required', 'WEBSOCKET_NO_CONNECTION')
        
        debug_log(correlation_id, "WEBSOCKET", "Receiving message", timeout=timeout)
        
        with debug_timing(correlation_id, "WEBSOCKET", "receive"):
            try:
                log_info(f"[{correlation_id}] Receiving WebSocket message from external server")
                
                message_str = connection.recv()
                message = json.loads(message_str)
                
                self._messages_received_count += 1
                record_metric('websocket.messages_received', 1.0)
                
                debug_log(correlation_id, "WEBSOCKET", "Message received successfully",
                         message_keys=list(message.keys()) if isinstance(message, dict) else None)
                log_info(f"[{correlation_id}] Message received successfully")
                
                return create_success_response("Message received", {
                    'message': message,
                    'correlation_id': correlation_id
                })
                
            except json.JSONDecodeError as e:
                debug_log(correlation_id, "WEBSOCKET", "Parse failed", error=str(e))
                log_error(f"[{correlation_id}] Failed to parse message: {str(e)}")
                self._errors_count += 1
                record_metric('websocket.receive_errors', 1.0)
                return create_error_response(f'Message parsing failed: {str(e)}', 'WEBSOCKET_PARSE_FAILED')
            except Exception as e:
                debug_log(correlation_id, "WEBSOCKET", "Receive failed", error=str(e))
                log_error(f"[{correlation_id}] Failed to receive message: {str(e)}")
                self._errors_count += 1
                record_metric('websocket.receive_errors', 1.0)
                return create_error_response(f'Receive failed: {str(e)}', 'WEBSOCKET_RECEIVE_FAILED')
    
    def close(self, connection: Any, correlation_id: str = None) -> Dict[str, Any]:
        """
        Close WebSocket CLIENT connection.
        
        Args:
            connection: Active WebSocket connection object
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Success response or error response
        """
        # ADDED: Debug integration
        from gateway import debug_log, debug_timing, generate_correlation_id, log_info, log_error
        from gateway import create_success_response, create_error_response, record_metric
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "WEBSOCKET", "Rate limit exceeded in close()")
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        self._total_operations += 1
        
        if not connection:
            debug_log(correlation_id, "WEBSOCKET", "Close failed - no connection")
            log_error(f"[{correlation_id}] WebSocket close failed: No connection provided")
            self._errors_count += 1
            return create_error_response('Connection parameter is required', 'WEBSOCKET_NO_CONNECTION')
        
        debug_log(correlation_id, "WEBSOCKET", "Closing connection")
        
        with debug_timing(correlation_id, "WEBSOCKET", "close"):
            try:
                log_info(f"[{correlation_id}] Closing WebSocket CLIENT connection")
                connection.close()
                record_metric('websocket.disconnections', 1.0)
                
                debug_log(correlation_id, "WEBSOCKET", "Connection closed successfully")
                log_info(f"[{correlation_id}] Connection closed successfully")
                
                return create_success_response("Connection closed", {
                    'correlation_id': correlation_id
                })
            except Exception as e:
                debug_log(correlation_id, "WEBSOCKET", "Close failed", error=str(e))
                log_error(f"[{correlation_id}] Failed to close connection: {str(e)}")
                self._errors_count += 1
                return create_error_response(f'Close failed: {str(e)}', 'WEBSOCKET_CLOSE_FAILED')
    
    def request(self, url: str, message: Dict[str, Any], timeout: int = 10, 
                correlation_id: str = None) -> Dict[str, Any]:
        """
        Execute complete WebSocket CLIENT request (connect + send + receive + close).
        
        Args:
            url: WebSocket URL (ws:// or wss://)
            message: Dictionary to send
            timeout: Connection and receive timeout in seconds
            correlation_id: Optional correlation ID for debug tracking
            
        Returns:
            Success response with server's response, or error response
        """
        # ADDED: Debug integration
        from gateway import debug_log, debug_timing, generate_correlation_id, log_info, log_error
        from gateway import create_success_response, create_error_response
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "WEBSOCKET", "Rate limit exceeded in request()")
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        self._total_operations += 1
        
        if not url:
            debug_log(correlation_id, "WEBSOCKET", "Request failed - no URL")
            log_error(f"[{correlation_id}] WebSocket request failed: URL is required")
            self._errors_count += 1
            return create_error_response('URL parameter is required', 'WEBSOCKET_NO_URL')
        
        if message is None:
            debug_log(correlation_id, "WEBSOCKET", "Request failed - no message")
            log_error(f"[{correlation_id}] WebSocket request failed: Message is required")
            self._errors_count += 1
            return create_error_response('Message parameter is required', 'WEBSOCKET_NO_MESSAGE')
        
        debug_log(correlation_id, "WEBSOCKET", "Executing request", url=url, timeout=timeout)
        log_info(f"[{correlation_id}] Executing WebSocket CLIENT request to {url}")
        
        with debug_timing(correlation_id, "WEBSOCKET", "request"):
            # Connect
            connect_result = self.connect(url=url, timeout=timeout, correlation_id=correlation_id)
            if not connect_result.get('success'):
                debug_log(correlation_id, "WEBSOCKET", "Request failed at connect stage")
                log_error(f"[{correlation_id}] WebSocket request failed at connect stage")
                return connect_result
            
            connection = connect_result.get('data', {}).get('connection')
            
            # Send
            send_result = self.send(connection=connection, message=message, correlation_id=correlation_id)
            if not send_result.get('success'):
                debug_log(correlation_id, "WEBSOCKET", "Request failed at send stage - closing")
                log_error(f"[{correlation_id}] WebSocket request failed at send stage, closing connection")
                self.close(connection=connection, correlation_id=correlation_id)
                return send_result
            
            # Receive
            receive_result = self.receive(connection=connection, timeout=timeout, correlation_id=correlation_id)
            
            # Always close
            close_result = self.close(connection=connection, correlation_id=correlation_id)
            
            # Check receive result after closing
            if not receive_result.get('success'):
                debug_log(correlation_id, "WEBSOCKET", "Request failed at receive stage")
                log_error(f"[{correlation_id}] WebSocket request failed at receive stage")
                return receive_result
            
            if not close_result.get('success'):
                debug_log(correlation_id, "WEBSOCKET", "Request completed but close failed")
                log_error(f"[{correlation_id}] WebSocket request completed but close failed")
            
            debug_log(correlation_id, "WEBSOCKET", "Request completed successfully")
            log_info(f"[{correlation_id}] WebSocket CLIENT request completed successfully")
            
            return create_success_response("WebSocket request completed", {
                'response': receive_result.get('data', {}).get('message'),
                'correlation_id': correlation_id
            })
    
    def get_stats(self, correlation_id: str = None) -> Dict[str, Any]:
        """Get WebSocket manager statistics."""
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id, create_success_response, create_error_response
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "WEBSOCKET", "Rate limit exceeded in get_stats()")
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        debug_log(correlation_id, "WEBSOCKET", "Getting statistics",
                 operations=self._total_operations, connections=self._connections_count)
        
        return create_success_response("WebSocket statistics", {
            'total_operations': self._total_operations,
            'connections_count': self._connections_count,
            'messages_sent_count': self._messages_sent_count,
            'messages_received_count': self._messages_received_count,
            'errors_count': self._errors_count,
            'rate_limited_count': self._rate_limited_count,
            'rate_limit_window_ms': self._rate_limit_window_ms,
            'current_rate_limit_size': len(self._rate_limiter),
            'max_rate_limit': self._rate_limiter.maxlen
        })
    
    def reset(self, correlation_id: str = None) -> bool:
        """Reset WebSocket manager state."""
        # ADDED: Debug integration
        from gateway import debug_log, generate_correlation_id
        
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not self._check_rate_limit():
            debug_log(correlation_id, "WEBSOCKET", "Rate limit exceeded in reset()")
            return False
        
        try:
            debug_log(correlation_id, "WEBSOCKET", "Resetting manager state")
            
            self._total_operations = 0
            self._connections_count = 0
            self._messages_sent_count = 0
            self._messages_received_count = 0
            self._errors_count = 0
            self._rate_limiter.clear()
            self._rate_limited_count = 0
            
            debug_log(correlation_id, "WEBSOCKET", "Manager reset complete")
            return True
        except Exception as e:
            debug_log(correlation_id, "WEBSOCKET", "Manager reset failed", error=str(e))
            return False


# SINGLETON pattern (LESS-18)
_websocket_core = None


def get_websocket_manager() -> WebSocketCore:
    """
    Get SINGLETON WebSocket manager instance.
    
    Uses gateway SINGLETON registry with fallback to module-level instance.
    
    Returns:
        WebSocketCore: The singleton manager instance
    """
    global _websocket_core
    
    try:
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('websocket_manager')
        if manager is None:
            if _websocket_core is None:
                _websocket_core = WebSocketCore()
            singleton_register('websocket_manager', _websocket_core)
            manager = _websocket_core
        
        return manager
        
    except (ImportError, Exception):
        if _websocket_core is None:
            _websocket_core = WebSocketCore()
        return _websocket_core


__all__ = ['WebSocketCore', 'get_websocket_manager']
