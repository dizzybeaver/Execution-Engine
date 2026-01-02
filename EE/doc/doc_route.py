"""
Route Documentation Generator - EE Doc Gateway

This module provides documentation generation for EE gateway routes.
It extracts route information and generates comprehensive documentation.

Based on:
D:\\Code\\Project\\Gateway\\Doc\\doc_route.py
"""

from __future__ import annotations

from typing import Any, Dict, List
from dataclasses import dataclass
import json


@dataclass
class RouteInfo:
    """Information about a gateway route.

    Attributes:
        route: Route identifier
        domain: Domain name
        description: Route description
        parameters: Route parameters
        returns: Return type description
        middleware: List of middleware applied
    """

    route: str
    domain: str
    description: str
    parameters: Dict[str, Any]
    returns: str
    middleware: List[str]


class RouteDocGenerator:
    """Generate documentation for gateway routes.

    This generator extracts route information from domain gateways and
    produces structured documentation in multiple formats.

    Attributes:
        gateway_registry: EE domain registry instance

    Examples:
        >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
        >>> registry = EEDomainRegistry.get_instance()
        >>> generator = RouteDocGenerator(registry)
        >>> docs = generator.generate_markdown()
        >>> print(docs)
        # Routes Documentation...
    """

    def __init__(self, gateway_registry: Any):
        """Initialize route documentation generator.

        Args:
            gateway_registry: EE domain registry instance
        """
        self.registry = gateway_registry

    def extract_routes(self) -> List[RouteInfo]:
        """Extract route information from all domains.

        Returns:
            List of route information objects
        """
        routes = []

        for domain_name in self.registry.list_domains():
            try:
                gateway = self.registry.get(domain_name)
                all_info = gateway.list_all()

                if "operations" in all_info:
                    for op in all_info["operations"]:
                        route = RouteInfo(
                            route=op.get("route", "unknown"),
                            domain=domain_name,
                            description=op.get("description", ""),
                            parameters=op.get("params", {}),
                            returns=op.get("returns", "Any"),
                            middleware=op.get("middleware", [])
                        )
                        routes.append(route)

            except Exception as e:
                # Skip domains that fail to load
                continue

        return routes

    def generate_markdown(self) -> str:
        """Generate route documentation in Markdown format.

        Returns:
            Markdown documentation string
        """
        routes = self.extract_routes()
        lines = []

        lines.append("# EE Gateway Routes Documentation")
        lines.append("")
        lines.append("This document provides comprehensive documentation for all EE gateway routes.")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Group by domain
        routes_by_domain: Dict[str, List[RouteInfo]] = {}
        for route in routes:
            if route.domain not in routes_by_domain:
                routes_by_domain[route.domain] = []
            routes_by_domain[route.domain].append(route)

        for domain_name, domain_routes in sorted(routes_by_domain.items()):
            lines.append(f"## {domain_name.title()} Routes")
            lines.append("")
            lines.append(f"Total routes: {len(domain_routes)}")
            lines.append("")

            for route in domain_routes:
                lines.append(f"### {route.route}")
                lines.append("")
                lines.append(f"**Description:** {route.description}")
                lines.append("")
                lines.append(f"**Domain:** {route.domain}")
                lines.append("")

                if route.parameters:
                    lines.append("**Parameters:**")
                    lines.append("")
                    lines.append("| Parameter | Type | Required | Description |")
                    lines.append("|-----------|------|----------|-------------|")

                    for param_name, param_info in route.parameters.items():
                        if isinstance(param_info, dict):
                            param_type = param_info.get("type", "any")
                            param_required = param_info.get("required", False)
                            param_desc = param_info.get("description", "")
                        else:
                            param_type = str(param_info)
                            param_required = False
                            param_desc = ""

                        required_mark = "Yes" if param_required else "No"
                        lines.append(f"| {param_name} | {param_type} | {required_mark} | {param_desc} |")

                    lines.append("")

                lines.append(f"**Returns:** {route.returns}")
                lines.append("")

                if route.middleware:
                    lines.append("**Middleware:**")
                    lines.append("")
                    for mw in route.middleware:
                        lines.append(f"- {mw}")
                    lines.append("")

                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def generate_json(self) -> str:
        """Generate route documentation in JSON format.

        Returns:
            JSON documentation string
        """
        routes = self.extract_routes()

        # Convert to serializable format
        serializable = [
            {
                "route": route.route,
                "domain": route.domain,
                "description": route.description,
                "parameters": route.parameters,
                "returns": route.returns,
                "middleware": route.middleware,
            }
            for route in routes
        ]

        return json.dumps(serializable, indent=2)

    def generate_html(self) -> str:
        """Generate route documentation in HTML format.

        Returns:
            HTML documentation string
        """
        routes = self.extract_routes()
        lines = []

        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append("<title>EE Gateway Routes Documentation</title>")
        lines.append("<style>")
        lines.append("body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }")
        lines.append("h1 { color: #333; border-bottom: 2px solid #333; }")
        lines.append("h2 { color: #555; margin-top: 30px; }")
        lines.append("h3 { color: #777; }")
        lines.append("table { border-collapse: collapse; width: 100%; margin: 10px 0; }")
        lines.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        lines.append("th { background-color: #4CAF50; color: white; }")
        lines.append("tr:nth-child(even) { background-color: #f2f2f2; }")
        lines.append(".badge { display: inline-block; padding: 3px 8px; font-size: 12px; border-radius: 3px; }")
        lines.append(".badge-yes { background-color: #4CAF50; color: white; }")
        lines.append(".badge-no { background-color: #f44336; color: white; }")
        lines.append("</style>")
        lines.append("</head>")
        lines.append("<body>")
        lines.append("<h1>EE Gateway Routes Documentation</h1>")
        lines.append("<p>This document provides comprehensive documentation for all EE gateway routes.</p>")
        lines.append("<hr>")

        # Group by domain
        routes_by_domain: Dict[str, List[RouteInfo]] = {}
        for route in routes:
            if route.domain not in routes_by_domain:
                routes_by_domain[route.domain] = []
            routes_by_domain[route.domain].append(route)

        for domain_name, domain_routes in sorted(routes_by_domain.items()):
            lines.append(f"<h2>{domain_name.title()} Routes</h2>")
            lines.append(f"<p>Total routes: {len(domain_routes)}</p>")

            for route in domain_routes:
                lines.append(f"<h3>{route.route}</h3>")
                lines.append(f"<p><strong>Description:</strong> {route.description}</p>")
                lines.append(f"<p><strong>Domain:</strong> {route.domain}</p>")

                if route.parameters:
                    lines.append("<p><strong>Parameters:</strong></p>")
                    lines.append("<table>")
                    lines.append("<tr><th>Parameter</th><th>Type</th><th>Required</th><th>Description</th></tr>")

                    for param_name, param_info in route.parameters.items():
                        if isinstance(param_info, dict):
                            param_type = param_info.get("type", "any")
                            param_required = param_info.get("required", False)
                            param_desc = param_info.get("description", "")
                        else:
                            param_type = str(param_info)
                            param_required = False
                            param_desc = ""

                        required_class = "badge-yes" if param_required else "badge-no"
                        required_text = "Yes" if param_required else "No"
                        lines.append(f"<tr><td>{param_name}</td><td>{param_type}</td><td><span class='badge {required_class}'>{required_text}</span></td><td>{param_desc}</td></tr>")

                    lines.append("</table>")

                lines.append(f"<p><strong>Returns:</strong> {route.returns}</p>")
                lines.append("<hr>")

        lines.append("</body>")
        lines.append("</html>")

        return "\n".join(lines)

    def save_documentation(self, output_path: str, format: str = "markdown") -> None:
        """Save documentation to file.

        Args:
            output_path: Path to output file
            format: Output format (markdown, json, html)

        Raises:
            DocFormatError: If format is not supported
        """
        if format == "markdown":
            content = self.generate_markdown()
            if not output_path.endswith(".md"):
                output_path += ".md"
        elif format == "json":
            content = self.generate_json()
            if not output_path.endswith(".json"):
                output_path += ".json"
        elif format == "html":
            content = self.generate_html()
            if not output_path.endswith(".html"):
                output_path += ".html"
        else:
            from EE.doc.doc_common import DocFormatError
            raise DocFormatError(f"Unsupported format: {format}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)


__all__ = [
    'RouteInfo',
    'RouteDocGenerator',
]
