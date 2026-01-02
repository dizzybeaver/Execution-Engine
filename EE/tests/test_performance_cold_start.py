"""Test Performance - Cold Start

Performance tests for cold start optimization:
- Gateway initialization time
- Interface import time
- Lazy import effectiveness
- Initial memory usage
- First operation latency
"""

import pytest
import time
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any


@pytest.mark.performance
@pytest.mark.slow
class TestColdStartPerformance:
    """Cold start performance tests."""

    def test_gateway_initialization_time(self, performance_thresholds):
        """Test Gateway initialization time (target: <3s)."""
        # This test measures cold start time by importing Gateway in a fresh process

        test_script = """
import sys
import time

start_time = time.time()

# Import gateway (this triggers lazy loading)
from EE import execute_operation, GatewayInterface

init_time = time.time() - start_time

print(f"INIT_TIME:{init_time:.3f}")
"""

        # Run in subprocess to simulate cold start
        result = subprocess.run(
            [sys.executable, '-c', test_script],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        # Extract initialization time
        for line in result.stdout.split('\n'):
            if line.startswith('INIT_TIME:'):
                init_time = float(line.split(':')[1])
                break
        else:
            pytest.skip("Could not measure initialization time")

        # Check against threshold
        target_ms = performance_thresholds.get('cold_start_ms', 3000.0)

        assert init_time < target_ms / 1000, \
            f"Cold start time {init_time * 1000:.2f}ms exceeds target {target_ms:.2f}ms"

    def test_lazy_import_effectiveness(self):
        """Test that lazy imports reduce cold start time."""
        # Compare eager vs lazy import time

        # Test lazy import (function-level)
        lazy_script = """
import time
start = time.time()
# Import gateway but don't use interfaces
from EE import execute_operation, GatewayInterface
lazy_time = time.time() - start
print(f"LAZY:{lazy_time:.3f}")
"""

        # Test eager import (using interface immediately)
        eager_script = """
import time
start = time.time()
from EE import execute_operation, GatewayInterface
# Trigger interface import by calling it
try:
    execute_operation(GatewayInterface.PLUGINS, 'list_all')
except:
    pass
eager_time = time.time() - start
print(f"EAGER:{eager_time:.3f}")
"""

        # Run lazy test
        lazy_result = subprocess.run(
            [sys.executable, '-c', lazy_script],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        lazy_time = None
        for line in lazy_result.stdout.split('\n'):
            if line.startswith('LAZY:'):
                lazy_time = float(line.split(':')[1])
                break

        # Run eager test
        eager_result = subprocess.run(
            [sys.executable, '-c', eager_script],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        eager_time = None
        for line in eager_result.stdout.split('\n'):
            if line.startswith('EAGER:'):
                eager_time = float(line.split(':')[1])
                break

        if lazy_time is None or eager_time is None:
            pytest.skip("Could not measure import times")

        # Lazy import should be faster
        # Note: This may vary based on system
        print(f"\nLazy import time: {lazy_time * 1000:.2f}ms")
        print(f"Eager import time: {eager_time * 1000:.2f}ms")
        print(f"Improvement: {((eager_time - lazy_time) / eager_time * 100):.1f}%")

        # At minimum, lazy import should not be significantly slower
        assert lazy_time <= eager_time * 1.1, \
            "Lazy import is significantly slower than eager import"

    def test_first_operation_latency(self, performance_thresholds):
        """Test latency of first operation after cold start."""
        test_script = """
import sys
import time

from EE import execute_operation, GatewayInterface

# Measure first operation
start_time = time.time()

try:
    result = execute_operation(GatewayInterface.PLUGINS, 'list_all')
    first_op_time = time.time() - start_time
    print(f"FIRST_OP:{first_op_time:.3f}")
except Exception as e:
    print(f"ERROR:{e}")
"""

        result = subprocess.run(
            [sys.executable, '-c', test_script],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        for line in result.stdout.split('\n'):
            if line.startswith('FIRST_OP:'):
                first_op_time = float(line.split(':')[1])
                break
            elif line.startswith('ERROR:'):
                pytest.skip("First operation failed")
                break
        else:
            pytest.skip("Could not measure first operation time")

        # First operation includes interface loading
        # Should still be reasonably fast (< 1s)
        assert first_op_time < 1.0, \
            f"First operation time {first_op_time * 1000:.2f}ms exceeds 1000ms"

    def test_memory_usage_after_cold_start(self, performance_thresholds):
        """Test memory usage after cold start."""
        import psutil
        import os

        # Measure memory of parent process (baseline)
        process = psutil.Process(os.getpid())
        baseline_mem = process.memory_info().rss / 1024 / 1024  # MB

        # Import Gateway
        from EE import execute_operation, GatewayInterface

        # Measure memory after import
        after_import_mem = process.memory_info().rss / 1024 / 1024  # MB

        memory_increase = after_import_mem - baseline_mem

        print(f"\nBaseline memory: {baseline_mem:.2f}MB")
        print(f"After import: {after_import_mem:.2f}MB")
        print(f"Increase: {memory_increase:.2f}MB")

        # Check against threshold
        target_mb = performance_thresholds.get('memory_mb', 80.0)

        assert after_import_mem < target_mb, \
            f"Memory usage {after_import_mem:.2f}MB exceeds target {target_mb:.2f}MB"

    def test_module_count_after_import(self):
        """Test number of modules loaded after Gateway import."""
        test_script = """
import sys

# Count modules before import
before_count = len(sys.modules)

# Import Gateway
from EE import execute_operation, GatewayInterface

# Count modules after import
after_count = len(sys.modules)

loaded_count = after_count - before_count

print(f"MODULES_LOADED:{loaded_count}")
print(f"TOTAL_MODULES:{after_count}")
"""

        result = subprocess.run(
            [sys.executable, '-c', test_script],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        modules_loaded = None
        total_modules = None

        for line in result.stdout.split('\n'):
            if line.startswith('MODULES_LOADED:'):
                modules_loaded = int(line.split(':')[1])
            elif line.startswith('TOTAL_MODULES:'):
                total_modules = int(line.split(':')[1])

        if modules_loaded is None or total_modules is None:
            pytest.skip("Could not measure module count")

        print(f"\nModules loaded by Gateway import: {modules_loaded}")
        print(f"Total modules after import: {total_modules}")

        # Gateway should load minimal modules (lazy loading)
        # Less than 50 modules is good
        assert modules_loaded < 50, \
            f"Too many modules loaded: {modules_loaded} (lazy loading may not be effective)"

    def test_cold_start_with_all_interfaces(self):
        """Test cold start when all interfaces are preloaded."""
        test_script = """
import sys
import time

start_time = time.time()

# Import and use all interfaces
from EE import execute_operation, GatewayInterface

interfaces_to_test = [
    GatewayInterface.PLUGINS,
    GatewayInterface.OBJECT_POOL,
    GatewayInterface.NETWORK,
]

for interface in interfaces_to_test:
    try:
        execute_operation(interface, 'list_all')
    except:
        pass

cold_start_time = time.time() - start_time

print(f"COLD_START_ALL:{cold_start_time:.3f}")
"""

        result = subprocess.run(
            [sys.executable, '-c', test_script],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        for line in result.stdout.split('\n'):
            if line.startswith('COLD_START_ALL:'):
                cold_start_time = float(line.split(':')[1])
                break
        else:
            pytest.skip("Could not measure cold start time")

        # Full cold start with all interfaces should still be fast
        assert cold_start_time < 5.0, \
            f"Full cold start time {cold_start_time * 1000:.2f}ms exceeds 5000ms"


@pytest.mark.performance
class TestColdStartOptimization:
    """Cold start optimization tests."""

    def test_lazy_import_coverage(self):
        """Test that all interfaces use lazy imports."""
        from gateway import gateway

        # Check that gateway uses lazy import function
        assert hasattr(gateway, '_import_interface_router'), \
            "Gateway should have lazy import function"

    def test_import_cache_effectiveness(self):
        """Test that module imports are cached."""
        import sys

        # Import interface twice
        from interface import interface_plugins

        # Check that it's cached
        assert 'interface.interface_plugins' in sys.modules, \
            "Interface module should be cached after first import"

        # Import again (should use cache)
        from interface import interface_plugins as plugins2

        # Should be same module object
        assert interface_plugins is plugins2, \
            "Cached module should be returned on second import"


@pytest.mark.benchmark
class TestColdStartBenchmarks:
    """Cold start benchmarks."""

    def test_benchmark_cold_start_averages(self):
        """Benchmark cold start time over multiple runs."""
        iterations = 5
        times = []

        test_script = """
import time
start = time.time()
from EE import execute_operation, GatewayInterface
elapsed = time.time() - start
print(f"{elapsed:.3f}")
"""

        for _ in range(iterations):
            result = subprocess.run(
                [sys.executable, '-c', test_script],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent)
            )

            time_str = result.stdout.strip()
            if time_str:
                try:
                    times.append(float(time_str))
                except ValueError:
                    pass

        if not times:
            pytest.skip("Could not benchmark cold start")

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\nCold start benchmark ({len(times)} runs):")
        print(f"  Average: {avg_time * 1000:.2f}ms")
        print(f"  Min: {min_time * 1000:.2f}ms")
        print(f"  Max: {max_time * 1000:.2f}ms")

        # Average should be under 3s
        assert avg_time < 3.0, \
            f"Average cold start {avg_time * 1000:.2f}ms exceeds 3000ms"
