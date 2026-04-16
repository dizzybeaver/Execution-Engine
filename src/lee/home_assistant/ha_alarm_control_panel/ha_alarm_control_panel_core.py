# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-04 - Refactor to use HABaseDevice base class

"""ha_alarm_control_panel_core.py

Core implementations for Home Assistant Alarm Control Panel interface.

Provides alarm control panel operations including arming (away, home, night,
custom bypass), disarming, and triggering. All operations use service calls
through the Home Assistant HTTP API.
"""

from typing import Any, Optional

from lee.home_assistant.ha_base_device import HABaseDevice, HADeviceMixin
from lee.home_assistant.ha_gateway_convenience import (
    ha_generate_correlation_id,
    ha_log_error,
)


def list_alarm_control_panels_impl(oauth_token: str = None, **kwargs) -> dict[str, Any]:  # pylint: disable=too-many-return-statements
    """List all alarm control panel entities.

    Args:
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Dict with success status and list of alarm control panels
    """
    try:
        # Use base class methods for config resolution and validation
        ha_url, ha_token, config_error = HABaseDevice.resolve_ha_config(oauth_token, **kwargs)
        if config_error:
            return config_error

        validation_error = HABaseDevice.validate_ha_config(ha_url, ha_token)
        if validation_error:
            return validation_error

        # Use base class method to create HTTP client
        with HABaseDevice.create_http_client(ha_url, ha_token) as ha_http:
            all_states = ha_http.get_states()
            alarm_panels = HADeviceMixin.filter_entities_by_domain(all_states, "alarm_control_panel")

        return {
            "success": True,
            "alarm_panels": alarm_panels,
            "count": len(alarm_panels)
        }

    except (ConnectionError, TimeoutError, OSError) as e:
        return HABaseDevice.handle_network_error("list_alarm_control_panels", e)
    except (ValueError, TypeError, KeyError) as e:
        return HABaseDevice.handle_validation_error("list_alarm_control_panels", e)
    except (ImportError, AttributeError) as e:
        return HABaseDevice.handle_config_error("list_alarm_control_panels", e)
    except Exception as e:
        return HABaseDevice.handle_generic_error("list_alarm_control_panels", e)


def _validate_alarm_code(code: str) -> tuple[bool, Optional[str]]:
    """Validate alarm code parameter for security.

    Args:
        code: Security code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not code:
        return True, None

    if not isinstance(code, str):
        return False, f"Code must be string, got {type(code).__name__}"

    if len(code) > 64:
        return False, "Code too long (max 64 characters)"

    if len(code) < 4:
        return False, "Code too short (min 4 characters)"

    # Only allow alphanumeric codes (no special characters that could be injection vectors)
    import re  # pylint: disable=import-outside-toplevel
    if not re.match(r'^[a-zA-Z0-9]+$', code):
        return False, "Code contains invalid characters (only alphanumeric allowed)"

    return True, None


def _validate_alarm_entity_id(entity_id: str) -> tuple[bool, Optional[str]]:
    """Validate alarm entity_id parameter for security.

    Args:
        entity_id: Alarm entity ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not entity_id:
        return False, "Entity ID cannot be empty"

    if not isinstance(entity_id, str):
        return False, f"Entity ID must be string, got {type(entity_id).__name__}"

    if len(entity_id) > 255:
        return False, "Entity ID too long (max 255 characters)"

    # Check entity_id format: alarm_control_panel.*
    import re  # pylint: disable=import-outside-toplevel
    if not re.match(r'^alarm_control_panel\.[a-z0-9_]+$', entity_id):
        return False, f"Invalid alarm entity ID format: '{entity_id}'. Must be 'alarm_control_panel.xxx'"

    # Block path traversal attempts
    if '..' in entity_id or entity_id.startswith('/'):
        return False, "Path traversal detected in entity ID"

    return True, None


