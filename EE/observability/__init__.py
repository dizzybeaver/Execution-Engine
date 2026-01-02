"""
Observability Domain - UG-ISP Compliant (EE 2.1)

Provides observability capabilities for EE applications:
- logging: Structured logging and CloudWatch integration
- metrics: Performance metrics and CloudWatch metrics
- debug: Debug logging, correlation tracking, and diagnostics
- diagnosis: Health checks and system diagnostics

UG-ISP Compliance (EE 2.1):
- Extends DomainGateway base class with proper constructor
- Uses injected factory functions (get_logger, get_metrics, call_operation)
- Cross-domain calls via call_operation callback
- No direct imports outside observability domain
- Proper DI patterns throughout
"""

from __future__ import annotations
from typing import Any, Dict, Callable

# Import DomainGateway from universal_gateway (same EE, not cross-domain)
# This is the ONLY allowed cross-import within EE
# FIXED: Removed sys.path manipulation fallback - use absolute import only
from EE.universal_gateway.domain_gateway import DomainGateway

# Import interface routers (within observability domain only)
from EE.observability.logging.logging_interface import execute_logging_operation
from EE.observability.metrics.metrics_interface import execute_metrics_operation
from EE.observability.debug.debug_interface import execute_debug_operation
from EE.observability.diagnosis.diagnosis_interface import execute_diagnosis_operation


