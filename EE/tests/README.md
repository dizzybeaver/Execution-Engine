# EE Testing Framework

**Comprehensive Testing Framework for EE (Execution Environment)**

Version: 1.0.0
Date: 2025-12-28

---

## Overview

The EE Testing Framework provides comprehensive testing capabilities for the EE execution environment, including unit tests, integration tests, performance benchmarks, and UG compliance verification.

---

## Features

### Test Categories

1. **Unit Tests** (`test_*.py`)
   - Interface tests (Plugins, Object Pool, Network)
   - Gateway tests (Factory, Routing)
   - DI Gateway tests
   - Individual component testing

2. **Integration Tests** (`test_integration_*.py`)
   - End-to-end workflows
   - Plugin system integration
   - Cross-interface operations
   - Real-world scenarios

3. **Performance Tests** (`test_performance_*.py`)
   - Cold start optimization
   - Hot path performance
   - Memory efficiency
   - Benchmarking

4. **Compliance Tests** (`test_ug_compliance.py`, `test_import_rules.py`)
   - UG architecture compliance
   - Import rule verification
   - Anti-pattern detection
   - File size validation

---

## Quick Start

### Installation

```bash
# Install dependencies
pip install pytest pytest-cov psutil

# Or use requirements.txt
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
python test_runner.py --all

# Run unit tests only
python test_runner.py --unit

# Run integration tests
python test_runner.py --integration

# Run performance benchmarks
python test_runner.py --benchmark

# Run UG compliance tests
python test_runner.py --compliance

# Run specific test file
python test_runner.py --test test_interface_plugins.py

# Generate coverage report
python test_runner.py --coverage

# Run tests in parallel
python test_runner.py --all --parallel
```

### Using pytest Directly

```bash
# Run all tests
pytest -v

# Run specific test file
pytest test_interface_plugins.py -v

# Run specific test
pytest test_interface_plugins.py::TestPluginsInterface::test_plugins_interface_exists -v

# Run with coverage
pytest --cov=../src --cov-report=html

# Run only fast tests
pytest -m fast

# Skip slow tests
pytest -m "not slow"
```

---

## Test Structure

```
tests/
├── conftest.py                      # Pytest fixtures and configuration
├── test_runner.py                   # Main test runner
├── test_config.yaml                 # Test configuration
├── README.md                        # This file
│
├── test_interface_plugins.py        # INT-16 PLUGINS interface tests
├── test_interface_object_pool.py    # INT-18 OBJECT_POOL interface tests
├── test_interface_network.py        # INT-17 NETWORK interface tests
├── test_gateway_factory.py          # Gateway Factory tests
├── test_gateway_routing.py          # Gateway Routing tests
├── test_di_gateway.py               # DI Gateway tests
│
├── test_integration_e2e.py          # End-to-end integration tests
├── test_integration_plugins.py      # Plugin integration tests
│
├── test_performance_cold_start.py   # Cold start performance tests
├── test_performance_hot_path.py     # Hot path performance tests
├── test_performance_memory.py       # Memory performance tests
│
├── test_ug_compliance.py     # UG architecture compliance
└── test_import_rules.py             # Import rules compliance
```

---

## Test Configuration

Configuration is managed via `test_config.yaml`:

```yaml
test_framework:
  name: "EE Testing Framework"
  version: "1.0.0"

performance_targets:
  cold_start:
    target_ms: 3000
  hot_path:
    target_ms: 50
  memory:
    target_mb: 80

ug_compliance:
  rules:
    - "All cross-interface calls must use execute_operation()"
    - "No internal debug helper functions"
    - "All files must be <= 350 lines"
```

---

## Fixtures

Key fixtures available in `conftest.py`:

- `execute_operation` - Gateway execute_operation function
- `GatewayInterface` - Gateway interface enum
- `EEGatewayInterface` - EE Gateway interface enum with categories
- `temp_dir` - Temporary directory for tests
- `mock_gateway_stats` - Mock gateway statistics
- `mock_plugin_config` - Mock plugin configuration
- `mock_object_pool_config` - Mock object pool configuration
- `performance_thresholds` - Performance target thresholds
- `ug_rules` - UG compliance rules

---

## Writing Tests

### Unit Test Template

```python
import pytest

@pytest.mark.unit
class TestMyFeature:
    """Test suite for MyFeature."""

    def test_feature_exists(self, execute_operation, EEGatewayInterface):
        """Test that feature exists."""
        result = execute_operation(
            EEGatewayInterface.PLUGINS,
            'my_operation'
        )
        assert result is not None

    @pytest.mark.parametrize("input,expected", [
        ("input1", "output1"),
        ("input2", "output2"),
    ])
    def test_feature_with_params(self, execute_operation, EEGatewayInterface, input, expected):
        """Test feature with parameters."""
        result = execute_operation(
            EEGatewayInterface.PLUGINS,
            'my_operation',
            param=input
        )
        assert result == expected
```

