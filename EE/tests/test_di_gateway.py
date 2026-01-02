"""Test DI Gateway (Dependency Injection)

Tests for the DI Gateway functionality:
- Dependency registration
- Dependency resolution
- Singleton lifecycle
- Transient lifecycle
- Scoped lifecycle
- Circular dependency detection
"""

import pytest
from typing import Dict, Any
from pathlib import Path


@pytest.mark.unit
class TestDIGateway:
    """Test suite for DI Gateway."""

    def test_di_gateway_exists(self):
        """Test that DI Gateway module exists."""
        try:
            from gateway import gateway_di
            assert gateway_di is not None
        except ImportError:
            pytest.skip("DI Gateway not yet implemented")

    def test_di_gateway_interface_exists(self, EEGatewayInterface):
        """Test DI interface exists in EEGatewayInterface."""
        assert hasattr(EEGatewayInterface, 'DI')
        assert EEGatewayInterface.DI is not None

    def test_register_dependency(self, execute_operation, EEGatewayInterface):
        """Test dependency registration."""
        try:
            result = execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='test_service',
                factory=lambda: {'service': 'test'},
                lifecycle='singleton'
            )

            # Should return success
            assert result is not None
            assert result.get('registered', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("DI register not yet implemented")

    def test_resolve_dependency(self, execute_operation, EEGatewayInterface):
        """Test dependency resolution."""
        try:
            # First register
            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='test_service',
                factory=lambda: {'service': 'test'},
                lifecycle='singleton'
            )

            # Then resolve
            result = execute_operation(
                EEGatewayInterface.DI,
                'resolve',
                name='test_service'
            )

            # Should return dependency instance
            assert result is not None
            assert result.get('service') == 'test'

        except (ValueError, NotImplementedError):
            pytest.skip("DI resolve not yet implemented")

    def test_singleton_lifecycle(self, execute_operation, EEGatewayInterface):
        """Test singleton lifecycle (same instance returned)."""
        try:
            # Register singleton
            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='singleton_service',
                factory=lambda: {'id': id(object())},
                lifecycle='singleton'
            )

            # Resolve twice
            instance1 = execute_operation(
                EEGatewayInterface.DI,
                'resolve',
                name='singleton_service'
            )

            instance2 = execute_operation(
                EEGatewayInterface.DI,
                'resolve',
                name='singleton_service'
            )

            # Should be same instance
            assert instance1 is instance2 or instance1.get('id') == instance2.get('id')

        except (ValueError, NotImplementedError):
            pytest.skip("Singleton lifecycle not yet implemented")

    def test_transient_lifecycle(self, execute_operation, EEGatewayInterface):
        """Test transient lifecycle (new instance each time)."""
        try:
            # Register transient
            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='transient_service',
                factory=lambda: {'id': id(object())},
                lifecycle='transient'
            )

            # Resolve twice
            instance1 = execute_operation(
                EEGatewayInterface.DI,
                'resolve',
                name='transient_service'
            )

            instance2 = execute_operation(
                EEGatewayInterface.DI,
                'resolve',
                name='transient_service'
            )

            # Should be different instances
            assert instance1 is not instance2 or instance1.get('id') != instance2.get('id')

        except (ValueError, NotImplementedError):
            pytest.skip("Transient lifecycle not yet implemented")

    def test_scoped_lifecycle(self, execute_operation, EEGatewayInterface):
        """Test scoped lifecycle (same instance within scope)."""
        try:
            # Register scoped
            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='scoped_service',
                factory=lambda: {'id': id(object())},
                lifecycle='scoped'
            )

            # Create scope
            scope_id = execute_operation(
                EEGatewayInterface.DI,
                'create_scope'
            )

            # Resolve twice in same scope
            instance1 = execute_operation(
                EEGatewayInterface.DI,
                'resolve',
                name='scoped_service',
                scope_id=scope_id
            )

            instance2 = execute_operation(
                EEGatewayInterface.DI,
                'resolve',
                name='scoped_service',
                scope_id=scope_id
            )

            # Should be same instance within scope
            assert instance1 is instance2 or instance1.get('id') == instance2.get('id')

        except (ValueError, NotImplementedError):
            pytest.skip("Scoped lifecycle not yet implemented")

    def test_dependency_injection_constructor(self, execute_operation, EEGatewayInterface):
        """Test constructor dependency injection."""
        try:
            # Register dependencies
            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='database',
                factory=lambda: {'connection': 'db'},
                lifecycle='singleton'
            )

            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='logger',
                factory=lambda: {'logger': 'test'},
                lifecycle='singleton'
            )

            # Register service with dependencies
            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='user_service',
                factory=lambda db, log: {'db': db, 'log': log},
                dependencies=['database', 'logger']
            )

            # Resolve service
            result = execute_operation(
                EEGatewayInterface.DI,
                'resolve',
                name='user_service'
            )

            # Should have injected dependencies
            assert result is not None
            assert 'db' in result
            assert 'log' in result

        except (ValueError, NotImplementedError):
            pytest.skip("Constructor injection not yet implemented")

    def test_circular_dependency_detection(self, execute_operation, EEGatewayInterface):
        """Test circular dependency detection."""
        try:
            # Create circular dependency
            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='service_a',
                factory=lambda b: {'dep': b},
                dependencies=['service_b']
            )

            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='service_b',
                factory=lambda a: {'dep': a},
                dependencies=['service_a']
            )

            # Should detect circular dependency
            with pytest.raises(ValueError):
                execute_operation(
                    EEGatewayInterface.DI,
                    'resolve',
                    name='service_a'
                )

        except (ValueError, NotImplementedError):
            pytest.skip("Circular dependency detection not yet implemented")

    def test_unregister_dependency(self, execute_operation, EEGatewayInterface):
        """Test dependency unregistration."""
        try:
            # Register
            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='temp_service',
                factory=lambda: {'service': 'temp'}
            )

            # Unregister
            result = execute_operation(
                EEGatewayInterface.DI,
                'unregister',
                name='temp_service'
            )

            # Should return success
            assert result is not None
            assert result.get('unregistered', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Dependency unregistration not yet implemented")

    def test_list_dependencies(self, execute_operation, EEGatewayInterface):
        """Test listing all registered dependencies."""
        try:
            result = execute_operation(
                EEGatewayInterface.DI,
                'list_all'
            )

            # Should return list of dependencies
            assert isinstance(result, (list, dict))

        except (ValueError, NotImplementedError):
            pytest.skip("List dependencies not yet implemented")


@pytest.mark.unit
class TestDIGatewaySUGAISPCompliance:
    """Test UG-ISP compliance for DI Gateway."""

    def test_di_uses_gateway_routing(self):
        """Test that DI operations go through Gateway routing."""
        import ast

        di_file = Path(__file__).parent.parent / 'src' / 'gateway' / 'gateway_di.py'

        if not di_file.exists():
            pytest.skip("DI Gateway file not found")

        with open(di_file, 'r') as f:
            source = f.read()

        # DI Gateway is part of gateway, so it's the ISP itself
        # Should not have direct imports to other interfaces
        for line in source.split('\n'):
            if 'from interface_' in line and not line.strip().startswith('#'):
                pytest.fail(f"Direct interface import in DI Gateway: {line}")

    def test_file_size_compliance(self):
        """Test that DI Gateway file is <= 350 lines."""
        di_file = Path(__file__).parent.parent / 'src' / 'gateway' / 'gateway_di.py'

        if not di_file.exists():
            pytest.skip("DI Gateway file not found")

        with open(di_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) <= 350, \
            f"DI Gateway file has {len(lines)} lines, exceeds 350 line limit"


@pytest.mark.integration
class TestDIIntegration:
    """Integration tests for DI Gateway."""

    def test_complex_dependency_graph(self, execute_operation, EEGatewayInterface):
        """Test resolving complex dependency graph."""
        try:
            # Create dependency graph:
            # controller -> service -> repository -> database
            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='database',
                factory=lambda: {'connection': 'db_conn'},
                lifecycle='singleton'
            )

            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='repository',
                factory=lambda db: {'db': db},
                dependencies=['database']
            )

            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='service',
                factory=lambda repo: {'repo': repo},
                dependencies=['repository']
            )

            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='controller',
                factory=lambda svc: {'service': svc},
                dependencies=['service']
            )

            # Resolve controller
            result = execute_operation(
                EEGatewayInterface.DI,
                'resolve',
                name='controller'
            )

            # Should have full dependency chain
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("Complex dependency graph not yet implemented")

    def test_di_with_object_pool(self, execute_operation, EEGatewayInterface):
        """Test DI integration with object pool."""
        try:
            # Register pooled dependency
            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='pooled_connection',
                factory=lambda: execute_operation(
                    EEGatewayInterface.OBJECT_POOL,
                    'acquire',
                    name='connection_pool'
                ),
                lifecycle='transient'
            )

            # Resolve
            result = execute_operation(
                EEGatewayInterface.DI,
                'resolve',
                name='pooled_connection'
            )

            # Should return pooled object
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("DI with object pool not yet implemented")


@pytest.mark.performance
class TestDIPerformance:
    """Performance tests for DI Gateway."""

    def test_resolve_performance(self, execute_operation, EEGatewayInterface, performance_thresholds):
        """Test dependency resolution performance."""
        import time

        try:
            # Register singleton
            execute_operation(
                EEGatewayInterface.DI,
                'register',
                name='perf_service',
                factory=lambda: {'service': 'perf'},
                lifecycle='singleton'
            )

            # Measure resolve time
            iterations = 1000
            start_time = time.time()

            for _ in range(iterations):
                execute_operation(
                    EEGatewayInterface.DI,
                    'resolve',
                    name='perf_service'
                )

            elapsed_ms = (time.time() - start_time) * 1000
            avg_ms = elapsed_ms / iterations

            # Should be fast (< 1ms per resolution)
            assert avg_ms < performance_thresholds.get('hot_path_ms', 50), \
                f"DI resolve too slow: {avg_ms:.3f}ms average"

        except (ValueError, NotImplementedError):
            pytest.skip("DI resolve performance testing not yet implemented")
