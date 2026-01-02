"""
Test Domain Gateway - EE 2.1 Compliant

Routes test operations to appropriate interfaces within the Test domain:
- pytest: Pytest-based testing operations
- scanner: Scanner test operations (scan, compile, report)
- report: Test report generation and export

EE 2.1 Compliance:
- Extends DomainGateway base class with proper __init__
- Uses execute_domain_operation(interface, operation, **kwargs)
- Cross-domain calls via call_operation callback
- Uniform constructor signature with get_config parameter
- NO sys.path manipulation
- NO legacy execute() method
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass

# FIXED: Removed sys.path manipulation - using proper import path
from EE.universal_gateway.domain_gateway import DomainGateway, DomainGatewayError


class TestGateway(DomainGateway):
    """Test Domain Gateway.

    Provides testing EE capabilities through the following interfaces:
    - pytest: Pytest operations (run_all, run_suite, run_file, get_results)
    - scanner: Scanner test operations (scan_all, scan_gateway, compile_all, generate_report)
    - report: Report operations (generate, export_html, export_json)

    All operations follow EE 2.1 patterns:
    - execute_domain_operation(interface, operation, **kwargs)
    - Cross-domain calls via call_operation callback
    - No direct imports outside test domain

    Example:
        gateway = TestGateway(
            domain_name="test",
            get_logger=logger_factory,
            get_metrics=metrics_factory,
            get_config=config_factory,
            call_operation=callback
        )

        # Run all tests
        result = gateway.execute_domain_operation(
            "pytest", "run_all", path="tests/"
        )

        # Generate report
        report = gateway.execute_domain_operation(
            "report", "generate", format="html"
        )
    """

    # FIXED: EE 2.1 Uniform Gateway Constructor Signature - REQUIRED parameters only
    def __init__(
        self,
        domain_name: str,
        get_logger: Callable[[str], Any],
        get_metrics: Callable[[str], Any],
        get_config: Callable[[str], Any],
        call_operation: Callable[..., Any],
    ):
        """Initialize test gateway with injected dependencies (EE 2.1).

        Args:
            domain_name: Domain name (must be "test")
            get_logger: Factory function to create loggers (REQUIRED)
            get_metrics: Factory function to create metrics collectors (REQUIRED)
            get_config: Factory function to get config values (REQUIRED)
            call_operation: Function to call operations in other domains (REQUIRED)
        """
        # Initialize parent DomainGateway with uniform signature
        super().__init__(
            domain_name=domain_name,
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation
        )

        # Register interfaces
        from EE.test.pytest.pytest_interface import create_pytest_interface
        from EE.test.scanner.scanner_test_interface import create_scanner_test_interface
        from EE.test.report.report_interface import create_report_interface

        self.register_interface("pytest", create_pytest_interface)
        self.register_interface("scanner", create_scanner_test_interface)
        self.register_interface("report", create_report_interface)

    # FIXED: Removed legacy execute() method - use execute_domain_operation instead

    def execute_domain_operation(
        self,
        interface: str,
        operation: str,
        **kwargs
    ) -> Any:
        """Execute domain operation using EE 2.1 pattern.

        Args:
            interface: Interface name (pytest, scanner, report)
            operation: Operation name (run_all, scan_all, generate, etc.)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            DomainGatewayError: If interface or operation is invalid
        """
        # Inject dependencies into kwargs
        kwargs.setdefault("get_logger", self._get_logger)
        kwargs.setdefault("get_metrics", self._get_metrics)
        kwargs.setdefault("get_config", self._get_config)
        kwargs.setdefault("call_operation", self._call_operation)

        # Use parent class method to execute
        return super().execute_domain_operation(interface, operation, **kwargs)

    def list_all(self) -> Dict[str, Any]:
        """List all test domain operations.

        Returns:
            Dictionary with all operations organized by interface
        """
        return {
            "domain": self._domain_name,
            "interfaces": {
                "pytest": {
                    "description": "Pytest-based testing operations",
                    "operations": [
                        {"operation": "run_all", "description": "Run all tests"},
                        {"operation": "run_suite", "description": "Run specific test suite"},
                        {"operation": "run_file", "description": "Run tests for specific file"},
                        {"operation": "get_results", "description": "Get test results"},
                    ]
                },
                "scanner": {
                    "description": "Scanner test operations",
                    "operations": [
                        {"operation": "scan_all", "description": "Scan all tests"},
                        {"operation": "scan_gateway", "description": "Scan gateway tests"},
                        {"operation": "compile_all", "description": "Compile all tests"},
                        {"operation": "generate_report", "description": "Generate scanner report"},
                    ]
                },
                "report": {
                    "description": "Test report generation and export",
                    "operations": [
                        {"operation": "generate", "description": "Generate test report"},
                        {"operation": "export_html", "description": "Export report as HTML"},
                        {"operation": "export_json", "description": "Export report as JSON"},
                    ]
                },
            }
        }


__all__ = [
    "TestGateway",
]
