"""ha_todo_core.py - Core Implementation for TODO Interface

Version: 2025-12-22_1
Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Optional

from lee.home_assistant.ha_gateway import (
    HAGatewayInterface,
    ha_execute_operation,
)

# ===== SHARED VALIDATION HELPER =====

def validate_todo_params(
    entity_id: Optional[str],
    required_params: Optional[dict[str, Any]] = None,
) -> Optional[tuple[bool, dict[str, Any]]]:
    """Shared validation for TODO operation parameters.

    Args:
        entity_id: Todo entity ID
        required_params: Dict of required parameter names to values

    Returns:
        Tuple of (is_valid, error_dict) - error_dict is None if valid

    Code Quality: Reduces duplication across 4 functions (~30 lines saved)
    """
    if not entity_id or (isinstance(entity_id, str) and entity_id.strip() == ""):
        return False, {
            "success": False,
            "error_code": "MISSING_PARAMETER",
            "error_message": "entity_id is required"
        }

    if required_params:
        for param_name, param_value in required_params.items():
            if not param_value or (isinstance(param_value, str) and param_value.strip() == ""):
                return False, {
                    "success": False,
                    "error_code": "MISSING_PARAMETER",
                    "error_message": f"{param_name} is required"
                }

    return True, None


def get_items_impl(
    entity_id: Optional[str] = None,
    status: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Get todo items via todo.get_items service.

    Args:
        entity_id: Todo entity ID
        status: Item status filter ("needs_action" or "completed", default: "needs_action")
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status and todo items
    """
    # Use shared validation helper (reduces duplication)
    is_valid, error = validate_todo_params(entity_id)
    if not is_valid:
        return error

    service_data = {"entity_id": entity_id}

    if status:
        service_data["status"] = status

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="todo",
        service="get_items",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Todo items retrieved successfully"

    return result


def add_item_impl(
    entity_id: Optional[str] = None,
    item: Optional[str] = None,
    due_date: Optional[str] = None,
    due_datetime: Optional[str] = None,
    description: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Add item to todo list via todo.add_item service.

    Args:
        entity_id: Todo entity ID
        item: Todo item summary (required)
        due_date: Due date (YYYY-MM-DD format)
        due_datetime: Due datetime (YYYY-MM-DD HH:MM:SS format)
        description: Item description
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    # Use shared validation helper (reduces duplication)
    is_valid, error = validate_todo_params(
        entity_id,
        required_params={"item": item}
    )
    if not is_valid:
        return error

    service_data = {"entity_id": entity_id, "item": item}

    if due_date:
        service_data["due_date"] = due_date
    if due_datetime:
        service_data["due_datetime"] = due_datetime
    if description:
        service_data["description"] = description

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="todo",
        service="add_item",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Todo item added successfully"

    return result


def update_item_impl(
    entity_id: Optional[str] = None,
    item: Optional[str] = None,
    rename: Optional[str] = None,
    status: Optional[str] = None,
    due_date: Optional[str] = None,
    due_datetime: Optional[str] = None,
    description: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Update todo item via todo.update_item service.

    Args:
        entity_id: Todo entity ID
        item: Current item summary (required)
        rename: New item name
        status: New status ("needs_action" or "completed")
        due_date: New due date (YYYY-MM-DD format)
        due_datetime: New due datetime (YYYY-MM-DD HH:MM:SS format)
        description: New description
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    # Use shared validation helper (reduces duplication)
    is_valid, error = validate_todo_params(
        entity_id,
        required_params={"item": item}
    )
    if not is_valid:
        return error

    service_data = {"entity_id": entity_id, "item": item}

    if rename:
        service_data["rename"] = rename
    if status:
        service_data["status"] = status
    if due_date:
        service_data["due_date"] = due_date
    if due_datetime:
        service_data["due_datetime"] = due_datetime
    if description:
        service_data["description"] = description

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="todo",
        service="update_item",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Todo item updated successfully"

    return result


def remove_item_impl(
    entity_id: Optional[str] = None,
    item: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Remove item from todo list via todo.remove_item service.

    Args:
        entity_id: Todo entity ID
        item: Item to remove (required)
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    # Use shared validation helper (reduces duplication)
    is_valid, error = validate_todo_params(
        entity_id,
        required_params={"item": item}
    )
    if not is_valid:
        return error

    service_data = {"entity_id": entity_id, "item": item}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="todo",
        service="remove_item",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Todo item removed successfully"

    return result


def remove_completed_items_impl(
    entity_id: Optional[str] = None,
    ha_config: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    **kwargs
) -> dict[str, Any]:
    """Remove all completed items via todo.remove_completed_items service.

    Args:
        entity_id: Todo entity ID
        ha_config: HA configuration
        correlation_id: Correlation ID for tracking

    Returns:
        Dict with success status
    """
    # Use shared validation helper (reduces duplication)
    is_valid, error = validate_todo_params(entity_id)
    if not is_valid:
        return error

    service_data = {"entity_id": entity_id}

    result = ha_execute_operation(
        HAGatewayInterface.DEVICES,
        "call_service",
        domain="todo",
        service="remove_completed_items",
        service_data=service_data,
        ha_config=ha_config,
        correlation_id=correlation_id
    )

    if result.get("success"):
        result["message"] = "Completed items removed successfully"

    return result
