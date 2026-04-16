# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Extract WebSocket connection management

"""connection_manager.py - WebSocket Connection Manager
Version: 2026-04-11
Purpose: Manage WebSocket connection lifecycle

This module handles:
- WebSocket connection tracking
- OAuth token management
- Connection state synchronization
- Reconnection handling

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Optional

from lee.gateway import GatewayInterface, execute_operation


class ConnectionManager:
    """Manages WebSocket connection state.

    Tracks connection status, manages OAuth token,
    and handles reconnection synchronization.
    """

    def __init__(self, lock, correlation_id, logging_fuse):
        """Initialize connection manager.

        Args:
            lock: Threading lock for synchronization
            correlation_id: Correlation ID for logging
            logging_fuse: Logging fuse for failure tracking
        """
        self._lock = lock
        self._correlation_id = correlation_id
        self._logging_fuse = logging_fuse

        # WebSocket connection tracking
        self._ws_connection = None
        self._is_connected = False
        self._subscription_id = None

        # OAuth token for reconnection and ChangeReport
        self._oauth_token: Optional[str] = None

    def set_connection(
        self,
        connection,
        is_connected: bool,
        oauth_token: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """Set active WebSocket connection.

        Args:
            connection: WebSocket connection object
            is_connected: Connection status
            oauth_token: OAuth token for reconnection and ChangeReport

        Returns:
            Tuple of (was_disconnected, oauth_token)
        """
        with self._lock:
            was_disconnected = not self._is_connected
            self._ws_connection = connection
            self._is_connected = is_connected

            # Store OAuth token for reconnection
            if oauth_token:
                self._oauth_token = oauth_token

            return was_disconnected, self._get_oauth_token()

    def is_connected(self) -> bool:
        """Check if WebSocket connection is active.

        Returns:
            True if WebSocket is connected, False otherwise
        """
        with self._lock:
            return self._is_connected

    def get_connection(self):
        """Get current WebSocket connection.

        Returns:
            WebSocket connection object or None
        """
        with self._lock:
            return self._ws_connection

    def get_subscription_id(self) -> Optional[int]:
        """Get subscription ID.

        Returns:
            Subscription ID or None
        """
        with self._lock:
            return self._subscription_id

    def set_subscription_id(self, subscription_id: int) -> None:
        """Set subscription ID.

        Args:
            subscription_id: Subscription ID from WebSocket
        """
        with self._lock:
            self._subscription_id = subscription_id

    def _get_oauth_token(self) -> str:
        """Get OAuth token for reconnection and ChangeReport processing.

        Returns:
            Stored OAuth token
        """
        if not self._oauth_token:
            # Fallback: try to get token from config
            try:
                ha_config = execute_operation(GatewayInterface.CONFIG, "get_ha_config")
                token = ha_config.get("token") if ha_config else None
                if token:
                    self._oauth_token = token
                    return token
            except (KeyError, AttributeError, RuntimeError):
                # Gateway unavailable
                pass

            # No token available - log warning and return empty string
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_warning",
                    message="No OAuth token available for resync",
                    corr_id=self._correlation_id,
                    scope="WS_STATE",
                )
            except (KeyError, AttributeError, RuntimeError):
                self._logging_fuse.record_failure()

            return ""

        return self._oauth_token

    def resync_state_subscriptions(self, subscriptions: dict) -> None:
        """Resync subscriptions with fresh state after reconnection.

        Args:
            subscriptions: Subscriptions dictionary
        """
        try:
            # Get current state for all subscribed entities
            entity_ids = list(set(sub.entity_id for sub in subscriptions.values() if sub.active))

            # Request fresh state for each entity
            for entity_id in entity_ids:
                # This would typically call HA API to get current state
                # For now, log the resync request
                execute_operation(GatewayInterface.LOGGING, "log_info",
                                 message=f"Resyncing state for entity: {entity_id}",
                                 corr_id=self._correlation_id,
                                 scope="WS_STATE")

        except Exception as e:
            # Log error but continue
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                                 message="Failed to resync state subscriptions",
                                 corr_id=self._correlation_id,
                                 scope="WS_STATE",
                                 error=str(e))
            except (ImportError, Exception):
                self._logging_fuse.record_failure()


__all__ = [
    "ConnectionManager",
]
