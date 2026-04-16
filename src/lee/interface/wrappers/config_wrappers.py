"""interface/wrappers/config_wrappers.py
Version: 2026-04-11_1 (Consolidated with base_wrapper)
Purpose: Config interface wrappers (SUGA-ISP compliant)
License: Apache 2.0

CONSOLIDATION:
- Removed duplicate correlation ID generation
- Uses base_wrapper module for common patterns
- Reduced code by ~15 lines
"""

from typing import Any

from lee.lee_config.config_loader import (
    load_from_environment,
    load_from_file,
)
from lee.lee_config.config_parameters import (
    get_category_config,
    get_parameter,
    get_state,
    initialize_config,
    set_parameter,
)
from lee.lee_config.config_presets import switch_preset
from lee.lee_config.config_validator import validate_all_sections


def config_initialize(correlation_id: str = None, **kwargs) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Initialize configuration system."""
    return initialize_config(**kwargs)


def config_get_parameter(key: str, default: Any = None, correlation_id: str = None) -> Any:  # pylint: disable=unused-argument
    """Get configuration parameter with SSM-first priority."""
    return get_parameter(key=key, default=default)


def config_set_parameter(key: str, value: Any, correlation_id: str = None) -> bool:  # pylint: disable=unused-argument
    """Set configuration parameter."""
    return set_parameter(key=key, value=value)


def config_get_category(category: str, correlation_id: str = None) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Get configuration category."""
    return get_category_config(category=category)


def config_get_state(correlation_id: str = None) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Get configuration state."""
    return get_state()


def config_reload(validate: bool = True, correlation_id: str = None) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Reload configuration."""
    from lee.lee_config.config_loader import reload_config as _reload_config  # pylint: disable=import-outside-toplevel
    return _reload_config(validate=validate)


def config_switch_preset(preset_name: str, correlation_id: str = None) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Switch configuration preset."""
    return switch_preset(preset_name=preset_name)


def config_load_environment(correlation_id: str = None) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Load configuration from environment variables."""
    return load_from_environment()


def config_load_file(filepath: str, correlation_id: str = None) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Load configuration from file."""
    return load_from_file(filepath=filepath)


def config_validate_all(correlation_id: str = None) -> dict[str, Any]:  # pylint: disable=unused-argument
    """Validate all configuration."""
    return validate_all_sections()


def config_reset(correlation_id: str = None, **kwargs) -> bool:  # pylint: disable=unused-argument
    """Reset configuration state."""
    from lee.lee_config.config_parameters import reset_config  # pylint: disable=import-outside-toplevel,no-name-in-module
    return reset_config(**kwargs)


# Legacy wrappers using base_wrapper

from lee.interface.wrappers.base_wrapper import (  # pylint: disable=wrong-import-position
    create_legacy_wrapper,
)

switch_config_preset = create_legacy_wrapper(
    config_switch_preset,
    "switch_config_preset"
)

load_config_from_environment = create_legacy_wrapper(
    config_load_environment,
    "load_config_from_environment"
)

load_config_from_file = create_legacy_wrapper(
    config_load_file,
    "load_config_from_file"
)

validate_all_config = create_legacy_wrapper(
    config_validate_all,
    "validate_all_config"
)


__all__ = [
    # Standardized wrappers
    "config_initialize",
    "config_get_parameter",
    "config_set_parameter",
    "config_get_category",
    "config_get_state",
    "config_reload",
    "config_switch_preset",
    "config_load_environment",
    "config_load_file",
    "config_validate_all",
    "config_reset",

    # Legacy wrappers
    "switch_config_preset",
    "load_config_from_environment",
    "load_config_from_file",
    "validate_all_config",
]
