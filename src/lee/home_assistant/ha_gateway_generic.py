# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Added LEE file header for compliance


"""ha_gateway_generic.py - Home Assistant Gateway Core Implementation (HA-SUGA)
Version: 2025-12-22_1
Description: Pattern-based registry with simplified routing for Home Assistant (SUGA-ISP compliant)

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import importlib
import os
from collections import defaultdict
from collections.abc import Callable
from typing import Any

# ===== INTERFACE ROUTER REGISTRY =====
# Maps HAGatewayInterface to (module_name, function_name)
# Pattern-based routing: Each interface has one router function with internal dispatch
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import enum from HA package to prevent circular imports
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG mode is enabled."""
    return os.environ.get("LEE_DEBUG", "false").lower() == "true"


def _debug_log(corr_id: str, **kwargs: Any) -> None:
    """Conditional debug logging that only executes when debug mode is enabled.

    Args:
        corr_id: Correlation ID for log tracking
        **kwargs: Additional parameters to pass to execute_operation
    """
    if _is_debug_mode():
        execute_operation(GatewayInterface.DEBUG, "log", corr_id=corr_id, **kwargs)


def _debug_timing(corr_id: str, operation_name: str, **kwargs: Any) -> Any:
    """Conditional debug timing context manager that only activates when debug mode is enabled.

    Args:
        corr_id: Correlation ID for tracking
        operation_name: Name of operation being timed
        **kwargs: Additional parameters for timing

    Returns:
        Context manager for timing (or no-op context manager if debug disabled)
    """
    if _is_debug_mode():
        return execute_operation(GatewayInterface.DEBUG, "timing",
                               corr_id=corr_id, operation_name=operation_name, **kwargs)
    from contextlib import nullcontext
    return nullcontext()

