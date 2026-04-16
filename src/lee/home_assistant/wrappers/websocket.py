"""WebSocket Wrapper Functions Namespace

7 functions for WebSocket communication.

Usage:
    from lee.home_assistant.wrappers import websocket

    # Establish connection
    ws = websocket.establish_websocket_connection()

    # Authenticate
    websocket.authenticate_websocket()

    # Send message
    websocket.send_websocket_message(message={'type': 'subscribe_events'})

    # Receive message
    message = websocket.receive_websocket_message()

    # Get status
    status = websocket.get_websocket_status()

    # Close connection
    websocket.close_websocket_connection()

    # Generic request
    result = websocket.websocket_request(method='get', path='api/')
"""

# Import all WebSocket wrapper functions
from lee.home_assistant.interface.wrappers.ha_websocket_wrappers import (
    authenticate_websocket,
    close_websocket_connection,
    establish_websocket_connection,
    get_websocket_status,
    receive_websocket_message,
    send_websocket_message,
    websocket_request,
)

__all__ = [
    'authenticate_websocket',
    'close_websocket_connection',
    'establish_websocket_connection',
    'get_websocket_status',
    'receive_websocket_message',
    'send_websocket_message',
    'websocket_request',
]
