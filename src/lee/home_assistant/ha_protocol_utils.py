"""Home Assistant Protocol Utilities

Version: 2026-04-04
Purpose: Shared utility functions for HA protocol conversions
License: Apache 2.0

This module provides common utility functions used across multiple
Home Assistant modules, particularly URL protocol conversions between
HTTP and WebSocket protocols.
"""



# Protocol conversion dispatch table for O(1) lookup
PROTOCOL_CONVERTERS = {
    "https://": lambda url: "wss://" + url[8:],
    "http://": lambda url: "ws://" + url[7:],
}


def convert_to_websocket_url(http_url: str) -> str:
    """Convert HTTP URL to WebSocket URL.

    PERFORMANCE: O(1) dispatch table lookup instead of O(n) if/elif chain.

    Args:
        http_url: HTTP URL to convert (http:// or https://)

    Returns:
        WebSocket URL (ws://, wss://, or original if no conversion needed)

    Examples:
        >>> convert_to_websocket_url("https://homeassistant:8123/api")
        'wss://homeassistant:8123/api'
        >>> convert_to_websocket_url("http://homeassistant:8123/api")
        'ws://homeassistant:8123/api'
        >>> convert_to_websocket_url("ws://existing")
        'ws://existing'
    """
    if not http_url:
        return http_url

    # Check each protocol and convert
    for protocol, converter in PROTOCOL_CONVERTERS.items():
        if http_url.startswith(protocol):
            return converter(http_url)

    # No conversion needed (already ws:// or wss://, or other protocol)
    return http_url


__all__ = [
    "convert_to_websocket_url",
    "PROTOCOL_CONVERTERS",
]
