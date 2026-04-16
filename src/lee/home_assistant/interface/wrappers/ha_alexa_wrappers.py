"""ha_alexa_wrappers.py
Version: 2025-12-22_3
Purpose: Alexa interface internal wrappers (SUGA-ISP Implementation)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the Alexa router.
External modules MUST use ha_alexa.execute_alexa_operation() instead of importing directly.
"""

import os
import uuid
from typing import Any

# Import gateway for SUGA-ISP compliance
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface

# Import directive validation for Alexa Smart Home API compliance
try:
    from lee.home_assistant.ha_common.ha_directive_validation import validate_directive
    _DIRECTIVE_VALIDATION_AVAILABLE = True
except ImportError:
    _DIRECTIVE_VALIDATION_AVAILABLE = False

# Security availability flag (Phase 5 - InputSanitizer integration)
_SECURITY_AVAILABLE = False

# NOTE: Core module imports removed - wrappers are self-contained implementations
# The interface router imports directly from this wrapper module
_ALEXA_AVAILABLE = True
_ALEXA_IMPORT_ERROR = None


def process_directive(event: dict[str, Any] = None, oauth_token: str = None, directive: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
    """Process Alexa Smart Home directive.

    DEPRECATED: Legacy directive handlers have been removed.
    Use proxy mode by setting USE_HA_ALEXA_ENDPOINT=true environment variable.
    All directives are now forwarded to Home Assistant's /api/alexa/smart_home endpoint.
    """
    correlation_id = generate_correlation_id("ha")

    execute_operation(GatewayInterface.LOGGING, "log_error",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="process_directive is deprecated. Use USE_HA_ALEXA_ENDPOINT=true for proxy mode.")

    return {
        "success": False,
        "error": "Legacy directive handlers removed. Set USE_HA_ALEXA_ENDPOINT=true to use proxy mode.",
        "error_code": "LEGACY_HANDLERS_REMOVED"
    }


def handle_discovery(event: dict[str, Any], oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.Discovery discovery request.

    Supports three modes:
    - Legacy mode: Enumerate/filter entities in LEE (default)
    - Proxy mode: Forward to Home Assistant /api/alexa/smart_home
    - Hybrid mode: Proxy for control, legacy for discovery

    Mode controlled by environment variables:
    - USE_HA_ALEXA_ENDPOINT=false: Legacy mode (both control and discovery)
    - USE_HA_ALEXA_ENDPOINT=true: Full proxy mode (both control and discovery)
    - USE_HA_ALEXA_PROXY_CONTROL=true + USE_HA_ALEXA_ENDPOINT=false: Hybrid mode

    Args:
        event: Alexa directive event
        oauth_token: OAuth token for authentication
        **kwargs: Additional parameters

    Returns:
        Alexa discovery response dict
    """
    correlation_id = generate_correlation_id("ha")

    # Check which mode to use for discovery
    # Priority: explicit discovery proxy setting > general proxy setting > legacy
    use_proxy_discovery = os.environ.get("USE_HA_ALEXA_PROXY_DISCOVERY", "false").lower() == "true"
    use_proxy_general = os.environ.get("USE_HA_ALEXA_ENDPOINT", "false").lower() == "true"

    # Use proxy discovery if explicitly enabled OR if general proxy mode is enabled
    use_proxy_mode = use_proxy_discovery or use_proxy_general

    if use_proxy_mode:
        # PROXY MODE: Forward to Home Assistant
        execute_operation(GatewayInterface.LOGGING, "log_info",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="Proxy discovery mode enabled - forwarding to Home Assistant")

        try:
            return _proxy_discovery_to_ha(event, oauth_token, correlation_id)
        except Exception as e:
            # If proxy discovery fails, log but don't crash
            execute_operation(GatewayInterface.LOGGING, "log_warning",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="Proxy discovery failed, falling back to legacy mode",
                             error=str(e))
            return _legacy_discovery(event, oauth_token, correlation_id)
    else:
        # LEGACY MODE: Use existing LEE discovery
        execute_operation(GatewayInterface.LOGGING, "log_info",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="Legacy discovery mode enabled - using LEE-side filtering")
        return _legacy_discovery(event, oauth_token, correlation_id)


def _proxy_discovery_to_ha(
    event: dict[str, Any],
    oauth_token: str,
    correlation_id: str
) -> dict[str, Any]:
    """Forward Alexa.Discovery directive to Home Assistant.

    Delegates entity filtering and endpoint mapping to Home Assistant's
    native Alexa integration using its alexa.yaml configuration.

    Args:
        event: Alexa directive event
        oauth_token: OAuth token for authentication
        correlation_id: Correlation ID for tracking

    Returns:
        Alexa discovery response from Home Assistant (forwarded unchanged)

    Raises:
        AlexaError: If forwarding fails
    """
    from lee.home_assistant.ha_alexa_proxy import forward_to_home_assistant_alexa

    directive = event.get("directive", {})

    execute_operation(GatewayInterface.LOGGING, "log_info",
                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                     message="Proxy discovery: Forwarding to Home Assistant /api/alexa/smart_home")

    try:
        # Forward to Home Assistant using existing proxy infrastructure
        ha_response = forward_to_home_assistant_alexa(directive, oauth_token)

        execute_operation(GatewayInterface.LOGGING, "log_info",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="Proxy discovery: Home Assistant response received")

        # Return HA's response unchanged (Alexa-compatible)
        return ha_response

    except Exception as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="Proxy discovery failed",
                         error=str(e))

        # Return Alexa error response
        directive_header = directive.get("header", {})
        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": str(uuid.uuid4()),
                    "correlationToken": directive_header.get("correlationToken", ""),
                    "payloadVersion": "3",
                },
                "payload": {
                    "type": "INTERNAL_ERROR",
                    "message": "Discovery forwarding failed"
                }
            }
        }


def _legacy_discovery(
    event: dict[str, Any],
    oauth_token: str,
    correlation_id: str
) -> dict[str, Any]:
    """Legacy discovery mode (LEE-side filtering).

    DEPRECATED: Use proxy mode by setting USE_HA_ALEXA_ENDPOINT=true

    This mode:
    - Calls /api/states to get all entities
    - Filters using alexa.yaml (5-stage filtering)
    - Maps entities to Alexa endpoints
    - Returns discovery response

    Args:
        event: Alexa directive event
        oauth_token: OAuth token for authentication
        correlation_id: Correlation ID for tracking

    Returns:
        Alexa discovery response dict
    """
    try:
        # Import discovery entity operations
        from lee.home_assistant.ha_discovery_entities import (
            enumerate_home_assistant_entities,
            filter_entities,
            map_entity_to_alexa_endpoint,
            build_discovery_response,
        )
    except ImportError as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="Failed to import discovery entities module",
                         error=str(e))
        return {
            "success": False,
            "error": f"Discovery module not available: {str(e)}",
            "error_code": "DISCOVERY_MODULE_IMPORT_FAILED"
        }

    try:
        # Step 1: Enumerate Home Assistant entities
        enum_result = enumerate_home_assistant_entities(correlation_id=correlation_id)
        if enum_result.get("success") is False:
            return enum_result

        all_entities = enum_result.get("entities", [])

        # Step 2: Filter entities for Alexa compatibility
        filter_result = filter_entities(all_entities, correlation_id=correlation_id)
        if filter_result.get("success") is False:
            return filter_result

        filtered_entities = filter_result.get("entities", [])

        # Step 3: Map entities to Alexa endpoints
        endpoints = []
        for entity in filtered_entities:
            endpoint = map_entity_to_alexa_endpoint(entity, correlation_id=correlation_id)
            endpoints.append(endpoint)

        # Step 4: Build discovery response
        response = build_discovery_response(endpoints, correlation_id=correlation_id, directive=event)

        execute_operation(GatewayInterface.LOGGING, "log_info",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="Device discovery completed successfully",
                         endpoint_count=len(endpoints))

        # Enable proactive state reporting to Alexa gateway
        try:
            from lee.home_assistant.ha_state_reporting import get_state_change_reporter

            reporter = get_state_change_reporter()
            alexa_gateway_url = os.environ.get(
                "ALEXA_GATEWAY_URL",
                "https://api.amazonalexa.com/v3/events"
            )

            if oauth_token:
                reporter.enable(
                    alexa_endpoint=alexa_gateway_url,
                    access_token=oauth_token
                )

                # Verify enable() succeeded
                if not reporter._enabled:
                    execute_operation(GatewayInterface.LOGGING, "log_error",
                                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                                     message="StateChangeReporter.enable() called but not enabled",
                                     alexa_endpoint=alexa_gateway_url)
                    raise RuntimeError("StateChangeReporter.enable() failed to initialize")

                execute_operation(GatewayInterface.LOGGING, "log_info",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="StateChangeReporter verified enabled for proactive reporting",
                                 alexa_endpoint=alexa_gateway_url,
                                 entity_count=len(endpoints))

                # Register WebSocket subscriptions for discovered entities
                try:
                    from lee.home_assistant.ha_websocket.state_subscriptions import get_subscription_manager

                    sub_manager = get_subscription_manager()

                    # Verify WebSocket is connected
                    if not sub_manager.is_connected():
                        execute_operation(GatewayInterface.LOGGING, "log_debug",
                                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                                         message="WebSocket not connected - skipping subscription registration")
                    else:
                        # Define Alexa-supported domains for state subscriptions
                        ALEXA_SUPPORTED_DOMAINS = (
                            "light.", "switch.", "climate.", "cover.", "lock.",
                            "media_player.", "fan.", "input_boolean.", "group."
                        )

                        # Extract entity IDs from discovered endpoints
                        entity_ids = []
                        for endpoint in endpoints:
                            endpoint_id = endpoint.get("endpointId", "").replace("#", ".")
                            if endpoint_id and endpoint_id.startswith(ALEXA_SUPPORTED_DOMAINS):
                                entity_ids.append(endpoint_id)

                        # Register subscriptions for state changes
                        subscription_count = 0
                        failed_count = 0
                        for entity_id in entity_ids:
                            try:
                                sub_manager.subscribe(
                                    entity_id=entity_id,
                                    callback=lambda eid, old, new, corr_id=correlation_id:
                                        get_state_change_reporter().on_state_change(
                                            eid, old, new, corr_id
                                        )
                                )
                                subscription_count += 1

                                execute_operation(GatewayInterface.LOGGING, "log_debug",
                                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                                 message="WebSocket subscription registered",
                                                 entity_id=entity_id)
                            except Exception as e:
                                failed_count += 1
                                execute_operation(GatewayInterface.LOGGING, "log_debug",
                                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                                 message="Failed to register WebSocket subscription",
                                                 entity_id=entity_id,
                                                 error=str(e))

                        execute_operation(GatewayInterface.LOGGING, "log_info",
                                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                                         message="WebSocket subscriptions registered",
                                         subscription_count=subscription_count,
                                         failed_count=failed_count)
                except Exception as e:
                    execute_operation(GatewayInterface.LOGGING, "log_debug",
                                     corr_id=correlation_id, scope="HOME_ASSISTANT",
                                     message="Failed to register WebSocket subscriptions",
                                     error=str(e))
            else:
                execute_operation(GatewayInterface.LOGGING, "log_debug",
                                 corr_id=correlation_id, scope="HOME_ASSISTANT",
                                 message="OAuth token not provided - skipping StateChangeReporter enable")
        except Exception as e:
            execute_operation(GatewayInterface.LOGGING, "log_debug",
                             corr_id=correlation_id, scope="HOME_ASSISTANT",
                             message="Failed to enable StateChangeReporter",
                             error=str(e))

        return response

    except Exception as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="Device discovery failed with exception",
                         error=str(e))
        return {
            "success": False,
            "error": f"Discovery failed: {str(e)}",
            "error_code": "DISCOVERY_FAILED"
        }


def handle_control(event: dict[str, Any], oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle generic controller directive."""
    correlation_id = generate_correlation_id("ha")

    # Handle control using HA gateway
    try:
        # Remove correlation_id from kwargs to avoid duplicate parameter
        kwargs.pop('correlation_id', None)
        return ha_gateway.ha_execute_operation(
            HAGatewayInterface.ALEXA, "control",
            event=event, oauth_token=oauth_token,
            correlation_id=correlation_id, **kwargs
        )
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="handle_control FAILED", error=str(e))
        return {"success": False, "error": str(e)}
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="handle_control FAILED with unexpected error", error=str(e))
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def _handle_alexa_control_base(
    operation_name: str,
    gateway_interface: HAGatewayInterface,
    ha_operation: str,
    entity_id: str,
    payload: dict[str, Any],
    oauth_token: str = None,
    param_map: dict[str, str] = None,
    **kwargs: Any
) -> dict[str, Any]:
    """Base handler for Alexa control directives.

    Provides unified error handling and logging for all Alexa control operations.

    Args:
        operation_name: Name of the Alexa operation (for logging)
        gateway_interface: HA gateway interface enum
        ha_operation: Home Assistant operation name
        entity_id: Entity ID to control
        payload: Directive payload from Alexa
        oauth_token: OAuth token for authentication
        param_map: Optional dict mapping payload keys to parameter names
        **kwargs: Additional parameters

    Returns:
        dict: Operation result with success/error status
    """
    correlation_id = generate_correlation_id("ha")

    try:
        # Build operation parameters
        # Remove correlation_id from kwargs to avoid duplicate parameter
        kwargs.pop('correlation_id', None)
        params = {"entity_id": entity_id, **kwargs}

        # Add OAuth token if provided
        if oauth_token is not None:
            params["oauth_token"] = oauth_token

        # Extract parameters from payload using param_map
        if param_map and payload:
            for payload_key, param_name in param_map.items():
                if payload_key in payload:
                    params[param_name] = payload[payload_key]

        # Execute via HA gateway
        return ha_gateway.ha_execute_operation(
            gateway_interface,
            ha_operation,
            correlation_id=correlation_id,
            **params
        )
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id,
            scope="HOME_ASSISTANT",
            message=f"{operation_name} FAILED",
            error=str(e)
        )
        return {"success": False, "error": str(e)}
    except Exception as e:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id,
            scope="HOME_ASSISTANT",
            message=f"{operation_name} FAILED with unexpected error",
            error=str(e)
        )
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


