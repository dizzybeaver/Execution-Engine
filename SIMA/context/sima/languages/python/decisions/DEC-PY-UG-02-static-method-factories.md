# DEC-PY-UG-02: Static Methods for Factories

**REF-ID:** DEC-PY-UG-02
**Category:** Technical Decision
**Priority:** Medium
**Status:** Active
**Date Decided:** 2025-12-31
**Last Updated:** 2025-12-31

---

## SUMMARY

Factory operations in Universal Gateway architecture should be implemented as static methods rather than instance methods or standalone functions. This provides simpler instantiation, cleaner interfaces, and better organization.

**Decision:** Factories use `@staticmethod` for all operations
**Impact Level:** Medium
**Reversibility:** Easy (refactorable to instance methods)

---

## CONTEXT

### Problem Statement

Factory classes in UG architecture need to:
- Create gateway instances without initialization overhead
- Provide utility functions without instance state
- Organize related operations logically
- Support simple calling patterns
- Avoid unnecessary object creation

### Background

From EE codebase analysis:
- Gateway factories use static methods for route execution
- No instance state needed in factories
- Simpler than creating factory instances
- Clearer separation of concerns

### Requirements

- No instance state in factories
- Direct execution without instantiation
- Clean, callable interface
- Logical grouping of operations
- Easy to test and mock

---

## DECISION

### What We Chose

Use Python `@staticmethod` decorator for all factory operations. Factory classes group related operations but don't require instantiation.

### Implementation Pattern

```python
from typing import Any, Dict

class ConfigFactory:
    """Configuration factory for creating config instances."""

    @staticmethod
    def create_config(config_type: str, **kwargs) -> Any:
        """Create configuration instance."""
        if config_type == "env":
            return EnvConfig(**kwargs)
        elif config_type == "file":
            return FileConfig(**kwargs)
        else:
            raise ValueError(f"Unknown config type: {config_type}")

    @staticmethod
    def load_config(source: str) -> Dict[str, Any]:
        """Load configuration from source."""
        # Implementation
        pass

# Usage: No instantiation needed
config = ConfigFactory.create_config("env", prefix="APP_")
settings = ConfigFactory.load_config("config.yaml")
```

### Benefits

**1. No Instantiation Overhead**
- Direct calls to factory methods
- No `__init__` execution
- Simpler calling pattern

**2. Clear Intent**
- Static methods = stateless operations
- Instance methods = stateful operations
- Obvious from method signature

**3. Better Organization**
- Related methods grouped in class
- Namespace separation
- Logical structure

**4. Easier Testing**
- Mock entire factory class
- No instance setup needed
- Isolated testing

---

## RATIONALE

### 1. Stateless Operations

**Factories create objects but hold no state:**

```python
# ✅ Good: Static methods (stateless)
class NetworkFactory:
    @staticmethod
    def create_http_client(config: Dict) -> HttpClient:
        return HttpClient(config)

    @staticmethod
    def create_websocket_connection(url: str) -> WebSocket:
        return WebSocket(url)

# Usage - direct
client = NetworkFactory.create_http_client(config)
ws = NetworkFactory.create_websocket_connection(url)

# ❌ Bad: Instance methods (unnecessary state)
class NetworkFactory:
    def __init__(self):
        self.config = None  # Never used!

    def create_http_client(self, config: Dict) -> HttpClient:
        return HttpClient(config)

# Usage - unnecessary instantiation
factory = NetworkFactory()  # Why?
client = factory.create_http_client(config)
```

**Why static?**
- Factory doesn't use instance attributes
- No state to track across calls
- Simpler calling pattern

### 2. Namespace Organization

**Group related operations:**

```python
class ConfigFactory:
    """All configuration-related operations."""

    @staticmethod
    def create_config(source: str) -> Config:
        """Create config instance."""
        pass

    @staticmethod
    def validate_config(config: Config) -> bool:
        """Validate configuration."""
        pass

    @staticmethod
    def merge_configs(*configs: Config) -> Config:
        """Merge multiple configs."""
        pass

class LogFactory:
    """All logging-related operations."""

    @staticmethod
    def create_logger(name: str) -> Logger:
        """Create logger instance."""
        pass

    @staticmethod
    def configure_logging(level: str) -> None:
        """Configure root logger."""
        pass
```

**Benefits:**
- Clear namespace separation
- Related operations grouped
- No naming conflicts

### 3. Simpler Testing

**Easy to mock static methods:**

```python
# Test code
def test_gateway_with_mock_factory():
    # Mock entire factory
    mock_config = MockConfig()
    ConfigFactory.create_config = Mock(return_value=mock_config)

    # Test gateway
    gateway = ConfigGateway()
    result = gateway.execute("config.get", {"key": "test"})

    # Verify
    ConfigFactory.create_config.assert_called_once()
```

### 4. Performance

**No object creation overhead:**

```python
# Static method (fast)
result = ConfigFactory.create_config("env")

# Instance method (slower)
factory = ConfigFactory()  # Unnecessary allocation
result = factory.create_config("env")
```

---

## ALTERNATIVES CONSIDERED

### Alternative 1: Instance Methods

**Pros:**
- Familiar pattern
- Can hold state if needed later
- Supports inheritance

**Cons:**
- Unnecessary instantiation
- Confusing intent (stateless vs stateful)
- Extra overhead

**Example:**
```python
class ConfigFactory:
    def __init__(self):
        # No state needed!
        pass

    def create_config(self, source: str) -> Config:
        return Config(source)

# Usage
factory = ConfigFactory()  # Why?
config = factory.create_config("env")
```

**Why Rejected:** Unnecessary overhead when no state needed.

---

### Alternative 2: Module-Level Functions

**Pros:**
- Simplest syntax
- No class wrapper

**Cons:**
- No namespace organization
- Harder to mock in tests
- All functions in one namespace

**Example:**
```python
# config_factory.py
def create_config(source: str) -> Config:
    return Config(source)

def validate_config(config: Config) -> bool:
    return config.validate()

# Usage - no grouping
from config_factory import create_config, validate_config
```

**Why Rejected:** Harder to organize in large codebases.

---

### Alternative 3: Class Methods

**Pros:**
- Access to class attributes
- Can be overridden

**Cons:**
- Receives `cls` argument (unused)
- Slightly more complex
- Not needed for stateless operations

**Example:**
```python
class ConfigFactory:
    default_type = "env"

    @classmethod
    def create_config(cls, source: str) -> Config:
        # cls parameter but never used
        return Config(source)
```

**Why Rejected:** Class methods intended for class-level state, not stateless factories.

---

## TRADE-OFFS

### What We Gained
- Simpler calling syntax (no instantiation)
- Clear intent (static = stateless)
- Better organization (grouped operations)
- Easier testing (easy mocking)
- Better performance (no object creation)

### What We Accepted
- Cannot hold instance state (feature, not bug)
- Cannot use inheritance to override behavior
- Slightly more verbose than module functions

---

## IMPACT ANALYSIS

### Technical Impact
- **Code Simplicity:** Improved (less boilerplate)
- **Performance:** Better (no allocation overhead)
- **Testability:** Improved (easy mocking)
- **Organization:** Better (logical grouping)

### Developer Impact
- **Clarity:** Improved (static = stateless)
- **Discovery:** Easier (related methods grouped)
- **Maintenance:** Reduced (clearer structure)

---

## USAGE EXAMPLES

### Basic Factory

```python
from typing import Any, Dict

class ConfigFactory:
