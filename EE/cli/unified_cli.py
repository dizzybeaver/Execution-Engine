"""
Unified CLI - EE CLI Gateway Main Interface

This module provides the main CLI interface for the EE universal gateway.
Integrates parser, executor, and output renderer into a unified CLI.

Based on:
D:\\Code\\Project\\Gateway\\CLI\\unified_cli.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Optional

from EE.cli.cli_parser import parse_cli_args
from EE.cli.cli_output import CLIOutputRenderer
from EE.cli.cli_executor import CLIExecutor
from EE.cli.cli_common import CLIGatewayError


@dataclass
class UnifiedGatewayCLI:
    """Unified Gateway CLI interface.

    This class provides a complete CLI interface for the EE gateway system.
    It integrates argument parsing, command execution, and output rendering
    into a simple, easy-to-use interface.

    Attributes:
        gateway: The EE gateway router instance

    Examples:
        >>> from gateway import get_unified_router
        >>> cli = UnifiedGatewayCLI(gateway=get_unified_router())
        >>>
        >>> # Run CLI commands
        >>> exit_code = cli.run(["list-domains"])
        >>> print(exit_code)
        0
        >>>
        >>> exit_code = cli.run(["exec", "config.get", "--payload", '{"key": "test"}'])
        >>> print(exit_code)
        0
    """

    gateway: Any

    def run(self, argv: list[str]) -> int:
        """Run CLI command with given arguments.

        This is the main entry point for CLI execution. It parses arguments,
        executes the command, and renders output. Returns 0 on success,
        1 on error.

        Args:
            argv: Command-line arguments (typically sys.argv[1:])

        Returns:
            Exit code (0 = success, 1 = error)

        Examples:
            >>> cli = UnifiedGatewayCLI(gateway=get_unified_router())
            >>>
            >>> # List all domains
            >>> exit_code = cli.run(["list-domains"])
            >>> # Output:
            >>> # config
            >>> # security
            >>> # logging
            >>> # metrics
            >>>
            >>> # Execute route
            >>> exit_code = cli.run([
            ...     "exec", "config.get",
            ...     "--payload", '{"key": "database.host"}'
            ... ])
            >>> # Output:
            >>> # value: localhost
            >>>
            >>> # JSON output
            >>> exit_code = cli.run(["--json", "list-domains"])
            >>> # Output:
            >>> # {
            >>> #   "domains": ["config", "security", "logging", ...]
            >>> # }
        """
        try:
            # Parse arguments
            args = parse_cli_args(argv)

            # Create output renderer
            renderer = CLIOutputRenderer(json_output=args.json_output)

            # Create executor
            executor = CLIExecutor(gateway=self.gateway)

            # Execute command
            result = executor.execute(args)

            # Render and print result
            output = renderer.render(result)
            print(output)

            return 0

        except CLIGatewayError as e:
            # Handle expected CLI errors
            renderer = CLIOutputRenderer(json_output=False)
            print(renderer.render_error(e))
            return 1

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\nInterrupted by user")
            return 130  # Standard exit code for SIGINT

        except Exception as e:
            # Handle unexpected errors
            renderer = CLIOutputRenderer(json_output=False)
            print(renderer.render_error(e))
            return 1


def create_cli_gateway(gateway: Optional[Any] = None) -> UnifiedGatewayCLI:
    """Create a CLI gateway instance.

    Factory function to create a UnifiedGatewayCLI instance.
    If no gateway is provided, it will import the default EE gateway.

    Args:
        gateway: Optional gateway router instance (defaults to EE gateway)

    Returns:
        Configured UnifiedGatewayCLI instance

    Examples:
        >>> # Use default EE gateway
        >>> cli = create_cli_gateway()
        >>> cli.run(["list-domains"])
        0
        >>>
        >>> # Use custom gateway
        >>> from gateway import get_unified_router
        >>> custom_gateway = get_unified_router()
        >>> cli = create_cli_gateway(gateway=custom_gateway)
        >>> cli.run(["stats"])
        0
    """
    if gateway is None:
        # Import default EE gateway
        try:
            from EE.src.gateway.gateway import get_unified_router
            gateway = get_unified_router()
        except ImportError as e:
            raise ImportError(
                f"Cannot import default EE gateway: {e}. "
                "Please provide a gateway instance or ensure gateway module is available."
            ) from e

    return UnifiedGatewayCLI(gateway=gateway)


def main() -> int:
    """Main entry point for CLI execution.

    This function is intended to be used as the entry point for
    standalone CLI scripts or console scripts.

    Returns:
        Exit code (0 = success, non-zero = error)

    Examples:
        >>> # In your script's __main__ block
        >>> if __name__ == "__main__":
        >>>     sys.exit(main())
        >>>
        >>> # Or as a console script entry point
        >>> # In setup.py or pyproject.toml:
        >>> # [project.scripts]
        >>> # ee-gateway = "gateway.cli.unified_cli:main"
    """
    cli = create_cli_gateway()
    return cli.run(sys.argv[1:])


__all__ = [
    'UnifiedGatewayCLI',
    'create_cli_gateway',
    'main',
]