_INTERFACE_ROUTERS: dict[HAGatewayInterface, tuple[str, str]] = {
    # Voice assistant interfaces
    HAGatewayInterface.ALEXA: ("lee.home_assistant.interface.ha_alexa", "execute_alexa_operation"),
    HAGatewayInterface.ASSIST: ("lee.home_assistant.interface.ha_assist", "execute_assist_operation"),
    HAGatewayInterface.ALEXA_RESPONSE: ("lee.home_assistant.interface.ha_alexa_response", "execute_alexa_response_operation"),

    # Core Home Assistant functionality
    HAGatewayInterface.DEVICES: ("lee.home_assistant.interface.ha_devices", "execute_devices_operation"),
    HAGatewayInterface.CONFIG: ("lee.home_assistant.interface.ha_config", "execute_config_operation"),
    HAGatewayInterface.WEBSOCKET: ("lee.home_assistant.interface.ha_websocket", "execute_websocket_operation"),
    HAGatewayInterface.REGISTRY: ("lee.home_assistant.interface.ha_registry", "execute_registry_operation"),
    HAGatewayInterface.AUTOMATION: ("lee.home_assistant.interface.ha_automation", "execute_automation_operation"),
    HAGatewayInterface.BLUEPRINT: ("lee.home_assistant.interface.ha_blueprint", "execute_blueprint_operation"),
    HAGatewayInterface.SUPERVISOR: ("lee.home_assistant.interface.ha_supervisor", "execute_supervisor_operation"),
    HAGatewayInterface.CAMERA: ("lee.home_assistant.interface.ha_camera", "execute_camera_operation"),
    HAGatewayInterface.ENERGY: ("lee.home_assistant.interface.ha_energy", "execute_energy_operation"),
    HAGatewayInterface.BACKUP: ("lee.home_assistant.interface.ha_backup", "execute_backup_operation"),
    HAGatewayInterface.HISTORY: ("lee.home_assistant.interface.ha_history", "execute_history_operation"),
    HAGatewayInterface.REPAIRS: ("lee.home_assistant.interface.ha_repairs", "execute_repairs_operation"),
    HAGatewayInterface.STATISTICS: ("lee.home_assistant.interface.ha_statistics", "execute_statistics_operation"),
    HAGatewayInterface.LOGBOOK: ("lee.home_assistant.interface.ha_logbook", "execute_logbook_operation"),
    HAGatewayInterface.SCENE: ("lee.home_assistant.interface.ha_scene", "execute_scene_operation"),
    HAGatewayInterface.SCRIPT: ("lee.home_assistant.interface.ha_script", "execute_script_operation"),
    HAGatewayInterface.NOTIFY: ("lee.home_assistant.interface.ha_notify", "execute_notify_operation"),
    HAGatewayInterface.ESPHOME: ("lee.home_assistant.interface.ha_esphome", "execute_esphome_operation"),
    HAGatewayInterface.MOBILE_APP: ("lee.home_assistant.interface.ha_mobile_app", "execute_mobile_app_operation"),
    HAGatewayInterface.LOGGER: ("lee.home_assistant.interface.ha_logger", "execute_logger_operation"),
    HAGatewayInterface.HARDWARE: ("lee.home_assistant.interface.ha_hardware", "execute_hardware_operation"),
    HAGatewayInterface.SENSOR: ("lee.home_assistant.interface.ha_sensor", "execute_sensor_operation"),
    HAGatewayInterface.NUMBER: ("lee.home_assistant.interface.ha_number", "execute_number_operation"),
    HAGatewayInterface.PERSISTENT: ("lee.home_assistant.interface.ha_persistent", "execute_persistent_operation"),
    HAGatewayInterface.CONVERSATION: ("lee.home_assistant.interface.ha_conversation", "execute_conversation_operation"),
    HAGatewayInterface.ZONE: ("lee.home_assistant.interface.ha_zone", "execute_zone_operation"),
    HAGatewayInterface.COUNTER: ("lee.home_assistant.interface.ha_counter", "execute_counter_operation"),
    HAGatewayInterface.TIMER: ("lee.home_assistant.interface.ha_timer", "execute_timer_operation"),
    HAGatewayInterface.INPUT_BOOLEAN: ("lee.home_assistant.interface.ha_input_boolean", "execute_input_boolean_operation"),
    HAGatewayInterface.REMOTE: ("lee.home_assistant.interface.ha_remote", "execute_remote_operation"),
    HAGatewayInterface.SIREN: ("lee.home_assistant.interface.ha_siren", "execute_siren_operation"),
    HAGatewayInterface.UPDATE: ("lee.home_assistant.interface.ha_update", "execute_update_operation"),
    HAGatewayInterface.CALENDAR: ("lee.home_assistant.interface.ha_calendar", "execute_calendar_operation"),
    HAGatewayInterface.IMAGE_PROCESSING: ("lee.home_assistant.interface.ha_image_processing", "execute_image_processing_operation"),
    HAGatewayInterface.STT: ("lee.home_assistant.interface.ha_stt", "execute_stt_operation"),
    HAGatewayInterface.TTS: ("lee.home_assistant.interface.ha_tts", "execute_tts_operation"),
    HAGatewayInterface.FILE: ("lee.home_assistant.interface.ha_file", "execute_file_operation"),
    HAGatewayInterface.TODO: ("lee.home_assistant.interface.ha_todo", "execute_todo_operation"),
    HAGatewayInterface.TEMPLATE: ("lee.home_assistant.interface.ha_template", "execute_template_operation"),
    HAGatewayInterface.MQTT: ("lee.home_assistant.interface.ha_mqtt", "execute_mqtt_operation"),
    HAGatewayInterface.SHOPPING_LIST: ("lee.home_assistant.interface.ha_shopping_list", "execute_shopping_list_operation"),
    HAGatewayInterface.UTILITY_METER: ("lee.home_assistant.interface.ha_utility_meter", "execute_utility_meter_operation"),
    HAGatewayInterface.WAKE_ON_LAN: ("lee.home_assistant.interface.ha_wake_on_lan", "execute_wake_on_lan_operation"),
    HAGatewayInterface.ZHA: ("lee.home_assistant.interface.ha_zha", "execute_zha_operation"),
    HAGatewayInterface.SONOS: ("lee.home_assistant.interface.ha_sonos", "execute_sonos_operation"),
    HAGatewayInterface.ANDROIDTV: ("lee.home_assistant.interface.ha_androidtv", "execute_androidtv_operation"),
    HAGatewayInterface.WEBOSTV: ("lee.home_assistant.interface.ha_webostv", "execute_webostv_operation"),
    HAGatewayInterface.DENONAVR: ("lee.home_assistant.interface.ha_denonavr", "execute_denonavr_operation"),
    HAGatewayInterface.ROKU: ("lee.home_assistant.interface.ha_roku", "execute_roku_operation"),
    HAGatewayInterface.GOOGLE_MAIL: ("lee.home_assistant.interface.ha_google_mail", "execute_google_mail_operation"),
    HAGatewayInterface.HUE: ("lee.home_assistant.interface.ha_hue", "execute_hue_operation"),
    HAGatewayInterface.NEATO: ("lee.home_assistant.interface.ha_neato", "execute_neato_operation"),
    HAGatewayInterface.TADO: ("lee.home_assistant.interface.ha_tado", "execute_tado_operation"),
    HAGatewayInterface.TPLINK: ("lee.home_assistant.interface.ha_tplink", "execute_tplink_operation"),
    HAGatewayInterface.ZWAVE_JS: ("lee.home_assistant.interface.ha_zwave_js", "execute_zwave_js_operation"),
    HAGatewayInterface.DECONZ: ("lee.home_assistant.interface.ha_deconz", "execute_deconz_operation"),
    HAGatewayInterface.HOMEKIT: ("lee.home_assistant.interface.ha_homekit", "execute_homekit_operation"),
    HAGatewayInterface.TRANSMISSION: ("lee.home_assistant.interface.ha_transmission", "execute_transmission_operation"),
    HAGatewayInterface.FFMPEG: ("lee.home_assistant.interface.ha_ffmpeg", "execute_ffmpeg_operation"),
    HAGatewayInterface.BROWSER: ("lee.home_assistant.interface.ha_browser", "execute_browser_operation"),
    HAGatewayInterface.BLUE_CURRENT: ("lee.home_assistant.interface.ha_blue_current", "execute_blue_current_operation"),
    HAGatewayInterface.CAST: ("lee.home_assistant.interface.ha_cast", "execute_cast_operation"),
    HAGatewayInterface.ECOVACS: ("lee.home_assistant.interface.ha_ecovacs", "execute_ecovacs_operation"),
    HAGatewayInterface.PS4: ("lee.home_assistant.interface.ha_ps4", "execute_ps4_operation"),
    HAGatewayInterface.VIZIO: ("lee.home_assistant.interface.ha_vizio", "execute_vizio_operation"),
    HAGatewayInterface.SNAPCAST: ("lee.home_assistant.interface.ha_snapcast", "execute_snapcast_operation"),
    HAGatewayInterface.WEMO: ("lee.home_assistant.interface.ha_wemo", "execute_wemo_operation"),
    HAGatewayInterface.BLUESOUND: ("lee.home_assistant.interface.ha_bluesound", "execute_bluesound_operation"),
    HAGatewayInterface.NUKI: ("lee.home_assistant.interface.ha_nuki", "execute_nuki_operation"),
    HAGatewayInterface.IMAP: ("lee.home_assistant.interface.ha_imap", "execute_imap_operation"),
    HAGatewayInterface.BLINK: ("lee.home_assistant.interface.ha_blink", "execute_blink_operation"),
    HAGatewayInterface.ICLOUD: ("lee.home_assistant.interface.ha_icloud", "execute_icloud_operation"),
    HAGatewayInterface.FLUX_LED: ("lee.home_assistant.interface.ha_flux_led", "execute_flux_led_operation"),
    HAGatewayInterface.HIVE: ("lee.home_assistant.interface.ha_hive", "execute_hive_operation"),
    HAGatewayInterface.ALERT: ("lee.home_assistant.interface.ha_alert", "execute_alert_operation"),
    HAGatewayInterface.ECOBEE: ("lee.home_assistant.interface.ha_ecobee", "execute_ecobee_operation"),
    HAGatewayInterface.SHELLY: ("lee.home_assistant.interface.ha_shelly", "execute_shelly_operation"),
    HAGatewayInterface.SIMPLISAFE: ("lee.home_assistant.interface.ha_simplisafe", "execute_simplisafe_operation"),
    HAGatewayInterface.GOOGLE_ASSISTANT: ("lee.home_assistant.interface.ha_google_assistant", "execute_google_assistant_operation"),
    HAGatewayInterface.LIFX: ("lee.home_assistant.interface.ha_lifx", "execute_lifx_operation"),
    HAGatewayInterface.ADGUARD: ("lee.home_assistant.interface.ha_adguard", "execute_adguard_operation"),
    HAGatewayInterface.ABODE: ("lee.home_assistant.interface.ha_abode", "execute_abode_operation"),
    HAGatewayInterface.AMCREST: ("lee.home_assistant.interface.ha_amcrest", "execute_amcrest_operation"),
    HAGatewayInterface.IFTTT: ("lee.home_assistant.interface.ha_ifttt", "execute_ifttt_operation"),
    HAGatewayInterface.ADS: ("lee.home_assistant.interface.ha_ads", "execute_ads_operation"),
    HAGatewayInterface.ALARMDECODER: ("lee.home_assistant.interface.ha_alarmdecoder", "execute_alarmdecoder_operation"),
    HAGatewayInterface.ADVANTAGE_AIR: ("lee.home_assistant.interface.ha_advantage_air", "execute_advantage_air_operation"),
    HAGatewayInterface.AMBERELECTRIC: ("lee.home_assistant.interface.ha_amberelectric", "execute_amberelectric_operation"),
    HAGatewayInterface.AGENT_DVR: ("lee.home_assistant.interface.ha_agent_dvr", "execute_agent_dvr_operation"),
    HAGatewayInterface.AI_TASK: ("lee.home_assistant.interface.ha_ai_task", "execute_ai_task_operation"),
    HAGatewayInterface.AFTERSHIP: ("lee.home_assistant.interface.ha_aftership", "execute_aftership_operation"),
    HAGatewayInterface.BANG_OLUFSEN: ("lee.home_assistant.interface.ha_bang_olufsen", "execute_bang_olufsen_operation"),
    HAGatewayInterface.ASSIST_SATELLITE: ("lee.home_assistant.interface.ha_assist_satellite", "execute_assist_satellite_operation"),
    HAGatewayInterface.TOUCH_PANEL: ("lee.home_assistant.interface.ha_touch_panel", "execute_touch_panel_operation"),
    HAGatewayInterface.SQUEEZEBOX: ("lee.home_assistant.interface.ha_squeezebox", "execute_squeezebox_operation"),
    HAGatewayInterface.ALEXA_DEVICES: ("lee.home_assistant.interface.ha_alexa_devices", "execute_alexa_devices_operation"),
    HAGatewayInterface.BOND: ("lee.home_assistant.interface.ha_bond", "execute_bond_operation"),
    HAGatewayInterface.BOSCH_ALARM: ("lee.home_assistant.interface.ha_bosch_alarm", "execute_bosch_alarm_operation"),
    HAGatewayInterface.BRING: ("lee.home_assistant.interface.ha_bring", "execute_bring_operation"),
    HAGatewayInterface.BSBLAN: ("lee.home_assistant.interface.ha_bsblan", "execute_bsblan_operation"),
    HAGatewayInterface.PROXIMITY: ("lee.home_assistant.interface.ha_proximity", "execute_proximity_operation"),
    HAGatewayInterface.SUN: ("lee.home_assistant.interface.ha_sun", "execute_sun_operation"),

    # PHASE 12: Device control interfaces
    HAGatewayInterface.SWITCH: ("lee.home_assistant.interface.ha_switch", "execute_switch_operation"),
    HAGatewayInterface.LIGHT: ("lee.home_assistant.interface.ha_light", "execute_light_operation"),
    HAGatewayInterface.CLIMATE: ("lee.home_assistant.interface.ha_climate", "execute_climate_operation"),
    HAGatewayInterface.COVER: ("lee.home_assistant.interface.ha_cover", "execute_cover_operation"),
    HAGatewayInterface.LOCK: ("lee.home_assistant.interface.ha_lock", "execute_lock_operation"),
    HAGatewayInterface.MEDIA_PLAYER: ("lee.home_assistant.interface.ha_media_player", "execute_media_player_operation"),
    HAGatewayInterface.VACUUM: ("lee.home_assistant.interface.ha_vacuum", "execute_vacuum_operation"),

    # PHASE 13: Additional device control interfaces
    HAGatewayInterface.FAN: ("lee.home_assistant.interface.ha_fan", "execute_fan_operation"),
    HAGatewayInterface.HUMIDIFIER: ("lee.home_assistant.interface.ha_humidifier", "execute_humidifier_operation"),
    HAGatewayInterface.WATER_HEATER: ("lee.home_assistant.interface.ha_water_heater", "execute_water_heater_operation"),
    HAGatewayInterface.ALARM_CONTROL_PANEL: ("lee.home_assistant.interface.ha_alarm_control_panel", "execute_alarm_control_panel_operation"),
    HAGatewayInterface.BUTTON: ("lee.home_assistant.interface.ha_button", "execute_button_operation"),
    HAGatewayInterface.GROUP: ("lee.home_assistant.interface.ha_group", "execute_group_operation"),
    HAGatewayInterface.PERSON: ("lee.home_assistant.interface.ha_person", "execute_person_operation"),
    HAGatewayInterface.WEATHER: ("lee.home_assistant.interface.ha_weather", "execute_weather_operation"),
    HAGatewayInterface.BINARY_SENSOR: ("lee.home_assistant.interface.ha_binary_sensor", "execute_binary_sensor_operation"),
    HAGatewayInterface.INPUT_BUTTON: ("lee.home_assistant.interface.ha_input_button", "execute_input_button_operation"),
    HAGatewayInterface.INPUT_DATETIME: ("lee.home_assistant.interface.ha_input_datetime", "execute_input_datetime_operation"),
    HAGatewayInterface.INPUT_NUMBER: ("lee.home_assistant.interface.ha_input_number", "execute_input_number_operation"),
    HAGatewayInterface.INPUT_TEXT: ("lee.home_assistant.interface.ha_input_text", "execute_input_text_operation"),
    HAGatewayInterface.INPUT_SELECT: ("lee.home_assistant.interface.ha_input_select", "execute_input_select_operation"),
    HAGatewayInterface.TIMED_BACKUP: ("lee.home_assistant.interface.ha_timed_backup", "execute_timed_backup_operation"),

    # Supporting infrastructure
    HAGatewayInterface.CACHE: ("lee.home_assistant.interface.ha_cache", "execute_cache_operation"),
    HAGatewayInterface.HEALTH: ("lee.home_assistant.interface.ha_health", "execute_ha_health_operation"),
}


