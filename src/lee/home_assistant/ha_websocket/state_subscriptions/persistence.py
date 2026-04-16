# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - Extract persistence operations from state_subscriptions.py

"""persistence.py - Queue Persistence Operations
Version: 2026-03-05_1
Purpose: Persist and restore message queue to L2 disk cache

This module handles:
- Saving message queue to persistent storage
- Restoring queue after reconnection
- Clearing persisted data

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from collections import deque
from typing import Any

from lee.gateway import GatewayInterface, execute_operation


class QueuePersistence:
    """Handles persistence of message queue to L2 disk cache."""

    def __init__(self, persistence_key: str, correlation_id: str):
        """Initialize persistence handler.

        Args:
            persistence_key: Unique key for persistence
            correlation_id: Correlation ID for logging
        """
        self._persistence_key = persistence_key
        self._correlation_id = correlation_id

    def save_queue(
        self,
        message_queue: deque,
        max_queue_size: int,
    ) -> bool:
        """Save message queue to persistent storage (L2 disk cache).

        Args:
            message_queue: Queue to persist
            max_queue_size: Maximum queue size

        Returns:
            Success status
        """
        try:
            # Convert queue to list for serialization
            queue_list = list(message_queue)

            # Convert QueuedMessage objects to dicts
            from lee.home_assistant.ha_websocket.state_subscriptions.models import QueuedMessage

            queue_data = [
                {
                    'entity_id': msg.entity_id,
                    'old_state': msg.old_state,
                    'new_state': msg.new_state,
                    'timestamp': msg.timestamp,
                    'correlation_id': msg.correlation_id,
                }
                for msg in queue_list
                if isinstance(msg, QueuedMessage)
            ]

            # Save to L2 cache with 1 hour TTL
            from lee.lee_cache.cache_l2_disk import l2_set

            return l2_set(
                self._persistence_key,
                queue_data,
                ttl=3600,  # 1 hour
                correlation_id=self._correlation_id,
            )

        except Exception as e:
            # Log error but don't fail operation
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_error",
                    message="Failed to save queue to persistence",
                    corr_id=self._correlation_id,
                    scope="WS_STATE",
                    error=str(e)
                )
            except (ImportError, Exception):
                pass  # Logging not available

            return False

    def restore_queue(self) -> list[dict[str, Any]]:
        """Restore message queue from persistent storage.

        Returns:
            List of queue message data
        """
        try:
            # Load from L2 cache
            from lee.lee_cache.cache_l2_disk import l2_get

            queue_data = l2_get(
                self._persistence_key,
                default=[],
                correlation_id=self._correlation_id,
            )

            if not queue_data:
                return []

            # Log restoration
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_info",
                    message="Restored queue from persistence",
                    corr_id=self._correlation_id,
                    scope="WS_STATE",
                    restored_count=len(queue_data)
                )
            except (ImportError, Exception):
                pass  # Logging not available

            return queue_data

        except Exception as e:
            # Log error but continue without persistence
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_error",
                    message="Failed to restore queue from persistence",
                    corr_id=self._correlation_id,
                    scope="WS_STATE",
                    error=str(e)
                )
            except (ImportError, Exception):
                pass  # Logging not available

            return []

    def clear_persistence(self) -> bool:
        """Clear persisted queue data.

        Returns:
            Success status
        """
        try:
            from lee.lee_cache.cache_l2_disk import l2_set

            return l2_set(
                self._persistence_key,
                [],  # Empty list
                ttl=60,  # Short TTL
                correlation_id=self._correlation_id,
            )

        except (ImportError, AttributeError, OSError):
            # L2 cache unavailable or disk error
            return False


__all__ = [
    "QueuePersistence",
]
