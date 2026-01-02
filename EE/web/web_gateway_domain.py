"""
Web Gateway Domain - EE Web Domain Gateway

This module provides the Web domain gateway implementation for the EE Universal
Gateway system. It integrates web console functionality with the gateway registry
and enables HTTP-based access to all gateway operations.

Architecture Layer: Layer 1 - Domain Gateway
Part of: Web Domain Gateway (gateway.web)

Routes:
    - web.execute: Execute gateway operation via HTTP
    - web.list_operations: List all available operations
    - web.list_domains: List all registered domains
    - web.start_console: Start web console server
    - web.stop_console: Stop web console server
    - web.get_stats: Get web console statistics

Based on Gateway reference implementation patterns.
"""

from __future__ import annotations
import sys
import threading
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass, field

# REMOVED: sys.path.insert() - using proper imports

from EE.universal_gateway.domain_gateway import DomainGateway

# Import web components
from EE.web.web_console_factory import WebConsole, create_web_console


class WebGatewayDomain(DomainGateway):
    """Web Domain Gateway for EE Universal Gateway System.

    This domain gateway provides web-based access to the EE gateway system.
    It manages the web console server lifecycle and integrates with the
    gateway registry for HTTP-based operation execution.

    Attributes:
        gateway: EE gateway instance (optional, injected at runtime)

    Note: Console state is managed through instance-level mutable storage
    to allow dynamic console lifecycle management.

    Routes:
        - web.execute: Execute gateway operation via web console
        - web.list_operations: List all web operations
        - web.list_domains: List all registered domains
        - web.start_console: Start web console server
        - web.stop_console: Stop web console server
        - web.get_stats: Get web console statistics
        - web.is_running: Check if console is running

    Example:
        >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
        >>> from EE.web import WebGatewayDomain
        >>>
        >>> registry = EEDomainRegistry.get_instance()
        >>> web_gateway = WebGatewayDomain(
        ...     domain_name="web",
        ...     get_logger=registry.get_logger,
        ...     get_metrics=registry.get_metrics,
        ...     get_config=registry.get_config,
        ...     call_operation=registry.call_operation
        ... )
        >>>
        >>> # Register web domain
        >>> registry.register("web", web_gateway)
        >>>
        >>> # Start web console
        >>> result = web_gateway.execute("web.start_console", {"port": 8080})
        >>>
        >>> # Check if running
        >>> status = web_gateway.execute("web.is_running", {})
        >>>
        >>> # Stop console
        >>> web_gateway.execute("web.stop_console", {})
    """

    # MODIFIED: EE 2.1 uniform constructor signature
    def __init__(
        self,
        domain_name: str,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable,
    ):
        """Initialize Web Gateway Domain with EE 2.1 dependencies.

        Args:
            domain_name: Domain name for this gateway
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Function to call operations in other domains
        """
        # ADDED: Call parent __init__ with all EE 2.1 parameters
        super().__init__(
            domain_name=domain_name,
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation,
        )

        # EE 2.1 UPGRADE: Removed 'self.gateway' attribute for backward compatibility (anti-pattern)
        self._console: Optional[WebConsole] = None
        self._console_lock = threading.Lock()

    def execute(self, route: str, payload: dict) -> Any:
        """Execute web gateway operation.

        Args:
            route: Operation route (e.g., "web.start_console")
            payload: Operation parameters as dictionary

        Returns:
            Operation result

        Raises:
            GatewayError: If operation fails or route is unknown
        """
        try:
            if route == "web.execute":
                return self._execute_via_web(payload)
            elif route == "web.list_operations":
                return self.list_all()
            elif route == "web.list_domains":
                return self._list_domains(payload)
            elif route == "web.start_console":
                return self._start_console(payload)
            elif route == "web.stop_console":
                return self._stop_console(payload)
            elif route == "web.get_stats":
                return self._get_stats(payload)
            elif route == "web.is_running":
                return self._is_running(payload)
            else:
                raise GatewayError(f"Unknown web route: {route}")

        except GatewayError:
            # Re-raise GatewayError as-is
            raise
        except Exception as e:
            raise GatewayError(f"Web gateway error: {e}") from e

    # ========================================================================
    # Route Implementations
    # ========================================================================

    def _execute_via_web(self, payload: dict) -> Dict[str, Any]:
        """Execute gateway operation via web console.

        This is a convenience method for executing operations through the
        web console without starting a server. Useful for testing and
        direct integration.

        Args:
            payload: {
                "route": str,  # Route to execute
                "params": dict  # Route parameters
            }

        Returns:
            Execution result

        Raises:
            GatewayError: If gateway not initialized or execution fails
        """
        if self.gateway is None:
            raise GatewayError("Gateway not initialized. Set gateway attribute first.")

        route = payload.get("route")
        if not route:
            raise GatewayError("Route is required")

        params = payload.get("params", {})

        try:
            result = self.gateway.execute(route, params)
            return {
                "success": True,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _list_domains(self, payload: dict) -> Dict[str, Any]:
        """List all registered domains.

        Args:
            payload: Empty dictionary

        Returns:
            Dictionary with list of domains

        Raises:
            GatewayError: If gateway not initialized
        """
        if self.gateway is None:
            raise GatewayError("Gateway not initialized. Set gateway attribute first.")

        if not hasattr(self.gateway, 'registry') or self.gateway.registry is None:
            raise GatewayError("Registry not initialized")

        domains = self.gateway.registry.list_domains()
        return {
            "domains": domains,
            "count": len(domains),
        }

    def _start_console(self, payload: dict) -> Dict[str, Any]:
        """Start web console server.

        Args:
            payload: {
                "host": str,  # Optional, default "127.0.0.1"
                "port": int,  # Optional, default 8080
                "background": bool  # Optional, default True
            }

        Returns:
            Dictionary with server information

        Raises:
            GatewayError: If console already running or fails to start
        """
        host = payload.get("host", "127.0.0.1")
        port = payload.get("port", 8080)
        background = payload.get("background", True)

        with self._console_lock:
            # Check if already running
            if self._console is not None:
                return {
                    "success": False,
                    "message": "Console already running",
                    "host": host,
                    "port": port,
                }

            try:
                # Create web console
                self._console = create_web_console(
                    gateway=self.gateway,
                    host=host,
                    port=port,
                )

                # Start server
                if background:
                    # Start in background thread
                    server_thread = threading.Thread(
                        target=self._console.serve_forever,
                        daemon=True,
                    )
                    server_thread.start()

                    return {
                        "success": True,
                        "message": f"Web console started on http://{host}:{port}",
                        "host": host,
                        "port": port,
                        "background": True,
                    }
                else:
                    # This will block - caller should handle this
                    return {
                        "success": True,
                        "message": f"Web console started on http://{host}:{port}",
                        "host": host,
                        "port": port,
                        "background": False,
                        "note": "Server will block in foreground",
                    }

            except Exception as e:
                self._console = None
                raise GatewayError(f"Failed to start web console: {e}") from e

    def _stop_console(self, payload: dict) -> Dict[str, Any]:
        """Stop web console server.

        Args:
            payload: Empty dictionary

        Returns:
            Dictionary with stop status

        Raises:
            GatewayError: If console not running or fails to stop
        """
        with self._console_lock:
            if self._console is None:
                return {
                    "success": False,
                    "message": "Console not running",
                }

            try:
                # Shutdown server
                if hasattr(self._console, 'server'):
                    self._console.server.shutdown()

                self._console = None

                return {
                    "success": True,
                    "message": "Web console stopped",
                }

            except Exception as e:
                raise GatewayError(f"Failed to stop web console: {e}") from e

    def _get_stats(self, payload: dict) -> Dict[str, Any]:
        """Get web console statistics.

        Args:
            payload: Empty dictionary

        Returns:
            Dictionary with console statistics
        """
        with self._console_lock:
            is_running = self._console is not None

            stats = {
                "console_running": is_running,
            }

            if is_running and self._console is not None:
                if hasattr(self._console, 'server'):
                    server = self._console.server
                    stats["server_address"] = server.server_address
                    stats["server_port"] = server.server_port

            return stats

    def _is_running(self, payload: dict) -> bool:
        """Check if web console is running.

        Args:
            payload: Empty dictionary

        Returns:
            True if console is running, False otherwise
        """
        with self._console_lock:
            return self._console is not None

    def list_all(self) -> Dict[str, Any]:
        """List all web gateway operations.

        Returns:
            Dictionary with operation metadata
        """
        return {
            "domain": "web",
            "description": "Web domain gateway for HTTP-based access to EE gateway system",
            "operations": [
                {
                    "route": "web.execute",
                    "description": "Execute gateway operation via web console",
                    "params": {
                        "route": "str (required) - Route to execute",
                        "params": "dict (optional) - Route parameters",
                    },
                },
                {
                    "route": "web.list_operations",
                    "description": "List all web gateway operations",
                    "params": {},
                },
                {
                    "route": "web.list_domains",
                    "description": "List all registered domains",
                    "params": {},
                },
                {
                    "route": "web.start_console",
                    "description": "Start web console server",
                    "params": {
                        "host": "str (optional) - Server host, default '127.0.0.1'",
                        "port": "int (optional) - Server port, default 8080",
                        "background": "bool (optional) - Run in background, default True",
                    },
                },
                {
                    "route": "web.stop_console",
                    "description": "Stop web console server",
                    "params": {},
                },
                {
                    "route": "web.get_stats",
                    "description": "Get web console statistics",
                    "params": {},
                },
                {
                    "route": "web.is_running",
                    "description": "Check if web console is running",
                    "params": {},
                },
            ],
        }


__all__ = [
    'WebGatewayDomain',
]
