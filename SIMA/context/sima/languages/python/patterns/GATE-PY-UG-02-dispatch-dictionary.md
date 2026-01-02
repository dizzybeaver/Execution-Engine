# GATE-PY-UG-02: DISPATCH Dictionary Pattern (Python)

**Category:** Implementation Pattern
**Status:** Active
**Source:** EE Codebase Analysis
**Created:** 2025-12-31
**Priority:** High

---

## SUMMARY

DISPATCH pattern uses Python dictionary for O(1) route-to-handler mapping. Eliminates if-elif chains, provides constant-time lookup, and enables dynamic handler registration.

**Pattern:** Dictionary mapping routes to callable handlers
**Benefits:** O(1) lookup, dynamic registration, cleaner code
**Use Case:** All gateways requiring efficient routing

---

## THE PROBLEM

### Inefficient if-elif Chains

```python
# ❌ BAD: O(n) lookup with repetitive chains
def execute_operation(route: str, payload: dict) -> Any:
    if route == "config.get":
        return _get_config(payload)
    elif route == "config.set":
        return _set_config(payload)
    elif route == "config.delete":
        return _delete_config(payload)
    elif route == "security.auth.authenticate":
        return _authenticate(payload)
    elif route == "security.encrypt":
        return _encrypt(payload)
    elif route == "security.decrypt":
        return _decrypt(payload)
    # ... 40 more routes
    else:
        raise ValueError(f"Unknown route: {route}")
```

**Issues:**
- O(n) time complexity
- Repetitive conditional logic
- Difficult to extend
- Hard to maintain
- Error-prone

---

## THE PATTERN

### Basic DISPATCH Dictionary

```python
from typing import Any, Dict, Callable

# Dispatch dictionary: route -> handler
DISPATCH: Dict[str, Callable[[dict], Any]] = {
    # Config routes
    "config.get": _get_config,
    "config.set": _set_config,
    "config.delete": _delete_config,
    "config.get_all": _get_all_config,

    # Security routes
    "security.auth.authenticate": _authenticate,
    "security.encrypt": _encrypt,
    "security.decrypt": _decrypt,
    "security.hash": _hash,
}

def execute_operation(route: str, payload: dict) -> Any:
    """Execute operation using dispatch dictionary.

    Args:
        route: Operation route (e.g., "config.get")
        payload: Operation parameters

    Returns:
        Handler result

    Raises:
        ValueError: If route not found
    """
    if route not in DISPATCH:
        raise ValueError(f"Unknown route: {route}")

    handler = DISPATCH[route]
    return handler(payload)
```

### Handler Implementation

```python
def _get_config(payload: dict) -> Any:
    """Get configuration value."""
    key = payload.get("key")
    default = payload.get("default")
    # Implementation
    return f"config_value_for_{key}"

def _set_config(payload: dict) -> bool:
    """Set configuration value."""
    key = payload.get("key")
    value = payload.get("value")
    # Implementation
    return True

def _authenticate(payload: dict) -> Dict[str, Any]:
    """Authenticate user."""
    credentials = payload.get("credentials")
    # Implementation
    return {"authenticated": True, "user": "test_user"}
```

---

## BENEFITS

### 1. O(1) Lookup Performance

```python
# Traditional: O(n) - checks each condition
def execute_ifelif(route: str, payload: dict) -> Any:
    if route == "route1":
        return handler1(payload)
    elif route == "route2":
        return handler2(payload)
    # ... 98 more checks
    elif route == "route100":
        return handler100(payload)
    # Average: 50 comparisons

# Dispatch: O(1) - dictionary lookup
def execute_dispatch(route: str, payload: dict) -> Any:
    return DISPATCH[route](payload)
# Average: 1 lookup, constant time
```

**Performance Comparison:**

| Routes | if-elif (avg) | Dispatch (avg) | Speedup |
|--------|---------------|----------------|---------|
| 10 | 5 | 1 | 5x |
| 50 | 25 | 1 | 25x |
| 100 | 50 | 1 | 50x |

### 2. Cleaner Code

**Lines of Code for 50 Routes:**

```python
# if-elif: ~150 lines
def execute(route, payload):
    if route == "route1":
        return handler1(payload)
    elif route == "route2":
        return handler2(payload)
    # ... 46 more lines
    elif route == "route50":
        return handler50(payload)
    else:
        raise ValueError(f"Unknown: {route}")

# Dispatch: ~52 lines
DISPATCH = {
    "route1": handler1,
    "route2": handler2,
    # ... 48 more lines
    "route50": handler50,
}

def execute(route, payload):
    if route not in DISPATCH:
        raise ValueError(f"Unknown: {route}")
    return DISPATCH[route](payload)
```

