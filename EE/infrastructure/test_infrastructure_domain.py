"""
Test Suite for Infrastructure Domain

Verifies Infrastructure domain operations including:
- Plugins interface operations
"""

import sys
from pathlib import Path

# Add EE to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.infrastructure_gateway import InfrastructureGateway


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


def test_plugins_interface():
    """Test plugins interface operations."""
    print("\n" + "="*60)
    print("Testing Plugins Interface")
    print("="*60)

    gateway = InfrastructureGateway(
        get_logger=lambda name: MockLogger(name),
        get_metrics=lambda name: MockMetrics(name),
        call_operation=mock_call_operation
    )

    # Test load
    print("\n1. Testing load...")
    result = gateway.execute_domain_operation(
        "plugins", "load",
        name="test_plugin",
        path="test/test_test_domain.py"
    )
    print(f"Result: {result['status']}, State: {result.get('state')}")

    # Test list
    print("\n2. Testing list...")
    result = gateway.execute_domain_operation("plugins", "list")
    print(f"Result: {len(result)} plugins loaded")
    for plugin in result:
        print(f"  - {plugin['name']}: {plugin['state']} (enabled: {plugin['enabled']})")

    # Test get_info
    print("\n3. Testing get_info...")
    result = gateway.execute_domain_operation(
        "plugins", "get_info",
        name="test_plugin"
    )
    print(f"Result: {result['name']}, State: {result['state']}, Enabled: {result['enabled']}")

    # Test disable
    print("\n4. Testing disable...")
    result = gateway.execute_domain_operation(
        "plugins", "disable",
        name="test_plugin"
    )
    print(f"Result: {result['status']}, Enabled: {result['enabled']}")

    # Test enable
    print("\n5. Testing enable...")
    result = gateway.execute_domain_operation(
        "plugins", "enable",
        name="test_plugin"
    )
    print(f"Result: {result['status']}, Enabled: {result['enabled']}")

    # Test reload
    print("\n6. Testing reload...")
    result = gateway.execute_domain_operation(
        "plugins", "reload",
        name="test_plugin"
    )
    print(f"Result: {result['status']}, State: {result.get('state')}")

    # Test unload
    print("\n7. Testing unload...")
    result = gateway.execute_domain_operation(
        "plugins", "unload",
        name="test_plugin"
    )
    print(f"Result: {result['status']}, State: {result.get('state')}")

    # Test list again (should be empty)
    print("\n8. Testing list after unload...")
    result = gateway.execute_domain_operation("plugins", "list")
    print(f"Result: {len(result)} plugins loaded")


def test_list_all():
    """Test list_all operation."""
    print("\n" + "="*60)
    print("Testing list_all Operation")
    print("="*60)

    gateway = InfrastructureGateway(
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
    print("INFRASTRUCTURE DOMAIN TEST SUITE")
    print("="*60)

    try:
        test_plugins_interface()
        test_list_all()

        print("\n" + "="*60)
        print("ALL TESTS PASSED")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
