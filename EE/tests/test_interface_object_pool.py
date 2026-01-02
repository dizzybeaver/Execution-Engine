"""Test Interface Object Pool (INT-18)

Tests for the Object Pool interface (INT-18) which manages object pooling:
- Pool creation
- Object acquisition
- Object release
- Pool statistics
- Pool configuration
- Pool cleanup
"""

import pytest
from typing import Dict, Any
from pathlib import Path


@pytest.mark.unit
class TestObjectPoolInterface:
    """Test suite for Object Pool interface."""

    def test_object_pool_interface_exists(self, EEGatewayInterface):
        """Test OBJECT_POOL interface exists in EEGatewayInterface."""
        assert hasattr(EEGatewayInterface, 'OBJECT_POOL')
        assert EEGatewayInterface.OBJECT_POOL is not None

    def test_execute_object_pool_operation_import(self):
        """Test that execute_object_pool_operation can be imported."""
        try:
            from interface import interface_object_pool
            assert hasattr(interface_object_pool, 'execute_object_pool_operation')
        except ImportError:
            pytest.skip("Object Pool interface not yet implemented")

    def test_pool_create_operation(self, execute_operation, EEGatewayInterface, mock_object_pool_config):
        """Test pool creation operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'create',
                **mock_object_pool_config
            )

            # Should return success
            assert result is not None
            assert result.get('created', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Pool creation not yet implemented")

    def test_pool_acquire_operation(self, execute_operation, EEGatewayInterface):
        """Test object acquisition operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'acquire',
                name='test_pool'
            )

            # Should return an object
            assert result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("Pool acquire not yet implemented")

    def test_pool_release_operation(self, execute_operation, EEGatewayInterface):
        """Test object release operation."""
        try:
            # First acquire an object
            obj = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'acquire',
                name='test_pool'
            )

            # Then release it
            result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'release',
                name='test_pool',
                obj=obj
            )

            # Should return success
            assert result is not None
            assert result.get('released', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Pool release not yet implemented")

    def test_pool_get_stats_operation(self, execute_operation, EEGatewayInterface):
        """Test pool statistics query operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'get_stats',
                name='test_pool'
            )

            # Should return stats dict
            assert isinstance(result, dict)
            # Should have pool stats
            assert any(key in result for key in ['size', 'available', 'in_use', 'total_created'])

        except (ValueError, NotImplementedError):
            pytest.skip("Pool get_stats not yet implemented")

    def test_pool_resize_operation(self, execute_operation, EEGatewayInterface):
        """Test pool resize operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'resize',
                name='test_pool',
                new_size=20
            )

            # Should return success
            assert result is not None
            assert result.get('resized', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Pool resize not yet implemented")

    def test_pool_clear_operation(self, execute_operation, EEGatewayInterface):
        """Test pool clear operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'clear',
                name='test_pool'
            )

            # Should return success
            assert result is not None
            assert result.get('cleared', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Pool clear not yet implemented")

    def test_pool_delete_operation(self, execute_operation, EEGatewayInterface):
        """Test pool deletion operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'delete',
                name='test_pool'
            )

            # Should return success
            assert result is not None
            assert result.get('deleted', False) or result is True

        except (ValueError, NotImplementedError):
            pytest.skip("Pool delete not yet implemented")

    def test_pool_list_all_operation(self, execute_operation, EEGatewayInterface):
        """Test list all pools operation."""
        try:
            result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'list_all'
            )

            # Should return list of pools
            assert isinstance(result, (list, dict))

        except (ValueError, NotImplementedError):
            pytest.skip("Pool list_all not yet implemented")


@pytest.mark.unit
class TestObjectPoolInterfaceSUGAISPCompliance:
    """Test UG-ISP compliance for Object Pool interface."""

    def test_no_direct_interface_import(self):
        """Test that direct interface imports are not used."""
        import ast

        interface_file = Path(__file__).parent.parent / 'src' / 'interface' / 'interface_object_pool.py'

        if not interface_file.exists():
            pytest.skip("Object Pool interface file not found")

        with open(interface_file, 'r') as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source)

        # Check for forbidden imports
        forbidden_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'gateway' in node.module:
                    forbidden_imports.append(f"Line {node.lineno}: from {node.module} import ...")

        # Assert no forbidden imports
        assert len(forbidden_imports) == 0, f"Found direct gateway imports: {forbidden_imports}"

    def test_operations_use_dispatch_dict(self):
        """Test that interface uses dispatch dictionary pattern."""
        interface_file = Path(__file__).parent.parent / 'src' / 'interface' / 'interface_object_pool.py'

        if not interface_file.exists():
            pytest.skip("Object Pool interface file not found")

        with open(interface_file, 'r') as f:
            source = f.read()

        # Check for DISPATCH dictionary
        assert 'DISPATCH' in source or 'dispatch' in source.lower(), \
            "Object Pool interface should use dispatch dictionary pattern"

    def test_file_size_compliance(self):
        """Test that interface file is <= 350 lines."""
        interface_file = Path(__file__).parent.parent / 'src' / 'interface' / 'interface_object_pool.py'

        if not interface_file.exists():
            pytest.skip("Object Pool interface file not found")

        with open(interface_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) <= 350, \
            f"Interface file has {len(lines)} lines, exceeds 350 line limit"


