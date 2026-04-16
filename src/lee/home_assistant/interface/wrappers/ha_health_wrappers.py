"""ha_health_wrappers.py
Version: 2025-12-22_1
Purpose: Health interface internal wrappers (SUGA-ISP Implementation)
License: Apache 2.0

WARNING: This module contains INTERNAL wrapper functions for the Health router.
External modules MUST use ha_gateway.ha_execute_operation() instead of importing directly.
"""

from typing import Any

from lee.gateway.gateway_core import generate_correlation_id

try:
    from lee.home_assistant.ha_health.ha_health_core import (
        check_component_health_impl,
        check_system_health_impl,
        get_diagnostic_info_impl,
        get_performance_report_impl,
        test_connectivity_impl,
    )
    _HEALTH_AVAILABLE = True
    _HEALTH_IMPORT_ERROR = None
except ImportError as e:
    _HEALTH_AVAILABLE = False
    _HEALTH_IMPORT_ERROR = str(e)


def check_system_health(correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Check overall Home Assistant system health."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("hah")

    try:
        from lee.gateway import GatewayInterface, execute_operation
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HA_HEALTH",
                         message="check_system_health called")

        if not _HEALTH_AVAILABLE:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HA_HEALTH",
                             message="Health core unavailable",
                             error=_HEALTH_IMPORT_ERROR)
            return {
                "success": False,
                "error": "Health core not available",
                "error_code": "CORE_UNAVAILABLE",
            }

        with execute_operation(GatewayInterface.DEBUG, "timing", corr_id=correlation_id, operation_name="check_system_health") as _:
            try:
                result = check_system_health_impl(correlation_id=correlation_id, **kwargs)
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="check_system_health completed",
                                 success=result.get("success", False))
                return result
            except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, OSError) as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="check_system_health failed",
                                 error_type=type(e).__name__, error=str(e))
                return {
                    "success": False,
                    "error": str(e),
                    "error_code": "CHECK_SYSTEM_HEALTH_FAILED",
                }
            except Exception as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="check_system_health failed with unexpected error",
                                 error_type=type(e).__name__, error=str(e))
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "error_code": "CHECK_SYSTEM_HEALTH_FAILED",
                }
    except ImportError:
        # Fallback without debug operations
        ...
        if not _HEALTH_AVAILABLE:
            return {
                "success": False,
                "error": "Health core not available",
                "error_code": "CORE_UNAVAILABLE",
            }
        try:
            return check_system_health_impl(correlation_id=correlation_id, **kwargs)
        except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, OSError) as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "CHECK_SYSTEM_HEALTH_FAILED",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "CHECK_SYSTEM_HEALTH_FAILED",
            }


def check_component_health(component: str, correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Check health of a specific Home Assistant component."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("hah")

    try:
        from lee.gateway import GatewayInterface, execute_operation
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HA_HEALTH",
                         message="check_component_health called", component=component)

        if not _HEALTH_AVAILABLE:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HA_HEALTH",
                             message="Health core unavailable",
                             error=_HEALTH_IMPORT_ERROR)
            return {
                "success": False,
                "error": "Health core not available",
                "error_code": "CORE_UNAVAILABLE",
            }

        with execute_operation(GatewayInterface.DEBUG, "timing", corr_id=correlation_id, operation_name="check_component_health", component=component) as _:
            try:
                result = check_component_health_impl(component=component, correlation_id=correlation_id, **kwargs)
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="check_component_health completed",
                                 success=result.get("success", False))
                return result
            except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, OSError) as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="check_component_health failed",
                                 error_type=type(e).__name__, error=str(e))
                return {
                    "success": False,
                    "error": str(e),
                    "error_code": "CHECK_COMPONENT_HEALTH_FAILED",
                }
            except Exception as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="check_component_health failed with unexpected error",
                                 error_type=type(e).__name__, error=str(e))
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "error_code": "CHECK_COMPONENT_HEALTH_FAILED",
                }
    except ImportError:
        # Fallback without debug operations
        ...
        if not _HEALTH_AVAILABLE:
            return {
                "success": False,
                "error": "Health core not available",
                "error_code": "CORE_UNAVAILABLE",
            }
        try:
            return check_component_health_impl(component=component, correlation_id=correlation_id, **kwargs)
        except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, OSError) as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "CHECK_COMPONENT_HEALTH_FAILED",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "CHECK_COMPONENT_HEALTH_FAILED",
            }