# ===== FAST PATH CACHE =====
_fast_path_enabled: bool = True  # ENABLED: Fast path caching for frequently called operations (60-80% faster)
_fast_path_cache: dict[tuple[HAGatewayInterface, str], tuple[Callable, str, str]] = {}
_operation_call_counts: dict[tuple[HAGatewayInterface, str], int] = defaultdict(int)


# ===== SUGA-ISP COMPLIANT HELPERS =====


def ha_execute_operation(interface: HAGatewayInterface, operation: str, **kwargs) -> Any:  # pylint: disable=R0912,R0915
    """Execute HA operation through pattern-based routing (SUGA-ISP compliant).

    This is the main entry point for all Home Assistant operations.
    Cross-interface calls to LEE should route through gateway.execute_operation().

        interface: The HAGatewayInterface to route through
        operation: The operation name to execute
        **kwargs: Operation-specific parameters

        Operation result from HA interface implementation

    Raises:
        ValueError: If interface unknown
        RuntimeError: If module/function loading fails or execution fails
    """
    # SUGA-ISP compliant: always use execute_operation() for all Gateway access

    import time

    # Generate correlation ID for debugging if not provided
    correlation_id = kwargs.get("correlation_id")
    if correlation_id is None:
        correlation_id = generate_correlation_id("ha")
        kwargs["correlation_id"] = correlation_id

    start_time = None
    if _is_debug_mode():
        import time
        start_time = time.perf_counter()

        _debug_log(correlation_id, scope="HA_GATEWAY",
                  message="ha_execute_operation ENTRY",
                  ha_interface=str(interface), ha_operation=operation,
                  param_keys=list(kwargs.keys()), param_count=len(kwargs))

    with _debug_timing(correlation_id, "ha_execute_operation",
                      ha_interface=str(interface), target_ha_operation=operation):
        try:
            # Increment call count for fast path decision
            _operation_call_counts[(interface, operation)] += 1

            # Try fast path first if enabled
            if _fast_path_enabled:
                cache_key = (interface, operation)
                if cache_key in _fast_path_cache:
                    _debug_log(correlation_id, scope="HA_GATEWAY",
                                     message="Using fast path cache",
                                     ha_interface=str(interface), ha_operation=operation)

                    func, module_name, func_name = _fast_path_cache[cache_key]

                    try:
                        # HA interface routers always need operation parameter
                        result = func(operation, **kwargs)
                        _debug_log(correlation_id, scope="HA_GATEWAY",
                                         message="Fast path execution completed",
                                         ha_ha_interface=str(interface), ha_operation=operation, success=True)
                        return result
                    except (ValueError, TypeError, KeyError) as e:
                        # Data validation error
                        _debug_log(correlation_id, scope="HA_GATEWAY",
                                         message="Fast path validation failed",
                                         ha_interface=str(interface), ha_operation=operation,
                                         error_type=type(e).__name__, error=str(e))
                        raise RuntimeError(
                            f"Failed to execute {interface.value}.{operation}: {e!s}",
                        ) from e
                    except (AttributeError, ImportError) as e:
                        # Configuration error
                        _debug_log(correlation_id, scope="HA_GATEWAY",
                                         message="Fast path config failed",
                                         ha_interface=str(interface), ha_operation=operation,
                                         error_type=type(e).__name__, error=str(e))
                        raise RuntimeError(
                            f"Failed to execute {interface.value}.{operation}: {e!s}",
                        ) from e
                    except (ConnectionError, TimeoutError, OSError) as e:
                        # Network or system error
                        _debug_log(correlation_id, scope="HA_GATEWAY",
                                         message="Fast path system error",
                                         ha_interface=str(interface), ha_operation=operation,
                                         error_type=type(e).__name__, error=str(e))
                        raise RuntimeError(
                            f"Failed to execute {interface.value}.{operation}: {e!s}",
                        ) from e
                    except Exception as e:
                        # Other unexpected errors
                        _debug_log(correlation_id, scope="HA_GATEWAY",
                                         message="Fast path execution failed",
                                         ha_interface=str(interface), ha_operation=operation,
                                         error_type=type(e).__name__, error=str(e))
                        raise RuntimeError(
                            f"Failed to execute {interface.value}.{operation}: {e!s}",
                        ) from e

            # Slow path: Pattern-based routing
            if interface not in _INTERFACE_ROUTERS:
                error_msg = f"Unknown HA interface: {interface.value}"
                _debug_log(correlation_id, scope="HA_GATEWAY",
                                 message="Unknown interface error",
                                 ha_interface=str(interface), interface_value=interface.value)
                raise ValueError(error_msg)

            module_name, func_name = _INTERFACE_ROUTERS[interface]

            # Lazy import with error handling
            try:
                _debug_log(correlation_id, scope="HA_GATEWAY",
                                 message="Importing module",
                                 module_name=module_name, ha_interface=str(interface))
                module = importlib.import_module(module_name)
            except ImportError as e:
                error_msg = f"Failed to import module '{module_name}' for {interface.value}: {e!s}"
                _debug_log(correlation_id, scope="HA_GATEWAY",
                                 message="Module import failed",
                                 module_name=module_name, ha_interface=str(interface),
                                 error_type=type(e).__name__, error=str(e))
                raise RuntimeError(error_msg) from e

            try:
                _debug_log(correlation_id, scope="HA_GATEWAY",
                                 message="Getting function",
                                 func_name=func_name, module_name=module_name)
                func = getattr(module, func_name)
            except AttributeError as e:
                error_msg = f"Function '{func_name}' not found in module '{module_name}' for {interface.value}: {e!s}"
                _debug_log(correlation_id, scope="HA_GATEWAY",
                                 message="Function not found",
                                 func_name=func_name, module_name=module_name,
                                 error_type=type(e).__name__, error=str(e))
                raise RuntimeError(error_msg) from e

            # Cache for fast path if operation is frequent
            if _fast_path_enabled and _operation_call_counts[(interface, operation)] >= 3:
                _fast_path_cache[(interface, operation)] = (func, module_name, func_name)
                _debug_log(correlation_id, scope="HA_GATEWAY",
                                 message="Added to fast path cache",
                                 ha_interface=str(interface), ha_operation=operation,
                                 call_count=_operation_call_counts[(interface, operation)])

            # Execute operation (HA interface routers always need operation parameter)
            _debug_log(correlation_id, scope="HA_GATEWAY",
                             message="Executing interface function",
                             func_name=func_name, ha_interface=str(interface), ha_operation=operation)

            try:
                result = func(operation, **kwargs)
                _debug_log(correlation_id, scope="HA_GATEWAY",
                                 message="ha_execute_operation completed",
                                 ha_interface=str(interface), ha_operation=operation, success=True)

                if _is_debug_mode() and start_time is not None:
                    import time
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    _debug_log(correlation_id, scope="HA_GATEWAY",
                             message="ha_execute_operation EXIT (fast path)",
                             ha_interface=str(interface), ha_operation=operation,
                             duration_ms=f"{duration_ms:.2f}", success=True)
                return result
            except (ValueError, TypeError, KeyError) as e:
                # Data validation error
                error_msg = f"Failed to execute {interface.value}.{operation}: {e!s}"
                _debug_log(correlation_id, scope="HA_GATEWAY",
                                 message="Interface function validation failed",
                                 ha_interface=str(interface), ha_operation=operation, func_name=func_name,
                                 error_type=type(e).__name__, error=str(e))
                raise RuntimeError(error_msg) from e
            except (ConnectionError, TimeoutError, OSError) as e:
                # Network or system error
                error_msg = f"Failed to execute {interface.value}.{operation}: {e!s}"
                _debug_log(correlation_id, scope="HA_GATEWAY",
                                 message="Interface function system error",
                                 ha_interface=str(interface), ha_operation=operation, func_name=func_name,
                                 error_type=type(e).__name__, error=str(e))
                raise RuntimeError(error_msg) from e
            except Exception as e:
                # Other unexpected errors
                error_msg = f"Failed to execute {interface.value}.{operation}: {e!s}"
                _debug_log(correlation_id, scope="HA_GATEWAY",
                                 message="Interface function execution failed",
                                 ha_interface=str(interface), ha_operation=operation, func_name=func_name,
                                 error_type=type(e).__name__, error=str(e))
                raise RuntimeError(error_msg) from e

        except Exception as e:
            # Catch any unexpected errors and ensure they're logged
            _debug_log(correlation_id, scope="HA_GATEWAY",
                             message="ha_execute_operation unexpected error",
                             ha_interface=str(interface), ha_operation=operation,
                             error_type=type(e).__name__, error=str(e))

            if _is_debug_mode() and start_time is not None:
                import time
                duration_ms = (time.perf_counter() - start_time) * 1000
                _debug_log(correlation_id, scope="HA_GATEWAY",
                         message="ha_execute_operation EXIT (error)",
                         ha_interface=str(interface), ha_operation=operation,
                         duration_ms=f"{duration_ms:.2f}", error=type(e).__name__)
            raise


