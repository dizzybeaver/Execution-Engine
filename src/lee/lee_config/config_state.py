"""config/config_state.py
Version: 2025-12-09_1
Purpose: Configuration state management
License: Apache 2.0
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ConfigurationVersion:
    """Track configuration version history."""

    version: str
    timestamp: float
    changes: dict[str, Any]


@dataclass
class ConfigurationState:
    """Track configuration state."""

    current_version: str = "1.0.0"
    active_preset: Optional[str] = None
    version_history: list[ConfigurationVersion] = field(default_factory=list)
    pending_changes: dict[str, Any] = field(default_factory=dict)
    last_reload_time: float = 0.0
    reload_count: int = 0
    validation_failures: int = 0


__all__ = [
    "ConfigurationState",
    "ConfigurationVersion",
]
