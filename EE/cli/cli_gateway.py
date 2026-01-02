"""
CLI Domain Gateway - EE Gateway System

This module provides the CLI Domain Gateway that integrates the CLI interface
with the EE gateway registry system. It exposes CLI operations through the
standard gateway domain interface.

Architecture:
    Gateway Registry -> CLI Domain Gateway -> CLI Executor -> Operations

Routes:
    - cli.run: Run CLI command programmatically
    - cli.list_commands: List all available CLI commands
    - cli.parse_args: Parse CLI arguments without executing
    - cli.list_all: List all CLI operations
"""

from __future__ import annotations

from typing import Any, Dict, Callable
from dataclasses import dataclass

from EE.universal_gateway.domain_gateway import DomainGateway
from EE.cli.cli_parser import parse_cli_args, create_cli_parser
from EE.cli.cli_executor import CLIExecutor
from EE.cli.unified_cli import UnifiedGatewayCLI


# REMOVED: Local GatewayError - now imported from DomainGateway
# REMOVED: @dataclass(frozen=True) decorator - not compatible with EE 2.1

class CLIGatewayDomain(DomainGateway):
    """CLI Domain Gateway for EE.

    This gateway provides programmatic access to CLI operations through
    the standard gateway interface. It allows other parts of the system
    to execute CLI commands without spawning a subprocess.

    Routes:
        - cli.run: Run a CLI command programmatically
        - cli.list_commands: List all available CLI commands
        - cli.parse_args: Parse CLI arguments without executing
        - cli.list_all: List all CLI operations

    Examples:
        >>> from EE.src.gateway.gateway import get_unified_router
        >>> router = get_unified_router()
        >>>
        >>> # Run CLI command programmatically
        >>> result = router.execute("cli.run", {
        ...     "args": ["list-domains"]
        ... })
        >>> print(result["exit_code"])
        0
        >>>
        >>> # List available commands
        >>> commands = router.execute("cli.list_commands", {})
        >>> print(commands)
        ['list-all', 'list-domains', 'list-routes', 'exec', 'stats']
    """

    # EE 2.1 UPGRADE: Removed legacy 'gateway' optional attribute (anti-pattern)
    # MODIFIED: EE 2.1 uniform constructor signature
    def __init__(
        self,
        domain_name: str,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable,
    ):
        """Initialize CLI Gateway Domain with EE 2.1 dependencies.

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

    # MODIFIED: Use GatewayError from DomainGateway base class
    def execute(self, route: str, payload: dict) -> Any:
        """Execute CLI gateway operation.

        Args:
            route: Operation route
            payload: Operation parameters

        Returns:
            Operation result

        Raises:
            GatewayError: If route is unknown or execution fails
        """
        try:
            if route == "cli.run":
                return self._run_command(payload)
            elif route == "cli.list_commands":
                return self._list_commands(payload)
            elif route == "cli.parse_args":
                return self._parse_args(payload)
            elif route == "cli.list_all":
                return self.list_all()
            else:
                raise GatewayError(f"Unknown CLI route: {route}")

        except GatewayError:
            raise
        except Exception as e:
            raise GatewayError(f"CLI gateway error: {e}") from e

    def _run_command(self, payload: dict) -> Dict[str, Any]:
        """Run a CLI command programmatically.

        Args:
            payload: Must contain 'args' key with list of arguments

        Returns:
            Dictionary with:
                - exit_code: Process exit code (0 = success)
                - output: Command output (if captured)
                - error: Error message (if failed)
        """
        if self.gateway is None:
            return {
                "exit_code": 1,
                "error": "CLI gateway not initialized"
            }

        args = payload.get("args", [])
        if not isinstance(args, list):
            return {
                "exit_code": 1,
                "error": f"Invalid args type: {type(args).__name__}, expected list"
            }

        try:
            # Create CLI instance
            cli = UnifiedGatewayCLI(gateway=self.gateway)

            # Capture output by redirecting stdout
            import io
            from contextlib import redirect_stdout

            output_buffer = io.StringIO()

            with redirect_stdout(output_buffer):
                exit_code = cli.run(args)

            output = output_buffer.getvalue()

            return {
                "exit_code": exit_code,
                "output": output,
            }

        except Exception as e:
            return {
                "exit_code": 1,
                "error": str(e)
            }

    def _list_commands(self, payload: dict) -> Dict[str, Any]:
        """List all available CLI commands.

        Returns:
            Dictionary with command information
        """
        # Use hardcoded command list (most reliable)
        commands = {
            "list-all": {
                "help": "List all domains and their operations",
                "description": "List all domains and their operations"
            },
            "list-domains": {
                "help": "List all registered domains",
                "description": "List all registered domains"
            },
            "list-routes": {
                "help": "List all available routes",
                "description": "List all available routes"
            },
            "exec": {
                "help": "Execute a gateway route",
                "description": "Execute a gateway route"
            },
            "stats": {
                "help": "Get gateway statistics",
                "description": "Get gateway statistics"
            },
        }

        return {
            "commands": commands,
            "total": len(commands),
        }

    def _parse_args(self, payload: dict) -> Dict[str, Any]:
        """Parse CLI arguments without executing.

        Args:
            payload: Must contain 'args' key with list of arguments

        Returns:
            Dictionary with parsed arguments
        """
        args = payload.get("args", [])

        try:
            parsed = parse_cli_args(args)

            return {
                "command": parsed.command,
                "route": parsed.route,
                "payload": parsed.payload,
                "json_output": parsed.json_output,
                "domain": parsed.domain,
            }

        except Exception as e:
            return {
                "error": f"Failed to parse arguments: {e}"
            }

    def list_all(self) -> Dict[str, Any]:
        """List all CLI gateway operations.

        Returns:
            Dictionary with operation metadata
        """
        return {
            "domain": "cli",
            "description": "Command-line interface gateway for EE",
            "operations": [
                {
                    "route": "cli.run",
                    "description": "Run CLI command programmatically",
                    "params": {
                        "args": "list[str] - Command-line arguments",
                    },
                    "returns": "dict with exit_code, output, error"
                },
                {
                    "route": "cli.list_commands",
                    "description": "List all available CLI commands",
                    "params": {},
                    "returns": "dict with command information"
                },
                {
                    "route": "cli.parse_args",
                    "description": "Parse CLI arguments without executing",
                    "params": {
                        "args": "list[str] - Command-line arguments",
                    },
                    "returns": "dict with parsed arguments"
                },
            ]
        }


__all__ = [
    'CLIGatewayDomain',
]
