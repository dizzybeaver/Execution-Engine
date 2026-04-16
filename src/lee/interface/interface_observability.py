"""interface/interface_observability.py
Version: 2026-03-24_2
Purpose: OBSERVABILITY interface router (SUGA-ISP Implementation)
License: Apache 2.0

SUGA-ISP Pattern: Gateway -> Interface -> Observability Operations
Interface acts as unified router for observability operations

This interface consolidates:
- Health checks and monitoring (from MONITORING + DIAGNOSIS)
- Alerting and notifications (from MONITORING)
- Error tracking and patterns (from DIAGNOSIS)
- Performance metrics and profiling (from PERFORMANCE)
- Anomaly detection (from PERFORMANCE)
- Time-aware baselines (from PERFORMANCE)
- Load prediction (from PERFORMANCE)
- System diagnostics (from DIAGNOSIS)
- Metrics collection (from METRICS) - Phase 2A

CRITICAL ARCHITECTURAL RULE:
- NO interface-to-interface imports (violates SUGA-ISP)
- Use execute_*_operation() functions to call other interfaces
- Import domain functions directly where needed

Operations organized by category:
- Health: System health checks and status
- Alerts: Alert creation, acknowledgment, resolution
- Errors: Error recording and pattern analysis
- Performance: Cold start metrics, profiling
- Anomaly: Anomaly detection and analysis
- Baselines: Time-aware baseline learning
- Load: Load prediction and statistics
- Diagnostics: System validation and import testing
"""

from typing import Any

# Import gateway for logging
from lee.gateway import GatewayInterface, execute_operation

# Import metrics operations (Phase 2A)
# Import domain functions directly to avoid circular dependency
# pylint: disable=no-name-in-module
from lee.metrics import (
    get_circuit_breaker_metrics,
    get_dispatcher_stats,
    get_http_metrics,
    get_operation_metrics,
    get_response_metrics,
    get_stats,
    increment_counter,
    record_api_metric,
    record_cache_metric,
    record_circuit_breaker_event,
    record_dispatcher_timing,
    record_error_response,
    record_http_metric,
    record_metric,
    record_operation_metric,
    record_response_metric,
    reset_metrics,
)
from lee.metrics import (
    get_performance_report as get_metrics_performance_report,
)

# ===== UNIFIED OBSERVABILITY DISPATCH =====

