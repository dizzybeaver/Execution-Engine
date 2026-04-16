# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Extract subscription lifecycle management

"""subscription_lifecycle.py - Subscription Lifecycle Management
Version: 2026-04-11
Purpose: Manage subscription creation, activation, and removal

This module handles:
- Subscription creation and ID generation
- Subscription activation/deactivation
- Subscription removal and cleanup
- WebSocket subscription/unsubscription messages

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import random
import time
from typing import Any, Callable

from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant.ha_websocket.ha_websocket_messaging import send_websocket_message
from lee.home_assistant.ha_websocket.state_subscriptions.models import StateSubscription


class SubscriptionLifecycleManager:
    """Manages subscription lifecycle operations.

    Handles subscription creation, activation, deactivation, and removal
    with proper index maintenance and WebSocket synchronization.
    """

    def __init__(self, lock, correlation_id, logging_fuse, ws_connection_ref, oauth_token_ref):
        """Initialize lifecycle manager.

        Args:
            lock: Threading lock for synchronization
            correlation_id: Correlation ID for logging
            logging_fuse: Logging fuse for failure tracking
            ws_connection_ref: Reference to WebSocket connection
            oauth_token_ref: Reference to OAuth token
        """
        self._lock = lock
        self._correlation_id = correlation_id
        self._logging_fuse = logging_fuse
        self._ws_connection_ref = ws_connection_ref
        self._oauth_token_ref = oauth_token_ref

    def create_subscription(
        self,
        subscriptions: dict,
        entity_index: dict,
        entity_index_active: dict,
        entity_id: str,
        callback: Callable[[dict[str, Any]], None],
        active: bool = True,
        ws_connection = None,
    ) -> str:
        """Create a new subscription.

        Args:
            subscriptions: Subscriptions dictionary
            entity_index: Entity reverse index
            entity_index_active: Active entity reverse index
            entity_id: Entity ID to watch
            callback: Function to call when state changes
            active: Whether to activate immediately
            ws_connection: WebSocket connection (optional)

        Returns:
            Subscription ID for tracking/unsubscribing
        """
        with self._lock:
            # Ensure unique subscription IDs (add random component)
            subscription_id = f"sub_{entity_id}_{int(time.time())}_{random.randbytes(4).hex()}"

            subscription = StateSubscription(
                entity_id=entity_id,
                callback=callback,
                active=True,
            )

            subscriptions[subscription_id] = subscription

            # PERFORMANCE: Update both reverse indexes for O(1) lookups
            if entity_id not in entity_index:
                entity_index[entity_id] = set()
            entity_index[entity_id].add(subscription_id)

            # Active subscriptions index (for fast event filtering)
            if entity_id not in entity_index_active:
                entity_index_active[entity_id] = set()
            entity_index_active[entity_id].add(subscription_id)

            # SUGA-ISP compliance: Log subscription
            try:
                execute_operation(GatewayInterface.LOGGING, "log_info",
                                 message="State subscription created",
                                 corr_id=self._correlation_id,
                                 scope="WS_STATE",
                                 entity_id=entity_id,
                                 subscription_id=subscription_id,
                                 total_subscriptions=len(subscriptions))
            except (ImportError, Exception):
                self._logging_fuse.record_failure()

            # If connected, subscribe via WebSocket
            if ws_connection:
                self._subscribe_via_websocket(ws_connection, entity_id)

            return subscription_id

    def set_subscription_active(
        self,
        subscriptions: dict,
        entity_index_active: dict,
        subscription_id: str,
        active: bool,
    ) -> bool:
        """Set subscription active status.

        Args:
            subscriptions: Subscriptions dictionary
            entity_index_active: Active entity reverse index
            subscription_id: Subscription ID from subscribe()
            active: True to activate, False to deactivate

        Returns:
            True if status updated, False if not found
        """
        with self._lock:
            if subscription_id not in subscriptions:
                return False

            subscription = subscriptions[subscription_id]
            was_active = subscription.active
            subscription.active = active
            entity_id = subscription.entity_id

            # Update active index if status changed
            if was_active != active:
                if active:
                    # Adding to active index
                    if entity_id not in entity_index_active:
                        entity_index_active[entity_id] = set()
                    entity_index_active[entity_id].add(subscription_id)
                else:
                    # Removing from active index
                    if entity_id in entity_index_active and subscription_id in entity_index_active[entity_id]:
                        entity_index_active[entity_id].remove(subscription_id)
                        if not entity_index_active[entity_id]:
                            del entity_index_active[entity_id]

                # SUGA-ISP compliance: Log
                try:
                    execute_operation(GatewayInterface.LOGGING, "log_info",
                                     message="Subscription active status changed",
                                     corr_id=self._correlation_id,
                                     scope="WS_STATE",
                                     entity_id=entity_id,
                                     subscription_id=subscription_id,
                                     active=active)
                except (ImportError, Exception):
                    self._logging_fuse.record_failure()

            return True

    def remove_subscription(
        self,
        subscriptions: dict,
        entity_index: dict,
        entity_index_active: dict,
        subscription_id: str,
        ws_connection = None,
    ) -> bool:
        """Remove a subscription.

        Args:
            subscriptions: Subscriptions dictionary
            entity_index: Entity reverse index
            entity_index_active: Active entity reverse index
            subscription_id: Subscription ID from subscribe()
            ws_connection: WebSocket connection (optional)

        Returns:
            True if unsubscribed, False if not found
        """
        with self._lock:
            if subscription_id not in subscriptions:
                return False

            subscription = subscriptions[subscription_id]
            entity_id = subscription.entity_id

            # Remove subscription
            del subscriptions[subscription_id]

            # PERFORMANCE: Update both reverse indexes
            if entity_id in entity_index and subscription_id in entity_index[entity_id]:
                entity_index[entity_id].remove(subscription_id)
                if not entity_index[entity_id]:
                    del entity_index[entity_id]

            if entity_id in entity_index_active and subscription_id in entity_index_active[entity_id]:
                entity_index_active[entity_id].remove(subscription_id)
                if not entity_index_active[entity_id]:
                    del entity_index_active[entity_id]

            # If connected, unsubscribe via WebSocket
            if ws_connection:
                self._unsubscribe_via_websocket(ws_connection, entity_id)

            # SUGA-ISP compliance: Log unsubscription
            try:
                execute_operation(GatewayInterface.LOGGING, "log_info",
                                 message="State subscription removed",
                                 corr_id=self._correlation_id,
                                 scope="WS_STATE",
                                 entity_id=entity_id,
                                 subscription_id=subscription_id,
                                 remaining_subscriptions=len(subscriptions))
            except (ImportError, Exception):
                self._logging_fuse.record_failure()

            return True

    def _subscribe_via_websocket(self, ws_connection, entity_id: str) -> None:
        """Subscribe to entity state changes via WebSocket.

        Args:
            ws_connection: WebSocket connection
            entity_id: Home Assistant entity_id
        """
        try:
            # Subscribe to fire_event style messages
            subscribe_message = {
                "id": self._generate_message_id(),
                "type": "subscribe_events",
                "event_type": "state_changed",
                "event_data": {
                    "entity_id": entity_id,
                },
            }

            # Send via WebSocket connection
            if ws_connection:
                # Use HA WebSocket messaging via gateway
                send_websocket_message(ws_connection, subscribe_message)

                # SUGA-ISP compliance: Log
                try:
                    execute_operation(GatewayInterface.LOGGING, "log_info",
                                     message="WebSocket subscription sent",
                                     corr_id=self._correlation_id,
                                     scope="WS_STATE",
                                     entity_id=entity_id)
                except (ImportError, Exception):
                    self._logging_fuse.record_failure()

        except Exception as e:
            # Log error
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                 message="Failed to subscribe via WebSocket",
                                 corr_id=self._correlation_id,
                                 scope="WS_STATE",
                                 entity_id=entity_id,
                                 error=str(e))
            except (ImportError, Exception):
                self._logging_fuse.record_failure()

    def _unsubscribe_via_websocket(self, ws_connection, entity_id: str, subscription_id: int = None) -> None:
        """Unsubscribe from entity state changes via WebSocket.

        Args:
            ws_connection: WebSocket connection
            entity_id: Home Assistant entity_id
            subscription_id: Subscription ID to unsubscribe
        """
        try:
            unsubscribe_message = {
                "id": self._generate_message_id(),
                "type": "unsubscribe_events",
                "subscription": subscription_id,
            }

            # Send via WebSocket connection
            if ws_connection:
                send_websocket_message(ws_connection, unsubscribe_message)

        except Exception as e:
            # Log error
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                 message="Failed to unsubscribe via WebSocket",
                                 corr_id=self._correlation_id,
                                 scope="WS_STATE",
                                 entity_id=entity_id,
                                 error=str(e))
            except (ImportError, Exception):
                self._logging_fuse.record_failure()

    def _generate_message_id(self) -> int:
        """Generate unique message ID for WebSocket."""
        return int(time.time() * 1000)

    def resubscribe_all(self, subscriptions: dict, ws_connection) -> None:
        """Resubscribe to all entities after reconnection.

        Args:
            subscriptions: Subscriptions dictionary
            ws_connection: WebSocket connection
        """
        # Get unique entity IDs
        entity_ids = set(sub.entity_id for sub in subscriptions.values())

        # Subscribe to each entity
        for entity_id in entity_ids:
            self._subscribe_via_websocket(ws_connection, entity_id)

        # SUGA-ISP compliance: Log
        try:
            execute_operation(GatewayInterface.LOGGING, "log_info",
                             message="Resubscribed to all entities",
                             corr_id=self._correlation_id,
                             scope="WS_STATE",
                             entity_count=len(entity_ids))
        except (ImportError, Exception):
            self._logging_fuse.record_failure()


__all__ = [
    "SubscriptionLifecycleManager",
]
