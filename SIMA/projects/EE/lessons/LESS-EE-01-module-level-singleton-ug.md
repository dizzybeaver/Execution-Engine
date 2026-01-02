# LESS-EE-01: Module-Level Singleton UG Pattern

**Category:** Lesson Learned
**Status:** Production
**EE Version:** 2.0.0
**Last Updated:** 2025-12-31

---

## Overview

**Lesson:** Use module-level singleton with lazy initialization for the Universal Gateway.

**Problem:** How to provide fast import times while maintaining a single UG instance?

**Solution:** Module-level private variables with lazy initialization via `get_ug()` function.

---

## The Pattern

### Implementation in EE/__init__.py

```python
# EE/__init__.py (lines 117-321)

# ============================================================================
# Create Global UG Instance
# ============================================================================

_ug: Optional[UniversalGateway] = None
_registry: Optional[EEDomainRegistry] = None


def get_ug() -> UniversalGateway:
    """Get the Universal Gateway instance.

    This function initializes the UG on first call and returns the singleton.

    Returns:
        UniversalGateway instance

    Example:
        ug = get_ug()
        stats = ug.get_stats()
    """
    global _ug
    if _ug is None:
        _ug = _initialize_ug()
    return _ug


def get_registry() -> EEDomainRegistry:
    """Get the domain registry instance.

    This function returns the registry containing all registered domain gateways.

    Returns:
        EEDomainRegistry instance

    Example:
        registry = get_registry()
        if registry.has_domain("foundation"):
            gateway = registry.get("foundation")
    """
    global _registry
    if _registry is None:
        _initialize_ug()
    return _registry
```

### Lazy Initialization Function

```python
# EE/__init__.py (lines 121-303)

def _initialize_ug() -> UniversalGateway:
    """Initialize the Universal Gateway with all domain gateways.

    This function is called once to create and configure the UG singleton.
    It registers all 15 domain gateways.

    Returns:
        Initialized UniversalGateway instance
    """
    global _ug, _registry

    if _ug is not None:
        return _ug

    # Create UG instance
    _ug = UniversalGateway(
        logger_factory=_default_logger_factory,
        metrics_factory=_default_metrics_factory,
    )

    # Create registry
    _registry = EEDomainRegistry.get_instance()

    # ========================================================================
    # Register ALL Domain Gateways
    # ========================================================================

    # 1. Foundation Domain (32 operations)
    from .foundation import FoundationGateway
    foundation_gateway = FoundationGateway(
        logger=_ug.get_logger("foundation"),
        metrics=_ug.get_metrics("foundation"),
        call_operation=_ug.execute_operation
    )
    _ug.register_domain_gateway("foundation", foundation_gateway)
    _registry.register("foundation", foundation_gateway)

    # 2. Observability Domain (38 operations)
    from .observability import ObservabilityGateway
    observability_gateway = ObservabilityGateway(
        logger=_ug.get_logger("observability"),
        metrics=_ug.get_metrics("observability"),
        call_operation=_ug.execute_operation
    )
    _ug.register_domain_gateway("observability", observability_gateway)
    _registry.register("observability", observability_gateway)

    # ... (13 more domains)

    return _ug
```

### Execute Operation Uses Singleton

```python
# EE/__init__.py (lines 434-436)

def execute_operation(
    domain: str,
    interface: str,
    operation: str,
    **kwargs: Any,
) -> Any:
    """SINGLE entry point for EE operations."""
    ug = get_ug()  # ← Lazy initialization on first call
    return ug.execute_operation(domain, interface, operation, **kwargs)
```

---

## Benefits

### 1. Fast Import Times

**Import is instant:**

```python
# This completes immediately (no initialization)
from EE import execute_operation

# UG initialization happens later, on first call
result = execute_operation(
    domain="foundation",
    interface="config",
    operation="get",
    key="database.host"
)
# ← _ug initialized here on first call
```

