# Python Universal Gateway Pattern Knowledge Index

**Version:** 1.0.0
**Date:** 2025-12-31
**Purpose:** Index of Python-specific UG pattern entries

---

## Overview

This index provides quick access to Python-specific Universal Gateway pattern knowledge entries created from EE codebase analysis and UG Architecture Guide extraction.

---

## Decisions (DEC-PY-UG-NN)

### DEC-PY-UG-01: Dataclass for Domain Gateways
**Location:** `/sima/languages/python/decisions/DEC-PY-UG-01-dataclass-domain-gateways.md`

**Summary:** Use `@dataclass` decorator for domain gateway implementations with `frozen=True` by default for thread safety and clean syntax.

**Key Points:**
- 70% less boilerplate code
- Type safety with static analysis
- Built-in immutability option
- Auto-generated `__init__`, `__repr__`, `__eq__`

**Example:**
```python
@dataclass(frozen=True)
class ConfigGateway(DomainGateway):
    config_manager: Optional[Any] = None

    def execute(self, route: str, payload: dict) -> Any:
        # Implementation
```

---

### DEC-PY-UG-02: Static Methods for Factories
**Location:** `/sima/languages/python/decisions/DEC-PY-UG-02-static-method-factories.md`

**Summary:** Factory operations should be static methods rather than instance methods for simpler instantiation and no unnecessary state.

**Key Points:**
- No instantiation overhead
- Clear intent (static = stateless)
- Better organization
- Easier testing

**Example:**
```python
class ConfigFactory:
    @staticmethod
    def create_config(source: str, **kwargs) -> Config:
        return Config(source, **kwargs)

# Usage: No instantiation needed
config = ConfigFactory.create_config("env")
```

---

## Patterns (GATE-PY-UG-NN)

### GATE-PY-UG-01: SimpleDomainGateway Implementation
**Location:** `/sima/languages/python/patterns/GATE-PY-UG-01-simple-domain-gateway.md`

**Summary:** Convenience base class using dispatch dictionary for O(1) route routing. Eliminates repetitive if-else chains.

**Key Points:**
- O(1) lookup vs O(n) for if-elif
- Cleaner code (60-70% less)
- Easier extension
- Dynamic handler registration

**Example:**
```python
class ConfigGateway(SimpleDomainGateway):
    def _register_handlers(self):
        self._register("config.get", self._get_config)
        self._register("config.set", self._set_config)
```

**Performance:**
- 10 routes: ~5x faster
- 50 routes: ~25x faster
- 100 routes: ~50x faster

---

### GATE-PY-UG-02: DISPATCH Dictionary Pattern (Python)
**Location:** `/sima/languages/python/patterns/GATE-PY-UG-02-dispatch-dictionary.md`

**Summary:** Python implementation of O(1) dispatch routing using dictionary mapping routes to callable handlers.

**Key Points:**
- O(1) constant-time lookup
- Dynamic registration support
- Clean separation of concerns
- Easy to test

**Example:**
```python
DISPATCH = {
    "config.get": _get_config,
    "config.set": _set_config,
    "security.encrypt": _encrypt,
}

def execute_operation(route: str, payload: dict) -> Any:
    if route not in DISPATCH:
        raise ValueError(f"Unknown route: {route}")
    return DISPATCH[route](payload)
```

**Advanced Patterns:**
- Nested dispatch (hierarchical routing)
- Wildcard matching (fnmatch support)
- Middleware chains (pre/post processing)
- Lazy loading (on-demand imports)

---

## Lessons (LESS-PY-UG-NN)

### LESS-PY-UG-01: Immutable Gateways Default
**Location:** `/sima/languages/python/lessons/LESS-PY-UG-01-immutable-gateways-default.md`

**Summary:** Prefer frozen dataclasses for domain gateways by default to ensure thread safety. Only use mutable when runtime state changes required.

**Key Points:**
- Thread safety by default
- Predictable behavior
- Easier debugging
- Safe sharing across threads

**When to Use Mutable:**
1. Runtime state changes required (caching, pooling)
2. Connection pool management
3. Metrics collection

**Best Practices:**
```python
# ✅ Default: Frozen gateway
@dataclass(frozen=True)
class ConfigGateway:
    config_manager: Any = None

# ⚠️ Exception: Mutable when necessary
@dataclass  # Document why!
class CacheGateway:
    """Mutable: Manages in-memory cache."""
    cache: Dict[str, Any] = None
```

---

## Cross-References

### EE Codebase Examples
- `EE/src_backup/gateway/gateway_domains.py` - All gateways use `@dataclass(frozen=True)`
- `EE/scanner/gateway/gateway.py` - Scanner gateway with dispatch pattern
- `EE/src_backup/gateway/gateway_router.py` - Unified router implementation

### Related Generic Entries
- **DEC-GEN-01:** Factory Pattern
- **DEC-GEN-02:** Singleton Registry
- **GATE-UG-01:** Domain Gateway Pattern (generic)

---

## Quick Reference

### Gateway Template

```python
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class MyGateway(SimpleDomainGateway):
    """My domain gateway."""

    dependency: Optional[Any] = None
    timeout: int = 30

    def _register_handlers(self) -> None:
        """Register route handlers."""
        self._register("my.route1", self._route1_handler)
        self._register("my.route2", self._route2_handler)

    def _route1_handler(self, payload: dict) -> Any:
        """Handle route1."""
        # Implementation
        pass

    def _route2_handler(self, payload: dict) -> Any:
        """Handle route2."""
        # Implementation
        pass
```

### Factory Template

```python
class MyFactory:
    """Factory for creating my instances."""

    @staticmethod
    def create_instance(**kwargs) -> Any:
        """Create instance with configuration."""
        return Instance(**kwargs)

    @staticmethod
    def validate_config(config: Dict) -> bool:
        """Validate configuration."""
        return True

# Usage
instance = MyFactory.create_instance(param="value")
```

---

## Usage Guidelines

### When to Use Which Pattern

| Situation | Pattern |
|-----------|---------|
| Simple gateway (< 50 routes) | GATE-PY-UG-01 (SimpleDomainGateway) |
| Complex routing needs | GATE-PY-UG-02 (DISPATCH pattern) |
| Stateful operations | LESS-PY-UG-01 (mutable gateway) |
| Stateless operations | DEC-PY-UG-01 (frozen dataclass) |
| Factory creation | DEC-PY-UG-02 (static methods) |

### Performance Guidelines

| Routes | Recommended Pattern |
|--------|-------------------|
| < 10 | Either (if-elif acceptable) |
| 10-50 | DISPATCH pattern |
| > 50 | DISPATCH pattern (significant speedup) |

---

## Compliance

All files comply with SIMA file standards:
- Maximum: 350 lines per file
- Encoding: UTF-8
- Line endings: LF
- Format: Markdown with Python code examples

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-31 | Initial index creation |

---

**END OF INDEX**

**Total Entries:** 5 (2 decisions, 2 patterns, 1 lesson)
**Total Lines:** 1,750 (350 per file)
**Source:** EE codebase analysis + UG Architecture Guide
