"""Dashboard Server Factory Module for EE.

This module provides factory functions for creating Dashboard servers that
serve the web interface and JSON API for the EE Universal Gateway.

Architecture Layer: Domain Gateway - Dashboard Domain - Server Factory

Based on:
    D:\\Code\\Project\\Gateway\\dashboard\\dashboard_server_factory.py

Integration:
    - Creates HTTPServer instances with DashboardHandler
    - Injects gateway registry into handler
    - Provides clean server lifecycle management

Example:
    >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
    >>> from EE.dashboard import create_dashboard_server
    >>>
    >>> registry = EEDomainRegistry.get_instance()
    >>> server = create_dashboard_server(registry, port=8080)
    >>> server.serve_forever()
"""

from __future__ import annotations

import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass
from typing import Any, Optional

from EE.dashboard.dashboard_common import DashboardServerError
from EE.dashboard.dashboard_handler import DashboardHandler


# ============================================================================
# Dashboard Server Wrapper
# ============================================================================

@dataclass
class DashboardServer:
    """Wrapper for Dashboard HTTP server.

    This class provides a clean interface for managing the Dashboard server
    lifecycle, including startup, shutdown, and status checking.

    Attributes:
        server: The underlying HTTPServer instance
        host: Server host address
        port: Server port number
        registry: Gateway registry instance

    Example:
        >>> server = create_dashboard_server(registry, port=8080)
        >>> server.serve_forever()
        >>> # Later...
        >>> server.shutdown()
    """
    server: HTTPServer
    host: str
    port: int
    registry: Any

    def serve_forever(self) -> None:
        """Start the server and run forever.

        This method blocks and handles HTTP requests until the server is
        explicitly shut down.

        Raises:
            DashboardServerError: If server fails to start
        """
        try:
            print(f"Starting EE Dashboard server on http://{self.host}:{self.port}")
            self.server.serve_forever()
        except Exception as e:
            raise DashboardServerError(
                message=f"Server error: {e}",
                host=self.host,
                port=self.port,
            ) from e

    def shutdown(self) -> None:
        """Shutdown the server gracefully.

        This method stops the server and closes all connections.
        """
        try:
            self.server.shutdown()
            print(f"EE Dashboard server on http://{self.host}:{self.port} shut down")
        except Exception as e:
            print(f"Error shutting down server: {e}")

    def is_running(self) -> bool:
        """Check if the server is currently running.

        Returns:
            True if server is running, False otherwise
        """
        # Check if server socket is still active
        try:
            return self.server.socket is not None
        except Exception:
            return False

    def get_address(self) -> tuple[str, int]:
        """Get the server address.

        Returns:
            Tuple of (host, port)
        """
        return self.server.server_address


# ============================================================================
# Server Factory Functions
# ============================================================================

def create_dashboard_server(
    gateway_registry: Any,
    *,
    host: str = "127.0.0.1",
    port: int = 8080,
) -> DashboardServer:
    """Create a Dashboard server for the EE Universal Gateway.

    This factory function creates a configured HTTP server that serves both
    the web UI and JSON API for interacting with the EE gateway.

    Args:
        gateway_registry: EEDomainRegistry instance to use for gateway operations
        host: Server host address (default: "127.0.0.1")
        port: Server port number (default: 8080)

    Returns:
        DashboardServer instance ready to be started

    Raises:
        DashboardServerError: If server creation fails

    Example:
        >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
        >>> from EE.dashboard import create_dashboard_server
        >>>
        >>> registry = EEDomainRegistry.get_instance()
        >>> server = create_dashboard_server(registry, port=8080)
        >>> server.serve_forever()

    Note:
        The server binds to 127.0.0.1 by default for security. To expose
        the dashboard externally, use host="0.0.0.0" with appropriate
        firewall rules and authentication.
    """
    try:
        # Inject gateway registry into handler
        handler = DashboardHandler
        handler.gateway_registry = gateway_registry

        # Create HTTP server
        http_server = HTTPServer((host, port), handler)

        # Create wrapper
        server = DashboardServer(
            server=http_server,
            host=host,
            port=port,
            registry=gateway_registry,
        )

        return server

    except socket.error as e:
        raise DashboardServerError(
            message=f"Failed to bind to address: {e}",
            host=host,
            port=port,
            context={"error_code": e.errno if hasattr(e, 'errno') else None},
        ) from e
    except Exception as e:
        raise DashboardServerError(
            message=f"Failed to create server: {e}",
            host=host,
            port=port,
        ) from e


def create_dashboard_server_with_auto_port(
    gateway_registry: Any,
    *,
    host: str = "127.0.0.1",
    starting_port: int = 8080,
    max_attempts: int = 10,
) -> DashboardServer:
    """Create a Dashboard server with automatic port selection.

    This factory function attempts to create a server on the specified port,
    and if that fails, automatically tries subsequent ports until an available
    port is found.

    Args:
        gateway_registry: EEDomainRegistry instance to use for gateway operations
        host: Server host address (default: "127.0.0.1")
        starting_port: First port to try (default: 8080)
        max_attempts: Maximum number of ports to try (default: 10)

    Returns:
        DashboardServer instance on an available port

    Raises:
        DashboardServerError: If no available port is found after max_attempts

    Example:
        >>> server = create_dashboard_server_with_auto_port(
        ...     registry,
        ...     starting_port=8080,
        ...     max_attempts=5
        ... )
        >>> print(f"Server running on port {server.port}")
        >>> server.serve_forever()
    """
    last_error = None

    for attempt in range(max_attempts):
        port = starting_port + attempt
        try:
            server = create_dashboard_server(
                gateway_registry=gateway_registry,
                host=host,
                port=port,
            )
            print(f"Successfully bound to port {port} (attempt {attempt + 1}/{max_attempts})")
            return server
        except DashboardServerError as e:
            last_error = e
            print(f"Port {port} unavailable, trying next port...")
            continue

    # All attempts failed
    raise DashboardServerError(
        message=f"Could not find available port after {max_attempts} attempts",
        host=host,
        port=starting_port,
        context={"max_attempts": max_attempts, "last_error": str(last_error)},
    )


def find_available_port(
    *,
    host: str = "127.0.0.1",
    starting_port: int = 8080,
    max_attempts: int = 10,
) -> int:
    """Find an available port for the Dashboard server.

    This utility function checks for available ports without actually
    creating a server. Useful for planning or validation.

    Args:
        host: Server host address (default: "127.0.0.1")
        starting_port: First port to check (default: 8080)
        max_attempts: Maximum number of ports to check (default: 10)

    Returns:
        First available port number found

    Raises:
        DashboardServerError: If no available port is found

    Example:
        >>> port = find_available_port(starting_port=8080)
        >>> print(f"Available port: {port}")
    """
    for attempt in range(max_attempts):
        port = starting_port + attempt
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return port
        except socket.error:
            continue

    raise DashboardServerError(
        message=f"No available port found after {max_attempts} attempts",
        host=host,
        port=starting_port,
        context={"max_attempts": max_attempts},
    )


__all__ = [
    'DashboardServer',
    'create_dashboard_server',
    'create_dashboard_server_with_auto_port',
    'find_available_port',
]
