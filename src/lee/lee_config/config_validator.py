# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-08 - Added _is_debug_mode, replaced print statement

"""config/config_validator.py
Version: 2025-12-09_1
Purpose: Configuration validation logic
License: Apache 2.0
"""

import os
from typing import Any
from contextlib import nullcontext

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Cache debug mode check at module load time
_DEBUG_MODE_ENABLED = os.getenv("LEE_DEBUG", "false").lower() == "true"


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled (cached value)."""
    return _DEBUG_MODE_ENABLED


# Lazy import to avoid circular dependency
def _get_config_manager():
    """Lazy import config manager to avoid circular dependency."""
    from lee.lee_config.config_generic import get_config_manager
    return get_config_manager


class ConfigurationValidator:
    """Configuration validation with debug integration."""

    def validate_parameter(self, key: str, value: Any) -> dict[str, Any]:
        """Validate a single parameter."""
        # SUGA-ISP compliant correlation ID generation
        corr_id = generate_correlation_id("cfg")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=corr_id, scope="CONFIG",
                           message="Validating parameter", key=key)
        except (ImportError, AttributeError):
            # Optional dependency - continue if unavailable
            ...

        # Basic validation rules
        if not isinstance(key, str) or not key:
            return {
                "valid": False,
                "error": "Key must be non-empty string",
            }

        if value is None:
            return {
                "valid": False,
                "error": "Value cannot be None",
            }

        return {"valid": True}

    def validate_section(self, section: str, config: dict[str, Any]) -> dict[str, Any]:
        """Validate a configuration section."""
        # SUGA-ISP compliant correlation ID generation
        corr_id = generate_correlation_id("cfg")

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=corr_id, scope="CONFIG",
                           message="Validating section", section=section)
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        errors = []

        # Validate each parameter in section
        for key, value in config.items():
            result = self.validate_parameter(key, value)
            if not result["valid"]:
                errors.append({
                    "key": key,
                    "error": result["error"],
                })

        return {
            "valid": len(errors) == 0,
            "section": section,
            "errors": errors,
        }

    def validate_all_sections(self, config: dict[str, Any] = None) -> dict[str, Any]:
        """Validate all configuration sections."""
        # SUGA-ISP compliant correlation ID generation
        corr_id = generate_correlation_id("cfg")
        if config is None:
            manager = _get_config_manager()
            config = manager.get_state()  # Use public method instead of _config

        try:
            # SUGA-ISP compliant timing
            try:
                timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                             corr_id=corr_id, scope="CONFIG",
                                             operation_name="validate_all")
            except (ImportError, RuntimeError):
                timing_ctx = nullcontext()

            with timing_ctx:
                # Group by sections
                sections = {}
                results = {}
                all_valid = True

                for key in config.keys():
                    # Validate key format before splitting
                    if not key or key.startswith('.'):
                        results[key] = {
                            "valid": False,
                            "error": "Invalid key format: keys cannot be empty or start with '.'"
                        }
                        all_valid = False
                        continue

                    if "." in key:
                        section = key.split(".")[0]
                    else:
                        section = "root"

                    if section not in sections:
                        sections[section] = {}
                    sections[section][key] = config[key]

                # Validate each section
                for section, section_config in sections.items():
                    result = self.validate_section(section, section_config)
                    results[section] = result
                    if not result["valid"]:
                        all_valid = False

                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                   corr_id=corr_id, scope="CONFIG",
                                   message="Validation complete",
                                   valid=all_valid, section_count=len(sections))
                except (ImportError, AttributeError):
                    # Optional dependency - continue if unavailable
                    ...

                return {
                    "valid": all_valid,
                    "sections": results,
                }

        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
            try:
                execute_operation(GatewayInterface.LOGGING, "log_error",
                               message=f"Validation failed: {e}",
                               error_type=type(e).__name__)
            except (ImportError, AttributeError, KeyError, TypeError):
                if _is_debug_mode():
                    try:
                        execute_operation(GatewayInterface.DEBUG, "log",
                                       message=f"Validation failed: {e}",
                                       scope="CONFIG")
                    except (ImportError, AttributeError, KeyError, TypeError):
                        pass
            return {
                "valid": False,
                "error": str(e),
            }


def validate_all_sections() -> dict[str, Any]:
    """Convenience function for validation."""
    validator = ConfigurationValidator()
    return validator.validate_all_sections()


__all__ = [
    "ConfigurationValidator",
    "validate_all_sections",
]
