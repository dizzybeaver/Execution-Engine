"""
Doc Domain Gateway - EE Gateway System

This module provides the Doc Domain Gateway that integrates the documentation
interface with the EE gateway registry system. It exposes documentation operations
through the standard gateway domain interface.

Architecture:
    Gateway Registry -> Doc Domain Gateway -> Doc Generators -> Documentation

Routes:
    - doc.generate.commands: Generate command documentation
    - doc.generate.routes: Generate route documentation
    - doc.generate.services: Generate service documentation
    - doc.generate.schemas: Generate schema documentation
    - doc.generate.all: Generate all documentation
    - doc.list_all: List all doc operations
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

from EE.universal_gateway.domain_gateway import DomainGateway
from EE.doc.unified_doc_generator import (
    UnifiedDocGenerator,
    create_doc_generator,
    DocGenerationConfig
)
from EE.doc.doc_command import CommandDocGenerator
from EE.doc.doc_route import RouteDocGenerator
from EE.doc.doc_service import ServiceDocGenerator
from EE.doc.doc_schema import SchemaDocGenerator


# REMOVED: @dataclass(frozen=True) decorator - not compatible with EE 2.1

class DocGatewayDomain(DomainGateway):
    """Doc Domain Gateway for EE.

    This gateway provides programmatic access to documentation generation
    operations through the standard gateway interface. It allows other parts
    of the system to generate documentation programmatically.

    Routes:
        - doc.generate.commands: Generate command documentation
        - doc.generate.routes: Generate route documentation
        - doc.generate.services: Generate service documentation
        - doc.generate.schemas: Generate schema documentation
        - doc.generate.all: Generate all documentation
        - doc.generate.merged: Generate merged documentation
        - doc.list_all: List all documentation operations

    Examples:
        >>> from EE.universal_gateway.domain_gateway import EEDomainRegistry
        >>> registry = EEDomainRegistry.get_instance()
        >>> doc_gateway = registry.get("doc")
        >>>
        >>> # Generate all documentation
        >>> result = doc_gateway.execute("doc.generate.all", {
        ...     "output_dir": "./docs",
        ...     "formats": ["markdown", "html"]
        ... })
        >>> print(result["success"])
        True
        >>>
        >>> # Generate specific documentation
        >>> result = doc_gateway.execute("doc.generate.commands", {
        ...     "output_dir": "./docs",
        ...     "format": "markdown"
        ... })
    """

    # EE 2.1 UPGRADE: Removed legacy 'registry' optional attribute (anti-pattern)
    # MODIFIED: EE 2.1 uniform constructor signature
    def __init__(
        self,
        domain_name: str,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable,
    ):
        """Initialize Doc Gateway Domain with EE 2.1 dependencies.

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

    def execute(self, route: str, payload: dict) -> Any:
        """Execute doc gateway operation.

        Args:
            route: Operation route
            payload: Operation parameters

        Returns:
            Operation result

        Raises:
            GatewayError: If route is unknown or execution fails
        """
        try:
            if route == "doc.generate.commands":
                return self._generate_commands(payload)
            elif route == "doc.generate.routes":
                return self._generate_routes(payload)
            elif route == "doc.generate.services":
                return self._generate_services(payload)
            elif route == "doc.generate.schemas":
                return self._generate_schemas(payload)
            elif route == "doc.generate.all":
                return self._generate_all(payload)
            elif route == "doc.generate.merged":
                return self._generate_merged(payload)
            elif route == "doc.list_all":
                return self.list_all()
            else:
                raise GatewayError(f"Unknown doc route: {route}")

        except GatewayError:
            raise
        except Exception as e:
            raise GatewayError(f"Doc gateway error: {e}") from e

    def _get_generator(self, payload: dict) -> UnifiedDocGenerator:
        """Get documentation generator from payload.

        Args:
            payload: Must contain output configuration

        Returns:
            UnifiedDocGenerator instance
        """
        output_dir = payload.get("output_dir", "./docs")
        formats = payload.get("formats", ["markdown"])
        merge_single_file = payload.get("merge_single_file", False)

        return create_doc_generator(
            gateway_registry=self.registry,
            output_dir=output_dir,
            formats=formats,
            merge_single_file=merge_single_file
        )

    def _generate_commands(self, payload: dict) -> Dict[str, Any]:
        """Generate command documentation.

        Args:
            payload: Must contain output_dir and optional format

        Returns:
            Dictionary with generation result
        """
        if self.registry is None:
            return {
                "success": False,
                "error": "Registry not initialized"
            }

        try:
            generator = self._get_generator(payload)
            result = generator.generate_commands()

            return {
                "success": True,
                "type": "commands",
                "files": result.get("files", []),
                "error": result.get("error")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_routes(self, payload: dict) -> Dict[str, Any]:
        """Generate route documentation.

        Args:
            payload: Must contain output_dir and optional format

        Returns:
            Dictionary with generation result
        """
        if self.registry is None:
            return {
                "success": False,
                "error": "Registry not initialized"
            }

        try:
            generator = self._get_generator(payload)
            result = generator.generate_routes()

            return {
                "success": True,
                "type": "routes",
                "files": result.get("files", []),
                "error": result.get("error")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_services(self, payload: dict) -> Dict[str, Any]:
        """Generate service documentation.

        Args:
            payload: Must contain output_dir and optional format

        Returns:
            Dictionary with generation result
        """
        if self.registry is None:
            return {
                "success": False,
                "error": "Registry not initialized"
            }

        try:
            generator = self._get_generator(payload)
            result = generator.generate_services()

            return {
                "success": True,
                "type": "services",
                "files": result.get("files", []),
                "error": result.get("error")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_schemas(self, payload: dict) -> Dict[str, Any]:
        """Generate schema documentation.

        Args:
            payload: Must contain output_dir and optional format

        Returns:
            Dictionary with generation result
        """
        if self.registry is None:
            return {
                "success": False,
                "error": "Registry not initialized"
            }

        try:
            generator = self._get_generator(payload)
            result = generator.generate_schemas()

            return {
                "success": True,
                "type": "schemas",
                "files": result.get("files", []),
                "error": result.get("error")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_all(self, payload: dict) -> Dict[str, Any]:
        """Generate all documentation.

        Args:
            payload: Must contain output_dir and optional formats

        Returns:
            Dictionary with generation result
        """
        if self.registry is None:
            return {
                "success": False,
                "error": "Registry not initialized"
            }

        try:
            generator = self._get_generator(payload)
            result = generator.generate_all()

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_merged(self, payload: dict) -> Dict[str, Any]:
        """Generate merged documentation in single file.

        Args:
            payload: Must contain output_dir and optional format

        Returns:
            Dictionary with generation result
        """
        if self.registry is None:
            return {
                "success": False,
                "error": "Registry not initialized"
            }

        try:
            generator = self._get_generator(payload)
            result = generator.generate_merged()

            return {
                "success": True,
                "type": "merged",
                "files": result.get("files", []),
                "error": result.get("error")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_all(self) -> Dict[str, Any]:
        """List all doc gateway operations.

        Returns:
            Dictionary with operation metadata
        """
        return {
            "domain": "doc",
            "description": "Documentation gateway for EE - Generate comprehensive documentation",
            "operations": [
                {
                    "route": "doc.generate.commands",
                    "description": "Generate command documentation",
                    "params": {
                        "output_dir": "str - Output directory (default: ./docs)",
                        "format": "str - Output format: markdown, json, html (default: markdown)",
                    },
                    "returns": "dict with success, files, error"
                },
                {
                    "route": "doc.generate.routes",
                    "description": "Generate route documentation",
                    "params": {
                        "output_dir": "str - Output directory (default: ./docs)",
                        "format": "str - Output format: markdown, json, html (default: markdown)",
                    },
                    "returns": "dict with success, files, error"
                },
                {
                    "route": "doc.generate.services",
                    "description": "Generate service documentation",
                    "params": {
                        "output_dir": "str - Output directory (default: ./docs)",
                        "format": "str - Output format: markdown, json, html (default: markdown)",
                    },
                    "returns": "dict with success, files, error"
                },
                {
                    "route": "doc.generate.schemas",
                    "description": "Generate schema documentation",
                    "params": {
                        "output_dir": "str - Output directory (default: ./docs)",
                        "format": "str - Output format: markdown, json, html (default: markdown)",
                    },
                    "returns": "dict with success, files, error"
                },
                {
                    "route": "doc.generate.all",
                    "description": "Generate all documentation (commands, routes, services, schemas)",
                    "params": {
                        "output_dir": "str - Output directory (default: ./docs)",
                        "formats": "list[str] - Output formats (default: [markdown])",
                    },
                    "returns": "dict with success, generated list, errors"
                },
                {
                    "route": "doc.generate.merged",
                    "description": "Generate merged documentation in single file",
                    "params": {
                        "output_dir": "str - Output directory (default: ./docs)",
                        "format": "str - Output format: markdown, json, html (default: markdown)",
                    },
                    "returns": "dict with success, files, error"
                },
            ]
        }


__all__ = [
    'DocGatewayDomain',
]
