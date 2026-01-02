# LESS-PY-UG-01: Immutable Gateways Default

**Status:** Active
**Category:** Architecture Lesson
**Source:** EE Codebase Analysis
**Created:** 2025-12-31
**Priority:** High

---

## SUMMARY

Prefer frozen dataclasses for domain gateways by default to ensure thread safety and prevent accidental state mutation. Only use mutable gateways when runtime state changes are required.

**Principle:** Immutability by default, mutability when necessary
**Benefit:** Thread safety, predictability, easier debugging
**Pattern:** `@dataclass(frozen=True)` for gateways

---

## THE PROBLEM

### Mutable Gateways Create Complexity

```python
# ❌ BAD: Mutable gateway (default behavior)
@dataclass  # Mutable by default
class ConfigGateway:
    """Configuration gateway (mutable)."""

    config_manager: Any = None
    cache: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize mutable state."""
        if self.cache is None:
            self.cache = {}

    def execute(self, route: str, payload: dict) -> Any:
        if route == "config.get":
            # Can accidentally mutate state
            self.cache["last_get"] = payload.get("key")
            return self._get_config(payload)

# Issues:
# 1. Multiple threads can modify self.cache simultaneously
# 2. Accidental state changes in unexpected places
# 3. Hard to debug when state changes
# 4. Race conditions in concurrent access
```

**Problems:**
- Thread safety issues
- Accidental mutations
- Hard to debug
- Unpredictable behavior

---

## THE SOLUTION

### Frozen Dataclasses by Default

```python
# ✅ GOOD: Immutable gateway (frozen)
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class ConfigGateway:
    """Configuration gateway (immutable)."""

    config_manager: Optional[Any] = None

    def execute(self, route: str, payload: dict) -> Any:
        if route == "config.get":
            return self._get_config(payload)
        elif route == "config.set":
            return self._set_config(payload)

    def _get_config(self, payload: dict) -> Any:
        """Get configuration value."""
        key = payload.get("key")
        default = payload.get("default")
        # Pure function - no state mutation
        return self.config_manager.get(key, default)

# Benefits:
# 1. Thread-safe - no mutable state
# 2. Predictable - state never changes
# 3. Easy to debug - no side effects
# 4. Safe to share across threads
```

---

## WHY IMMUTABILITY

### 1. Thread Safety

**Mutable gateway (unsafe):**
```python
@dataclass
class MetricsGateway:
    """Mutable metrics gateway."""

    counters: Dict[str, int] = None

    def __post_init__(self):
        self.counters = {}

    def increment(self, name: str):
        """NOT thread-safe!"""
        self.counters[name] = self.counters.get(name, 0) + 1

# Problem: Race condition
# Thread 1: reads counters[name] = 5
# Thread 2: reads counters[name] = 5
# Thread 1: writes counters[name] = 6
# Thread 2: writes counters[name] = 6 (should be 7!)
```

**Immutable gateway (safe):**
```python
@dataclass(frozen=True)
class MetricsGateway:
    """Immutable metrics gateway."""

    store: Any = None  # Thread-safe external store

    def increment(self, name: str):
        """Thread-safe - delegates to external store."""
        return self.store.increment(name)  # Store handles synchronization
```

### 2. Predictable Behavior

**Mutable gateway (unpredictable):**
```python
gateway = ConfigGateway(manager)

# Call 1
result1 = gateway.execute("config.get", {"key": "foo"})
print(gateway.cache)  # {"last_get": "foo"}

# Call 2
result2 = gateway.execute("config.get", {"key": "bar"})
print(gateway.cache)  # {"last_get": "bar"} - Changed!

# Hard to reason about state
```

**Immutable gateway (predictable):**
```python
gateway = ConfigGateway(manager)

# Call 1
result1 = gateway.execute("config.get", {"key": "foo"})

# Call 2
result2 = gateway.execute("config.get", {"key": "bar"})

# State never changes - always predictable
```

### 3. Easier Debugging

