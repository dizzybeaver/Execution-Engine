"""config/config_loader.py
Version: 2025-12-09_1
Purpose: Configuration loading from various sources
License: Apache 2.0
"""

import json
import os
from contextlib import nullcontext
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.lee_config.config_generic import get_config_manager


def load_from_environment() -> dict[str, Any]:
    """Load configuration from environment variables."""
    # SUGA-ISP compliant correlation ID generation
    corr_id = generate_correlation_id("cfg")

    try:
        # SUGA-ISP compliant timing
        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=corr_id, scope="CONFIG",
                                         operation="load_environment")
        except (ImportError, Exception):
            timing_ctx = nullcontext()

        with timing_ctx:
            config = {}

            # Load common config patterns
            env_prefixes = ["LEE_", "HA_", "LAMBDA_", "AWS_", "CONFIG_"]

            for key, value in os.environ.items():
                # Check if key matches known patterns
                for prefix in env_prefixes:
                    if key.startswith(prefix):
                        config[key] = value
                        break

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=corr_id, scope="CONFIG",
                               message="Environment loaded", key_count=len(config))
            except ImportError:
                # Optional dependency - continue if unavailable
                ...

            return config

    except Exception as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Load from environment failed: {e}")
        except (ImportError, Exception) as e:
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'(ImportError, Exception) occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available
        return {}


def load_from_file(filepath: str) -> dict[str, Any]:
    """Load configuration from file."""
    # SUGA-ISP compliant correlation ID generation
    corr_id = generate_correlation_id("cfg")

    try:
        # SUGA-ISP compliant timing
        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=corr_id, scope="CONFIG",
                                         operation="load_file")
        except (ImportError, Exception):
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=corr_id, scope="CONFIG",
                               message="Loading file", filepath=filepath)
            except ImportError:
                # Optional dependency - continue if unavailable
                ...

            with open(filepath, encoding="utf-8") as f:
                if filepath.endswith(".json"):
                    config = json.load(f)
                elif filepath.endswith((".yaml", ".yml")):
                    from lee.lee_config.yaml_handler import load_yaml_file
                    config = load_yaml_file(filepath)
                else:
                    # Simple key=value format
                    config = {}
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                config[key.strip()] = value.strip()

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=corr_id, scope="CONFIG",
                               message="File loaded",
                               filepath=filepath, key_count=len(config))
            except ImportError:
                # Optional dependency - continue if unavailable
                ...

            return config

    except Exception as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Load from file failed ({filepath}): {e}")
        except (ImportError, Exception) as e:
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'(ImportError, Exception) occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available
        return {}


def reload_config(validate: bool = True) -> dict[str, Any]:
    """Reload configuration from environment."""
    # SUGA-ISP compliant correlation ID generation
    corr_id = generate_correlation_id("cfg")

    manager = get_config_manager()

    try:
        # SUGA-ISP compliant timing
        try:
            timing_ctx = execute_operation(GatewayInterface.DEBUG, "timing",
                                         corr_id=corr_id, scope="CONFIG",
                                         operation="reload")
        except (ImportError, Exception):
            timing_ctx = nullcontext()

        with timing_ctx:
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=corr_id, scope="CONFIG",
                               message="Reloading config", validate=validate)
            except ImportError:
                # Optional dependency - continue if unavailable
                ...

            # Clear existing config
            manager._config.clear()

            # Reload from environment
            env_config = load_from_environment()
            manager._config.update(env_config)

            # Validate if requested
            if validate:
                from lee.lee_config.config_validator import validate_all_sections
                validation = validate_all_sections()

                if not validation.get("valid", True):
                    try:
                        execute_operation(GatewayInterface.LOGGING, "log_warning",
                                       message="Config validation failed after reload")
                    except (ImportError, Exception) as e:
                        try:
                            execute_operation(
                                GatewayInterface.LOGGING,
                                'log_error',
                                message=f'(ImportError, Exception) occurred: {e}',
                                corr_id=None
                            )
                        except (ImportError, AttributeError, RuntimeError):
                            pass  # Gateway not available
                    return {
                        "success": False,
                        "error": "Validation failed",
                        "validation": validation,
                    }

            return {
                "success": True,
                "parameter_count": len(manager._config),
            }

    except Exception as e:
        try:
            execute_operation(GatewayInterface.LOGGING, "log_error",
                           message=f"Config reload failed: {e}")
        except (ImportError, Exception) as e:
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f'(ImportError, Exception) occurred: {e}',
                    corr_id=None
                )
            except (ImportError, AttributeError, RuntimeError):
                pass  # Gateway not available
        return {"success": False, "error": str(e)}


def merge_configs(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Merge two configuration dictionaries."""
    merged = base.copy()
    merged.update(override)
    return merged


__all__ = [
    "load_from_environment",
    "load_from_file",
    "merge_configs",
    "reload_config",
]
