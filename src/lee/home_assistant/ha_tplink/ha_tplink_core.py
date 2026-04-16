"""ha_tplink_core.py - TP-Link Kasa Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def sequence_effect_impl(  # pylint: disable=R0913,R0917
    entity_id=None,
    sequence=None,
    segments=None,
    brightness=None,
    duration=None,
    repeat_times=None,
    transition=None,
    spread=None,
    direction=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Run TP-Link sequence effect on light.

    Args:
        entity_id: TP-Link light entity ID
        sequence: Color sequence list (required)
        segments: Light segments to apply effect (default: 0)
        brightness: Effect brightness 1-100% (default: 100)
        duration: Effect duration 0-5000ms (default: 0)
        repeat_times: Number of repeats 0-10 (default: 0)
        transition: Transition time 0-6000ms (default: 0)
        spread: Spread value 0-16 (default: 0)
        direction: Direction 1-4 (default: 4)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id or not sequence:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and sequence are required",
        }

    service_data = {"entity_id": entity_id, "sequence": sequence}
    if segments is not None:
        service_data["segments"] = segments
    if brightness is not None:
        service_data["brightness"] = brightness
    if duration is not None:
        service_data["duration"] = duration
    if repeat_times is not None:
        service_data["repeat_times"] = repeat_times
    if transition is not None:
        service_data["transition"] = transition
    if spread is not None:
        service_data["spread"] = spread
    if direction is not None:
        service_data["direction"] = direction

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="tplink",
        service="sequence_effect",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def random_effect_impl(  # pylint: disable=R0913,R0914,R0917
    entity_id=None,
    init_states=None,
    backgrounds=None,
    segments=None,
    brightness=None,
    duration=None,
    transition=None,
    fadeoff=None,
    hue_range=None,
    saturation_range=None,
    brightness_range=None,
    transition_range=None,
    random_seed=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Run TP-Link random effect on light.

    Args:
        entity_id: TP-Link light entity ID
        init_states: Initial RGB color state [R, G, B] (required)
        backgrounds: Background color list
        segments: Light segments to apply effect (default: 0)
        brightness: Effect brightness 1-100% (default: 100)
        duration: Effect duration 0-5000ms (default: 0)
        transition: Transition time 0-6000ms (default: 0)
        fadeoff: Fadeoff time 0-3000ms (default: 0)
        hue_range: Hue range [min, max]
        saturation_range: Saturation range [min, max]
        brightness_range: Brightness range [min, max]
        transition_range: Transition range [min, max]
        random_seed: Random seed 1-600 (default: 100)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entity_id or not init_states:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id and init_states are required",
        }

    service_data = {"entity_id": entity_id, "init_states": init_states}
    if backgrounds is not None:
        service_data["backgrounds"] = backgrounds
    if segments is not None:
        service_data["segments"] = segments
    if brightness is not None:
        service_data["brightness"] = brightness
    if duration is not None:
        service_data["duration"] = duration
    if transition is not None:
        service_data["transition"] = transition
    if fadeoff is not None:
        service_data["fadeoff"] = fadeoff
    if hue_range is not None:
        service_data["hue_range"] = hue_range
    if saturation_range is not None:
        service_data["saturation_range"] = saturation_range
    if brightness_range is not None:
        service_data["brightness_range"] = brightness_range
    if transition_range is not None:
        service_data["transition_range"] = transition_range
    if random_seed is not None:
        service_data["random_seed"] = random_seed

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="tplink",
        service="random_effect",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
