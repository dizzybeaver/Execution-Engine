# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-25 - Implemented secure Alexa device operations with HA-SUGA gateway calls


"""ha_alexa_devices_core.py - Alexa Devices Core Implementation

Version: 2026-03-25_2
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0

This module provides core implementation functions for Alexa device operations
through Home Assistant's Alexa Media Player integration.
"""

from collections.abc import Sequence
from typing import Any

from lee.lee_security import InputSanitizer, SanitizeLevel


def send_text_command_impl(**kwargs: Any) -> dict[str, Any]:
    """Send text-to-speech command to Alexa device via Home Assistant.

    This function sends TTS commands to Alexa devices through HA's notify service.
    Requires alexa_media component to be configured in Home Assistant.

    Args:
        **kwargs: Command parameters including:
            - device_id: Target device identifier (str, required, non-empty)
            - text: Text to speak (str, required, non-empty, max 10000 chars)
            - corr_id: Correlation ID for tracking

    Returns:
        Response dictionary with status and result

    Raises:
        ValueError: If required parameters missing, invalid types, or unsafe input

    Example:
        >>> send_text_command_impl(device_id='media_player.echo_living_room', text='Hello home')
        {'status': 'success', 'device_id': 'media_player.echo_living_room', 'result': 'TTS sent'}
    """
    device_id = kwargs.get("device_id")
    text = kwargs.get("text")

    # Validate types
    if not isinstance(device_id, str) or not device_id.strip():
        raise ValueError("device_id must be a non-empty string")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")

    # Validate length
    if len(text) > 10000:
        raise ValueError("text exceeds maximum length of 10000 characters")

    # Sanitize input
    sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
    sanitized = sanitizer.sanitize(text)

    # Check for threats
    if not sanitized.is_safe:
        threat_count = len(sanitized.threats)
        raise ValueError(
            f"Unsafe text detected: {threat_count} threat(s) found. "
            f"Use InputSanitizer to review threats."
        )

    # Import HA gateway dynamically to avoid import cycles
    try:
        from lee.home_assistant import ha_gateway  # pylint: disable=import-outside-toplevel
        from lee.home_assistant.ha_gateway_enums import HAGatewayInterface  # pylint: disable=import-outside-toplevel

        # Call Home Assistant's notify.alexa_media service through DEVICES interface
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            'call_service',
            domain='notify',
            service='alexa_media',
            service_data={
                'entity_id': device_id,
                'message': sanitized.sanitized
            },
            corr_id=kwargs.get('corr_id')
        )

        return {
            "status": "success",
            "device_id": device_id,
            "result": "TTS sent",
            "ha_response": result
        }

    except (ImportError, AttributeError) as e:
        # HA gateway import error
        import os  # pylint: disable=import-outside-toplevel
        if os.environ.get('LEE_SIMULATION_MODE', 'false').lower() == 'true':
            return {
                "status": "simulated",
                "device_id": device_id,
                "text": sanitized.sanitized,
                "result": "TTS sent (simulated - HA gateway unavailable)",
                "error": f"HA gateway error: {e}"
            }
        else:
            raise
    except Exception as e:  # pylint: disable=broad-except
        # Check if simulation mode is enabled (for testing only)
        import os  # pylint: disable=import-outside-toplevel
        if os.environ.get('LEE_SIMULATION_MODE', 'false').lower() == 'true':
            return {
                "status": "simulated",
                "device_id": device_id,
                "text": sanitized.sanitized,
                "result": "TTS sent (simulated - HA gateway unavailable)",
                "error": str(e)
            }
        else:
            # Production: fail fast and propagate error
            raise


def send_sound_impl(**kwargs: Any) -> dict[str, Any]:
    """Send sound/notification to Alexa device via Home Assistant.

    This function plays sound effects or notification sounds on Alexa devices
    through HA's alexa_media component.

    Args:
        **kwargs: Sound parameters including:
            - device_id: Target device identifier (str, required, non-empty)
            - sound: Sound identifier or URL (str, required, non-empty, max 500 chars)
            - corr_id: Correlation ID for tracking

    Returns:
        Response dictionary with status and result

    Raises:
        ValueError: If required parameters missing, invalid types, or unsafe input

    Example:
        >>> send_sound_impl(device_id='media_player.echo_kitchen', sound='doorbell')
        {'status': 'success', 'device_id': 'media_player.echo_kitchen', 'result': 'Sound sent'}
    """
    device_id = kwargs.get("device_id")
    sound = kwargs.get("sound")

    # Validate types
    if not isinstance(device_id, str) or not device_id.strip():
        raise ValueError("device_id must be a non-empty string")
    if not isinstance(sound, str) or not sound.strip():
        raise ValueError("sound must be a non-empty string")

    # Validate length
    if len(sound) > 500:
        raise ValueError("sound exceeds maximum length of 500 characters")

    # Sanitize input
    sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
    sanitized = sanitizer.sanitize(sound)

    # Check for threats
    if not sanitized.is_safe:
        threat_count = len(sanitized.threats)
        raise ValueError(
            f"Unsafe sound detected: {threat_count} threat(s) found. "
            f"Use InputSanitizer to review threats."
        )

    # Import HA gateway dynamically to avoid import cycles
    try:
        from lee.home_assistant import ha_gateway  # pylint: disable=import-outside-toplevel
        from lee.home_assistant.ha_gateway_enums import HAGatewayInterface  # pylint: disable=import-outside-toplevel

        # Call Home Assistant's alexa_media play_sound service through DEVICES interface
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            'call_service',
            domain='media_player',
            service='play_media',
            service_data={
                'entity_id': device_id,
                'media_content_id': sanitized.sanitized,
                'media_content_type': 'sound'
            },
            corr_id=kwargs.get('corr_id')
        )

        return {
            "status": "success",
            "device_id": device_id,
            "result": "Sound sent",
            "ha_response": result
        }

    except (ImportError, AttributeError) as e:
        # HA gateway import error
        return {
            "status": "simulated",
            "device_id": device_id,
            "sound": sanitized.sanitized,
            "result": "Sound sent (simulated - HA gateway unavailable)",
            "error": f"HA gateway error: {e}"
        }
    except Exception as e:  # pylint: disable=broad-except
        # If HA gateway unavailable, return simulated response for testing
        return {
            "status": "simulated",
            "device_id": device_id,
            "sound": sanitized.sanitized,
            "result": "Sound sent (simulated - HA gateway unavailable)",
            "error": str(e)
        }