def alarm_arm_away_impl(entity_id: str, code: Optional[str] = None,  # pylint: disable=too-many-return-statements,too-many-locals,too-many-branches
                        oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Arm alarm control panel in away mode.

    Args:
        entity_id: Alarm control panel entity ID
        code: Optional security code
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Dict with success status
    """
    correlation_id = kwargs.get("correlation_id", ha_generate_correlation_id("arm_away"))

    # Validate entity_id for security
    is_valid, error = _validate_alarm_entity_id(entity_id)
    if not is_valid:
        return {
            "success": False,
            "error": f"Invalid entity ID: {error}",
            "error_code": "INVALID_ENTITY_ID",
            "correlation_id": correlation_id,
        }

    # Validate alarm code for security
    if code:
        is_valid, error = _validate_alarm_code(code)
        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid alarm code: {error}",
                "error_code": "INVALID_CODE",
                "correlation_id": correlation_id,
            }

    try:
        from urllib.parse import urlparse  # pylint: disable=import-outside-toplevel

        from lee.home_assistant.ha_config import get_ha_config  # pylint: disable=import-outside-toplevel
        from lee.home_assistant.http_client import HomeAssistantHTTP  # pylint: disable=import-outside-toplevel

        ha_url = kwargs.get("ha_url")
        ha_token = oauth_token or kwargs.get("ha_token")

        if not ha_url or not ha_token:
            config = get_ha_config()
            if config:
                if not ha_url and config.HOME_ASSISTANT_URL:
                    ha_url = config.HOME_ASSISTANT_URL
                if not ha_token and config.HOME_ASSISTANT_API_KEY:
                    ha_token = config.HOME_ASSISTANT_API_KEY

        if not ha_token:
            return {
                "success": False,
                "error": "No Home Assistant token provided",
                "error_code": "NO_TOKEN",
                "correlation_id": correlation_id,
            }

        if not ha_url:
            return {
                "success": False,
                "error": "No Home Assistant URL configured",
                "error_code": "NO_URL",
                "correlation_id": correlation_id,
            }

        parsed_url = urlparse(ha_url)
        with HomeAssistantHTTP(host=parsed_url.hostname, port=parsed_url.port,
                             token=ha_token, use_ssl=parsed_url.scheme == "https") as ha_http:
            service_data = {"entity_id": entity_id}
            if code:
                service_data["code"] = code

            ha_http.call_service("alarm_control_panel", "alarm_arm_away", service_data)

        return {"success": True, "correlation_id": correlation_id}

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_away network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": correlation_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_away validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": correlation_id,
        }
    except (ImportError, AttributeError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_away config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR",
            "correlation_id": correlation_id,
        }
    except Exception:  # pylint: disable=broad-except
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message="alarm_arm_away failed")
        return {
            "success": False,
            "error": "Unknown error",
            "error_code": "ARM_AWAY_ERROR",
            "correlation_id": correlation_id,
        }


def alarm_arm_home_impl(entity_id: str, code: Optional[str] = None,  # pylint: disable=too-many-return-statements,too-many-locals,too-many-branches
                        oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Arm alarm control panel in home mode.

    Args:
        entity_id: Alarm control panel entity ID
        code: Optional security code
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Dict with success status
    """
    correlation_id = kwargs.get("correlation_id", ha_generate_correlation_id("arm_home"))

    # Validate alarm code for security
    if code:
        is_valid, error = _validate_alarm_code(code)
        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid alarm code: {error}",
                "error_code": "INVALID_CODE",
                "correlation_id": correlation_id,
            }

    try:
        from urllib.parse import urlparse  # pylint: disable=import-outside-toplevel

        from lee.home_assistant.ha_config import get_ha_config  # pylint: disable=import-outside-toplevel
        from lee.home_assistant.http_client import HomeAssistantHTTP  # pylint: disable=import-outside-toplevel

        ha_url = kwargs.get("ha_url")
        ha_token = oauth_token or kwargs.get("ha_token")

        if not ha_url or not ha_token:
            config = get_ha_config()
            if config:
                if not ha_url and config.HOME_ASSISTANT_URL:
                    ha_url = config.HOME_ASSISTANT_URL
                if not ha_token and config.HOME_ASSISTANT_API_KEY:
                    ha_token = config.HOME_ASSISTANT_API_KEY

        if not ha_token:
            return {
                "success": False,
                "error": "No Home Assistant token provided",
                "error_code": "NO_TOKEN",
                "correlation_id": correlation_id,
            }

        if not ha_url:
            return {
                "success": False,
                "error": "No Home Assistant URL configured",
                "error_code": "NO_URL",
                "correlation_id": correlation_id,
            }

        parsed_url = urlparse(ha_url)
        with HomeAssistantHTTP(host=parsed_url.hostname, port=parsed_url.port,
                             token=ha_token, use_ssl=parsed_url.scheme == "https") as ha_http:
            service_data = {"entity_id": entity_id}
            if code:
                service_data["code"] = code

            ha_http.call_service("alarm_control_panel", "alarm_arm_home", service_data)

        return {"success": True, "correlation_id": correlation_id}

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_home network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": correlation_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_home validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": correlation_id,
        }
    except (ImportError, AttributeError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_home config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR",
            "correlation_id": correlation_id,
        }
    except Exception:  # pylint: disable=broad-except
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message="alarm_arm_home failed")
        return {
            "success": False,
            "error": "Unknown error",
            "error_code": "ARM_HOME_ERROR",
            "correlation_id": correlation_id,
        }


