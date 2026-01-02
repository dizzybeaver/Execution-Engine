"""
HA Routing Gateway Factory - Home Assistant Routing and Execution Layer

This module provides the HA Routing Gateway for managing routes with
pre/post processing hooks for Home Assistant operations.

Architecture Layer: HA Domain - Routing and Execution Layer

Based on:
D:\\Code\\Project\\Gateway\\HA\\ha_routing_gateway_factory.py

Integration:
    - Uses HAGatewayError from ha_common
    - Provides route-based execution with middleware support
    - Supports pre/post processing hooks
    - Enables flexible HA operation pipelines

Usage:
    >>> from ee.gateway.ha import create_ha_routing_gateway, HARoute
    >>>
    >>> # Define handler
    >>> def handle_call_service(payload):
    ...     # Call HA service
    ...     return ha_api.call_service(**payload)
    >>>
    >>> # Create route with pre/post hooks
    >>> route = HARoute(
    ...     name="service.call",
    ...     target=handle_call_service,
    ...     pre=validate_payload,
    ...     post=format_response,
    ... )
    >>>
    >>> # Create routing gateway
    >>> gateway = create_ha_routing_gateway(
    ...     service_call=route,
    ...     state_get=state_route,
    ... )
    >>>
    >>> # Route request
    >>> result = gateway.route("service_call", {
    ...     "domain": "light",
    ...     "service": "turn_on"
    ... })
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional

from EE.universal_gateway.domain_gateway import RouteNotFoundError
from EE.ha.ha_common import HAGatewayError


@dataclass
class HARoute:
    """Represents a single HA route with optional pre/post processing.

    An HARoute defines an execution pipeline for HA operations:
    1. Pre-processing hook (optional) - transform/validate input
    2. Target handler - execute main logic
    3. Post-processing hook (optional) - transform/format output

    This enables middleware-style processing for HA operations such as:
    - Input validation and transformation
    - Authentication/authorization
    - Logging/monitoring
    - Response formatting
    - Error handling

    Attributes:
        name: Unique route name (e.g., "service.call", "state.get")
        target: Main handler callable that executes the HA operation
        pre: Optional pre-processing hook (called before target)
        post: Optional post-processing hook (called after target)

    Example:
        >>> def validate_service_call(payload):
        ...     # Validate domain and service
        ...     if "domain" not in payload or "service" not in payload:
        ...         raise ValueError("Missing required fields")
        ...     return payload
        >>>
        >>> def format_response(result):
        ...     # Add metadata to response
        ...     return {
        ...         "data": result,
        ...         "timestamp": datetime.now().isoformat()
        ...     }
        >>>
        >>> def call_ha_service(payload):
        ...     # Actual HA API call
        ...     return ha_api.call_service(**payload)
        >>>
        >>> route = HARoute(
        ...     name="service.call",
        ...     target=call_ha_service,
        ...     pre=validate_service_call,
        ...     post=format_response,
        ... )
        >>>
        >>> # Execute route
        >>> result = route.execute({
        ...     "domain": "light",
        ...     "service": "turn_on",
        ...     "entity_id": "light.living_room"
        ... })
    """

    name: str
    target: Callable[[dict], Any]
    pre: Optional[Callable[[dict], dict]] = None
    post: Optional[Callable[[Any], Any]] = None

    def execute(self, payload: dict) -> Any:
        """Execute the route with pre/post processing.

        Execution pipeline:
        1. Run pre-hook if provided (transform input)
        2. Execute target handler with (possibly modified) payload
        3. Run post-hook if provided (transform output)
        4. Return final result

        Args:
            payload: Input data for the route

        Returns:
            Result from target, optionally processed by post-hook

        Raises:
            HAGatewayError: If route execution fails at any stage

        Example:
            >>> route = HARoute(...)
            >>> result = route.execute({
            ...     "domain": "light",
            ...     "service": "turn_on"
            ... })
        """
        try:
            # Step 1: Pre-processing (optional)
            if self.pre:
                payload = self.pre(payload)

            # Step 2: Execute target
            result = self.target(payload)

            # Step 3: Post-processing (optional)
            if self.post:
                result = self.post(result)

            return result

        except Exception as e:
            # Enhance error with route context
            raise HAGatewayError(
                f"HA route '{self.name}' failed: {str(e)}",
                error_code="HA_ROUTE_ERROR",
                context={
                    "route_name": self.name,
                    "payload": payload,
                    "has_pre_hook": self.pre is not None,
                    "has_post_hook": self.post is not None,
                    "target": (
                        self.target.__name__
                        if hasattr(self.target, '__name__')
                        else str(self.target)
                    ),
                },
                operation="route_execute",
            ) from e

    def execute_pre_only(self, payload: dict) -> dict:
        """Execute only the pre-processing hook.

        Useful for testing or debugging pre-processing logic.

        Args:
            payload: Input data to pre-process

        Returns:
            Pre-processed payload

        Raises:
            HAGatewayError: If pre-hook is not defined or fails
        """
        if not self.pre:
            raise HAGatewayError(
                f"Route '{self.name}' has no pre-hook",
                error_code="HA_NO_PRE_HOOK",
                context={"route_name": self.name},
                operation="pre_execute",
            )

        try:
            return self.pre(payload)
        except Exception as e:
            raise HAGatewayError(
                f"Pre-hook failed for route '{self.name}': {str(e)}",
                error_code="HA_PRE_HOOK_ERROR",
                context={"route_name": self.name, "payload": payload},
                operation="pre_execute",
            ) from e

    def execute_post_only(self, result: Any) -> Any:
        """Execute only the post-processing hook.

        Useful for testing or debugging post-processing logic.

        Args:
            result: Result to post-process

        Returns:
            Post-processed result

        Raises:
            HAGatewayError: If post-hook is not defined or fails
        """
        if not self.post:
            raise HAGatewayError(
                f"Route '{self.name}' has no post-hook",
                error_code="HA_NO_POST_HOOK",
                context={"route_name": self.name},
                operation="post_execute",
            )

        try:
            return self.post(result)
        except Exception as e:
            raise HAGatewayError(
                f"Post-hook failed for route '{self.name}': {str(e)}",
                error_code="HA_POST_HOOK_ERROR",
                context={"route_name": self.name, "result": result},
                operation="post_execute",
            ) from e


@dataclass
class HARoutingGateway:
    """Gateway for managing and routing HA operations.

    The HARoutingGateway provides a centralized registry for all HA routes
    with execution support and route discovery. Routes can have pre/post
    processing hooks for flexible operation pipelines.

    Attributes:
        routes: Dictionary mapping route names to HARoute instances

    Example:
        >>> gateway = HARoutingGateway(routes={
        ...     "service_call": service_route,
        ...     "state_get": state_route,
        ... })
        >>>
        >>> # Route a request
        >>> result = gateway.route("service_call", {
        ...     "domain": "light",
        ...     "service": "turn_on"
        ... })
        >>>
        >>> # List all routes
        >>> routes = gateway.list_routes()
    """

    routes: Dict[str, HARoute]

    def route(self, name: str, payload: dict) -> Any:
        """Route a request to the appropriate HA route.

        Args:
            name: Route name (e.g., "service_call", "state_get")
            payload: Request payload as dictionary

        Returns:
            Route execution result

        Raises:
            RouteNotFoundError: If route name is not registered
            HAGatewayError: If route execution fails

        Example:
            >>> gateway = create_ha_routing_gateway(...)
            >>> result = gateway.route("service_call", {
            ...     "domain": "light",
            ...     "service": "turn_on"
            ... })
        """
        if name not in self.routes:
            available = list(self.routes.keys())
            raise RouteNotFoundError(
                route_name=name,
                available_routes=available,
                context={
                    "domain": "ha",
                    "operation": "route_request",
                    "payload": payload,
                },
            )

        route = self.routes[name]
        try:
            return route.execute(payload)
        except HAGatewayError:
            # Re-raise HA errors as-is
            raise
        except Exception as e:
            # Wrap other exceptions
            raise HAGatewayError(
                f"HA routing for '{name}' failed: {str(e)}",
                error_code="HA_ROUTING_ERROR",
                context={
                    "route_name": name,
                    "payload": payload,
                },
                operation="route_request",
            ) from e

    def has_route(self, name: str) -> bool:
        """Check if a route is registered.

        Args:
            name: Route name to check

        Returns:
            True if route exists, False otherwise

        Example:
            >>> if gateway.has_route("service_call"):
            ...     gateway.route("service_call", {...})
        """
        return name in self.routes

    def get_route(self, name: str) -> HARoute:
        """Get a route by name without executing it.

        Useful for inspection or testing individual hooks.

        Args:
            name: Route name

        Returns:
            HARoute instance

        Raises:
            RouteNotFoundError: If route is not registered

        Example:
            >>> route = gateway.get_route("service_call")
            >>> # Test pre-hook
            >>> processed = route.execute_pre_only(raw_payload)
        """
        if name not in self.routes:
            available = list(self.routes.keys())
            raise RouteNotFoundError(
                route_name=name,
                available_routes=available,
                context={
                    "domain": "ha",
                    "operation": "get_route",
                },
            )

        return self.routes[name]

    def list_routes(self) -> Dict[str, str]:
        """List all registered routes with their target handler types.

        Returns:
            Dictionary mapping route names to their target handler types

        Example:
            >>> gateway.list_routes()
            {
                "service_call": "function",
                "state_get": "callable",
                "automation_trigger": "function"
            }
        """
        return {
            name: (
                type(r.target).__name__
                if hasattr(r.target, '__class__')
                else type(r.target).__name__
            )
            for name, r in self.routes.items()
        }

    def list_route_info(self) -> Dict[str, Dict[str, Any]]:
        """List detailed information about all routes.

        Returns:
            Dictionary with route metadata including:
            - name: Route name
            - has_pre_hook: Whether route has pre-processing
            - has_post_hook: Whether route has post-processing
            - target_name: Target handler name (if available)

        Example:
            >>> gateway.list_route_info()
            {
                "service_call": {
                    "name": "service_call",
                    "has_pre_hook": True,
                    "has_post_hook": True,
                    "target_name": "call_ha_service"
                },
                ...
            }
        """
        return {
            name: {
                "name": name,
                "has_pre_hook": route.pre is not None,
                "has_post_hook": route.post is not None,
                "target_name": (
                    route.target.__name__
                    if hasattr(route.target, '__name__')
                    else str(route.target)
                ),
            }
            for name, route in self.routes.items()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get gateway statistics.

        Returns:
            Dictionary with gateway stats

        Example:
            >>> gateway.get_stats()
            {
                "total_routes": 5,
                "routes_with_pre_hooks": 3,
                "routes_with_post_hooks": 2,
                "route_names": ["service_call", ...]
            }
        """
        return {
            "total_routes": len(self.routes),
            "routes_with_pre_hooks": sum(
                1 for r in self.routes.values() if r.pre is not None
            ),
            "routes_with_post_hooks": sum(
                1 for r in self.routes.values() if r.post is not None
            ),
            "route_names": list(self.routes.keys()),
        }


