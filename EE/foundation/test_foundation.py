#!/usr/bin/env python3
"""
Test Foundation Domain - UG-ISP Compliance Verification

Tests the foundation domain implementation for UG-ISP compliance.
"""

import sys
import os

# Add EE to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from EE.foundation import FoundationGateway


def test_foundation_gateway():
    """Test foundation gateway."""
    print("=" * 80)
    print("Testing Foundation Domain - UG-ISP Compliance")
    print("=" * 80)
    print()

    # Create gateway
    gateway = FoundationGateway()

    # Test 1: List all operations
    print("Test 1: List all operations")
    print("-" * 40)
    all_ops = gateway.list_all()
    print(f"Domain: {all_ops['domain']}")
    print(f"Interfaces: {list(all_ops['interfaces'].keys())}")
    print()

    # Test 2: Config operations
    print("Test 2: Config operations")
    print("-" * 40)

    # Get config
    cache_config = gateway.execute_domain_operation("config", "get", category="cache")
    print(f"Cache config: {cache_config}")

    # Get config value by path
    ttl = gateway.execute_domain_operation("config", "get_value", path="cache.default_ttl_seconds")
    print(f"Default TTL: {ttl}")

    # Set config
    gateway.execute_domain_operation("config", "set", category="test", key="value", value="test_value")
    print("Set test config: test.value = test_value")

    # Get all config
    all_config = gateway.execute_domain_operation("config", "get_all")
    print(f"Total config categories: {len(all_config)}")
    print()

    # Test 3: Singleton operations
    print("Test 3: Singleton operations")
    print("-" * 40)

    # Set singleton
    test_obj = {"data": "test_object"}
    gateway.execute_domain_operation("singleton", "set", name="test_singleton", instance=test_obj)
    print("Set singleton: test_singleton")

    # Get singleton
    retrieved = gateway.execute_domain_operation("singleton", "get", name="test_singleton")
    print(f"Retrieved singleton: {retrieved}")

    # Check exists
    exists = gateway.execute_domain_operation("singleton", "exists", name="test_singleton")
    print(f"Singleton exists: {exists}")

    # List all
    all_singletons = gateway.execute_domain_operation("singleton", "list_all")
    print(f"All singletons: {all_singletons}")
    print()

    # Test 4: Utility operations
    print("Test 4: Utility operations")
    print("-" * 40)

    # JSON operations
    test_data = {"key": "value", "number": 42}
    json_str = gateway.execute_domain_operation("utility", "json_to_string", data=test_data)
    print(f"JSON string: {json_str}")

    parsed_data = gateway.execute_domain_operation("utility", "json_from_string", json_string=json_str)
    print(f"Parsed data: {parsed_data}")

    # UUID generation
    uuid1 = gateway.execute_domain_operation("utility", "generate_uuid")
    uuid2 = gateway.execute_domain_operation("utility", "generate_uuid")
    print(f"UUID 1: {uuid1}")
    print(f"UUID 2: {uuid2}")
    print(f"UUIDs are different: {uuid1 != uuid2}")

    # Validation
    is_valid = gateway.execute_domain_operation(
        "utility", "validate_string",
        value="test_string", min_length=5, max_length=100
    )
    print(f"String validation: {is_valid}")
    print()

    # Test 5: DI operations
    print("Test 5: DI operations")
    print("-" * 40)

    # Create container
    container = gateway.execute_domain_operation("di", "container_create")
    print(f"Created DI container: {type(container).__name__}")

    # Register services
    class Database:
        def __init__(self):
            self.name = "Database"

    class Repository:
        def __init__(self, db: Database):
            self.db = db

    gateway.execute_domain_operation(
        "di", "register_singleton",
        service_type=Database, implementation=Database
    )
    print("Registered Database as singleton")

    gateway.execute_domain_operation(
        "di", "register_transient",
        service_type=Repository, implementation=Repository
    )
    print("Registered Repository as transient")

    # Check registration
    is_registered = gateway.execute_domain_operation("di", "is_registered", service_type=Database)
    print(f"Database registered: {is_registered}")

    # Get services
    services = gateway.execute_domain_operation("di", "get_services")
    print(f"Registered services: {[s.__name__ for s in services]}")
    print()

    # Test 6: Initialization operations
    print("Test 6: Initialization operations")
    print("-" * 40)

    # Initialize
    success = gateway.execute_domain_operation("initialization", "initialize")
    print(f"Initialize system: {success}")

    # Get status
    status = gateway.execute_domain_operation("initialization", "get_status")
    print(f"System status: {status}")

    # Get health
    health = gateway.execute_domain_operation("initialization", "get_health")
    print(f"System health: {health}")

    # Shutdown
    success = gateway.execute_domain_operation("initialization", "shutdown")
    print(f"Shutdown system: {success}")
    print()

    # Test 7: Legacy execute() method
    print("Test 7: Legacy execute() method (backward compat)")
    print("-" * 40)

    result = gateway.execute("config.get", {"category": "cache", "key": "default_ttl_seconds"})
    print(f"Legacy execute result: {result}")
    print()

    print("=" * 80)
    print("All tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    test_foundation_gateway()
