"""ha_shopping_list_core.py - Core Implementation for SHOPPING_LIST Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import HAGatewayInterface, ha_execute_operation


def add_item_impl(
    name: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Add item to shopping list via shopping_list.add_item service.

    Args:
        name: Item name (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not name:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "name is required"
        }

    service_data = {"name": name}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="shopping_list",
        service="add_item",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Item added to shopping list successfully"

    return result


def remove_item_impl(
    name: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Remove item from shopping list via shopping_list.remove_item service.

    Args:
        name: Item name (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not name:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "name is required"
        }

    service_data = {"name": name}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="shopping_list",
        service="remove_item",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Item removed from shopping list successfully"

    return result


def complete_item_impl(
    name: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Mark item as completed via shopping_list.complete_item service.

    Args:
        name: Item name (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not name:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "name is required"
        }

    service_data = {"name": name}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="shopping_list",
        service="complete_item",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Item marked as completed successfully"

    return result


def incomplete_item_impl(
    name: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Mark item as incomplete via shopping_list.incomplete_item service.

    Args:
        name: Item name (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    if not name:
        return {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "name is required"
        }

    service_data = {"name": name}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="shopping_list",
        service="incomplete_item",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Item marked as incomplete successfully"

    return result


def complete_all_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Mark all items as completed via shopping_list.complete_all service.

    Args:
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    service_data = {}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="shopping_list",
        service="complete_all",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "All items marked as completed successfully"

    return result


def incomplete_all_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Mark all items as incomplete via shopping_list.incomplete_all service.

    Args:
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    service_data = {}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="shopping_list",
        service="incomplete_all",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "All items marked as incomplete successfully"

    return result


def clear_completed_items_impl(
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Clear completed items via shopping_list.clear_completed_items service.

    Args:
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    service_data = {}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="shopping_list",
        service="clear_completed_items",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Completed items cleared successfully"

    return result


def sort_impl(
    reverse: Optional[bool] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Sort shopping list via shopping_list.sort service.

    Args:
        reverse: Sort in reverse order (default: false)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    service_data = {}

    if reverse is not None:
        service_data["reverse"] = reverse

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="shopping_list",
        service="sort",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Shopping list sorted successfully"

    return result
