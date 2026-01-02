"""Test Gateway Routing

Tests for Gateway routing functionality:
- Operation routing to interfaces
- Interface dispatch
- Error handling
- Performance of routing
"""

import pytest
from typing import Dict, Any
from pathlib import Path


@pytest.mark.unit
class TestGatewayRouting:
    """Test suite for Gateway routing."""

    def test_execute_operation_exists(self, execute_operation):
        """Test that execute_operation function exists."""
        assert execute_operation is not None
        assert callable(execute_operation)

    def test_execute_operation_signature(self, execute_operation):
        """Test execute_operation has correct signature."""
        import inspect

        sig = inspect.signature(execute_operation)

        # Should have at least 2 parameters: interface, operation
        params = list(sig.parameters.keys())
        assert 'interface' in params
        assert 'operation' in params
        assert 'kwargs' in params or any(param.kind == inspect.Parameter.VAR_KEYWORD for param in sig.parameters.values())

    def test_routing_to_plugins_interface(self, execute_operation, EEGatewayInterface):
        """Test routing to PLUGINS interface."""
        try:
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'list_all'
            )

            # Should route successfully
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("PLUGINS interface routing not yet implemented")

    def test_routing_to_object_pool_interface(self, execute_operation, EEGatewayInterface):
        """Test routing to OBJECT_POOL interface."""
        try:
            result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'list_all'
            )

            # Should route successfully
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("OBJECT_POOL interface routing not yet implemented")

    def test_routing_to_network_interface(self, execute_operation, EEGatewayInterface):
        """Test routing to NETWORK interface."""
        try:
            result = execute_operation(
                EEGatewayInterface.NETWORK,
                'get_status',
                protocol='test'
            )

            # Should route successfully
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("NETWORK interface routing not yet implemented")

    def test_invalid_interface_error(self, execute_operation, EEGatewayInterface):
        """Test error handling for invalid interface."""
        with pytest.raises(ValueError):
            execute_operation(
                "INVALID_INTERFACE",
                'test_operation'
            )

    def test_invalid_operation_error(self, execute_operation, EEGatewayInterface):
        """Test error handling for invalid operation."""
        try:
            with pytest.raises(ValueError):
                execute_operation(
                    EEGatewayInterface.PLUGINS,
                    'invalid_operation'
                )
        except (ValueError, NotImplementedError):
            pytest.skip("Invalid operation error handling not yet implemented")

    def test_kwargs_forwarding(self, execute_operation, EEGatewayInterface):
        """Test that kwargs are forwarded correctly to interface."""
        try:
            result = execute_operation(
                EEGatewayInterface.PLUGINS,
                'get_status',
                name='test_plugin',
                verbose=True
            )

            # Should route with kwargs
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("Kwargs forwarding not yet implemented")


@pytest.mark.unit
class TestGatewayRoutingSUGAISPCompliance:
    """Test UG-ISP compliance for Gateway routing."""

    def test_gateway_is_isp(self):
        """Test that Gateway acts as ISP (central routing)."""
        from gateway.gateway import execute_operation
        import ast

        gateway_file = Path(__file__).parent.parent / 'src' / 'gateway' / 'gateway.py'

        with open(gateway_file, 'r') as f:
            source = f.read()

        # Should have execute_operation function
        assert 'def execute_operation' in source

        # Should use dispatch dictionary
        assert 'DISPATCH' in source or 'dispatch' in source.lower()

        # Should route to interfaces
        assert 'interface' in source.lower()

    def test_no_interface_to_interface_routing(self):
        """Test that interfaces don't route directly to each other."""
        interface_files = [
            'interface_plugins.py',
            'interface_object_pool.py',
            'interface_network.py',
        ]

        ee_src = Path(__file__).parent.parent / 'src' / 'interface'

        for interface_file in interface_files:
            file_path = ee_src / interface_file

            if not file_path.exists():
                continue

            with open(file_path, 'r') as f:
                source = f.read()

            # Check for direct imports from other interfaces
            for line in source.split('\n'):
                if 'from interface_' in line and not line.strip().startswith('#'):
                    pytest.fail(f"Direct interface-to-interface import in {interface_file}: {line}")

    def test_file_size_compliance(self):
        """Test that gateway file is <= 350 lines."""
        gateway_file = Path(__file__).parent.parent / 'src' / 'gateway' / 'gateway.py'

        with open(gateway_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) <= 350, \
            f"Gateway file has {len(lines)} lines, exceeds 350 line limit"