# Dispatch table for Alexa control operations
# Format: (gateway_interface, operation_name, param_mapping)
# param_mapping is optional: dict mapping payload keys to parameter names
_ALEXA_CONTROL_DISPATCH = {
    # Already refactored (3 functions)
    "power_control": (HAGatewayInterface.ALEXA, "power_control", None),
    "brightness_control": (HAGatewayInterface.ALEXA, "brightness_control", None),
    "thermostat_control": (HAGatewayInterface.ALEXA, "thermostat_control", None),

    # Color controllers (4 functions)
    "set_color": (HAGatewayInterface.LIGHT, "turn_on", {"rgb_color": "rgb_color"}),
    "set_color_temperature": (HAGatewayInterface.LIGHT, "turn_on", {"color_temp": "color_temp"}),
    "increase_color_temperature": (HAGatewayInterface.LIGHT, "turn_on", {"color_temp_kelvin": "color_temp_kelvin"}),
    "decrease_color_temperature": (HAGatewayInterface.LIGHT, "turn_on", {"color_temp_kelvin": "color_temp_kelvin"}),

    # Scene controllers (2 functions)
    "scene_activate": (HAGatewayInterface.SCENE, "turn_on", None),
    "scene_deactivate": (HAGatewayInterface.SCENE, "turn_off", None),

    # Lock controllers (2 functions)
    "lock_lock": (HAGatewayInterface.LOCK, "lock", None),
    "lock_unlock": (HAGatewayInterface.LOCK, "unlock", None),

    # Speaker controllers (3 functions)
    "speaker_set_volume": (HAGatewayInterface.MEDIA_PLAYER, "volume_set", {"volume_level": "volume_level"}),
    "speaker_adjust_volume": (HAGatewayInterface.MEDIA_PLAYER, "volume_set", {"volume_level": "volume_level"}),
    "speaker_set_mute": (HAGatewayInterface.MEDIA_PLAYER, "volume_mute", {"is_muted": "is_volume_muted"}),

    # Playback controllers (6 functions)
    "playback_play": (HAGatewayInterface.MEDIA_PLAYER, "media_play", None),
    "playback_pause": (HAGatewayInterface.MEDIA_PLAYER, "media_pause", None),
    "playback_stop": (HAGatewayInterface.MEDIA_PLAYER, "media_stop", None),
    "playback_next": (HAGatewayInterface.MEDIA_PLAYER, "media_next_track", None),
    "playback_previous": (HAGatewayInterface.MEDIA_PLAYER, "media_previous_track", None),

    # Thermostat controllers (2 functions)
    "thermostat_adjust_target_temperature": (HAGatewayInterface.CLIMATE, "set_temperature", {"temperature": "temperature"}),
    "thermostat_set_thermostat_mode": (HAGatewayInterface.CLIMATE, "set_hvac_mode", {"hvac_mode": "hvac_mode"}),
}


