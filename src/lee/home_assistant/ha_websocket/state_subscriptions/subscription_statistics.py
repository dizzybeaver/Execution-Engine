# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Extract statistics and diagnostics

"""subscription_statistics.py - Subscription Statistics and Diagnostics
Version: 2026-04-11
Purpose: Provide subscription manager statistics and diagnostics

This module handles:
- Subscription statistics collection
- Diagnostic information gathering
- Performance metrics calculation

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
from typing import Any


class SubscriptionStatistics:
    """Provides statistics and diagnostics for subscription manager.

    Collects and reports subscription metrics, queue status,
    and performance indicators.
    """

    def __init__(self, lock, correlation_id):
        """Initialize statistics collector.

        Args:
            lock: Threading lock for synchronization
            correlation_id: Correlation ID for logging
        """
        self._lock = lock
        self._correlation_id = correlation_id

    def get_statistics(
        self,
        subscriptions: dict,
        entity_index: dict,
        entity_index_active: dict,
        message_queue_size: int,
        is_connected: bool,
        max_queue_size: int,
    ) -> dict[str, Any]:
        """Get subscription manager statistics.

        Args:
            subscriptions: Subscriptions dictionary
            entity_index: Entity reverse index
            entity_index_active: Active entity reverse index
            message_queue_size: Current queue size
            is_connected: WebSocket connection status
            max_queue_size: Maximum queue size

        Returns:
            Statistics dictionary
        """
        with self._lock:
            active_count = sum(1 for sub in subscriptions.values() if sub.active)
            entity_count = len(entity_index)
            active_entity_count = len(entity_index_active)

            return {
                "total_subscriptions": len(subscriptions),
                "active_subscriptions": active_count,
                "inactive_subscriptions": len(subscriptions) - active_count,
                "queued_messages": message_queue_size,
                "is_connected": is_connected,
                "max_queue_size": max_queue_size,
                # PERFORMANCE: Dual-index optimization metrics
                "tracked_entities": entity_count,
                "active_entities": active_entity_count,
                "index_efficiency_percent": round(
                    (active_entity_count / entity_count * 100) if entity_count > 0 else 100, 2
                ),
            }

    def get_diagnostics(
        self,
        subscriptions: dict,
        entity_index: dict,
        entity_index_active: dict,
        message_queue,
        is_connected: bool,
        max_queue_size: int,
        monitoring_active: bool,
    ) -> dict[str, Any]:
        """Get detailed diagnostic information.

        Args:
            subscriptions: Subscriptions dictionary
            entity_index: Entity reverse index
            entity_index_active: Active entity reverse index
            message_queue: Message queue
            is_connected: WebSocket connection status
            max_queue_size: Maximum queue size
            monitoring_active: Whether monitoring is active

        Returns:
            Diagnostic information dictionary
        """
        with self._lock:
            stats = self.get_statistics(
                subscriptions,
                entity_index,
                entity_index_active,
                len(message_queue),
                is_connected,
                max_queue_size,
            )

            # Calculate additional metrics
            queue_pressure = len(message_queue) / max_queue_size

            # Age of oldest and newest queued messages
            if message_queue:
                oldest_age = time.time() - message_queue[0].timestamp
                newest_age = time.time() - message_queue[-1].timestamp
            else:
                oldest_age = 0
                newest_age = 0

            # Active subscriptions by entity type
            entity_types = {}
            for sub in subscriptions.values():
                if sub.active:
                    entity_type = sub.entity_id.split(".")[0]
                    entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

            return {
                **stats,
                "queue_pressure_percent": queue_pressure * 100,
                "oldest_queged_message_age_seconds": oldest_age,
                "newest_queged_message_age_seconds": newest_age,
                "entity_subscription_types": entity_types,
                "monitoring_active": monitoring_active,
            }


__all__ = [
    "SubscriptionStatistics",
]