### Integration Test Template

```python
import pytest

@pytest.mark.integration
class TestMyIntegration:
    """Integration tests for MyFeature."""

    def test_full_workflow(self, execute_operation, EEGatewayInterface):
        """Test complete workflow."""
        # Step 1
        execute_operation(EEGatewayInterface.PLUGINS, 'step1')

        # Step 2
        result = execute_operation(EEGatewayInterface.PLUGINS, 'step2')

        # Verify
        assert result is not None
```

### Performance Test Template

```python
import pytest
import time

@pytest.mark.performance
class TestMyPerformance:
    """Performance tests for MyFeature."""

    def test_operation_performance(self, execute_operation, EEGatewayInterface, performance_thresholds):
        """Test operation performance."""
        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            execute_operation(EEGatewayInterface.PLUGINS, 'my_operation')

        elapsed_ms = (time.time() - start_time) * 1000
        avg_ms = elapsed_ms / iterations

        target_ms = performance_thresholds.get('hot_path_ms', 50)
        assert avg_ms < target_ms, f"Too slow: {avg_ms:.2f}ms"
```

### Compliance Test Template

```python
import pytest
import ast
from pathlib import Path

@pytest.mark.compliance
class TestMyCompliance:
    """Compliance tests for MyFeature."""

    def test_no_forbidden_imports(self):
        """Test that forbidden imports are not used."""
        source_file = Path(__file__).parent.parent / 'src' / 'module.py'

        with open(source_file, 'r') as f:
            source = f.read()

        # Check for forbidden patterns
        assert 'forbidden_import' not in source
```

---

## Performance Targets

| Metric | Target | Warning |
|--------|--------|---------|
| Cold Start | <3000ms | <2500ms |
| Hot Path | <50ms | <40ms |
| Memory Usage | <80MB | <70MB |
| Gateway Routing | <1ms | <0.5ms |
| Plugin Load | <500ms | <400ms |

---

## UG Compliance

The testing framework verifies UG architecture compliance:

### Gateway = ISP (Internet Service Provider)
- Central routing hub
- execute_operation() function
- Dispatch dictionary routing

### Interfaces = Routers
- Operation routing
- Dispatch dictionaries
- No cross-interface direct imports

### Implementation = Local Network
- Same-interface dependencies only
- No upward dependencies

### Forbidden Patterns
- Internal debug helper functions (bypasses Gateway)
- Direct imports across interfaces
- Module-level cross-interface imports
- Files > 350 lines

---

## Test Markers

Tests are marked with appropriate markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.compliance` - Compliance tests
- `@pytest.mark.fast` - Fast-running tests
- `@pytest.mark.slow` - Slow-running tests

Run tests by marker:

```bash
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m performance    # Performance tests only
pytest -m compliance     # Compliance tests only
pytest -m fast           # Fast tests only
pytest -m "not slow"     # Skip slow tests
```

---

## Coverage

Generate coverage reports:

```bash
# HTML report
pytest --cov=../src --cov-report=html

# Terminal report
pytest --cov=../src --cov-report=term-missing

# XML report (for CI)
pytest --cov=../src --cov-report=xml

# Minimum coverage threshold
pytest --cov=../src --cov-fail-under=80
```

View HTML coverage report:

```bash
# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## Continuous Integration

Example CI configuration:

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install pytest pytest-cov psutil

      - name: Run tests
        run: |
          cd EE/tests
          python test_runner.py --all --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Troubleshooting

### Import Errors

If you encounter import errors:

```bash
# Add EE src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../src"

# Or use -m pytest
cd EE/tests
python -m pytest -v
```

### Missing Dependencies

```bash
# Install all dependencies
pip install pytest pytest-cov psutil

# Or from requirements
pip install -r requirements.txt
```

### Tests Skipped

If tests are being skipped:

```bash
# Run with -v to see why
pytest -v

# Check if feature is implemented
# Skipped tests expect NotImplementedError
```

---

## Contributing

When adding new tests:

1. Follow naming convention: `test_<feature>_<aspect>.py`
2. Use appropriate markers (@pytest.mark.unit, etc.)
3. Add docstrings to test classes and methods
4. Use parametrize for data-driven tests
5. Include both success and failure cases
6. Update this README if adding new test categories

---

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Use descriptive test names
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Fixtures**: Use fixtures for common setup
5. **Markers**: Mark tests appropriately
6. **Skip Reasons**: Always provide skip reasons
7. **Assertions**: Use specific assertions with helpful messages

---

## Reference

- **LEE Import Rules**: `/reference/LEE-Import-Rules.md`
- **UG Architecture**: `/SIMA/entries/core/ARCH-UG.md`
- **EE Architecture**: `/EE/ARCHITECTURE.md`
- **Function Maps**: `/reference/function-map-*.md`

---

**End of EE Testing Framework README**
