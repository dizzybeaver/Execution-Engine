# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-09 - Implement proactive state reporting for Alexa


"""ha_state_reporting.py - Proactive State Reporting for Alexa
Version: 2026-04-09_1
Purpose: Listen for Home Assistant state changes and report to Alexa

This module provides:
- StateChangeReporter for proactive state reporting
- MessageCoalescer for batching rapid state changes
- Significant change filtering to avoid spam
- Alexa Gateway API integration
- Rate limiting and error handling

Architecture:
- All HA operations use gateway pattern
- Message coalescing window (100ms default)
- Significant change detection per entity type
- Rate limiting (max 1 report per second per endpoint)
- Comprehensive debug logging with timing

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os
import time
import uuid
from threading import Lock
from typing import Any
from datetime import datetime, UTC

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.wrappers import http
from lee.lee_security.security_validation import SecurityValidator


def log_debug(message: str, **context: Any) -> None:
    """Log debug message through LEE gateway.

    Args:
        message: Log message
        **context: Additional context fields
    """
    if os.environ.get("LEE_DEBUG", "false").lower() == "true":
        try:
            execute_operation(
                GatewayInterface.DEBUG,
                "log",
                message=message,
                **context,
            )
        except (AttributeError, RuntimeError):
            pass


def metrics_increment(metric_name: str, value: float = 1.0, **tags: Any) -> None:
    """Increment metric through LEE gateway.

    Args:
        metric_name: Metric name
        value: Value to increment
        **tags: Metric tags
    """
    try:
        execute_operation(
            GatewayInterface.OBSERVABILITY,
            "increment",
            metric_name=metric_name,
            value=value,
            **tags,
        )
    except (AttributeError, ImportError, RuntimeError):
        pass


class MessageCoalescer:
    """Coalesce rapid state changes into single updates.

    Prevents spamming Alexa with rapid state changes by batching
    updates within a coalescing window (default 100ms).
    """

    def __init__(self, coalesce_window_ms: int = 100) -> None:
        """Initialize message coalescer.

        Args:
            coalesce_window_ms: Coalescing window in milliseconds
        """
        self.coalesce_window_ms = coalesce_window_ms
        self._pending_changes: dict[str, Any] = {}
        self._last_report_time: dict[str, float] = {}
        self._lock = Lock()

    def should_report(
        self,
        entity_id: str,
        properties: list[dict[str, Any]],
    ) -> bool:
        """Check if state change should be reported.

        Args:
            entity_id: Entity ID
            properties: List of Alexa properties

        Returns:
            True if change should be reported
        """
        with self._lock:
            current_time = time.perf_counter()

            # Check rate limiting (max 1 report per second per endpoint)
            last_report = self._last_report_time.get(entity_id, 0)
            if current_time - last_report < 1.0:
                # Within rate limit window, coalesce
                self._pending_changes[entity_id] = properties
                return False

            # Check coalescing window
            if entity_id in self._pending_changes:
                # Have pending changes, check if outside window
                time_since_pending = current_time - last_report
                if time_since_pending < (self.coalesce_window_ms / 1000.0):
                    # Within coalescing window, update pending
                    self._pending_changes[entity_id] = properties
                    return False

            # Outside all windows, should report
            self._last_report_time[entity_id] = current_time
            self._pending_changes.pop(entity_id, None)
            return True

    def get_pending_properties(self, entity_id: str) -> list[dict[str, Any]] | None:
        """Get pending properties for entity.

        Args:
            entity_id: Entity ID

        Returns:
            Pending properties or None
        """
        with self._lock:
            return self._pending_changes.get(entity_id)

    def clear_pending(self, entity_id: str) -> None:
        """Clear pending changes for entity.

        Args:
            entity_id: Entity ID
        """
        with self._lock:
            self._pending_changes.pop(entity_id, None)


class StateChangeReporter:
    """Proactive state reporter for Alexa.

    Listens for Home Assistant state change events and reports
    significant changes to Alexa via the Gateway API.
    """

    def __init__(self) -> None:
        """Initialize state change reporter."""
        self.message_coalescer = MessageCoalescer()
        self._alexa_endpoint: str | None = None
        self._access_token: str | None = None
        self._enabled = False

    def enable(self, alexa_endpoint: str, access_token: str) -> None:
        """Enable proactive state reporting.

        Args:
            alexa_endpoint: Alexa Gateway API endpoint
            access_token: OAuth access token

        Raises:
            ValueError: If endpoint URL or access token is invalid
        """
        validator = SecurityValidator()

        if not validator.validate_url(alexa_endpoint):
            raise ValueError(f"Invalid Alexa endpoint URL: {alexa_endpoint}")

        if not access_token or not isinstance(access_token, str):
            raise ValueError("Invalid access token")

        self._alexa_endpoint = alexa_endpoint
        self._access_token = access_token
        self._enabled = True

        log_debug(
            "StateChangeReporter enabled",
            endpoint=alexa_endpoint,
        )

    def disable(self) -> None:
        """Disable proactive state reporting."""
        self._enabled = False
        self._alexa_endpoint = None
        self._access_token = None

        log_debug("StateChangeReporter disabled")

    def on_state_change(
        self,
        entity_id: str,
        old_state: dict[str, Any] | None,
        new_state: dict[str, Any],
        correlation_id: str,
    ) -> None:
        """Handle state change event.

        Args:
            entity_id: Entity ID
            old_state: Old state dictionary (None if new entity)
            new_state: New state dictionary
            correlation_id: Correlation ID for tracking
        """
        start_time = time.perf_counter()

        if not self._enabled:
            return

        if not self._alexa_endpoint or not self._access_token:
            log_debug(
                f"[{correlation_id}] StateChangeReporter: Not configured",
                entity_id=entity_id,
            )
            return

        try:
            # Build Alexa properties from state
            properties = self._build_alexa_properties(
                entity_id=entity_id,
                old_state=old_state,
                new_state=new_state,
            )

            if not properties:
                log_debug(
                    f"[{correlation_id}] StateChangeReporter: No properties",
                    entity_id=entity_id,
                )
                return

            # Check if change is significant
            if not self._is_significant_change(
                entity_id=entity_id,
                old_state=old_state,
                new_state=new_state,
                properties=properties,
            ):
                log_debug(
                    f"[{correlation_id}] StateChangeReporter: Insignificant change",
                    entity_id=entity_id,
                )
                return

            # Check message coalescing
            if not self.message_coalescer.should_report(entity_id, properties):
                log_debug(
                    f"[{correlation_id}] StateChangeReporter: Coalesced",
                    entity_id=entity_id,
                )
                return

            # Send ChangeReport to Alexa
            self._send_change_report(
                entity_id=entity_id,
                properties=properties,
                correlation_id=correlation_id,
            )

            duration_ms = (time.perf_counter() - start_time) * 1000

            log_debug(
                f"[{correlation_id}] StateChangeReporter: Success",
                entity_id=entity_id,
                property_count=len(properties),
                duration_ms=f"{duration_ms:.2f}",
            )

            metrics_increment(
                "alexa_state_report_success",
                entity_domain=entity_id.split(".", 1)[0],
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            log_debug(
                f"[{correlation_id}] StateChangeReporter: Error",
                entity_id=entity_id,
                error_type=type(e).__name__,
                error_message=str(e),
                duration_ms=f"{duration_ms:.2f}",
            )

            metrics_increment(
                "alexa_state_report_error",
                entity_domain=entity_id.split(".", 1)[0],
                error_type=type(e).__name__,
            )

    def _build_alexa_properties(
        self,
        entity_id: str,
        old_state: dict[str, Any] | None,
        new_state: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Build Alexa properties from Home Assistant state.

        Args:
            entity_id: Entity ID
            old_state: Old state dictionary
            new_state: New state dictionary

        Returns:
            List of Alexa property dictionaries
        """
        properties: list[dict[str, Any]] = []
        domain = entity_id.split(".", 1)[0]
        new_attributes = new_state.get("attributes", {})
        new_state_value = new_state.get("state", "")
        old_attributes = old_state.get("attributes", {}) if old_state else {}
        old_state_value = old_state.get("state", "") if old_state else ""

        # Calculate time of sample (ISO 8601 format)
        last_updated = new_state.get("last_updated")
        if last_updated and isinstance(last_updated, (int, float)):
            dt_object = datetime.fromtimestamp(last_updated / 1000, UTC)
            time_of_sample = dt_object.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            time_of_sample = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        # PowerController property
        if new_state_value in ("on", "off", "unavailable"):
            if new_state_value != old_state_value:
                properties.append({
                    "namespace": "Alexa.PowerController",
                    "name": "powerState",
                    "value": "ON" if new_state_value == "on" else "OFF",
                    "timeOfSample": time_of_sample,
                    "uncertaintyInMilliseconds": 0,
                })

        # BrightnessController property
        if domain == "light" and "brightness" in new_attributes:
            new_brightness = new_attributes.get("brightness", 0)
            old_brightness = old_attributes.get("brightness", 0) if old_attributes else 0

            if isinstance(new_brightness, str):
                new_brightness = int(new_brightness)
            if isinstance(old_brightness, str):
                old_brightness = int(old_brightness)

            # Convert to 0-100 scale
            new_brightness_percent = int((new_brightness / 255) * 100) if new_brightness else 0
            old_brightness_percent = int((old_brightness / 255) * 100) if old_brightness else 0

            # Only report if changed by more than 5%
            if abs(new_brightness_percent - old_brightness_percent) > 5:
                properties.append({
                    "namespace": "Alexa.BrightnessController",
                    "name": "brightness",
                    "value": new_brightness_percent,
                    "timeOfSample": time_of_sample,
                    "uncertaintyInMilliseconds": 0,
                })

        # ThermostatController properties
        if domain == "climate":
            new_temp = new_attributes.get("current_temperature")
            old_temp = old_attributes.get("current_temperature") if old_attributes else None

            if new_temp is not None and new_temp != old_temp:
                # Check if change is significant (>0.5 degrees)
                if old_temp is None or abs(new_temp - old_temp) > 0.5:
                    properties.append({
                        "namespace": "Alexa.ThermostatController",
                        "name": "thermostatMode",
                        "value": self._map_thermostat_mode(new_state_value),
                        "timeOfSample": time_of_sample,
                        "uncertaintyInMilliseconds": 0,
                    })

                    properties.append({
                        "namespace": "Alexa.ThermostatController",
                        "name": "targetSetpoint",
                        "value": {
                            "value": new_temp,
                            "scale": "CELSIUS",
                        },
                        "timeOfSample": time_of_sample,
                        "uncertaintyInMilliseconds": 0,
                    })

        # PercentageController properties
        if domain in ("cover", "fan") and "percentage" in new_attributes:
            new_percentage = new_attributes.get("percentage", 0)
            old_percentage = old_attributes.get("percentage", 0) if old_attributes else 0

            if isinstance(new_percentage, str):
                new_percentage = int(new_percentage)
            if isinstance(old_percentage, str):
                old_percentage = int(old_percentage)

            # Only report if changed by more than 5%
            if abs(new_percentage - old_percentage) > 5:
                properties.append({
                    "namespace": "Alexa.PercentageController",
                    "name": "percentage",
                    "value": new_percentage,
                    "timeOfSample": time_of_sample,
                    "uncertaintyInMilliseconds": 0,
                })

        # LockController properties
        if domain == "lock":
            if new_state_value != old_state_value:
                properties.append({
                    "namespace": "Alexa.LockController",
                    "name": "lockState",
                    "value": "LOCKED" if new_state_value == "locked" else "UNLOCKED",
                    "timeOfSample": time_of_sample,
                    "uncertaintyInMilliseconds": 0,
                })

        return properties

    def _is_significant_change(
        self,
        entity_id: str,
        old_state: dict[str, Any] | None,
        new_state: dict[str, Any],
        properties: list[dict[str, Any]],
    ) -> bool:
        """Check if state change is significant.

        Args:
            entity_id: Entity ID
            old_state: Old state dictionary
            new_state: New state dictionary
            properties: List of Alexa properties

        Returns:
            True if change is significant
        """
        # If no properties built, not significant
        if not properties:
            return False

        # If old state is None (new entity), always significant
        if old_state is None:
            return True

        # Properties already filtered by threshold in _build_alexa_properties
        # So if we have properties here, the change is significant
        return True

    def _send_change_report(
        self,
        entity_id: str,
        properties: list[dict[str, Any]],
        correlation_id: str,
    ) -> None:
        """Send ChangeReport message to Alexa.

        Args:
            entity_id: Entity ID
            properties: List of Alexa properties
            correlation_id: Correlation ID for tracking

        Raises:
            RuntimeError: If reporter not enabled or configured
        """
        if not self._enabled or not self._alexa_endpoint or not self._access_token:
            raise RuntimeError("StateChangeReporter not enabled")

        # Build ChangeReport message
        message = {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ChangeReport",
                    "messageId": str(uuid.uuid4()),
                    "payloadVersion": "3",
                },
                "endpoint": {
                    "endpointId": entity_id.replace(".", "#"),
                    "scope": {
                        "type": "BearerToken",
                        "token": self._access_token,
                    }
                },
                "payload": {
                    "change": {
                        "cause": {
                            "type": "APP_INTERACTION",
                        },
                        "properties": properties,
                    },
                },
            },
            "context": {
                "properties": properties,
            },
        }

        # Send to Alexa Gateway API
        try:
            # Use LEE gateway HTTP client wrapper to send to Alexa Gateway
            response = http.post(
                url=self._alexa_endpoint,
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "Content-Type": "application/json",
                },
                json=message,
                timeout=10.0,
            )

            # Check response
            if response and response.get("status_code") != 200:
                raise RuntimeError(
                    f"Alexa Gateway returned error: "
                    f"{response.get('status_code')}"
                )

        except Exception as e:
            log_debug(
                f"[{correlation_id}] StateChangeReporter: HTTP request failed",
                entity_id=entity_id,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise

    def _map_thermostat_mode(self, ha_mode: str) -> str:
        """Map Home Assistant thermostat mode to Alexa mode.

        Args:
            ha_mode: Home Assistant thermostat mode

        Returns:
            Alexa thermostat mode
        """
        from lee.home_assistant.ha_thermostat_utils import (
            map_ha_to_alexa_thermostat_mode,
        )

        return map_ha_to_alexa_thermostat_mode(ha_mode)


# Global state change reporter instance
_state_change_reporter: StateChangeReporter | None = None
_reporter_lock = Lock()


def get_state_change_reporter() -> StateChangeReporter:
    """Get global state change reporter instance.

    Returns:
        StateChangeReporter instance (singleton)
    """
    global _state_change_reporter

    with _reporter_lock:
        if _state_change_reporter is None:
            _state_change_reporter = StateChangeReporter()

        return _state_change_reporter


__all__ = [
    "MessageCoalescer",
    "StateChangeReporter",
    "get_state_change_reporter",
]
