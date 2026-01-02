#!/usr/bin/env python3
"""
EE Dashboard Launcher

Launches the EE Dashboard server using UG (Unified Gateway).

The Dashboard provides a web-based UI and JSON API for interacting with
all EE gateway operations.

Usage:
    python launcher_dashboard.py [--port PORT] [--host HOST]

Examples:
    python launcher_dashboard.py
    python launcher_dashboard.py --port 8080
    python launcher_dashboard.py --host 0.0.0.0 --port 9090
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path


def main() -> int:
    """
    Main entry point for Dashboard launcher.

    Returns:
        Exit code (0 = success, non-zero = error)
    """
    # Add launcher to path
    launcher_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(launcher_dir))

    from launcher_common.launcher_base import LauncherBase, LauncherError

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='EE Dashboard Server Launcher'
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port to bind to (default: 8080)'
    )
    parser.add_argument(
        '--auto-port',
        action='store_true',
        help='Automatically find available port if default is in use'
    )
    args = parser.parse_args()

    # Create launcher
    launcher = LauncherBase(name="Dashboard")

    try:
        # Initialize UG
        gateway = launcher.initialize()

        # Get domain registry
        from EE.src.gateway.gateway import get_domain_registry
        registry = get_domain_registry()

        # Import dashboard server factory
        from EE.src.gateway.dashboard.dashboard_server_factory import (
            create_dashboard_server,
            create_dashboard_server_with_auto_port,
        )

        # Create dashboard server
        launcher.log_info(f"Creating Dashboard server on {args.host}:{args.port}")

        if args.auto_port:
            # Auto-find available port
            server = create_dashboard_server_with_auto_port(
                gateway_registry=registry,
                host=args.host,
                starting_port=args.port,
            )
        else:
            # Use specified port
            server = create_dashboard_server(
                gateway_registry=registry,
                host=args.host,
                port=args.port,
            )

        # Start server (blocking)
        launcher.log_info(f"Starting Dashboard server on http://{args.host}:{server.port}")
        server.serve_forever()

        # Cleanup (this runs after server shuts down)
        launcher.shutdown()
        return 0

    except LauncherError as e:
        return launcher.handle_error(e)
    except KeyboardInterrupt:
        launcher.log_info("\nDashboard server interrupted by user")
        launcher.shutdown()
        return 130
    except Exception as e:
        launcher.log_error(f"Unexpected error: {e}")
        launcher.shutdown()
        return 1


if __name__ == "__main__":
    sys.exit(main())
