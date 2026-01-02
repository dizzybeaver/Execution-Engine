# DEC-PY-UG-01: Dataclass for Domain Gateways

**REF-ID:** DEC-PY-UG-01
**Category:** Technical Decision
**Priority:** High
**Status:** Active
**Date Decided:** 2025-12-31
**Last Updated:** 2025-12-31

---

## SUMMARY

Use Python's `@dataclass` decorator for domain gateway implementations in Universal Gateway architecture. Provides clean syntax, type safety, and immutability options.

**Decision:** Domain gateways use `@dataclass(frozen=True)` by default
**Impact Level:** Medium
**Reversibility:** Easy (refactorable to regular class)

---

## CONTEXT

### Problem Statement

Domain gateways in UG architecture need:
- Clean, declarative syntax for configuration
- Type safety for domain parameters
- Immutability for thread safety
- Minimal boilerplate code
- Easy instantiation and testing

### Background

From EE codebase analysis:
- `gateway_domains.py` uses `@dataclass(frozen=True)` for all gateways
- Provides clean configuration initialization
- Frozen prevents accidental state mutation
- Type hints improve IDE support

### Requirements

- Declarative configuration syntax
- Type safety with static analysis
- Thread-safe default (immutable)
- Support for optional dependencies
- Easy to test and instantiate

---

## DECISION

### What We Chose

Use Python `@dataclass` decorator for all domain gateway implementations. Default to `frozen=True` for immutability.

### Implementation Pattern

```python
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class ConfigGateway(DomainGateway):
    """Configuration management gateway."""

    config_manager: Optional[Any] = None

    def execute(self, route: str, payload: dict) -> Any:
        """Execute configuration operation."""
        if route == "config.get":
            return self._get_config(payload)
        elif route == "config.set":
            return self._set_config(payload)
        # ... more routes

    def _get_config(self, payload: dict) -> Any:
        """Get configuration value."""
        # Implementation
        pass
```

### Benefits

**1. Clean Syntax**
- Declarative field definitions
- Auto-generated `__init__`, `__repr__`, `__eq__`
- No boilerplate code

**2. Type Safety**
- Type hints for all fields
- Static analysis support (mypy, pyright)
- Better IDE autocomplete

**3. Immutability Option**
- `frozen=True` prevents state mutation
- Thread-safe by default
- Catches accidental modifications

**4. Default Values**
- Easy field initialization
- Optional fields supported
- Clean instantiation

---

## RATIONALE

### 1. Reduced Boilerplate

**Without dataclass (traditional class):**
```python
class ConfigGateway(DomainGateway):
    def __init__(self, config_manager: Optional[Any] = None):
        self.config_manager = config_manager

    def __repr__(self):
        return f"ConfigGateway(config_manager={self.config_manager!r})"

    def __eq__(self, other):
        if not isinstance(other, ConfigGateway):
            return NotImplemented
        return self.config_manager == other.config_manager

    def execute(self, route: str, payload: dict) -> Any:
        # ... implementation
```

**With dataclass:**
```python
@dataclass(frozen=True)
class ConfigGateway(DomainGateway):
    config_manager: Optional[Any] = None

    def execute(self, route: str, payload: dict) -> Any:
        # ... implementation
```

**Lines saved:** 15 lines → 4 lines (73% reduction)

### 2. Type Safety

```python
@dataclass(frozen=True)
class SecurityGateway(DomainGateway):
    auth_service: Any  # Generic type
    encryption_key: str  # Required field
    max_retries: int = 3  # Default value

# Type checking catches errors
gateway = SecurityGateway(
    auth_service=auth,
    encryption_key=123,  # ❌ Type error: int != str
    max_retries="three"  # ❌ Type error: str != int
)
```

### 3. Thread Safety

**Frozen dataclass:**
```python
@dataclass(frozen=True)
class MetricsGateway(DomainGateway):
    metrics_store: Any = None

# Immutable - cannot modify
gateway = MetricsGateway(store)
gateway.metrics_store = new_store  # ❌ Raises: FrozenInstanceError
```

**Benefits:**
- Safe to share across threads
- No accidental state changes
- Predictable behavior

### 4. Clean Instantiation

```python
# All fields documented in class definition
gateway = ConfigGateway(
    config_manager=my_config
)

# Optional fields use defaults
gateway = ConfigGateway()  # config_manager=None

# Clear repr for debugging
print(gateway)
# Output: ConfigGateway(config_manager=<ConfigManager object at 0x...>)
```

---

## ALTERNATIVES CONSIDERED

### Alternative 1: Regular Classes

**Pros:**
- Full control over initialization
- Mutable by default
- Familiar pattern

**Cons:**
- More boilerplate code
- Manual `__init__`, `__repr__`, `__eq__`
- No automatic type checking
- More maintenance overhead

**Why Rejected:** Dataclass provides same features with less code.

---

### Alternative 2: Named Tuples

**Pros:**
- Immutable by default
- Lightweight

**Cons:**
- No default values (Python <3.11)
- Cannot have methods
- Less flexible
- No inheritance support

**Why Rejected:** Too restrictive for gateway use cases.

---

### Alternative 3: Pydantic Models

**Pros:**
- Validation on instantiation
- JSON serialization
- Type coercion

**Cons:**
- External dependency
- Heavier than dataclass
- Overkill for simple gateways

**Why Rejected:** Unnecessary complexity for internal gateways.

---

## TRADE-OFFS

### What We Gained
- Clean, declarative syntax (70% less boilerplate)
- Type safety with static analysis
- Built-in immutability option
- Better debugging with auto-generated `__repr__`
- Consistent pattern across all gateways

### What We Accepted
- Requires Python 3.7+ (dataclass introduced)
- Frozen classes require `dataclasses.replace()` to update
- Slightly less flexible than manual classes

---

## IMPACT ANALYSIS

### Technical Impact
- **Code Volume:** Reduced by 60-70%
- **Type Safety:** Improved with type hints
- **Thread Safety:** Default with frozen=True
- **Testing:** Easier with clear initialization

### Developer Impact
- **Readability:** Improved (clear field definitions)
- **Maintenance:** Reduced (less boilerplate)
- **Onboarding:** Faster (consistent pattern)
- **IDE Support:** Better (type hints)

---

## USAGE EXAMPLES

### Basic Gateway

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class LoggingGateway(DomainGateway):
    """Logging operations gateway."""

    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"

    def execute(self, route: str, payload: dict) -> Any:
        if route == "logging.log.info":
            return self._log_info(payload)
        # ... more routes

    def _log_info(self, payload: dict) -> bool:
        message = payload.get("message")
        print(f"[{self.log_level}] {message}")
        return True
```

### Gateway with Dependencies

```python
@dataclass(frozen=True)
class NetworkGateway(DomainGateway):
    """Network operations gateway."""

    http_client: Any  # Required dependency
    connection_pool: Any = None  # Optional
    timeout: int = 30  # Default value

    def execute(self, route: str, payload: dict) -> Any:
        if route == "network.http.get":
            return self._http_get(payload)
        # ... more routes
```

### Creating Gateway Variants

```python
# Create with custom config
custom_gateway = LoggingGateway(
    log_level="DEBUG",
    log_format="%(levelname)s: %(message)s"
)

# Update frozen gateway
from dataclasses import replace

updated_gateway = replace(
    custom_gateway,
    log_level="ERROR"
)
```

---

## WHEN TO USE MUTABLE

Use `frozen=False` when:

**1. Runtime Configuration Changes**
```python
@dataclass  # Mutable
class ConfigGateway(DomainGateway):
    config_manager: Any = None

    def reload_config(self):
        # Allowed to modify state