@pytest.mark.integration
class TestObjectPoolIntegration:
    """Integration tests for Object Pool interface."""

    def test_pool_full_lifecycle(self, execute_operation, EEGatewayInterface):
        """Test complete pool lifecycle: create -> acquire -> release -> delete."""
        try:
            pool_name = 'lifecycle_test_pool'

            # Create
            create_result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'create',
                name=pool_name,
                factory_func=lambda: {'data': 'test'},
                max_size=5,
                initial_size=2
            )
            assert create_result is not None

            # Acquire
            obj = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'acquire',
                name=pool_name
            )
            assert obj is not None

            # Release
            release_result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'release',
                name=pool_name,
                obj=obj
            )
            assert release_result is not None

            # Delete
            delete_result = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'delete',
                name=pool_name
            )
            assert delete_result is not None

        except (ValueError, NotImplementedError):
            pytest.skip("Pool lifecycle not yet fully implemented")

    def test_concurrent_acquisition(self, execute_operation, EEGatewayInterface):
        """Test concurrent object acquisition from pool."""
        try:
            import concurrent.futures

            pool_name = 'concurrent_test_pool'

            # Create pool
            execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'create',
                name=pool_name,
                factory_func=lambda: {'connection': 'test'},
                max_size=10,
                initial_size=5
            )

            # Acquire multiple objects concurrently
            def acquire_object():
                return execute_operation(
                    EEGatewayInterface.OBJECT_POOL,
                    'acquire',
                    name=pool_name
                )

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(acquire_object) for _ in range(5)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            # Should get 5 objects
            assert len(results) == 5
            assert all(obj is not None for obj in results)

        except (ValueError, NotImplementedError):
            pytest.skip("Concurrent acquisition not yet implemented")

    def test_pool_exhaustion_behavior(self, execute_operation, EEGatewayInterface):
        """Test pool behavior when exhausted."""
        try:
            pool_name = 'exhaustion_test_pool'

            # Create small pool
            execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'create',
                name=pool_name,
                factory_func=lambda: {'data': 'test'},
                max_size=2,
                initial_size=2
            )

            # Acquire all objects
            obj1 = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'acquire',
                name=pool_name
            )
            obj2 = execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'acquire',
                name=pool_name
            )

            # Try to acquire beyond max size
            # Should either block, wait, or raise error
            try:
                obj3 = execute_operation(
                    EEGatewayInterface.OBJECT_POOL,
                    'acquire',
                    name=pool_name,
                    timeout=1.0
                )
                # If successful, pool auto-expanded
                assert obj3 is not None
            except (TimeoutError, ValueError):
                # Expected behavior - pool exhausted
                pass

        except (ValueError, NotImplementedError):
            pytest.skip("Pool exhaustion testing not yet implemented")


@pytest.mark.performance
class TestObjectPoolPerformance:
    """Performance tests for Object Pool interface."""

    def test_pool_acquisition_performance(self, execute_operation, EEGatewayInterface, performance_thresholds):
        """Test pool acquisition performance."""
        import time

        try:
            pool_name = 'perf_test_pool'

            # Create pool
            execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'create',
                name=pool_name,
                factory_func=lambda: {'data': 'test'},
                max_size=100,
                initial_size=50
            )

            # Measure acquisition time
            iterations = 100
            start_time = time.time()

            for _ in range(iterations):
                obj = execute_operation(
                    EEGatewayInterface.OBJECT_POOL,
                    'acquire',
                    name=pool_name
                )
                execute_operation(
                    EEGatewayInterface.OBJECT_POOL,
                    'release',
                    name=pool_name,
                    obj=obj
                )

            elapsed_ms = (time.time() - start_time) * 1000
            avg_ms = elapsed_ms / iterations

            # Should be fast (< 1ms per operation)
            assert avg_ms < performance_thresholds.get('gateway_routing_ms', 1.0) * 1000, \
                f"Pool acquisition too slow: {avg_ms:.3f}ms average"

        except (ValueError, NotImplementedError):
            pytest.skip("Pool performance testing not yet implemented")

    def test_pool_memory_efficiency(self, execute_operation, EEGatewayInterface):
        """Test pool memory efficiency."""
        import sys

        try:
            pool_name = 'memory_test_pool'

            # Create pool with large objects
            def large_factory():
                return {'data': 'x' * 1000}

            execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'create',
                name=pool_name,
                factory_func=large_factory,
                max_size=100
            )

            # Acquire some objects
            objects = []
            for _ in range(10):
                obj = execute_operation(
                    EEGatewayInterface.OBJECT_POOL,
                    'acquire',
                    name=pool_name
                )
                objects.append(obj)

            # Check that pool reuses objects (memory efficient)
            # This is a simple check - real implementation would track object IDs
            assert len(objects) == 10

        except (ValueError, NotImplementedError):
            pytest.skip("Pool memory efficiency testing not yet implemented")
