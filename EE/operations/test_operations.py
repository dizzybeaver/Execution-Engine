"""
Test Suite for Operations Domain - UG-ISP Compliance

Tests all operations domain interfaces and factories.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from operations import OperationsGateway
from operations.cache import CacheFactory, execute_cache_operation
from operations.circuit_breaker import CircuitBreakerFactory, CircuitState, execute_circuit_breaker_operation
from operations.fileio import FileIOFactory, execute_fileio_operation
from operations.serialization import SerializationFactory, execute_serialization_operation
from operations.template import TemplateFactory, execute_template_operation
from operations.object_pool import ObjectPoolFactory, PoolConfig, execute_object_pool_operation
from operations.threading import ThreadingFactory, execute_threading_operation

import tempfile
import time


def test_operations_gateway():
    """Test Operations Gateway."""
    print("=" * 60)
    print("Testing Operations Gateway")
    print("=" * 60)

    gateway = OperationsGateway()

    # Test list_all
    all_ops = gateway.list_all()
    print(f"Domain: {all_ops['domain']}")
    print(f"Interfaces: {list(all_ops['interfaces'].keys())}")

    # Verify all interfaces are present
    assert all_ops['domain'] == 'operations'
    expected_interfaces = [
        'cache', 'circuit_breaker', 'fileio', 'serialization',
        'template', 'object_pool', 'threading'
    ]
    for iface in expected_interfaces:
        assert iface in all_ops['interfaces']
        print(f"  - {iface}: {all_ops['interfaces'][iface]['description']}")
        print(f"    Operations: {[op['operation'] for op in all_ops['interfaces'][iface]['operations']]}")

    print("\nOperations Gateway: PASSED\n")


def test_cache_interface():
    """Test Cache Interface."""
    print("=" * 60)
    print("Testing Cache Interface")
    print("=" * 60)

    # Test via interface
    execute_cache_operation("set", key="test_key", value="test_value")
    value = execute_cache_operation("get", key="test_key")
    assert value == "test_value", f"Expected 'test_value', got {value}"
    print(f"Set and get: PASSED (value={value})")

    # Test exists
    exists = execute_cache_operation("exists", key="test_key")
    assert exists, "Key should exist"
    print(f"Exists check: PASSED")

    # Test stats
    stats = execute_cache_operation("stats")
    print(f"Stats: {stats}")
    assert stats['hits'] > 0, "Should have at least one hit"
    print(f"Stats: PASSED")

    # Test delete
    deleted = execute_cache_operation("delete", key="test_key")
    assert deleted, "Delete should succeed"
    print(f"Delete: PASSED")

    value = execute_cache_operation("get", key="test_key")
    assert value is None, "Key should be deleted"
    print(f"After delete get: PASSED")

    print("\nCache Interface: PASSED\n")


def test_circuit_breaker_interface():
    """Test Circuit Breaker Interface."""
    print("=" * 60)
    print("Testing Circuit Breaker Interface")
    print("=" * 60)

    def failing_function():
        raise Exception("Simulated failure")

    def success_function():
        return "success"

    # Test successful execution
    result = execute_circuit_breaker_operation(
        "execute",
        name="test_cb",
        func=success_function,
        failure_threshold=3
    )
    assert result == "success", f"Expected 'success', got {result}"
    print(f"Successful execution: PASSED")

    # Test get_state
    state = execute_circuit_breaker_operation("get_state", name="test_cb")
    print(f"Circuit state: {state}")
    assert state == "closed", f"Expected 'closed', got {state}"
    print(f"Get state: PASSED")

    # Test failures
    for i in range(3):
        try:
            execute_circuit_breaker_operation(
                "execute",
                name="test_cb_fail",
                func=failing_function,
                failure_threshold=3
            )
        except:
            pass

    state = execute_circuit_breaker_operation("get_state", name="test_cb_fail")
    print(f"After failures state: {state}")
    assert state == "open", f"Expected 'open', got {state}"
    print(f"Circuit opened: PASSED")

    # Test reset
    reset = execute_circuit_breaker_operation("reset", name="test_cb_fail")
    assert reset, "Reset should succeed"
    state = execute_circuit_breaker_operation("get_state", name="test_cb_fail")
    assert state == "closed", f"Expected 'closed' after reset, got {state}"
    print(f"Reset: PASSED")

    print("\nCircuit Breaker Interface: PASSED\n")


def test_fileio_interface():
    """Test File I/O Interface."""
    print("=" * 60)
    print("Testing File I/O Interface")
    print("=" * 60)

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        temp_path = f.name
        f.write("test content")

    try:
        # Test read
        content = execute_fileio_operation("read", path=temp_path)
        assert content == "test content", f"Expected 'test content', got {content}"
        print(f"Read file: PASSED")

        # Test exists
        exists = execute_fileio_operation("exists", path=temp_path)
        assert exists, "File should exist"
        print(f"Exists check: PASSED")

        # Test write
        new_path = temp_path + ".new"
        execute_fileio_operation("write", path=new_path, content="new content")
        new_content = execute_fileio_operation("read", path=new_path)
        assert new_content == "new content", f"Expected 'new content', got {new_content}"
        print(f"Write file: PASSED")

        # Test append
        execute_fileio_operation("append", path=new_path, content="\nappended")
        appended = execute_fileio_operation("read", path=new_path)
        assert "appended" in appended, "Append should succeed"
        print(f"Append file: PASSED")

        # Test delete
        execute_fileio_operation("delete", path=new_path)
        exists = execute_fileio_operation("exists", path=new_path)
        assert not exists, "File should be deleted"
        print(f"Delete file: PASSED")

    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

    print("\nFile I/O Interface: PASSED\n")


def test_serialization_interface():
    """Test Serialization Interface."""
    print("=" * 60)
    print("Testing Serialization Interface")
    print("=" * 60)

    # Test JSON
    data = {"name": "Alice", "age": 30}
    json_str = execute_serialization_operation("to_json", obj=data)
    assert json_str, "JSON serialization should succeed"
    print(f"To JSON: PASSED ({json_str})")

    parsed = execute_serialization_operation("from_json", json_str=json_str)
    assert parsed == data, f"Expected {data}, got {parsed}"
    print(f"From JSON: PASSED")

    # Test Pickle
    pickle_bytes = execute_serialization_operation("to_pickle", obj=data)
    assert pickle_bytes, "Pickle serialization should succeed"
    print(f"To Pickle: PASSED")

    unpickled = execute_serialization_operation("from_pickle", pickle_bytes=pickle_bytes)
    assert unpickled == data, f"Expected {data}, got {unpickled}"
    print(f"From Pickle: PASSED")

    print("\nSerialization Interface: PASSED\n")


def test_template_interface():
    """Test Template Interface."""
    print("=" * 60)
    print("Testing Template Interface")
    print("=" * 60)

    # Test render
    result = execute_template_operation(
        "render",
        template_str="Hello {{name}}!",
        context={"name": "World"}
    )
    assert result == "Hello World!", f"Expected 'Hello World!', got {result}"
    print(f"Render: PASSED ({result})")

    # Test compile and render_string
    execute_template_operation(
        "compile",
        name="greeting",
        template_str="Welcome {{user}}!"
    )
    result = execute_template_operation(
        "render_string",
        name="greeting",
        context={"user": "Alice"}
    )
    assert result == "Welcome Alice!", f"Expected 'Welcome Alice!', got {result}"
    print(f"Compile and render_string: PASSED ({result})")

    print("\nTemplate Interface: PASSED\n")


def test_object_pool_interface():
    """Test Object Pool Interface."""
    print("=" * 60)
    print("Testing Object Pool Interface")
    print("=" * 60)

    # Create a simple factory function
    def create_item():
        return {"id": id(time.time())}

    # Test create_pool
    created = execute_object_pool_operation(
        "create_pool",
        name="test_pool",
        factory_func=create_item,
        max_size=5,
        initial_size=2
    )
    assert created, "Pool creation should succeed"
    print(f"Create pool: PASSED")

    # Test acquire
    item = execute_object_pool_operation("acquire", name="test_pool")
    assert item is not None, "Should acquire an item"
    print(f"Acquire: PASSED (item={item})")

    # Test release
    released = execute_object_pool_operation("release", name="test_pool", obj=item)
    assert released, "Release should succeed"
    print(f"Release: PASSED")

    # Test stats
    stats = execute_object_pool_operation("get_stats", name="test_pool")
    print(f"Stats: {stats}")
    assert stats is not None, "Should get stats"
    assert stats['current_size'] > 0, "Pool should have items"
    print(f"Get stats: PASSED")

    # Test list_pools
    pools = execute_object_pool_operation("list_pools")
    assert "test_pool" in pools, "Pool should be in list"
    print(f"List pools: PASSED ({pools})")

    # Test resize_pool
    resized = execute_object_pool_operation("resize_pool", name="test_pool", new_size=10)
    assert resized, "Resize should succeed"
    print(f"Resize pool: PASSED")

    # Test warm_pool
    warmed = execute_object_pool_operation("warm_pool", name="test_pool", count=2)
    print(f"Warm pool: PASSED (created {warmed} items)")

    # Test clear_pool
    cleared = execute_object_pool_operation("clear_pool", name="test_pool")
    assert cleared, "Clear should succeed"
    print(f"Clear pool: PASSED")

    print("\nObject Pool Interface: PASSED\n")


def test_threading_interface():
    """Test Threading Interface."""
    print("=" * 60)
    print("Testing Threading Interface")
    print("=" * 60)

    # Test submit
    def simple_task(x):
        return x * 2

    future = execute_threading_operation(
        "submit",
        func=simple_task,
        args=(5,)
    )
    assert future is not None, "Should submit task"
    result = future.result(timeout=5)
    assert result == 10, f"Expected 10, got {result}"
    print(f"Submit: PASSED (result={result})")

    # Test map
    numbers = [1, 2, 3, 4, 5]
    results = execute_threading_operation(
        "map",
        func=simple_task,
        iterable=numbers
    )
    expected = [2, 4, 6, 8, 10]
    assert results == expected, f"Expected {expected}, got {results}"
    print(f"Map: PASSED (results={results})")

    # Test stats
    stats = execute_threading_operation("get_stats")
    print(f"Stats: {stats}")
    assert stats is not None, "Should get stats"
    assert stats['submitted'] > 0, "Should have submitted tasks"
    print(f"Get stats: PASSED")

    print("\nThreading Interface: PASSED\n")


def run_all_tests():
    """Run all tests."""
    print("\n")
    print("*" * 60)
    print("* Operations Domain Test Suite")
    print("*" * 60)
    print("\n")

    try:
        test_operations_gateway()
        test_cache_interface()
        test_circuit_breaker_interface()
        test_fileio_interface()
        test_serialization_interface()
        test_template_interface()
        test_object_pool_interface()
        test_threading_interface()

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
