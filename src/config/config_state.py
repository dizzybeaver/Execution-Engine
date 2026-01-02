"""
config/config_state.py
Version: 2025-12-09_1
Purpose: Configuration state management
License: Apache 2.0
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class ConfigurationVersion:
    """Track configuration version history."""
    version: str
    timestamp: float
    changes: Dict[str, Any]


@dataclass
class ConfigurationState:
    """Track configuration state."""
    current_version: str = "1.0.0"
    active_preset: Optional[str] = None
    version_history: List[ConfigurationVersion] = field(default_factory=list)
    pending_changes: Dict[str, Any] = field(default_factory=dict)
    last_reload_time: float = 0.0
    reload_count: int = 0
    validation_failures: int = 0


__all__ = [
    'ConfigurationVersion',
    'ConfigurationState'
]
