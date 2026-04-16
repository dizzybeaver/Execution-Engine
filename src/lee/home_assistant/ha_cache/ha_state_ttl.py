# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-12 - TTL calculation and management

"""Home Assistant state cache TTL management.

Provides domain-specific TTL configuration and intelligent TTL calculation
for different entity types, including battery sensor special handling.
"""

from typing import Any, Optional


# Domain-specific TTL configuration (in seconds)
HA_CACHE_TTL_CONFIG = {
    # Standard entities - 2 hours
    "light": 7200,
    "switch": 7200,
    "sensor": 7200,
    "binary_sensor": 3600,  # 1 hour for binary sensors

    # Climate/Security - 30 minutes
    "climate": 1800,
    "lock": 1800,
    "alarm_control_panel": 1800,

    # Media - 1 hour
    "media_player": 3600,

    # Covers/doors - 30 minutes
    "cover": 1800,

    # Battery sensors - special handling
    "battery": 7200,  # Base TTL, extended when offline
}


def calculate_entity_ttl(state: dict[str, Any]) -> int:
    """Calculate appropriate TTL for entity state.

    Factors:
    1. Domain-specific base TTL
    2. Battery-powered detection
    3. Device state (offline extension)
    4. User-defined overrides

    Args:
        state: Entity state dict from Home Assistant

    Returns:
        TTL in seconds
    """
    entity_id = state.get("entity_id", "")
    domain = entity_id.split(".", 1)[0] if "." in entity_id else "unknown"
    attributes = state.get("attributes", {})

    # Get base TTL for domain
    base_ttl = HA_CACHE_TTL_CONFIG.get(domain, 7200)  # Default 2 hours

    # Battery sensor special handling
    if is_battery_sensor(state):
        # Check if device is offline
        device_class = attributes.get("device_class", "")
        state_value = state.get("state", "unknown")

        if device_class == "battery" and state_value in ["unknown", "unavailable", "none"]:
            # Battery sensors get extended TTL when offline
            return 7200
        else:
            # Online battery sensor - standard TTL
            return base_ttl

    # Check for battery-powered device
    if is_battery_powered_device(attributes):
        # Extend TTL for battery-powered devices (max 2 hours)
        return min(base_ttl * 2, 7200)

    return base_ttl


def is_battery_sensor(state: dict[str, Any]) -> bool:
    """Detect if state is a battery sensor.

    Args:
        state: Entity state dict

    Returns:
        True if this is a battery sensor
    """
    entity_id = state.get("entity_id", "")
    attributes = state.get("attributes", {})

    # Check entity_id pattern
    if "_battery" in entity_id or "battery_" in entity_id:
        return True

    # Check device class
    if attributes.get("device_class") == "battery":
        return True

    # Check unit of measurement
    if attributes.get("unit_of_measurement") in ["%", "V"]:
        return True

    return False


def is_battery_powered_device(attributes: dict[str, Any]) -> bool:
    """Detect if device is battery-powered.

    Args:
        attributes: Entity attributes dict

    Returns:
        True if device is battery-powered
    """
    # Check power_source attribute
    if attributes.get("power_source") == "battery":
        return True

    # Check for battery entity in device
    if attributes.get("device_class") == "battery":
        return True

    return False


def is_entry_expired(cached_entry: Any) -> bool:
    """Check if cache entry is expired.

    Args:
        cached_entry: Cache entry object

    Returns:
        True if entry is expired
    """
    if not cached_entry:
        return True

    import time
    current_time = time.time()

    # Check if entry has timestamp and ttl
    if not hasattr(cached_entry, 'timestamp') or not hasattr(cached_entry, 'ttl'):
        return True

    age = current_time - cached_entry.timestamp
    return age > cached_entry.ttl