def send_info_skill_impl(**kwargs: Any) -> dict[str, Any]:  # pylint: disable=too-many-locals,too-many-branches
    """Send Alexa info skill command to device via Home Assistant.

    This function triggers Alexa info skills (Flash Briefing, weather, traffic, etc.)
    through HA's alexa_media component.

    Args:
        **kwargs: Info skill parameters including:
            - device_id: Target device identifier (str, required, non-empty)
            - skill: Skill identifier (str, required, non-empty, max 100 chars)
            - data: Additional skill data (dict, optional)
            - corr_id: Correlation ID for tracking

    Returns:
        Response dictionary with status and result

    Raises:
        ValueError: If required parameters missing, invalid types, or unsafe input

    Example:
        >>> send_info_skill_impl(device_id='media_player.echo_bedroom', skill='weather')
        {'status': 'success', 'device_id': 'media_player.echo_bedroom', 'result': 'Skill triggered'}
    """
    device_id = kwargs.get("device_id")
    skill = kwargs.get("skill")
    data = kwargs.get("data", {})

    # Validate types
    if not isinstance(device_id, str) or not device_id.strip():
        raise ValueError("device_id must be a non-empty string")
    if not isinstance(skill, str) or not skill.strip():
        raise ValueError("skill must be a non-empty string")
    if not isinstance(data, dict):
        raise ValueError("data must be a dictionary")

    # Validate length
    if len(skill) > 100:
        raise ValueError("skill exceeds maximum length of 100 characters")

    # Sanitize input
    sanitizer = InputSanitizer(level=SanitizeLevel.STRICT)
    sanitized_skill = sanitizer.sanitize(skill)

    # Check for threats
    if not sanitized_skill.is_safe:
        threat_count = len(sanitized_skill.threats)
        raise ValueError(
            f"Unsafe skill detected: {threat_count} threat(s) found. "
            f"Use InputSanitizer to review threats."
        )

    # Import HA gateway dynamically to avoid import cycles
    try:
        from lee.home_assistant import ha_gateway  # pylint: disable=import-outside-toplevel
        from lee.home_assistant.ha_gateway_enums import HAGatewayInterface  # pylint: disable=import-outside-toplevel

        # Build service data
        service_data = {
            'entity_id': device_id,
            'skill': sanitized_skill.sanitized
        }

        # Add optional data if provided
        if data:
            # Sanitize data values
            sanitized_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    sanitized_value = sanitizer.sanitize(value)
                    if sanitized_value.is_safe:
                        sanitized_data[key] = sanitized_value.sanitized
                    else:
                        raise ValueError(f"Unsafe data in key '{key}'")
                else:
                    sanitized_data[key] = value
            service_data.update(sanitized_data)

        # Call Home Assistant's alexa_media trigger_skill service through DEVICES interface
        result = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            'call_service',
            domain='media_player',
            service='play_media',
            service_data=service_data,
            corr_id=kwargs.get('corr_id')
        )

        return {
            "status": "success",
            "device_id": device_id,
            "skill": sanitized_skill.sanitized,
            "result": "Skill triggered",
            "ha_response": result
        }

    except (ImportError, AttributeError) as e:
        # HA gateway import error
        return {
            "status": "simulated",
            "device_id": device_id,
            "skill": sanitized_skill.sanitized,
            "data": data,
            "result": "Skill triggered (simulated - HA gateway unavailable)",
            "error": f"HA gateway error: {e}"
        }
    except Exception as e:  # pylint: disable=broad-except
        # If HA gateway unavailable, return simulated response for testing
        return {
            "status": "simulated",
            "device_id": device_id,
            "skill": sanitized_skill.sanitized,
            "data": data,
            "result": "Skill triggered (simulated - HA gateway unavailable)",
            "error": str(e)
        }