### 3. Dynamic Registration

```python
# Register new routes at runtime
def register_route(route: str, handler: Callable) -> None:
    """Register new route handler."""
    DISPATCH[route] = handler

# Usage
register_route("config.new_route", new_handler)
```

### 4. Easy Testing

```python
def test_dispatch_routing():
    # Test handler registration
    assert "config.get" in DISPATCH
    assert DISPATCH["config.get"] == _get_config

    # Test execution
    result = execute_operation("config.get", {"key": "test"})
    assert result == "config_value_for_test"

    # Test unknown route
    try:
        execute_operation("unknown.route", {})
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Unknown route" in str(e)
```

---

## ADVANCED PATTERNS

### 1. Nested Dispatch

```python
# Hierarchical dispatch by domain
DOMAIN_DISPATCH: Dict[str, Dict[str, Callable]] = {
    "config": {
        "get": _get_config,
        "set": _set_config,
        "delete": _delete_config,
    },
    "security": {
        "auth.authenticate": _authenticate,
        "encrypt": _encrypt,
        "decrypt": _decrypt,
    },
    "logging": {
        "log.info": _log_info,
        "log.error": _log_error,
    },
}

def execute_nested(route: str, payload: dict) -> Any:
    """Execute using nested dispatch."""
    parts = route.split(".", 1)

    if len(parts) < 2:
        raise ValueError(f"Invalid route: {route}")

    domain, operation = parts

    if domain not in DOMAIN_DISPATCH:
        raise ValueError(f"Unknown domain: {domain}")

    domain_handlers = DOMAIN_DISPATCH[domain]

    if operation not in domain_handlers:
        raise ValueError(f"Unknown operation: {operation}")

    handler = domain_handlers[operation]
    return handler(payload)
```

### 2. Wildcard Matching

```python
import fnmatch

class WildcardDispatcher:
    """Dispatcher with wildcard route matching."""

    def __init__(self):
        self.routes: Dict[str, Callable] = {}

    def register(self, route_pattern: str, handler: Callable) -> None:
        """Register route with wildcard support."""
        self.routes[route_pattern] = handler

    def dispatch(self, route: str, payload: dict) -> Any:
        """Dispatch using wildcard matching."""
        # Try exact match first
        if route in self.routes:
            return self.routes[route](payload)

        # Try wildcard match
        for pattern, handler in self.routes.items():
            if fnmatch.fnmatch(route, pattern):
                return handler(payload)

        raise ValueError(f"No match for route: {route}")

# Usage
dispatcher = WildcardDispatcher()
dispatcher.register("config.*", config_handler)  # Wildcard
dispatcher.register("security.auth.*", auth_handler)  # Wildcard
dispatcher.register("logging.log.info", specific_handler)  # Exact

result = dispatcher.dispatch("config.get", payload)  # Matches config.*
result = dispatcher.dispatch("config.set", payload)  # Matches config.*
```

### 3. Middleware Chain

```python
class Dispatcher:
    """Dispatcher with middleware support."""

    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []

    def use(self, middleware: Callable) -> None:
        """Add middleware."""
        self.middleware.append(middleware)

    def register(self, route: str, handler: Callable) -> None:
        """Register route handler."""
        self.handlers[route] = handler

    def dispatch(self, route: str, payload: dict) -> Any:
        """Dispatch with middleware chain."""
        if route not in self.handlers:
            raise ValueError(f"Unknown route: {route}")

        # Build middleware chain
        handler = self.handlers[route]
        for mw in reversed(self.middleware):
            handler = lambda p, h=handler, m=mw: m(p, h)

        return handler(payload)

# Middleware functions
def logging_middleware(payload, next_handler):
    """Log before and after."""
    print(f"[BEFORE] {payload}")
    result = next_handler(payload)
    print(f"[AFTER] {result}")
    return result

def timing_middleware(payload, next_handler):
    """Time execution."""
    import time
    start = time.time()
    result = next_handler(payload)
    elapsed = time.time() - start
    print(f"[TIMING] {elapsed:.3f}s")
    return result

# Usage
dispatcher = Dispatcher()
dispatcher.use(logging_middleware)
dispatcher.use(timing_middleware)
dispatcher.register("config.get", _get_config)
