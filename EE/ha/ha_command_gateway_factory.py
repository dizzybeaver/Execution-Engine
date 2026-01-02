"""
HA Command Gateway Factory - Home Assistant Command Execution Layer

This module provides the HA Command Gateway for managing and executing
Home Assistant commands with centralized command registry.

Architecture Layer: HA Domain - Command Execution Layer

Based on:
D:\\Code\\Project\\Gateway\\HA\\ha_command_gateway_factory.py

Integration:
    - Uses HACommand from ha_command_factory
    - Uses HAGatewayError from ha_common
    - Provides command registry and execution interface
    - Supports dynamic command discovery and listing

Usage:
    >>> from ee.gateway.ha import create_ha_command_gateway, create_ha_command
    >>>
    >>> # Create commands
    >>> light_on = create_ha_command(
    ...     name="light.turn_on",
    ...     schema=light_schema,
    ...     template=light_template,
    ...     handler=light_handler,
    ... )
    >>>
    >>> # Create command gateway
    >>> gateway = create_ha_command_gateway(
    ...     light_turn_on=light_on,
    ...     light_off=light_off_cmd,
    ...     sensor_get=sensor_cmd,
    ... )
    >>>
    >>> # Execute command
    >>> result = gateway.execute("light_turn_on", {
    ...     "entity_id": "light.living_room"
    ... })
    >>>
    >>> # List available commands
    >>> commands = gateway.list_commands()
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

from EE.universal_gateway.domain_gateway import CommandNotFoundError
from EE.ha.ha_common import HAGatewayError
from EE.ha.ha_command_factory import HACommand


@dataclass
class HACommandGateway:
    """Gateway for managing and executing HA commands.

    The HACommandGateway provides a centralized registry for all HA commands
    with execution support and command discovery. It acts as the command
    execution layer in the HA domain gateway architecture.

    Attributes:
        commands: Dictionary mapping command names to HACommand instances

    Example:
        >>> gateway = HACommandGateway(commands={
        ...     "light_turn_on": light_on_command,
        ...     "light_turn_off": light_off_command,
        ... })
        >>>
        >>> # Execute a command
        >>> result = gateway.execute("light_turn_on", {
        ...     "entity_id": "light.living_room",
        ...     "brightness": 255
        ... })
        >>>
        >>> # List all commands
        >>> commands = gateway.list_commands()
        >>> # {"light_turn_on": "HACommand", "light_turn_off": "HACommand"}
    """

    commands: Dict[str, HACommand]

    def execute(self, name: str, payload: dict) -> Any:
        """Execute an HA command by name.

        Args:
            name: Command name (e.g., "light_turn_on", "sensor_get_state")
            payload: Command parameters as dictionary

        Returns:
            Command execution result

        Raises:
            CommandNotFoundError: If command name is not registered
            HAGatewayError: If command execution fails

        Example:
            >>> gateway = create_ha_command_gateway(...)
            >>> result = gateway.execute("light_turn_on", {
            ...     "entity_id": "light.living_room"
            ... })
        """
        if name not in self.commands:
            available = list(self.commands.keys())
            raise CommandNotFoundError(
                command_name=name,
                available_commands=available,
                context={
                    "domain": "ha",
                    "operation": "execute_command",
                    "payload": payload,
                },
            )

        command = self.commands[name]
        try:
            return command.execute(payload)
        except HAGatewayError:
            # Re-raise HA errors as-is
            raise
        except Exception as e:
            # Wrap other exceptions
            raise HAGatewayError(
                f"HA command '{name}' execution failed: {str(e)}",
                error_code="HA_COMMAND_EXECUTION_ERROR",
                context={
                    "command_name": name,
                    "payload": payload,
                },
                operation="command_execute",
            ) from e

    def has_command(self, name: str) -> bool:
        """Check if a command is registered.

        Args:
            name: Command name to check

        Returns:
            True if command exists, False otherwise

        Example:
            >>> if gateway.has_command("light_turn_on"):
            ...     gateway.execute("light_turn_on", {...})
        """
        return name in self.commands

    def get_command(self, name: str) -> HACommand:
        """Get a command by name without executing it.

        Useful for inspection or pre-flight validation.

        Args:
            name: Command name

        Returns:
            HACommand instance

        Raises:
            CommandNotFoundError: If command is not registered

        Example:
            >>> command = gateway.get_command("light_turn_on")
            >>> # Validate payload before execution
            >>> validated = command.validate({"entity_id": "light.kitchen"})
        """
        if name not in self.commands:
            available = list(self.commands.keys())
            raise CommandNotFoundError(
                command_name=name,
                available_commands=available,
                context={
                    "domain": "ha",
                    "operation": "get_command",
                },
            )

        return self.commands[name]

    def list_commands(self) -> Dict[str, str]:
        """List all registered commands with their type names.

        Returns:
            Dictionary mapping command names to their types

        Example:
            >>> gateway.list_commands()
            {
                "light_turn_on": "HACommand",
                "light_turn_off": "HACommand",
                "sensor_get_state": "HACommand",
            }
        """
        return {
            name: type(cmd).__name__
            for name, cmd in self.commands.items()
        }

    def list_command_info(self) -> Dict[str, Dict[str, Any]]:
        """List detailed information about all commands.

        Returns:
            Dictionary with command metadata including:
            - name: Command name
            - type: Command type
            - has_serializer: Whether command has serializer
            - handler_name: Handler function name (if available)

        Example:
            >>> gateway.list_command_info()
            {
                "light_turn_on": {
                    "name": "light_turn_on",
                    "type": "HACommand",
                    "has_serializer": True,
                    "handler_name": "turn_on_handler"
                },
                ...
            }
        """
        return {
            name: {
                "name": name,
                "type": type(cmd).__name__,
                "has_serializer": cmd.serializer is not None,
                "handler_name": (
                    cmd.handler.__name__
                    if hasattr(cmd.handler, '__name__')
                    else str(cmd.handler)
                ),
            }
            for name, cmd in self.commands.items()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get gateway statistics.

        Returns:
            Dictionary with gateway stats

        Example:
            >>> gateway.get_stats()
            {
                "total_commands": 5,
                "commands_with_serializers": 3,
                "command_names": ["light_turn_on", ...]
            }
        """
        return {
            "total_commands": len(self.commands),
            "commands_with_serializers": sum(
                1 for cmd in self.commands.values() if cmd.serializer is not None
            ),
            "command_names": list(self.commands.keys()),
        }


