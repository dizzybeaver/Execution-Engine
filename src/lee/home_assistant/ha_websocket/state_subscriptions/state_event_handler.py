# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Extract state change event handling

"""state_event_handler.py - State Change Event Handler
Version: 2026-04-11
Purpose: Handle Home Assistant state change events

This module handles:
- State change event processing
- Callback invocation
- Cache invalidation
- Observability metrics recording

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
from typing import Any, Callable

from lee.circuit_breaker.circuit_breaker_core import CircuitBreaker
from lee.gateway import GatewayInterface, execute_operation


class StateEventHandler:
    """Handles state change events from Home Assistant WebSocket.

    Processes incoming state change events, triggers callbacks,
    invalidates cache, and records metrics.
    """

    def __init__(
        self,
        lock,
        correlation_id,
        logging_fuse,
        obs_breaker: CircuitBreaker,
        queue_state_change_func: Callable,
    ):
        """Initialize event handler.

        Args:
            lock: Threading lock for synchronization
            correlation_id: Correlation ID for logging
            logging_fuse: Logging fuse for failure tracking
            obs_breaker: Observability circuit breaker
            queue_state_change_func: Function to queue state changes
        """
        self._lock = lock
        self._correlation_id = correlation_id
        self._logging_fuse = logging_fuse
        self._obs_breaker = obs_breaker
        self._queue_state_change = queue_state_change_func

    def handle_state_changed_event(
        self,
        event_data: dict[str, Any],
        subscriptions: dict,
        entity_index_active: dict,
        is_connected: bool,
    ) -> None:
        """Handle state_changed event from WebSocket.

        Args:
            event_data: Event data from Home Assistant
            subscriptions: Subscriptions dictionary
            entity_index_active: Active entity reverse index
            is_connected: WebSocket connection status
        """
        start_time = time.time()
        entity_id = event_data.get("entity_id")
        success = True

        try:
            entity_id = event_data.get("entity_id")
            old_state = event_data.get("old_state", {})
            new_state = event_data.get("new_state", {})

            if not entity_id:
                success = False
                return

            # Invalidate cache for this entity
            self._invalidate_entity_cache(entity_id)

            # PERFORMANCE: O(1) lookup using active index (no filtering needed)
            with self._lock:
                matching_subscription_ids = entity_index_active.get(entity_id, set())
                # Set intersection for O(1) lookup - more efficient than list comprehension
                valid_subscription_ids = matching_subscription_ids & subscriptions.keys()
                matching_subscriptions = [subscriptions[sub_id] for sub_id in valid_subscription_ids]

            # Trigger callbacks
            for subscription in matching_subscriptions:
                try:
                    subscription.callback(entity_id, old_state, new_state)
                    subscription.last_event_time = time.time()
                except Exception as e:
                    success = False
                    # Log callback error
                    try:
                        execute_operation(GatewayInterface.LOGGING, "log_error",
                                         message="State change callback error",
                                         corr_id=self._correlation_id,
                                         scope="WS_STATE",
                                         entity_id=entity_id,
                                         error=str(e))
                    except (ImportError, Exception):
                        self._logging_fuse.record_failure()

            # Queue message for ChangeReport
            if not is_connected:
                self._queue_state_change(entity_id, old_state, new_state)

            # Record metrics via observability gateway
            try:
                obs = execute_operation(GatewayInterface.OBSERVABILITY, 'get_observability')
                duration_ms = (time.time() - start_time) * 1000
                obs.record_request("state_changed_event", duration_ms, success,
                                 self._correlation_id,
                                 entity_id=entity_id,
                                 callbacks_triggered=len(matching_subscriptions))

                # Record success for observability circuit breaker
                if self._obs_breaker:
                    self._obs_breaker.record_success()
            except (ImportError, Exception) as e:
                # Record failure for observability circuit breaker
                if self._obs_breaker:
                    self._obs_breaker.record_failure(str(e))

            # SUGA-ISP compliance: Log
            try:
                execute_operation(GatewayInterface.LOGGING, "log_info",
                                 message="State changed event processed",
                                 corr_id=self._correlation_id,
                                 scope="WS_STATE",
                                 entity_id=entity_id,
                                 callbacks_triggered=len(matching_subscriptions))
            except (ImportError, Exception):
                self._logging_fuse.record_failure()

        except Exception as e:
            success = False
            # Log error
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                 message="Error handling state_changed event",
                                 corr_id=self._correlation_id,
                                 scope="WS_STATE",
                                 error=str(e))
            except (ImportError, Exception):
                self._logging_fuse.record_failure()

            # Record failure in observability
            try:
                obs = execute_operation(GatewayInterface.OBSERVABILITY, 'get_observability')
                duration_ms = (time.time() - start_time) * 1000
                obs.record_request("state_changed_event", duration_ms, success,
                                 self._correlation_id,
                                 error=str(e))

                # Record failure for observability circuit breaker
                if self._obs_breaker:
                    self._obs_breaker.record_failure(str(e))
            except (ImportError, Exception):
                pass

    def _invalidate_entity_cache(self, entity_id: str) -> None:
        """Invalidate cache entries for entity.

        Args:
            entity_id: Home Assistant entity_id
        """
        try:
            # Invalidate entity cache
            execute_operation(
                GatewayInterface.CACHE, "invalidate_by_tags",
                tags=[f"entity:{entity_id}", "entity"],
                corr_id=self._correlation_id,
            )

            # SUGA-ISP compliance: Log
            execute_operation(GatewayInterface.LOGGING, "log_info",
                             message="Entity cache invalidated",
                             corr_id=self._correlation_id,
                             scope="WS_STATE",
                             entity_id=entity_id)

        except Exception as e:
            # Log error (non-critical)
            try:
                execute_operation(GatewayInterface.LOGGING, "log_warning",
                                 message="Failed to invalidate entity cache",
                                 corr_id=self._correlation_id,
                                 scope="WS_STATE",
                                 entity_id=entity_id,
                                 error=str(e))
            except (ImportError, Exception):
                self._logging_fuse.record_failure()


__all__ = [
    "StateEventHandler",
]
