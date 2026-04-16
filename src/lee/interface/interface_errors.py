"""interface/interface_errors.py
Version: 2026-04-02_1
Purpose: Standardized error handling for interface routers
License: Apache 2.0

Provides consistent error types, messages, and handling patterns
for all interface routers in the LEE project.
"""

from typing import Any, Optional


class InterfaceError(Exception):
    """Base exception for all interface errors."""


class InterfaceUnavailableError(InterfaceError):
    """Raised when interface module cannot be imported."""

    def __init__(self, interface_name: str, import_error: str) -> None:
        self.interface_name = interface_name
        self.import_error = import_error
        super().__init__(
            f"{interface_name} interface unavailable: {import_error}"
        )


class UnknownOperationError(InterfaceError):
    """Raised when invalid operation is requested."""

    def __init__(
        self,
        interface_name: str,
        operation: str,
        valid_operations: Optional[list[str]] = None,
    ) -> None:
        self.interface_name = interface_name
        self.operation = operation
        self.valid_operations = valid_operations

        if valid_operations:
            valid_list = ", ".join(sorted(valid_operations))
            message = (
                f"Unknown {interface_name} operation: '{operation}'. "
                f"Valid operations: {valid_list}"
            )
        else:
            message = f"Unknown {interface_name} operation: '{operation}'"

        super().__init__(message)


class MissingParameterError(InterfaceError):
    """Raised when required parameter is missing."""

    def __init__(
        self,
        interface_name: str,
        operation: str,
        parameter_name: str,
    ) -> None:
        self.interface_name = interface_name
        self.operation = operation
        self.parameter_name = parameter_name
        super().__init__(
            f"{interface_name}.{operation} requires '{parameter_name}' parameter"
        )


class InvalidParameterTypeError(InterfaceError):
    """Raised when parameter has wrong type."""

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        interface_name: str,
        operation: str,
        parameter_name: str,
        expected_type: str,
        actual_type: str,
    ) -> None:
        self.interface_name = interface_name
        self.operation = operation
        self.parameter_name = parameter_name
        self.expected_type = expected_type
        self.actual_type = actual_type
        super().__init__(
            f"{interface_name}.{operation} '{parameter_name}' must be "
            f"{expected_type}, got {actual_type}"
        )


def validate_required_parameter(
    interface_name: str,
    operation: str,
    kwargs: dict[str, Any],
    parameter_name: str,
) -> None:
    """Validate that required parameter exists.

    Args:
        interface_name: Name of interface (e.g., 'cache', 'config')
        operation: Operation being performed
        kwargs: Keyword arguments passed to operation
        parameter_name: Name of required parameter

    Raises:
        MissingParameterError: If parameter missing

    """
    if parameter_name not in kwargs:
        raise MissingParameterError(
            interface_name,
            operation,
            parameter_name,
        )


def validate_parameter_type(
    interface_name: str,
    operation: str,
    kwargs: dict[str, Any],
    parameter_name: str,
    expected_type: type | tuple[type, ...],
) -> None:
    """Validate parameter type.

    Args:
        interface_name: Name of interface (e.g., 'cache', 'config')
        operation: Operation being performed
        kwargs: Keyword arguments passed to operation
        parameter_name: Name of parameter to validate
        expected_type: Expected type(s)

    Raises:
        InvalidParameterTypeError: If parameter has wrong type

    """
    if parameter_name not in kwargs:
        return

    value = kwargs[parameter_name]

    if isinstance(expected_type, tuple):
        type_names = ", ".join(t.__name__ for t in expected_type)
        if not isinstance(value, expected_type):
            raise InvalidParameterTypeError(
                interface_name,
                operation,
                parameter_name,
                type_names,
                type(value).__name__,
            )
    else:
        if not isinstance(value, expected_type):
            raise InvalidParameterTypeError(
                interface_name,
                operation,
                parameter_name,
                expected_type.__name__,
                type(value).__name__,
            )


def validate_string_parameter(
    interface_name: str,
    operation: str,
    kwargs: dict[str, Any],
    parameter_name: str,
    required: bool = True,
) -> None:
    """Validate string parameter.

    Convenience function combining required and type validation.

    Args:
        interface_name: Name of interface
        operation: Operation being performed
        kwargs: Keyword arguments
        parameter_name: Name of parameter
        required: Whether parameter is required

    Raises:
        MissingParameterError: If required parameter missing
        InvalidParameterTypeError: If parameter not a string

    """
    if required:
        validate_required_parameter(
            interface_name,
            operation,
            kwargs,
            parameter_name,
        )

    if parameter_name in kwargs:
        validate_parameter_type(
            interface_name,
            operation,
            kwargs,
            parameter_name,
            str,
        )


__all__ = [
    "InterfaceError",
    "InterfaceUnavailableError",
    "UnknownOperationError",
    "MissingParameterError",
    "InvalidParameterTypeError",
    "validate_required_parameter",
    "validate_parameter_type",
    "validate_string_parameter",
]
