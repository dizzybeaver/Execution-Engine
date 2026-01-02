"""
Test Suite for Test Domain

Verifies Test domain operations including:
- Pytest interface operations
- Scanner test interface operations
- Report interface operations
"""

import sys
from pathlib import Path

# Add EE to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.test_gateway import TestGateway


class MockLogger:
    """Mock logger for testing."""
    def __init__(self, name):
        self.name = name

    def debug(self, msg, **kwargs):
        print(f"[DEBUG] {self.name}: {msg}")

    def info(self, msg, **kwargs):
        print(f"[INFO] {self.name}: {msg}")

    def warning(self, msg, **kwargs):
        print(f"[WARN] {self.name}: {msg}")

    def error(self, msg, **kwargs):
        print(f"[ERROR] {self.name}: {msg}")


class MockMetrics:
    """Mock metrics for testing."""
    def __init__(self, name):
        self.name = name
        self.metrics = {}

    def increment(self, metric, value=1):
        self.metrics[metric] = self.metrics.get(metric, 0) + value
        print(f"[METRICS] {self.name}.{metric}: +{value}")

    def timing(self, metric, value):
        print(f"[METRICS] {self.name}.{metric}: {value}s")


def mock_call_operation(domain, interface, operation, **kwargs):
    """Mock cross-domain operation caller."""
    print(f"[CROSS-DOMAIN] {domain}.{interface}.{operation}")
    return {"status": "mocked"}


def test_pytest_interface():
    """Test pytest interface operations."""
    print("\n" + "="*60)
    print("Testing Pytest Interface")
    print("="*60)

    gateway = TestGateway(
        get_logger=lambda name: MockLogger(name),
        get_metrics=lambda name: MockMetrics(name),
        call_operation=mock_call_operation
    )

    # Test run_all
    print("\n1. Testing run_all...")
    result = gateway.execute_domain_operation(
        "pytest", "run_all",
        path="test/",
        verbose=True
    )
    print(f"Result: {result['status']}, Tests: {result.get('tests_run', 0)}")

    # Test run_suite
    print("\n2. Testing run_suite...")
    result = gateway.execute_domain_operation(
        "pytest", "run_suite",
        suite="test_pytest",
        path="test/"
    )
    print(f"Result: {result['status']}, Suite: {result.get('suite')}")

    # Test run_file
    print("\n3. Testing run_file...")
    result = gateway.execute_domain_operation(
        "pytest", "run_file",
        file="test/test_test_domain.py"
    )
    print(f"Result: {result['status']}, File: {result.get('file')}")

    # Test get_results
    print("\n4. Testing get_results...")
    result = gateway.execute_domain_operation(
        "pytest", "get_results",
        run_id="test_run_123"
    )
    print(f"Result: {result.get('status')}")


def test_scanner_interface():
    """Test scanner test interface operations."""
    print("\n" + "="*60)
    print("Testing Scanner Test Interface")
    print("="*60)

    gateway = TestGateway(
        get_logger=lambda name: MockLogger(name),
        get_metrics=lambda name: MockMetrics(name),
        call_operation=mock_call_operation
    )

    # Test scan_all
    print("\n1. Testing scan_all...")
    result = gateway.execute_domain_operation(
        "scanner", "scan_all",
        path="test/",
        pattern="*.py"
    )
    print(f"Result: {result['status']}, Files: {result.get('files_scanned', 0)}")

    # Test scan_gateway
    print("\n2. Testing scan_gateway...")
    result = gateway.execute_domain_operation(
        "scanner", "scan_gateway",
        gateway_path="universal_gateway/"
    )
    print(f"Result: {result['status']}, Files: {result.get('files_scanned', 0)}")

    # Test compile_all
    print("\n3. Testing compile_all...")
    result = gateway.execute_domain_operation(
        "scanner", "compile_all",
        path="test/"
    )
    print(f"Result: {result['status']}, Compiled: {result.get('compiled', 0)}")

    # Test generate_report
    print("\n4. Testing generate_report...")
    result = gateway.execute_domain_operation(
        "scanner", "generate_report",
        report_type="full",
        output_path="reports/scanner/"
    )
    print(f"Result: {result.get('status')}")


def test_report_interface():
    """Test report interface operations."""
    print("\n" + "="*60)
    print("Testing Report Interface")
    print("="*60)

    gateway = TestGateway(
        get_logger=lambda name: MockLogger(name),
        get_metrics=lambda name: MockMetrics(name),
        call_operation=mock_call_operation
    )

    # Test generate
    print("\n1. Testing generate...")
    test_results = {
        "tests_run": 10,
        "failures": 2,
        "errors": 0,
        "skipped": 1,
    }
    result = gateway.execute_domain_operation(
        "report", "generate",
        test_results=test_results,
        title="Test Report"
    )
    print(f"Result: {result['title']}, Total: {result['summary']['total']}")

    # Test export_html
    print("\n2. Testing export_html...")
    result = gateway.execute_domain_operation(
        "report", "export_html",
        report=result,
        output_path="reports/test_report.html"
    )
    print(f"Result: {result['status']}, Path: {result.get('path')}")

    # Test export_json
    print("\n3. Testing export_json...")
    result = gateway.execute_domain_operation(
        "report", "export_json",
        report=result,
        output_path="reports/test_report.json"
    )
    print(f"Result: {result['status']}, Path: {result.get('path')}")


def test_list_all():
    """Test list_all operation."""
    print("\n" + "="*60)
    print("Testing list_all Operation")
    print("="*60)

    gateway = TestGateway(
        get_logger=lambda name: MockLogger(name),
        get_metrics=lambda name: MockMetrics(name),
        call_operation=mock_call_operation
    )

    info = gateway.list_all()
    print(f"\nDomain: {info['domain']}")
    print(f"\nInterfaces:")
    for interface_name, interface_info in info['interfaces'].items():
        print(f"\n  {interface_name}:")
        print(f"    Description: {interface_info['description']}")
        print(f"    Operations:")
        for op in interface_info['operations']:
            print(f"      - {op['operation']}: {op['description']}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST DOMAIN TEST SUITE")
    print("="*60)

    try:
        test_pytest_interface()
        test_scanner_interface()
        test_report_interface()
        test_list_all()

        print("\n" + "="*60)
        print("ALL TESTS PASSED")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
