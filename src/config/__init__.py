"""
config/__init__.py
Version: 2025-12-09_1
Purpose: Config module public API
License: Apache 2.0
"""

from config.config_core import (
    ConfigurationCore,
    get_config_manager
)

from config.config_parameters import (
    initialize_config,
    get_parameter,
    set_parameter,
    get_category_config,
    get_state
)

from config.config_loader import (
    load_from_environment,
    load_from_file,
    reload_config
)

from config.config_presets import (
    switch_preset,
    get_preset_list
)

from config.config_validator import (
    validate_all_sections,
    ConfigurationValidator
)

__all__ = [
    'ConfigurationCore',
    'get_config_manager',
    'initialize_config',
    'get_parameter',
    'set_parameter',
    'get_category_config',
    'get_state',
    'load_from_environment',
    'load_from_file',
    'reload_config',
    'switch_preset',
    'get_preset_list',
    'validate_all_sections',
    'ConfigurationValidator'
]
