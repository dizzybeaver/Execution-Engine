"""
Command Documentation Generator - EE Doc Gateway

This module provides documentation generation for EE gateway commands.
It extracts command information and generates comprehensive documentation.

Based on:
D:\\Code\\Project\\Gateway\\Doc\\doc_command.py
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import json


@dataclass
class CommandInfo:
    """Information about a gateway command.

    Attributes:
        name: Command name
        description: Command description
        parameters: List of command parameters
        returns: Return type description
        examples: List of usage examples
    """

    name: str
    description: str
    parameters: List[Dict[str, Any]]
    returns: str
    examples: List[Dict[str, Any]]


class CommandDocGenerator:
    """Generate documentation for gateway commands.

    This generator extracts command information from domain gateways and
    produces structured documentation in multiple formats.

    Attributes:
        gateway_registry: EE domain registry instance

    Examples:
        >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
        >>> registry = EEDomainRegistry.get_instance()
        >>> generator = CommandDocGenerator(registry)
        >>> docs = generator.generate_markdown()
        >>> print(docs)
        # Commands Documentation...
    """

    def __init__(self, gateway_registry: Any):
        """Initialize command documentation generator.

        Args:
            gateway_registry: EE domain registry instance
        """
        self.registry = gateway_registry

    def extract_commands(self) -> Dict[str, List[CommandInfo]]:
        """Extract command information from all domains.

        Returns:
            Dictionary mapping domain names to command lists
        """
        commands = {}

        for domain_name in self.registry.list_domains():
            try:
                gateway = self.registry.get(domain_name)
                all_info = gateway.list_all()

                if "operations" in all_info:
                    domain_commands = []
                    for op in all_info["operations"]:
                        cmd = CommandInfo(
                            name=op.get("route", "unknown"),
                            description=op.get("description", ""),
                            parameters=op.get("params", {}),
                            returns=op.get("returns", "Any"),
                            examples=op.get("examples", [])
                        )
                        domain_commands.append(cmd)
                    commands[domain_name] = domain_commands

            except Exception as e:
                # Skip domains that fail to load
                continue

        return commands

    def generate_markdown(self) -> str:
        """Generate command documentation in Markdown format.

        Returns:
            Markdown documentation string
        """
        commands = self.extract_commands()
        lines = []

        lines.append("# EE Gateway Commands Documentation")
        lines.append("")
        lines.append("This document provides comprehensive documentation for all EE gateway commands.")
        lines.append("")
        lines.append("---")
        lines.append("")

        for domain_name, domain_commands in commands.items():
            lines.append(f"## {domain_name.title()} Domain")
            lines.append("")

            for cmd in domain_commands:
                lines.append(f"### {cmd.name}")
                lines.append("")
                lines.append(f"**Description:** {cmd.description}")
                lines.append("")

                if cmd.parameters:
                    lines.append("**Parameters:**")
                    lines.append("")
                    lines.append("| Parameter | Type | Description |")
                    lines.append("|-----------|------|-------------|")

                    for param_name, param_info in cmd.parameters.items():
                        if isinstance(param_info, dict):
                            param_type = param_info.get("type", "any")
                            param_desc = param_info.get("description", "")
                        else:
                            param_type = str(param_info)
                            param_desc = ""

                        lines.append(f"| {param_name} | {param_type} | {param_desc} |")

                    lines.append("")

                lines.append(f"**Returns:** {cmd.returns}")
                lines.append("")

                if cmd.examples:
                    lines.append("**Examples:**")
                    lines.append("")

                    for example in cmd.examples:
                        if "code" in example:
                            lines.append("```python")
                            lines.append(example["code"])
                            lines.append("```")
                            lines.append("")

                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def generate_json(self) -> str:
        """Generate command documentation in JSON format.

        Returns:
            JSON documentation string
        """
        commands = self.extract_commands()

        # Convert to serializable format
        serializable = {}
        for domain_name, domain_commands in commands.items():
            serializable[domain_name] = [
                {
                    "name": cmd.name,
                    "description": cmd.description,
                    "parameters": cmd.parameters,
                    "returns": cmd.returns,
                    "examples": cmd.examples,
                }
                for cmd in domain_commands
            ]

        return json.dumps(serializable, indent=2)

    def generate_html(self) -> str:
        """Generate command documentation in HTML format.

        Returns:
            HTML documentation string
        """
        commands = self.extract_commands()
        lines = []

        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append("<title>EE Gateway Commands Documentation</title>")
        lines.append("<style>")
        lines.append("body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }")
        lines.append("h1 { color: #333; border-bottom: 2px solid #333; }")
        lines.append("h2 { color: #555; margin-top: 30px; }")
        lines.append("h3 { color: #777; }")
        lines.append("table { border-collapse: collapse; width: 100%; margin: 10px 0; }")
        lines.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        lines.append("th { background-color: #4CAF50; color: white; }")
        lines.append("tr:nth-child(even) { background-color: #f2f2f2; }")
        lines.append("pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }")
        lines.append("</style>")
        lines.append("</head>")
        lines.append("<body>")
        lines.append("<h1>EE Gateway Commands Documentation</h1>")
        lines.append("<p>This document provides comprehensive documentation for all EE gateway commands.</p>")
        lines.append("<hr>")

        for domain_name, domain_commands in commands.items():
            lines.append(f"<h2>{domain_name.title()} Domain</h2>")

            for cmd in domain_commands:
                lines.append(f"<h3>{cmd.name}</h3>")
                lines.append(f"<p><strong>Description:</strong> {cmd.description}</p>")

                if cmd.parameters:
                    lines.append("<p><strong>Parameters:</strong></p>")
                    lines.append("<table>")
                    lines.append("<tr><th>Parameter</th><th>Type</th><th>Description</th></tr>")

                    for param_name, param_info in cmd.parameters.items():
                        if isinstance(param_info, dict):
                            param_type = param_info.get("type", "any")
                            param_desc = param_info.get("description", "")
                        else:
                            param_type = str(param_info)
                            param_desc = ""

                        lines.append(f"<tr><td>{param_name}</td><td>{param_type}</td><td>{param_desc}</td></tr>")

                    lines.append("</table>")

                lines.append(f"<p><strong>Returns:</strong> {cmd.returns}</p>")
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
    'CommandInfo',
    'CommandDocGenerator',
]
