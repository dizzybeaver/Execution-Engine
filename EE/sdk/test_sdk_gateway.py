"""
Test SDK Gateway Domain Integration

This script tests the SDK Gateway Domain to verify:
- SDK gateway creation
- Local SDK creation and execution
- Remote SDK creation
- Gateway registry integration
"""

import sys
sys.path.insert(0, 'D:/Code/Project/EE/src')

from EE.sdk import SDKGatewayDomain, SDKGatewayError
from EE.universal_gateway.domain_gateway import EEDomainRegistry


def test_local_sdk():
    """Test local SDK functionality."""
    print("Testing Local SDK...")

    # Create a simple handler
    def process_handler(params):
        data = params.get("data", "")
        return {
            "result": f"processed: {data}",
            "length": len(data)
        }

    def validate_handler(params):
        data = params.get("data", "")
        return {
            "valid": len(data) > 0,
            "data": data
        }

    # Create SDK gateway
    sdk_gateway = SDKGatewayDomain()

    # Create local SDK
    result = sdk_gateway.execute("sdk.create", {
        "sdk_type": "local",
        "name": "test_processor",
        "config": {
            "methods": {
                "process": process_handler,
                "validate": validate_handler
            },
            "timeout": 30
        }
    })

    print(f"  Created SDK: {result['message']}")
    assert result["success"] == True

    # Call SDK method
    result = sdk_gateway.execute("sdk.call", {
        "sdk_name": "test_processor",
        "method": "process",
        "params": {"data": "hello world"}
    })

    print(f"  Called method: {result['result']}")
    assert result["success"] == True
    assert result["result"]["result"] == "processed: hello world"

    # Get status
    status = sdk_gateway.execute("sdk.get_status", {
        "sdk_name": "test_processor"
    })

    print(f"  SDK status: {status['status']}")
    assert status["status"] == "initialized"

    # List instances
    instances = sdk_gateway.execute("sdk.list_instances", {})
    print(f"  Total instances: {instances['count']}")
    assert instances['count'] == 1

    # Shutdown
    result = sdk_gateway.execute("sdk.shutdown", {
        "sdk_name": "test_processor"
    })

    print(f"  Shutdown: {result['message']}")
    assert result["success"] == True

    print("  Local SDK test passed!")


def test_registry_integration():
    """Test gateway registry integration."""
    print("\nTesting Registry Integration...")

    # Get registry
    registry = EEDomainRegistry.get_instance()

    # Create SDK gateway
    sdk_gateway = SDKGatewayDomain()

    # Register SDK domain
    registry.register("sdk", sdk_gateway)
    print("  Registered SDK domain")

    # Verify domain is registered
    assert registry.has_domain("sdk")
    print("  Domain verified in registry")

    # Execute through registry
    result = registry.get("sdk").execute("sdk.list_operations", {})
    print(f"  Operations: {result['domain']}")
    assert result["domain"] == "sdk"

    print("  Registry integration test passed!")


def test_validation():
    """Test configuration validation."""
    print("\nTesting Configuration Validation...")

    sdk_gateway = SDKGatewayDomain()

    # Test valid local config
    result = sdk_gateway.execute("sdk.validate_config", {
        "sdk_type": "local",
        "config": {
            "methods": {"test": lambda x: x},
            "timeout": 30
        }
    })

    print(f"  Local config validation: {result['success']}")
    assert result["success"] == True

    # Test invalid local config (missing methods)
    result = sdk_gateway.execute("sdk.validate_config", {
        "sdk_type": "local",
        "config": {
            "timeout": 30
        }
    })

    print(f"  Invalid local config: {not result['success']}")
    assert result["success"] == False

    # Test valid remote config
    result = sdk_gateway.execute("sdk.validate_config", {
        "sdk_type": "remote",
        "config": {
            "base_url": "https://api.example.com",
            "methods": {"process": "/api/process"},
            "timeout": 30
        }
    })

    print(f"  Remote config validation: {result['success']}")
    assert result["success"] == True

    print("  Configuration validation test passed!")


def test_error_handling():
    """Test error handling."""
    print("\nTesting Error Handling...")

    sdk_gateway = SDKGatewayDomain()

    # Test calling non-existent SDK
    try:
        sdk_gateway.execute("sdk.call", {
            "sdk_name": "nonexistent",
            "method": "test",
            "params": {}
        })
        assert False, "Should have raised GatewayError"
    except Exception as e:
        print(f"  Caught error: {type(e).__name__}")
        assert "not found" in str(e).lower() or "SDK" in str(e)

    # Test invalid route
    try:
        sdk_gateway.execute("sdk.invalid_route", {})
        assert False, "Should have raised GatewayError"
    except Exception as e:
        print(f"  Caught invalid route error: {type(e).__name__}")
        assert "unknown" in str(e).lower() or "route" in str(e).lower()

    print("  Error handling test passed!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("SDK Gateway Domain Integration Tests")
    print("=" * 60)

    try:
        test_local_sdk()
        test_registry_integration()
        test_validation()
        test_error_handling()

        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
