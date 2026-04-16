"""interface/interface_config.py
Version: 2026-03-22_1
Purpose: Config interface router with dispatch dictionary
License: Apache 2.0

CHANGES (2026-03-22_1):
- Refactored to blueprint pattern - import from lee_config/ domain
- Static dispatch dictionary with metadata
- Direct function references instead of lambda wrappers
"""

from typing import Any

from lee.interface.interface_common import validate_module_available
from lee.interface.interface_errors import (
    UnknownOperationError,
    validate_string_parameter,
)

# Import domain functions directly (BLUEPRINT PATTERN)
try:
    from lee.lee_config import (
        get_category_config,
        get_config_manager,
        get_parameter,
        get_state,
        initialize_config,
        load_from_environment,
        load_from_file,
        load_yaml_file,
        load_yaml_string,
        reload_config,
        set_parameter,
        switch_preset,
        validate_all_sections,
        validate_yaml,
        dump_yaml,
    )
    _CONFIG_AVAILABLE = True
    _CONFIG_IMPORT_ERROR = None
except ImportError as e:
    _CONFIG_AVAILABLE = False
    _CONFIG_IMPORT_ERROR = str(e)


def _validate_key_param(
    kwargs: dict[str, Any],
    operation: str,
) -> None:
    """Validate key parameter exists and is string."""
    validate_string_parameter("config", operation, kwargs, "key")


def _validate_set_params(kwargs: dict[str, Any]) -> None:
    """Validate set operation parameters."""
    _validate_key_param(kwargs, "set")
    if "value" not in kwargs:
        raise ValueError("config.set requires 'value' parameter")


def _validate_category_param(kwargs: dict[str, Any]) -> None:
    """Validate category parameter."""
    validate_string_parameter(
        "config",
        "get_category",
        kwargs,
        "category",
    )


def _validate_preset_param(kwargs: dict[str, Any]) -> None:
    """Validate preset_name parameter."""
    validate_string_parameter(
        "config",
        "switch_preset",
        kwargs,
        "preset_name",
    )


def _validate_filepath_param(kwargs: dict[str, Any]) -> None:
    """Validate filepath parameter."""
    validate_string_parameter(
        "config",
        "load_file",
        kwargs,
        "filepath",
    )


def _validate_yaml_string_param(kwargs: dict[str, Any]) -> None:
    """Validate yaml_string parameter."""
    validate_string_parameter(
        "config",
        "safe_load",
        kwargs,
        "yaml_string",
    )


def _get_lambda(**kw) -> Any:
    """Get parameter with default support."""
    return get_parameter(kw["key"], kw.get("default"))


def _set_lambda(**kw) -> Any:
    """Set parameter value."""
    return set_parameter(kw["key"], kw["value"])


def _build_dispatch_dict() -> dict[str, dict[str, Any]]:
    """Build static dispatch dictionary (DDS) for config operations."""
    return {
        "initialize": {
            "func": initialize_config,
            "category": "admin",
            "description": "Initialize configuration system",
        },
        "get": {
            "func": _get_lambda,
            "category": "read",
            "description": "Get configuration parameter by key",
        },
        "get_parameter": {
            "func": _get_lambda,
            "category": "read",
            "description": "Alias for get - get parameter",
        },
        "set": {
            "func": _set_lambda,
            "category": "write",
            "description": "Set configuration parameter value",
        },
        "set_parameter": {
            "func": _set_lambda,
            "category": "write",
            "description": "Alias for set - set parameter",
        },
        "get_category": {
            "func": lambda **kw: get_category_config(kw["category"]),
            "category": "read",
            "description": "Get all parameters in a category",
        },
        "get_state": {
            "func": lambda **kw: get_state(),
            "category": "read",
            "description": "Get configuration system state",
        },
        "reload": {
            "func": lambda **kw: reload_config(kw.get("validate", True)),
            "category": "admin",
            "description": "Reload configuration from source",
        },
        "switch_preset": {
            "func": lambda **kw: switch_preset(kw["preset_name"]),
            "category": "write",
            "description": "Switch to a configuration preset",
        },
        "load_environment": {
            "func": load_from_environment,
            "category": "write",
            "description": "Load configuration from environment",
        },
        "load_file": {
            "func": lambda **kw: load_from_file(kw["filepath"]),
            "category": "write",
            "description": "Load configuration from file",
        },
        "validate_all": {
            "func": validate_all_sections,
            "category": "admin",
            "description": "Validate all configuration sections",
        },
        "reset": {
            "func": lambda **kw: get_config_manager().reset(),
            "category": "admin",
            "description": "Reset configuration to defaults",
        },
        "load_yaml": {
            "func": lambda **kw: load_yaml_file(kw["filepath"]),
            "category": "write",
            "description": "Load YAML configuration file",
        },
        "safe_load": {
            "func": lambda **kw: load_yaml_string(kw["yaml_string"]),
            "category": "read",
            "description": "Parse YAML string safely",
        },
        "safe_dump": {
            "func": lambda **kw: dump_yaml(kw["data"], kw.get("filepath")),
            "category": "write",
            "description": "Serialize data to YAML safely",
        },
        "validate_yaml": {
            "func": lambda **kw: validate_yaml(kw["yaml_string"]),
            "category": "read",
            "description": "Validate YAML syntax",
        },
        "get_config_manager": {
            "func": lambda **kw: get_config_manager(),
            "category": "read",
            "description": "Get configuration manager instance",
        },
    }


_OPERATION_DISPATCH = _build_dispatch_dict() if _CONFIG_AVAILABLE else {}


def execute_config_operation(operation: str, **kwargs) -> Any:
    """Route config operations to implementations.

    Operations:
        - initialize: Initialize configuration system
        - get/get_parameter: Get configuration parameter
        - set/set_parameter: Set configuration parameter
        - get_category: Get category configuration
        - reload: Reload configuration
        - switch_preset: Switch to preset
        - get_state: Get configuration state
        - load_environment: Load from environment
        - load_file: Load from file
        - validate_all: Validate all sections
        - reset: Reset configuration
        - load_yaml: Load YAML file
        - safe_load: Parse YAML string safely
        - safe_dump: Serialize data to YAML
        - validate_yaml: Validate YAML syntax

    """
    validate_module_available("config", _CONFIG_AVAILABLE, _CONFIG_IMPORT_ERROR)

    if operation not in _OPERATION_DISPATCH:
        raise UnknownOperationError(
            "config",
            operation,
            list(_OPERATION_DISPATCH.keys()),
        )

    # Parameter validation
    if operation in ["get", "get_parameter", "set", "set_parameter"]:
        _validate_key_param(kwargs, operation)
    if operation in ["set", "set_parameter"]:
        _validate_set_params(kwargs)
    if operation == "get_category":
        _validate_category_param(kwargs)
    if operation == "switch_preset":
        _validate_preset_param(kwargs)
    if operation in ["load_file", "load_yaml"]:
        _validate_filepath_param(kwargs)
    if operation in ["safe_load", "validate_yaml"]:
        _validate_yaml_string_param(kwargs)

    dispatch_entry = _OPERATION_DISPATCH[operation]
    handler = dispatch_entry["func"]
    return handler(**kwargs)


__all__ = ["execute_config_operation"]