def alarm_arm_night_impl(entity_id: str, code: Optional[str] = None,  # pylint: disable=too-many-return-statements,too-many-locals,too-many-branches
                         oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Arm alarm control panel in night mode.

    Args:
        entity_id: Alarm control panel entity ID
        code: Optional security code
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Dict with success status
    """
    correlation_id = kwargs.get("correlation_id", ha_generate_correlation_id("arm_night"))

    # Validate alarm code for security
    if code:
        is_valid, error = _validate_alarm_code(code)
        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid alarm code: {error}",
                "error_code": "INVALID_CODE",
                "correlation_id": correlation_id,
            }

    try:
        from urllib.parse import urlparse  # pylint: disable=import-outside-toplevel

        from lee.home_assistant.ha_config import get_ha_config  # pylint: disable=import-outside-toplevel
        from lee.home_assistant.http_client import HomeAssistantHTTP  # pylint: disable=import-outside-toplevel

        ha_url = kwargs.get("ha_url")
        ha_token = oauth_token or kwargs.get("ha_token")

        if not ha_url or not ha_token:
            config = get_ha_config()
            if config:
                if not ha_url and config.HOME_ASSISTANT_URL:
                    ha_url = config.HOME_ASSISTANT_URL
                if not ha_token and config.HOME_ASSISTANT_API_KEY:
                    ha_token = config.HOME_ASSISTANT_API_KEY

        if not ha_token:
            return {
                "success": False,
                "error": "No Home Assistant token provided",
                "error_code": "NO_TOKEN",
                "correlation_id": correlation_id,
            }

        if not ha_url:
            return {
                "success": False,
                "error": "No Home Assistant URL configured",
                "error_code": "NO_URL",
                "correlation_id": correlation_id,
            }

        parsed_url = urlparse(ha_url)
        with HomeAssistantHTTP(host=parsed_url.hostname, port=parsed_url.port,
                             token=ha_token, use_ssl=parsed_url.scheme == "https") as ha_http:
            service_data = {"entity_id": entity_id}
            if code:
                service_data["code"] = code

            ha_http.call_service("alarm_control_panel", "alarm_arm_night", service_data)

        return {"success": True, "correlation_id": correlation_id}

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_night network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": correlation_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_night validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": correlation_id,
        }
    except (ImportError, AttributeError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_night config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR",
            "correlation_id": correlation_id,
        }
    except Exception:  # pylint: disable=broad-except
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message="alarm_arm_night failed")
        return {
            "success": False,
            "error": "Unknown error",
            "error_code": "ARM_NIGHT_ERROR",
            "correlation_id": correlation_id,
        }


def alarm_arm_custom_bypass_impl(entity_id: str, code: Optional[str] = None,  # pylint: disable=too-many-return-statements,too-many-locals,too-many-branches
                                  oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Arm alarm control panel in custom bypass mode.

    Args:
        entity_id: Alarm control panel entity ID
        code: Optional security code
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Dict with success status
    """
    correlation_id = kwargs.get("correlation_id", ha_generate_correlation_id("arm_custom"))

    # Validate alarm code for security
    if code:
        is_valid, error = _validate_alarm_code(code)
        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid alarm code: {error}",
                "error_code": "INVALID_CODE",
                "correlation_id": correlation_id,
            }

    try:
        from urllib.parse import urlparse  # pylint: disable=import-outside-toplevel

        from lee.home_assistant.ha_config import get_ha_config  # pylint: disable=import-outside-toplevel
        from lee.home_assistant.http_client import HomeAssistantHTTP  # pylint: disable=import-outside-toplevel

        ha_url = kwargs.get("ha_url")
        ha_token = oauth_token or kwargs.get("ha_token")

        if not ha_url or not ha_token:
            config = get_ha_config()
            if config:
                if not ha_url and config.HOME_ASSISTANT_URL:
                    ha_url = config.HOME_ASSISTANT_URL
                if not ha_token and config.HOME_ASSISTANT_API_KEY:
                    ha_token = config.HOME_ASSISTANT_API_KEY

        if not ha_token:
            return {
                "success": False,
                "error": "No Home Assistant token provided",
                "error_code": "NO_TOKEN",
                "correlation_id": correlation_id,
            }

        if not ha_url:
            return {
                "success": False,
                "error": "No Home Assistant URL configured",
                "error_code": "NO_URL",
                "correlation_id": correlation_id,
            }

        parsed_url = urlparse(ha_url)
        with HomeAssistantHTTP(host=parsed_url.hostname, port=parsed_url.port,
                             token=ha_token, use_ssl=parsed_url.scheme == "https") as ha_http:
            service_data = {"entity_id": entity_id}
            if code:
                service_data["code"] = code

            ha_http.call_service("alarm_control_panel", "alarm_arm_custom_bypass", service_data)

        return {"success": True, "correlation_id": correlation_id}

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_custom_bypass network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": correlation_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_custom_bypass validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": correlation_id,
        }
    except (ImportError, AttributeError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_arm_custom_bypass config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR",
            "correlation_id": correlation_id,
        }
    except Exception:  # pylint: disable=broad-except
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message="alarm_arm_custom_bypass failed")
        return {
            "success": False,
            "error": "Unknown error",
            "error_code": "ARM_CUSTOM_BYPASS_ERROR",
            "correlation_id": correlation_id,
        }


