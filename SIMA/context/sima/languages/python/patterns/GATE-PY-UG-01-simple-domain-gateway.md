# GATE-PY-UG-01: SimpleDomainGateway Implementation

**Category:** Implementation Pattern
**Status:** Active
**Source:** EE Codebase Analysis
**Created:** 2025-12-31
**Priority:** High

---

## SUMMARY

SimpleDomainGateway is a convenience base class for Python domain gateways that uses a dispatch dictionary for O(1) route routing. Provides simple registration pattern and eliminates repetitive if-else chains.

**Pattern:** Dictionary-based dispatch with handler registration
**Benefits:** O(1) lookup, cleaner code, easier extension
**Use Case:** Simple domain gateways with static routes

---

## THE PROBLEM

### Traditional Gateway Implementation

```python
class ConfigGateway:
    """Configuration gateway with repetitive if-else chains."""

    def execute(self, route: str, payload: dict) -> Any:
        if route == "config.get":
            return self._get_config(payload)
        elif route == "config.set":
            return self._set_config(payload)
        elif route == "config.delete":
            return self._delete_config(payload)
        elif route == "config.get_all":
            return self._get_all_config(payload)
        elif route == "config.reload":
            return self._reload_config(payload)
        elif route == "config.list_all":
            return self.list_all()
        else:
            raise ValueError(f"Unknown route: {route}")
```

**Issues:**
- Repetitive if-elif chains
- O(n) lookup performance
- Hard to extend
- Violates Open/Closed Principle
- Difficult to maintain

---

## THE PATTERN

### SimpleDomainGateway Base Class

```python
from typing import Any, Dict, Callable, Optional
from dataclasses import dataclass

class SimpleDomainGateway:
    """Base class for domain gateways using dispatch dictionary.

    Provides O(1) route dispatch through handler registration.
    Eliminates repetitive if-elif chains.
    """

    def __init__(self):
        """Initialize gateway with empty dispatch table."""
        self._handlers: Dict[str, Callable] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register route handlers. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement _register_handlers")

    def _register(self, route: str, handler: Callable) -> None:
        """Register a route handler.

        Args:
            route: Route string (e.g., "config.get")
            handler: Function to call for route
        """
        self._handlers[route] = handler

    def execute(self, route: str, payload: dict) -> Any:
        """Execute operation by routing to handler.

        Args:
            route: Operation route (e.g., "config.get")
            payload: Operation parameters

        Returns:
            Handler result

        Raises:
            ValueError: If route not found
        """
        if route not in self._handlers:
            raise ValueError(f"Unknown route: {route}")

        handler = self._handlers[route]
        return handler(payload)

    def list_all(self) -> Dict[str, Any]:
        """List all available routes."""
        return {
            "routes": list(self._handlers.keys())
        }
```

### Using the Pattern

```python
@dataclass(frozen=True)
class ConfigGateway(SimpleDomainGateway):
    """Configuration gateway using dispatch pattern."""

    config_manager: Optional[Any] = None

    def _register_handlers(self) -> None:
        """Register all config route handlers."""
        self._register("config.get", self._get_config)
        self._register("config.set", self._set_config)
        self._register("config.delete", self._delete_config)
        self._register("config.get_all", self._get_all_config)
        self._register("config.reload", self._reload_config)
        self._register("config.list_all", lambda p: self.list_all())

    def _get_config(self, payload: dict) -> Any:
        """Get configuration value."""
        key = payload.get("key")
        default = payload.get("default")
        # Implementation
        return f"config_value_for_{key}"

    def _set_config(self, payload: dict) -> bool:
        """Set configuration value."""
        key = payload.get("key")
        value = payload.get("value")
        # Implementation
        return True

    def _delete_config(self, payload: dict) -> bool:
        """Delete configuration value."""
        key = payload.get("key")
        # Implementation
        return True

    def _get_all_config(self, payload: dict) -> Dict[str, Any]:
        """Get all configuration."""
        # Implementation
        return {}

    def _reload_config(self, payload: dict) -> bool:
        """Reload configuration."""
        # Implementation
        return True
```

---

## BENEFITS

### 1. O(1) Lookup Performance

```python
# Traditional: O(n) - checks each condition
if route == "config.get":
    ...
elif route == "config.set":
    ...
elif route == "config.delete":
    ...  # Worse as routes increase

# Dispatch: O(1) - dictionary lookup
self._handlers[route](payload)  # Fast regardless of route count
```

