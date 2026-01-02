"""
HA Command Factory - Home Assistant Command Creation Layer

This module provides the factory pattern for creating HA (Home Assistant)
commands with schema validation, template rendering, and result serialization.

Architecture Layer: HA Domain - Command Creation Layer

Based on:
D:\\Code\\Project\\Gateway\\HA\\ha_command_factory.py

Integration:
    - Uses HAGatewayError from ha_common
    - Provides command building blocks for HACommandGateway
    - Supports schema validation and template rendering
    - Handles result serialization

Usage:
    >>> from ee.gateway.ha import create_ha_command
    >>>
    >>> # Create a command
    >>> command = create_ha_command(
    ...     name="turn_on_light",
    ...     schema=light_schema,
    ...     template=light_template,
    ...     handler=light_handler,
    ...     serializer=json_serializer,
    ... )
    >>>
    >>> # Execute command
    >>> result = command.execute({"entity_id": "light.living_room"})
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Optional

from EE.ha.ha_common import HAGatewayError


@dataclass
class HACommand:
    """Represents a single HA command with validation, rendering, and execution.

    An HACommand encapsulates the complete lifecycle of a Home Assistant operation:
    1. Input validation using schema
    2. Template rendering with validated data
    3. Handler execution with rendered output
    4. Result serialization (optional)

    Attributes:
        name: Unique command name (e.g., "light.turn_on", "sensor.get_state")
        schema: Schema validator for input validation (e.g., JSONSchema, Marshmallow)
        template: Template renderer for HA API payloads (e.g., Jinja2, string template)
        handler: Callable that executes the actual HA operation
        serializer: Optional serializer for result (e.g., JSON, YAML)

    Example:
        >>> command = HACommand(
        ...     name="light.turn_on",
        ...     schema=LightTurnOnSchema(),
        ...     template=LightTemplate(),
        ...     handler=call_ha_service,
        ...     serializer=json_serializer,
        ... )
        >>> result = command.execute({
        ...     "entity_id": "light.living_room",
        ...     "brightness": 255
        ... })
    """

    name: str
    schema: Any
    template: Any
    handler: Callable[[dict], Any]
    serializer: Optional[Any] = None

    def execute(self, payload: dict) -> Any:
        """Execute the HA command with the given payload.

        Execution pipeline:
        1. Validate payload against schema
        2. Render template with validated data
        3. Execute handler with rendered template
        4. Serialize result if serializer provided

        Args:
            payload: Command input data (e.g., entity_id, service parameters)

        Returns:
            Result from handler, optionally serialized

        Raises:
            HAGatewayError: If command execution fails at any stage

        Example:
            >>> command = HACommand(...)
            >>> result = command.execute({
            ...     "entity_id": "light.living_room",
            ...     "color_temp": 400
            ... })
        """
        try:
            # Step 1: Validate input
            validated = self.schema.validate(payload)

            # Step 2: Render template
            rendered = self.template.render(**validated)

            # Step 3: Execute handler
            # Handler receives both rendered template and original validated data
            result = self.handler({
                "rendered": rendered,
                "validated": validated,
            })

            # Step 4: Serialize if needed
            if self.serializer:
                return self.serializer.dumps(result)

            return result

        except Exception as e:
            # Enhance error with command context
            raise HAGatewayError(
                f"HA command '{self.name}' failed: {str(e)}",
                error_code="HA_COMMAND_ERROR",
                context={
                    "command_name": self.name,
                    "payload": payload,
                    "handler": self.handler.__name__ if hasattr(self.handler, '__name__') else str(self.handler),
                },
                operation="command_execute",
            ) from e

    def validate(self, payload: dict) -> Any:
        """Validate payload against schema without executing.

        Useful for pre-flight validation or testing.

        Args:
            payload: Command input data to validate

        Returns:
            Validated data

        Raises:
            HAGatewayError: If validation fails
        """
        try:
            return self.schema.validate(payload)
        except Exception as e:
            raise HAGatewayError(
                f"HA command '{self.name}' validation failed: {str(e)}",
                error_code="HA_VALIDATION_ERROR",
                context={
                    "command_name": self.name,
                    "payload": payload,
                },
                operation="command_validate",
            ) from e

    def render_template(self, payload: dict) -> Any:
        """Render template with payload (useful for debugging).

        Args:
            payload: Command input data

        Returns:
            Rendered template output

        Raises:
            HAGatewayError: If rendering fails
        """
        try:
            validated = self.schema.validate(payload)
            return self.template.render(**validated)
        except Exception as e:
            raise HAGatewayError(
                f"HA command '{self.name}' template rendering failed: {str(e)}",
                error_code="HA_TEMPLATE_ERROR",
                context={
                    "command_name": self.name,
                    "payload": payload,
                },
                operation="command_render",
            ) from e


def create_ha_command(
    *,
    name: str,
    schema: Any,
    template: Any,
    handler: Callable[[dict], Any],
    serializer: Optional[Any] = None,
) -> HACommand:
    """Factory function to create an HACommand.

    This factory provides a clean interface for creating HA commands with
    all necessary components. Use this instead of directly instantiating
    HACommand for better readability and consistency.

    Args:
        name: Unique command name (e.g., "light.turn_on", "automation.trigger")
        schema: Schema validator for input validation
            - Must have validate(payload: dict) -> dict method
            - Examples: JSONSchema, Marshmallow schema, Pydantic model
        template: Template renderer for HA API payloads
            - Must have render(**kwargs) -> Any method
            - Examples: Jinja2 Template, string.Template, custom renderer
        handler: Callable that executes the actual HA operation
            - Receives dict with "rendered" and "validated" keys
            - Returns operation result
        serializer: Optional result serializer
            - Must have dumps(data: Any) -> str method
            - Examples: JSON serializer, YAML serializer

    Returns:
        Configured HACommand instance

    Raises:
        ValueError: If required parameters are missing or invalid

    Example:
        >>> from ee.serializers import create_json_serializer
        >>> from ee.templates import create_jinja_template
        >>>
        >>> # Define handler
        >>> def turn_on_handler(data):
        ...     rendered = data["rendered"]
        ...     # Call HA API with rendered data
        ...     return ha_api.call_service(**rendered)
        >>>
        >>> # Create command
        >>> command = create_ha_command(
        ...     name="light.turn_on",
        ...     schema=LightTurnOnSchema(),
        ...     template=create_jinja_template("light_turn_on.j2"),
        ...     handler=turn_on_handler,
        ...     serializer=create_json_serializer(),
        ... )
        >>>
        >>> # Execute
        >>> result = command.execute({
        ...     "entity_id": "light.living_room",
        ...     "brightness": 255
        ... })

    Common HA Commands:
        - light.turn_on: Turn on a light
        - light.turn_off: Turn off a light
        - sensor.get_state: Get sensor state
        - automation.trigger: Trigger automation
        - script.run: Run a script
        - switch.toggle: Toggle a switch
        - climate.set_temperature: Set thermostat temperature
        - media_player.play_media: Play media on player
    """
    # Validate required parameters
    if not name:
        raise ValueError("Command name cannot be empty")
    if not schema:
        raise ValueError("Schema cannot be None")
    if not template:
        raise ValueError("Template cannot be None")
    if not handler:
        raise ValueError("Handler cannot be None")

    # Validate schema has validate method
    if not hasattr(schema, 'validate'):
        raise ValueError("Schema must have a 'validate' method")

    # Validate template has render method
    if not hasattr(template, 'render'):
        raise ValueError("Template must have a 'render' method")

    # Validate handler is callable
    if not callable(handler):
        raise ValueError("Handler must be callable")

    # Validate serializer if provided
    if serializer and not hasattr(serializer, 'dumps'):
        raise ValueError("Serializer must have a 'dumps' method")

    return HACommand(
        name=name,
        schema=schema,
        template=template,
        handler=handler,
        serializer=serializer,
    )


__all__ = [
    'HACommand',
    'create_ha_command',
]