def handle_power_control(entity_id: str, payload: dict[str, Any],
                        oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.PowerController directive."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["power_control"]
    return _handle_alexa_control_base(
        "handle_power_control", interface, operation,
        entity_id, payload, oauth_token, param_map, **kwargs
    )


def handle_brightness_control(entity_id: str, payload: dict[str, Any],
                             oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.BrightnessController directive."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["brightness_control"]
    return _handle_alexa_control_base(
        "handle_brightness_control", interface, operation,
        entity_id, payload, oauth_token, param_map, **kwargs
    )


def handle_thermostat_control(entity_id: str, payload: dict[str, Any],
                             oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.ThermostatController directive."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["thermostat_control"]
    return _handle_alexa_control_base(
        "handle_thermostat_control", interface, operation,
        entity_id, payload, oauth_token, param_map, **kwargs
    )


def handle_accept_grant(event: dict[str, Any], oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.Authorization.AcceptGrant directive."""
    correlation_id = generate_correlation_id("ha")

    # Handle accept grant using HA gateway
    try:
        # Remove correlation_id from kwargs to avoid duplicate parameter
        kwargs.pop('correlation_id', None)
        return ha_gateway.ha_execute_operation(
            HAGatewayInterface.ALEXA, "accept_grant",
            event=event, oauth_token=oauth_token,
            correlation_id=correlation_id, **kwargs
        )
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="handle_accept_grant FAILED", error=str(e))
        return {"success": False, "error": str(e)}
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HOME_ASSISTANT",
                         message="handle_accept_grant FAILED with unexpected error", error=str(e))
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def handle_set_color_wrapper(entity_id: str, payload: dict[str, Any],
                             oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.ColorController directive (set light color)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["set_color"]
    return _handle_alexa_control_base(
        "handle_set_color_wrapper", interface, operation,
        entity_id, payload, oauth_token, param_map, **kwargs
    )


def handle_set_color_temperature_wrapper(entity_id: str, payload: dict[str, Any],
                                         oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.ColorTemperatureController directive (set color temperature)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["set_color_temperature"]
    return _handle_alexa_control_base(
        "handle_set_color_temperature_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_increase_color_temperature_wrapper(entity_id: str, payload: dict[str, Any],
                                              oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.ColorTemperatureController directive (increase color temperature)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["increase_color_temperature"]
    return _handle_alexa_control_base(
        "handle_increase_color_temperature_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_decrease_color_temperature_wrapper(entity_id: str, payload: dict[str, Any],
                                              oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.ColorTemperatureController directive (decrease color temperature)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["decrease_color_temperature"]
    return _handle_alexa_control_base(
        "handle_decrease_color_temperature_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_scene_activate_wrapper(entity_id: str, payload: dict[str, Any],
                                   oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.SceneController directive (activate scene)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["scene_activate"]
    return _handle_alexa_control_base(
        "handle_scene_activate_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_scene_deactivate_wrapper(entity_id: str, payload: dict[str, Any],
                                     oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.SceneController directive (deactivate scene)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["scene_deactivate"]
    return _handle_alexa_control_base(
        "handle_scene_deactivate_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_lock_lock_wrapper(entity_id: str, payload: dict[str, Any],
                             oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.LockController directive (lock door)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["lock_lock"]
    return _handle_alexa_control_base(
        "handle_lock_lock_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_lock_unlock_wrapper(entity_id: str, payload: dict[str, Any],
                               oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.LockController directive (unlock door)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["lock_unlock"]
    return _handle_alexa_control_base(
        "handle_lock_unlock_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_speaker_set_volume_wrapper(entity_id: str, payload: dict[str, Any],
                                      oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.Speaker directive (set speaker volume)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["speaker_set_volume"]
    return _handle_alexa_control_base(
        "handle_speaker_set_volume_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_speaker_adjust_volume_wrapper(entity_id: str, payload: dict[str, Any],
                                         oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.Speaker directive (adjust speaker volume)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["speaker_adjust_volume"]
    return _handle_alexa_control_base(
        "handle_speaker_adjust_volume_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_speaker_set_mute_wrapper(entity_id: str, payload: dict[str, Any],
                                    oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.Speaker directive (mute/unmute speaker)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["speaker_set_mute"]
    return _handle_alexa_control_base(
        "handle_speaker_set_mute_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_playback_play_wrapper(entity_id: str, payload: dict[str, Any],
                                 oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.PlaybackController directive (start playback)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["playback_play"]
    return _handle_alexa_control_base(
        "handle_playback_play_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_playback_pause_wrapper(entity_id: str, payload: dict[str, Any],
                                  oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.PlaybackController directive (pause playback)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["playback_pause"]
    return _handle_alexa_control_base(
        "handle_playback_pause_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_playback_stop_wrapper(entity_id: str, payload: dict[str, Any],
                                 oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.PlaybackController directive (stop playback)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["playback_stop"]
    return _handle_alexa_control_base(
        "handle_playback_stop_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_playback_next_wrapper(entity_id: str, payload: dict[str, Any],
                                 oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.PlaybackController directive (next track)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["playback_next"]
    return _handle_alexa_control_base(
        "handle_playback_next_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_playback_previous_wrapper(entity_id: str, payload: dict[str, Any],
                                     oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.PlaybackController directive (previous track)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["playback_previous"]
    return _handle_alexa_control_base(
        "handle_playback_previous_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_thermostat_adjust_target_temperature_wrapper(entity_id: str, payload: dict[str, Any],
                                                         oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.ThermostatController directive (adjust target temperature)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["thermostat_adjust_target_temperature"]
    return _handle_alexa_control_base(
        "handle_thermostat_adjust_target_temperature_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def handle_thermostat_set_thermostat_mode_wrapper(entity_id: str, payload: dict[str, Any],
                                                   oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa.ThermostatController directive (set thermostat mode)."""
    interface, operation, param_map = _ALEXA_CONTROL_DISPATCH["thermostat_set_thermostat_mode"]
    return _handle_alexa_control_base(
        "handle_thermostat_set_thermostat_mode_wrapper", interface, operation,
        entity_id, payload, oauth_token, **kwargs
    )


def execute_alexa_operation(operation: str, **kwargs) -> Any:
    """Execute Alexa operation via dispatch with SUGA-ISP debug support.
    
    This function provides a unified interface for all Alexa operations,
    routing to appropriate wrapper functions with proper error handling
    and observability.
    
    Args:
        operation: The Alexa operation to execute (e.g., 'process_directive', 'handle_discovery')
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from the underlying Alexa gateway
    """
    correlation_id = kwargs.pop("correlation_id", None) or generate_correlation_id("ha")

    # Map operation names to wrapper functions
    operation_mapping = {
        "process_directive": process_directive,
        "handle_discovery": handle_discovery,
        "handle_power_control": handle_power_control,
        "handle_brightness_control": handle_brightness_control,
        "handle_thermostat_control": handle_thermostat_control,
        "handle_accept_grant": handle_accept_grant,
    }

    if operation not in operation_mapping:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="ALEXA_WRAPPERS",
                         message="Unsupported Alexa operation", operation=operation)
        return {
            "success": False,
            "error": f"Unsupported Alexa operation: {operation}",
            "error_code": "UNSUPPORTED_OPERATION"
        }

    try:
        # Extract event from kwargs for operations that require it positionally
        # Some operations (process_directive, handle_discovery, handle_control) require
        # event as first positional parameter, while others (handle_*_control) use entity_id/payload
        # Remove correlation_id from kwargs to avoid duplicate parameter error
        kwargs.pop('correlation_id', None)

        if 'event' in kwargs:
            event = kwargs.pop('event')
            return operation_mapping[operation](event, correlation_id=correlation_id, **kwargs)
        else:
            return operation_mapping[operation](correlation_id=correlation_id, **kwargs)
    except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="ALEXA_WRAPPERS",
                         message="execute_alexa_operation FAILED", operation=operation, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "error_code": "OPERATION_FAILED"
        }
    except Exception as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="ALEXA_WRAPPERS",
                         message="execute_alexa_operation FAILED with unexpected error", operation=operation, error=str(e))
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_code": "OPERATION_FAILED"
        }
