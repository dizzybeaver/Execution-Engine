"""
HA Gateway Factory - Home Assistant Domain Gateway Main Layer

This module provides the main HA Gateway for Home Assistant domain operations.
It integrates with the Universal Gateway (UG) architecture to provide HA operations.

Architecture Layer: HA Domain - Main Gateway Layer

Based on:
D:\\Code\\Project\\Gateway\\HA\\ha_gateway_factory.py

Integration:
    - Uses DomainGateway as base class
    - Receives get_logger, get_metrics, call_operation via DI
    - Manages HA operations through execute() method
    - Provides unified HA domain interface

Usage:
    >>> from EE.ha import create_ha_gateway
    >>>
    >>> # Create HA gateway with UG dependencies
    >>> ha_gateway = create_ha_gateway(
    ...     get_logger=ug.get_logger,
    ...     get_metrics=ug.get_metrics,
    ...     call_operation=ug.execute_operation
    ... )
    >>>
    >>> # Execute HA operations
    >>> result = ha_gateway.execute("service_call", {
    ...     "domain": "light",
    ...     "service": "turn_on"
    ... })
    >>>
    >>> # List all operations
    >>> all_ops = ha_gateway.list_all()
"""

from __future__ import annotations
from typing import Dict, Any, Callable

from EE.ha.ha_common import HAGatewayError
from EE.universal_gateway.domain_gateway import DomainGateway


