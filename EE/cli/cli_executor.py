"""
CLI Executor - EE CLI Gateway Command Executor

This module handles execution of CLI commands and delegates to the
gateway router for actual operations.

Based on:
D:\\Code\\Project\\Gateway\\CLI\\cli_executor.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from EE.cli.cli_common import CLIGatewayError, CLIExecutionError, CLIValidationError
from EE.cli.cli_parser import CLIArgs


@dataclass
class CLIExecutor:
    """CLI command executor.

    This class executes CLI commands by delegating to the gateway router.
    Handles command parsing, validation, and error handling.

    Attributes:
        gateway: The EE gateway router instance

    Examples:
        >>> from gateway import get_unified_router
        >>> executor = CLIExecutor(gateway=get_unified_router())
        >>> result = executor.execute(CLIArgs(command="list-domains"))
        >>> print(result)
        ['config', 'security', 'logging', 'metrics', ...]
    """

    gateway: Any

    def execute(self, args: CLIArgs) -> Any:
        """Execute a CLI command.

        Args:
            args: Parsed CLI arguments

        Returns:
            Command execution result (varies by command)

        Raises:
            CLIValidationError: If command validation fails
            CLIExecutionError: If command execution fails
            CLIGatewayError: For other CLI-related errors

        Examples:
            >>> # List all domains
            >>> result = executor.execute(CLIArgs(command="list-domains"))
            >>> print(result)
            ['config', 'security', 'logging', 'metrics', 'debug', 'serialization']

            >>> # List all routes
            >>> result = executor.execute(CLIArgs(command="list-routes"))
            >>> print(result.keys())
            dict_keys(['config', 'security', 'logging', ...])

            >>> # Execute route
            >>> result = executor.execute(CLIArgs(
            ...     command="exec",
            ...     route="config.get",
            ...     payload='{"key": "database.host"}'
            ... ))
            >>> print(result)
            "localhost"

            >>> # Get statistics
            >>> result = executor.execute(CLIArgs(command="stats"))
            >>> print(result["total_routes"])
            50
        """
        try:
            if args.command == "list-all":
                return self._execute_list_all(args)

            if args.command == "list-domains":
                return self._execute_list_domains(args)

            if args.command == "list-routes":
                return self._execute_list_routes(args)

            if args.command == "exec":
                return self._execute_exec(args)

            if args.command == "stats":
                return self._execute_stats(args)

            raise CLIExecutionError(f"Unknown CLI command: {args.command}")

        except CLIGatewayError:
            # Re-raise CLI errors
            raise
        except Exception as e:
            # Wrap other exceptions
            raise CLIExecutionError(
                f"Command execution failed: {e}"
            ) from e

    def _execute_list_all(self, args: CLIArgs) -> dict:
        """Execute 'list-all' command.

        Lists all domains and their complete operation details.

        Args:
            args: CLI arguments

        Returns:
            Dictionary with all domain operations
        """
        return self.gateway.list_all()

    def _execute_list_domains(self, args: CLIArgs) -> list:
        """Execute 'list-domains' command.

        Lists all registered domain names.

        Args:
            args: CLI arguments

        Returns:
            List of domain names
        """
        registry = self.gateway.get_domain_registry()
        return registry.list_domains()

    def _execute_list_routes(self, args: CLIArgs) -> dict:
        """Execute 'list-routes' command.

        Lists all available routes, optionally filtered by domain.

        Args:
            args: CLI arguments (may contain domain filter)

        Returns:
            Dictionary of routes by domain
        """
        all_routes = self.gateway.list_all()

        # Filter by domain if specified
        if args.domain:
            if args.domain not in all_routes:
                raise CLIValidationError(f"Domain '{args.domain}' not found")
            return {args.domain: all_routes[args.domain]}

        return all_routes

    def _execute_exec(self, args: CLIArgs) -> Any:
        """Execute 'exec' command.

        Executes a specific gateway route with optional payload.

        Args:
            args: CLI arguments containing route and payload

        Returns:
            Route execution result

        Raises:
            CLIValidationError: If route is missing or payload is invalid JSON
        """
        if not args.route:
            raise CLIValidationError("Missing route for 'exec' command")

        # Parse payload
        payload = {}
        if args.payload:
            try:
                payload = json.loads(args.payload)
            except json.JSONDecodeError as e:
                raise CLIValidationError(f"Invalid JSON payload: {e}") from e

        # Execute route
        try:
            return self.gateway.execute(args.route, payload)
        except Exception as e:
            raise CLIExecutionError(
                f"Route execution failed for '{args.route}': {e}"
            ) from e

    def _execute_stats(self, args: CLIArgs) -> dict:
        """Execute 'stats' command.

        Gets gateway usage and performance statistics.

        Args:
            args: CLI arguments

        Returns:
            Dictionary with gateway statistics
        """
        return self.gateway.get_stats()


__all__ = [
    'CLIExecutor',
]