**Benchmark:**
- Import time: ~1ms (just module loading)
- First call: ~50-100ms (UG initialization + domain registration)
- Subsequent calls: ~1-5ms (just routing)

### 2. Lambda-Friendly

**AWS Lambda cold start:**

```python
# lambda_function.py
from EE import execute_operation

def lambda_handler(event, context):
    """Lambda handler - UG initializes on first invocation."""

    # First invocation: cold start (~100ms)
    # - Import EE (already done by Lambda)
    # - Call execute_operation triggers UG init
    result = execute_operation(
        domain="observability",
        interface="logging",
        operation="info",
        message="Lambda invoked"
    )

    # Process event (subsequent calls are fast)
    config = execute_operation(
        domain="foundation",
        interface="config",
        operation="get",
        key="API_KEY"
    )

    return process_event(event, config)
```

**Benefits:**
- Import happens during Lambda's init phase (free time)
- UG initialization happens during first invocation (necessary work)
- Subsequent invocations reuse initialized UG (warm start)

### 3. Thread-Safe Singleton

**Python's GIL protects the singleton:**

```python
# Thread-safe due to GIL
def get_ug() -> UniversalGateway:
    global _ug
    if _ug is None:
        _ug = _initialize_ug()  # Only one thread executes this
    return _ug

# Multiple threads can safely call get_ug()
# First thread initializes, others get existing instance
```

**Note:** For true thread-safe lazy initialization in multi-threaded environments:

```python
import threading

_ug = None
_lock = threading.Lock()

def get_ug() -> UniversalGateway:
    global _ug
    if _ug is None:
        with _lock:
            # Double-check pattern
            if _ug is None:
                _ug = _initialize_ug()
    return _ug
```

### 4. Test-Friendly

**Can reset UG in tests:**

```python
# test_module.py
import EE
from EE.universal_gateway import UniversalGateway

def test_with_mock_ug():
    """Test with mocked UG instance."""

    # Save original
    original_ug = EE._ug

    try:
        # Set test UG
        EE._ug = UniversalGateway(
            logger_factory=lambda name: MockLogger(),
            metrics_factory=lambda name: MockMetrics()
        )

        # Test uses mocked UG
        result = EE.execute_operation(
            domain="foundation",
            interface="config",
            operation="get",
            key="test.key"
        )

        assert result == "mocked_value"

    finally:
        # Restore original
        EE._ug = original_ug
```

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Eager Initialization

```python
# DON'T: Initialize at module import time
from EE.universal_gateway import UniversalGateway

_ug = UniversalGateway(...)  # ← Slow import!

# Problem:
# - Import statement takes 100ms
# - Lambda cold starts pay penalty even if function not called
# - Unit tests always initialize UG
```

### ❌ Anti-Pattern 2: Class-Based Singleton

```python
# DON'T: Use class-based singleton pattern
class UniversalGateway:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Problems:
# - More complex than module-level singleton
# - Harder to test (can't easily swap instance)
# - Class-level state is less Pythonic
```

### ❌ Anti-Pattern 3: Borg Pattern

```python
# DON'T: Use Borg pattern (shared state)
class UniversalGateway:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state

# Problems:
# - Over-engineered for UG use case
# - Confusing behavior
# - Still requires initialization logic
```

---

## Best Practices

### ✅ Best Practice 1: Module-Level Singleton

```python
# DO: Use module-level singleton with lazy init

_ug: Optional[UniversalGateway] = None

def get_ug() -> UniversalGateway:
    """Get UG instance (lazy initialization)."""
    global _ug
    if _ug is None:
        _ug = _initialize_ug()
    return _ug
```

### ✅ Best Practice 2: Private Module Variables

```python
# DO: Use underscore prefix for private globals

# ✅ Correct: Private module variables
_ug: Optional[UniversalGateway] = None
_registry: Optional[EEDomainRegistry] = None

# ❌ Wrong: Public module variables
ug: Optional[UniversalGateway] = None
registry: Optional[EEDomainRegistry] = None
```

