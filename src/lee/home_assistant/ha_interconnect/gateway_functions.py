# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - Extract gateway convenience functions from ha_interconnect.py

"""gateway_functions.py - HA-SUGA Gateway Convenience Functions
Version: 2025-03-02_1
Purpose: Re-export HA-SUGA gateway functions with correlation IDs

This module provides convenience wrappers for HA-SUGA gateway functions.

Copyright 2025 Joseph Hersey
Licensed under Apache License, Version 2.0
"""

import os
import time
from typing import Any

from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_interconnect.utils import generate_ha_correlation_id, log_debug


def alexa_handle_discovery(event: dict[str, Any], _oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Handle Alexa device discovery via HA-SUGA."""
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    corr_id = kwargs.pop("correlation_id", None) or generate_ha_correlation_id()

    if debug_enabled:
        start_time = time.perf_counter()
        log_debug("alexa_handle_discovery ENTRY", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")
    log_debug(f"[{corr_id}] Handling discovery via HA-SUGA")
    result = ha_gateway.ha_alexa_handle_discovery(
        request=event,
        **kwargs,
    )

    if debug_enabled:
        duration_ms = (time.perf_counter() - start_time) * 1000
        device_count = len(result.get('payload', {}).get('endpoints', [])) if isinstance(result, dict) else 0
        log_debug(f"alexa_handle_discovery EXIT - device_count={device_count} duration_ms={duration_ms:.2f}", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")

    return result


def devices_call_service(domain: str, service: str, service_data: dict[str, Any] = None,
                        _oauth_token: str = None, **kwargs) -> Any:
    """Call Home Assistant service via HA-SUGA."""
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    corr_id = kwargs.pop("correlation_id", None) or generate_ha_correlation_id()

    if debug_enabled:
        start_time = time.perf_counter()
        entity_id = service_data.get('entity_id') if service_data else None
        log_debug(f"devices_call_service ENTRY - domain={domain} service={service} entity_id={entity_id}", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")
    log_debug(f"[{corr_id}] Calling HA service: {domain}.{service}")
    result = ha_gateway.ha_devices_call_service(
        domain=domain,
        service=service,
        service_data=service_data,
        **kwargs,
    )

    if debug_enabled:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_debug(f"devices_call_service EXIT - domain={domain} service={service} duration_ms={duration_ms:.2f}", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")

    return result


def devices_get_states(_oauth_token: str = None, **kwargs) -> list[dict[str, Any]]:
    """Get all device states from Home Assistant via HA-SUGA."""
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    corr_id = kwargs.pop("correlation_id", None) or generate_ha_correlation_id()

    if debug_enabled:
        start_time = time.perf_counter()
        log_debug("devices_get_states ENTRY", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")
    log_debug(f"[{corr_id}] Getting all HA states")
    result = ha_gateway.ha_devices_get_states(**kwargs)

    if debug_enabled:
        duration_ms = (time.perf_counter() - start_time) * 1000
        entity_count = len(result) if isinstance(result, list) else 0
        log_debug(f"devices_get_states EXIT - entity_count={entity_count} duration_ms={duration_ms:.2f}", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")

    return result


def devices_get_by_id(entity_id: str, _oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get device state by entity ID via HA-SUGA."""
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    corr_id = kwargs.pop("correlation_id", None) or generate_ha_correlation_id()

    if debug_enabled:
        start_time = time.perf_counter()
        log_debug(f"devices_get_by_id ENTRY - entity_id={entity_id}", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")
    log_debug(f"[{corr_id}] Getting HA entity: {entity_id}")
    result = ha_gateway.ha_devices_get_by_id(
        entity_id=entity_id,
        **kwargs,
    )

    if debug_enabled:
        duration_ms = (time.perf_counter() - start_time) * 1000
        state = result.get('state') if isinstance(result, dict) else None
        log_debug(f"devices_get_by_id EXIT - entity_id={entity_id} state={state} duration_ms={duration_ms:.2f}", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")

    return result


def assist_send_message(message: str, _oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Send message to Home Assistant Assist via HA-SUGA."""
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    corr_id = kwargs.pop("correlation_id", None) or generate_ha_correlation_id()

    if debug_enabled:
        start_time = time.perf_counter()
        msg_len = len(message)
        log_debug(f"assist_send_message ENTRY - message_length={msg_len}", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")
    log_debug(f"[{corr_id}] Sending Assist message")
    result = ha_gateway.ha_assist_send_message(
        message=message,
        **kwargs,
    )

    if debug_enabled:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_debug(f"assist_send_message EXIT - duration_ms={duration_ms:.2f}", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")

    return result


def config_get_ha_config(_oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Get Home Assistant configuration via HA-SUGA."""
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    corr_id = kwargs.pop("correlation_id", None) or generate_ha_correlation_id()

    if debug_enabled:
        start_time = time.perf_counter()
        log_debug("config_get_ha_config ENTRY", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")
    log_debug(f"[{corr_id}] Getting HA config")
    result = ha_gateway.ha_config_get_ha_config(**kwargs)

    if debug_enabled:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_debug(f"config_get_ha_config EXIT - duration_ms={duration_ms:.2f}", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")

    return result


def health_check_system(_oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Check HA-SUGA system health."""
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    corr_id = kwargs.pop("correlation_id", None) or generate_ha_correlation_id()

    if debug_enabled:
        start_time = time.perf_counter()
        log_debug("health_check_system ENTRY", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")
    log_debug(f"[{corr_id}] Checking HA system health")
    result = ha_gateway.ha_health_check_system(**kwargs)

    if debug_enabled:
        duration_ms = (time.perf_counter() - start_time) * 1000
        is_healthy = result.get('healthy') if isinstance(result, dict) else None
        log_debug(f"health_check_system EXIT - healthy={is_healthy} duration_ms={duration_ms:.2f}", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")

    return result


def devices_get_ha_entities(_oauth_token: str = None, **kwargs) -> list[dict[str, Any]]:
    """Get all Home Assistant entity configurations."""
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"

    corr_id = kwargs.pop("correlation_id", None) or generate_ha_correlation_id()

    if debug_enabled:
        start_time = time.perf_counter()
        log_debug("devices_get_ha_entities ENTRY", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")
    log_debug(f"[{corr_id}] Getting HA entities")
    result = ha_gateway.ha_config_get_ha_entities(**kwargs)

    if debug_enabled:
        duration_ms = (time.perf_counter() - start_time) * 1000
        entity_count = len(result) if isinstance(result, list) else 0
        log_debug(f"devices_get_ha_entities EXIT - entity_count={entity_count} duration_ms={duration_ms:.2f}", corr_id=corr_id, scope="GATEWAY_FUNCTIONS")

    return result


__all__ = [
    "alexa_handle_discovery",
    "devices_call_service",
    "devices_get_states",
    "devices_get_by_id",
    "assist_send_message",
    "config_get_ha_config",
    "health_check_system",
    "devices_get_ha_entities",
]
