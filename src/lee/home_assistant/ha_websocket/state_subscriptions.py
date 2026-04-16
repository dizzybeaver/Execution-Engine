# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - DEPRECATED: Module split into package

"""state_subscriptions.py - WebSocket State Subscription System

DEPRECATED (2026-04-06): This module has been split into a package for better maintainability.

New import location:
    from lee.home_assistant.ha_websocket.state_subscriptions import (
        StateSubscriptionManager,
        get_subscription_manager,
        QueuedMessage,
        StateSubscription,
    )

This file now imports from the new package structure for backward compatibility.

Package structure:
    state_subscriptions/
        __init__.py          - Main exports and singleton
        models.py            - Data classes (StateSubscription, QueuedMessage)
        subscription_manager.py - Main StateSubscriptionManager class
        persistence.py       - Queue persistence operations
        monitoring.py        - WebSocket monitoring and cleanup

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# Import everything from new package for backward compatibility
from lee.home_assistant.ha_websocket.state_subscriptions.models import (
    QueuedMessage,
    StateSubscription,
)
from lee.home_assistant.ha_websocket.state_subscriptions.subscription_manager import (
    StateSubscriptionManager,
)
from lee.home_assistant.ha_websocket.state_subscriptions import get_subscription_manager

__all__ = [
    "QueuedMessage",
    "StateSubscription",
    "StateSubscriptionManager",
    "get_subscription_manager",
]
