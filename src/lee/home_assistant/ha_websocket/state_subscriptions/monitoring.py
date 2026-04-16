# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - Extract monitoring operations from state_subscriptions.py

from typing import Optional
"""monitoring.py - WebSocket Monitoring and Subscription Cleanup
Version: 2026-03-05_1
Purpose: Monitor WebSocket connection and clean up stale subscriptions

This module handles:
- WebSocket connection monitoring (keep-alive pings)
- Queue pressure monitoring
- Stale subscription cleanup
- Adaptive sleep intervals based on activity

Copyright 2026 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import threading
import time
from collections import deque

from lee.gateway import GatewayInterface, execute_operation


class WebSocketMonitor:
    """Monitors WebSocket connection and manages subscription lifecycle."""

    def __init__(
        self,
        correlation_id: str,
        message_queue: deque,
        max_queue_size: int,
        subscription_ttl_seconds: int = 3600,
    ):
        """Initialize WebSocket monitor.

        Args:
            correlation_id: Correlation ID for logging
            message_queue: Message queue to monitor
            max_queue_size: Maximum queue size
            subscription_ttl_seconds: Subscription TTL in seconds (default 1 hour)
        """
        self._correlation_id = correlation_id
        self._message_queue = message_queue
        self._max_queue_size = max_queue_size
        self._subscription_ttl_seconds = subscription_ttl_seconds

        # Thread control
        self._stop_event = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None

        # Adaptive monitoring sleep configuration
        self._min_sleep_seconds = 1  # Fast polling during activity
        self._max_sleep_seconds = 5  # Normal polling interval
        self._last_activity_time = time.time()
        self._activity_timeout_seconds = 60  # Switch to slow poll after 60s idle

        # Cleanup tracking
        self._last_cleanup_time = time.time()

    def start_monitoring(
        self,
        ws_connection,
        ping_callback,
        cleanup_callback,
    ) -> None:
        """Start WebSocket connection monitoring for resilience.

        Args:
            ws_connection: WebSocket connection object
            ping_callback: Function to send ping
            cleanup_callback: Function to clean up subscriptions
        """

        def monitor_loop():
            while not self._stop_event.is_set():
                try:
                    # Check connection status
                    if ws_connection:
                        # Send ping to keep connection alive
                        ping_callback()

                    # Check for queue pressure
                    queue_pressure = len(self._message_queue) / self._max_queue_size
                    if queue_pressure > 0.8:  # 80% queue full
                        self._handle_queue_pressure()
                        self._record_activity()  # Activity detected

                    # Clean up stale subscriptions (every 5 minutes)
                    if time.time() - self._last_cleanup_time > 300:
                        cleanup_callback()
                        self._last_cleanup_time = time.time()

                    # Adaptive sleep based on recent activity
                    sleep_time = self._get_adaptive_sleep_time()
                    time.sleep(sleep_time)
                except Exception as e:
                    # Continue monitoring even if there are errors
                    try:
                        execute_operation(
                            GatewayInterface.LOGGING,
                            "log_warning",
                            message=f"Monitor loop error: {e}",
                            corr_id=self._correlation_id,
                            scope="WS_STATE",
                        )
                    except (KeyError, AttributeError, RuntimeError):
                        pass  # Gateway unavailable

                    # Use adaptive sleep even after errors
                    sleep_time = self._get_adaptive_sleep_time()
                    time.sleep(sleep_time)

        # Start monitoring in background
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()

        # Log monitoring start
        try:
            execute_operation(
                GatewayInterface.LOGGING,
                "log_info",
                message="WebSocket monitoring started",
                corr_id=self._correlation_id,
                scope="WS_STATE"
            )
        except (KeyError, AttributeError, RuntimeError):
            pass  # Gateway unavailable

    def stop_monitoring(self) -> None:
        """Stop WebSocket monitoring thread gracefully."""
        self._stop_event.set()
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=5)
            if self._monitor_thread.is_alive():
                # Thread did not stop gracefully
                try:
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_warning",
                        message="Monitor thread did not stop within timeout",
                        corr_id=self._correlation_id,
                        scope="WS_STATE",
                    )
                except (KeyError, AttributeError, RuntimeError):
                    pass  # Gateway unavailable
            self._monitor_thread = None

    def _record_activity(self) -> None:
        """Record recent activity for adaptive monitoring."""
        self._last_activity_time = time.time()

    def _get_adaptive_sleep_time(self) -> float:
        """Calculate adaptive sleep time based on recent activity.

        Returns:
            Sleep time in seconds (1-5 seconds depending on activity)
        """
        time_since_activity = time.time() - self._last_activity_time

        if time_since_activity < self._activity_timeout_seconds:
            return self._min_sleep_seconds
        else:
            return self._max_sleep_seconds

    def _handle_queue_pressure(self) -> None:
        """Handle high queue pressure by logging warnings."""
        queue_usage = len(self._message_queue)
        pressure_level = queue_usage / self._max_queue_size

        if pressure_level > 0.9:  # 90% full
            # Log critical pressure
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_error",
                    message="WebSocket queue critical pressure",
                    corr_id=self._correlation_id,
                    scope="WS_STATE",
                    queue_usage=queue_usage,
                    max_size=self._max_queue_size
                )
            except (KeyError, AttributeError, RuntimeError):
                pass  # Gateway unavailable


__all__ = [
    "WebSocketMonitor",
]