class AlexaDevicesCore:
    """Alexa Devices Core - Wrapper for device operations.

    This class provides a clean API for Alexa device operations,
    wrapping the implementation functions.
    """

    def send_text_command(self, **kwargs: Any) -> dict[str, Any]:
        """Send text command to Alexa device.
        
        Args:
            **kwargs: Command parameters
            
        Returns:
            Response dictionary
        """
        return send_text_command_impl(**kwargs)

    def send_sound(self, **kwargs: Any) -> dict[str, Any]:
        """Send sound to Alexa device.
        
        Args:
            **kwargs: Sound parameters
            
        Returns:
            Response dictionary
        """
        return send_sound_impl(**kwargs)

    def send_info_skill(self, **kwargs: Any) -> dict[str, Any]:
        """Send info skill command to Alexa device.
        
        Args:
            **kwargs: Info skill parameters
            
        Returns:
            Response dictionary
        """
        return send_info_skill_impl(**kwargs)


def discover_alexa_devices_impl(**kwargs: Any) -> dict[str, Any]:
    """Discover all Alexa devices in Home Assistant.

    This function queries Home Assistant for all media_player entities
    that are part of the alexa_media integration.

    Args:
        **kwargs: Discovery parameters including:
            - corr_id: Correlation ID for tracking

    Returns:
        Response dictionary with list of discovered Alexa devices

    Example:
        >>> discover_alexa_devices_impl()
        {'status': 'success', 'devices': [...], 'count': 5}
    """
    try:
        from lee.home_assistant import ha_gateway  # pylint: disable=import-outside-toplevel
        from lee.home_assistant.ha_gateway_enums import HAGatewayInterface  # pylint: disable=import-outside-toplevel

        # Get all states from Home Assistant
        states = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            'get_states',
            corr_id=kwargs.get('corr_id')
        )

        # Filter for Alexa media player devices
        alexa_devices = []
        if states and isinstance(states, Sequence):
            for state in states:
                entity_id = state.get('entity_id', '')
                if entity_id.startswith('media_player.') and 'alexa' in entity_id.lower():
                    alexa_devices.append({
                        'entity_id': entity_id,
                        'state': state.get('state'),
                        'attributes': state.get('attributes', {}),
                        'friendly_name': state.get('attributes', {}).get('friendly_name', entity_id)
                    })

        return {
            "status": "success",
            "devices": alexa_devices,
            "count": len(alexa_devices)
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "status": "error",
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "devices": [],
            "count": 0
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "status": "error",
            "error": f"Data error: {e}",
            "error_code": "DATA_ERROR",
            "devices": [],
            "count": 0
        }
    except (ImportError, AttributeError) as e:
        return {
            "status": "error",
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR",
            "devices": [],
            "count": 0
        }
    except Exception:  # pylint: disable=broad-except
        return {
            "status": "error",
            "error": "Unknown error",
            "devices": [],
            "count": 0
        }


def get_alexa_device_state_impl(**kwargs: Any) -> dict[str, Any]:
    """Get current state of an Alexa device.

    Args:
        **kwargs: State query parameters including:
            - device_id: Target device identifier (str, required, non-empty)
            - corr_id: Correlation ID for tracking

    Returns:
        Response dictionary with device state

    Raises:
        ValueError: If required parameters missing

    Example:
        >>> get_alexa_device_state_impl(device_id='media_player.echo_living_room')
        {'status': 'success', 'state': 'playing', 'attributes': {...}}
    """
    device_id = kwargs.get("device_id")

    if not isinstance(device_id, str) or not device_id.strip():
        raise ValueError("device_id must be a non-empty string")

    try:
        from lee.home_assistant import ha_gateway  # pylint: disable=import-outside-toplevel
        from lee.home_assistant.ha_gateway_enums import HAGatewayInterface  # pylint: disable=import-outside-toplevel

        # Get specific device state
        state = ha_gateway.ha_execute_operation(
            HAGatewayInterface.DEVICES,
            'get_state',
            entity_id=device_id,
            corr_id=kwargs.get('corr_id')
        )

        return {
            "status": "success",
            "device_id": device_id,
            "state": state
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "status": "error",
            "device_id": device_id,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "state": None
        }
    except (ValueError, TypeError, KeyError) as e:
        return {
            "status": "error",
            "device_id": device_id,
            "error": f"Data error: {e}",
            "error_code": "DATA_ERROR",
            "state": None
        }
    except (ImportError, AttributeError) as e:
        return {
            "status": "error",
            "device_id": device_id,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR",
            "state": None
        }
    except Exception:  # pylint: disable=broad-except
        return {
            "status": "error",
            "device_id": device_id,
            "error": "Unknown error",
            "state": None
        }


__all__ = [
    "AlexaDevicesCore",
    "send_text_command_impl",
    "send_sound_impl",
    "send_info_skill_impl",
    "discover_alexa_devices_impl",
    "get_alexa_device_state_impl",
]