def create_ha_routing_gateway(**routes: HARoute) -> HARoutingGateway:
    """Factory function to create an HARoutingGateway.

    This factory provides a clean interface for creating an HA routing gateway
    with all registered routes. Use keyword arguments to name each route.

    Args:
        **routes: Keyword arguments mapping route names to HARoute instances
            - Key: Route name (e.g., "service_call", "state_get")
            - Value: HARoute instance

    Returns:
        Configured HARoutingGateway instance

    Raises:
        ValueError: If no routes provided or if routes are not HARoute instances

    Example:
        >>> from ee.gateway.ha import create_ha_routing_gateway, HARoute
        >>>
        >>> # Create routes
        >>> service_route = HARoute(
        ...     name="service.call",
        ...     target=call_ha_service,
        ...     pre=validate_service,
        ...     post=format_response,
        ... )
        >>>
        >>> state_route = HARoute(
        ...     name="state.get",
        ...     target=get_ha_state,
        ...     pre=validate_entity,
        ... )
        >>>
        >>> # Create gateway
        >>> gateway = create_ha_routing_gateway(
        ...     service_call=service_route,
        ...     state_get=state_route,
        ...     automation_trigger=automation_route,
        ... )
        >>>
        >>> # Use gateway
        >>> result = gateway.route("service_call", {
        ...     "domain": "light",
        ...     "service": "turn_on"
        ... })

    Common Route Naming Patterns:
        - Use underscores for route names: "service_call", "state_get"
        - Use domain_action pattern: "service_call", "state_get"
        - Be consistent with naming across your gateway
        - Use descriptive names that indicate the HA operation
    """
    # Validate that routes are provided
    if not routes:
        raise ValueError("At least one route must be provided")

    # Validate that all values are HARoute instances
    for name, route in routes.items():
        if not isinstance(route, HARoute):
            raise ValueError(
                f"Route '{name}' must be an HARoute instance, "
                f"got {type(route).__name__}"
            )

    return HARoutingGateway(routes=dict(routes))


__all__ = [
    'HARoute',
    'HARoutingGateway',
    'create_ha_routing_gateway',
]