**Mutable gateway (hard to debug):**
```python
# Bug: Gateway state is corrupted somewhere
gateway = ConfigGateway(manager)

gateway.execute("config.set", {"key": "foo", "value": 1})
gateway.execute("some_other_operation", {})  # Oops, mutates state!
gateway.execute("config.get", {"key": "foo"})  # Returns wrong value

# Where did state change? Hard to track!
```

**Immutable gateway (easy to debug):**
```python
# State cannot be corrupted
gateway = ConfigGateway(manager)

gateway.execute("config.set", {"key": "foo", "value": 1})
gateway.execute("some_other_operation", {})  # Cannot mutate gateway
gateway.execute("config.get", {"key": "foo"})  # Always works

# State is always consistent
```

### 4. Safer Sharing

**Mutable gateway (unsafe sharing):**
```python
# Shared across threads
gateway = ConfigGateway(manager)

# Thread 1
def thread1():
    gateway.execute("config.set", {"key": "foo", "value": 1})

# Thread 2
def thread2():
    gateway.execute("config.set", {"key": "foo", "value": 2})

# Race condition! Which value wins?
```

**Immutable gateway (safe sharing):**
```python
# Shared across threads - no problem!
gateway = ConfigGateway(manager)

# Both threads can execute safely
# No state mutation means no race conditions
```

---

## USING FROZEN DATACLASSES

### Basic Pattern

```python
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class Gateway:
    """Immutable gateway."""

    dependency: Optional[Any] = None
    timeout: int = 30

    def execute(self, route: str, payload: dict) -> Any:
        """Execute operation."""
        # Implementation
        pass

# Usage
gateway = Gateway(dependency=manager, timeout=60)
result = gateway.execute("operation", {})
```

### Creating Variants with dataclasses.replace()

```python
from dataclasses import replace

# Original gateway
gateway = ConfigGateway(manager, timeout=30)

# Create variant with different timeout
gateway_with_timeout = replace(gateway, timeout=60)

# Original unchanged
print(gateway.timeout)  # 30
print(gateway_with_timeout.timeout)  # 60
```

### Initialization Validation

```python
@dataclass(frozen=True)
class Gateway:
    """Gateway with validation."""

    dependency: Any
    timeout: int = 30

    def __post_init__(self):
        """Validate after initialization."""
        if self.timeout <= 0:
            raise ValueError(f"Timeout must be positive: {self.timeout}")

        if self.dependency is None:
            raise ValueError("Dependency required")

# Usage
gateway = Gateway(manager, timeout=30)  # OK
gateway = Gateway(manager, timeout=-1)  # Raises ValueError
```

---

## WHEN TO USE MUTABLE

Only use mutable gateways when:

### 1. Runtime State Changes Required

```python
@dataclass  # Mutable
class CacheGateway:
    """Gateway with mutable cache."""

    cache: Dict[str, Any] = None

    def __post_init__(self):
        self.cache = {}

    def execute(self, route: str, payload: dict) -> Any:
        if route == "cache.get":
            return self._get(payload)
        elif route == "cache.set":
            return self._set(payload)

    def _get(self, payload: dict) -> Any:
        key = payload.get("key")
        return self.cache.get(key)

    def _set(self, payload: dict) -> bool:
        key = payload.get("key")
        value = payload.get("value")
        self.cache[key] = value  # Mutation required
        return True
```

**Why mutable here:**
- Cache inherently needs state changes
- Local cache doesn't require thread safety
- Performance requires in-memory mutations

### 2. Connection Pool Management

```python
@dataclass  # Mutable
class ConnectionGateway:
    """Gateway managing connection pool."""

    pool: List[Any] = None
    max_size: int = 10

    def __post_init__(self):
        self.pool = []

    def get_connection(self) -> Any:
        """Get connection from pool."""
        if self.pool:
            return self.pool.pop()
        return self._create_connection()

    def return_connection(self, conn: Any) -> None:
        """Return connection to pool."""
        if len(self.pool) < self.max_size:
            self.pool.append(conn)  # Mutation required
```

**Why mutable here:**