# ===== STATISTICS =====

def get_ha_gateway_stats() -> dict[str, Any]:
    """Get HA gateway statistics."""
    return {
        "total_interfaces": len(_INTERFACE_ROUTERS),
        "fast_path_entries": len(_fast_path_cache),
        "fast_path_enabled": _fast_path_enabled,
        "operation_counts": dict(_operation_call_counts),
    }


def reset_ha_gateway_state() -> dict[str, Any]:
    """Reset HA gateway state including fast path cache and operation counts.

        Dict containing counts of cleared items

    """
    global _fast_path_cache, _operation_call_counts  # pylint: disable=W0603

    fast_path_count = len(_fast_path_cache)
    operation_count = len(_operation_call_counts)

    _fast_path_cache.clear()
    _operation_call_counts.clear()

    return {
        "fast_path_entries_cleared": fast_path_count,
        "operation_counts_cleared": operation_count,
        "state_reset": True,
    }


# ===== FAST PATH MANAGEMENT =====

def enable_ha_fast_path() -> None:
    """Enable fast path caching."""
    global _fast_path_enabled  # pylint: disable=W0603
    _fast_path_enabled = True


def disable_ha_fast_path() -> None:
    """Disable fast path caching."""
    global _fast_path_enabled  # pylint: disable=W0603
    _fast_path_enabled = False


def clear_ha_fast_path_cache() -> int:
    """Clear fast path cache and return number of entries cleared."""
    count = len(_fast_path_cache)
    _fast_path_cache.clear()
    return count


# ===== EXPORTS =====

__all__ = [
    "_INTERFACE_ROUTERS",
    "HAGatewayInterface",  # Re-exported from ha_gateway_enums
    "clear_ha_fast_path_cache",
    "disable_ha_fast_path",
    "enable_ha_fast_path",
    "get_ha_gateway_stats",
    "ha_execute_operation",
    "reset_ha_gateway_state",
]