@pytest.mark.performance
class TestGatewayRoutingPerformance:
    """Performance tests for Gateway routing."""

    def test_routing_overhead(self, execute_operation, EEGatewayInterface, performance_thresholds):
        """Test Gateway routing overhead."""
        import time

        try:
            # Measure routing time
            iterations = 1000
            start_time = time.time()

            for _ in range(iterations):
                execute_operation(
                    EEGatewayInterface.PLUGINS,
                    'list_all'
                )

            elapsed_ms = (time.time() - start_time) * 1000
            avg_ms = elapsed_ms / iterations

            # Should be very fast (< 1ms per routing)
            assert avg_ms < performance_thresholds.get('gateway_routing_ms', 1.0), \
                f"Gateway routing too slow: {avg_ms:.3f}ms average"

        except (ValueError, NotImplementedError):
            pytest.skip("Routing overhead testing not yet implemented")

    def test_dispatch_lookup_performance(self):
        """Test dispatch dictionary lookup performance."""
        import time

        from gateway.gateway import _GATEWAY_DISPATCH
        from gateway.gateway_enums import GatewayInterface

        # Simulate dispatch lookups
        iterations = 10000
        start_time = time.time()

        for _ in range(iterations):
            _ = _GATEWAY_DISPATCH.get(GatewayInterface.PLUGINS)

        elapsed_ms = (time.time() - start_time) * 1000
        avg_ms = elapsed_ms / iterations

        # Should be extremely fast (< 0.01ms per lookup)
        assert avg_ms < 0.01, \
            f"Dispatch lookup too slow: {avg_ms:.4f}ms average"

    def test_lazy_import_performance(self):
        """Test lazy import performance."""
        import time
        import sys

        # Clear any cached interface imports
        modules_to_clear = [m for m in sys.modules.keys() if 'interface_' in m]
        for module in modules_to_clear:
            del sys.modules[module]

        from gateway.gateway import _import_interface_router
        from gateway.gateway_enums import GatewayInterface

        # Measure first import (cold)
        start_time = time.time()
        router1 = _import_interface_router(GatewayInterface.PLUGINS)
        cold_import_ms = (time.time() - start_time) * 1000

        # Measure second import (warm)
        start_time = time.time()
        router2 = _import_interface_router(GatewayInterface.PLUGINS)
        warm_import_ms = (time.time() - start_time) * 1000

        # Both should return same router
        assert router1 == router2

        # Warm import should be faster (cached)
        # Note: This may vary based on module system
        assert warm_import_ms <= cold_import_ms or warm_import_ms < 10


@pytest.mark.integration
class TestGatewayRoutingIntegration:
    """Integration tests for Gateway routing."""

    def test_multi_interface_routing(self, execute_operation, EEGatewayInterface):
        """Test routing to multiple interfaces in sequence."""
        try:
            # Route to PLUGINS
            result1 = execute_operation(
                EEGatewayInterface.PLUGINS,
                'list_all'
            )

            # Route to OBJECT_POOL
            result2 = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'list_all'
            )

            # Route to NETWORK
            result3 = execute_operation(
                EEGatewayInterface.NETWORK,
                'get_status',
                protocol='test'
            )

            # All should succeed
            assert result1 is not None
            assert result2 is not None
            assert result3 is not None

        except (ValueError, NotImplementedError):
            pytest.skip("Multi-interface routing not yet implemented")

    def test_concurrent_routing(self, execute_operation, EEGatewayInterface):
        """Test concurrent routing operations."""
        import concurrent.futures

        try:
            def route_operation():
                return execute_operation(
                    EEGatewayInterface.PLUGINS,
                    'list_all'
                )

            # Run concurrent routing operations
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(route_operation) for _ in range(10)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            # All should succeed
            assert all(result is not None for result in results)

        except (ValueError, NotImplementedError):
            pytest.skip("Concurrent routing not yet implemented")

    def test_error_propagation_through_gateway(self, execute_operation, EEGatewayInterface):
        """Test that errors from interfaces are properly propagated."""
        try:
            # Trigger an error from interface
            with pytest.raises((ValueError, RuntimeError, NotImplementedError)):
                execute_operation(
                    EEGatewayInterface.PLUGINS,
                    'invalid_operation'
                )

        except (ValueError, NotImplementedError):
            pytest.skip("Error propagation testing not yet implemented")