**Rationale:**
- Underscore prefix signals "private, don't access directly"
- Users call `get_ug()`, not `EE._ug`
- Maintains encapsulation

### ✅ Best Practice 3: Initialize Once

```python
# DO: Guard against multiple initialization

def _initialize_ug() -> UniversalGateway:
    """Initialize UG (called once)."""
    global _ug, _registry

    # Check if already initialized
    if _ug is not None:
        return _ug

    # Perform initialization
    _ug = UniversalGateway(...)
    _registry = EEDomainRegistry.get_instance()

    # Register domains
    ...

    return _ug
```

### ✅ Best Practice 4: Explicit Getter Functions

```python
# DO: Provide explicit getters for dependencies

def get_ug() -> UniversalGateway:
    """Get UG instance."""
    global _ug
    if _ug is None:
        _ug = _initialize_ug()
    return _ug

def get_registry() -> EEDomainRegistry:
    """Get registry instance."""
    global _registry
    if _registry is None:
        _initialize_ug()
    return _registry

# Benefits:
# - Clear intent
# - Lazy initialization
# - Type hints in return value
```

---

## Real-World Examples from EE

### Example 1: Foundation Domain Singleton

```python
# EE/foundation/singleton/singleton_factory.py

_instance = None

def get_singleton_instance():
    """Get singleton instance (lazy initialization)."""
    global _instance
    if _instance is None:
        _instance = SingletonManager()
    return _instance
```

### Example 2: Domain Registry Singleton

```python
# EE/universal_gateway/gateway_registry.py

class EEDomainRegistry:
    """Registry for all EE domain gateways."""

    _instance: Optional["EEDomainRegistry"] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "EEDomainRegistry":
        """Get singleton registry instance (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
```

---

## When to Use This Pattern

### ✅ Use When:

1. **Expensive initialization:** UG takes 50-100ms to initialize
2. **Not always needed:** Some imports may not call UG
3. **Single instance needed:** Only one UG per process
4. **Global access needed:** Multiple modules need UG access
5. **Fast import times important:** Lambda, CLI tools

### ❌ Don't Use When:

1. **Cheap initialization:** If init is <1ms, eager is fine
2. **Always needed:** If every import calls UG immediately
3. **Multiple instances needed:** If you need multiple UG instances
4. **Test isolation:** If tests need independent instances (use dependency injection)

---

## Testing with Singleton

### Pattern 1: Reset Between Tests

```python
import EE

def setup_function():
    """Reset UG before each test."""
    EE._ug = None
    EE._registry = None

def test_1():
    """Test with fresh UG."""
    result = EE.execute_operation(...)
    assert result == ...

def test_2():
    """Test with fresh UG (independent of test_1)."""
    result = EE.execute_operation(...)
    assert result == ...
```

### Pattern 2: Mock UG for Tests

```python
import EE
from unittest.mock import Mock, MagicMock

def test_with_mock():
    """Test with mocked UG."""
    # Create mock UG
    mock_ug = MagicMock()
    mock_ug.execute_operation.return_value = "mocked"

    # Replace global UG
    EE._ug = mock_ug

    # Test uses mock
    result = EE.execute_operation("foundation", "config", "get", key="test")
    assert result == "mocked"

    # Verify call
    mock_ug.execute_operation.assert_called_once_with(
        "foundation", "config", "get", key="test"
    )
```

---

## Related Patterns

- **ARCH-EE-01:** Single entry point pattern
- **GATE-EE-01:** UniversalGateway class implementation
- **SINGLE-GEN-01:** Generic singleton pattern guidelines

---

## References

- **Implementation:** `d:\Code\Project\EE\__init__.py` (lines 117-321)
- **UG Architecture:** `d:\Code\Project\UG Architecture Guide.md`
- **Domain Registry:** `d:\Code\Project\EE\universal_gateway\gateway_registry.py`
- **Foundation Singleton:** `d:\Code\Project\EE\foundation\singleton\`
