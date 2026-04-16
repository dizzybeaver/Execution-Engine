"""lambda_diagnostic.py
Version: 2025-03-02_1
Purpose: Diagnostic mode handler (wrapper for DIAGNOSIS interface)
License: Apache 2.0
"""

# CRITICAL: sys.path fix for subdirectory imports
import os
import sys
from typing import Any

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Import gateway for SUGA-ISP compliant access
from lee.gateway import GatewayInterface, execute_operation

# Import standardized error handler
try:
    from lee.lee_utility.error_handler import create_error_response, handle_error
    _ERROR_HANDLER_AVAILABLE = True
except ImportError:
    _ERROR_HANDLER_AVAILABLE = False
    handle_error = None
    create_error_response = None


def lambda_handler(_event: dict[str, Any], _context: Any) -> dict[str, Any]:
    """Diagnostic mode handler - tests module imports sequentially.

    AWS Lambda Handler Setting: lambda_diagnostic.lambda_diagnostic_handler

    This handler tests the import chain for critical modules in dependency order.
    Returns diagnostic information about the Lambda environment.

    Args:
        event: Lambda event (can be empty for diagnostics)
        context: Lambda context

    Returns:
        Diagnostic response with import results

    """
    # Define critical modules to test in order
    modules = [
        # Core gateway (most critical)
        "gateway.gateway_core",
        "gateway.gateway_enums",

        # Core implementations
        "singleton.singleton_generic",
        "lee_config.config_state",
        "lee_logging.logging_generic",
        "lee_security.security_validation",
        "lee_utility.utility_core",

        # Interface routers
        "interface.interface_singleton",
        "interface.interface_config",
        "interface.interface_logging",
        "interface.interface_metrics",
        "interface.interface_security",
        "interface.interface_http",
        "interface.interface_websocket",
        "interface.interface_cache",
        "interface.interface_circuit_breaker",
        "interface.interface_debug",
        "interface.interface_diagnosis",
        "interface.interface_initialization",
        "interface.interface_test",
        "interface.interface_utility",

        # HA extension (conditional)
        "home_assistant.ha_gateway_generic",
        "home_assistant.ha_gateway_enums",
        "home_assistant.ha_interconnect",
    ]

    # Use DIAGNOSIS interface via gateway (SUGA-ISP compliant)
    try:
        result = execute_operation(
            GatewayInterface.DIAGNOSIS,
            "test_import_sequence",
            modules=modules,
        )
        return result
    except (ImportError, AttributeError) as e:
        # Gateway unavailable - acceptable for diagnostic mode
        if create_error_response:
            return create_error_response(
                error=e,
                operation="test_import_sequence",
                error_category="Gateway Unavailable",
                context="DIAGNOSIS interface not available"
            )
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "DIAGNOSIS interface unavailable",
            "modules_tested": len(modules),
            "tested_modules": modules,
        }
    except (ValueError, TypeError, KeyError) as e:
        # Invalid input - module list malformed
        if _ERROR_HANDLER_AVAILABLE:
            handle_error(e, operation_name="test_import_sequence", re_raise=False)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Invalid module list format",
            "modules_tested": len(modules),
            "tested_modules": modules,
        }
    except (ConnectionError, TimeoutError, OSError) as e:
        # Network or system errors during gateway operations
        if _ERROR_HANDLER_AVAILABLE:
            handle_error(e, operation_name="test_import_sequence", re_raise=False)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Network or system error in diagnostic handler",
            "modules_tested": len(modules),
            "tested_modules": modules,
        }
    except NameError as e:
        # Gateway operation interface errors
        if _ERROR_HANDLER_AVAILABLE:
            handle_error(e, operation_name="test_import_sequence", re_raise=False)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Gateway interface error in diagnostic handler",
            "modules_tested": len(modules),
            "tested_modules": modules,
        }
    except RuntimeError as e:
        # Runtime errors from gateway state issues
        if _ERROR_HANDLER_AVAILABLE:
            handle_error(e, operation_name="test_import_sequence", re_raise=False)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "Runtime error in diagnostic handler",
            "modules_tested": len(modules),
            "tested_modules": modules,
        }


# EOF
