"""ha_timed_backup_core.py - Core Implementation for Timed Backup Interface

Version: 2026-03-18_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.home_assistant.ha_gateway_convenience import (
    ha_generate_correlation_id,
    ha_log_error,
    ha_log_info,
)


def list_backups_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """List all timed backups.

    Args:
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - backups: list of backup info
            - count: int
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "list_backups",
        }

    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message="Listing timed backups",
        corr_id=corr_id,
    )

    try:
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            command_type="backup/info",
            ha_config=ha_config,
            correlation_id=corr_id,
        )

        if result.get("success"):
            backups = result.get("result", {}).get("backups", [])
            return {
                "success": True,
                "backups": backups,
                "count": len(backups),
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to list backups"),
            "correlation_id": corr_id,
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        ha_log_error(
            message="Failed to list backups (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {str(e)}",
            "correlation_id": corr_id,
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to list backups (network error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {str(e)}",
            "correlation_id": corr_id,
        }
    except (RuntimeError, MemoryError):
        ha_log_error(
            message="Failed to list backups (runtime error)",
            corr_id=corr_id,
        )
        return {
            "success": False,
            "error_code": "RUNTIME_ERROR",
            "error_message": "Runtime error occurred",
            "correlation_id": corr_id,
        }


def create_backup_impl(
    name: Optional[str] = None,
    include_database: Optional[bool] = None,
    include_config: Optional[bool] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Create a timed backup.

    Args:
        name: Backup name
        include_database: Include database in backup
        include_config: Include configuration in backup
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - backup_id: str
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "create_backup",
        }

    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message=f"Creating timed backup: {name}",
        corr_id=corr_id,
    )

    try:
        backup_data = {}

        if name:
            backup_data["name"] = name
        if include_database is not None:
            backup_data["include_database"] = include_database
        if include_config is not None:
            backup_data["include_config"] = include_config

        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            command_type="backup/new",
            ha_config=ha_config,
            backup_data=backup_data,
            correlation_id=corr_id,
        )

        if result.get("success"):
            backup_info = result.get("result", {})
            return {
                "success": True,
                "backup_id": backup_info.get("slug", ""),
                "message": "Backup created successfully",
                "backup_info": backup_info,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to create backup"),
            "correlation_id": corr_id,
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        ha_log_error(
            message="Failed to create backup (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {str(e)}",
            "correlation_id": corr_id,
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to create backup (network error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {str(e)}",
            "correlation_id": corr_id,
        }
    except (RuntimeError, MemoryError):
        ha_log_error(
            message="Failed to create backup (runtime error)",
            corr_id=corr_id,
        )
        return {
            "success": False,
            "error_code": "RUNTIME_ERROR",
            "error_message": "Runtime error occurred",
            "correlation_id": corr_id,
        }


def restore_backup_impl(
    backup_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Restore a timed backup.

    Args:
        backup_id: Backup ID to restore
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not backup_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "backup_id is required",
        }

    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "restore_backup",
        }

    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message=f"Restoring backup: {backup_id}",
        corr_id=corr_id,
    )

    try:
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            command_type="backup/restore",
            ha_config=ha_config,
            backup_id=backup_id,
            correlation_id=corr_id,
        )

        if result.get("success"):
            return {
                "success": True,
                "message": f"Backup {backup_id} restored successfully",
                "backup_id": backup_id,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to restore backup"),
            "correlation_id": corr_id,
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        ha_log_error(
            message="Failed to restore backup (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {str(e)}",
            "correlation_id": corr_id,
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to restore backup (network error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {str(e)}",
            "correlation_id": corr_id,
        }
    except (RuntimeError, MemoryError):
        ha_log_error(
            message="Failed to restore backup (runtime error)",
            corr_id=corr_id,
        )
        return {
            "success": False,
            "error_code": "RUNTIME_ERROR",
            "error_message": "Runtime error occurred",
            "correlation_id": corr_id,
        }


def delete_backup_impl(
    backup_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **_kwargs
) -> dict[str, Any]:
    """Delete a timed backup.

    Args:
        backup_id: Backup ID to delete
        ha_config: Home Assistant configuration dict with url and token
        correlation_id: Correlation ID for tracking
        **kwargs: Additional parameters

    Returns:
        dict with:
            - success: bool
            - message: str
            - error_code: str (if error)
            - error_message: str (if error)
    """
    if not backup_id:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "backup_id is required",
        }

    if ha_config is None:
        return {
            "success": False,
            "error_code": "CONFIG_REQUIRED",
            "error_message": "Home Assistant configuration (ha_config) is required",
            "operation": "delete_backup",
        }

    corr_id = correlation_id or ha_generate_correlation_id()

    ha_log_info(
        message=f"Deleting backup: {backup_id}",
        corr_id=corr_id,
    )

    try:
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            "call_ws_command",
            command_type="backup/delete",
            ha_config=ha_config,
            backup_id=backup_id,
            correlation_id=corr_id,
        )

        if result.get("success"):
            return {
                "success": True,
                "message": f"Backup {backup_id} deleted successfully",
                "backup_id": backup_id,
                "correlation_id": corr_id,
            }
        return {
            "success": False,
            "error_message": result.get("error_message", "Failed to delete backup"),
            "correlation_id": corr_id,
        }

    except (ValueError, TypeError, KeyError, AttributeError) as e:
        ha_log_error(
            message="Failed to delete backup (validation error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "error_message": f"Validation error: {str(e)}",
            "correlation_id": corr_id,
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        ha_log_error(
            message="Failed to delete backup (network error)",
            corr_id=corr_id,
            error=str(e),
        )
        return {
            "success": False,
            "error_code": "NETWORK_ERROR",
            "error_message": f"Network error: {str(e)}",
            "correlation_id": corr_id,
        }
    except (RuntimeError, MemoryError):
        ha_log_error(
            message="Failed to delete backup (runtime error)",
            corr_id=corr_id,
        )
        return {
            "success": False,
            "error_code": "RUNTIME_ERROR",
            "error_message": "Runtime error occurred",
            "correlation_id": corr_id,
        }
