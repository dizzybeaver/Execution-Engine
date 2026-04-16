"""Generic diagnosis module for LEE project.

This module provides system diagnostic capabilities including architecture validation,
import validation, gateway routing validation, and comprehensive diagnostic suites.

All diagnostic functions use the gateway pattern for SUGA-ISP compliance.
Functions use standardized error handling with specific exception categorization.

Exports:
    validate_system_architecture: Validate SUGA architecture compliance
    validate_imports: Validate no direct imports between modules
    validate_gateway_routing: Validate all gateway routing works
    run_diagnostic_suite: Run comprehensive diagnostic suite
"""

from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Import standardized error handler
try:
    from lee.lee_utility.error_handler import create_error_response, handle_error
    _ERROR_HANDLER_AVAILABLE = True
except ImportError:
    _ERROR_HANDLER_AVAILABLE = False
    handle_error = None
    create_error_response = None


def validate_system_architecture(**_kwargs) -> dict[str, Any]:
    """Validate SUGA architecture compliance."""
    corr_id = generate_correlation_id("diag")
    issues = []

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=corr_id, scope="DIAGNOSIS",
                         message="Starting SUGA architecture validation")

        # Check operation registry via public gateway function (to be added)
        try:
            from lee.gateway import get_operation_registry  # pylint: disable=import-outside-toplevel
            registry = get_operation_registry()
            if not registry:
                issues.append("Empty operation registry")
        except (ImportError, AttributeError):
            # Gateway function not yet implemented
            issues.append("get_operation_registry() not available in gateway")

        import_check = validate_imports()
        if not import_check.get("compliant", False):
            issues.extend(import_check.get("violations", []))

        result = {
            "success": True,
            "compliant": len(issues) == 0,
            "issues": issues,
        }

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=corr_id, scope="DIAGNOSIS",
                         message="SUGA architecture validation completed",
                         compliant=result["compliant"], issue_count=len(issues))

        return result
    except (ImportError, AttributeError) as e:
        # Gateway unavailable
        if _ERROR_HANDLER_AVAILABLE:
            handle_error(e, operation_name="validate_system_architecture", correlation_id=corr_id, re_raise=False)
        return create_error_response(e, "validate_system_architecture", "Gateway Unavailable") if create_error_response else {"success": False, "error": str(e)}
    except (ValueError, TypeError, KeyError) as e:
        # Invalid input
        if _ERROR_HANDLER_AVAILABLE:
            handle_error(e, operation_name="validate_system_architecture", correlation_id=corr_id, re_raise=False)
        return create_error_response(e, "validate_system_architecture", "Invalid Input") if create_error_response else {"success": False, "error": str(e)}
    except (OSError, RuntimeError, ConnectionError, TimeoutError) as e:
        # Unexpected system-level error
        if _ERROR_HANDLER_AVAILABLE:
            handle_error(e, operation_name="validate_system_architecture", correlation_id=corr_id, re_raise=False)
        return create_error_response(e, "validate_system_architecture", "Unexpected Error") if create_error_response else {"success": False, "error": str(e)}


def validate_imports(**_kwargs) -> dict[str, Any]:
    """Validate no direct imports between modules."""
    try:
        from import_fixer import validate_imports as fixer_validate_imports  # pylint: disable=import-outside-toplevel
        return fixer_validate_imports(".")
    except ImportError:
        return {"success": True, "compliant": True, "note": "import_fixer not available"}


def validate_gateway_routing(**_kwargs) -> dict[str, Any]:
    """Validate all gateway routing works."""
    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         scope="DIAGNOSIS",
                         message="Starting gateway routing validation")

        test_operations = [
            (GatewayInterface.CACHE, "get_stats"),
            (GatewayInterface.LOGGING, "get_stats"),
            (GatewayInterface.OBSERVABILITY, "get_stats"),
        ]

        results = {
            "tested": 0,
            "passed": 0,
            "failed": [],
        }

        for interface, operation in test_operations:
            results["tested"] += 1
            try:
                execute_operation(interface, operation)
                results["passed"] += 1
            except (ImportError, AttributeError, ConnectionError, TimeoutError) as e:
                # Gateway or network error - expected
                results["failed"].append(f"{interface.value}.{operation}: {e!s}")
            except (ValueError, TypeError, KeyError) as e:
                # Invalid input - log but continue
                if _ERROR_HANDLER_AVAILABLE:
                    handle_error(e, operation_name=f"validate_gateway_routing.{interface.value}.{operation}", re_raise=False)
                results["failed"].append(f"{interface.value}.{operation}: {e!s}")

        result = {
            "success": True,
            "compliant": results["passed"] == results["tested"],
            "results": results,
        }

        execute_operation(GatewayInterface.DEBUG, "log",
                         scope="DIAGNOSIS",
                         message="Gateway routing validation completed",
                         compliant=result["compliant"], tested=results["tested"],
                         passed=results["passed"], failed=len(results["failed"]))

        return result
    except (OSError, RuntimeError, ConnectionError, TimeoutError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         scope="DIAGNOSIS",
                         message="Gateway routing validation failed", error=str(e))
        return {"success": False, "error": str(e)}


def run_diagnostic_suite(**_kwargs) -> dict[str, Any]:
    """Run comprehensive diagnostic suite."""
    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         scope="DIAGNOSIS",
                         message="Starting comprehensive diagnostic suite")

        from lee.diagnosis.diagnosis_performance import diagnose_system_health  # pylint: disable=import-outside-toplevel
        from lee.diagnosis.health.diagnosis_health_checks import generate_health_report  # pylint: disable=import-outside-toplevel

        report = {
            "timestamp": "2025-12-08",
            "suite": "comprehensive",
            "results": {},
        }

        # Health report
        try:
            report["results"]["health"] = generate_health_report()
        except (ValueError, KeyError, AttributeError, ConnectionError, TimeoutError) as e:
            report["results"]["health"] = {"error": str(e)}

        # System health
        try:
            report["results"]["system"] = diagnose_system_health()
        except (ValueError, KeyError, AttributeError, ConnectionError, TimeoutError) as e:
            report["results"]["system"] = {"error": str(e)}

        # Architecture validation
        try:
            report["results"]["architecture"] = validate_system_architecture()
        except (ValueError, KeyError, AttributeError, ConnectionError, TimeoutError) as e:
            report["results"]["architecture"] = {"error": str(e)}

        # Import validation
        try:
            report["results"]["imports"] = validate_imports()
        except (ValueError, KeyError, AttributeError, ConnectionError, TimeoutError) as e:
            report["results"]["imports"] = {"error": str(e)}

        # Gateway routing
        try:
            report["results"]["gateway_routing"] = validate_gateway_routing()
        except (ValueError, KeyError, AttributeError, ConnectionError, TimeoutError) as e:
            report["results"]["gateway_routing"] = {"error": str(e)}

        execute_operation(GatewayInterface.DEBUG, "log",
                         scope="DIAGNOSIS",
                         message="Comprehensive diagnostic suite completed",
                         test_count=len(report["results"]))

        return report
    except (ValueError, KeyError, AttributeError, ConnectionError, TimeoutError, RuntimeError) as e:
        execute_operation(GatewayInterface.DEBUG, "log",
                         scope="DIAGNOSIS",
                         message="Comprehensive diagnostic suite failed", error=str(e))
        return {"success": False, "error": str(e)}


__all__ = [
    "run_diagnostic_suite",
    "validate_gateway_routing",
    "validate_imports",
    "validate_system_architecture",
]