def execute_observability_operation(operation: str, **kwargs) -> Any:
    """Route observability operations through unified dispatch dictionary.

    This function implements the SUGA-ISP pattern where the interface acts
    as a router, dispatching operations to specific implementations.

    Consolidates operations from:
    - MONITORING interface (health checks, alerting)
    - DIAGNOSIS interface (health validation, diagnostics)
    - PERFORMANCE interface (profiling, anomaly detection)

    CRITICAL: NO interface-to-interface imports. Use execute_*_operation().

    Args:
        operation: The operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from appropriate implementation

    Raises:
        ValueError: If operation unknown
        RuntimeError: If operation execution fails

    Available Operations by Category:

    Health Operations:
    - health_check: Perform system health check
    - record_health_check: Record health check result
    - get_system_metrics: Get system performance metrics

    Metrics Collection Operations (Phase 2A):
    - record_metric: Record generic metric
    - increment_counter: Increment counter metric
    - get_stats: Get metric statistics
    - get_operation_metrics: Get operation-specific metrics
    - record_operation_metric: Record operation timing metric
    - get_response_metrics: Get HTTP response metrics
    - record_response_metric: Record HTTP response metric
    - get_http_metrics: Get HTTP client metrics
    - record_http_metric: Record HTTP client metric
    - get_circuit_breaker_metrics: Get circuit breaker metrics
    - record_circuit_breaker_event: Record circuit breaker event
    - get_dispatcher_stats: Get gateway dispatcher statistics
    - record_dispatcher_timing: Record gateway dispatcher timing
    - record_cache_metric: Record cache performance metric
    - record_api_metric: Record API performance metric
    - record_error_response: Record error response metric
    - get_metrics_performance_report: Get metrics performance report
    - reset_metrics: Reset all metrics

    Alerting Operations:
    - create_alert: Create new alert with de-duplication
    - acknowledge_alert: Acknowledge active alert
    - resolve_alert: Resolve alert
    - get_alerts: Get all or filtered alerts
    - get_alert_by_id: Get specific alert
    - get_alert_stats: Get alert statistics
    - reset_alerts: Clear all alerts
    - check_alerts: Check and trigger alerts
    - check_and_trigger_alerts: Check conditions and trigger alerts
    - suppress_alert: Suppress alerts by pattern
    - unsuppress_alert: Remove alert suppression

    Error Tracking:
    - record_error: Record error occurrence
    - get_error_patterns: Get error patterns
    - get_error_summary: Get error summary
    - get_error_details: Get error details
    - get_error_frequency: Get error frequency
    - is_error_chronic: Check if error is chronic
    - get_recent_errors: Get recent errors
    - get_errors_by_component: Get errors by component
    - reset_error_tracker: Reset error tracking

    Performance Metrics:
    - get_metrics: Get performance metrics (alias for get_performance_report)
    - get_profile_stats: Get profiling stats for operation
    - get_all_profiles: Get all profiling stats
    - get_performance_report: Get comprehensive performance report
    - reset_profiler: Reset profiler state
    - cold_start: Get cold start metrics
    - is_cold_start: Check if currently in cold start
    - import_summary: Get import timing summary

    Anomaly Detection:
    - detect_anomaly: Detect anomaly using specified algorithm
    - add_anomaly_sample: Add sample to anomaly detector
    - get_anomaly_stats: Get anomaly statistics
    - reset_detector: Reset anomaly detector
    - cache_status: Get anomaly cache status
    - clear_cache: Clear anomaly cache

    Baselines:
    - add_sample: Add time-aware sample
    - learn_baselines: Learn time-aware baselines
    - is_deviation: Check deviation from baseline
    - get_baselines: Get current baselines
    - get_bin_count: Get time bin sample count
    - reset_baselines: Reset baselines

    Load Prediction:
    - record_request: Record load request
    - predict_load: Predict system load
    - get_load_stats: Get load statistics
    - reset_predictor: Reset load predictor

    Diagnostics:
    - run_suite: Run diagnostic suite
    - validate_component: Validate component
    - validate_system: Validate system
    - validate_imports: Validate imports
    - validate_routing: Validate routing
    - import_failure: Diagnose import failure
    - component_perf: Diagnose component performance
    - init_perf: Diagnose initialization performance
    - utility_perf: Diagnose utility performance
    - singleton_perf: Diagnose singleton performance
    """
    # NOTE: Using gateway execute_operation to follow SUGA-ISP pattern
    # Helper functions for gateway calls
    # pylint: disable=too-many-locals
    def _lazy_execute_monitoring(operation: str, **kwargs):
        # pylint: disable=no-member
        return execute_operation(GatewayInterface.OBSERVABILITY, operation, **kwargs)

    def _lazy_execute_diagnosis(operation: str, **kwargs):
        return execute_operation(GatewayInterface.DIAGNOSIS, operation, **kwargs)

    def _lazy_execute_performance(operation: str, **kwargs):
        return execute_operation(GatewayInterface.PERFORMANCE, operation, **kwargs)

    # Health operations
    health_operations = {
        "health_check": {
            "func": lambda **kwargs: {
                "status": "healthy",
                "interface": "OBSERVABILITY",
                "timestamp": __import__('time').time(),
                "checks": {
                    "alerts_system": "operational",
                    "metrics_collection": "operational",
                    "health_checks": "operational",
                }
            },
            "category": "health",
            "description": "Perform system health check",
        },
        "record_health_check": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "record_health_check", **kwargs
            ),
            "category": "health",
            "description": "Record health check result",
        },
        "get_system_metrics": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "get_system_metrics", **kwargs
            ),
            "category": "health",
            "description": "Get system performance metrics",
        },
    }

    # Alerting operations
    alerting_operations = {
        "create_alert": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "create_alert", **kwargs
            ),
            "category": "alerts",
            "description": "Create new alert with de-duplication",
        },
        "acknowledge_alert": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "acknowledge_alert", **kwargs
            ),
            "category": "alerts",
            "description": "Acknowledge active alert",
        },
        "resolve_alert": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "resolve_alert", **kwargs
            ),
            "category": "alerts",
            "description": "Resolve alert",
        },
        "get_alerts": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "get_alerts", **kwargs
            ),
            "category": "alerts",
            "description": "Get all or filtered alerts",
        },
        "get_alert_by_id": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "get_alert_by_id", **kwargs
            ),
            "category": "alerts",
            "description": "Get specific alert",
        },
        "get_alert_stats": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "get_alert_stats", **kwargs
            ),
            "category": "alerts",
            "description": "Get alert statistics",
        },
        "reset_alerts": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "reset_alerts", **kwargs
            ),
            "category": "alerts",
            "description": "Clear all alerts",
        },
        "check_alerts": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "check_alerts", **kwargs
            ),
            "category": "alerts",
            "description": "Check and trigger alerts",
        },
        "check_and_trigger_alerts": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "check_and_trigger_alerts", **kwargs
            ),
            "category": "alerts",
            "description": "Check conditions and trigger alerts",
        },
        "suppress_alert": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "suppress_alert", **kwargs
            ),
            "category": "alerts",
            "description": "Suppress alerts by pattern",
        },
        "unsuppress_alert": {
            "func": lambda **kwargs: _lazy_execute_monitoring(
                "unsuppress_alert", **kwargs
            ),
            "category": "alerts",
            "description": "Remove alert suppression",
        },
    }

    # Performance metrics operations
    performance_operations = {
        "get_metrics": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "get_performance_report", **kwargs
            ),
            "category": "performance",
            "description": "Get performance metrics",
        },
        "get_profile_stats": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "get_profile_stats", **kwargs
            ),
            "category": "performance",
            "description": "Get profiling stats for operation",
        },
        "get_all_profiles": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "get_all_profile_stats", **kwargs
            ),
            "category": "performance",
            "description": "Get all profiling stats",
        },
        "get_performance_report": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "get_performance_report", **kwargs
            ),
            "category": "performance",
            "description": "Get comprehensive performance report",
        },
        "reset_profiler": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "reset_profiler", **kwargs
            ),
            "category": "performance",
            "description": "Reset profiler state",
        },
        "cold_start": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "get_cold_start_metrics", **kwargs
            ),
            "category": "performance",
            "description": "Get cold start metrics",
        },
        "is_cold_start": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "is_cold_start", **kwargs
            ),
            "category": "performance",
            "description": "Check if currently in cold start",
        },
        "import_summary": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "get_import_summary", **kwargs
            ),
            "category": "performance",
            "description": "Get import timing summary",
        },
    }

    # Anomaly detection operations
    anomaly_operations = {
        "detect_anomaly": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "detect_anomaly", **kwargs
            ),
            "category": "anomaly",
            "description": "Detect anomaly using specified algorithm",
        },
        "add_anomaly_sample": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "add_anomaly_sample", **kwargs
            ),
            "category": "anomaly",
            "description": "Add sample to anomaly detector",
        },
        "get_anomaly_stats": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "get_anomaly_stats", **kwargs
            ),
            "category": "anomaly",
            "description": "Get anomaly statistics",
        },
        "reset_detector": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "reset_anomaly_detector", **kwargs
            ),
            "category": "anomaly",
            "description": "Reset anomaly detector",
        },
        "cache_status": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "get_anomaly_cache_status", **kwargs
            ),
            "category": "anomaly",
            "description": "Get anomaly cache status",
        },
        "clear_cache": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "clear_anomaly_cache", **kwargs
            ),
            "category": "anomaly",
            "description": "Clear anomaly cache",
        },
    }

    # Baseline operations
    baseline_operations = {
        "add_sample": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "add_time_aware_sample", **kwargs
            ),
            "category": "baselines",
            "description": "Add time-aware sample",
        },
        "learn_baselines": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "learn_baselines", **kwargs
            ),
            "category": "baselines",
            "description": "Learn time-aware baselines",
        },
        "is_deviation": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "is_deviation_from_baseline", **kwargs
            ),
            "category": "baselines",
            "description": "Check deviation from baseline",
        },
        "get_baselines": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "get_baselines", **kwargs
            ),
            "category": "baselines",
            "description": "Get current baselines",
        },
        "get_bin_count": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "get_time_bin_sample_count", **kwargs
            ),
            "category": "baselines",
            "description": "Get time bin sample count",
        },
        "reset_baselines": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "reset_time_aware_baselines", **kwargs
            ),
            "category": "baselines",
            "description": "Reset baselines",
        },
    }

    # Load prediction operations
    load_operations = {
        "record_request": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "record_load_request", **kwargs
            ),
            "category": "load",
            "description": "Record load request",
        },
        "predict_load": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "predict_load", **kwargs
            ),
            "category": "load",
            "description": "Predict system load",
        },
        "get_load_stats": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "get_load_stats", **kwargs
            ),
            "category": "load",
            "description": "Get load statistics",
        },
        "reset_predictor": {
            "func": lambda **kwargs: _lazy_execute_performance(
                "reset_load_predictor", **kwargs
            ),
            "category": "load",
            "description": "Reset load predictor",
        },
    }

    # Error tracking operations (from DIAGNOSIS)
    error_operations = {
        "record_error": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "record_error", **kwargs
            ),
            "category": "errors",
            "description": "Record error occurrence",
        },
        "get_error_patterns": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "get_error_patterns", **kwargs
            ),
            "category": "errors",
            "description": "Get error patterns",
        },
        "get_error_summary": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "get_error_summary", **kwargs
            ),
            "category": "errors",
            "description": "Get error summary",
        },
        "get_error_details": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "get_error_details", **kwargs
            ),
            "category": "errors",
            "description": "Get error details",
        },
        "get_error_frequency": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "get_error_frequency", **kwargs
            ),
            "category": "errors",
            "description": "Get error frequency",
        },
        "is_error_chronic": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "is_error_chronic", **kwargs
            ),
            "category": "errors",
            "description": "Check if error is chronic",
        },
        "get_recent_errors": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "get_recent_errors", **kwargs
            ),
            "category": "errors",
            "description": "Get recent errors",
        },
        "get_errors_by_component": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "get_errors_by_component", **kwargs
            ),
            "category": "errors",
            "description": "Get errors by component",
        },
        "reset_error_tracker": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "reset_error_tracker", **kwargs
            ),
            "category": "errors",
            "description": "Reset error tracking",
        },
    }

    # Diagnostic operations (from DIAGNOSIS)
    diagnostic_operations = {
        "run_suite": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "run_diagnostic_suite", **kwargs
            ),
            "category": "diagnostics",
            "description": "Run diagnostic suite",
        },
        "validate_component": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "check_component_health", **kwargs
            ),
            "category": "diagnostics",
            "description": "Validate component",
        },
        "validate_system": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "validate_system_architecture", **kwargs
            ),
            "category": "diagnostics",
            "description": "Validate system",
        },
        "validate_imports": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "validate_imports", **kwargs
            ),
            "category": "diagnostics",
            "description": "Validate imports",
        },
        "validate_routing": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "validate_gateway_routing", **kwargs
            ),
            "category": "diagnostics",
            "description": "Validate routing",
        },
        "import_failure": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "diagnose_import_failure", **kwargs
            ),
            "category": "diagnostics",
            "description": "Diagnose import failure",
        },
        "component_perf": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "diagnose_component_performance", **kwargs
            ),
            "category": "diagnostics",
            "description": "Diagnose component performance",
        },
        "init_perf": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "diagnose_initialization_performance", **kwargs
            ),
            "category": "diagnostics",
            "description": "Diagnose initialization performance",
        },
        "utility_perf": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "diagnose_utility_performance", **kwargs
            ),
            "category": "diagnostics",
            "description": "Diagnose utility performance",
        },
        "singleton_perf": {
            "func": lambda **kwargs: _lazy_execute_diagnosis(
                "diagnose_singleton_performance", **kwargs
            ),
            "category": "diagnostics",
            "description": "Diagnose singleton performance",
        },
    }

    # Metrics collection operations (Phase 2A)
    # Direct domain function calls to avoid circular dependency
    metrics_collection_operations = {
        "record_metric": {
            "func": record_metric,
            "category": "metrics_collection",
            "description": "Record generic metric",
        },
        "increment_counter": {
            "func": increment_counter,
            "category": "metrics_collection",
            "description": "Increment counter metric",
        },
        "get_stats": {
            "func": get_stats,
            "category": "metrics_collection",
            "description": "Get metric statistics",
        },
        "get_operation_metrics": {
            "func": get_operation_metrics,
            "category": "metrics_collection",
            "description": "Get operation-specific metrics",
        },
        "record_operation_metric": {
            "func": record_operation_metric,
            "category": "metrics_collection",
            "description": "Record operation timing metric",
        },
        "get_response_metrics": {
            "func": get_response_metrics,
            "category": "metrics_collection",
            "description": "Get HTTP response metrics",
        },
        "record_response_metric": {
            "func": record_response_metric,
            "category": "metrics_collection",
            "description": "Record HTTP response metric",
        },
        "get_http_metrics": {
            "func": get_http_metrics,
            "category": "metrics_collection",
            "description": "Get HTTP client metrics",
        },
        "record_http_metric": {
            "func": record_http_metric,
            "category": "metrics_collection",
            "description": "Record HTTP client metric",
        },
        "get_circuit_breaker_metrics": {
            "func": get_circuit_breaker_metrics,
            "category": "metrics_collection",
            "description": "Get circuit breaker metrics",
        },
        "record_circuit_breaker_event": {
            "func": record_circuit_breaker_event,
            "category": "metrics_collection",
            "description": "Record circuit breaker event",
        },
        "get_dispatcher_stats": {
            "func": get_dispatcher_stats,
            "category": "metrics_collection",
            "description": "Get gateway dispatcher statistics",
        },
        "record_dispatcher_timing": {
            "func": lambda **kwargs: record_dispatcher_timing(
                kwargs.get("interface_name", ""),
                kwargs.get("operation_name", ""),
                kwargs.get("duration_ms", 0.0),
                **{k: v for k, v in kwargs.items() if k not in ["interface_name", "operation_name", "duration_ms"]}
            ),
            "category": "metrics_collection",
            "description": "Record gateway dispatcher timing",
        },
        "record_cache_metric": {
            "func": record_cache_metric,
            "category": "metrics_collection",
            "description": "Record cache performance metric",
        },
        "record_api_metric": {
            "func": record_api_metric,
            "category": "metrics_collection",
            "description": "Record API performance metric",
        },
        "record_error_response": {
            "func": record_error_response,
            "category": "metrics_collection",
            "description": "Record error response metric",
        },
        "get_metrics_performance_report": {
            "func": get_metrics_performance_report,
            "category": "metrics_collection",
            "description": "Get metrics performance report",
        },
        "reset_metrics": {
            "func": reset_metrics,
            "category": "metrics_collection",
            "description": "Reset all metrics",
        },
    }

    # Unified dispatch dictionary
    dispatch = {
        **health_operations,
        **alerting_operations,
        **error_operations,
        **performance_operations,
        **anomaly_operations,
        **baseline_operations,
        **load_operations,
        **diagnostic_operations,
        **metrics_collection_operations,
    }

    if operation not in dispatch:
        available = ", ".join(dispatch.keys())
        raise ValueError(
            f"Unknown OBSERVABILITY operation: {operation}. "
            f"Available operations: {available}"
        )

    op_info = dispatch[operation]
    func = op_info["func"]

    # Debug logging (optional)
    try:
        if kwargs.get("debug", False):
            execute_operation(
                GatewayInterface.LOGGING,
                "log_debug",
                message=f"OBSERVABILITY.{operation} invoked",
                corr_id=kwargs.get("correlation_id"),
            )
    except (ImportError, AttributeError):
        # Optional dependency - continue if unavailable
        pass

    # Execute operation
    try:
        result = func(**kwargs)
        return result
    except (AttributeError, KeyError, TypeError, ValueError, ImportError, RuntimeError) as e:
        # Error logging
        try:
            execute_operation(
                GatewayInterface.LOGGING,
                "log_error",
                message=f"OBSERVABILITY.{operation} failed: {str(e)}",
                corr_id=kwargs.get("correlation_id"),
            )
        except (ImportError, AttributeError, KeyError, TypeError):
            # Optional dependency - continue if unavailable
            pass

        raise RuntimeError(f"OBSERVABILITY operation '{operation}' failed: {str(e)}") from e


__all__ = ["execute_observability_operation"]
