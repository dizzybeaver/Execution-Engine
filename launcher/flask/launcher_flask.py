#!/usr/bin/env python3
"""
EE Flask Server Launcher

Launches the EE Flask web server with SocketIO support.

The Flask server provides a modern web interface with real-time updates
via WebSocket for all EE gateway operations.

Usage:
    python launcher_flask.py [--port PORT] [--host HOST] [--debug]

Examples:
    python launcher_flask.py
    python launcher_flask.py --port 5000
    python launcher_flask.py --host 0.0.0.0 --port 5000 --debug
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path


def main() -> int:
    """
    Main entry point for Flask server launcher.

    Returns:
        Exit code (0 = success, non-zero = error)
    """
    # Add launcher to path
    launcher_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(launcher_dir))

    from launcher_common.launcher_base import LauncherBase, LauncherError

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='EE Flask Web Server Launcher'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    args = parser.parse_args()

    # Create launcher
    launcher = LauncherBase(name="Flask")

    try:
        # Initialize UG (for gateway access in Flask app)
        launcher.initialize()
        launcher.log_info("UG initialized for Flask server")

        # Import Flask server
        from EE.src.flask_server.run import main as flask_main

        # Prepare arguments for Flask server
        flask_args = [
            '--host', args.host,
            '--port', str(args.port),
        ]

        if args.debug:
            flask_args.append('--debug')

        launcher.log_info(f"Starting Flask server on http://{args.host}:{args.port}")

        # Start Flask server (this is blocking)
        sys.argv = ['flask_server'] + flask_args
        flask_main()

        # Cleanup (this runs after server shuts down)
        launcher.shutdown()
        return 0

    except SystemExit as e:
        # Flask server uses sys.exit, catch it
        launcher.shutdown()
        return e.code if e.code is not None else 0

    except LauncherError as e:
        return launcher.handle_error(e)
    except KeyboardInterrupt:
        launcher.log_info("\nFlask server interrupted by user")
        launcher.shutdown()
        return 130
    except Exception as e:
        launcher.log_error(f"Unexpected error: {e}")
        launcher.shutdown()
        return 1


if __name__ == "__main__":
    sys.exit(main())
