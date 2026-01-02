"""
EE Launcher Common Module

Provides common initialization and utilities for all EE launchers.
"""

from .launcher_base import (
    LauncherBase,
    LauncherError,
    create_launcher,
)

__all__ = [
    'LauncherBase',
    'LauncherError',
    'create_launcher',
]
