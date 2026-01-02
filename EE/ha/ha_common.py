"""
HA Common Module - Home Assistant Domain Gateway Base

This module provides HA-specific error handling and common utilities
for the EE Home Assistant domain gateway.

Architecture Layer: HA Domain - Base Layer

Based on:
D:\\Code\\Project\\Gateway\\HA\\ha_common.py

Integration:
    - Uses EE gateway infrastructure (GatewayError from gateway_common)
    - Provides HA-specific error classes
    - Maintains error chaining and context preservation
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
from datetime import datetime



class HAGatewayError(Exception):
    """Base error for Home Assistant gateway failures in EE.

    This error class extends GatewayError with HA-specific error handling
    for Home Assistant domain operations including service calls,
    state queries, automation triggers, and entity management.

    Attributes:
        ha_domain: HA domain that caused the error (e.g., "light", "sensor")
        ha_entity: HA entity ID if relevant (e.g., "light.living_room")
        ha_service: HA service being called if relevant (e.g., "turn_on")
        operation: HA operation type (e.g., "service_call", "state_get")

    Example:
        >>> try:
        ...     ha_gateway.execute("service.call", {"domain": "light", "service": "turn_on"})
        ... except HAGatewayError as e:
        ...     print(f"HA Error: {e.error_code}")
        ...     print(f"Domain: {e.ha_domain}, Service: {e.ha_service}")
        ...     print(f"Context: {e.context}")
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
        ha_domain: Optional[str] = None,
        ha_entity: Optional[str] = None,
        ha_service: Optional[str] = None,
        operation: Optional[str] = None,
    ) -> None:
        """Initialize an HAGatewayError.

        Args:
            message: Human-readable error description
            error_code: Optional error code for categorization
            context: Optional dictionary with error context
            source: Optional source component name
            ha_domain: HA domain that caused the error (e.g., "light", "sensor")
            ha_entity: HA entity ID (e.g., "light.living_room")
            ha_service: HA service being called (e.g., "turn_on")
            operation: HA operation type (e.g., "service_call", "state_get")
        """
        self.ha_domain = ha_domain
        self.ha_entity = ha_entity
        self.ha_service = ha_service
        self.operation = operation

        # Add HA-specific context
        ha_context = {
            "ha_domain": ha_domain,
            "ha_entity": ha_entity,
            "ha_service": ha_service,
            "operation": operation,
        }
        # Filter out None values
        ha_context = {k: v for k, v in ha_context.items() if v is not None}

        if context:
            ha_context.update(context)

        # Default to HA Gateway if not specified
        ha_source = source or "HAGateway"

        # Default error code
        ha_error_code = error_code or "HA_GATEWAY_ERROR"

        super().__init__(
            message=message,
            error_code=ha_error_code,
            context=ha_context,
            source=ha_source,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation.

        Returns:
            Dictionary with all error information including HA-specific fields
        """
        base_dict = super().to_dict()
        base_dict.update({
            "ha_domain": self.ha_domain,
            "ha_entity": self.ha_entity,
            "ha_service": self.ha_service,
            "operation": self.operation,
        })
        return base_dict


class HAServiceNotFoundError(HAGatewayError):
    """Raised when a requested HA service is not found.

    Example:
        >>> raise HAServiceNotFoundError(
        ...     ha_domain="light",
        ...     service_name="turn_on_blue",
        ...     available_services=["turn_on", "turn_off", "toggle"]
        ... )
    """

    def __init__(
        self,
        ha_domain: str,
        service_name: str,
        available_services: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a HAServiceNotFoundError.

        Args:
            ha_domain: HA domain where service was not found
            service_name: Name of the service that was not found
            available_services: List of available service names (if known)
            context: Optional additional context
        """
        self.service_name = service_name
        self.available_services = available_services or []

        error_context = {
            "ha_domain": ha_domain,
            "requested_service": service_name,
            "available_services": self.available_services,
        }
        if context:
            error_context.update(context)

        super().__init__(
            message=f"HA service not found: {ha_domain}.{service_name}",
            error_code="HA_SERVICE_NOT_FOUND",
            context=error_context,
            ha_domain=ha_domain,
            ha_service=service_name,
            operation="service_call",
        )


class HAEntityNotFoundError(HAGatewayError):
    """Raised when a requested HA entity is not found.

    Example:
        >>> raise HAEntityNotFoundError(
        ...     entity_id="light.nonexistent",
        ...     available_entities=["light.living_room", "light.kitchen"]
        ... )
    """

    def __init__(
        self,
        entity_id: str,
        available_entities: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an HAEntityNotFoundError.

        Args:
            entity_id: Entity ID that was not found
            available_entities: List of available entity IDs (if known)
            context: Optional additional context
        """
        self.entity_id = entity_id
        self.available_entities = available_entities or []

        # Extract domain from entity_id
        ha_domain = entity_id.split('.')[0] if '.' in entity_id else None

        error_context = {
            "entity_id": entity_id,
            "available_entities": self.available_entities,
        }
        if context:
            error_context.update(context)

        super().__init__(
            message=f"HA entity not found: {entity_id}",
            error_code="HA_ENTITY_NOT_FOUND",
            context=error_context,
            ha_domain=ha_domain,
            ha_entity=entity_id,
            operation="entity_get",
        )


class HAStateError(HAGatewayError):
    """Raised when HA state operation fails."""

    def __init__(
        self,
        message: str,
        entity_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an HAStateError.

        Args:
            message: Human-readable error description
            entity_id: Entity ID if relevant
            context: Optional additional context
        """
        error_context = {"entity_id": entity_id} if entity_id else {}
        if context:
            error_context.update(context)

        # Extract domain from entity_id if available
        ha_domain = entity_id.split('.')[0] if entity_id and '.' in entity_id else None

        super().__init__(
            message=message,
            error_code="HA_STATE_ERROR",
            context=error_context,
            ha_domain=ha_domain,
            ha_entity=entity_id,
            operation="state_operation",
        )


class HAAutomationError(HAGatewayError):
    """Raised when HA automation operation fails."""

    def __init__(
        self,
        message: str,
        automation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an HAAutomationError.

        Args:
            message: Human-readable error description
            automation_id: Automation ID if relevant
            context: Optional additional context
        """
        error_context = {"automation_id": automation_id} if automation_id else {}
        if context:
            error_context.update(context)

        super().__init__(
            message=message,
            error_code="HA_AUTOMATION_ERROR",
            context=error_context,
            ha_domain="automation",
            operation="automation_operation",
        )


__all__ = [
    'HAGatewayError',
    'HAServiceNotFoundError',
    'HAEntityNotFoundError',
    'HAStateError',
    'HAAutomationError',
]
