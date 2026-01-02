"""
Web Handler Module - EE Web Domain Gateway

This module provides HTTP request handling for the Web domain gateway.
It implements the HTTP server logic and routes requests to the gateway system.

Architecture Layer: Layer 1 - Domain Gateway Infrastructure
Part of: Web Domain Gateway (gateway.web)

Based on: D:\\Code\\Project\\Gateway\\Web\\web_handler.py
"""

from __future__ import annotations
from http.server import BaseHTTPRequestHandler
from typing import Any, Optional, Callable
import logging

from EE.web.web_request import WebRequest
from EE.web.web_response import (
    WebResponse,
    success_response,
    error_response,
    not_found_response,
    server_error_response,
)
from EE.web.web_common import WebConsoleError, RouteExecutionError

logger = logging.getLogger(__name__)


class WebHandler(BaseHTTPRequestHandler):
    """HTTP request handler for EE Web Console.

    This handler processes HTTP GET and POST requests and routes them
    to the EE gateway system for execution. It supports:

    - GET /list-all: List all gateway operations
    - GET /list-domains: List all registered domains
    - GET /list-routes: List all routes
    - GET /stats: Get gateway statistics
    - POST /exec/{route}: Execute gateway route
    - POST /exec-domain/{domain}/{operation}: Execute domain operation

    The handler requires a gateway instance to be set as a class variable
    before the HTTP server starts.

    Attributes:
        gateway: EE gateway instance (set as class variable)
        registry: EE domain registry (set as class variable)

    Example:
        >>> handler = WebHandler
        >>> handler.gateway = my_gateway
        >>> handler.registry = my_registry
        >>> # Start HTTP server with this handler
    """

    # Class variables set by WebConsoleFactory
    gateway: Optional[Any] = None
    registry: Optional[Any] = None

    def _send_response(self, response: WebResponse) -> None:
        """Send HTTP response to client.

        Args:
            response: WebResponse object to send
        """
        # Send status code
        self.send_response(response.status)

        # Send headers
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

        # Add custom headers if present
        if response.headers:
            for header_name, header_value in response.headers.items():
                self.send_header(header_name, header_value)

        self.end_headers()

        # Send body
        self.wfile.write(response.to_http())

    def _handle_error(self, error: Exception, status: int = 500) -> None:
        """Handle error and send error response.

        Args:
            error: Exception that occurred
            status: HTTP status code (default: 500)
        """
        logger.error(f"Error handling request: {error}", exc_info=error)

        if isinstance(error, WebConsoleError):
            response = error_response(
                message=error.message,
                status=error.http_status,
                error_code=error.error_code,
                context=error.context,
            )
        else:
            response = server_error_response(
                message=str(error),
                original_error=error,
            )

        self._send_response(response)

    def do_GET(self) -> None:
        """Handle HTTP GET requests."""
        try:
            # Route: GET /list-all
            if self.path == "/list-all":
                self._handle_list_all()
                return

            # Route: GET /list-domains
            if self.path == "/list-domains":
                self._handle_list_domains()
                return

            # Route: GET /list-routes
            if self.path == "/list-routes":
                self._handle_list_routes()
                return

            # Route: GET /stats
            if self.path == "/stats":
                self._handle_get_stats()
                return

            # Route: GET /health
            if self.path == "/health":
                self._handle_health_check()
                return

            # Unknown route
            self._send_response(
                not_found_response(
                    resource_type="endpoint",
                    resource_id=self.path,
                    available_resources=[
                        "/list-all",
                        "/list-domains",
                        "/list-routes",
                        "/stats",
                        "/health",
                    ],
                )
            )

        except Exception as e:
            self._handle_error(e)

    def do_POST(self) -> None:
        """Handle HTTP POST requests."""
        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length > 0 else b""

            # Parse request
            request = WebRequest.parse("POST", self.path, body)

            # Route: POST /exec/{route}
            if request.route:
                self._handle_execute_route(request)
                return

            # Unknown route
            self._send_response(
                not_found_response(
                    resource_type="endpoint",
                    resource_id=self.path,
                )
            )

        except WebConsoleError as e:
            self._handle_error(e, e.http_status)
        except Exception as e:
            self._handle_error(e)

    def do_OPTIONS(self) -> None:
        """Handle HTTP OPTIONS requests (CORS preflight)."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _handle_list_all(self) -> None:
        """Handle GET /list-all - List all gateway operations."""
        if self.gateway is None:
            raise WebConsoleError(
                message="Gateway not initialized",
                http_status=503,
                error_code="GATEWAY_NOT_INITIALIZED",
            )

        result = self.gateway.list_all()
        self._send_response(success_response(result))

    def _handle_list_domains(self) -> None:
        """Handle GET /list-domains - List all registered domains."""
        if self.registry is None:
            raise WebConsoleError(
                message="Registry not initialized",
                http_status=503,
                error_code="REGISTRY_NOT_INITIALIZED",
            )

        domains = self.registry.list_domains()
        self._send_response(success_response({"domains": domains}))

    def _handle_list_routes(self) -> None:
        """Handle GET /list-routes - List all routes from all domains."""
        if self.registry is None:
            raise WebConsoleError(
                message="Registry not initialized",
                http_status=503,
                error_code="REGISTRY_NOT_INITIALIZED",
            )

        all_operations = self.registry.list_all_operations()
        self._send_response(success_response(all_operations))

    def _handle_get_stats(self) -> None:
        """Handle GET /stats - Get gateway statistics."""
        if self.registry is None:
            raise WebConsoleError(
                message="Registry not initialized",
                http_status=503,
                error_code="REGISTRY_NOT_INITIALIZED",
            )

        stats = self.registry.get_stats()
        self._send_response(success_response(stats))

    def _handle_health_check(self) -> None:
        """Handle GET /health - Health check endpoint."""
        health = {
            "status": "healthy",
            "gateway_initialized": self.gateway is not None,
            "registry_initialized": self.registry is not None,
        }

        if self.registry is not None:
            health["domains_count"] = len(self.registry.list_domains())

        self._send_response(success_response(health))

    def _handle_execute_route(self, request: WebRequest) -> None:
        """Handle POST /exec/{route} - Execute gateway route.

        Args:
            request: Parsed WebRequest object
        """
        if self.gateway is None:
            raise WebConsoleError(
                message="Gateway not initialized",
                http_status=503,
                error_code="GATEWAY_NOT_INITIALIZED",
            )

        if not request.route:
            raise WebConsoleError(
                message="Route is required for execution",
                http_status=400,
                error_code="MISSING_ROUTE",
            )

        try:
            # Execute route through gateway
            result = self.gateway.execute(request.route, request.payload)
            self._send_response(success_response({"result": result}))

        except Exception as e:
            raise RouteExecutionError(
                route=request.route,
                original_error=e,
            ) from e

    def log_message(self, format: str, *args) -> None:
        """Override log_message to use logging module."""
        logger.info(f"{self.address_string()} - {format % args}")


__all__ = [
    'WebHandler',
]
