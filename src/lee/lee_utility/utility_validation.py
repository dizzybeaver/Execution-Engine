"""utility/utility_validation.py
Version: 2025-12-13_1
Purpose: Validation operations for utility interface
License: Apache 2.0
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

if TYPE_CHECKING:
    from lee.lee_utility.utility_core import SharedUtilityCore


logger = logging.getLogger(__name__)


class UtilityValidationOperations:
    """Validation operations for strings, data structures, and parameters."""

    def __init__(self, manager: "SharedUtilityCore") -> None:
        """Initialize with reference to SharedUtilityCore manager."""
        self._manager = manager

    def validate_string(self, value: str, min_length: int = 0, max_length: int = 1000,
                       correlation_id: str = None) -> dict[str, Any]:
        """Validate string input."""
        # SUGA-ISP compliant correlation ID generation
        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="UTILITY",
                           message="String validation called", value=str(value)[:100])
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        if not isinstance(value, str):
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=correlation_id, scope="UTILITY",
                               message="String validation failed: not a string",
                               value_type=type(value).__name__)
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return {"valid": False, "error": "Value must be a string"}

        if len(value) < min_length:
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=correlation_id, scope="UTILITY",
                               message="String validation failed: too short",
                               length=len(value), min_length=min_length)
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return {"valid": False, "error": f"String too short (min: {min_length})"}

        if len(value) > max_length:
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=correlation_id, scope="UTILITY",
                               message="String validation failed: too long",
                               length=len(value), max_length=max_length)
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return {"valid": False, "error": f"String too long (max: {max_length})"}

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="UTILITY",
                           message="String validation passed",
                           length=len(value))
        except ImportError:
            # Optional dependency - continue if unavailable
            ...
        return {"valid": True}

    def validate_data_structure(self, data: Any, expected_type: type,
                               required_fields: Optional[list[str]] = None,
                               correlation_id: str = None) -> bool:
        """Validate data structure."""
        # SUGA-ISP compliant correlation ID generation
        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="UTILITY",
                           message="Data structure validation called",
                           expected_type=expected_type.__name__)
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        if not isinstance(data, expected_type):
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=correlation_id, scope="UTILITY",
                               message="Data structure validation failed: wrong type",
                               expected_type=expected_type.__name__, actual_type=type(data).__name__)
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return False

        if required_fields and isinstance(data, dict):
            for field in required_fields:
                if field not in data:
                    try:
                        execute_operation(GatewayInterface.DEBUG, "log",
                                       corr_id=correlation_id, scope="UTILITY",
                                       message="Data structure validation failed: missing field",
                                       field=field)
                    except ImportError:
                        # Optional dependency - continue if unavailable
                        ...
                    return False

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="UTILITY",
                           message="Data structure validation passed",
                           expected_type=expected_type.__name__)
        except ImportError:
            # Optional dependency - continue if unavailable
            ...
        return True

    def validate_operation_parameters(self, required_params: list[str],
                                     optional_params: Optional[list[str]] = None,
                                     correlation_id: str = None,
                                     **kwargs) -> dict[str, Any]:
        """Generic parameter validation for any interface operation."""
        # SUGA-ISP compliant correlation ID generation
        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="UTILITY",
                           message="Parameter validation called",
                           required_count=len(required_params))
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        missing = [param for param in required_params if param not in kwargs]

        if missing:
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=correlation_id, scope="UTILITY",
                               message="Parameter validation failed: missing params",
                               missing_params=missing)
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return {
                "valid": False,
                "missing_params": missing,
                "error": f"Missing required parameters: {', '.join(missing)}",
            }

        if optional_params:
            all_params = set(required_params + optional_params)
            unexpected = [k for k in kwargs if k not in all_params]

            if unexpected:
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="UTILITY",
                                   message="Parameter validation passed with warnings",
                                   unexpected_params=unexpected)
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                return {
                    "valid": True,
                    "warning": f"Unexpected parameters: {', '.join(unexpected)}",
                }

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="UTILITY",
                           message="Parameter validation passed",
                           required_count=len(required_params))
        except ImportError:
            # Optional dependency - continue if unavailable
            ...
        return {"valid": True}


__all__ = [
    "UtilityValidationOperations",
]
