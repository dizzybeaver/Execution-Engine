"""
Test Suite for Operations Domain - UG-ISP Compliance (Simple)

Tests all operations domain interfaces and factories.
"""

import sys
import os

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import factories directly
from operations.cache.cache_factory import CacheFactory
from operations.circuit_breaker.circuit_breaker_factory import CircuitBreakerFactory, CircuitState
from operations.fileio.fileio_factory import FileIOFactory
from operations.serialization.serialization_factory import SerializationFactory
from operations.template.template_factory import TemplateFactory
from operations.object_pool.object_pool_factory import ObjectPoolFactory, PoolConfig
from operations.threading_ops.threading_factory import ThreadingFactory

import tempfile
import time


def test_cache_factory():
    """Test Cache Factory."""
    print("=" * 60)
    print("Testing Cache Factory")
    print("=" * 60)

    factory = CacheFactory()

    # Test set and get
    factory.set("test_key", "test_value")
    value = factory.get("test_key")
    assert value == "test_value", f"Expected 'test_value', got {value}"
    print(f"Set and get: PASSED (value={value})")

    # Test exists
    exists = factory.exists("test_key")
    assert exists, "Key should exist"
    print(f"Exists check: PASSED")

    # Test stats
    stats = factory.stats()
    print(f"Stats: {stats}")
    assert stats['hits'] > 0, "Should have at least one hit"
    print(f"Stats: PASSED")

    # Test delete
    deleted = factory.delete("test_key")
    assert deleted, "Delete should succeed"
    print(f"Delete: PASSED")

    value = factory.get("test_key")
    assert value is None, "Key should be deleted"
    print(f"After delete get: PASSED")

    print("\nCache Factory: PASSED\n")


def test_circuit_breaker_factory():
    """Test Circuit Breaker Factory."""
    print("=" * 60)
    print("Testing Circuit Breaker Factory")
    print("=" * 60)

    factory = CircuitBreakerFactory()

    def failing_function():
        raise Exception("Simulated failure")

    def success_function():
        return "success"

    # Test successful execution
    result = factory.execute(
        name="test_cb",
        func=success_function,
        failure_threshold=3
    )
    assert result == "success", f"Expected 'success', got {result}"
    print(f"Successful execution: PASSED")

    # Test get_state
    state = factory.get_state(name="test_cb")
    print(f"Circuit state: {state}")
    assert state == "closed", f"Expected 'closed', got {state}"
    print(f"Get state: PASSED")

    # Test failures
    for i in range(3):
        try:
            factory.execute(
                name="test_cb_fail",
                func=failing_function,
                failure_threshold=3
            )
        except:
            pass

    state = factory.get_state(name="test_cb_fail")
    print(f"After failures state: {state}")
    assert state == "open", f"Expected 'open', got {state}"
    print(f"Circuit opened: PASSED")

    # Test reset
    reset = factory.reset(name="test_cb_fail")
    assert reset, "Reset should succeed"
    state = factory.get_state(name="test_cb_fail")
    assert state == "closed", f"Expected 'closed' after reset, got {state}"
    print(f"Reset: PASSED")

    print("\nCircuit Breaker Factory: PASSED\n")


def test_fileio_factory():
    """Test File I/O Factory."""
    print("=" * 60)
    print("Testing File I/O Factory")
    print("=" * 60)

    factory = FileIOFactory()

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        temp_path = f.name
        f.write("test content")

    try:
        # Test read
        content = factory.read(path=temp_path)
        assert content == "test content", f"Expected 'test content', got {content}"
        print(f"Read file: PASSED")

        # Test exists
        exists = factory.exists(path=temp_path)
        assert exists, "File should exist"
        print(f"Exists check: PASSED")

        # Test write
        new_path = temp_path + ".new"
        factory.write(path=new_path, content="new content")
        new_content = factory.read(path=new_path)
        assert new_content == "new content", f"Expected 'new content', got {new_content}"
        print(f"Write file: PASSED")

        # Test append
        factory.append(path=new_path, content="\nappended")
        appended = factory.read(path=new_path)
        assert "appended" in appended, "Append should succeed"
        print(f"Append file: PASSED")

        # Test delete
        factory.delete(path=new_path)
        exists = factory.exists(path=new_path)
        assert not exists, "File should be deleted"
        print(f"Delete file: PASSED")

    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print("\nFile I/O Factory: PASSED\n")