class HAGateway(DomainGateway):
    """Main gateway for Home Assistant domain operations.

    The HAGateway provides a unified interface for all HA operations.
    It follows the UG architecture pattern, receiving dependencies via
    dependency injection (get_logger, get_metrics, call_operation).

    This class implements the DomainGateway interface for integration with
    the UG, making it a first-class domain gateway in EE.

    Architecture:
        HAGateway (DomainGateway)
            ├── Receives get_logger for logging
            ├── Receives get_metrics for metrics
            └── Receives call_operation for cross-domain calls

    Example:
        >>> gateway = create_ha_gateway(
        ...     get_logger=ug.get_logger,
        ...     get_metrics=ug.get_metrics,
        ...     call_operation=ug.execute_operation
        ... )
        >>>
        >>> # Execute route-based operation
        >>> result = gateway.execute("service_call", {
        ...     "domain": "light",
        ...     "service": "turn_on"
        ... })
        >>>
        >>> # List all capabilities
        >>> all = gateway.list_all()
        >>> # {
        >>> #     "domain": "ha",
        >>> #     "operations": [...]
        >>> # }
    """

    # MODIFIED: EE 2.1 uniform constructor signature - ADDED get_config
    def __init__(
        self,
        domain_name: str,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str], Any],
        call_operation: Callable[[str, str, str], Any],
    ):
        """Initialize HA gateway with UG dependencies.

        Args:
            domain_name: Domain name for this gateway
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Function to call operations in other domains
        """
        # Initialize base DomainGateway with all EE 2.1 parameters
        super().__init__(
            domain_name=domain_name,  # MODIFIED: Pass domain_name instead of hardcoding
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,  # ADDED: get_config parameter
            call_operation=call_operation
        )

        # HA-specific logger
        self._ha_logger = self._get_logger("ha")
        self._ha_metrics = self._get_metrics("ha")

    def execute_domain_operation(
        self,
        interface: str,
        operation: str,
        **kwargs: Any,
    ) -> Any:
        """Execute an HA operation (overrides DomainGateway method).

        This is the main entry point for HA operations called by the UG.
        The interface and operation are combined to determine which HA
        operation to execute.

        Args:
            interface: Interface name (e.g., "service", "state", "entity")
            operation: Operation name (e.g., "call", "get", "set")
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            HAGatewayError: If operation execution fails

        Example:
            >>> gateway = create_ha_gateway(...)
            >>>
            >>> # Call HA service
            >>> result = gateway.execute_domain_operation(
            ...     interface="service",
            ...     operation="call",
            ...     domain="light",
            ...     service="turn_on",
            ...     entity_id="light.living_room"
            ... )
            >>>
            >>> # Get entity state
            >>> state = gateway.execute_domain_operation(
            ...     interface="state",
            ...     operation="get",
            ...     entity_id="sensor.temperature"
            ... )
        """
        try:
            # Log operation
            self._ha_logger.debug(
                f"Executing HA operation: {interface}.{operation}"
            )

            # Route to appropriate HA operation handler
            # Combine interface and operation for routing
            op_key = f"{interface}_{operation}"

            if op_key == "service_call":
                return self._service_call(kwargs)
            elif op_key == "state_get":
                return self._state_get(kwargs)
            elif op_key == "state_set":
                return self._state_set(kwargs)
            elif op_key == "entity_get":
                return self._entity_get(kwargs)
            else:
                raise HAGatewayError(
                    f"Unknown HA operation: {interface}.{operation}",
                    error_code="HA_UNKNOWN_OPERATION",
                    context={"interface": interface, "operation": operation},
                    operation="execute_domain_operation"
                )

        except HAGatewayError:
            # Re-raise HA errors as-is
            raise
        except Exception as e:
            # Wrap other exceptions
            raise HAGatewayError(
                f"HA gateway execution failed for '{interface}.{operation}': {str(e)}",
                error_code="HA_GATEWAY_EXECUTION_ERROR",
                context={
                    "interface": interface,
                    "operation": operation,
                    "kwargs": kwargs,
                },
                operation="execute_domain_operation",
            ) from e

    def _service_call(self, params: dict) -> dict:
        """Call a Home Assistant service.

        Args:
            params: Service call parameters (domain, service, entity_id, etc.)

        Returns:
            Service call result

        Note:
            This is a placeholder implementation. Real implementation would
            make HTTP/WebSocket calls to Home Assistant API.
        """
        # Placeholder - real implementation would call HA API
        self._ha_logger.info(f"HA service call: {params}")
        self._ha_metrics.increment("ha.service_call", 1.0)
        return {"status": "success", "message": "Service call placeholder"}

    def _state_get(self, params: dict) -> dict:
        """Get entity state from Home Assistant.

        Args:
            params: State get parameters (entity_id)

        Returns:
            Entity state

        Note:
            This is a placeholder implementation. Real implementation would
            make HTTP/WebSocket calls to Home Assistant API.
        """
        # Placeholder - real implementation would call HA API
        self._ha_logger.info(f"HA state get: {params}")
        self._ha_metrics.increment("ha.state_get", 1.0)
        return {"entity_id": params.get("entity_id"), "state": "unknown"}

    def _state_set(self, params: dict) -> dict:
        """Set entity state in Home Assistant.

        Args:
            params: State set parameters (entity_id, state, attributes)

        Returns:
            State set result

        Note:
            This is a placeholder implementation. Real implementation would
            make HTTP/WebSocket calls to Home Assistant API.
        """
        # Placeholder - real implementation would call HA API
        self._ha_logger.info(f"HA state set: {params}")
        self._ha_metrics.increment("ha.state_set", 1.0)
        return {"status": "success", "message": "State set placeholder"}

    def _entity_get(self, params: dict) -> dict:
        """Get entity details from Home Assistant.

        Args:
            params: Entity get parameters (entity_id)

        Returns:
            Entity details

        Note:
            This is a placeholder implementation. Real implementation would
            make HTTP/WebSocket calls to Home Assistant API.
        """
        # Placeholder - real implementation would call HA API
        self._ha_logger.info(f"HA entity get: {params}")
        self._ha_metrics.increment("ha.entity_get", 1.0)
        return {"entity_id": params.get("entity_id"), "attributes": {}}

    def list_all(self) -> Dict[str, Any]:
        """List all available operations in the HA gateway.

        This method implements the DomainGateway interface requirement
        and provides a comprehensive view of all HA capabilities.

        Returns:
            Dictionary with all operations:
            {
                "domain": "ha",
                "operations": [
                    {"route": "ha.service_call", "description": "..."},
                    {"route": "ha.state_get", "description": "..."},
                    {"route": "ha.state_set", "description": "..."},
                ],
                "stats": {...}
            }

        Example:
            >>> gateway = create_ha_gateway(...)
            >>> all_ops = gateway.list_all()
            >>> # {
            >>> #     "domain": "ha",
            >>> #     "operations": [...],
            >>> #     "stats": {...}
            >>> # }
        """
        operations = [
            {"route": "ha.service_call", "description": "Call HA service"},
            {"route": "ha.state_get", "description": "Get entity state"},
            {"route": "ha.state_set", "description": "Set entity state"},
        ]

        return {
            "domain": "ha",
            "operations": operations,
            "stats": {
                "total_operations": len(operations),
            },
        }

    def get_domain_info(self) -> Dict[str, Any]:
        """Get detailed information about the HA domain gateway.

        Returns:
            Dictionary with domain metadata and capabilities

        Example:
            >>> info = gateway.get_domain_info()
            >>> # {
            >>> #     "domain": "ha",
            >>> #     "name": "Home Assistant",
            >>> #     "description": "Smart home automation gateway",
            >>> #     "version": "1.0.0",
            >>> #     "capabilities": [...]
            >>> # }
        """
        return {
            "domain": "ha",
            "name": "Home Assistant",
            "description": "Smart home automation and control gateway",
            "version": "1.0.0",
            "capabilities": [
                "service_call",
                "state_get",
                "state_set",
            ],
            "supported_domains": [
                "light",
                "switch",
                "sensor",
                "binary_sensor",
                "climate",
                "cover",
                "media_player",
            ],
        }