class ObservabilityGateway(DomainGateway):
    """Observability Domain Gateway - EE 2.1 Compliant.

    Provides observability capabilities through the following interfaces:
    - logging: Structured logging (log, debug, info, warn, error)
    - metrics: Performance metrics (increment, gauge, timing, flush)
    - debug: Debug tools (enable_debug, disable_debug, get_correlation_id)
    - diagnosis: Health checks (health_check, diagnose, get_stats)

    EE 2.1 Compliance:
    - Proper constructor signature: DomainGateway(domain_name, get_logger, get_metrics, call_operation)
    - Factory functions injected (not instances)
    - Cross-domain calls via call_operation callback
    - No direct imports outside observability domain
    - Interface isolation maintained

    Example:
        from EE.universal_gateway import UniversalGatewayFactory

        # Create UG with observability domain
        ug = UniversalGatewayFactory.create()

        # Log message
        ug.execute_operation(
            route="observability.logging.info",
            payload={"message": "System started"}
        )

        # Record metric
        ug.execute_operation(
            route="observability.metrics.increment",
            payload={"metric_name": "api.requests", "value": 1}
        )

        # Health check
        health = ug.execute_operation(
            route="observability.diagnosis.health_check",
            payload={"component": "database"}
        )
    """

    def __init__(
        self,
        domain_name: str,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str], Any],
        call_operation: Callable[
            [str, str, str],  # domain, interface, operation
            Any
        ],
    ) -> None:
        """Initialize observability gateway with injected dependencies (EE 2.1).

        Args:
            domain_name: Domain identifier (must be "observability")
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Callback for cross-domain operations
                           Signature: call_operation(domain, interface, operation, **kwargs)
        """
        # EE 2.1 REQUIRED: Call parent constructor with proper signature
        super().__init__(
            domain_name=domain_name,
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation
        )

        # Store factory functions for use in operations
        self._get_logger = get_logger
        self._get_metrics = get_metrics
        self._get_config = get_config
        self._call_operation = call_operation

    def execute_domain_operation(
        self,
        interface: str,
        operation: str,
        **kwargs
    ) -> Any:
        """Execute domain operation using UG-ISP pattern (EE 2.1).

        EE 2.1 Rules:
        - Inject factory functions (not instances)
        - Interface routers receive logger, metrics, call_operation
        - Cross-domain calls use call_operation(domain, interface, operation, **kwargs)

        Args:
            interface: Interface name (logging, metrics, debug, diagnosis)
            operation: Operation name (log, increment, health_check, etc.)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            DomainGatewayError: If interface or operation is invalid
        """
        # EE 2.1: Inject factory functions (not instances)
        kwargs.setdefault("get_logger", self._get_logger)
        kwargs.setdefault("get_metrics", self._get_metrics)
        kwargs.setdefault("call_operation", self._call_operation)

        # Route to appropriate interface
        try:
            if interface == "logging":
                return execute_logging_operation(operation, **kwargs)
            elif interface == "metrics":
                return execute_metrics_operation(operation, **kwargs)
            elif interface == "debug":
                return execute_debug_operation(operation, **kwargs)
            elif interface == "diagnosis":
                return execute_diagnosis_operation(operation, **kwargs)
            else:
                from EE.universal_gateway.domain_gateway import InterfaceNotFoundError
                raise InterfaceNotFoundError(
                    f"Unknown observability interface: {interface}. "
                    f"Valid interfaces: logging, metrics, debug, diagnosis"
                )
        except ValueError as e:
            from EE.universal_gateway.domain_gateway import DomainGatewayError
            raise DomainGatewayError(
                f"Operation failed: {e}"
            ) from e

    def list_all(self) -> Dict[str, Any]:
        """List all observability domain operations.

        Returns:
            Dictionary with all operations organized by interface
        """
        return {
            "domain": self._domain_name,
            "interfaces": {
                "logging": {
                    "description": "Structured logging and CloudWatch integration",
                    "operations": [
                        {"operation": "log", "description": "Log message with level"},
                        {"operation": "debug", "description": "Log debug message"},
                        {"operation": "info", "description": "Log info message"},
                        {"operation": "warning", "description": "Log warning message"},
                        {"operation": "error", "description": "Log error message"},
                        {"operation": "critical", "description": "Log critical message"},
                        {"operation": "exception", "description": "Log exception"},
                        {"operation": "set_level", "description": "Set log level"},
                        {"operation": "get_level", "description": "Get current log level"},
                        {"operation": "add_handler", "description": "Add log handler"},
                        {"operation": "remove_handler", "description": "Remove log handler"},
                        {"operation": "flush", "description": "Flush log buffers"},
                    ]
                },
                "metrics": {
                    "description": "Performance metrics and CloudWatch metrics",
                    "operations": [
                        {"operation": "increment", "description": "Increment counter"},
                        {"operation": "decrement", "description": "Decrement counter"},
                        {"operation": "gauge", "description": "Set gauge value"},
                        {"operation": "timing", "description": "Record timing"},
                        {"operation": "histogram", "description": "Record histogram value"},
                        {"operation": "flush", "description": "Flush metrics"},
                        {"operation": "get_metrics", "description": "Get all metrics"},
                        {"operation": "reset", "description": "Reset metrics"},
                        {"operation": "enable_cloudwatch", "description": "Enable CloudWatch"},
                        {"operation": "disable_cloudwatch", "description": "Disable CloudWatch"},
                    ]
                },
                "debug": {
                    "description": "Debug logging, correlation tracking, and diagnostics",
                    "operations": [
                        {"operation": "enable_debug", "description": "Enable debug mode"},
                        {"operation": "disable_debug", "description": "Disable debug mode"},
                        {"operation": "is_debug_enabled", "description": "Check debug status"},
                        {"operation": "set_correlation_id", "description": "Set correlation ID"},
                        {"operation": "get_correlation_id", "description": "Get correlation ID"},
                        {"operation": "clear_correlation_id", "description": "Clear correlation ID"},
                        {"operation": "start_trace", "description": "Start trace span"},
                        {"operation": "end_trace", "description": "End trace span"},
                        {"operation": "get_trace_context", "description": "Get trace context"},
                    ]
                },
                "diagnosis": {
                    "description": "Health checks and system diagnostics",
                    "operations": [
                        {"operation": "health_check", "description": "Perform health check"},
                        {"operation": "diagnose", "description": "Diagnose component"},
                        {"operation": "get_stats", "description": "Get system statistics"},
                        {"operation": "check_dependency", "description": "Check dependency health"},
                        {"operation": "run_diagnostics", "description": "Run full diagnostics"},
                        {"operation": "get_status", "description": "Get system status"},
                        {"operation": "get_health_report", "description": "Generate health report"},
                    ]
                },
            }
        }


__all__ = [
    "ObservabilityGateway",
]
