# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Add alexa.yaml filter support


"""ha_discovery_entities.py - Home Assistant Discovery Entity Operations

Implements device discovery operations for Home Assistant integration:
- Entity enumeration from Home Assistant
- Entity filtering based on alexa.yaml configuration
- Entity to Alexa endpoint mapping
- Discovery response construction
- Bitwise capability detection for advanced features
- Incremental discovery with device change tracking

Reference: e:/LEE/docs/ha/02_device_discovery.md
Reference: e:/LEE/docs/ha/05_discovery_implementation.md
Reference: e:/LEE/docs/Alexa/Device_Discovery_Guide.md

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import hashlib
import json
from dataclasses import dataclass
from enum import Flag, auto
from functools import partial
from pathlib import Path
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


class ClimateEntityFeatures:
    """ClimateEntityFeature constants for Home Assistant climate entities.

    Reference: homeassistant/components/climate/const.py
    """
    TURN_ON_OFF = 1


class ClimateCapabilities(Flag):
    """Climate device capability flags for bitwise detection.

    Uses Python Flag enum for efficient bitwise capability detection.
    Supports multiple capabilities per device using bitwise operations.
    """

    BASIC = auto()  # Basic temperature control
    TURN_ON_OFF = auto()  # Power on/off support
    TARGET_TEMPERATURE = auto()  # Target temperature setting
    CURRENT_TEMPERATURE = auto()  # Current temperature reporting
    MODES = auto()  # Operating mode support (heat/cool/auto/etc)
    FAN_MODES = auto()  # Fan mode support
    SWING_MODES = auto()  # Swing mode support
    HUMIDITY = auto()  # Humidity control
    SETPOINT_SUPPORT = auto()  # Separate heating/cooling setpoints


@dataclass
class DeviceChange:
    """Represents a device change for incremental discovery."""

    entity_id: str
    change_type: str  # "added", "modified", "removed"
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None


class DeviceChangeTracker:
    """Track device changes for incremental discovery.

    Maintains previous device state using hash comparison to detect
    changes efficiently. Supports persistence via gateway cache.

    Example:
        >>> tracker = DeviceChangeTracker()
        >>> # Get changes since last discovery
        >>> changes = tracker.get_device_changes(current_devices)
        >>> # Update stored state
        >>> tracker.update_device_state(current_devices)
    """

    CACHE_KEY_PREFIX = "ha_discovery_device_state"
    CACHE_TTL = 86400  # 24 hours

    def __init__(self):
        """Initialize device change tracker."""
        self._current_state: dict[str, str] = {}

    def _compute_device_hash(self, device: dict[str, Any]) -> str:
        """Compute hash of device state for change detection.

        Args:
            device: Device state dict

        Returns:
            SHA256 hash of normalized device state
        """
        # Normalize device state for consistent hashing
        normalized = {
            "entity_id": device.get("entity_id"),
            "state": device.get("state"),
            "attributes": device.get("attributes", {}),
            "last_changed": device.get("last_changed"),
            "last_updated": device.get("last_updated"),
        }

        # Convert to JSON and compute hash
        device_json = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(device_json.encode()).hexdigest()

    def _load_previous_state(self) -> dict[str, str]:
        """Load previous device state from cache.

        Returns:
            Dict mapping entity_id to device hash
        """
        try:
            cached = execute_operation(
                GatewayInterface.CACHE,
                "get",
                key=self.CACHE_KEY_PREFIX,
            )
            if cached and isinstance(cached, dict):
                return cached
            return {}
        except (ConnectionError, TimeoutError, ValueError, TypeError, KeyError):
            return {}

    def _save_current_state(self, state: dict[str, str]) -> None:
        """Save current device state to cache.

        Args:
            state: Dict mapping entity_id to device hash
        """
        try:
            execute_operation(
                GatewayInterface.CACHE,
                "set",
                key=self.CACHE_KEY_PREFIX,
                value=state,
                ttl=self.CACHE_TTL,
            )
        except (ConnectionError, TimeoutError, ValueError, TypeError, KeyError):
            pass  # Cache save failure is not critical

    def get_device_changes(
        self,
        current_devices: list[dict[str, Any]],
        correlation_id: Optional[str] = None,
    ) -> list[DeviceChange]:
        """Detect device changes since last discovery.

        Args:
            current_devices: List of current device states
            correlation_id: Optional correlation ID for logging

        Returns:
            List of DeviceChange objects
        """
        corr_id = correlation_id or execute_operation(
            GatewayInterface.DEBUG, "generate_correlation_id", scope="discovery"
        )

        execute_operation(
            GatewayInterface.LOGGING, "log_info",
            message="Detecting device changes for incremental discovery",
            corr_id=corr_id
        )

        # Load previous state from cache
        previous_state = self._load_previous_state()
        changes = []

        # Compute current device hashes
        current_state = {}
        for device in current_devices:
            entity_id = device.get("entity_id")
            if not entity_id:
                continue

            device_hash = self._compute_device_hash(device)
            current_state[entity_id] = device_hash

            # Check for added or modified devices
            if entity_id not in previous_state:
                changes.append(DeviceChange(
                    entity_id=entity_id,
                    change_type="added",
                    new_hash=device_hash
                ))
                execute_operation(
                    GatewayInterface.LOGGING, "log_debug",
                    message=f"Device added: {entity_id}",
                    corr_id=corr_id
                )
            elif previous_state[entity_id] != device_hash:
                changes.append(DeviceChange(
                    entity_id=entity_id,
                    change_type="modified",
                    old_hash=previous_state[entity_id],
                    new_hash=device_hash
                ))
                execute_operation(
                    GatewayInterface.LOGGING, "log_debug",
                    message=f"Device modified: {entity_id}",
                    corr_id=corr_id
                )

        # Check for removed devices
        for entity_id in previous_state:
            if entity_id not in current_state:
                changes.append(DeviceChange(
                    entity_id=entity_id,
                    change_type="removed",
                    old_hash=previous_state[entity_id]
                ))
                execute_operation(
                    GatewayInterface.LOGGING, "log_debug",
                    message=f"Device removed: {entity_id}",
                    corr_id=corr_id
                )

        execute_operation(
            GatewayInterface.LOGGING, "log_info",
            message=f"Detected {len(changes)} device changes",
            corr_id=corr_id,
            change_count=len(changes)
        )

        return changes

    def update_device_state(
        self,
        devices: list[dict[str, Any]],
        correlation_id: Optional[str] = None,
    ) -> None:
        """Update stored device state after discovery.

        Args:
            devices: List of current device states
            correlation_id: Optional correlation ID for logging
        """
        corr_id = correlation_id or execute_operation(
            GatewayInterface.DEBUG, "generate_correlation_id", scope="discovery"
        )

        # Compute current device hashes
        current_state = {}
        for device in devices:
            entity_id = device.get("entity_id")
            if not entity_id:
                continue

            current_state[entity_id] = self._compute_device_hash(device)

        # Save to cache
        self._save_current_state(current_state)

        execute_operation(
            GatewayInterface.LOGGING, "log_info",
            message=f"Updated device state for {len(current_state)} devices",
            corr_id=corr_id,
            device_count=len(current_state)
        )


def detect_climate_capabilities(
    entity_attributes: dict[str, Any],
    correlation_id: Optional[str] = None
) -> ClimateCapabilities:
    """Detect climate device capabilities using bitwise feature detection.

    Analyzes entity attributes to determine supported capabilities using
    bitwise flags for efficient combination and testing.

    Args:
        entity_attributes: Home Assistant entity attributes dict
        correlation_id: Optional correlation ID for logging

    Returns:
        ClimateCapabilities flags indicating supported features
    """
    corr_id = correlation_id or execute_operation(
        GatewayInterface.DEBUG, "generate_correlation_id", scope="discovery"
    )

    capabilities = ClimateCapabilities.BASIC

    # Check for power on/off support
    supported_features = entity_attributes.get("supported_features", 0)
    if supported_features & ClimateEntityFeatures.TURN_ON_OFF:
        capabilities |= ClimateCapabilities.TURN_ON_OFF
        execute_operation(
            GatewayInterface.LOGGING, "log_debug",
            message="Climate device supports TURN_ON_OFF",
            corr_id=corr_id
        )

    # Check for target temperature support
    if entity_attributes.get("temperature") is not None:
        capabilities |= ClimateCapabilities.TARGET_TEMPERATURE

    # Check for current temperature reporting
    if entity_attributes.get("current_temperature") is not None:
        capabilities |= ClimateCapabilities.CURRENT_TEMPERATURE

    # Check for mode support
    if entity_attributes.get("hvac_modes") not in [None, []]:
        capabilities |= ClimateCapabilities.MODES

    # Check for fan mode support
    if entity_attributes.get("fan_modes") not in [None, []]:
        capabilities |= ClimateCapabilities.FAN_MODES

    # Check for swing mode support
    if entity_attributes.get("swing_modes") not in [None, []]:
        capabilities |= ClimateCapabilities.SWING_MODES

    # Check for humidity support
    if entity_attributes.get("current_humidity") is not None:
        capabilities |= ClimateCapabilities.HUMIDITY

    # Check for separate setpoint support
    if entity_attributes.get("target_temp_low") is not None or \
       entity_attributes.get("target_temp_high") is not None:
        capabilities |= ClimateCapabilities.SETPOINT_SUPPORT

    execute_operation(
        GatewayInterface.LOGGING, "log_debug",
        message=f"Climate capabilities detected: {capabilities}",
        corr_id=corr_id,
        capabilities=capabilities
    )

    return capabilities


def enumerate_home_assistant_entities(
    correlation_id: Optional[str] = None
) -> dict[str, Any]:
    """Enumerate all Home Assistant entities via /api/states endpoint.

    Args:
        correlation_id: Optional correlation ID for tracking

    Returns:
        Dict with success status and entities list
        {
            "success": True/False,
            "entities": [...],  # List of entity state dicts
            "error": str  # Only present if success=False
        }
    """
    corr_id = correlation_id or execute_operation(
        GatewayInterface.DEBUG, "generate_correlation_id", scope="ha"
    )

    execute_operation(
        GatewayInterface.LOGGING, "log_info",
        message="Enumerating Home Assistant entities",
        corr_id=corr_id
    )

    try:
        # Call Home Assistant /api/states endpoint
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES, "get_states",
            correlation_id=corr_id
        )

        if result.get("success") is False:
            execute_operation(
                GatewayInterface.LOGGING, "log_error",
                message="Failed to enumerate entities",
                corr_id=corr_id,
                error=result.get("error")
            )
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "error_code": "ENTITY_ENUMERATION_FAILED"
            }

        entities = result.get("states", [])
        execute_operation(
            GatewayInterface.LOGGING, "log_info",
            message=f"Enumerated {len(entities)} entities",
            corr_id=corr_id,
            entity_count=len(entities)
        )

        # Warm cache with discovered entity states
        try:
            from lee.home_assistant.ha_cache.ha_cache_warmer import warm_entity_states_cache

            entity_ids = [entity.get("entity_id") for entity in entities if entity.get("entity_id")]

            if entity_ids:
                warm_result = warm_entity_states_cache(
                    entity_ids=entity_ids,
                    oauth_token=None,  # Uses default token
                    corr_id=corr_id
                )

                if warm_result.get("success"):
                    execute_operation(
                        GatewayInterface.LOGGING, "log_info",
                        message=f"Warmed cache for {warm_result.get('warmed_count', 0)}/{len(entity_ids)} entities",
                        corr_id=corr_id
                    )

        except (ImportError, AttributeError) as cache_error:
            # Cache warming not available - non-fatal
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=corr_id, scope="HOME_ASSISTANT",
                message="Entity enumeration cache warming unavailable",
                error=str(cache_error)
            )

        return {
            "success": True,
            "entities": entities,
            "entity_count": len(entities)
        }

    except Exception as e:
        execute_operation(
            GatewayInterface.LOGGING, "log_error",
            message="Entity enumeration failed with exception",
            corr_id=corr_id,
            error=str(e)
        )
        return {
            "success": False,
            "error": f"Entity enumeration failed: {str(e)}",
            "error_code": "ENTITY_ENUMERATION_EXCEPTION"
        }


def load_alexa_config() -> dict[str, Any]:
    """Load alexa.yaml configuration file.

    DEPRECATED: This function is used by legacy discovery mode.
    Use proxy mode (USE_HA_ALEXA_ENDPOINT=true) with Home Assistant's
    native alexa.yaml configuration instead.

    Returns:
        Dict with configuration:
        {
            "include_entities": [str],  # Entities to explicitly include
            "exclude_domains": [str],   # Domains to exclude
        }
    """
    config = {
        "include_entities": [],
        "exclude_domains": []
    }

    try:
        # Try multiple possible locations for alexa.yaml
        possible_paths = [
            Path("/var/task/alexa.yaml"),  # Lambda deployment
            Path("E:/LEE/alexa.yaml"),     # Local development
            Path("alexa.yaml"),             # Current directory
        ]

        alexa_yaml_path = None
        for path in possible_paths:
            if path.exists():
                alexa_yaml_path = path
                break

        if alexa_yaml_path is None:
            execute_operation(
                GatewayInterface.LOGGING, "log_debug",
                message="alexa.yaml not found, using no-filter defaults",
                scope="discovery"
            )
            return config

        # Simple YAML parser for alexa.yaml structure
        include_entities = []
        exclude_domains = []
        in_filter = False
        in_include = False
        in_exclude = False

        with open(alexa_yaml_path, "r") as f:
            for line in f:
                stripped = line.strip()

                # Skip comments and empty lines
                if not stripped or stripped.startswith("#"):
                    continue

                # Track section depth
                if stripped.startswith("filter:"):
                    in_filter = True
                    in_include = False
                    in_exclude = False
                elif stripped.startswith("include_entities:"):
                    in_include = True
                    in_exclude = False
                elif stripped.startswith("exclude_domains:"):
                    in_exclude = True
                    in_include = False
                # Parse list items
                elif stripped.startswith("- ") and in_filter:
                    item = stripped[2:].strip().strip("'\"")
                    if in_include:
                        include_entities.append(item)
                    elif in_exclude:
                        exclude_domains.append(item)

        config["include_entities"] = include_entities
        config["exclude_domains"] = exclude_domains

        execute_operation(
            GatewayInterface.LOGGING, "log_info",
            message=f"Loaded alexa.yaml config from {alexa_yaml_path}",
            scope="discovery",
            include_count=len(config["include_entities"]),
            exclude_count=len(config["exclude_domains"])
        )

        return config

    except (IOError, OSError) as e:
        execute_operation(
            GatewayInterface.LOGGING, "log_warning",
            message=f"Failed to load alexa.yaml: {str(e)}",
            scope="discovery",
            error=str(e)
        )
        return config


def filter_entities(
    entities: list[dict[str, Any]],
    correlation_id: Optional[str] = None
) -> dict[str, Any]:
    """Filter entities based on Alexa-compatible domains and alexa.yaml configuration.

    DEPRECATED: This function is used by legacy discovery mode.
    Use proxy mode (USE_HA_ALEXA_ENDPOINT=true) to let Home Assistant
    handle filtering instead.

    Args:
        entities: List of entity state dicts from Home Assistant
        correlation_id: Optional correlation ID for tracking

    Returns:
        Dict with success status and filtered entities list
        {
            "success": True/False,
            "entities": [...],  # Filtered list of entity state dicts
            "filtered_count": int  # Number of entities filtered out
        }
    """
    corr_id = correlation_id or execute_operation(
        GatewayInterface.DEBUG, "generate_correlation_id", scope="ha"
    )

    # Load alexa.yaml configuration
    alexa_config = load_alexa_config()
    include_entities = set(alexa_config.get("include_entities", []))
    exclude_domains = set(alexa_config.get("exclude_domains", []))

    # Check if using explicit include list (filter mode)
    use_include_filter = len(include_entities) > 0

    # Alexa-compatible domains (based on HA Alexa integration support)
    alexa_compatible_domains = {
        "light", "switch", "fan", "cover", "lock",
        "climate", "humidifier", "media_player", "vacuum",
        "scene", "script", "automation", "group",
        "input_boolean", "button", "input_button",
        "sensor", "binary_sensor",
        "alarm_control_panel", "camera",
        "remote", "timer", "input_number", "number"
    }

    execute_operation(
        GatewayInterface.LOGGING, "log_info",
        message=(
            f"Filtering {len(entities)} entities "
            f"(include_filter={use_include_filter}, "
            f"exclude_domains={len(exclude_domains)})"
        ),
        corr_id=corr_id,
        use_include_filter=use_include_filter,
        exclude_domains_count=len(exclude_domains)
    )

    try:
        filtered_entities = []
        for entity in entities:
            entity_id = entity.get("entity_id", "")

            # Extract domain from entity_id (e.g., "light.bubs_bedroom_inside_light_switch_1" -> "light")
            if "." not in entity_id:
                continue

            domain = entity_id.split(".", 1)[0]

            # Filter 1: If include_entities is specified, only include those entities
            # This takes priority over exclude_domains
            if use_include_filter:
                if entity_id not in include_entities:
                    continue
            else:
                # Filter 2: Exclude domains from alexa.yaml
                # (only if not using include filter)
                if domain in exclude_domains:
                    continue

            # Filter 3: Check if domain is Alexa-compatible
            if domain not in alexa_compatible_domains:
                continue

            # Filter 4: Filter out entities with entity_category (config/diagnostic)
            entity_category = entity.get("attributes", {}).get("entity_category")
            if entity_category is not None:
                continue

            # Filter 5: Filter out hidden entities
            hidden_by = entity.get("attributes", {}).get("hidden_by")
            if hidden_by is not None:
                continue

            filtered_entities.append(entity)

        filtered_count = len(entities) - len(filtered_entities)

        execute_operation(
            GatewayInterface.LOGGING, "log_info",
            message=f"Filtered to {len(filtered_entities)} entities "
                   f"({filtered_count} excluded)",
            corr_id=corr_id,
            compatible_count=len(filtered_entities),
            excluded_count=filtered_count
        )

        return {
            "success": True,
            "entities": filtered_entities,
            "filtered_count": filtered_count,
            "compatible_count": len(filtered_entities)
        }

    except Exception as e:
        execute_operation(
            GatewayInterface.LOGGING, "log_error",
            message="Entity filtering failed with exception",
            corr_id=corr_id,
            error=str(e)
        )
        return {
            "success": False,
            "error": f"Entity filtering failed: {str(e)}",
            "error_code": "ENTITY_FILTERING_EXCEPTION"
        }


def map_entity_to_alexa_endpoint(
    entity: dict[str, Any],
    correlation_id: Optional[str] = None
) -> dict[str, Any]:
    """Map a Home Assistant entity to Alexa endpoint format.

    Args:
        entity: Entity state dict from Home Assistant
        correlation_id: Optional correlation ID for tracking

    Returns:
        Alexa endpoint dict with proper structure
        {
            "endpointId": str,
            "friendlyName": str,
            "description": str,
            "manufacturerName": str,
            "displayCategories": [str],
            "additionalAttributes": dict,
            "cookie": dict,
            "capabilities": [dict]
        }
    """
    corr_id = correlation_id or execute_operation(
        GatewayInterface.DEBUG, "generate_correlation_id", scope="ha"
    )

    try:
        entity_id = entity.get("entity_id", "")
        domain = entity_id.split(".", 1)[0] if "." in entity_id else "unknown"

        # Generate endpoint ID (replace . with #)
        endpoint_id = entity_id.replace(".", "#")

        # Get friendly name
        friendly_name = entity.get("attributes", {}).get("friendly_name", entity_id)

        # Get display category based on domain
        display_category = _get_display_category(domain, entity)

        # Get capabilities based on domain and entity attributes
        capabilities = _get_entity_capabilities(domain, entity, correlation_id=corr_id)

        # Build endpoint object
        endpoint = {
            "endpointId": endpoint_id,
            "friendlyName": friendly_name,
            "description": f"{entity_id} via Home Assistant",
            "manufacturerName": "Home Assistant",
            "displayCategories": [display_category],
            "additionalAttributes": {
                "manufacturer": "Home Assistant",
                "model": domain,
                "softwareVersion": "2026.04.09",
                "customIdentifier": f"lee-{entity_id}"
            },
            "cookie": {
                "entity_id": entity_id
            },
            "capabilities": capabilities
        }

        return endpoint

    except Exception as e:
        execute_operation(
            GatewayInterface.LOGGING, "log_warning",
            message=f"Failed to map entity {entity.get('entity_id', 'unknown')} "
                   f"to endpoint",
            corr_id=corr_id,
            error=str(e)
        )
        # Return minimal endpoint structure on error
        entity_id = entity.get("entity_id", "unknown")
        friendly_name = entity.get("attributes", {}).get(
            "friendly_name", "Unknown"
        )
        return {
            "endpointId": entity_id.replace(".", "#"),
            "friendlyName": friendly_name,
            "description": "Error mapping entity",
            "manufacturerName": "Home Assistant",
            "displayCategories": ["OTHER"],
            "capabilities": []
        }


def _get_display_category(domain: str, entity: dict[str, Any]) -> str:
    """Get Alexa display category for entity domain.

    Args:
        domain: Entity domain (e.g., "light", "switch")
        entity: Entity state dict for additional context

    Returns:
        Alexa display category string
    """
    # Display category mapping (based on HA Alexa integration)
    category_map = {
        "light": "LIGHT",
        "switch": "SWITCH",
        "fan": "FAN",
        "cover": "OTHER",  # Could be DOOR, GARAGE_DOOR, WINDOW based on device_class
        "lock": "SMARTLOCK",
        "climate": "THERMOSTAT",
        "humidifier": "OTHER",
        "media_player": "TV",  # or SPEAKER based on device_class
        "vacuum": "VACUUM_CLEANER",
        "scene": "SCENE_TRIGGER",
        "script": "ACTIVITY_TRIGGER",
        "automation": "ACTIVITY_TRIGGER",
        "group": "OTHER",
        "input_boolean": "OTHER",
        "button": "ACTIVITY_TRIGGER",
        "input_button": "ACTIVITY_TRIGGER",
        "sensor": "TEMPERATURE_SENSOR",  # Could vary based on device_class
        "binary_sensor": "CONTACT_SENSOR",  # Could be MOTION_SENSOR, DOORBELL, etc.
        "alarm_control_panel": "SECURITY_PANEL",
        "camera": "CAMERA",
        "remote": "REMOTE",
        "timer": "OTHER",
        "input_number": "OTHER",
        "number": "OTHER"
    }

    return category_map.get(domain, "OTHER")


# Common capability definitions (shared across builders)
_PROPERTIES_POWER_STATE = {
    "supported": [{"name": "powerState"}],
    "proactivelyReported": True,
    "retrievable": True
}

_PROPERTIES_LOCK_STATE = {
    "supported": [{"name": "lockState"}],
    "proactivelyReported": True,
    "retrievable": True
}

_PROPERTIES_TEMPERATURE = {
    "supported": [{"name": "temperature"}],
    "proactivelyReported": True,
    "retrievable": True
}

_PROPERTIES_HUMIDITY = {
    "supported": [{"name": "relativeHumidity"}],
    "proactivelyReported": True,
    "retrievable": True
}

_PROPERTIES_THERMOSTAT = {
    "supported": [
        {"name": "targetSetpoint"},
        {"name": "thermostatMode"}
    ],
    "proactivelyReported": True,
    "retrievable": True
}

_PROPERTIES_THERMOSTAT_DUAL = {
    "supported": [
        {"name": "lowerSetpoint"},
        {"name": "upperSetpoint"},
        {"name": "thermostatMode"}
    ],
    "proactivelyReported": True,
    "retrievable": True
}

_PROPERTIES_SECURITY_PANEL = {
    "supported": [
        {"name": "armState"},
        {"name": "burglaryAlarm"},
        {"name": "fireAlarm"},
        {"name": "carbonMonoxideAlarm"},
        {"name": "waterAlarm"}
    ],
    "proactivelyReported": True,
    "retrievable": True
}

_PROPERTIES_BRIGHTNESS = {
    "supported": [{"name": "brightness"}],
    "proactivelyReported": True,
    "retrievable": True
}

_PROPERTIES_COLOR = {
    "supported": [{"name": "color"}],
    "proactivelyReported": True,
    "retrievable": True
}

_PROPERTIES_COLOR_TEMP = {
    "supported": [{"name": "colorTemperatureInKelvin"}],
    "proactivelyReported": True,
    "retrievable": True
}

_POWER_CONTROLLER = {
    "type": "AlexaInterface",
    "interface": "Alexa.PowerController",
    "version": "3",
    "properties": _PROPERTIES_POWER_STATE
}

_LOCK_CONTROLLER = {
    "type": "AlexaInterface",
    "interface": "Alexa.LockController",
    "version": "3",
    "properties": _PROPERTIES_LOCK_STATE
}

_BRIGHTNESS_CONTROLLER = {
    "type": "AlexaInterface",
    "interface": "Alexa.BrightnessController",
    "version": "3",
    "properties": _PROPERTIES_BRIGHTNESS
}

_COLOR_CONTROLLER = {
    "type": "AlexaInterface",
    "interface": "Alexa.ColorController",
    "version": "3",
    "properties": _PROPERTIES_COLOR
}

_COLOR_TEMPERATURE_CONTROLLER = {
    "type": "AlexaInterface",
    "interface": "Alexa.ColorTemperatureController",
    "version": "3",
    "properties": _PROPERTIES_COLOR_TEMP
}

_TEMPERATURE_SENSOR = {
    "type": "AlexaInterface",
    "interface": "Alexa.TemperatureSensor",
    "version": "3",
    "properties": _PROPERTIES_TEMPERATURE
}

_HUMIDITY_SENSOR = {
    "type": "AlexaInterface",
    "interface": "Alexa.HumiditySensor",
    "version": "3",
    "properties": _PROPERTIES_HUMIDITY
}

_THERMOSTAT_CONTROLLER = {
    "type": "AlexaInterface",
    "interface": "Alexa.ThermostatController",
    "version": "3",
    "properties": _PROPERTIES_THERMOSTAT
}

_THERMOSTAT_CONTROLLER_DUAL = {
    "type": "AlexaInterface",
    "interface": "Alexa.ThermostatController",
    "version": "3",
    "properties": _PROPERTIES_THERMOSTAT_DUAL
}

_SECURITY_PANEL_CONTROLLER = {
    "type": "AlexaInterface",
    "interface": "Alexa.SecurityPanelController",
    "version": "3",
    "properties": _PROPERTIES_SECURITY_PANEL
}

_ALEXA_INTERFACE = {
    "type": "AlexaInterface",
    "interface": "Alexa",
    "version": "3"
}

_ENDPOINT_HEALTH = {
    "type": "AlexaInterface",
    "interface": "Alexa.EndpointHealth",
    "version": "3",
    "properties": {
        "supported": [{"name": "connectivity"}],
        "proactivelyReported": True,
        "retrievable": True
    }
}


def _build_light_capabilities(entity: dict[str, Any]) -> list[dict[str, Any]]:
    """Build capabilities for light domain.

    Args:
        entity: Entity state dict

    Returns:
        List of Alexa capability dicts
    """
    capabilities = [_POWER_CONTROLLER]
    attrs = entity.get("attributes", {})
    supported_color_modes = attrs.get("supported_color_modes", [])

    if supported_color_modes and any(
        "brightness" in mode for mode in supported_color_modes
    ):
        capabilities.append(_BRIGHTNESS_CONTROLLER)

    if "hs" in supported_color_modes or "xy" in supported_color_modes:
        capabilities.append(_COLOR_CONTROLLER)

    if "color_temp" in supported_color_modes:
        capabilities.append(_COLOR_TEMPERATURE_CONTROLLER)

    return capabilities


def _build_switch_capabilities(entity: dict[str, Any]) -> list[dict[str, Any]]:
    """Build capabilities for switch domain.

    Args:
        entity: Entity state dict

    Returns:
        List of Alexa capability dicts
    """
    return [_POWER_CONTROLLER]


def _build_fan_capabilities(entity: dict[str, Any]) -> list[dict[str, Any]]:
    """Build capabilities for fan domain.

    Args:
        entity: Entity state dict

    Returns:
        List of Alexa capability dicts
    """
    return [_POWER_CONTROLLER]


def _build_cover_capabilities(entity: dict[str, Any]) -> list[dict[str, Any]]:
    """Build capabilities for cover domain.

    Args:
        entity: Entity state dict

    Returns:
        List of Alexa capability dicts
    """
    return [_POWER_CONTROLLER]


def _build_lock_capabilities(entity: dict[str, Any]) -> list[dict[str, Any]]:
    """Build capabilities for lock domain.

    Args:
        entity: Entity state dict

    Returns:
        List of Alexa capability dicts
    """
    return [_LOCK_CONTROLLER]


def _build_climate_capabilities(entity: dict[str, Any]) -> list[dict[str, Any]]:
    """Build capabilities for climate domain.

    Args:
        entity: Entity state dict

    Returns:
        List of Alexa capability dicts

    Note:
        Per Amazon's Alexa documentation, climate devices can have both
        ThermostatController and TemperatureSensor interfaces when they
        display temperature. ThermostatController handles control operations
        while TemperatureSensor reports the current ambient temperature.

        Per Amazon's official Alexa ThermostatController documentation:
        https://developer.amazon.com/docs/device-apis/alexa-thermostatcontroller.html

        Per Amazon's official Alexa TemperatureSensor documentation:
        https://developer.amazon.com/docs/device-apis/alexa-temperaturesensor.html
    """
    attributes = entity.get("attributes", {})
    capabilities = []

    # Determine thermostat type based on supported features
    supports_dual = (
        "target_temp_low" in attributes and
        "target_temp_high" in attributes
    )

    # Add appropriate thermostat controller
    if supports_dual:
        capabilities.append(_THERMOSTAT_CONTROLLER_DUAL)
    else:
        capabilities.append(_THERMOSTAT_CONTROLLER)

    # Add TemperatureSensor if climate device reports current temperature
    # This is REQUIRED for air conditioners and thermostats that display temp
    if "current_temperature" in attributes:
        capabilities.append(_TEMPERATURE_SENSOR)

    return capabilities


def _build_scene_capabilities(
    entity: dict[str, Any],
    domain: str
) -> list[dict[str, Any]]:
    """Build capabilities for scene-like domains.

    Args:
        entity: Entity state dict
        domain: Entity domain

    Returns:
        List of Alexa capability dicts
    """
    return [{
        "type": "AlexaInterface",
        "interface": "Alexa.SceneController",
        "version": "3",
        "supportsDeactivation": domain in ("group", "input_boolean"),
        "proactivelyReported": False
    }]


def _build_sensor_capabilities(
    entity: dict[str, Any],
    domain: str
) -> list[dict[str, Any]]:
    """Build capabilities for sensor domains.

    Args:
        entity: Entity state dict
        domain: Entity domain

    Returns:
        List of Alexa capability dicts
    """
    attributes = entity.get("attributes", {})
    device_class = attributes.get("device_class")

    if domain == "sensor":
        if device_class == "temperature":
            return [_TEMPERATURE_SENSOR]
        elif device_class == "humidity":
            return [_HUMIDITY_SENSOR]

    return []


def _build_alarm_control_panel_capabilities(
    entity: dict[str, Any]
) -> list[dict[str, Any]]:
    """Build capabilities for alarm_control_panel domain.

    Args:
        entity: Entity state dict

    Returns:
        List of Alexa capability dicts
    """
    return [_SECURITY_PANEL_CONTROLLER]


# Domain capability builder mapping
DOMAIN_BUILDERS: dict[str, callable] = {
    "light": _build_light_capabilities,
    "switch": _build_switch_capabilities,
    "fan": _build_fan_capabilities,
    "cover": _build_cover_capabilities,
    "lock": _build_lock_capabilities,
    "climate": _build_climate_capabilities,
    "scene": partial(_build_scene_capabilities, domain="scene"),
    "script": partial(_build_scene_capabilities, domain="script"),
    "automation": partial(_build_scene_capabilities, domain="automation"),
    "group": partial(_build_scene_capabilities, domain="group"),
    "input_boolean": partial(_build_scene_capabilities, domain="input_boolean"),
    "button": partial(_build_scene_capabilities, domain="button"),
    "input_button": partial(_build_scene_capabilities, domain="input_button"),
    "sensor": partial(_build_sensor_capabilities, domain="sensor"),
    "binary_sensor": partial(_build_sensor_capabilities, domain="binary_sensor"),
    "alarm_control_panel": _build_alarm_control_panel_capabilities,
}


def _get_entity_capabilities(
    domain: str,
    entity: dict[str, Any],
    correlation_id: Optional[str] = None
) -> list[dict[str, Any]]:
    """Get Alexa capabilities for an entity based on domain and attributes.

    Args:
        domain: Entity domain
        entity: Entity state dict
        correlation_id: Optional correlation ID for tracking

    Returns:
        List of Alexa capability dicts
    """
    capabilities = [_ALEXA_INTERFACE, _ENDPOINT_HEALTH]

    builder = DOMAIN_BUILDERS.get(domain)
    if builder:
        capabilities.extend(builder(entity))

    return capabilities


def build_discovery_response(
    endpoints: list[dict[str, Any]],
    correlation_id: Optional[str] = None,
    directive: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Build Alexa.Discovery Discover.Response from endpoint list.

    Args:
        endpoints: List of Alexa endpoint dicts
        correlation_id: Optional correlation ID for tracking
        directive: Optional original directive to extract correlationToken

    Returns:
        Alexa discovery response dict
    """
    corr_id = correlation_id or execute_operation(
        GatewayInterface.DEBUG, "generate_correlation_id", scope="ha"
    )

    execute_operation(
        GatewayInterface.LOGGING, "log_info",
        message=f"Building discovery response with {len(endpoints)} endpoints",
        corr_id=corr_id,
        endpoint_count=len(endpoints)
    )

    # Extract correlationToken from directive if available
    correlation_token = ""
    if directive:
        header = directive.get("header", {})
        correlation_token = header.get("correlationToken", "")

    response_header = {
        "namespace": "Alexa.Discovery",
        "name": "Discover.Response",
        "payloadVersion": "3",
        "messageId": corr_id
    }

    # Add correlationToken if present in request (required by Alexa)
    if correlation_token:
        response_header["correlationToken"] = correlation_token

    return {
        "event": {
            "header": response_header,
            "payload": {
                "endpoints": endpoints
            }
        }
    }


__all__ = [
    "enumerate_home_assistant_entities",
    "filter_entities",
    "map_entity_to_alexa_endpoint",
    "build_discovery_response",
]