def alarm_disarm_impl(entity_id: str, code: Optional[str] = None,  # pylint: disable=too-many-return-statements,too-many-locals,too-many-branches
                      oauth_token: str = None, **kwargs) -> dict[str, Any]:
    """Disarm alarm control panel.

    Args:
        entity_id: Alarm control panel entity ID
        code: Optional security code
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Dict with success status
    """
    correlation_id = kwargs.get("correlation_id", ha_generate_correlation_id("disarm"))

    # Validate alarm code for security
    if code:
        is_valid, error = _validate_alarm_code(code)
        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid alarm code: {error}",
                "error_code": "INVALID_CODE",
                "correlation_id": correlation_id,
            }

    try:
        from urllib.parse import urlparse  # pylint: disable=import-outside-toplevel

        from lee.home_assistant.ha_config import get_ha_config  # pylint: disable=import-outside-toplevel
        from lee.home_assistant.http_client import HomeAssistantHTTP  # pylint: disable=import-outside-toplevel

        ha_url = kwargs.get("ha_url")
        ha_token = oauth_token or kwargs.get("ha_token")

        if not ha_url or not ha_token:
            config = get_ha_config()
            if config:
                if not ha_url and config.HOME_ASSISTANT_URL:
                    ha_url = config.HOME_ASSISTANT_URL
                if not ha_token and config.HOME_ASSISTANT_API_KEY:
                    ha_token = config.HOME_ASSISTANT_API_KEY

        if not ha_token:
            return {
                "success": False,
                "error": "No Home Assistant token provided",
                "error_code": "NO_TOKEN",
                "correlation_id": correlation_id,
            }

        if not ha_url:
            return {
                "success": False,
                "error": "No Home Assistant URL configured",
                "error_code": "NO_URL",
                "correlation_id": correlation_id,
            }

        parsed_url = urlparse(ha_url)
        with HomeAssistantHTTP(host=parsed_url.hostname, port=parsed_url.port,
                             token=ha_token, use_ssl=parsed_url.scheme == "https") as ha_http:
            service_data = {"entity_id": entity_id}
            if code:
                service_data["code"] = code

            ha_http.call_service("alarm_control_panel", "alarm_disarm", service_data)

        return {"success": True, "correlation_id": correlation_id}

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_disarm network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": correlation_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_disarm validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": correlation_id,
        }
    except (ImportError, AttributeError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_disarm config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR",
            "correlation_id": correlation_id,
        }
    except Exception:  # pylint: disable=broad-except
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message="alarm_disarm failed")
        return {
            "success": False,
            "error": "Unknown error",
            "error_code": "DISARM_ERROR",
            "correlation_id": correlation_id,
        }


