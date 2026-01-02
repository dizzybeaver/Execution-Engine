"""EE Testing Framework - Pytest Configuration and Fixtures

Shared fixtures and configuration for all EE tests.
"""

import sys
import os
from pathlib import Path
import pytest
import tempfile
import shutil
from typing import Generator, Dict, Any

# Add EE src to path
ee_src = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(ee_src))


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def ee_src_path() -> Path:
    """EE source code path."""
    return ee_src


@pytest.fixture(scope="session")
def tests_path() -> Path:
    """Tests directory path."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def test_data_path() -> Path:
    """Test data directory path."""
    path = Path(__file__).parent / 'test_data'
    path.mkdir(exist_ok=True)
    return path


@pytest.fixture(scope="session")
def test_reports_path() -> Path:
    """Test reports directory path."""
    path = Path(__file__).parent / 'test_reports'
    path.mkdir(exist_ok=True)
    return path


# ============================================================================
# Gateway Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def gateway():
    """EE Gateway instance for testing."""
    from gateway import gateway
    return gateway


@pytest.fixture(scope="function")
def execute_operation():
    """execute_operation function from gateway."""
    from gateway.gateway import execute_operation
    return execute_operation


@pytest.fixture(scope="function")
def GatewayInterface():
    """GatewayInterface enum."""
    from gateway.gateway_enums import GatewayInterface
    return GatewayInterface


@pytest.fixture(scope="function")
def EEGatewayInterface():
    """EEGatewayInterface enum with categories."""
    from gateway.ee_gateway_enums import EEGatewayInterface
    return EEGatewayInterface


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """Temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def temp_config_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Temporary YAML config file."""
    config_file = temp_dir / "test_config.yaml"
    yield config_file
    if config_file.exists():
        config_file.unlink()


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def mock_gateway_stats() -> Dict[str, Any]:
    """Mock gateway statistics."""
    return {
        'total_operations': 1000,
        'successful_operations': 980,
        'failed_operations': 20,
        'cache_hit_rate': 0.85,
        'average_response_time_ms': 23.5,
    }


@pytest.fixture(scope="function")
def mock_plugin_config() -> Dict[str, Any]:
    """Mock plugin configuration."""
    return {
        'name': 'test_plugin',
        'enabled': True,
        'version': '1.0.0',
        'config': {
            'timeout': 30,
            'retries': 3,
        }
    }


@pytest.fixture(scope="function")
def mock_object_pool_config() -> Dict[str, Any]:
    """Mock object pool configuration."""
    return {
        'name': 'test_pool',
        'factory_func': lambda: {'connection': 'test'},
        'max_size': 10,
        'initial_size': 2,
    }


# ============================================================================
# Performance Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def performance_thresholds() -> Dict[str, float]:
    """Performance threshold targets (in milliseconds)."""
    return {
        'cold_start_ms': 3000.0,
        'hot_path_ms': 50.0,
        'memory_mb': 80.0,
        'gateway_routing_ms': 1.0,
        'plugin_load_ms': 500.0,
    }


# ============================================================================
# UG-ISP Compliance Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def ug_isp_rules() -> Dict[str, str]:
    """UG-ISP compliance rules."""
    return {
        'cross_interface': 'All cross-interface calls must use execute_operation()',
        'debug_routing': 'All debug operations must route through GatewayInterface.DEBUG',
        'no_helpers': 'No internal debug helper functions (bypasses Gateway)',
        'no_direct_imports': 'No direct imports across interfaces',
        'file_size': 'All files must be <= 350 lines',
        'isp_topology': 'Gateway = ISP, Interfaces = Routers, Implementation = Local Network',
    }


@pytest.fixture(scope="function")
def forbidden_patterns() -> Dict[str, list]:
    """Forbidden code patterns (UG-ISP violations)."""
    return {
        'CRITICAL': [
            r'def _debug_log\(',  # Internal debug helper
            r'def _debug_timing\(',  # Internal timing helper
            r'from interface\.\w+ import',  # Direct interface import
            r'from EE\.(gateway|interface)\.\w+ import \w+',  # Direct gateway import
        ],
        'HIGH': [
            r'import interface_\w+',  # Module-level interface import
            r'from cache\.\w+ import',  # Direct implementation import
            r'from logging\.\w+ import',  # Direct implementation import
        ],
        'MEDIUM': [
            r'# TODO: fix UG-ISP',  # Acknowledged violations
            r'# FIXME: architecture',  # Known issues
        ],
    }


# ============================================================================
# Plugin Test Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def sample_plugin():
    """Sample plugin for testing."""
    class TestPlugin:
        def __init__(self):
            self.name = "test_plugin"
            self.enabled = True
            self.initialized = False

        def initialize(self, config: Dict[str, Any]):
            self.config = config
            self.initialized = True
            return True

        def execute(self, operation: str, **kwargs):
            if not self.initialized:
                raise RuntimeError("Plugin not initialized")
            return f"Executed {operation}"

        def shutdown(self):
            self.initialized = False

    return TestPlugin()


# ============================================================================
# Network Test Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def mock_network_configs() -> Dict[str, Dict[str, Any]]:
    """Mock network protocol configurations."""
    return {
        'mqtt': {
            'host': 'localhost',
            'port': 1883,
            'keepalive': 60,
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
        },
        'ntp': {
            'host': 'pool.ntp.org',
            'port': 123,
            'version': 4,
        },
    }


# ============================================================================
# Markers
# ============================================================================

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance benchmarks")
    config.addinivalue_line("markers", "compliance: UG-ISP compliance tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "fast: Fast-running tests")


# ============================================================================
# Hooks
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add slow marker to performance tests
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.slow)

        # Add fast marker to unit tests
        elif "test_interface" in str(item.fspath) or "test_gateway" in str(item.fspath):
            item.add_marker(pytest.mark.fast)


# ============================================================================
# Skip Conditions
# ============================================================================

def pytest_collection_finish(session):
    """Print collection summary."""
    print(f"\n{'=' * 70}")
    print(f"Collected {len(session.items)} tests")
    print(f"{'=' * 70}\n")
