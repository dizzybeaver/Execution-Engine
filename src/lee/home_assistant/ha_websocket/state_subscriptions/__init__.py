# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - Create __init__.py for state_subscriptions module

from typing import Optional
"""state_subscriptions - WebSocket State Subscription System

This package provides WebSocket-based state subscriptions for Home Assistant:
- Real-time state change detection
- Proactive ChangeReport generation
- Message queue buffering for disconnection resilience
- Correlation ID tracking for request tracing

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import threading

from lee.home_assistant.ha_websocket.state_subscriptions.models import QueuedMessage, StateSubscription
from lee.home_assistant.ha_websocket.state_subscriptions.subscription_manager import StateSubscriptionManager

# Singleton instance
_subscription_manager: Optional[StateSubscriptionManager] = None
_subscription_manager_lock = threading.Lock()


def get_subscription_manager(max_queue_size: int = 100) -> StateSubscriptionManager:
    """Get or create singleton subscription manager instance.

    Args:
        max_queue_size: Maximum queue size (only used on first call)

    Returns:
        StateSubscriptionManager singleton instance
    """
    global _subscription_manager

    if _subscription_manager is None:
        with _subscription_manager_lock:
            if _subscription_manager is None:
                _subscription_manager = StateSubscriptionManager(max_queue_size=max_queue_size)

    return _subscription_manager


__all__ = [
    "QueuedMessage",
    "StateSubscription",
    "StateSubscriptionManager",
    "get_subscription_manager",
]
