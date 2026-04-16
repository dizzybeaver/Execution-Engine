"""ha_imap_core.py - IMAP Email Interface Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation
from lee.home_assistant.utils import missing_parameter


def seen_impl(
    entry=None, uid=None, seen=None, ha_config=None, correlation_id=None, **kwargs
):
    """Mark email as seen.

    Args:
        entry: IMAP config entry (required)
        uid: Email UID (required)
        seen: Seen status (optional)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entry or not uid:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entry and uid are required",
        }

    service_data = {"entry": entry, "uid": uid}

    if seen is not None:
        service_data["seen"] = seen

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="imap",
            service="seen",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id,
        )

        return result

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e}",
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error: {e}",
        }


def move_impl(
    entry=None,
    uid=None,
    seen=None,
    target_folder=None,
    ha_config=None,
    correlation_id=None,
    **kwargs,
):
    """Move email to folder.

    Args:
        entry: IMAP config entry (required)
        uid: Email UID (required)
        seen: Mark as seen (optional)
        target_folder: Target folder (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entry or not uid or not target_folder:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entry, uid, and target_folder are required",
        }

    service_data = {"entry": entry, "uid": uid, "target_folder": target_folder}

    if seen is not None:
        service_data["seen"] = seen

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="imap",
            service="move",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id,
        )

        return result

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e}",
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error: {e}",
        }


def delete_impl(entry=None, uid=None, ha_config=None, correlation_id=None, **kwargs):
    """Delete email.

    Args:
        entry: IMAP config entry (required)
        uid: Email UID (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entry or not uid:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entry and uid are required",
        }

    service_data = {"entry": entry, "uid": uid}

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="imap",
            service="delete",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id,
        )

        return result

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e}",
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error: {e}",
        }


def fetch_impl(entry=None, ha_config=None, correlation_id=None, **kwargs):
    """Fetch email.

    Args:
        entry: IMAP config entry (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entry:
        return missing_parameter("entry")

    service_data = {"entry": entry}

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="imap",
            service="fetch",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id,
        )

        return result

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e}",
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error: {e}",
        }


def fetch_part_impl(
    entry=None, uid=None, part=None, ha_config=None, correlation_id=None, **kwargs
):
    """Fetch email part.

    Args:
        entry: IMAP config entry (required)
        uid: Email UID (required)
        part: Part number (required)
        ha_config: Home Assistant configuration
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Result dictionary with success status
    """
    if not entry or not uid or not part:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entry, uid, and part are required",
        }

    service_data = {"entry": entry, "uid": uid, "part": part}

    try:
        result = ha_execute_operation(
            HAGatewayInterface.DEVICES,
            "call_service",
            domain="imap",
            service="fetch_part",
            service_data=service_data,
            ha_config=ha_config,
            correlation_id=correlation_id,
        )

        return result

    except (ConnectionError, TimeoutError, OSError) as e:
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {e}",
        }
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        return {
            "success": False,
            "error_code": "DATA_ERROR",
            "error_message": f"Data error: {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXCEPTION",
            "error_message": f"Unexpected error: {e}",
        }
