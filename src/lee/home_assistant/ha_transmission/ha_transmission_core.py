"""ha_transmission_core.py - BitTorrent Client Core Implementation

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""


from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface


def add_torrent_impl(  # pylint: disable=R0913,R0917
    entry_id=None,
    torrent=None,
    download_path=None,
    labels=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Add torrent to Transmission.

    Args:
        entry_id: Transmission config entry ID
        torrent: Torrent URL or magnet link (required)
        download_path: Download directory path
        labels: Comma-separated labels (e.g., "Notify,Remove")
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entry_id or not torrent:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entry_id and torrent are required",
        }

    service_data = {"entry_id": entry_id, "torrent": torrent}
    if download_path:
        service_data["download_path"] = download_path
    if labels:
        service_data["labels"] = labels

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="transmission",
        service="add_torrent",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def get_torrents_impl(entry_id=None, torrent_filter=None, ha_config=None, correlation_id=None, **kwargs):
    """Get torrents from Transmission.

    Args:
        entry_id: Transmission config entry ID
        torrent_filter: Filter type (all, active, started, paused, completed)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entry_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entry_id is required",
        }

    service_data = {"entry_id": entry_id}
    if torrent_filter:
        service_data["torrent_filter"] = torrent_filter

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="transmission",
        service="get_torrents",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def remove_torrent_impl(
    entry_id=None,
    torrent_id=None,
    delete_data=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Remove torrent from Transmission.

    Args:
        entry_id: Transmission config entry ID
        torrent_id: Torrent ID to remove
        delete_data: Delete downloaded data (default: false)
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entry_id or not torrent_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entry_id and torrent_id are required",
        }

    service_data = {"entry_id": entry_id, "id": torrent_id}
    if delete_data is not None:
        service_data["delete_data"] = delete_data

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="transmission",
        service="remove_torrent",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def start_torrent_impl(
    entry_id=None,
    torrent_id=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Start torrent in Transmission.

    Args:
        entry_id: Transmission config entry ID
        torrent_id: Torrent ID to start
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entry_id or not torrent_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entry_id and torrent_id are required",
        }

    service_data = {"entry_id": entry_id, "id": torrent_id}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="transmission",
        service="start_torrent",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result


def stop_torrent_impl(
    entry_id=None,
    torrent_id=None,
    ha_config=None,
    correlation_id=None,
    **kwargs
):
    """Stop torrent in Transmission.

    Args:
        entry_id: Transmission config entry ID
        torrent_id: Torrent ID to stop
        ha_config: HA configuration (optional, auto-loaded)
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        Operation result dictionary
    """
    if not entry_id or not torrent_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entry_id and torrent_id are required",
        }

    service_data = {"entry_id": entry_id, "id": torrent_id}

    result = ha_gateway.ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="transmission",
        service="stop_torrent",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id,
        **kwargs,
    )
    return result
