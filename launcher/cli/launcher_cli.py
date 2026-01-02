#!/usr/bin/env python3
"""
EE CLI Launcher

Launches the EE Command-Line Interface using UG (Unified Gateway).

This launcher provides a command-line interface for interacting with all EE
gateway operations. It uses the UG CLI gateway for all functionality.

Usage:
    python launcher_cli.py [args]

Examples:
    python launcher_cli.py list-domains
    python launcher_cli.py exec config.get --payload '{"key": "test"}'
    python launcher_cli.py --json exec security.encrypt --payload '{"data": "secret"}'
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    """
    Main entry point for CLI launcher.

    Returns:
        Exit code (0 = success, non-zero = error)
    """
    # Add launcher to path
    launcher_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(launcher_dir))

    from launcher_common.launcher_base import LauncherBase, LauncherError

    # Create launcher
    launcher = LauncherBase(name="CLI")

    try:
        # Initialize UG
        gateway = launcher.initialize()

        # Import CLI gateway
        from EE.src.gateway.cli.unified_cli import UnifiedGatewayCLI

        # Create CLI interface with UG
        cli = UnifiedGatewayCLI(gateway=gateway)

        # Run CLI with provided arguments
        exit_code = cli.run(sys.argv[1:])

        launcher.shutdown()
        return exit_code

    except LauncherError as e:
        return launcher.handle_error(e)
    except KeyboardInterrupt:
        launcher.log_info("\nCLI interrupted by user")
        launcher.shutdown()
        return 130
    except Exception as e:
        launcher.log_error(f"Unexpected error: {e}")
        launcher.shutdown()
        return 1


if __name__ == "__main__":
    sys.exit(main())
