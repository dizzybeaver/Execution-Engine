"""
Schema Documentation Generator - EE Doc Gateway

This module provides documentation generation for EE gateway schemas.
It extracts schema information and generates comprehensive documentation.

Based on:
D:\\Code\\Project\\Gateway\\Doc\\doc_schema.py
"""

from __future__ import annotations

from typing import Any, Dict, List
from dataclasses import dataclass
import json


@dataclass
class SchemaField:
    """Information about a schema field.

    Attributes:
        name: Field name
        type: Field type
        required: Whether field is required
        description: Field description
        default: Default value
        constraints: Field constraints
    """

    name: str
    type: str
    required: bool
    description: str
    default: Any
    constraints: Dict[str, Any]


@dataclass
class SchemaInfo:
    """Information about a gateway schema.

    Attributes:
        name: Schema name
        domain: Domain name
        description: Schema description
        fields: List of schema fields
        examples: List of example data
    """

    name: str
    domain: str
    description: str
    fields: List[SchemaField]
    examples: List[Dict[str, Any]]


class SchemaDocGenerator:
    """Generate documentation for gateway schemas.

    This generator extracts schema information from domain gateways and
    produces structured documentation in multiple formats.

    Attributes:
        gateway_registry: EE domain registry instance

    Examples:
        >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
        >>> registry = EEDomainRegistry.get_instance()
        >>> generator = SchemaDocGenerator(registry)
        >>> docs = generator.generate_markdown()
        >>> print(docs)
        # Schemas Documentation...
    """

    def __init__(self, gateway_registry: Any):
        """Initialize schema documentation generator.

        Args:
            gateway_registry: EE domain registry instance
        """
        self.registry = gateway_registry

    def extract_schemas(self) -> List[SchemaInfo]:
        """Extract schema information from all domains.

        Returns:
            List of schema information objects
        """
        schemas = []

        for domain_name in self.registry.list_domains():
            try:
                gateway = self.registry.get(domain_name)
                all_info = gateway.list_all()

                # Check if domain has schemas
                if "schemas" in all_info:
                    for schema_data in all_info["schemas"]:
                        fields = []
                        for field_name, field_info in schema_data.get("fields", {}).items():
                            if isinstance(field_info, dict):
                                field = SchemaField(
                                    name=field_name,
                                    type=field_info.get("type", "any"),
                                    required=field_info.get("required", False),
                                    description=field_info.get("description", ""),
                                    default=field_info.get("default", None),
                                    constraints=field_info.get("constraints", {})
                                )
                            else:
                                field = SchemaField(
                                    name=field_name,
                                    type=str(field_info),
                                    required=False,
                                    description="",
                                    default=None,
                                    constraints={}
                                )
                            fields.append(field)

                        schema = SchemaInfo(
                            name=schema_data.get("name", "unknown"),
                            domain=domain_name,
                            description=schema_data.get("description", ""),
                            fields=fields,
                            examples=schema_data.get("examples", [])
                        )
                        schemas.append(schema)

            except Exception as e:
                # Skip domains that fail to load
                continue

        return schemas

    def generate_markdown(self) -> str:
        """Generate schema documentation in Markdown format.

        Returns:
            Markdown documentation string
        """
        schemas = self.extract_schemas()
        lines = []

        lines.append("# EE Gateway Schemas Documentation")
        lines.append("")
        lines.append("This document provides comprehensive documentation for all EE gateway schemas.")
        lines.append("")
        lines.append("---")
        lines.append("")

        for schema in schemas:
            lines.append(f"## {schema.name} Schema")
            lines.append("")
            lines.append(f"**Domain:** {schema.domain}")
            lines.append("")
            lines.append(f"**Description:** {schema.description}")
            lines.append("")

            if schema.fields:
                lines.append("**Fields:**")
                lines.append("")
                lines.append("| Field | Type | Required | Description | Default | Constraints |")
                lines.append("|-------|------|----------|-------------|---------|-------------|")

                for field in schema.fields:
                    required_mark = "Yes" if field.required else "No"
                    default_val = str(field.default) if field.default is not None else "-"
                    constraints_str = ", ".join(f"{k}={v}" for k, v in field.constraints.items()) if field.constraints else "-"

                    lines.append(f"| {field.name} | {field.type} | {required_mark} | {field.description} | {default_val} | {constraints_str} |")

                lines.append("")

            if schema.examples:
                lines.append("**Examples:**")
                lines.append("")

                for i, example in enumerate(schema.examples, 1):
                    lines.append(f"Example {i}:")
                    lines.append("```json")
                    lines.append(json.dumps(example, indent=2))
                    lines.append("```")
                    lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def generate_json(self) -> str:
        """Generate schema documentation in JSON format.

        Returns:
            JSON documentation string
        """
        schemas = self.extract_schemas()

        # Convert to serializable format
        serializable = []
        for schema in schemas:
            schema_dict = {
                "name": schema.name,
                "domain": schema.domain,
                "description": schema.description,
                "fields": [
                    {
                        "name": field.name,
                        "type": field.type,
                        "required": field.required,
                        "description": field.description,
                        "default": field.default,
                        "constraints": field.constraints,
                    }
                    for field in schema.fields
                ],
                "examples": schema.examples,
            }
            serializable.append(schema_dict)

        return json.dumps(serializable, indent=2)

    def generate_html(self) -> str:
        """Generate schema documentation in HTML format.

        Returns:
            HTML documentation string
        """
        schemas = self.extract_schemas()
        lines = []

        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append("<title>EE Gateway Schemas Documentation</title>")
        lines.append("<style>")
        lines.append("body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }")
        lines.append("h1 { color: #333; border-bottom: 2px solid #333; }")
        lines.append("h2 { color: #555; margin-top: 30px; }")
        lines.append("table { border-collapse: collapse; width: 100%; margin: 10px 0; }")
        lines.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        lines.append("th { background-color: #4CAF50; color: white; }")
        lines.append("tr:nth-child(even) { background-color: #f2f2f2; }")
        lines.append("pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }")
        lines.append(".badge { display: inline-block; padding: 3px 8px; font-size: 12px; border-radius: 3px; }")
        lines.append(".badge-yes { background-color: #4CAF50; color: white; }")
        lines.append(".badge-no { background-color: #f44336; color: white; }")
        lines.append("</style>")
        lines.append("</head>")
        lines.append("<body>")
        lines.append("<h1>EE Gateway Schemas Documentation</h1>")
        lines.append("<p>This document provides comprehensive documentation for all EE gateway schemas.</p>")
        lines.append("<hr>")

        for schema in schemas:
            lines.append(f"<h2>{schema.name} Schema</h2>")
            lines.append(f"<p><strong>Domain:</strong> {schema.domain}</p>")
            lines.append(f"<p><strong>Description:</strong> {schema.description}</p>")

            if schema.fields:
                lines.append("<p><strong>Fields:</strong></p>")
                lines.append("<table>")
                lines.append("<tr><th>Field</th><th>Type</th><th>Required</th><th>Description</th><th>Default</th><th>Constraints</th></tr>")

                for field in schema.fields:
                    required_class = "badge-yes" if field.required else "badge-no"
                    required_text = "Yes" if field.required else "No"
                    default_val = str(field.default) if field.default is not None else "-"
                    constraints_str = ", ".join(f"{k}={v}" for k, v in field.constraints.items()) if field.constraints else "-"

                    lines.append(f"<tr><td>{field.name}</td><td>{field.type}</td><td><span class='badge {required_class}'>{required_text}</span></td><td>{field.description}</td><td>{default_val}</td><td>{constraints_str}</td></tr>")

                lines.append("</table>")

            if schema.examples:
                lines.append("<p><strong>Examples:</strong></p>")

                for i, example in enumerate(schema.examples, 1):
                    lines.append(f"<p>Example {i}:</p>")
                    lines.append("<pre>")
                    lines.append(json.dumps(example, indent=2))
                    lines.append("</pre>")

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
    'SchemaField',
    'SchemaInfo',
    'SchemaDocGenerator',
]
