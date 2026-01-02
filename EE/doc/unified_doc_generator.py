"""
Unified Documentation Generator - EE Doc Gateway

This module provides a unified documentation generator that combines all
documentation generators into a single interface. It orchestrates the
generation of commands, routes, services, and schemas documentation.

Based on:
D:\\Code\\Project\\Gateway\\Doc\\unified_doc_generator.py
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

from EE.doc.doc_command import CommandDocGenerator
from EE.doc.doc_route import RouteDocGenerator
from EE.doc.doc_service import ServiceDocGenerator
from EE.doc.doc_schema import SchemaDocGenerator


@dataclass
class DocGenerationConfig:
    """Configuration for documentation generation.

    Attributes:
        output_dir: Output directory for generated documentation
        formats: List of output formats (markdown, json, html)
        include_commands: Include command documentation
        include_routes: Include route documentation
        include_services: Include service documentation
        include_schemas: Include schema documentation
        merge_single_file: Merge all documentation into single file
    """

    output_dir: str = "./docs"
    formats: List[str] = None
    include_commands: bool = True
    include_routes: bool = True
    include_services: bool = True
    include_schemas: bool = True
    merge_single_file: bool = False

    def __post_init__(self):
        if self.formats is None:
            self.formats = ["markdown"]


class UnifiedDocGenerator:
    """Unified documentation generator for EE gateway.

    This generator orchestrates all documentation generators and provides
    a single interface for generating comprehensive documentation.

    Attributes:
        gateway_registry: EE domain registry instance
        config: Documentation generation configuration
        command_gen: Command documentation generator
        route_gen: Route documentation generator
        service_gen: Service documentation generator
        schema_gen: Schema documentation generator

    Examples:
        >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
        >>> registry = EEDomainRegistry.get_instance()
        >>> generator = UnifiedDocGenerator(registry)
        >>>
        >>> # Generate all documentation
        >>> generator.generate_all()
        >>>
        >>> # Generate specific documentation
        >>> generator.generate_commands()
        >>> generator.generate_routes()
    """

    def __init__(
        self,
        gateway_registry: Any,
        config: Optional[DocGenerationConfig] = None
    ):
        """Initialize unified documentation generator.

        Args:
            gateway_registry: EE domain registry instance
            config: Documentation generation configuration
        """
        self.registry = gateway_registry
        self.config = config or DocGenerationConfig()

        # Initialize individual generators
        self.command_gen = CommandDocGenerator(gateway_registry)
        self.route_gen = RouteDocGenerator(gateway_registry)
        self.service_gen = ServiceDocGenerator(gateway_registry)
        self.schema_gen = SchemaDocGenerator(gateway_registry)

    def generate_all(self) -> Dict[str, Any]:
        """Generate all documentation.

        Returns:
            Dictionary with generation results
        """
        results = {
            "success": True,
            "generated": [],
            "errors": []
        }

        try:
            if self.config.include_commands:
                cmd_result = self.generate_commands()
                results["generated"].append(cmd_result)

            if self.config.include_routes:
                route_result = self.generate_routes()
                results["generated"].append(route_result)

            if self.config.include_services:
                svc_result = self.generate_services()
                results["generated"].append(svc_result)

            if self.config.include_schemas:
                schema_result = self.generate_schemas()
                results["generated"].append(schema_result)

            if self.config.merge_single_file:
                merged_result = self.generate_merged()
                results["generated"].append(merged_result)

        except Exception as e:
            results["success"] = False
            results["errors"].append(str(e))

        return results

    def generate_commands(self) -> Dict[str, Any]:
        """Generate command documentation.

        Returns:
            Dictionary with generation results
        """
        results = {
            "type": "commands",
            "files": []
        }

        for fmt in self.config.formats:
            try:
                output_path = str(Path(self.config.output_dir) / f"commands.{fmt}")

                if fmt == "markdown":
                    content = self.command_gen.generate_markdown()
                    ext = ".md"
                elif fmt == "json":
                    content = self.command_gen.generate_json()
                    ext = ".json"
                elif fmt == "html":
                    content = self.command_gen.generate_html()
                    ext = ".html"
                else:
                    continue

                # Ensure output directory exists
                Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

                # Write documentation
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)

                results["files"].append(output_path)

            except Exception as e:
                results["error"] = str(e)

        return results

    def generate_routes(self) -> Dict[str, Any]:
        """Generate route documentation.

        Returns:
            Dictionary with generation results
        """
        results = {
            "type": "routes",
            "files": []
        }

        for fmt in self.config.formats:
            try:
                output_path = str(Path(self.config.output_dir) / f"routes.{fmt}")

                if fmt == "markdown":
                    content = self.route_gen.generate_markdown()
                    ext = ".md"
                elif fmt == "json":
                    content = self.route_gen.generate_json()
                    ext = ".json"
                elif fmt == "html":
                    content = self.route_gen.generate_html()
                    ext = ".html"
                else:
                    continue

                # Ensure output directory exists
                Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

                # Write documentation
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)

                results["files"].append(output_path)

            except Exception as e:
                results["error"] = str(e)

        return results

    def generate_services(self) -> Dict[str, Any]:
        """Generate service documentation.

        Returns:
            Dictionary with generation results
        """
        results = {
            "type": "services",
            "files": []
        }

        for fmt in self.config.formats:
            try:
                output_path = str(Path(self.config.output_dir) / f"services.{fmt}")

                if fmt == "markdown":
                    content = self.service_gen.generate_markdown()
                    ext = ".md"
                elif fmt == "json":
                    content = self.service_gen.generate_json()
                    ext = ".json"
                elif fmt == "html":
                    content = self.service_gen.generate_html()
                    ext = ".html"
                else:
                    continue

                # Ensure output directory exists
                Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

                # Write documentation
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)

                results["files"].append(output_path)

            except Exception as e:
                results["error"] = str(e)

        return results

    def generate_schemas(self) -> Dict[str, Any]:
        """Generate schema documentation.

        Returns:
            Dictionary with generation results
        """
        results = {
            "type": "schemas",
            "files": []
        }

        for fmt in self.config.formats:
            try:
                output_path = str(Path(self.config.output_dir) / f"schemas.{fmt}")

                if fmt == "markdown":
                    content = self.schema_gen.generate_markdown()
                    ext = ".md"
                elif fmt == "json":
                    content = self.schema_gen.generate_json()
                    ext = ".json"
                elif fmt == "html":
                    content = self.schema_gen.generate_html()
                    ext = ".html"
                else:
                    continue

                # Ensure output directory exists
                Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

                # Write documentation
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)

                results["files"].append(output_path)

            except Exception as e:
                results["error"] = str(e)

        return results

    def generate_merged(self) -> Dict[str, Any]:
        """Generate merged documentation in single file.

        Returns:
            Dictionary with generation results
        """
        results = {
            "type": "merged",
            "files": []
        }

        for fmt in self.config.formats:
            try:
                output_path = str(Path(self.config.output_dir) / f"gateway_docs.{fmt}")

                if fmt == "markdown":
                    content = self._generate_merged_markdown()
                elif fmt == "json":
                    content = self._generate_merged_json()
                elif fmt == "html":
                    content = self._generate_merged_html()
                else:
                    continue

                # Ensure output directory exists
                Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

                # Write documentation
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)

                results["files"].append(output_path)

            except Exception as e:
                results["error"] = str(e)

        return results

    def _generate_merged_markdown(self) -> str:
        """Generate merged markdown documentation.

        Returns:
            Merged markdown string
        """
        parts = []

        parts.append("# EE Gateway Documentation")
        parts.append("")
        parts.append("This document provides comprehensive documentation for the EE Gateway system.")
        parts.append("")
        parts.append("---")
        parts.append("")

        if self.config.include_commands:
            parts.append(self.command_gen.generate_markdown())

        if self.config.include_routes:
            parts.append(self.route_gen.generate_markdown())

        if self.config.include_services:
            parts.append(self.service_gen.generate_markdown())

        if self.config.include_schemas:
            parts.append(self.schema_gen.generate_markdown())

        return "\n".join(parts)

    def _generate_merged_json(self) -> str:
        """Generate merged JSON documentation.

        Returns:
            Merged JSON string
        """
        import json

        merged = {}

        if self.config.include_commands:
            merged["commands"] = json.loads(self.command_gen.generate_json())

        if self.config.include_routes:
            merged["routes"] = json.loads(self.route_gen.generate_json())

        if self.config.include_services:
            merged["services"] = json.loads(self.service_gen.generate_json())

        if self.config.include_schemas:
            merged["schemas"] = json.loads(self.schema_gen.generate_json())

        return json.dumps(merged, indent=2)

    def _generate_merged_html(self) -> str:
        """Generate merged HTML documentation.

        Returns:
            Merged HTML string
        """
        parts = []

        parts.append("<!DOCTYPE html>")
        parts.append("<html>")
        parts.append("<head>")
        parts.append("<title>EE Gateway Documentation</title>")
        parts.append("<style>")
        parts.append("body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }")
        parts.append("h1 { color: #333; border-bottom: 2px solid #333; }")
        parts.append("h2 { color: #555; margin-top: 30px; }")
        parts.append(".section { margin: 30px 0; }")
        parts.append("</style>")
        parts.append("</head>")
        parts.append("<body>")
        parts.append("<h1>EE Gateway Documentation</h1>")
        parts.append("<p>This document provides comprehensive documentation for the EE Gateway system.</p>")

        if self.config.include_commands:
            parts.append('<div class="section">')
            # Extract body content from HTML
            cmd_html = self.command_gen.generate_html()
            body_start = cmd_html.find("<body>") + 6
            body_end = cmd_html.find("</body>")
            parts.append(cmd_html[body_start:body_end])
            parts.append("</div>")

        if self.config.include_routes:
            parts.append('<div class="section">')
            route_html = self.route_gen.generate_html()
            body_start = route_html.find("<body>") + 6
            body_end = route_html.find("</body>")
            parts.append(route_html[body_start:body_end])
            parts.append("</div>")

        if self.config.include_services:
            parts.append('<div class="section">')
            svc_html = self.service_gen.generate_html()
            body_start = svc_html.find("<body>") + 6
            body_end = svc_html.find("</body>")
            parts.append(svc_html[body_start:body_end])
            parts.append("</div>")

        if self.config.include_schemas:
            parts.append('<div class="section">')
            schema_html = self.schema_gen.generate_html()
            body_start = schema_html.find("<body>") + 6
            body_end = schema_html.find("</body>")
            parts.append(schema_html[body_start:body_end])
            parts.append("</div>")

        parts.append("</body>")
        parts.append("</html>")

        return "\n".join(parts)


def create_doc_generator(
    gateway_registry: Any,
    output_dir: str = "./docs",
    formats: Optional[List[str]] = None,
    merge_single_file: bool = False
) -> UnifiedDocGenerator:
    """Create unified documentation generator with default configuration.

    Args:
        gateway_registry: EE domain registry instance
        output_dir: Output directory for documentation
        formats: List of output formats (default: ["markdown"])
        merge_single_file: Whether to merge all into single file

    Returns:
        Configured UnifiedDocGenerator instance

    Examples:
        >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
        >>> registry = EEDomainRegistry.get_instance()
        >>> generator = create_doc_generator(registry, output_dir="./docs")
        >>> generator.generate_all()
    """
    config = DocGenerationConfig(
        output_dir=output_dir,
        formats=formats,
        merge_single_file=merge_single_file
    )

    return UnifiedDocGenerator(gateway_registry, config)


__all__ = [
    'DocGenerationConfig',
    'UnifiedDocGenerator',
    'create_doc_generator',
]
