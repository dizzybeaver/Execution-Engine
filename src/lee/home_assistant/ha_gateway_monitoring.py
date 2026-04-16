# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-01 - Extracted monitoring functions from ha_gateway.py

"""ha_gateway_monitoring.py - Monitoring Interfaces for HA Gateway
Version: 2026-04-01
Purpose: Camera, energy, backup, history, repairs, statistics, and logbook interfaces

This module contains functions for monitoring Home Assistant systems:
- Camera operations
- Energy management
- Backup management (standard and timed)
- Historical data
- Repairs system
- Statistics
- Logbook (human-readable events)

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Optional

# Core imports
from lee.home_assistant import ha_gateway
from lee.home_assistant.ha_gateway_enums import HAGatewayInterface

# ===== CAMERA INTERFACE =====

def ha_camera_list_cameras(**kwargs) -> list:
    """List all cameras through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "list_cameras", **kwargs)


def ha_camera_get_info(entity_id: str, **kwargs) -> dict:
    """Get camera information through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "get_camera_info", entity_id=entity_id, **kwargs)


def ha_camera_get_capabilities(entity_id: str, **kwargs) -> dict:
    """Get camera capabilities through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "get_camera_capabilities", entity_id=entity_id, **kwargs)


def ha_camera_take_snapshot(entity_id: str, **kwargs) -> dict:
    """Take camera snapshot through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "take_snapshot", entity_id=entity_id, **kwargs)


def ha_camera_get_stream_url(entity_id: str, **kwargs) -> dict:
    """Get camera stream URL through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.CAMERA, "get_camera_stream_url", entity_id=entity_id, **kwargs)


# ===== ENERGY INTERFACE =====

def ha_energy_get_preferences(**kwargs) -> dict:
    """Get energy preferences through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ENERGY, "get_energy_preferences", **kwargs)


def ha_energy_save_preferences(energy_sources: list = None, device_consumption: list = None, device_consumption_water: list = None, **kwargs) -> dict:
    """Save energy preferences through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ENERGY, "save_energy_preferences", energy_sources=energy_sources, device_consumption=device_consumption, device_consumption_water=device_consumption_water, **kwargs)


def ha_energy_get_info(**kwargs) -> dict:
    """Get energy information through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ENERGY, "get_energy_info", **kwargs)


def ha_energy_validate_config(**kwargs) -> dict:
    """Validate energy configuration through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ENERGY, "validate_energy_config", **kwargs)


def ha_energy_get_solar_forecast(**kwargs) -> dict:
    """Get solar forecast through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ENERGY, "get_solar_forecast", **kwargs)


def ha_energy_get_fossil_energy_consumption(start_time: str, end_time: str, energy_statistic_ids: list, co2_statistic_id: str, period: str = "hour", **kwargs) -> dict:
    """Get fossil fuel energy consumption through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.ENERGY, "get_fossil_energy_consumption", start_time=start_time, end_time=end_time, energy_statistic_ids=energy_statistic_ids, co2_statistic_id=co2_statistic_id, period=period, **kwargs)


# ===== BACKUP INTERFACE =====

def ha_backup_get_info(**kwargs) -> dict:
    """Get backup information through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BACKUP, "get_backup_info", **kwargs)


def ha_backup_get_details(backup_id: str, **kwargs) -> dict:
    """Get backup details through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BACKUP, "get_backup_details", backup_id=backup_id, **kwargs)


def ha_backup_create(name: str = None, include: list = None, exclude: list = None, **kwargs) -> dict:
    """Create backup through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BACKUP, "create_backup", name=name, include=include, exclude=exclude, **kwargs)


def ha_backup_delete(backup_id: str, **kwargs) -> dict:
    """Delete backup through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BACKUP, "delete_backup", backup_id=backup_id, **kwargs)


def ha_backup_restore(backup_id: str, **kwargs) -> dict:
    """Restore from backup through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.BACKUP, "restore_backup", backup_id=backup_id, **kwargs)


# ===== TIMED_BACKUP INTERFACE =====

def ha_timed_backup_list_backups(**kwargs) -> dict:
    """List timed backups through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TIMED_BACKUP, "list_backups", **kwargs)


def ha_timed_backup_create_backup(name: str = None, include_database: bool = None, include_config: bool = None, **kwargs) -> dict:
    """Create timed backup through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TIMED_BACKUP, "create_backup", name=name, include_database=include_database, include_config=include_config, **kwargs)


def ha_timed_backup_restore_backup(backup_id: str, **kwargs) -> dict:
    """Restore timed backup through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TIMED_BACKUP, "restore_backup", backup_id=backup_id, **kwargs)


def ha_timed_backup_delete_backup(backup_id: str, **kwargs) -> dict:
    """Delete timed backup through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.TIMED_BACKUP, "delete_backup", backup_id=backup_id, **kwargs)


# ===== HISTORY INTERFACE =====

def ha_history_get_during_period(start_time: str, entity_ids: list, end_time: str = None, include_start_time_state: bool = True, significant_changes_only: bool = True, minimal_response: bool = False, no_attributes: bool = False, **kwargs) -> dict:  # pylint: disable=too-many-arguments,too-many-positional-arguments
    """Get history during period through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.HISTORY, "get_history_during_period", start_time=start_time, entity_ids=entity_ids, end_time=end_time, include_start_time_state=include_start_time_state, significant_changes_only=significant_changes_only, minimal_response=minimal_response, no_attributes=no_attributes, **kwargs)


