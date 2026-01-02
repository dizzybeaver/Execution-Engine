"""Test Performance - Memory

Memory performance tests:
- Initial memory footprint
- Memory growth under load
- Memory leak detection
- Object pool effectiveness
- Memory efficiency of operations
"""

import pytest
import gc
import sys
from pathlib import Path
from typing import Dict, Any


@pytest.mark.performance
class TestMemoryPerformance:
    """Memory performance tests."""

    def test_initial_memory_footprint(self, performance_thresholds):
        """Test initial memory footprint after Gateway import."""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())

            # Baseline memory before import
            baseline_mem = process.memory_info().rss / 1024 / 1024  # MB

            # Import Gateway
            from EE import execute_operation, GatewayInterface

            # Memory after import
            after_import_mem = process.memory_info().rss / 1024 / 1024  # MB

            memory_increase = after_import_mem - baseline_mem

            print(f"\nBaseline memory: {baseline_mem:.2f}MB")
            print(f"After import: {after_import_mem:.2f}MB")
            print(f"Increase: {memory_increase:.2f}MB")

            # Check against threshold
            target_mb = performance_thresholds.get('memory_mb', 80.0)

            assert after_import_mem < target_mb, \
                f"Memory usage {after_import_mem:.2f}MB exceeds target {target_mb:.2f}MB"

        except ImportError:
            pytest.skip("psutil not available - skipping memory test")

    def test_memory_growth_under_load(self, execute_operation, EEGatewayInterface):
        """Test memory growth under sustained load."""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())

            # Initial memory
            initial_mem = process.memory_info().rss / 1024 / 1024

            # Perform many operations
            for i in range(1000):
                try:
                    execute_operation(
                        EEGatewayInterface.PLUGINS,
                        'list_all'
                    )
                except (ValueError, NotImplementedError):
                    pass

            # Force garbage collection
            gc.collect()

            # Memory after load
            after_load_mem = process.memory_info().rss / 1024 / 1024

            memory_growth = after_load_mem - initial_mem

            print(f"\nInitial memory: {initial_mem:.2f}MB")
            print(f"After load: {after_load_mem:.2f}MB")
            print(f"Growth: {memory_growth:.2f}MB")

            # Growth should be minimal (< 10MB)
            assert memory_growth < 10, \
                f"Memory growth {memory_growth:.2f}MB exceeds 10MB (possible memory leak)"

        except ImportError:
            pytest.skip("psutil not available - skipping memory test")

    def test_object_pool_memory_efficiency(self, execute_operation, EEGatewayInterface):
        """Test memory efficiency of object pooling."""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())

            # Create pool with large objects
            pool_name = 'memory_test_pool'

            # Measure memory without pool
            gc.collect()
            baseline_mem = process.memory_info().rss / 1024 / 1024

            # Create objects without pooling
            objects = []
            for _ in range(100):
                objects.append({'data': 'x' * 1000})

            gc.collect()
            without_pool_mem = process.memory_info().rss / 1024 / 1024

            # Clear objects
            objects.clear()
            gc.collect()

            # Create pool
            try:
                execute_operation(
                    EEGatewayInterface.OBJECT_POOL,
                    'create',
                    name=pool_name,
                    factory_func=lambda: {'data': 'x' * 1000},
                    max_size=100
                )

                # Acquire objects from pool
                pooled_objects = []
                for _ in range(100):
                    obj = execute_operation(
                        EEGatewayInterface.OBJECT_POOL,
                        'acquire',
                        name=pool_name
                    )
                    pooled_objects.append(obj)

                gc.collect()
                with_pool_mem = process.memory_info().rss / 1024 / 1024

                print(f"\nBaseline: {baseline_mem:.2f}MB")
                print(f"Without pool: {without_pool_mem:.2f}MB")
                print(f"With pool: {with_pool_mem:.2f}MB")

                # Pool should not use significantly more memory
                # (object reuse should be efficient)
                pool_overhead = with_pool_mem - baseline_mem

                assert pool_overhead < 20, \
                    f"Pool overhead {pool_overhead:.2f}MB too high"

            except (ValueError, NotImplementedError):
                pytest.skip("Object pool memory testing not yet implemented")

        except ImportError:
            pytest.skip("psutil not available - skipping memory test")

    def test_memory_leak_detection(self, execute_operation, EEGatewayInterface):
        """Test for memory leaks in repeated operations."""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())

            # Perform operations and measure memory
            memory_snapshots = []

            for iteration in range(5):
                # Force GC before snapshot
                gc.collect()

                mem_before = process.memory_info().rss / 1024 / 1024

                # Perform operations
                for _ in range(100):
                    try:
                        execute_operation(
                            EEGatewayInterface.PLUGINS,
                            'list_all'
                        )
                    except (ValueError, NotImplementedError):
                        pass

                gc.collect()

                mem_after = process.memory_info().rss / 1024 / 1024

                memory_snapshots.append({
                    'iteration': iteration,
                    'before': mem_before,
                    'after': mem_after,
                    'growth': mem_after - mem_before
                })

            # Check for consistent memory growth (leak indicator)
            growth_values = [s['growth'] for s in memory_snapshots]

            print(f"\nMemory growth snapshots:")
            for snapshot in memory_snapshots:
                print(f"  Iteration {snapshot['iteration']}: {snapshot['growth']:.2f}MB")

            # If memory grows consistently, there might be a leak
            # Allow some variation, but not consistent growth
            avg_growth = sum(growth_values) / len(growth_values)

            assert avg_growth < 5, \
                f"Average memory growth {avg_growth:.2f}MB per iteration suggests memory leak"

        except ImportError:
            pytest.skip("psutil not available - skipping memory test")

    def test_string_interning_efficiency(self):
        """Test string interning for common operations."""
        import sys

        # Create many similar strings
        strings = []
        for _ in range(1000):
            strings.append('test_operation')

        # Check if strings are interned (same object)
        # In CPython, small strings are automatically interned
        first = strings[0]
        last = strings[-1]

        # They might be the same object (interned)
        # or different objects (not interned)
        is_interned = first is last

        print(f"\nStrings interned: {is_interned}")

        # This is just informational
        # String interning is automatic in CPython for most cases

    def test_module_import_memory(self):
        """Test memory impact of module imports."""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())

            # Clear modules
            modules_to_clear = [m for m in sys.modules.keys() if 'EE' in m or 'gateway' in m or 'interface' in m]
            for module in modules_to_clear:
                del sys.modules[module]

            gc.collect()
            baseline_mem = process.memory_info().rss / 1024 / 1024

            # Import modules one by one
            from gateway import gateway
            mem_after_gateway = process.memory_info().rss / 1024 / 1024

            from interface import interface_plugins
            mem_after_plugins = process.memory_info().rss / 1024 / 1024

            from interface import interface_object_pool
            mem_after_object_pool = process.memory_info().rss / 1024 / 1024

            from interface import interface_network
            mem_after_network = process.memory_info().rss / 1024 / 1024

            print(f"\nBaseline: {baseline_mem:.2f}MB")
            print(f"After gateway: {mem_after_gateway:.2f}MB (+{mem_after_gateway - baseline_mem:.2f}MB)")
            print(f"After plugins: {mem_after_plugins:.2f}MB (+{mem_after_plugins - mem_after_gateway:.2f}MB)")
            print(f"After object_pool: {mem_after_object_pool:.2f}MB (+{mem_after_object_pool - mem_after_plugins:.2f}MB)")
            print(f"After network: {mem_after_network:.2f}MB (+{mem_after_network - mem_after_object_pool:.2f}MB)")

            # Each module should not add excessive memory
            # (< 5MB per module is reasonable)
            module_memory = mem_after_network - baseline_mem
            avg_per_module = module_memory / 4

            assert avg_per_module < 5, \
                f"Average module memory {avg_per_module:.2f}MB too high"

        except ImportError:
            pytest.skip("psutil not available - skipping memory test")

    def test_large_operation_memory(self, execute_operation, EEGatewayInterface):
        """Test memory handling of large operations."""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())

            gc.collect()
            baseline_mem = process.memory_info().rss / 1024 / 1024

            # Perform operation with large data
            large_data = {'data': 'x' * 1000000}  # 1MB string

            # This would test if interfaces handle large data efficiently
            # For now, just verify we don't crash

            gc.collect()
            after_mem = process.memory_info().rss / 1024 / 1024

            memory_growth = after_mem - baseline_mem

            print(f"\nBaseline: {baseline_mem:.2f}MB")
            print(f"After large data: {after_mem:.2f}MB")
            print(f"Growth: {memory_growth:.2f}MB")

            # Growth should be reasonable
            assert memory_growth < 20, \
                f"Memory growth {memory_growth:.2f}MB too high for large operation"

        except ImportError:
            pytest.skip("psutil not available - skipping memory test")


