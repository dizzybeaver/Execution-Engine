# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-12 - Enforce HTTPS with HTTP fallback only for local networks

"""Forward Alexa directives to Home Assistant's /api/alexa/smart_home endpoint.

SECURITY: HTTPS is enforced by default. HTTP is only allowed for local
network addresses (10.*, 192.168.*, 127.*, localhost).
"""

import ipaddress
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant.ha_directive_errors import AlexaError


def _is_local_network(hostname: str) -> bool:
    """Check if hostname is a local network address.

    Args:
        hostname: Hostname or IP address to check

    Returns:
        True if hostname is a local/private network address

    Security:
        Only allows HTTP connections to local networks to prevent
        token exposure over public networks.

    """
    try:
        addr = ipaddress.ip_address(hostname)
        # Check for private IP ranges (RFC 1918)
        return addr.is_private
    except ValueError:
        # Not an IP address, check for localhost hostnames
        return hostname in (
            'localhost',
            'homeassistant.local',
            'hassio.local',
            'homeassistant'
        )


def forward_to_home_assistant_alexa(
    directive: dict[str, Any],
    oauth_token: str,
) -> dict[str, Any]:
    """Forward Alexa directive to Home Assistant /api/alexa/smart_home.

    Args:
        directive: Alexa directive dictionary
        oauth_token: OAuth token for authentication

    Returns:
        Alexa response from Home Assistant

    Raises:
        AlexaError: If forwarding fails
    """
    # Build request body - fix structure for discovery vs control
    # Discovery directives have scope in payload, control directives have endpoint
    if directive.get("header", {}).get("name") == "Discover":
        # Discovery: move scope from endpoint to payload, remove endpoint
        request_directive = {
            "header": directive.get("header", {}),
            "payload": {}
        }

        # Extract scope from endpoint and put it in payload
        endpoint = directive.get("endpoint", {})
        if "scope" in endpoint:
            request_directive["payload"]["scope"] = endpoint["scope"]

        request_body = {"directive": request_directive}
    else:
        # Control: send as-is with endpoint field
        request_body = {"directive": directive}

    # Get Home Assistant configuration
    ha_url = execute_operation(
        GatewayInterface.CONFIG,
        "get",
        key="HOME_ASSISTANT_URL"
    )
    ha_token = oauth_token

    # Create HTTP client with HTTPS enforcement
    from urllib.parse import urlparse
    from lee.home_assistant.http_client import HomeAssistantHTTP

    parsed_url = urlparse(ha_url)

    # SECURITY: Enforce HTTPS for public URLs
    use_ssl = (parsed_url.scheme == "https")

    if not use_ssl and parsed_url.hostname:
        # Check if hostname is local network
        if not _is_local_network(parsed_url.hostname):
            raise AlexaError(
                "HTTP connections to public hosts are blocked for security. "
                f"Host {parsed_url.hostname} requires HTTPS. "
                "HTTP is only allowed for local networks "
                "(10.*, 192.168.*, 127.*, localhost).",
                payload={"type": "INVALID_AUTHORIZATION_CREDENTIAL"}
            )

        # Log security warning for local HTTP
        execute_operation(
            GatewayInterface.LOGGING,
            'log_warning',
            message=(
                f"HTTP connection to {parsed_url.hostname} - "
                "Tokens sent unencrypted. Local network only."
            ),
            corr_id="ALEXA_PROXY_SECURITY"
        )

    ha_http = HomeAssistantHTTP(
        host=parsed_url.hostname,
        port=parsed_url.port,
        token=ha_token,
        use_ssl=use_ssl,
        verify_ssl=use_ssl  # Only verify SSL if using HTTPS
    )

    # CHECK CACHE FIRST for performance optimization
    from lee.home_assistant.ha_alexa_proxy_cache import (
        get_cached_response,
        should_use_cache,
        cache_response,
        invalidate_on_control_directive
    )

    # Invalidate cache for control directives
    if not should_use_cache(directive):
        invalidate_on_control_directive(directive)

    # Check cache for cacheable directives
    if should_use_cache(directive):
        cached_response = get_cached_response(directive)
        if cached_response:
            return cached_response

    # Forward to /api/alexa/smart_home
    try:
        # Log request details for debugging
        execute_operation(
            GatewayInterface.LOGGING,
            "log_info",
            corr_id="PROXY_DEBUG",
            scope="HOME_ASSISTANT",
            message="Proxy request: POST to /api/alexa/smart_home",
            ha_url=ha_url,
            url_scheme=parsed_url.scheme,
            target_host=parsed_url.hostname,
            target_port=parsed_url.port,
            use_ssl=use_ssl
        )

        response = ha_http.post(
            "alexa/smart_home",
            json=request_body
        )
    except (ConnectionError, TimeoutError, OSError) as e:
        raise AlexaError(
            f"Failed to connect to Home Assistant: {e!s}",
            payload={"type": "INTERNAL_ERROR"}
        )

    # Cache successful responses for better performance
    if response.ok:
        try:
            response_data = response.json()

            # Cache the response if it's successful and cacheable
            from lee.home_assistant.ha_alexa_proxy_cache import (
                cache_response,
                is_cache_successful_response
            )

            if is_cache_successful_response(response_data):
                cache_response(directive, response_data)

            return response_data
        except (ValueError, KeyError, AttributeError) as e:
            raise AlexaError(
                f"Invalid response from Home Assistant: {e!s}",
                payload={"type": "INTERNAL_ERROR"}
            )
    else:
        # Error responses are not cached
        return response.json() if response.text else {}


__all__ = ["forward_to_home_assistant_alexa"]
