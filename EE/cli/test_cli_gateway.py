#!/usr/bin/env python3
"""
CLI Gateway Test Script - Demonstrates EE CLI Gateway functionality

This script demonstrates the complete CLI gateway implementation including:
1. Standalone CLI usage
2. Programmatic CLI usage
3. CLI domain gateway integration
4. JSON and text output formats

Usage:
    python test_cli_gateway.py
"""

import sys
import os

# Add EE src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from EE.cli import (
    create_cli_gateway,
    CLIGatewayDomain,
    CLIOutputRenderer,
)
from EE.src.gateway.gateway import execute, list_all


def test_standalone_cli():
    """Test standalone CLI usage."""
    print("=" * 70)
    print("TEST 1: Standalone CLI Usage")
    print("=" * 70)

    # Create CLI instance
    cli = create_cli_gateway()

    # Test list-domains command
    print("\n[Command] ee-gateway list-domains")
    exit_code = cli.run(["list-domains"])
    print(f"\n[Exit Code] {exit_code}\n")

    # Test list-routes command
    print("\n[Command] ee-gateway list-routes")
    exit_code = cli.run(["list-routes"])
    print(f"\n[Exit Code] {exit_code}\n")

    # Test with JSON output
    print("\n[Command] ee-gateway --json list-domains")
    exit_code = cli.run(["--json", "list-domains"])
    print(f"\n[Exit Code] {exit_code}\n")


def test_programmatic_cli():
    """Test programmatic CLI usage."""
    print("=" * 70)
    print("TEST 2: Programmatic CLI Usage")
    print("=" * 70)

    from EE.cli import CLIExecutor, CLIArgs, parse_cli_args

    # Get gateway
    from EE.src.gateway.gateway import get_unified_router
    gateway = get_unified_router()

    # Create executor
    executor = CLIExecutor(gateway=gateway)

    # Execute commands programmatically
    print("\n[Programmatic] List domains:")
    args = CLIArgs(command="list-domains")
    result = executor.execute(args)
    print(f"Domains: {result}\n")

    print("\n[Programmatic] List all operations:")
    args = CLIArgs(command="list-all")
    result = executor.execute(args)
    print(f"Total domains: {len(result)}\n")


def test_cli_domain_gateway():
    """Test CLI domain gateway integration."""
    print("=" * 70)
    print("TEST 3: CLI Domain Gateway Integration")
    print("=" * 70)

    # List CLI operations through gateway
    print("\n[Gateway Route] cli.list_all:")
    result = execute("cli.list_all", {})
    print(f"Domain: {result['domain']}")
    print(f"Total Operations: {len(result['operations'])}\n")

    # List available CLI commands
    print("\n[Gateway Route] cli.list_commands:")
    result = execute("cli.list_commands", {})
    print(f"Available Commands: {list(result['commands'].keys())}\n")

    # Parse CLI arguments through gateway
    print("\n[Gateway Route] cli.parse_args:")
    result = execute("cli.parse_args", {
        "args": ["list-domains"]
    })
    print(f"Parsed Command: {result['command']}\n")


def test_output_rendering():
    """Test output rendering capabilities."""
    print("=" * 70)
    print("TEST 4: Output Rendering")
    print("=" * 70)

    from EE.cli import CLIOutputRenderer

    # Test text renderer
    print("\n[Text Output]")
    renderer = CLIOutputRenderer(json_output=False)
    result = {
        "domains": ["config", "security", "logging", "metrics", "cli"],
        "status": "active",
        "total": 5
    }
    print(renderer.render(result))

    # Test JSON renderer
    print("\n[JSON Output]")
    renderer = CLIOutputRenderer(json_output=True)
    print(renderer.render(result))

    # Test error rendering
    print("\n[Error Output]")
    renderer = CLIOutputRenderer(json_output=False)
    try:
        raise ValueError("Test error message")
    except ValueError as e:
        print(renderer.render_error(e))


def test_cli_execution():
    """Test CLI command execution through gateway."""
    print("=" * 70)
    print("TEST 5: CLI Command Execution Through Gateway")
    print("=" * 70)

    # Run CLI command programmatically
    print("\n[Gateway Route] cli.run:")
    result = execute("cli.run", {
        "args": ["list-domains"]
    })
    print(f"Exit Code: {result['exit_code']}")
    print(f"Output:\n{result['output']}")


def main():
    """Run all tests."""
    print("\n")
    print("*" * 70)
    print("EE CLI Gateway - Complete Test Suite")
    print("*" * 70)

    try:
        # Test 1: Standalone CLI
        test_standalone_cli()

        # Test 2: Programmatic CLI
        test_programmatic_cli()

        # Test 3: CLI Domain Gateway
        test_cli_domain_gateway()

        # Test 4: Output Rendering
        test_output_rendering()

        # Test 5: CLI Execution Through Gateway
        test_cli_execution()

        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 70)

        return 0

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