# MODIFIED: EE 2.1 factory signature - ADDED get_config
def create_ha_gateway(
    domain_name: str,
    get_logger: Callable[[str], Any],
    get_metrics: Callable[[str], Any],
    get_config: Callable[[str], Any],
    call_operation: Callable[[str, str, str], Any],
) -> HAGateway:
    """Factory function to create an HA Gateway with UG dependencies.

    This factory creates a complete HAGateway that integrates with the
    Universal Gateway architecture, receiving dependencies via DI.

    Args:
        domain_name: Domain name for this gateway
        get_logger: Factory function to create loggers
        get_metrics: Factory function to create metrics collectors
        get_config: Factory function to get configuration values
        call_operation: Function to call operations in other domains

    Returns:
        Fully configured HAGateway instance

    Raises:
        ValueError: If required parameters are missing

    Example:
        >>> from EE.ha import create_ha_gateway
        >>>
        >>> # Create HA gateway
        >>> ha_gateway = create_ha_gateway(
        ...     domain_name="ha",
        ...     get_logger=ug.get_logger,
        ...     get_metrics=ug.get_metrics,
        ...     get_config=ug.get_config,
        ...     call_operation=ug.execute_operation
        ... )
        >>>
        >>> # Use gateway
        >>> result = ha_gateway.execute("ha.service_call", {
        ...     "domain": "light",
        ...     "service": "turn_on",
        ...     "entity_id": "light.living_room"
        ... })

    Integration with UG:
        The HA gateway uses call_operation to interact with other domains:
        - Can call networking domain for HTTP/WebSocket connections
        - Can call config domain for HA configuration
        - Can call security domain for authentication
    """
    # Validate inputs
    if not domain_name:
        raise ValueError("domain_name is required")
    if not get_logger:
        raise ValueError("get_logger is required")
    if not get_metrics:
        raise ValueError("get_metrics is required")
    if not get_config:
        raise ValueError("get_config is required")  # ADDED
    if not call_operation:
        raise ValueError("call_operation is required")

    # Create and return HA gateway with all EE 2.1 parameters
    return HAGateway(
        domain_name=domain_name,  # ADDED
        get_logger=get_logger,
        get_metrics=get_metrics,
        get_config=get_config,  # ADDED
        call_operation=call_operation
    )


__all__ = [
    'HAGateway',
    'create_ha_gateway',
]
