"""Config Wrapper Functions

Direct access to configuration operations (21 functions).
All functions execute via gateway internally.

Usage:
    from lee.gateway.wrappers import config

    # Initialize config
    config.initialize()

    # Get parameter
    value = config.get_parameter(name='HOME_ASSISTANT_URL')

    # Set parameter
    config.set_parameter(name='HOME_ASSISTANT_URL', value='http://localhost:8123')

    # Get category
    category = config.get_category(name='home_assistant')

    # Get config state
    state = config.get_state()

    # Reload config
    config.reload()

    # Switch preset
    config.switch_preset(preset_name='production')
"""

from typing import Any

from lee.gateway.gateway_core import GatewayInterface, execute_operation


def config_initialize(**kwargs: Any) -> dict[str, Any]:
    """Initialize configuration system.

    Args:
        **kwargs: Additional initialization options

    Returns:
        Configuration dictionary
    """
    return execute_operation(GatewayInterface.CONFIG, 'initialize', **kwargs)


def config_get_parameter(name: str, default: Any = None, **kwargs: Any) -> Any:
    """Get configuration parameter.

    Args:
        name: Parameter name
        default: Default value if not found
        **kwargs: Additional options

    Returns:
        Parameter value or default
    """
    return execute_operation(GatewayInterface.CONFIG, 'get', key=name, default=default, **kwargs)


def config_set_parameter(name: str, value: Any, **kwargs: Any) -> None:
    """Set configuration parameter.

    Args:
        name: Parameter name
        value: Parameter value
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.CONFIG, 'set', key=name, value=value, **kwargs)


def config_get_category(name: str, **kwargs: Any) -> dict[str, Any]:
    """Get configuration category.

    Args:
        name: Category name
        **kwargs: Additional options

    Returns:
        Category configuration dictionary
    """
    return execute_operation(GatewayInterface.CONFIG, 'get_category', name=name, **kwargs)


def config_get_state(**kwargs: Any) -> dict[str, Any]:
    """Get configuration state.

    Args:
        **kwargs: Additional options

    Returns:
        State dictionary
    """
    return execute_operation(GatewayInterface.CONFIG, 'get_state', **kwargs)


def config_reload(**kwargs: Any) -> None:
    """Reload configuration.

    Args:
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.CONFIG, 'reload', **kwargs)


def config_switch_preset(preset_name: str, **kwargs: Any) -> None:
    """Switch configuration preset.

    Args:
        preset_name: Preset name
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.CONFIG, 'switch_preset', preset_name=preset_name, **kwargs)


def config_load_environment(**kwargs: Any) -> None:
    """Load configuration from environment variables.

    Args:
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.CONFIG, 'load_environment', **kwargs)


def config_load_file(file_path: str, **kwargs: Any) -> None:
    """Load configuration from file.

    Args:
        file_path: Path to configuration file
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.CONFIG, 'load_file', file_path=file_path, **kwargs)


def config_validate_all(**kwargs: Any) -> tuple[bool, list[str]]:
    """Validate all configuration sections.

    Args:
        **kwargs: Additional options

    Returns:
        Tuple of (is_valid, error_messages)
    """
    return execute_operation(GatewayInterface.CONFIG, 'validate_all', **kwargs)


def config_reset(**kwargs: Any) -> None:
    """Reset configuration to defaults.

    Args:
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.CONFIG, 'reset', **kwargs)


def config_load_yaml(file_path: str, **kwargs: Any) -> dict[str, Any]:
    """Load YAML configuration file.

    Args:
        file_path: Path to YAML file
        **kwargs: Additional options

    Returns:
        Configuration dictionary
    """
    return execute_operation(GatewayInterface.CONFIG, 'load_yaml', filepath=file_path, **kwargs)


def config_safe_load(yaml_string: str, **kwargs: Any) -> Any:
    """Parse YAML string safely.

    Args:
        yaml_string: YAML content
        **kwargs: Additional options

    Returns:
        Parsed YAML object
    """
    return execute_operation(GatewayInterface.CONFIG, 'safe_load', yaml_string=yaml_string, **kwargs)


def config_safe_dump(data: Any, file_path: str | None = None, **kwargs: Any) -> str | None:
    """Serialize data to YAML safely.

    Args:
        data: Python object to serialize
        file_path: Optional file path to write
        **kwargs: Additional options

    Returns:
        YAML string if file_path is None, None otherwise
    """
    return execute_operation(GatewayInterface.CONFIG, 'safe_dump', data=data, filepath=file_path, **kwargs)


def config_validate_yaml(yaml_string: str, **kwargs: Any) -> dict[str, Any]:
    """Validate YAML syntax.

    Args:
        yaml_string: YAML content to validate
        **kwargs: Additional options

    Returns:
        Dict with 'valid' bool and optional 'error'
    """
    return execute_operation(GatewayInterface.CONFIG, 'validate_yaml', yaml_string=yaml_string, **kwargs)


# Aliases for backward compatibility
initialize_config = config_initialize
get_config = config_get_parameter
set_config = config_set_parameter
get_config_category = config_get_category
get_config_state = config_get_state
reload_config = config_reload
switch_config_preset = config_switch_preset
load_config_from_environment = config_load_environment
load_config_from_file = config_load_file
validate_all_config = config_validate_all


# Convenience aliases without config_ prefix
get = config_get_parameter
set = config_set_parameter
get_category = config_get_category
get_state = config_get_state
reload = config_reload
switch_preset = config_switch_preset

# YAML aliases
load_yaml = config_load_yaml
safe_load = config_safe_load
safe_dump = config_safe_dump
validate_yaml = config_validate_yaml


__all__ = [
    'config_initialize',
    'config_get_parameter',
    'config_set_parameter',
    'config_get_category',
    'config_get_state',
    'config_reload',
    'config_switch_preset',
    'config_load_environment',
    'config_load_file',
    'config_validate_all',
    'config_reset',
    'config_load_yaml',
    'config_safe_load',
    'config_safe_dump',
    'config_validate_yaml',
    # Aliases
    'initialize_config',
    'get_config',
    'set_config',
    'get_config_category',
    'get_config_state',
    'reload_config',
    'switch_config_preset',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config',
    # Convenience aliases
    'get',
    'set',
    'get_category',
    'get_state',
    'reload',
    'switch_preset',
    # YAML aliases
    'load_yaml',
    'safe_load',
    'safe_dump',
    'validate_yaml',
]
