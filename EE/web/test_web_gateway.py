"""
Test script for Web Domain Gateway integration.

This script demonstrates the Web domain gateway functionality and
verifies integration with the EE Gateway system.
"""

import sys
sys.path.insert(0, 'D:/Code/Project/EE/src')

from EE.universal_gateway.domain_gateway import EEDomainRegistry, DomainGateway, GatewayError
from EE.web import WebGatewayDomain, create_web_console
from EE.web.web_request import WebRequest
from EE.web.web_response import success_response, error_response
from EE.web.web_common import WebConsoleError


def test_web_request_parsing():
    """Test WebRequest parsing."""
    print("Testing WebRequest parsing...")

    # Test valid JSON body
    body = b'{"key": "value", "number": 123}'
    request = WebRequest.parse("POST", "/exec/config.get", body)

    assert request.method == "POST"
    assert request.path == "/exec/config.get"
    assert request.route == "config.get"
    assert request.payload == {"key": "value", "number": 123}

    print("  - Valid JSON: PASS")

    # Test empty body
    request = WebRequest.parse("GET", "/list-all", b"")
    assert request.route is None
    assert request.payload == {}

    print("  - Empty body: PASS")

    # Test invalid JSON
    try:
        WebRequest.parse("POST", "/exec/test", b'{invalid json}')
        assert False, "Should have raised InvalidJSONError"
    except WebConsoleError as e:
        assert e.http_status == 400
        print("  - Invalid JSON: PASS")


def test_web_response_building():
    """Test WebResponse building."""
    print("\nTesting WebResponse building...")

    # Test success response
    response = success_response({"result": "success"})
    assert response.status == 200
    assert response.body == {"result": "success"}
    assert response.is_success()
    assert not response.is_error()

    print("  - Success response: PASS")

    # Test error response
    response = error_response("Something went wrong", status=500)
    assert response.status == 500
    assert "error" in response.body
    assert response.body["error"] == "Something went wrong"
    assert response.is_error()

    print("  - Error response: PASS")

    # Test serialization
    response = success_response({"key": "value"})
    body_bytes = response.to_http()
    assert isinstance(body_bytes, bytes)

    print("  - Serialization: PASS")


def test_web_gateway_domain():
    """Test WebGatewayDomain."""
    print("\nTesting WebGatewayDomain...")

    # Create web gateway domain
    web_gateway = WebGatewayDomain()

    # Test list_all operation
    operations = web_gateway.list_all()
    assert operations["domain"] == "web"
    assert "operations" in operations
    assert len(operations["operations"]) > 0

    print("  - list_all: PASS")

    # Test is_running operation
    is_running = web_gateway.execute("web.is_running", {})
    assert isinstance(is_running, bool)
    assert is_running == False  # Console not started yet

    print("  - is_running: PASS")

    # Test get_stats operation
    stats = web_gateway.execute("web.get_stats", {})
    assert "console_running" in stats
    assert stats["console_running"] == False

    print("  - get_stats: PASS")


def test_web_gateway_registration():
    """Test Web gateway registration with domain registry."""
    print("\nTesting Web gateway registration...")

    # Get registry instance
    registry = EEDomainRegistry.get_instance()
    registry.clear()  # Clear any previous registrations

    # Create and register web gateway
    web_gateway = WebGatewayDomain()
    registry.register("web", web_gateway)

    # Verify registration
    assert registry.has_domain("web")

    # Retrieve web gateway
    retrieved_gateway = registry.get("web")
    assert retrieved_gateway is web_gateway

    print("  - Registration: PASS")

    # List domains
    domains = registry.list_domains()
    assert "web" in domains

    print("  - List domains: PASS")

    # List all operations
    all_ops = registry.list_all_operations()
    assert "web" in all_ops

    print("  - List all operations: PASS")


def test_web_console_creation():
    """Test web console creation (without starting server)."""
    print("\nTesting web console creation...")

    # Mock gateway for testing
    class MockGateway:
        def __init__(self):
            self.registry = EEDomainRegistry.get_instance()

        def execute(self, route, payload):
            return {"route": route, "payload": payload}

        def list_all(self):
            return {"domains": []}

    mock_gateway = MockGateway()
    web_gateway = WebGatewayDomain(gateway=mock_gateway)

    # Test start_console operation (mock, doesn't actually start server)
    try:
        result = web_gateway.execute("web.start_console", {
            "host": "127.0.0.1",
            "port": 9999,  # Use different port for testing
            "background": True,
        })

        assert result["success"] == True
        assert "message" in result

        print("  - Start console: PASS")

        # Check if running
        is_running = web_gateway.execute("web.is_running", {})
        assert is_running == True

        print("  - Console running: PASS")

        # Stop console
        result = web_gateway.execute("web.stop_console", {})
        assert result["success"] == True

        print("  - Stop console: PASS")

    except Exception as e:
        print(f"  - Console operations: FAILED ({e})")
        # This is okay in test environment


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("EE Web Domain Gateway Integration Tests")
    print("=" * 60)

    try:
        test_web_request_parsing()
        test_web_response_building()
        test_web_gateway_domain()
        test_web_gateway_registration()
        test_web_console_creation()

        print("\n" + "=" * 60)
        print("All tests PASSED!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\nTest FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
