# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - Extract data models from state_subscriptions.py

"""models.py - State Subscription Data Models
Version: 2026-03-05_1
Purpose: Data structures for WebSocket state subscriptions

This module contains data classes for:
- StateSubscription: Represents a single state change subscription
- QueuedMessage: Represents a queued state change message

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
from dataclasses import dataclass, field
from typing import Any

from collections.abc import Callable

from lee.gateway.gateway_core import generate_correlation_id


@dataclass
class StateSubscription:
    """Represents a state change subscription."""

    entity_id: str
    callback: Callable[[str, dict[str, Any], dict[str, Any]], None]
    active: bool = True
    subscribe_time: float = field(default_factory=time.time)
    last_event_time: float = 0.0


@dataclass
class QueuedMessage:
    """Represents a queued state change message."""

    entity_id: str
    old_state: dict[str, Any]
    new_state: dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = field(default_factory=lambda: generate_correlation_id("ws_state"))


__all__ = [
    "QueuedMessage",
    "StateSubscription",
]
