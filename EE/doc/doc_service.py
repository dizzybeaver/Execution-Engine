"""
Service Documentation Generator - EE Doc Gateway

This module provides documentation generation for EE gateway services.
It extracts service information and generates comprehensive documentation.

Based on:
D:\\Code\\Project\\Gateway\\Doc\\doc_service.py
"""

from __future__ import annotations

from typing import Any, Dict, List
from dataclasses import dataclass
import json


@dataclass
class ServiceInfo:
    """Information about a gateway service.

    Attributes:
        name: Service name
        domain: Domain name
        description: Service description
        methods: List of service methods
        dependencies: List of service dependencies
        configuration: Service configuration
    """

    name: str
    domain: str
    description: str
    methods: List[Dict[str, Any]]
    dependencies: List[str]
    configuration: Dict[str, Any]


class ServiceDocGenerator:
    """Generate documentation for gateway services.

    This generator extracts service information from domain gateways and
    produces structured documentation in multiple formats.

    Attributes:
        gateway_registry: EE domain registry instance

    Examples:
        >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
        >>> registry = EEDomainRegistry.get_instance()
        >>> generator = ServiceDocGenerator(registry)
        >>> docs = generator.generate_markdown()
        >>> print(docs)
        # Services Documentation...
    """

    def __init__(self, gateway_registry: Any):
        """Initialize service documentation generator.

        Args:
            gateway_registry: EE domain registry instance
        """
        self.registry = gateway_registry

    def extract_services(self) -> List[ServiceInfo]:
        """Extract service information from all domains.

        Returns:
            List of service information objects
        """
        services = []

        for domain_name in self.registry.list_domains():
            try:
                gateway = self.registry.get(domain_name)
                all_info = gateway.list_all()

                # Check if domain has services
                if "services" in all_info:
                    for svc in all_info["services"]:
                        service = ServiceInfo(
                            name=svc.get("name", "unknown"),
                            domain=domain_name,
                            description=svc.get("description", ""),
                            methods=svc.get("methods", []),
                            dependencies=svc.get("dependencies", []),
                            configuration=svc.get("configuration", {})
                        )
                        services.append(service)
                else:
                    # Create service from domain operations
                    service = ServiceInfo(
                        name=domain_name,
                        domain=domain_name,
                        description=f"{domain_name.title()} domain service",
                        methods=all_info.get("operations", []),
                        dependencies=[],
                        configuration={}
                    )
                    services.append(service)

            except Exception as e:
                # Skip domains that fail to load
                continue

        return services

    def generate_markdown(self) -> str:
        """Generate service documentation in Markdown format.

        Returns:
            Markdown documentation string
        """
        services = self.extract_services()
        lines = []

        lines.append("# EE Gateway Services Documentation")
        lines.append("")
        lines.append("This document provides comprehensive documentation for all EE gateway services.")
        lines.append("")
        lines.append("---")
        lines.append("")

        for service in services:
            lines.append(f"## {service.name} Service")
            lines.append("")
            lines.append(f"**Domain:** {service.domain}")
            lines.append("")
            lines.append(f"**Description:** {service.description}")
            lines.append("")

            if service.dependencies:
                lines.append("**Dependencies:**")
                lines.append("")
                for dep in service.dependencies:
                    lines.append(f"- {dep}")
                lines.append("")

            if service.configuration:
                lines.append("**Configuration:**")
                lines.append("")
                lines.append("| Key | Value | Description |")
                lines.append("|-----|-------|-------------|")

                for key, value in service.configuration.items():
                    if isinstance(value, dict):
                        desc = value.get("description", "")
                        val = value.get("default", "")
                    else:
                        desc = ""
                        val = str(value)

                    lines.append(f"| {key} | {val} | {desc} |")

                lines.append("")

            if service.methods:
                lines.append("**Methods:**")
                lines.append("")

                for method in service.methods:
                    method_name = method.get("route", method.get("name", "unknown"))
                    method_desc = method.get("description", "")
                    lines.append(f"- **{method_name}**: {method_desc}")

                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def generate_json(self) -> str:
        """Generate service documentation in JSON format.

        Returns:
            JSON documentation string
        """
        services = self.extract_services()

        # Convert to serializable format
        serializable = [
            {
                "name": service.name,
                "domain": service.domain,
                "description": service.description,
                "methods": service.methods,
                "dependencies": service.dependencies,
                "configuration": service.configuration,
            }
            for service in services
        ]

        return json.dumps(serializable, indent=2)

    def generate_html(self) -> str:
        """Generate service documentation in HTML format.

        Returns:
            HTML documentation string
        """
        services = self.extract_services()
        lines = []

        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append("<title>EE Gateway Services Documentation</title>")
        lines.append("<style>")
        lines.append("body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }")
        lines.append("h1 { color: #333; border-bottom: 2px solid #333; }")
        lines.append("h2 { color: #555; margin-top: 30px; }")
        lines.append("table { border-collapse: collapse; width: 100%; margin: 10px 0; }")
        lines.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        lines.append("th { background-color: #4CAF50; color: white; }")
        lines.append("tr:nth-child(even) { background-color: #f2f2f2; }")
        lines.append("ul { line-height: 1.6; }")
        lines.append("</style>")
        lines.append("</head>")
        lines.append("<body>")
        lines.append("<h1>EE Gateway Services Documentation</h1>")
        lines.append("<p>This document provides comprehensive documentation for all EE gateway services.</p>")
        lines.append("<hr>")

        for service in services:
            lines.append(f"<h2>{service.name} Service</h2>")
            lines.append(f"<p><strong>Domain:</strong> {service.domain}</p>")
            lines.append(f"<p><strong>Description:</strong> {service.description}</p>")

            if service.dependencies:
                lines.append("<p><strong>Dependencies:</strong></p>")
                lines.append("<ul>")
                for dep in service.dependencies:
                    lines.append(f"<li>{dep}</li>")
                lines.append("</ul>")

            if service.configuration:
                lines.append("<p><strong>Configuration:</strong></p>")
                lines.append("<table>")
                lines.append("<tr><th>Key</th><th>Value</th><th>Description</th></tr>")

                for key, value in service.configuration.items():
                    if isinstance(value, dict):
                        desc = value.get("description", "")
                        val = value.get("default", "")
                    else:
                        desc = ""
                        val = str(value)

                    lines.append(f"<tr><td>{key}</td><td>{val}</td><td>{desc}</td></tr>")

                lines.append("</table>")

            if service.methods:
                lines.append("<p><strong>Methods:</strong></p>")
                lines.append("<ul>")

                for method in service.methods:
                    method_name = method.get("route", method.get("name", "unknown"))
                    method_desc = method.get("description", "")
                    lines.append(f"<li><strong>{method_name}</strong>: {method_desc}</li>")

                lines.append("</ul>")

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
    'ServiceInfo',
    'ServiceDocGenerator',
]
