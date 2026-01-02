"""
CLI Parser - EE CLI Gateway Argument Parser

This module provides command-line argument parsing for the EE CLI gateway.
Supports multiple commands including listing domains, routes, and executing
gateway operations.

Based on:
D:\\Code\\Project\\Gateway\\CLI\\cli_parser.py
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Optional


@dataclass
class CLIArgs:
    """Parsed CLI arguments.

    Attributes:
        command: The command to execute (e.g., "list-all", "exec")
        route: The gateway route (for "exec" command)
        payload: JSON payload string (for "exec" command)
        json_output: Whether to format output as JSON
        domain: Optional domain filter (for list operations)

    Examples:
        >>> args = CLIArgs(
        ...     command="exec",
        ...     route="config.get",
        ...     payload='{"key": "database.host"}',
        ...     json_output=False,
        ...     domain=None
        ... )
    """

    command: str
    route: Optional[str] = None
    payload: Optional[str] = None
    json_output: bool = False
    domain: Optional[str] = None


def create_cli_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser.

    Returns:
        Configured ArgumentParser instance

    The parser supports the following commands:
        - list-all: List all domains and their operations
        - list-domains: List all registered domains
        - list-routes: List all available routes
        - exec: Execute a gateway route
        - stats: Get gateway statistics

    Examples:
        >>> parser = create_cli_parser()
        >>> args = parser.parse_args(["list-domains"])
        >>> args.command
        'list-domains'

        >>> args = parser.parse_args(["exec", "config.get", "--payload", '{"key": "test"}'])
        >>> args.command, args.route, args.payload
        ('exec', 'config.get', '{"key": "test"}')
    """
    parser = argparse.ArgumentParser(
        prog="ee-gateway",
        description="EE Universal Gateway CLI - Command-line interface for EE gateway system",
        epilog="""
Examples:
  # List all domains
  ee-gateway list-domains

  # List all routes
  ee-gateway list-routes

  # Execute a route
  ee-gateway exec config.get --payload '{"key": "database.host"}'

  # Execute with JSON output
  ee-gateway --json exec security.auth.authenticate --payload '{"user": "admin"}'

  # Get gateway statistics
  ee-gateway stats

  # List routes for specific domain
  ee-gateway list-routes --domain config
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Global arguments
    parser.add_argument(
        "--json",
        action="store_true",
        help="Format output as JSON"
    )

    # Create subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        title="Available Commands",
        description="Subcommands for interacting with the gateway",
        required=True,
        metavar="<command>"
    )

    # list-all command
    list_all_parser = subparsers.add_parser(
        "list-all",
        help="List all domains, routes, and operations",
        description="List all registered domains with their complete operation details"
    )

    # list-domains command
    list_domains_parser = subparsers.add_parser(
        "list-domains",
        help="List all registered domains",
        description="List all registered domain names in the gateway system"
    )

    # list-routes command
    list_routes_parser = subparsers.add_parser(
        "list-routes",
        help="List all available routes",
        description="List all available routes across all domains"
    )
    list_routes_parser.add_argument(
        "--domain",
        help="Filter routes by domain (e.g., config, security)",
        default=None,
        metavar="<domain>"
    )

    # exec command
    exec_parser = subparsers.add_parser(
        "exec",
        help="Execute a gateway route",
        description="Execute a specific gateway route with optional payload"
    )
    exec_parser.add_argument(
        "route",
        help="Gateway route in format 'domain.operation' (e.g., config.get, security.auth.authenticate)",
        metavar="<route>"
    )
    exec_parser.add_argument(
        "--payload",
        help="JSON payload string with route parameters",
        default=None,
        metavar="<json>"
    )

    # stats command
    stats_parser = subparsers.add_parser(
        "stats",
        help="Get gateway statistics",
        description="Display gateway usage and performance statistics"
    )

    return parser


def parse_cli_args(argv: list[str]) -> CLIArgs:
    """Parse CLI arguments from command line.

    Args:
        argv: List of command-line arguments (typically sys.argv[1:])

    Returns:
        Parsed arguments as CLIArgs dataclass

    Raises:
        SystemExit: If arguments are invalid (handled by argparse)

    Examples:
        >>> args = parse_cli_args(["list-domains"])
        >>> args.command
        'list-domains'

        >>> args = parse_cli_args(["exec", "config.get", "--payload", '{"key": "test"}'])
        >>> args.route, args.payload
        ('config.get', '{"key": "test"}')

        >>> args = parse_cli_args(["--json", "exec", "security.encrypt"])
        >>> args.json_output
        True
    """
    parser = create_cli_parser()
    args = parser.parse_args(argv)

    return CLIArgs(
        command=args.command,
        route=getattr(args, "route", None),
        payload=getattr(args, "payload", None),
        json_output=args.json,
        domain=getattr(args, "domain", None),
    )


__all__ = [
    'CLIArgs',
    'create_cli_parser',
    'parse_cli_args',
]