**Performance Comparison:**
- 10 routes: Negligible difference
- 50 routes: Dispatch ~5x faster
- 100 routes: Dispatch ~10x faster

### 2. Cleaner Code

**Lines of Code Comparison:**

```python
# Traditional if-elif: 20 lines for 5 routes
def execute(self, route: str, payload: dict) -> Any:
    if route == "config.get":
        return self._get_config(payload)
    elif route == "config.set":
        return self._set_config(payload)
    elif route == "config.delete":
        return self._delete_config(payload)
    elif route == "config.get_all":
        return self._get_all_config(payload)
    elif route == "config.reload":
        return self._reload_config(payload)
    else:
        raise ValueError(f"Unknown route: {route}")

# Dispatch pattern: 6 lines for 5 routes
def _register_handlers(self) -> None:
    self._register("config.get", self._get_config)
    self._register("config.set", self._set_config)
    self._register("config.delete", self._delete_config)
    self._register("config.get_all", self._get_all_config)
    self._register("config.reload", self._reload_config)
```

### 3. Easier Extension

```python
# Adding new route
class ConfigGateway(SimpleDomainGateway):
    def _register_handlers(self) -> None:
        # Existing routes
        self._register("config.get", self._get_config)
        self._register("config.set", self._set_config)

        # New route - just add one line!
        self._register("config.validate", self._validate_config)

    def _validate_config(self, payload: dict) -> bool:
        """Validate configuration (NEW)."""
        # Implementation
        return True
```

### 4. Better Testing

```python
def test_config_gateway():
    gateway = ConfigGateway()

    # Test handler registration
    assert "config.get" in gateway._handlers
    assert "config.set" in gateway._handlers

    # Test execution
    result = gateway.execute("config.get", {"key": "test"})
    assert result == "config_value_for_test"

    # Test unknown route
    try:
        gateway.execute("config.unknown", {})
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Unknown route" in str(e)
```

---

## ADVANCED USAGE

### Dynamic Route Registration

```python
class ConfigGateway(SimpleDomainGateway):
    """Gateway with dynamic route registration."""

    def _register_handlers(self) -> None:
        """Register handlers dynamically."""
        # Core routes
        core_routes = {
            "config.get": self._get_config,
            "config.set": self._set_config,
            "config.delete": self._delete_config,
        }

        # Register all core routes
        for route, handler in core_routes.items():
            self._register(route, handler)

        # Register profile routes
        self._register_profile_routes()

    def _register_profile_routes(self) -> None:
        """Register profile-related routes."""
        profile_routes = {
            "config.get_profile": self._get_profile,
            "config.set_profile": self._set_profile,
            "config.list_profiles": self._list_profiles,
        }

        for route, handler in profile_routes.items():
            self._register(route, handler)
```

### Route Prefixing

```python
class PrefixedGateway(SimpleDomainGateway):
    """Gateway with automatic route prefixing."""

    def __init__(self, prefix: str):
        super().__init__()
        self._prefix = prefix

    def _register(self, route: str, handler: Callable) -> None:
        """Register route with prefix."""
        full_route = f"{self._prefix}.{route}"
        super()._register(full_route, handler)

# Usage
gateway = PrefixedGateway(prefix="config")
gateway._register("get", handler)  # Registers as "config.get"
gateway._register("set", handler)  # Registers as "config.set"
```

### Conditional Registration

```python
class ConfigGateway(SimpleDomainGateway):
    """Gateway with conditional route registration."""

    def __init__(self, config_manager=None, enable_validation=False):
        super().__init__()
        self.config_manager = config_manager
        self.enable_validation = enable_validation

    def _register_handlers(self) -> None:
        """Register handlers based on configuration."""
        # Always register
        self._register("config.get", self._get_config)
        self._register("config.set", self._set_config)

        # Conditional registration
        if self.enable_validation:
            self._register("config.validate", self._validate_config)
            self._register("config.schema", self._get_schema)
```

### Middleware/Interceptors

```python
class LoggingGateway(SimpleDomainGateway):
    """Gateway with logging middleware."""

    def execute(self, route: str, payload: dict) -> Any:
        """Execute with logging."""
        # Before
        print(f"[BEFORE] Executing: {route}")

        # Execute