def test_serialization_factory():
    """Test Serialization Factory."""
    print("=" * 60)
    print("Testing Serialization Factory")
    print("=" * 60)

    factory = SerializationFactory()

    # Test JSON
    data = {"name": "Alice", "age": 30}
    json_str = factory.to_json(obj=data)
    assert json_str, "JSON serialization should succeed"
    print(f"To JSON: PASSED ({json_str})")

    parsed = factory.from_json(json_str=json_str)
    assert parsed == data, f"Expected {data}, got {parsed}"
    print(f"From JSON: PASSED")

    # Test Pickle
    pickle_bytes = factory.to_pickle(obj=data)
    assert pickle_bytes, "Pickle serialization should succeed"
    print(f"To Pickle: PASSED")

    unpickled = factory.from_pickle(pickle_bytes=pickle_bytes)
    assert unpickled == data, f"Expected {data}, got {unpickled}"
    print(f"From Pickle: PASSED")

    print("\nSerialization Factory: PASSED\n")


def test_template_factory():
    """Test Template Factory."""
    print("=" * 60)
    print("Testing Template Factory")
    print("=" * 60)

    factory = TemplateFactory()

    # Test render
    result = factory.render(
        template_str="Hello {{name}}!",
        context={"name": "World"}
    )
    assert result == "Hello World!", f"Expected 'Hello World!', got {result}"
    print(f"Render: PASSED ({result})")

    # Test compile and render_string
    factory.compile(
        name="greeting",
        template_str="Welcome {{user}}!"
    )
    result = factory.render_string(
        name="greeting",
        context={"user": "Alice"}
    )
    assert result == "Welcome Alice!", f"Expected 'Welcome Alice!', got {result}"
    print(f"Compile and render_string: PASSED ({result})")

    print("\nTemplate Factory: PASSED\n")


def test_object_pool_factory():
    """Test Object Pool Factory."""
    print("=" * 60)
    print("Testing Object Pool Factory")
    print("=" * 60)

    factory = ObjectPoolFactory.get_instance()

    # Create a simple factory function
    def create_item():
        return {"id": id(time.time())}

    # Test create_pool
    created = factory.create_pool(
        name="test_pool",
        factory_func=create_item,
        max_size=5,
        initial_size=2
    )
    assert created, "Pool creation should succeed"
    print(f"Create pool: PASSED")

    # Test acquire
    item = factory.acquire(name="test_pool")
    assert item is not None, "Should acquire an item"
    print(f"Acquire: PASSED (item={item})")

    # Test release
    released = factory.release(name="test_pool", obj=item)
    assert released, "Release should succeed"
    print(f"Release: PASSED")

    # Test stats
    stats = factory.get_stats(name="test_pool")
    print(f"Stats: {stats}")
    assert stats is not None, "Should get stats"
    assert stats['current_size'] > 0, "Pool should have items"
    print(f"Get stats: PASSED")

    # Test list_pools
    pools = factory.list_pools()
    assert "test_pool" in pools, "Pool should be in list"
    print(f"List pools: PASSED ({pools})")

    # Test resize_pool
    resized = factory.resize_pool(name="test_pool", new_size=10)
    assert resized, "Resize should succeed"
    print(f"Resize pool: PASSED")

    # Test warm_pool
    warmed = factory.warm_pool(name="test_pool", count=2)
    print(f"Warm pool: PASSED (created {warmed} items)")

    # Test clear_pool
    cleared = factory.clear_pool(name="test_pool")
    assert cleared, "Clear should succeed"
    print(f"Clear pool: PASSED")

    print("\nObject Pool Factory: PASSED\n")


def test_threading_factory():
    """Test Threading Factory."""
    print("=" * 60)
    print("Testing Threading Factory")
    print("=" * 60)

    factory = ThreadingFactory.get_instance()

    # Test submit
    def simple_task(x):
        return x * 2

    future = factory.submit(
        simple_task, 5
    )
    assert future is not None, "Should submit task"
    result = future.result(timeout=5)
    assert result == 10, f"Expected 10, got {result}"
    print(f"Submit: PASSED (result={result})")

    # Test map
    numbers = [1, 2, 3, 4, 5]
    results = factory.map(
        func=simple_task,
        iterable=numbers
    )
    # Sort results since they may come back in any order
    results_sorted = sorted(results)
    expected = [2, 4, 6, 8, 10]
    assert results_sorted == expected, f"Expected {expected}, got {results_sorted}"
    print(f"Map: PASSED (results={results_sorted})")

    # Test stats
    stats = factory.get_stats()
    print(f"Stats: {stats}")
    assert stats is not None, "Should get stats"
    assert stats['submitted'] > 0, "Should have submitted tasks"
    print(f"Get stats: PASSED")

    print("\nThreading Factory: PASSED\n")


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("*" * 60)
    print("* Operations Domain Test Suite (Simple)")
    print("*" * 60)
    print("\n")

    try:
        test_cache_factory()
        test_circuit_breaker_factory()
        test_fileio_factory()
        test_serialization_factory()
        test_template_factory()
        test_object_pool_factory()
        test_threading_factory()

        print("\n")
        print("*" * 60)
        print("* ALL TESTS PASSED")
        print("*" * 60)
        print("\n")

        return True

    except AssertionError as e:
        print(f"\n!!! TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n!!! ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
