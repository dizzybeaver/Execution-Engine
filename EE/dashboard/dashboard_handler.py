"""Dashboard Handler Module for EE.

This module provides HTTP request handling for the Dashboard Domain Gateway.
It implements GET and POST handlers for serving the web interface and processing
gateway requests.

Architecture Layer: Domain Gateway - Dashboard Domain - HTTP Handler

Based on:
    D:\\Code\\Project\\Gateway\\dashboard\\dashboard_handler.py

Integration:
    - Uses HTTP server from Python standard library
    - Integrates with EE gateway registry
    - Provides web UI and JSON API endpoints
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from dataclasses import dataclass
from typing import Any, Dict

from EE.dashboard.dashboard_common import DashboardRequestError


# ============================================================================
# Dashboard HTML Template
# ============================================================================

from EE.dashboard.dashboard_html import DASHBOARD_HTML



# ============================================================================
# Web Request and Response Data Classes
# ============================================================================

@dataclass
class DashboardRequest:
    """Represents an HTTP request to the Dashboard.

    Attributes:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        route: Extracted route (if /exec/ path)
        payload: Request payload as dictionary
    """
    method: str
    path: str
    route: str | None
    payload: Dict[str, Any]

    @staticmethod
    def parse(method: str, path: str, body: bytes) -> "DashboardRequest":
        """Parse an HTTP request into a DashboardRequest.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            body: Request body as bytes

        Returns:
            Parsed DashboardRequest instance

        Raises:
            DashboardRequestError: If request parsing fails
        """
        try:
            route = None
            if path.startswith("/exec/"):
                route = path[len("/exec/"):]

            payload = {}
            if body:
                try:
                    payload = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError as e:
                    raise DashboardRequestError(
                        message=f"Invalid JSON body: {e}",
                        method=method,
                        path=path,
                        context={"body_length": len(body)}
                    ) from e

            return DashboardRequest(
                method=method,
                path=path,
                route=route,
                payload=payload,
            )
        except DashboardRequestError:
            raise
        except Exception as e:
            raise DashboardRequestError(
                message=f"Failed to parse request: {e}",
                method=method,
                path=path,
            ) from e


@dataclass
class DashboardResponse:
    """Represents an HTTP response from the Dashboard.

    Attributes:
        status: HTTP status code
        body: Response body as dictionary
    """
    status: int
    body: Dict[str, Any]

    def to_http(self) -> bytes:
        """Convert response to HTTP body bytes.

        Returns:
            Response body as JSON bytes
        """
        return json.dumps(self.body, indent=2).encode("utf-8")


def success(body: Dict[str, Any]) -> DashboardResponse:
    """Create a successful response.

    Args:
        body: Response body dictionary

    Returns:
        DashboardResponse with status 200
    """
    return DashboardResponse(status=200, body={"data": body})


def error(message: str, status: int = 400) -> DashboardResponse:
    """Create an error response.

    Args:
        message: Error message
        status: HTTP status code (default: 400)

    Returns:
        DashboardResponse with error status
    """
    return DashboardResponse(status=status, body={"error": message})


# ============================================================================
# Dashboard HTTP Handler
# ============================================================================

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the EE Dashboard.

    This handler serves both the web UI and JSON API endpoints for interacting
    with the EE Universal Gateway.

    Class Attributes:
        gateway_registry: EEDomainRegistry instance (injected at server creation)

    GET Endpoints:
        / or /index.html: Serve dashboard web UI
        /list-domains: List all registered gateway domains
        /list-routes: List all routes for all domains
        /health: Health check endpoint

    POST Endpoints:
        /exec/{route}: Execute a gateway route with JSON payload

    Based on:
        D:\\Code\\Project\\Gateway\\dashboard\\dashboard_handler.py
    """

    # Class-level attribute to be injected by server factory
    gateway_registry = None

    def _send_response(self, response: DashboardResponse) -> None:
        """Send HTTP response to client.

        Args:
            response: DashboardResponse to send
        """
        self.send_response(response.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response.to_http())

    def _send_html(self, html_content: str) -> None:
        """Send HTML response to client.

        Args:
            html_content: HTML content to send
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def do_OPTIONS(self) -> None:
        """Handle OPTIONS request for CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        """Handle GET requests.

        Routes:
            /: Serve dashboard web UI
            /index.html: Serve dashboard web UI
            /list-domains: List all registered domains
            /list-routes: List all routes for all domains
            /health: Health check
        """
        try:
            # Serve web UI
            if self.path == "/" or self.path == "/index.html":
                self._send_html(DASHBOARD_HTML)
                return

            # Health check
            if self.path == "/health":
                self._send_response(success({
                    "status": "healthy",
                    "service": "EE Dashboard",
                    "registry_initialized": self.gateway_registry is not None
                }))
                return

            # List all domains
            if self.path == "/list-domains":
                if self.gateway_registry is None:
                    self._send_response(error("Gateway registry not initialized", 500))
                    return

                domains = self.gateway_registry.list_domains()
                self._send_response(success(domains))
                return

            # List all routes
            if self.path == "/list-routes":
                if self.gateway_registry is None:
                    self._send_response(error("Gateway registry not initialized", 500))
                    return

                all_operations = self.gateway_registry.list_all_operations()
                # Extract routes from operations
                routes_by_domain = {}
                for domain_name, domain_info in all_operations.items():
                    if "operations" in domain_info:
                        routes = {}
                        for op in domain_info["operations"]:
                            route = op.get("route", "")
                            if "." in route:
                                # Extract route part after domain
                                route_parts = route.split(".", 1)
                                if len(route_parts) > 1:
                                    route_name = route_parts[1]
                                    routes[route_name] = op.get("description", "")
                        routes_by_domain[domain_name] = routes

                self._send_response(success(routes_by_domain))
                return

            # Unknown endpoint
            self._send_response(error(f"Unknown GET endpoint: {self.path}", 404))

        except Exception as e:
            self._send_response(error(f"Internal server error: {e}", 500))

    def do_POST(self) -> None:
        """Handle POST requests.

        Routes:
            /exec/{route}: Execute a gateway route

        Request body should be JSON with optional payload.
        """
        try:
            # Read request body
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length > 0 else b""

            # Parse request
            req = DashboardRequest.parse("POST", self.path, body)

            # Execute route
            if req.route:
                if self.gateway_registry is None:
                    self._send_response(error("Gateway registry not initialized", 500))
                    return

                # Parse route to domain and operation
                route_parts = req.route.split(".", 1)
                if len(route_parts) != 2:
                    self._send_response(error(f"Invalid route format: {req.route}. Expected: domain.operation", 400))
                    return

                domain_name, operation = route_parts

                # Check if domain exists
                if not self.gateway_registry.has_domain(domain_name):
                    available = self.gateway_registry.list_domains()
                    self._send_response(error(
                        f"Domain '{domain_name}' not found. Available: {available}",
                        404
                    ))
                    return

                # Get domain gateway and execute
                domain_gateway = self.gateway_registry.get(domain_name)
                full_route = f"{domain_name}.{operation}"

                try:
                    result = domain_gateway.execute(full_route, req.payload)
                    self._send_response(success(result))
                except Exception as e:
                    self._send_response(error(f"Execution error: {e}", 500))
                return

            # Unknown endpoint
            self._send_response(error(f"Unknown POST endpoint: {self.path}", 404))

        except DashboardRequestError as e:
            self._send_response(error(str(e), 400))
        except Exception as e:
            self._send_response(error(f"Internal server error: {e}", 500))

    def log_message(self, format: str, *args) -> None:
        """Log HTTP request (override to customize logging)."""
        # Suppress default logging or customize as needed
        pass


__all__ = [
    'DashboardHandler',
    'DashboardRequest',
    'DashboardResponse',
    'success',
    'error',
]