# ===== REPAIRS INTERFACE =====

def ha_repairs_list_issues(**kwargs) -> dict:
    """List repair issues through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REPAIRS, "list_issues", **kwargs)


def ha_repairs_get_issue_data(domain: str, issue_id: str, **kwargs) -> dict:
    """Get repair issue data through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REPAIRS, "get_issue_data", domain=domain, issue_id=issue_id, **kwargs)


def ha_repairs_ignore_issue(domain: str, issue_id: str, ignore: bool, **kwargs) -> dict:
    """Ignore/unignore repair issue through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.REPAIRS, "ignore_issue", domain=domain, issue_id=issue_id, ignore=ignore, **kwargs)


# ===== STATISTICS CONVENIENCE FUNCTIONS =====

def ha_statistics_list_statistic_ids(statistic_type: Optional[str] = None, **kwargs) -> dict:
    """List all available statistic IDs through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.STATISTICS, "list_statistic_ids", statistic_type=statistic_type, **kwargs)


def ha_statistics_get_statistic_during_period(statistic_id: str, start_time: str, end_time: Optional[str] = None, period: str = "hour", units: Optional[dict] = None, types: Optional[list] = None, **kwargs) -> dict:  # pylint: disable=too-many-arguments,too-many-positional-arguments
    """Get statistics for a single statistic_id during a time period through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.STATISTICS, "get_statistic_during_period", statistic_id=statistic_id, start_time=start_time, end_time=end_time, period=period, units=units, types=types, **kwargs)


def ha_statistics_get_statistics_during_period(statistic_ids: list, start_time: str, end_time: Optional[str] = None, period: str = "hour", units: Optional[dict] = None, types: Optional[list] = None, **kwargs) -> dict:  # pylint: disable=too-many-arguments,too-many-positional-arguments
    """Get statistics for multiple statistic_ids during a time period through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.STATISTICS, "get_statistics_during_period", statistic_ids=statistic_ids, start_time=start_time, end_time=end_time, period=period, units=units, types=types, **kwargs)


def ha_statistics_get_statistics_metadata(statistic_ids: Optional[list] = None, **kwargs) -> dict:
    """Get metadata for statistics through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.STATISTICS, "get_statistics_metadata", statistic_ids=statistic_ids, **kwargs)


def ha_statistics_update_statistics_metadata(statistic_id: str, unit_of_measurement: Optional[str] = None, has_mean: Optional[bool] = None, has_sum: Optional[bool] = None, **kwargs) -> dict:
    """Update metadata for a statistic through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.STATISTICS, "update_statistics_metadata", statistic_id=statistic_id, unit_of_measurement=unit_of_measurement, has_mean=has_mean, has_sum=has_sum, **kwargs)


def ha_statistics_change_statistics_unit(statistic_id: str, new_unit: str, **kwargs) -> dict:
    """Change the unit of a statistic through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.STATISTICS, "change_statistics_unit", statistic_id=statistic_id, new_unit=new_unit, **kwargs)


def ha_statistics_clear_statistics(statistic_id: str, **kwargs) -> dict:
    """Clear all statistics for a statistic_id through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.STATISTICS, "clear_statistics", statistic_id=statistic_id, **kwargs)


def ha_statistics_adjust_sum_statistics(statistic_id: str, start_time: str, end_time: str, adjustment: float, **kwargs) -> dict:
    """Adjust sum statistics for a period through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.STATISTICS, "adjust_sum_statistics", statistic_id=statistic_id, start_time=start_time, end_time=end_time, adjustment=adjustment, **kwargs)


def ha_statistics_import_statistics(statistic_id: str, statistics: list, **kwargs) -> dict:
    """Import external statistics through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.STATISTICS, "import_statistics", statistic_id=statistic_id, statistics=statistics, **kwargs)


def ha_statistics_validate_statistics(**kwargs) -> dict:
    """Validate statistics and find issues through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.STATISTICS, "validate_statistics", **kwargs)


def ha_statistics_update_statistics_issues(statistic_id: str, issues: list, **kwargs) -> dict:
    """Update validation issues for statistics through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.STATISTICS, "update_statistics_issues", statistic_id=statistic_id, issues=issues, **kwargs)


# ===== LOGBOOK CONVENIENCE FUNCTIONS =====

def ha_logbook_get_events(start_time: str, end_time: Optional[str] = None, entity_ids: Optional[list] = None, device_ids: Optional[list] = None, **kwargs) -> dict:
    """Get human-readable event logs through HA gateway."""
    return ha_gateway.ha_execute_operation(HAGatewayInterface.LOGBOOK, "get_events", start_time=start_time, end_time=end_time, entity_ids=entity_ids, device_ids=device_ids, **kwargs)
