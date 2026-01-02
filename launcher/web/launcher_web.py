#!/usr/bin/env python3
"""
EE Web Console Launcher

Launches the EE Web Console using UG (Unified Gateway).

The Web Console provides a browser-based interface for interacting with
all EE gateway operations.

Usage:
    python launcher_web.py [--port PORT] [--host HOST]

Examples:
    python launcher_web.py
    python launcher_web.py --port 9000
    python launcher_web.py --host 0.0.0.0 --port 9000
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path


def main() -> int:
    """
    Main entry point for Web Console launcher.

    Returns:
        Exit code (0 = success, non-zero = error)
    """
    # Add launcher to path
    launcher_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(launcher_dir))

    from launcher_common.launcher_base import LauncherBase, LauncherError

    # Parse arguments
    parser = argparse.ArgumentParser(
        description='EE Web Console Launcher'
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9000,
        help='Port to bind to (default: 9000)'
    )
    parser.add_argument(
        '--background',
        action='store_true',
        help='Run server in background (non-blocking)'
    )
    args = parser.parse_args()

    # Create launcher
    launcher = LauncherBase(name="WebConsole")

    try:
        # Initialize UG
        gateway = launcher.initialize()

        # Import web console factory
        from EE.src.gateway.web.web_console_factory import create_web_console

        # Create web console
        launcher.log_info(f"Creating Web Console on {args.host}:{args.port}")
        console = create_web_console(
            gateway=gateway,
            host=args.host,
            port=args.port,
        )

        # Start server
        launcher.log_info(f"Starting Web Console on http://{args.host}:{args.port}")

        if args.background:
            # Start in background (non-blocking)
            import threading
            server_thread = threading.Thread(
                target=console.serve_forever,
                daemon=True,
            )
            server_thread.start()
            launcher.log_info("Web Console running in background")
            launcher.log_info("Press Ctrl+C to stop")

            # Keep main thread alive
            try:
                server_thread.join()
            except KeyboardInterrupt:
                launcher.log_info("\nShutting down Web Console")
                console.shutdown()
        else:
            # Start in foreground (blocking)
            console.serve_forever()

        # Cleanup
        launcher.shutdown()
        return 0

    except LauncherError as e:
        return launcher.handle_error(e)
    except KeyboardInterrupt:
        launcher.log_info("\nWeb Console interrupted by user")
        launcher.shutdown()
        return 130
    except Exception as e:
        launcher.log_error(f"Unexpected error: {e}")
        launcher.shutdown()
        return 1


if __name__ == "__main__":
    sys.exit(main())
