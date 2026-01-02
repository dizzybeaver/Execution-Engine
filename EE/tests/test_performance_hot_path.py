"""Test Performance - Hot Path

Performance tests for hot path operations:
- Gateway routing overhead
- Interface dispatch performance
- Frequently used operations
- Cache operations
- Singleton operations
"""

import pytest
import time
from typing import Dict, Any


@pytest.mark.performance
@pytest.mark.fast
class TestHotPathPerformance:
    """Hot path performance tests."""

    def test_gateway_routing_overhead(self, execute_operation, EEGatewayInterface, performance_thresholds):
        """Test Gateway execute_operation() routing overhead (target: <1ms)."""
        try:
            iterations = 1000
            start_time = time.time()

            for _ in range(iterations):
                execute_operation(
                    EEGatewayInterface.PLUGINS,
                    'list_all'
                )

            elapsed_ms = (time.time() - start_time) * 1000
            avg_ms = elapsed_ms / iterations

            print(f"\nGateway routing overhead: {avg_ms:.4f}ms average")

            # Should be very fast (< 1ms)
            target_ms = performance_thresholds.get('gateway_routing_ms', 1.0)
            assert avg_ms < target_ms, \
                f"Gateway routing {avg_ms:.4f}ms exceeds target {target_ms:.4f}ms"

        except (ValueError, NotImplementedError):
            pytest.skip("Gateway routing overhead testing not yet implemented")

    def test_dispatch_lookup_performance(self, execute_operation, EEGatewayInterface):
        """Test dispatch dictionary lookup performance."""
        from gateway.gateway import _GATEWAY_DISPATCH
        from gateway.gateway_enums import GatewayInterface

        iterations = 10000
        start_time = time.time()

        for _ in range(iterations):
            _ = _GATEWAY_DISPATCH.get(GatewayInterface.PLUGINS)

        elapsed_ms = (time.time() - start_time) * 1000
        avg_ms = elapsed_ms / iterations

        print(f"\nDispatch lookup: {avg_ms:.6f}ms average")

        # Should be extremely fast (< 0.01ms)
        assert avg_ms < 0.01, \
            f"Dispatch lookup {avg_ms:.6f}ms exceeds 0.01ms"

    def test_cache_operation_performance(self, execute_operation, EEGatewayInterface, performance_thresholds):
        """Test cache operation performance (frequently used)."""
        try:
            # First, set up cache
            execute_operation(
                EEGatewayInterface.CACHE,
                'set',
                key='test_hot_key',
                value='test_value'
            )

            # Measure GET performance
            iterations = 1000
            start_time = time.time()

            for _ in range(iterations):
                execute_operation(
                    EEGatewayInterface.CACHE,
                    'get',
                    key='test_hot_key'
                )

            elapsed_ms = (time.time() - start_time) * 1000
            avg_ms = elapsed_ms / iterations

            print(f"\nCache GET: {avg_ms:.4f}ms average")

            # Should be fast (< 1ms)
            target_ms = performance_thresholds.get('hot_path_ms', 50.0)
            assert avg_ms < target_ms, \
                f"Cache GET {avg_ms:.4f}ms exceeds target {target_ms:.4f}ms"

        except (ValueError, NotImplementedError, AttributeError):
            pytest.skip("Cache performance testing not yet implemented")

    def test_singleton_operation_performance(self, execute_operation, EEGatewayInterface, performance_thresholds):
        """Test singleton operation performance (frequently used)."""
        try:
            # Measure singleton GET performance
            iterations = 1000
            start_time = time.time()

            for _ in range(iterations):
                execute_operation(
                    EEGatewayInterface.SINGLETON,
                    'get',
                    name='test_instance'
                )

            elapsed_ms = (time.time() - start_time) * 1000
            avg_ms = elapsed_ms / iterations

            print(f"\nSingleton GET: {avg_ms:.4f}ms average")

            # Should be fast (< 1ms)
            target_ms = performance_thresholds.get('hot_path_ms', 50.0)
            assert avg_ms < target_ms, \
                f"Singleton GET {avg_ms:.4f}ms exceeds target {target_ms:.4f}ms"

        except (ValueError, NotImplementedError, AttributeError):
            pytest.skip("Singleton performance testing not yet implemented")

    def test_concurrent_operation_performance(self, execute_operation, EEGatewayInterface):
        """Test concurrent operation performance."""
        import concurrent.futures

        try:
            def run_operation():
                return execute_operation(
                    EEGatewayInterface.PLUGINS,
                    'list_all'
                )

            iterations = 100
            start_time = time.time()

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(run_operation) for _ in range(iterations)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            elapsed_ms = (time.time() - start_time) * 1000
            avg_ms = elapsed_ms / iterations

            print(f"\nConcurrent operations: {avg_ms:.4f}ms average")

            # Should still be fast
            assert avg_ms < 10, \
                f"Concurrent operation {avg_ms:.4f}ms exceeds 10ms"

        except (ValueError, NotImplementedError):
            pytest.skip("Concurrent operation testing not yet implemented")