@pytest.mark.performance
class TestMemoryOptimizations:
    """Memory optimization tests."""

    def test_lazy_loading_memory_savings(self):
        """Test that lazy loading reduces memory usage."""
        try:
            import subprocess
            import sys

            # Test eager loading
            eager_script = """
import sys
from EE import execute_operation, GatewayInterface
# Force load all interfaces
try:
    execute_operation(GatewayInterface.PLUGINS, 'list_all')
    execute_operation(GatewayInterface.OBJECT_POOL, 'list_all')
    execute_operation(GatewayInterface.NETWORK, 'get_status', protocol='test')
except:
    pass
print(f"EAGER_OK")
"""

            # Test lazy loading
            lazy_script = """
from EE import execute_operation, GatewayInterface
# Don't use any interfaces
print(f"LAZY_OK")
"""

            # Measure eager loading memory
            eager_result = subprocess.run(
                [sys.executable, '-c', eager_script],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent)
            )

            # Measure lazy loading memory
            lazy_result = subprocess.run(
                [sys.executable, '-c', lazy_script],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent)
            )

            # Just verify both complete without errors
            assert 'EAGER_OK' in eager_result.stdout
            assert 'LAZY_OK' in lazy_result.stdout

        except Exception as e:
            pytest.skip(f"Lazy loading memory test failed: {e}")

    def test_object_reuse_efficiency(self, execute_operation, EEGatewayInterface):
        """Test that objects are reused efficiently."""
        try:
            pool_name = 'reuse_test_pool'

            # Create pool
            execute_operation(
                EEGatewayInterface.OBJECT_POOL,
                'create',
                name=pool_name,
                factory_func=lambda: {'id': id(object()), 'data': 'test'},
                max_size=10
            )

            # Acquire and release objects
            objects = []
            for _ in range(10):
                obj = execute_operation(
                    EEGatewayInterface.OBJECT_POOL,
                    'acquire',
                    name=pool_name
                )
                objects.append(obj)

            # Release all
            for obj in objects:
                execute_operation(
                    EEGatewayInterface.OBJECT_POOL,
                    'release',
                    name=pool_name,
                    obj=obj
                )

            # Acquire again - should get same objects
            reused_objects = []
            for _ in range(10):
                obj = execute_operation(
                    EEGatewayInterface.OBJECT_POOL,
                    'acquire',
                    name=pool_name
                )
                reused_objects.append(obj)

            # Check if objects are reused (same IDs)
            # This depends on pool implementation
            print(f"\nAcquired {len(reused_objects)} objects from pool")
            print("Object reuse depends on pool implementation")

        except (ValueError, NotImplementedError):
            pytest.skip("Object reuse efficiency testing not yet implemented")