def alarm_trigger_impl(entity_id: str, oauth_token: str = None,  # pylint: disable=too-many-return-statements
                       **kwargs) -> dict[str, Any]:
    """Trigger alarm control panel.

    Args:
        entity_id: Alarm control panel entity ID
        oauth_token: Home Assistant access token
        **kwargs: Additional parameters

    Returns:
        Dict with success status
    """
    correlation_id = kwargs.get("correlation_id", ha_generate_correlation_id("trigger"))

    try:
        from urllib.parse import urlparse  # pylint: disable=import-outside-toplevel

        from lee.home_assistant.ha_config import get_ha_config  # pylint: disable=import-outside-toplevel
        from lee.home_assistant.http_client import HomeAssistantHTTP  # pylint: disable=import-outside-toplevel

        ha_url = kwargs.get("ha_url")
        ha_token = oauth_token or kwargs.get("ha_token")

        if not ha_url or not ha_token:
            config = get_ha_config()
            if config:
                if not ha_url and config.HOME_ASSISTANT_URL:
                    ha_url = config.HOME_ASSISTANT_URL
                if not ha_token and config.HOME_ASSISTANT_API_KEY:
                    ha_token = config.HOME_ASSISTANT_API_KEY

        if not ha_token:
            return {
                "success": False,
                "error": "No Home Assistant token provided",
                "error_code": "NO_TOKEN",
                "correlation_id": correlation_id,
            }

        if not ha_url:
            return {
                "success": False,
                "error": "No Home Assistant URL configured",
                "error_code": "NO_URL",
                "correlation_id": correlation_id,
            }

        parsed_url = urlparse(ha_url)
        with HomeAssistantHTTP(host=parsed_url.hostname, port=parsed_url.port,
                             token=ha_token, use_ssl=parsed_url.scheme == "https") as ha_http:
            service_data = {"entity_id": entity_id}
            ha_http.call_service("alarm_control_panel", "alarm_trigger", service_data)

        return {"success": True, "correlation_id": correlation_id}

    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_trigger network error: {str(e)}")
        return {
            "success": False,
            "error": f"Network error: {e}",
            "error_code": "NETWORK_ERROR",
            "correlation_id": correlation_id,
        }
    except (ValueError, TypeError, KeyError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_trigger validation error: {str(e)}")
        return {
            "success": False,
            "error": f"Invalid data: {e}",
            "error_code": "VALIDATION_ERROR",
            "correlation_id": correlation_id,
        }
    except (ImportError, AttributeError) as e:
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message=f"alarm_trigger config error: {str(e)}")
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "error_code": "CONFIG_ERROR",
            "correlation_id": correlation_id,
        }
    except Exception:  # pylint: disable=broad-except
        ha_log_error(
                         corr_id=correlation_id, scope="ALARM_CONTROL_PANEL",
                         message="alarm_trigger failed")
        return {
            "success": False,
            "error": "Unknown error",
            "error_code": "TRIGGER_ERROR",
            "correlation_id": correlation_id,
        }
