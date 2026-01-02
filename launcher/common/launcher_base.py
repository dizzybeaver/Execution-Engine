"""
EE Launcher Base Module

Provides common initialization and utilities for all EE launchers.
All launchers MUST use this base module to ensure:
1. Proper path setup (adds EE/src to sys.path for Lambda compatibility)
2. UG (Unified Gateway) initialization
3. Professional error handling
4. Consistent logging

This module uses ONLY UG for all operations - no code reimplementations.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional, Dict
import traceback


class LauncherError(Exception):
    """Base exception for launcher errors."""

    def __init__(self, message: str, exit_code: int = 1):
        self.message = message
        self.exit_code = exit_code
        super().__init__(self.message)


class LauncherBase:
    """
    Base class for all EE launchers.

    Provides:
    - Path setup (EE/src to sys.path)
    - UG initialization
    - Error handling
    - Logging utilities

    Usage:
        >>> launcher = LauncherBase(name="MyLauncher")
        >>> gateway = launcher.initialize()
        >>> result = launcher.execute("config.get", {"key": "test"})
        >>> launcher.shutdown()
    """

    def __init__(self, name: str):
        """
        Initialize launcher base.

        Args:
            name: Launcher name (for logging)
        """
        self.name = name
        self._gateway = None
        self._initialized = False

        # Setup paths immediately
        self._setup_paths()

    def _setup_paths(self) -> None:
        """
        Setup Python path for EE imports.

        Adds EE/src to sys.path for Lambda compatibility.
        Uses absolute paths from project root.
        """
        # Get project root (launcher/ is at D:/Code/Project/launcher/)
        launcher_dir = Path(__file__).parent
        project_root = launcher_dir.parent

        # Add EE/src to path
        ee_src = project_root / "EE" / "src"

        # Convert to absolute path and add to sys.path
        ee_src_abs = str(ee_src.resolve())

        # Add only if not already present
        if ee_src_abs not in sys.path:
            sys.path.insert(0, ee_src_abs)

    def initialize(self) -> Any:
        """
        Initialize the Unified Gateway (UG).

        Returns:
            Gateway instance (UnifiedRouter)

        Raises:
            LauncherError: If initialization fails
        """
        if self._initialized:
            return self._gateway

        try:
            # Import UG components
            from EE.src.gateway.gateway import get_unified_router

            # Initialize UG
            self._gateway = get_unified_router()
            self._initialized = True

            self.log_info(f"{self.name} - UG initialized successfully")
            return self._gateway

        except ImportError as e:
            raise LauncherError(
                f"Failed to import gateway modules: {e}",
                exit_code=2
            ) from e
        except Exception as e:
            raise LauncherError(
                f"Failed to initialize UG: {e}",
                exit_code=3
            ) from e

    def execute(self, route: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute gateway operation using UG.

        Args:
            route: Operation route (e.g., "config.get")
            payload: Operation parameters (default: {})

        Returns:
            Operation result

        Raises:
            LauncherError: If gateway not initialized or execution fails
        """
        if not self._initialized or self._gateway is None:
            raise LauncherError(
                "Gateway not initialized. Call initialize() first.",
                exit_code=4
            )

        if payload is None:
            payload = {}

        try:
            # Use UG for execution
            result = self._gateway.execute(route, payload)
            return result

        except Exception as e:
            raise LauncherError(
                f"Execution failed for route '{route}': {e}",
                exit_code=5
            ) from e

    def list_all_operations(self) -> Dict[str, Any]:
        """
        List all available operations using UG.

        Returns:
            Dictionary of all available operations

        Raises:
            LauncherError: If gateway not initialized
        """
        if not self._initialized or self._gateway is None:
            raise LauncherError(
                "Gateway not initialized. Call initialize() first.",
                exit_code=4
            )

        try:
            # Use UG to list operations
            return self._gateway.list_all_routes()

        except Exception as e:
            raise LauncherError(
                f"Failed to list operations: {e}",
                exit_code=6
            ) from e

    def get_gateway_stats(self) -> Dict[str, Any]:
        """
        Get gateway statistics using UG.

        Returns:
            Dictionary with gateway statistics

        Raises:
            LauncherError: If gateway not initialized
        """
        if not self._initialized or self._gateway is None:
            raise LauncherError(
                "Gateway not initialized. Call initialize() first.",
                exit_code=4
            )

        try:
            # Use UG to get stats
            return self._gateway.get_stats()

        except Exception as e:
            raise LauncherError(
                f"Failed to get stats: {e}",
                exit_code=7
            ) from e

    def shutdown(self) -> None:
        """
        Shutdown the launcher gracefully.
        """
        if self._initialized:
            self.log_info(f"{self.name} - Shutting down")
            self._gateway = None
            self._initialized = False

    # ========================================================================
    # Logging Utilities (using UG when available, fallback to print)
    # ========================================================================

    def log_info(self, message: str) -> None:
        """Log info message."""
        self._log(message, level="INFO")

    def log_warning(self, message: str) -> None:
        """Log warning message."""
        self._log(message, level="WARNING")

    def log_error(self, message: str) -> None:
        """Log error message."""
        self._log(message, level="ERROR")

    def log_debug(self, message: str) -> None:
        """Log debug message."""
        self._log(message, level="DEBUG")

    def _log(self, message: str, level: str = "INFO") -> None:
        """
        Internal logging method.

        Uses UG logging gateway if available, otherwise falls back to print.
        """
        if self._initialized and self._gateway is not None:
            try:
                # Try to use UG logging
                route = f"logging.log.{level.lower()}"
                self._gateway.execute(route, {"message": message})
                return
            except Exception:
                # Fall back to print if UG logging fails
                pass

        # Fallback to print
        print(f"[{level}] {message}")

    # ========================================================================
    # Error Handling Utilities
    # ========================================================================

    def handle_error(self, error: Exception) -> int:
        """
        Handle exception with proper logging and exit code.

        Args:
            error: Exception to handle

        Returns:
            Exit code
        """
        if isinstance(error, LauncherError):
            self.log_error(error.message)
            return error.exit_code
        else:
            self.log_error(f"Unexpected error in {self.name}: {error}")
            self.log_debug(traceback.format_exc())
            return 1


def create_launcher(name: str) -> LauncherBase:
    """
    Factory function to create a launcher instance.

    Args:
        name: Launcher name

    Returns:
        LauncherBase instance
    """
    return LauncherBase(name=name)


__all__ = [
    'LauncherBase',
    'LauncherError',
    'create_launcher',
]
