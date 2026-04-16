# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Extract message queue management

"""queue_manager.py - Message Queue Manager
Version: 2026-04-11
Purpose: Manage state change message queue

This module handles:
- State change message queuing
- Queue persistence and restoration
- Queued message processing
- Queue overflow handling

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
from collections import deque
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant.ha_websocket.state_subscriptions.models import QueuedMessage
from lee.home_assistant.ha_websocket.state_subscriptions.persistence import QueuePersistence


class MessageQueueManager:
    """Manages state change message queue.

    Handles buffering of state changes during disconnection,
    with persistence for resilience and automatic processing on reconnection.
    """

    def __init__(self, lock, correlation_id, logging_fuse, max_queue_size: int = 100):
        """Initialize queue manager.

        Args:
            lock: Threading lock for synchronization
            correlation_id: Correlation ID for logging
            logging_fuse: Logging fuse for failure tracking
            max_queue_size: Maximum messages to queue
        """
        self._lock = lock
        self._correlation_id = correlation_id
        self._logging_fuse = logging_fuse
        self._message_queue: deque = deque(maxlen=max_queue_size)
        self._max_queue_size = max_queue_size
        self._persistence_key = f"ws_state_queue_{id(self)}"  # Unique key for persistence

        # Initialize persistence handler
        self._persistence = QueuePersistence(self._persistence_key, self._correlation_id)

        # Restore queue from persistence
        self._restore_queue_from_persistence()

    def queue_state_change(
        self,
        entity_id: str,
        old_state: dict[str, Any],
        new_state: dict[str, Any],
    ) -> None:
        """Queue state change for later processing.

        Args:
            entity_id: Home Assistant entity_id
            old_state: Previous state
            new_state: New state
        """
        with self._lock:
            # Check queue capacity
            if len(self._message_queue) >= self._max_queue_size:
                # Queue full - remove oldest
                self._message_queue.popleft()

                # SUGA-ISP compliance: Log
                try:
                    execute_operation(GatewayInterface.LOGGING, "log_warning",
                                     message="State change queue full, dropped oldest",
                                     corr_id=self._correlation_id,
                                     scope="WS_STATE",
                                     queue_size=len(self._message_queue))
                except (ImportError, Exception):
                    self._logging_fuse.record_failure()

            # Add to queue
            queued_msg = QueuedMessage(
                entity_id=entity_id,
                old_state=old_state,
                new_state=new_state,
            )

            self._message_queue.append(queued_msg)

            # Persist queue to disk for resilience
            self._persistence.save_queue(self._message_queue, self._max_queue_size)

    def process_queued_messages(
        self,
        subscriptions: dict,
        entity_index_active: dict,
    ) -> int:
        """Process queued state change messages.

        Call this after WebSocket reconnection.

        Args:
            subscriptions: Subscriptions dictionary
            entity_index_active: Active entity reverse index

        Returns:
            Number of messages processed
        """
        processed = 0
        queue_empty = False

        with self._lock:
            while self._message_queue:
                queued_msg = self._message_queue.popleft()

                try:
                    # Trigger callback for queued message
                    entity_id = queued_msg.entity_id

                    # PERFORMANCE: O(1) lookup using active index (no filtering needed)
                    matching_subscription_ids = entity_index_active.get(entity_id, set())
                    # Set intersection for O(1) lookup - more efficient than list comprehension
                    valid_subscription_ids = matching_subscription_ids & subscriptions.keys()
                    matching_subscriptions = [subscriptions[sub_id] for sub_id in valid_subscription_ids]

                    for subscription in matching_subscriptions:
                        try:
                            subscription.callback(
                                entity_id,
                                queued_msg.old_state,
                                queued_msg.new_state,
                            )
                        except (RuntimeError, ValueError, TypeError):
                            # Callback failed - continue processing
                            pass

                    processed += 1

                except (RuntimeError, ValueError):
                    # Message processing failed - continue with next message
                    pass

            queue_empty = not self._message_queue

        # Clear persistence after processing all messages
        if queue_empty:
            self._persistence.clear_persistence()
        else:
            # Update persistence with remaining messages
            self._persistence.save_queue(self._message_queue, self._max_queue_size)

        # SUGA-ISP compliance: Log
        try:
            execute_operation(GatewayInterface.LOGGING, "log_info",
                             message="Queued messages processed",
                             corr_id=self._correlation_id,
                             scope="WS_STATE",
                             processed=processed,
                             remaining=len(self._message_queue))
        except (ImportError, Exception):
            self._logging_fuse.record_failure()

        return processed

    def _restore_queue_from_persistence(self) -> int:
        """Restore message queue from persistent storage.

        Returns:
            Number of messages restored
        """
        try:
            # Load from persistence handler
            queue_data = self._persistence.restore_queue()

            if not queue_data:
                return 0

            # Restore queue
            restored_count = 0
            with self._lock:
                for msg_data in queue_data:
                    queued_msg = QueuedMessage(
                        entity_id=msg_data['entity_id'],
                        old_state=msg_data['old_state'],
                        new_state=msg_data['new_state'],
                        timestamp=msg_data.get('timestamp', time.time()),
                        correlation_id=msg_data.get('correlation_id'),
                    )
                    self._message_queue.append(queued_msg)
                    restored_count += 1

            return restored_count

        except Exception as e:
            # Log error but continue without persistence
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                 message="Failed to restore queue from persistence",
                                 corr_id=self._correlation_id,
                                 scope="WS_STATE",
                                 error=str(e))
            except (ImportError, Exception):
                self._logging_fuse.record_failure()

            return 0

    def get_queue_size(self) -> int:
        """Get current queue size.

        Returns:
            Number of messages in queue
        """
        with self._lock:
            return len(self._message_queue)

    def get_queue_pressure(self) -> float:
        """Get queue pressure (0.0 to 1.0).

        Returns:
            Queue pressure as ratio of current size to max size
        """
        with self._lock:
            return len(self._message_queue) / self._max_queue_size

    def emergency_flush(self, subscriptions: dict) -> int:
        """Emergency flush of queued messages when connection is critical.

        Args:
            subscriptions: Subscriptions dictionary

        Returns:
            Number of messages flushed
        """
        flushed_count = 0

        with self._lock:
            # Process all queued messages without checking subscription status
            while self._message_queue:
                queued_msg = self._message_queue.popleft()

                try:
                    # Trigger callback regardless of subscription status
                    for sub in subscriptions.values():
                        if sub.entity_id == queued_msg.entity_id:
                            sub.callback(
                                queued_msg.entity_id,
                                queued_msg.old_state,
                                queued_msg.new_state,
                            )
                            sub.last_event_time = time.time()

                    flushed_count += 1
                except (KeyError, AttributeError, TypeError):
                    # Continue flushing despite individual message errors
                    pass

        # Log emergency flush
        try:
            execute_operation(GatewayInterface.LOGGING, "log_warning",
                             message="Emergency flush of queued messages",
                             corr_id=self._correlation_id,
                             scope="WS_STATE",
                             flushed=flushed_count,
                             remaining=len(self._message_queue))
        except (ImportError, Exception):
            self._logging_fuse.record_failure()

        return flushed_count


__all__ = [
    "MessageQueueManager",
]