def get_performance_report(correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Generate a comprehensive performance report for Home Assistant."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("hah")

    try:
        from lee.gateway import GatewayInterface, execute_operation
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HA_HEALTH",
                         message="get_performance_report called")

        if not _HEALTH_AVAILABLE:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HA_HEALTH",
                             message="Health core unavailable",
                             error=_HEALTH_IMPORT_ERROR)
            return {
                "success": False,
                "error": "Health core not available",
                "error_code": "CORE_UNAVAILABLE",
            }

        with execute_operation(GatewayInterface.DEBUG, "timing", corr_id=correlation_id, operation_name="get_performance_report") as _:
            try:
                result = get_performance_report_impl(correlation_id=correlation_id, **kwargs)
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="get_performance_report completed",
                                 success=result.get("success", False))
                return result
            except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, OSError) as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="get_performance_report failed",
                                 error_type=type(e).__name__, error=str(e))
                return {
                    "success": False,
                    "error": str(e),
                    "error_code": "GET_PERFORMANCE_REPORT_FAILED",
                }
            except Exception as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="get_performance_report failed with unexpected error",
                                 error_type=type(e).__name__, error=str(e))
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "error_code": "GET_PERFORMANCE_REPORT_FAILED",
                }
    except ImportError:
        # Fallback without debug operations
        ...
        if not _HEALTH_AVAILABLE:
            return {
                "success": False,
                "error": "Health core not available",
                "error_code": "CORE_UNAVAILABLE",
            }
        try:
            return get_performance_report_impl(correlation_id=correlation_id, **kwargs)
        except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, OSError) as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "GET_PERFORMANCE_REPORT_FAILED",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "GET_PERFORMANCE_REPORT_FAILED",
            }


def get_diagnostic_info(category: str = None, correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Get diagnostic information for troubleshooting."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("hah")

    try:
        from lee.gateway import GatewayInterface, execute_operation
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HA_HEALTH",
                         message="get_diagnostic_info called", category=category)

        if not _HEALTH_AVAILABLE:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HA_HEALTH",
                             message="Health core unavailable",
                             error=_HEALTH_IMPORT_ERROR)
            return {
                "success": False,
                "error": "Health core not available",
                "error_code": "CORE_UNAVAILABLE",
            }

        with execute_operation(GatewayInterface.DEBUG, "timing", corr_id=correlation_id, operation_name="get_diagnostic_info", category=category) as _:
            try:
                result = get_diagnostic_info_impl(category=category, correlation_id=correlation_id, **kwargs)
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="get_diagnostic_info completed",
                                 success=result.get("success", False))
                return result
            except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, OSError) as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="get_diagnostic_info failed",
                                 error_type=type(e).__name__, error=str(e))
                return {
                    "success": False,
                    "error": str(e),
                    "error_code": "GET_DIAGNOSTIC_INFO_FAILED",
                }
            except Exception as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="get_diagnostic_info failed with unexpected error",
                                 error_type=type(e).__name__, error=str(e))
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "error_code": "GET_DIAGNOSTIC_INFO_FAILED",
                }
    except ImportError:
        # Fallback without debug operations
        ...
        if not _HEALTH_AVAILABLE:
            return {
                "success": False,
                "error": "Health core not available",
                "error_code": "CORE_UNAVAILABLE",
            }
        try:
            return get_diagnostic_info_impl(category=category, correlation_id=correlation_id, **kwargs)
        except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, OSError) as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "GET_DIAGNOSTIC_INFO_FAILED",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "GET_DIAGNOSTIC_INFO_FAILED",
            }


def test_connectivity(service: str = None, correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Test connectivity to various Home Assistant services and endpoints."""
    if correlation_id is None:
        correlation_id = generate_correlation_id("hah")

    try:
        from lee.gateway import GatewayInterface, execute_operation
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HA_HEALTH",
                         message="test_connectivity called", service=service)

        if not _HEALTH_AVAILABLE:
            execute_operation(GatewayInterface.DEBUG, "log",
                             corr_id=correlation_id, scope="HA_HEALTH",
                             message="Health core unavailable",
                             error=_HEALTH_IMPORT_ERROR)
            return {
                "success": False,
                "error": "Health core not available",
                "error_code": "CORE_UNAVAILABLE",
            }

        with execute_operation(GatewayInterface.DEBUG, "timing", corr_id=correlation_id, operation_name="test_connectivity", service=service) as _:
            try:
                result = test_connectivity_impl(service=service, correlation_id=correlation_id, **kwargs)
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="test_connectivity completed",
                                 success=result.get("success", False))
                return result
            except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, OSError, ConnectionError, TimeoutError) as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="test_connectivity failed",
                                 error_type=type(e).__name__, error=str(e))
                return {
                    "success": False,
                    "error": str(e),
                    "error_code": "TEST_CONNECTIVITY_FAILED",
                }
            except Exception as e:
                execute_operation(GatewayInterface.DEBUG, "log",
                                 corr_id=correlation_id, scope="HA_HEALTH",
                                 message="test_connectivity failed with unexpected error",
                                 error_type=type(e).__name__, error=str(e))
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "error_code": "TEST_CONNECTIVITY_FAILED",
                }
    except ImportError:
        # Fallback without debug operations
        ...
        if not _HEALTH_AVAILABLE:
            return {
                "success": False,
                "error": "Health core not available",
                "error_code": "CORE_UNAVAILABLE",
            }
        try:
            return test_connectivity_impl(service=service, correlation_id=correlation_id, **kwargs)
        except (ValueError, KeyError, AttributeError, TypeError, RuntimeError, OSError, ConnectionError, TimeoutError) as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "TEST_CONNECTIVITY_FAILED",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "TEST_CONNECTIVITY_FAILED",
            }
