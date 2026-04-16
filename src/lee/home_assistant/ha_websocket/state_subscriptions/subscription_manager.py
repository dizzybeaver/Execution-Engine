# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor into focused modules

"""subscription_manager.py - State Subscription Manager
Version: 2026-04-11
Purpose: Manage Home Assistant state subscriptions via WebSocket

This module implements WebSocket-based state subscriptions for:
- Real-time state change detection
- Proactive ChangeReport generation
- Message queue buffering for disconnection resilience
- Correlation ID tracking for request tracing

Architecture:
- SUGA-ISP compliant: Uses execute_operation for all gateway access
- Message queue: 100-message buffer during disconnection
- Automatic reconnection: Resumes subscriptions after connection loss
- Cache integration: Invalidates cache on state changes

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import time
from threading import RLock
from typing import Any, Callable, Optional

from lee.circuit_breaker.circuit_breaker_core import CircuitBreaker
from lee.circuit_breaker.circuit_breaker_manager import get_circuit_breaker_manager
from lee.circuit_breaker.logging_fuse import LoggingFuse
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.home_assistant.ha_websocket.state_subscriptions.connection_manager import ConnectionManager
from lee.home_assistant.ha_websocket.state_subscriptions.monitoring import WebSocketMonitor
from lee.home_assistant.ha_websocket.state_subscriptions.queue_manager import MessageQueueManager
from lee.home_assistant.ha_websocket.state_subscriptions.state_event_handler import StateEventHandler
from lee.home_assistant.ha_websocket.state_subscriptions.subscription_lifecycle import SubscriptionLifecycleManager
from lee.home_assistant.ha_websocket.state_subscriptions.subscription_statistics import SubscriptionStatistics


class StateSubscriptionManager:
    """WebSocket State Subscription Manager.

    Manages subscriptions to Home Assistant state changes with:
    - Real-time state change detection
    - Message queue buffering (100 messages)
    - Automatic reconnection handling
    - Cache invalidation on state changes
    """

    def __init__(self, max_queue_size: int = 100):
        """Initialize subscription manager.

        Args:
            max_queue_size: Maximum messages to queue during disconnection
        """
        self._subscriptions: dict[str, Any] = {}
        self._lock = RLock()
        self._max_queue_size = max_queue_size
        self._correlation_id = generate_correlation_id("ws_state")

        # PERFORMANCE: Dual reverse indexes for O(1) entity_id lookup
        # entity_id -> set of subscription_ids (all)
        self._entity_index: dict[str, set[str]] = {}
        # entity_id -> set of subscription_ids (active only)
        self._entity_index_active: dict[str, set[str]] = {}

        # Subscription cleanup configuration
        self._subscription_ttl_seconds = int(os.environ.get("SUBSCRIPTION_TTL_SECONDS", "3600"))  # 1 hour default

        # Initialize logging fuse
        self._logging_fuse = LoggingFuse(name="state_subscriptions")

        # Observability Circuit Breaker - CBFuse Phase 2.1
        # Monitors observability failures - unexpected failures that need investigation
        self._obs_breaker: Optional[CircuitBreaker] = None
        try:
            cb_manager = get_circuit_breaker_manager()

            # Get or create observability circuit breaker
            self._obs_breaker = cb_manager.get(
                name="observability",
                failure_threshold=3,
                timeout=60,
                enable_cbfuse=True,  # Monitored breaker - trips indicate problems
                correlation_id=self._correlation_id
            )

            # Log circuit breaker initialization
            execute_operation(
                GatewayInterface.LOGGING, "log_info",
                message="ObservabilityCircuitBreaker initialized",
                corr_id=self._correlation_id,
                scope="WS_STATE",
                breaker_name="observability",
                enable_cbfuse=True,
                threshold=3
            )
        except Exception as e:
            # Log error but continue without circuit breaker
            try:
                execute_operation(
                    GatewayInterface.LOGGING, "log_error",
                    message="Failed to initialize ObservabilityCircuitBreaker",
                    corr_id=self._correlation_id,
                    scope="WS_STATE",
                    error=str(e)
                )
            except (ImportError, Exception):
                pass  # Logging not available

        # Initialize focused module managers
        self._connection_manager = ConnectionManager(
            self._lock,
            self._correlation_id,
            self._logging_fuse,
        )

        self._queue_manager = MessageQueueManager(
            self._lock,
            self._correlation_id,
            self._logging_fuse,
            max_queue_size,
        )

        self._event_handler = StateEventHandler(
            self._lock,
            self._correlation_id,
            self._logging_fuse,
            self._obs_breaker,
            self._queue_manager.queue_state_change,
        )

        self._lifecycle_manager = SubscriptionLifecycleManager(
            self._lock,
            self._correlation_id,
            self._logging_fuse,
            None,  # WebSocket connection reference
            None,  # OAuth token reference
        )

        self._statistics = SubscriptionStatistics(
            self._lock,
            self._correlation_id,
        )

        # SUGA-ISP compliance: Log initialization
        try:
            execute_operation(GatewayInterface.LOGGING, "log_info",
                             message="StateSubscriptionManager initialized",
                             corr_id=self._correlation_id,
                             scope="WS_STATE",
                             max_queue_size=max_queue_size,
                             resilience_features=[
                             "auto-reconnect", "message-queue", "state-sync", "queue-persistence"],
                             performance_features=["entity_index", "O1_lookup"])
        except (ImportError, Exception):
            self._logging_fuse.record_failure()

        # Start monitoring for connection resilience
        self.start_monitoring()

    def subscribe(
        self,
        entity_id: str,
        callback: Callable[[dict[str, Any]], None],
        active: bool = True,
    ) -> str:
        """Subscribe to state changes for an entity.

        Args:
            entity_id: Entity ID to watch
            callback: Function to call when state changes
            active: Whether to activate immediately

        Returns:
            Subscription ID for tracking/unsubscribing
        """
        self._record_activity()  # Record subscription activity
        ws_connection = self._connection_manager.get_connection()
        return self._lifecycle_manager.create_subscription(
            self._subscriptions,
            self._entity_index,
            self._entity_index_active,
            entity_id,
            callback,
            active,
            ws_connection,
        )

    def set_subscription_active(self, subscription_id: str, active: bool) -> bool:
        """Set subscription active status.

        Args:
            subscription_id: Subscription ID from subscribe()
            active: True to activate, False to deactivate

        Returns:
            True if status updated, False if not found
        """
        return self._lifecycle_manager.set_subscription_active(
            self._subscriptions,
            self._entity_index_active,
            subscription_id,
            active,
        )

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from state changes.

        Args:
            subscription_id: Subscription ID from subscribe()

        Returns:
            True if unsubscribed, False if not found
        """
        self._record_activity()  # Record unsubscription activity
        ws_connection = self._connection_manager.get_connection()
        return self._lifecycle_manager.remove_subscription(
            self._subscriptions,
            self._entity_index,
            self._entity_index_active,
            subscription_id,
            ws_connection,
        )

    def handle_state_changed_event(
        self,
        event_data: dict[str, Any],
        oauth_token: str,
    ) -> None:
        """Handle state_changed event from WebSocket.

        Args:
            event_data: Event data from Home Assistant
            oauth_token: OAuth token for ChangeReport
        """
        is_connected = self._connection_manager.is_connected()
        self._event_handler.handle_state_changed_event(
            event_data,
            self._subscriptions,
            self._entity_index_active,
            is_connected,
        )

    def process_queued_messages(self, oauth_token: str) -> int:
        """Process queued state change messages.

        Call this after WebSocket reconnection.

        Args:
            oauth_token: OAuth token for ChangeReport

        Returns:
            Number of messages processed
        """
        return self._queue_manager.process_queued_messages(
            self._subscriptions,
            self._entity_index_active,
        )

    def set_websocket_connection(
        self, connection, is_connected: bool, oauth_token: Optional[str] = None
    ) -> None:
        """Set active WebSocket connection.

        Args:
            connection: WebSocket connection object
            is_connected: Connection status
            oauth_token: OAuth token for reconnection and ChangeReport
        """
        was_disconnected, oauth_token = self._connection_manager.set_connection(
            connection,
            is_connected,
            oauth_token,
        )

        # If reconnected, process queued messages and resubscribe
        if is_connected and was_disconnected:
            # Process queued state changes
            self.process_queued_messages(oauth_token)

            # Resync subscriptions with fresh state
            self._connection_manager.resync_state_subscriptions(self._subscriptions)

        # If connected, resubscribe to all entities
        if is_connected:
            ws_connection = self._connection_manager.get_connection()
            self._lifecycle_manager.resubscribe_all(self._subscriptions, ws_connection)

    def is_connected(self) -> bool:
        """Check if WebSocket connection is active.

        Returns:
            True if WebSocket is connected, False otherwise
        """
        return self._connection_manager.is_connected()

    def _record_activity(self) -> None:
        """Record recent activity for adaptive monitoring."""
        # This will be used by the monitor
        pass

    def start_monitoring(self) -> None:
        """Start WebSocket connection monitoring for resilience."""
        # Create monitor instance
        self._monitor = WebSocketMonitor(
            self._correlation_id,
            self._queue_manager._message_queue,
            self._max_queue_size,
            self._subscription_ttl_seconds,
        )

        # Start monitoring
        ws_connection = self._connection_manager.get_connection()
        self._monitor.start_monitoring(
            ws_connection,
            self._send_ping,
            self._cleanup_stale_subscriptions,
        )

    def stop_monitoring(self) -> None:
        """Stop WebSocket monitoring thread gracefully."""
        if hasattr(self, '_monitor'):
            self._monitor.stop_monitoring()

    def _cleanup_stale_subscriptions(self) -> None:
        """Clean up stale and inactive subscriptions to prevent memory leaks.

        Removes subscriptions that:
        - Are marked as inactive
        - Haven't received events in SUBSCRIPTION_TTL_SECONDS
        - Have never received events after 24 hours
        """
        with self._lock:
            current_time = time.time()
            subscriptions_to_remove = []

            for subscription_id, subscription in self._subscriptions.items():
                # Remove inactive subscriptions
                if not subscription.active:
                    subscriptions_to_remove.append(subscription_id)
                    continue

                # Remove stale subscriptions (no events for TTL period)
                if subscription.last_event_time > 0:
                    stale_time = current_time - subscription.last_event_time
                    if stale_time > self._subscription_ttl_seconds:
                        subscriptions_to_remove.append(subscription_id)
                        continue

                # Remove orphaned subscriptions (created but never received events after 24h)
                if subscription.last_event_time == 0:
                    orphan_time = current_time - subscription.subscribe_time
                    if orphan_time > 86400:  # 24 hours
                        subscriptions_to_remove.append(subscription_id)
                        continue

            # Remove identified subscriptions
            for subscription_id in subscriptions_to_remove:
                subscription = self._subscriptions[subscription_id]
                entity_id = subscription.entity_id

                # Remove from main storage
                del self._subscriptions[subscription_id]

                # Update reverse indexes
                if entity_id in self._entity_index and subscription_id in self._entity_index[entity_id]:
                    self._entity_index[entity_id].remove(subscription_id)
                    if not self._entity_index[entity_id]:
                        del self._entity_index[entity_id]

                if entity_id in self._entity_index_active and subscription_id in self._entity_index_active[entity_id]:
                    self._entity_index_active[entity_id].remove(subscription_id)
                    if not self._entity_index_active[entity_id]:
                        del self._entity_index_active[entity_id]

            # Log cleanup results
            if subscriptions_to_remove:
                try:
                    execute_operation(
                        GatewayInterface.LOGGING, "log_info",
                        message=f"Cleaned up {len(subscriptions_to_remove)} stale subscriptions",
                        corr_id=self._correlation_id,
                        scope="WS_STATE",
                        remaining_subscriptions=len(self._subscriptions)
                    )
                except (ImportError, Exception):
                    self._logging_fuse.record_failure()

    def _send_ping(self) -> None:
        """Send ping to WebSocket connection to keep it alive."""
        from lee.home_assistant.ha_websocket.ha_websocket_messaging import send_websocket_message
        import time

        try:
            ws_connection = self._connection_manager.get_connection()
            if ws_connection:
                ping_message = {
                    "id": int(time.time() * 1000),
                    "type": "ping",
                }

                send_websocket_message(ws_connection, ping_message)
        except Exception as e:
            # Log ping error but continue
            try:
                execute_operation(GatewayInterface.LOGGING, "log_warning",
                                 message="WebSocket ping failed",
                                 corr_id=self._correlation_id,
                                 scope="WS_STATE",
                                 error=str(e))
            except (ImportError, Exception):
                self._logging_fuse.record_failure()

    def get_statistics(self) -> dict[str, Any]:
        """Get subscription manager statistics.

        Returns:
            Statistics dictionary
        """
        return self._statistics.get_statistics(
            self._subscriptions,
            self._entity_index,
            self._entity_index_active,
            self._queue_manager.get_queue_size(),
            self._connection_manager.is_connected(),
            self._max_queue_size,
        )

    def get_diagnostics(self) -> dict[str, Any]:
        """Get detailed diagnostic information."""
        return self._statistics.get_diagnostics(
            self._subscriptions,
            self._entity_index,
            self._entity_index_active,
            self._queue_manager._message_queue,
            self._connection_manager.is_connected(),
            self._max_queue_size,
            hasattr(self, "_monitor"),
        )

    def emergency_flush(self) -> int:
        """Emergency flush of queued messages when connection is critical.

        Returns:
            Number of messages flushed
        """
        return self._queue_manager.emergency_flush(self._subscriptions)


__all__ = [
    "StateSubscriptionManager",
]
