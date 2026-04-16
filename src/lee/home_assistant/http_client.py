# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-12 - Enforce HTTPS with HTTP fallback only for local networks

"""home_assistant/http_client.py

Home Assistant–aware HTTP client built on network.http_core.HttpClient.

Provides convenience methods for Home Assistant API interactions with
automatic authentication and proper URL handling.

SECURITY: HTTPS is enforced by default. HTTP is only allowed for local
network addresses (10.*, 192.168.*, 127.*, localhost) to prevent token
exposure over public networks.
"""

import ipaddress
import os
import time
import warnings
from typing import Any, Optional
from urllib.parse import urlparse

from lee.home_assistant.ha_deployment_mode import DeploymentMode, get_deployment_mode
from lee.network.http_auth import bearer_token
from lee.network.http_core import HttpClient
from lee.network.ssrf_protect import validate_url
from lee.gateway import execute_operation, GatewayInterface


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled."""
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


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


class HomeAssistantHTTP:  # pylint: disable=R0902
    """Home Assistant HTTP client wrapper.

    Handles:
      - Bearer token authentication
      - Proper base URL construction
      - API path prefix (/api/)
      - JSON convenience methods

    Usage:
        ha_http = HomeAssistantHTTP(
            host="homeassistant.local",
            token="YOUR_LONG_LIVED_TOKEN"
        )
        config = ha_http.json("config")
        states = ha_http.json("states")
        ha_http.close()
    """

    def __init__(  # pylint: disable=R0913,R0914
        self,
        host: str,
        *,
        token: str,
        port: Optional[int] = None,
        use_ssl: bool = True,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        proxy: Optional[str] = None,
        verify_ssl: bool = True,
        extra_headers: Optional[dict[str, str]] = None,
    ):
        """Initialize Home Assistant HTTP client.

        Args:
            host: Home Assistant hostname or IP
            token: Long-lived access token
            port: Home Assistant port (default: 8123)
            use_ssl: Use HTTPS (default: True)
            timeout: Request timeout in seconds (None for mode-aware default)
            max_retries: Maximum retry attempts (None for mode-aware default)
            proxy: Optional proxy URL
            verify_ssl: Verify SSL certificates (default: True)
            extra_headers: Additional headers to include

        Security:
            HTTPS is enforced by default. HTTP is only allowed for local
            network addresses to prevent token exposure over public networks.

        Raises:
            ValueError: If HTTP is requested for a non-local hostname

        """
        # SECURITY: Enforce HTTPS by default
        if not use_ssl:
            # Check if hostname is local network
            if not _is_local_network(host):
                raise ValueError(
                    f"HTTP is only allowed for local networks (10.*, 192.168.*, 127.*, localhost). "
                    f"Host {host} requires HTTPS. "
                    f"This restriction prevents token exposure over public networks."
                )

            # Warn about HTTP usage even for local networks
            warnings.warn(
                f"HTTP connection to {host} - Tokens will be sent unencrypted. "
                f"Use HTTPS for production environments.",
                UserWarning,
                stacklevel=2
            )

            # Log security warning
            execute_operation(
                GatewayInterface.LOGGING,
                'log_warning',
                message=f"HTTP connection to {host}:{port or 80} - Tokens sent unencrypted. Local network only.",
                corr_id="HTTP_CLIENT_SECURITY"
            )

        self.host = host
        # Cloudflare tunnel uses standard HTTPS port 443, not HA's internal 8123
        if use_ssl:
            # For HTTPS, default to port 443 unless explicitly specified
            self.port = port if port is not None else 443
        else:
            # For HTTP, default to port 80 unless explicitly specified
            self.port = port if port is not None else 80
        self.token = token
        self.use_ssl = use_ssl

        # Use mode-aware defaults if not explicitly provided
        self.timeout = timeout if timeout is not None else self._get_default_timeout()
        actual_max_retries = max_retries if max_retries is not None else self._get_default_max_retries()

        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.extra_headers = extra_headers or {}

        scheme = "https" if use_ssl else "http"
        # Build base_url, omitting standard ports (443 for HTTPS, 80 for HTTP)
        # Cloudflare tunnel uses port 443 for HTTPS
        if (self.use_ssl and self.port == 443) or (not self.use_ssl and self.port == 80):
            # Standard port - omit from URL
            base_url = f"{scheme}://{host}/api/"
        else:
            # Custom port - include in URL
            base_url = f"{scheme}://{host}:{self.port}/api/"

        # SECURITY: Validate URL for SSRF attacks before creating client
        try:
            debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

            if debug_enabled:
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message="HomeAssistantHTTP - Validate URL for SSRF",
                                 scope='HTTP_CLIENT')

            # For Home Assistant, allow local network URLs from .env
            # Build allowlist dynamically to support both http and https
            allowlist = []

            env_url = os.getenv("HOME_ASSISTANT_URL")
            if env_url:
                # Allow the exact URL from .env file
                allowlist.append(env_url)
                # Also allow variations (different ports, protocols)
                parsed = urlparse(env_url)
                if parsed.hostname:
                    # Allow http/https with same hostname
                    allowlist.append(f"http://{parsed.hostname}:{parsed.port}")
                    allowlist.append(f"https://{parsed.hostname}:{parsed.port}")
                    # Allow without port
                    allowlist.append(f"http://{parsed.hostname}")
                    allowlist.append(f"https://{parsed.hostname}")
                    # Allow with /api/ path (used by base_url)
                    allowlist.append(f"http://{parsed.hostname}:{parsed.port}/api/")
                    allowlist.append(f"https://{parsed.hostname}:{parsed.port}/api/")
                    # Allow with /api path (without trailing slash)
                    allowlist.append(f"http://{parsed.hostname}:{parsed.port}/api")
                    allowlist.append(f"https://{parsed.hostname}:{parsed.port}/api")

            # SECURITY: Always allow local network base_url
            # This enables local testing while blocking public HTTP
            if _is_local_network(host):
                allowlist.append(base_url)

            is_safe = validate_url(base_url, allowlist=allowlist)

            debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

            if debug_enabled:
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message="HomeAssistantHTTP - After is_safe",
                                 scope='HTTP_CLIENT')

            if not is_safe:
                raise ValueError(
                    f"URL failed SSRF validation: {base_url}. "
                    f"Home Assistant HTTP client cannot connect to this URL."
                )
        except ValueError as e:
            raise ValueError(f"SSRF validation failed for Home Assistant HTTP client: {e}") from e

        self.client = HttpClient(
            base_url=base_url,
            timeout=self.timeout,
            max_retries=actual_max_retries,
            proxy=proxy,
            verify_ssl=verify_ssl,
            default_headers=self.extra_headers,
            auth_header_factory=bearer_token(token),
        )

        debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message="HomeAssistantHTTP - self.client = HttpClient",
                             scope='HTTP_CLIENT')


    # Standard HTTP methods
    def get(self, path, **kwargs):
        """GET request to Home Assistant API."""
        debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"HomeAssistantHTTP.get ENTRY - path={path}, timeout={self.timeout}, kwargs_keys={list(kwargs.keys())}",
                             scope='HTTP_CLIENT')
            execute_operation(GatewayInterface.DEBUG, 'timing',
                             operation_name='http_get_entry',
                             scope='HTTP_CLIENT')

        # Trace before calling underlying client
        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"About to call self.client.get(path={path})",
                             scope='HTTP_CLIENT')
            execute_operation(GatewayInterface.DEBUG, 'timing',
                             operation_name='before_client_get',
                             scope='HTTP_CLIENT')

        result = self.client.get(path, **kwargs)

        if debug_enabled:
            execute_operation(GatewayInterface.DEBUG, 'timing',
                             operation_name='after_client_get',
                             scope='HTTP_CLIENT')
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"self.client.get returned - status={result.status_code if hasattr(result, 'status_code') else 'unknown'}",
                             scope='HTTP_CLIENT')
            execute_operation(GatewayInterface.DEBUG, 'timing',
                             operation_name='http_get_complete',
                             scope='HTTP_CLIENT')

        return result

    def post(self, path, **kwargs):
        """POST request to Home Assistant API."""
        debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
        if debug_enabled:
            start_time = time.perf_counter()
            data_size = len(str(kwargs.get('json', {}))) if 'json' in kwargs else 0
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.post ENTRY - path={path} data_size={data_size} timeout={self.timeout}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        result = self.client.post(path, **kwargs)

        if debug_enabled:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.post EXIT - path={path} status={result.status} duration_ms={duration_ms:.2f}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        return result

    def put(self, path, **kwargs):
        """PUT request to Home Assistant API."""
        debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
        if debug_enabled:
            start_time = time.perf_counter()
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.put ENTRY - path={path} timeout={self.timeout}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        result = self.client.put(path, **kwargs)

        if debug_enabled:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.put EXIT - path={path} status={result.status} duration_ms={duration_ms:.2f}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        return result

    def delete(self, path, **kwargs):
        """DELETE request to Home Assistant API."""
        debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
        if debug_enabled:
            start_time = time.perf_counter()
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.delete ENTRY - path={path} timeout={self.timeout}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        result = self.client.delete(path, **kwargs)

        if debug_enabled:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.delete EXIT - path={path} status={result.status} duration_ms={duration_ms:.2f}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        return result

    # Convenience methods
    def json(self, path, **kwargs):
        """GET request with JSON response parsing.

        Args:
            path: API path (e.g., "config", "states")
            **kwargs: Additional request arguments

        Returns:
            Parsed JSON response data

        Example:
            config = ha_http.json("config")
            states = ha_http.json("states")

        """
        debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
        if debug_enabled:
            start_time = time.perf_counter()
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.json ENTRY - path={path}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        response = self.get(path, **kwargs)
        result = response.json()

        if debug_enabled:
            duration_ms = (time.perf_counter() - start_time) * 1000
            result_type = type(result).__name__
            if isinstance(result, list):
                if _is_debug_mode():
                    execute_operation(
                        GatewayInterface.DEBUG,
                        "log",
                        message=f"HomeAssistantHTTP.json EXIT - path={path} result_type=list[{len(result)}] duration_ms={duration_ms:.2f}",
                        corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                        scope="HTTP_CLIENT"
                    )
            elif isinstance(result, dict):
                if _is_debug_mode():
                    execute_operation(
                        GatewayInterface.DEBUG,
                        "log",
                        message=f"HomeAssistantHTTP.json EXIT - path={path} result_type=dict keys={list(result.keys())[:5]} duration_ms={duration_ms:.2f}",
                        corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                        scope="HTTP_CLIENT"
                    )
            else:
                if _is_debug_mode():
                    execute_operation(
                        GatewayInterface.DEBUG,
                        "log",
                        message=f"HomeAssistantHTTP.json EXIT - path={path} result_type={result_type} duration_ms={duration_ms:.2f}",
                        corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                        scope="HTTP_CLIENT"
                    )

        return result

    def post_json(self, path, data: dict[str, Any], **kwargs):
        """POST request with JSON body and response parsing.

        Args:
            path: API path
            data: Request body data
            **kwargs: Additional request arguments

        Returns:
            Parsed JSON response data

        Example:
            result = ha_http.post_json("services/light/turn_on", {
                "entity_id": "light.bubs_bedroom_inside_light_switch_1"
            })

        """
        debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
        if debug_enabled:
            start_time = time.perf_counter()
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.post_json ENTRY - path={path} data_keys={list(data.keys())[:5]}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        response = self.client.post(path, json=data, **kwargs)
        result = response.json()

        if debug_enabled:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.post_json EXIT - path={path} duration_ms={duration_ms:.2f}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        return result

    def call_service(self, domain: str, service: str, service_data: Optional[dict[str, Any]] = None):
        """Call Home Assistant service.

        Args:
            domain: Service domain (e.g., "light", "switch")
            service: Service name (e.g., "turn_on", "toggle")
            service_data: Service data (entity_id, etc.)

        Returns:
            Service call response

        Example:
            ha_http.call_service("light", "turn_on", {
                "entity_id": "light.bubs_bedroom_inside_light_switch_1",
                "brightness": 255
            })

        """
        debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
        if debug_enabled:
            start_time = time.perf_counter()
            entity_id = service_data.get('entity_id') if service_data else None
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.call_service ENTRY - domain={domain} service={service} entity_id={entity_id}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        path = f"services/{domain}/{service}"
        result = self.post_json(path, service_data or {})

        if debug_enabled:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.call_service EXIT - domain={domain} service={service} duration_ms={duration_ms:.2f}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        return result

    def get_state(self, entity_id: str):
        """Get entity state from Home Assistant.

        Args:
            entity_id: Entity ID (e.g., "light.bubs_bedroom_inside_light_switch_1")

        Returns:
            Entity state data

        Example:
            state = ha_http.get_state("light.bubs_bedroom_inside_light_switch_1")
            print(state['state'])  # "on"

        """
        debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
        if debug_enabled:
            start_time = time.perf_counter()
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.get_state ENTRY - entity_id={entity_id}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        result = self.json(f"states/{entity_id}")

        if debug_enabled:
            duration_ms = (time.perf_counter() - start_time) * 1000
            state = result.get('state') if isinstance(result, dict) else None
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.get_state EXIT - entity_id={entity_id} state={state} duration_ms={duration_ms:.2f}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        return result

    def get_states(self):
        """Get all states from Home Assistant.

        Returns:
            List of all entity states

        """
        debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
        if debug_enabled:
            start_time = time.perf_counter()
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message="HomeAssistantHTTP.get_states ENTRY",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        result = self.json("states")

        if debug_enabled:
            duration_ms = (time.perf_counter() - start_time) * 1000
            entity_count = len(result) if isinstance(result, list) else 0
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.get_states EXIT - entity_count={entity_count} duration_ms={duration_ms:.2f}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        return result

    def get_config(self):
        """Get Home Assistant configuration.

        Returns:
            Configuration data

        """
        debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
        if debug_enabled:
            start_time = time.perf_counter()
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message="HomeAssistantHTTP.get_config ENTRY",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        result = self.json("config")

        if debug_enabled:
            duration_ms = (time.perf_counter() - start_time) * 1000
            if _is_debug_mode():
                execute_operation(
                    GatewayInterface.DEBUG,
                    "log",
                    message=f"HomeAssistantHTTP.get_config EXIT - duration_ms={duration_ms:.2f}",
                    corr_id=self._correlation_id if hasattr(self, "_correlation_id") else "unknown",
                    scope="HTTP_CLIENT"
                )

        return result

    def close(self):
        """Close the HTTP client and connection pool."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _get_default_timeout(self) -> float:
        """Get default timeout based on deployment mode.

        Returns:
            float: Default timeout in seconds
                - Lambda: 3.0 seconds (fail fast on connection issues)
                - Local/WSGI: 30.0 seconds (more tolerant)

        """
        mode = get_deployment_mode()
        if mode == DeploymentMode.LAMBDA:
            return 10.0  # Increased from 3.0 - allows for Lambda network overhead

        return 30.0

    def _get_default_max_retries(self) -> int:
        """Get default max retries based on deployment mode.

        Returns:
            int: Default maximum retry attempts
                - Lambda: 1 retry (fail fast on connection issues)
                - Local/WSGI: 5 retries (more tolerant)

        """
        mode = get_deployment_mode()
        if mode == DeploymentMode.LAMBDA:
            return 3  # Increased from 1 - handles transient network issues

        return 5


__all__ = [
    "HomeAssistantHTTP",
]
