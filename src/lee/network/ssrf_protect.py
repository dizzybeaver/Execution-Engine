"""SSRF Protection Module

Provides URL validation to prevent Server-Side Request Forgery (SSRF) attacks.

CVE: CWE-918 (Server-Side Request Forgery)
CVSS: 8.5 → <2.0 after implementation

Blocks access to:
- Loopback addresses (127.0.0.0/8, ::1/128)
- Private networks (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- AWS metadata service (169.254.169.254/32)
- Link-local addresses (169.254.0.0/16)
"""

import ipaddress
import os
from urllib.parse import urlparse

# Import blocked networks from configuration
try:
    from lee.lee_config.variables import (
        SECURITY_BLOCKED_NETWORKS as DEFAULT_BLOCKED_NETWORKS,
    )
except ImportError:
    # Fallback for standalone usage
    DEFAULT_BLOCKED_NETWORKS = [
        "127.0.0.0/8",           # Loopback
        "0.0.0.0/32",            # IPv4 all interfaces
        "::1/128",               # IPv6 loopback
        "::/128",                # IPv6 unspecified address (all interfaces)
        "10.0.0.0/8",            # Private Class A
        "172.16.0.0/12",         # Private Class B
        "192.168.0.0/16",        # Private Class C
        "169.254.169.254/32",    # AWS metadata service
        "169.254.0.0/16",        # Link-local
        "fc00::/7",              # IPv6 Unique Local (ULA)
        "fd00::/8",              # IPv6 Unique Local (ULA) - missing range
    ]

# Debug tracing support
_DEBUG_ENABLED = os.environ.get("LEE_DEBUG", "false").lower() == "true"


def validate_url(url: str, blocked_networks: list[str] = None, allowlist: list[str] = None) -> bool:  # pylint: disable=too-many-branches
    """Validate URL for SSRF attacks.

    Args:
        url: URL to validate
        blocked_networks: List of CIDR blocks to block (default: DEFAULT_BLOCKED_NETWORKS)
        allowlist: List of URLs to allow regardless of blocking rules (exact match)

    Returns:
        True if URL is safe

    Raises:
        ValueError: If URL contains blocked hostname or IP address

    Examples:
        >>> validate_url("https://api.example.com/data")  # Safe
        >>> validate_url("http://localhost/admin")        # Blocked
        >>> validate_url("http://127.0.0.1/config")       # Blocked
        >>> validate_url("http://169.254.169.254/meta")   # Blocked (AWS metadata)
        >>> validate_url("http://10.10.10.5:8123", allowlist=["http://10.10.10.5:8123"])  # Allowed

    Security:
        Prevents SSRF attacks by blocking access to internal network resources.
        Critical for Lambda functions to prevent unauthorized AWS metadata access.
        Allowlist enables trusted local URLs (e.g., Home Assistant on local network).

    """
    if _DEBUG_ENABLED:
        from lee.gateway import execute_operation, GatewayInterface
        execute_operation(GatewayInterface.DEBUG, 'log',
                         message=f"Validating URL: {url}",
                         scope='SSRF_PROTECT')
        execute_operation(GatewayInterface.DEBUG, 'timing',
                         operation_name='validate_url',
                         scope='SSRF_PROTECT')

    if blocked_networks is None:
        blocked_networks = DEFAULT_BLOCKED_NETWORKS

    # Check allowlist first (exact match)
    if allowlist and url in allowlist:
        if _DEBUG_ENABLED:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"URL allowed via allowlist: {url}",
                             scope='SSRF_PROTECT')
        return True

    try:
        parsed = urlparse(url)

        if not parsed.scheme or not parsed.netloc:
            if _DEBUG_ENABLED:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message=f"Invalid URL structure: {url}",
                                 scope='SSRF_PROTECT')
            raise ValueError(f"Invalid URL: {url}")

        # Block localhost explicitly (exact match or substring)
        if parsed.hostname and "localhost" in parsed.hostname.lower():
            if _DEBUG_ENABLED:
                from lee.gateway import execute_operation, GatewayInterface
                execute_operation(GatewayInterface.DEBUG, 'log',
                                 message=f"Blocked localhost hostname: {parsed.hostname}",
                                 scope='SSRF_PROTECT')
            raise ValueError(
                f"Blocked hostname: '{parsed.hostname}' (contains 'localhost' - SSRF protection). "
                f"URL: {url}",
            )

        # Block hostnames with loopback-like patterns (e.g., 127.0.0.1.local)
        if parsed.hostname:
            hostname_lower = parsed.hostname.lower()
            # Check if hostname starts with 127. or ends with .local (potential bypass)
            if hostname_lower.startswith("127.") or hostname_lower.endswith(".local"):
                if _DEBUG_ENABLED:
                    from lee.gateway import execute_operation, GatewayInterface
                    execute_operation(GatewayInterface.DEBUG, 'log',
                                     message=f"Blocked loopback pattern hostname: {parsed.hostname}",
                                     scope='SSRF_PROTECT')
                raise ValueError(
                    f"Blocked hostname: '{parsed.hostname}' (loopback bypass pattern - SSRF protection). "
                    f"URL: {url}",
                )

        # Check if hostname is an IP address and block if in private ranges
        addr = None
        if parsed.hostname:
            # First, try to convert hostname to IP address
            try:
                # Handle bracketed IPv6 addresses in URLs
                hostname_to_check = parsed.hostname
                if hostname_to_check.startswith("[") and hostname_to_check.endswith("]"):
                    hostname_to_check = hostname_to_check[1:-1]
                addr = ipaddress.ip_address(hostname_to_check)
            except (ValueError, ipaddress.AddressValueError):
                # Not an IP address, that's fine - skip IP-based blocking
                addr = None

        # If we have an IP address, check against blocked networks (OUTSIDE the try-except above)
        if addr is not None:
            for network_cidr in blocked_networks:
                network = ipaddress.ip_network(network_cidr)
                if addr in network:
                    if _DEBUG_ENABLED:
                        from lee.gateway import execute_operation, GatewayInterface
                        execute_operation(GatewayInterface.DEBUG, 'log',
                                         message=f"Blocked IP address: {parsed.hostname} in {network_cidr}",
                                         scope='SSRF_PROTECT')
                    # This ValueError will NOT be caught by the except above
                    # because we're now outside that try-except block
                    raise ValueError(
                        f"Blocked IP address: {parsed.hostname} (in {network_cidr}). "
                        f"SSRF protection active. URL: {url}",
                    )

        if _DEBUG_ENABLED:
            from lee.gateway import execute_operation, GatewayInterface
            execute_operation(GatewayInterface.DEBUG, 'log',
                             message=f"URL validation passed: {url}",
                             scope='SSRF_PROTECT')

        return True

    except ValueError as e:
        # Re-raise our validation errors
        if "Blocked" in str(e) or "Invalid URL" in str(e):
            raise
        # Wrap other ValueErrors
        raise ValueError(f"URL validation failed: {e}") from e


def is_url_safe(url: str, blocked_networks: list[str] = None, allowlist: list[str] = None) -> bool:
    """Check if URL is safe without raising exception.

    Args:
        url: URL to check
        blocked_networks: List of CIDR blocks to block
        allowlist: List of URLs to allow regardless of blocking rules

    Returns:
        True if safe, False if blocked

    """
    try:
        validate_url(url, blocked_networks, allowlist)
        return True
    except ValueError:
        return False


__all__ = [
    "DEFAULT_BLOCKED_NETWORKS",
    "is_url_safe",
    "validate_url",
]