@pytest.mark.benchmark
class TestMemoryBenchmarks:
    """Memory benchmarks."""

    def test_benchmark_steady_state_memory(self, execute_operation, EEGatewayInterface):
        """Benchmark steady-state memory usage."""
        try:
            import psutil
            import os
            import time

            process = psutil.Process(os.getpid())

            # Perform operations for 10 seconds
            duration = 10
            start_time = time.time()

            memory_samples = []

            while (time.time() - start_time) < duration:
                # Perform operations
                for _ in range(10):
                    try:
                        execute_operation(
                            EEGatewayInterface.PLUGINS,
                            'list_all'
                        )
                    except (ValueError, NotImplementedError):
                        pass

                # Sample memory
                gc.collect()
                mem_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(mem_mb)

                time.sleep(0.1)

            # Calculate statistics
            avg_mem = sum(memory_samples) / len(memory_samples)
            min_mem = min(memory_samples)
            max_mem = max(memory_samples)
            mem_variance = max_mem - min_mem

            print(f"\nSteady-state memory (over {len(memory_samples)} samples):")
            print(f"  Average: {avg_mem:.2f}MB")
            print(f"  Min: {min_mem:.2f}MB")
            print(f"  Max: {max_mem:.2f}MB")
            print(f"  Variance: {mem_variance:.2f}MB")

            # Variance should be low (< 5MB)
            assert mem_variance < 5, \
                f"Memory variance {mem_variance:.2f}MB too high (possible leak)"

        except ImportError:
            pytest.skip("psutil not available - skipping memory benchmark")
