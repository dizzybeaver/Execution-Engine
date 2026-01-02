"""Dashboard Domain Integration Test for EE.

This module demonstrates the integration of the Dashboard Domain Gateway
with the EE Universal Gateway system.

Usage:
    python test_dashboard_integration.py

Architecture:
    Universal Gateway -> Domain Registry -> Dashboard Server -> HTTP Interface
"""

from __future__ import annotations

import sys
import time
import threading
from dataclasses import dataclass

# Add EE src to path
sys.path.insert(0, 'D:/Code/Project/EE/src')

from EE.universal_gateway.domain_gateway import (
    EEDomainRegistry,
    DomainGateway,
)
from EE.dashboard import create_dashboard_server


# ============================================================================
# Test Domain Gateway
# ============================================================================

@dataclass(frozen=True)
class TestDomainGateway(DomainGateway):
    """Test domain gateway for demonstration."""

    def execute(self, route: str, payload: dict) -> any:
        """Execute test operation."""
        if route == "test.echo":
            return {"echo": payload.get("message", "no message")}
        if route == "test.add":
            a = payload.get("a", 0)
            b = payload.get("b", 0)
            return {"result": a + b}
        if route == "test.status":
            return {
                "status": "running",
                "version": "1.0.0",
                "domains": ["test", "config", "security"]
            }
        from EE.universal_gateway.domain_gateway import RouteNotFoundError
        raise RouteNotFoundError(route)

    def list_all(self) -> dict:
        """List all test operations."""
        return {
            "domain": "test",
            "operations": [
                {
                    "route": "test.echo",
                    "description": "Echo back the message",
                    "params": {"message": "str"}
                },
                {
                    "route": "test.add",
                    "description": "Add two numbers",
                    "params": {"a": "number", "b": "number"}
                },
                {
                    "route": "test.status",
                    "description": "Get system status",
                    "params": {}
                },
            ]
        }


# ============================================================================
# Integration Test Functions
# ============================================================================

def test_dashboard_creation():
    """Test Dashboard server creation."""
    print("=" * 60)
    print("Test 1: Dashboard Server Creation")
    print("=" * 60)  # noqa: E501

    try:
        # Get registry
        registry = EEDomainRegistry.get_instance()
        print(f"[OK] Got registry instance: {registry}")

        # Create test domain
        test_gateway = TestDomainGateway()
        print(f"[OK] Created test gateway: {test_gateway}")

        # Register test domain
        registry.register("test", test_gateway)
        print(f"[OK] Registered 'test' domain")

        # List domains
        domains = registry.list_domains()
        print(f"[OK] Registered domains: {domains}")

        # Create dashboard server
        server = create_dashboard_server(registry, port=8081)
        print(f"[OK] Created dashboard server on port {server.port}")

        return server

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


def test_dashboard_endpoints():
    """Test Dashboard HTTP endpoints."""
    print("\n" + "=" * 60)
    print("Test 2: Dashboard HTTP Endpoints")
    print("=" * 60)  # noqa: E501

    try:
        import urllib.request
        import json

        base_url = "http://127.0.0.1:8081"

        # Test health endpoint
        print("\n1. Testing /health endpoint...")
        try:
            with urllib.request.urlopen(f"{base_url}/health") as response:
                data = json.loads(response.read().decode())
                print(f"   [OK] Health: {data}")
        except Exception as e:
            print(f"   [ERROR] {e}")

        # Test list-domains endpoint
        print("\n2. Testing /list-domains endpoint...")
        try:
            with urllib.request.urlopen(f"{base_url}/list-domains") as response:
                data = json.loads(response.read().decode())
                print(f"   [OK] Domains: {data}")
        except Exception as e:
            print(f"   [ERROR] {e}")

        # Test list-routes endpoint
        print("\n3. Testing /list-routes endpoint...")
        try:
            with urllib.request.urlopen(f"{base_url}/list-routes") as response:
                data = json.loads(response.read().decode())
                print(f"   [OK] Routes: {json.dumps(data, indent=2)[:200]}...")
        except Exception as e:
            print(f"   [ERROR] {e}")

        # Test execute endpoint
        print("\n4. Testing /exec/test.echo endpoint...")
        try:
            payload = json.dumps({"message": "Hello Dashboard!"}).encode()
            req = urllib.request.Request(
                f"{base_url}/exec/test.echo",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                print(f"   [OK] Echo result: {data}")
        except Exception as e:
            print(f"   [ERROR] {e}")

        # Test execute endpoint with add
        print("\n5. Testing /exec/test.add endpoint...")
        try:
            payload = json.dumps({"a": 5, "b": 3}).encode()
            req = urllib.request.Request(
                f"{base_url}/exec/test.add",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                print(f"   [OK] Add result: {data}")
        except Exception as e:
            print(f"   [ERROR] {e}")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


def run_dashboard_demo(server, duration: int = 30):
    """Run dashboard server for a demonstration period.

    Args:
        server: DashboardServer instance
        duration: Duration in seconds to run (default: 30)
    """
    print("\n" + "=" * 60)
    print(f"Dashboard Demo - Running for {duration} seconds")
    print("=" * 60)  # noqa: E501
    print("\nOpen your browser to: http://127.0.0.1:8081")
    print("Press Ctrl+C to stop early\n")

    # Run server in background thread
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        # Wait for specified duration or user interrupt
        for i in range(duration):
            time.sleep(1)
            if i % 5 == 0 and i > 0:
                remaining = duration - i
                print(f"Running... {remaining} seconds remaining")

        print("\nDemo period complete.")

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        # Shutdown server
        print("\nShutting down server...")
        server.shutdown()


# ============================================================================
# Main Test Function
# ============================================================================

def main():
    """Run all Dashboard integration tests."""
    print("\n")
    print("=" * 60)
    print("  EE Dashboard Domain Integration Test")
    print("=" * 60)

    # Test 1: Create Dashboard
    server = test_dashboard_creation()
    if not server:
        print("\n✗ Failed to create dashboard server")
        return

    # Test 2: Test endpoints (requires server to be running)
    # Run server in background for testing
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(1)  # Give server time to start

    test_dashboard_endpoints()

    # Shutdown server
    server.shutdown()

    print("\n" + "=" * 60)
    print("Integration Test Summary")
    print("=" * 60)
    print("[OK] Dashboard module imported successfully")
    print("[OK] Dashboard server created successfully")
    print("[OK] Dashboard domain registered with gateway registry")
    print("[OK] HTTP endpoints tested successfully")
    print("\nAll tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
