# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Add YAML handler module for config system

"""YAML handler module for LEE configuration system.

Provides safe YAML operations using PyYAML with security-focused defaults.
All operations use SafeLoader/SafeDumper to prevent arbitrary code execution.
"""

from pathlib import Path
from typing import Any, Optional, Union

from lee.utils.yaml import (
    YAMLError,
    safe_load as yaml_safe_load,
    safe_dump as yaml_safe_dump,
)


def load_yaml_file(filepath: Union[str, Path]) -> dict[str, Any]:
    """Load YAML file safely.

    Args:
        filepath: Path to YAML file (str or Path object)

    Returns:
        Parsed YAML content as dictionary

    Raises:
        YAMLError: If YAML parsing fails
        IOError: If file cannot be read

    """
    path = Path(filepath)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    data = yaml_safe_load(content)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise YAMLError(f"YAML file must contain dictionary, got {type(data).__name__}")
    return data


def load_yaml_string(yaml_string: str) -> Any:
    """Parse YAML string safely.

    Args:
        yaml_string: YAML content as string

    Returns:
        Parsed YAML object (typically dict or list)

    Raises:
        YAMLError: If YAML parsing fails

    """
    return yaml_safe_load(yaml_string)


def dump_yaml(
    data: Any,
    filepath: Optional[Union[str, Path]] = None,
    **kwargs: Any
) -> Optional[str]:
    """Serialize data to YAML safely.

    Args:
        data: Python object to serialize
        filepath: Optional path to write YAML file
        **kwargs: Additional arguments for safe_dump (default_flow_style=False)

    Returns:
        YAML string if filepath is None, None if written to file

    """
    kwargs.setdefault('default_flow_style', False)
    kwargs.setdefault('sort_keys', False)

    yaml_str = yaml_safe_dump(data, **kwargs)

    if filepath is not None:
        path = Path(filepath)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(yaml_str)
        return None

    return yaml_str


def validate_yaml(yaml_string: str) -> dict[str, Any]:
    """Validate YAML syntax without parsing.

    Args:
        yaml_string: YAML content to validate

    Returns:
        Dictionary with validation result:
        - valid (bool): True if YAML is valid
        - error (str, optional): Error message if invalid

    """
    try:
        yaml_safe_load(yaml_string)
        return {'valid': True}
    except YAMLError as e:
        return {'valid': False, 'error': str(e)}
