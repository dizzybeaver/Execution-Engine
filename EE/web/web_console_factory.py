"""
Web Console Factory - EE Web Domain Gateway

This module provides factory functions for creating web console servers
that expose the EE gateway system through HTTP/REST API.

Architecture Layer: Layer 1 - Domain Gateway Infrastructure
Part of: Web Domain Gateway (gateway.web)

Based on: D:\\Code\\Project\\Gateway\\Web\\web_console_factory.py
"""

from __future__ import annotations
from http.server import HTTPServer
from dataclasses import dataclass
from typing import Any, Optional
import logging

from EE.web.web_handler import WebHandler

logger = logging.getLogger(__name__)


@dataclass
class WebConsole:
    """Web console server for EE Gateway system.

    This dataclass wraps an HTTPServer instance and provides
    methods for serving the web console.

    Attributes:
        server: HTTPServer instance
        host: Server host address
        port: Server port number

    Example:
        >>> console = create_web_console(gateway, port=8080)
        >>> console.serve_forever()  # Blocks
        >>>
        >>> # Or run in background thread
        >>> import threading
        >>> thread = threading.Thread(target=console.serve_forever, daemon=True)
        >>> thread.start()
    """

    server: HTTPServer
    host: str
    port: int

    def serve_forever(self) -> None:
        """Start the web console server (blocks).

        This method starts the HTTP server and blocks until the server
        is stopped (e.g., via server.shutdown()).
        """
        logger.info(f"Starting EE Web Console on http://{self.host}:{self.port}")
        self.server.serve_forever()

    def shutdown(self) -> None:
        """Shutdown the web console server.

        This method gracefully shuts down the HTTP server.
        """
        logger.info(f"Shutting down EE Web Console on http://{self.host}:{self.port}")
        self.server.shutdown()

    def get_address(self) -> tuple[str, int]:
        """Get the server address.

        Returns:
            Tuple of (host, port)
        """
        return self.server.server_address


def create_web_console(
    gateway: Any,
    registry: Optional[Any] = None,
    *,
    host: str = "127.0.0.1",
    port: int = 8080,
) -> WebConsole:
    """Create a web console server for EE Gateway system.

    This factory function creates an HTTP server that exposes the EE gateway
    system through a REST API. The server supports:

    - GET /list-all: List all gateway operations
    - GET /list-domains: List all registered domains
    - GET /list-routes: List all routes
    - GET /stats: Get gateway statistics
    - GET /health: Health check
    - POST /exec/{route}: Execute gateway route

    Args:
        gateway: EE gateway instance
        registry: EE domain registry instance (optional, extracted from gateway if None)
        host: Server host address (default: "127.0.0.1")
        port: Server port number (default: 8080)

    Returns:
        WebConsole instance ready to serve

    Raises:
        ValueError: If gateway is None

    Example:
        >>> from EE.src.gateway.gateway import EEGateway
        >>> from EE.web import create_web_console
        >>>
        >>> # Create gateway
        >>> gateway = EEGateway()
        >>>
        >>> # Create web console
        >>> console = create_web_console(gateway, port=8080)
        >>>
        >>> # Start server (blocks)
        >>> console.serve_forever()
        >>>
        >>> # Or run in background
        >>> import threading
        >>> thread = threading.Thread(target=console.serve_forever, daemon=True)
        >>> thread.start()
        >>> print(f"Console running at http://127.0.0.1:8080")

    Example:
        Using with domain registry:

        >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
        >>> from EE.web import create_web_console
        >>>
        >>> # Setup gateway and registry
        >>> gateway = create_my_gateway()
        >>> registry = EEDomainRegistry.get_instance()
        >>>
        >>> # Create web console with registry
        >>> console = create_web_console(
        ...     gateway=gateway,
        ...     registry=registry,
        ...     port=8080
        ... )
        >>>
        >>> # Start server
        >>> console.serve_forever()
    """
    if gateway is None:
        raise ValueError("Gateway instance is required")

    # Extract registry from gateway if not provided
    if registry is None and hasattr(gateway, 'registry'):
        registry = gateway.registry

    # Configure handler class with gateway and registry
    WebHandler.gateway = gateway
    WebHandler.registry = registry

    # Create HTTP server
    server = HTTPServer((host, port), WebHandler)

    # Create web console wrapper
    console = WebConsole(
        server=server,
        host=host,
        port=port,
    )

    logger.info(f"Created EE Web Console on http://{host}:{port}")
    return console


def create_and_start_web_console(
    gateway: Any,
    registry: Optional[Any] = None,
    *,
    host: str = "127.0.0.1",
    port: int = 8080,
    background: bool = True,
) -> WebConsole:
    """Create and start a web console server.

    This is a convenience function that creates and immediately starts
    the web console server.

    Args:
        gateway: EE gateway instance
        registry: EE domain registry instance (optional)
        host: Server host address (default: "127.0.0.1")
        port: Server port number (default: 8080)
        background: If True, run server in background thread (default: True)

    Returns:
        WebConsole instance

    Example:
        >>> from EE.src.gateway.gateway import EEGateway
        >>> from EE.web import create_and_start_web_console
        >>>
        >>> gateway = EEGateway()
        >>>
        >>> # Create and start in background
        >>> console = create_and_start_web_console(gateway, port=8080)
        >>> print(f"Console running at http://127.0.0.1:8080")
        >>>
        >>> # Server is running in background, can continue work
        >>> ...
        >>>
        >>> # Stop when done
        >>> console.shutdown()
    """
    import threading

    # Create console
    console = create_web_console(
        gateway=gateway,
        registry=registry,
        host=host,
        port=port,
    )

    if background:
        # Start in background thread
        server_thread = threading.Thread(
            target=console.serve_forever,
            daemon=True,
        )
        server_thread.start()
        logger.info(f"Web console started in background on http://{host}:{port}")
    else:
        # Start in foreground (blocks)
        logger.info(f"Web console starting in foreground on http://{host}:{port}")
        console.serve_forever()

    return console


__all__ = [
    'WebConsole',
    'create_web_console',
    'create_and_start_web_console',
]