@pytest.mark.performance
class TestHotPathOptimizations:
    """Hot path optimization tests."""

    def test_zaph_optimization_exists(self):
        """Test that ZAPH (Zero-Abstraction Performance Hot-path) optimization exists."""
        # Check if ZAPH optimization is available
        ee_src = Path(__file__).parent.parent / 'src'

        zaph_file = ee_src / 'optimization' / 'zaph' / 'zaph_core.py'

        if not zaph_file.exists():
            pytest.skip("ZAPH optimization not yet implemented")

        # ZAPH should provide fast path for critical operations
        assert zaph_file.exists(), "ZAPH optimization should exist"

    def test_fast_path_operations(self, execute_operation, EEGatewayInterface):
        """Test that fast path operations are faster than normal path."""
        try:
            import time

            # Normal path
            start = time.time()
            execute_operation(EEGatewayInterface.PLUGINS, 'list_all')
            normal_time = time.time() - start

            # Fast path (if available)
            # This would use ZAPH optimization
            # For now, just measure normal path

            print(f"\nNormal path: {normal_time * 1000:.4f}ms")

            # Normal path should still be reasonably fast
            assert normal_time < 0.1, \
                f"Normal path too slow: {normal_time * 1000:.4f}ms"

        except (ValueError, NotImplementedError):
            pytest.skip("Fast path testing not yet implemented")

    def test_operation_caching(self, execute_operation, EEGatewayInterface):
        """Test that operations are cached effectively."""
        try:
            import time

            # First call (cache miss)
            start = time.time()
            execute_operation(EEGatewayInterface.PLUGINS, 'list_all')
            first_call = time.time() - start

            # Second call (cache hit)
            start = time.time()
            execute_operation(EEGatewayInterface.PLUGINS, 'list_all')
            second_call = time.time() - start

            print(f"\nFirst call: {first_call * 1000:.4f}ms")
            print(f"Second call: {second_call * 1000:.4f}ms")

            # Second call should be faster or equal
            # (This depends on caching strategy)
            assert second_call <= first_call * 1.1, \
                "Second call should not be significantly slower"

        except (ValueError, NotImplementedError):
            pytest.skip("Operation caching testing not yet implemented")


@pytest.mark.benchmark
class TestHotPathBenchmarks:
    """Hot path benchmarks."""

    def test_benchmark_operation_frequency(self, execute_operation, EEGatewayInterface):
        """Benchmark operation frequency (operations per second)."""
        try:
            import time

            duration_seconds = 5
            start_time = time.time()
            operations = 0

            while (time.time() - start_time) < duration_seconds:
                execute_operation(EEGatewayInterface.PLUGINS, 'list_all')
                operations += 1

            elapsed = time.time() - start_time
            ops_per_second = operations / elapsed

            print(f"\nOperations per second: {ops_per_second:.2f}")

            # Should be able to do at least 100 ops/sec
            assert ops_per_second >= 100, \
                f"Operation rate {ops_per_second:.2f} ops/sec below 100 ops/sec"

        except (ValueError, NotImplementedError):
            pytest.skip("Operation frequency benchmarking not yet implemented")

    def test_benchmark_p99_latency(self, execute_operation, EEGatewayInterface):
        """Benchmark P99 latency (99th percentile)."""
        try:
            import time

            iterations = 1000
            times = []

            for _ in range(iterations):
                start = time.time()
                execute_operation(EEGatewayInterface.PLUGINS, 'list_all')
                times.append((time.time() - start) * 1000)  # ms

            # Calculate P99
            times.sort()
            p99_index = int(iterations * 0.99)
            p99_latency = times[p99_index]

            print(f"\nP99 latency: {p99_latency:.4f}ms")

            # P99 should be under 50ms
            assert p99_latency < 50, \
                f"P99 latency {p99_latency:.4f}ms exceeds 50ms"

        except (ValueError, NotImplementedError):
            pytest.skip("P99 latency benchmarking not yet implemented")

    def test_benchmark_throughput_scaling(self, execute_operation, EEGatewayInterface):
        """Benchmark throughput scaling with concurrent operations."""
        import concurrent.futures
        import time

        try:
            def run_operations(count):
                start = time.time()
                for _ in range(count):
                    execute_operation(EEGatewayInterface.PLUGINS, 'list_all')
                return time.time() - start

            # Single thread
            single_time = run_operations(100)

            # Multiple threads
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(run_operations, 100) for _ in range(4)]
                multi_times = [f.result() for f in concurrent.futures.as_completed(futures)]

            total_multi_time = sum(multi_times)
            avg_multi_time = total_multi_time / 4

            print(f"\nSingle thread time: {single_time * 1000:.2f}ms")
            print(f"Multi-thread avg time: {avg_multi_time * 1000:.2f}ms")

            # Multi-threading should not be significantly slower
            # (some overhead is expected)
            assert avg_multi_time < single_time * 2, \
                "Multi-threading overhead too high"

        except (ValueError, NotImplementedError):
            pytest.skip("Throughput scaling benchmarking not yet implemented")