def create_ha_command_gateway(**commands: HACommand) -> HACommandGateway:
    """Factory function to create an HACommandGateway.

    This factory provides a clean interface for creating an HA command gateway
    with all registered commands. Use keyword arguments to name each command.

    Args:
        **commands: Keyword arguments mapping command names to HACommand instances
            - Key: Command name (e.g., "light_turn_on", "sensor_get")
            - Value: HACommand instance

    Returns:
        Configured HACommandGateway instance

    Raises:
        ValueError: If no commands provided or if commands are not HACommand instances

    Example:
        >>> from ee.gateway.ha import create_ha_command, create_ha_command_gateway
        >>>
        >>> # Create commands
        >>> light_on = create_ha_command(
        ...     name="light.turn_on",
        ...     schema=LightTurnOnSchema(),
        ...     template=LightTemplate(),
        ...     handler=light_handler,
        ... )
        >>>
        >>> light_off = create_ha_command(
        ...     name="light.turn_off",
        ...     schema=LightTurnOffSchema(),
        ...     template=LightTemplate(),
        ...     handler=light_handler,
        ... )
        >>>
        >>> # Create gateway
        >>> gateway = create_ha_command_gateway(
        ...     light_turn_on=light_on,
        ...     light_turn_off=light_off,
        ...     sensor_get_state=sensor_cmd,
        ... )
        >>>
        >>> # Use gateway
        >>> result = gateway.execute("light_turn_on", {
        ...     "entity_id": "light.living_room"
        ... })

    Common Command Naming Patterns:
        - Use underscores for command names: "light_turn_on", "sensor_get_state"
        - Use domain_entity_action pattern: "light_turn_on", "automation_trigger"
        - Be consistent with naming across your gateway
        - Use descriptive names that indicate the HA domain and action
    """
    # Validate that commands are provided
    if not commands:
        raise ValueError("At least one command must be provided")

    # Validate that all values are HACommand instances
    for name, command in commands.items():
        if not isinstance(command, HACommand):
            raise ValueError(
                f"Command '{name}' must be an HACommand instance, "
                f"got {type(command).__name__}"
            )

    return HACommandGateway(commands=dict(commands))


__all__ = [
    'HACommandGateway',
    'create_ha_command_gateway',
]
