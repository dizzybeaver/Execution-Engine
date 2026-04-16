# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-08 - Added _is_debug_mode, replaced print statement

"""config/config_presets.py
Version: 2025-12-09_1
Purpose: Configuration preset management
License: Apache 2.0
"""

import os
from typing import Any
from contextlib import nullcontext

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.lee_config.config_generic import get_config_manager

# Cache debug mode check at module load time
_DEBUG_MODE_ENABLED = os.getenv("LEE_DEBUG", "false").lower() == "true"


def _is_debug_mode() -> bool:
    """Check if LEE_DEBUG is enabled (cached value)."""
    return _DEBUG_MODE_ENABLED

# Configuration presets
_PRESETS = {
    "minimal": {
        "description": "Minimal resource usage",
        "config": {
            "cache.enabled": "false",
            "metrics.enabled": "false",
            "logging.level": "ERROR",
        },
    },
    "standard": {
        "description": "Standard production configuration",
        "config": {
            "cache.enabled": "true",
            "cache.ttl": "300",
            "metrics.enabled": "true",
            "logging.level": "INFO",
        },
    },
    "debug": {
        "description": "Debug mode with verbose logging",
        "config": {
            "cache.enabled": "true",
            "metrics.enabled": "true",
            "logging.level": "DEBUG",
            "debug.enabled": "true",
        },
    },
    "performance": {
        "description": "Performance optimized",
        "config": {
            "cache.enabled": "true",
            "cache.ttl": "600",
            "metrics.enabled": "true",
            "logging.level": "WARNING",
        },
    },
}


def switch_preset(preset_name: str) -> dict[str, Any]:
    """Switch to a configuration preset."""
    # SUGA-ISP compliant correlation ID generation
    corr_id = generate_correlation_id("cfg")

    manager = get_config_manager()

    try:
        # SUGA-ISP compliant timing
        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=corr_id, scope="CONFIG",
                                         operation_name="switch_preset")
        except (ImportError, RuntimeError):
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=corr_id, scope="CONFIG",
                               message="Switching preset", preset=preset_name)
            except ImportError:
                # Optional dependency - continue if unavailable
                ...

            if preset_name not in _PRESETS:
                return {
                    "success": False,
                    "error": f"Unknown preset: {preset_name}",
                    "available": list(_PRESETS.keys()),
                }

            preset = _PRESETS[preset_name]

            # Apply preset configuration
            for key, value in preset["config"].items():
                manager.set_parameter(key, value)

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=corr_id, scope="CONFIG",
                               message="Preset applied",
                               preset=preset_name,
                               param_count=len(preset["config"]))
            except ImportError:
                # Optional dependency - continue if unavailable
                ...

            return {
                "success": True,
                "preset": preset_name,
                "description": preset["description"],
                "applied_count": len(preset["config"]),
            }

    except (ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Switch preset failed ({preset_name}): {e}",
                           error_type=type(e).__name__)
        except (ImportError, AttributeError, KeyError, TypeError):
            if _is_debug_mode():
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                   message=f"Switch preset failed ({preset_name}): {e}",
                                   scope="CONFIG")
                except (ImportError, AttributeError, KeyError, TypeError):
                    pass
        return {"success": False, "error": str(e)}


def get_preset_list() -> list[dict[str, str]]:
    """Get list of available presets."""
    return [
        {
            "name": name,
            "description": preset["description"],
        }
        for name, preset in _PRESETS.items()
    ]


def get_preset_config(preset_name: str) -> dict[str, Any]:
    """Get configuration for a specific preset."""
    if preset_name not in _PRESETS:
        return {}

    return _PRESETS[preset_name]["config"].copy()


__all__ = [
    "get_preset_config",
    "get_preset_list",
    "switch_preset",
]
