# DEC-PY-02: Future Annotations Import

**Status:** Accepted
**Date:** 2025-12-31
**Context:** Python type hinting best practices
**Applies to:** All Python modules using type hints

---

## Decision

Always use `from __future__ import annotations` at the top of every Python module that uses type hints.

## Rationale

### Benefits

1. **Forward References**: Type hints can reference types defined later in the file without string quotes
2. **PEP 563 Compliance**: Adopts postponed evaluation of annotations (standard in Python 3.11+)
3. **Cleaner Code**: Eliminates need for `TYPE_CHECKING` imports and string quoting
4. **Performance**: Annotations stored as strings, not evaluated at import time
5. **Future-Proof**: Prepares codebase for Python 3.11+ behavior where this is default

### Comparison

**Without `from __future__ import annotations`:**
```python
from typing import List, Optional, TYPE_CHECKING

# Need TYPE_CHECKING for forward references
if TYPE_CHECKING:
    from my_module import SomeClass

# Need string quotes for forward references
def process(data: List['SomeClass']) -> Optional['OtherClass']:
    pass
```

**With `from __future__ import annotations`:**
```python
from __future__ import annotations
from typing import List, Optional

# Direct references, no quotes needed
def process(data: List[SomeClass]) -> Optional[OtherClass]:
    pass

class OtherClass:
    pass  # Can reference before definition
```

## Implementation

### Module Template

```python
"""Module docstring describing purpose."""

# 1. Future imports FIRST (before any other imports)
from __future__ import annotations

# 2. Standard library imports
import logging
from typing import Any, Dict, Optional, Protocol

# 3. Third-party imports
# (if any)

# 4. Local imports
from my_package.other_module import SomeClass
```

### Forward References

```python
from __future__ import annotations

# Can reference types before they're defined
class Node:
    def __init__(self, value: int) -> None:
        self.value = value
        self.children: list[Node] = []  # Forward reference works
        self.parent: Optional[Node] = None  # Forward reference works

    def add_child(self, child: Node) -> None:
        self.children.append(child)
        child.parent = self
```

### Mutual Recursion

```python
from __future__ import annotations

# Types can reference each other
class ClassA:
    def __init__(self) -> None:
        self.b_ref: Optional[ClassB] = None

class ClassB:
    def __init__(self) -> None:
        self.a_ref: Optional[ClassA] = None
```

### Type Aliases

```python
from __future__ import annotations
from typing import Dict, List

# Complex type aliases work without quotes
ConfigDict = dict[str, dict[str, Any]]
DataProcessor = callable[[dict[str, Any]], list[str]]

class DataPipeline:
    def __init__(self, config: ConfigDict) -> None:
        self.config = config
```

### Protocols and Callbacks

```python
from __future__ import annotations
from typing import Protocol, Callable

class Handler(Protocol):
    """Protocol with forward reference."""
    def handle(self, event: Event) -> Response: ...

class Event:
    pass

class Response:
    pass

# Callback type with forward references
EventHandler = Callable[[Event], Response]
```

## Common Patterns

### Pattern 1: Class Methods Returning Self

```python
from __future__ import annotations

class Builder:
    def add_item(self, item: str) -> Builder:
        """Return self for chaining."""
        # Without future annotations, would need:
        # def add_item(self, item: str) -> 'Builder':
        return self
```

### Pattern 2: Decorators

```python
from __future__ import annotations
from typing import Callable, TypeVar

T = TypeVar('T')

def my_decorator(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator with preserved return type."""
    def wrapper(*args: Any) -> T:
        return func(*args)
    return wrapper

@my_decorator
def get_value() -> int:
    return 42
```

### Pattern 3: Generic Classes

```python
from __future__ import annotations
from typing import TypeVar, Generic

T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = T

    def get(self) -> T:
        return self.value

    def set(self, value: T) -> Container[T]:
        self.value = value
        return self
```

### Pattern 4: Dataclasses

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class TreeNode:
    value: int
    left: Optional[TreeNode] = None
    right: Optional[TreeNode] = None

# Works without string quotes
```

## Migration Guide

### Before (String Quotes)

```python
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models import User

class UserService:
    def get_user(self, user_id: int) -> Optional['User']:
        # Implementation
        pass

    def list_users(self) -> List['User']:
        # Implementation
        pass
```

### After (Future Annotations)

```python
from __future__ import annotations
from typing import Optional, List
from models import User  # Direct import

class UserService:
    def get_user(self, user_id: int) -> Optional[User]:
        # Implementation
        pass

    def list_users(self) -> List[User]:
        # Implementation
        pass
```

## Compatibility

### Python Version Support

| Python Version | Required | Behavior |
|---------------|----------|----------|
| 3.7+ | Yes | Enables PEP 563 behavior |
| 3.11+ | Optional | Default behavior (can omit import) |

### Type Checkers

**mypy:**
```bash
# Requires mypy 0.900+ for full support
mypy --python-version 3.7 my_module.py
```

**pyright:**
```json
// pyrightconfig.json
{
  "pythonVersion": "3.7",
  "typeCheckingMode": "strict"
}
```

## Caveats and Limitations

### 1. Runtime Access to Annotations

```python
from __future__ import annotations

class MyClass:
    value: int

# Annotations are strings, not types
print(MyClass.__annotations__)
# Output: {'value': 'int'}

# If you need runtime types:
import typing
typing.get_type_hints(MyClass)
# Output: {'value': <class 'int'>}
```

### 2. Type Variables

```python
from __future__ import annotations
from typing import TypeVar

# TypeVar must still be created with string
T = TypeVar('T', bound='MyClass')  # OK
# NOT: T = TypeVar(T, bound=MyClass)  # Error
```

### 3. Class Creation in Annotations

```python
from __future__ import annotations

# This works - type is string at runtime
def get_items() -> list[dict[str, int]]:
    return [{"key": 1}]
```

## Best Practices

### 1. Import Order

```python
# CORRECT
from __future__ import annotations  # Always first

import sys
from typing import Any
```

### 2. All or Nothing

```python
# Use in ALL modules with type hints
# Don't mix modules with and without it in same package
```

### 3. Combine with Protocol

```python
from __future__ import annotations
from typing import Protocol

class Factory(Protocol):
    """Forward references work with Protocol."""
    def create(self) -> MyClass: ...

class MyClass:
    pass
```

### 4. Remove TYPE_CHECKING

```python
# BEFORE
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from module import Type

def func(arg: 'Type') -> None:
    pass

# AFTER
from __future__ import annotations
from module import Type

def func(arg: Type) -> None:
    pass
```

## Cross-References

- **DEC-PY-01**: Required for clean Protocol-based type hints
- **Generic Principles**: Don't Repeat Yourself (DRY), reduce string quoting boilerplate

## Examples from EE Codebase

**Location:** `d:\Code\Project\EE\universal_gateway\gateway.py`

```python
"""
Universal Gateway (UG) - Central entry point for all EE operations.
"""

from __future__ import annotations  # Line 1: Future import
from typing import Any, Dict, Callable, Optional, Protocol
import logging

class LoggerFactory(Protocol):
    """Protocol for logger factory functions.

    The logger factory creates logger instances for components.
    """
    def __call__(self, name: str) -> logging.Logger: ...

class UniversalGateway:
    def __init__(
        self,
        logger_factory: LoggerFactory,  # Forward reference works
        metrics_factory: MetricsFactory,
    ) -> None:
        self._logger_factory: LoggerFactory = logger_factory
```

**Location:** `d:\Code\Project\EE\universal_gateway\domain_gateway.py`

```python
"""
Domain Gateway - Base class for all domain gateways in UG architecture.
"""

from __future__ import annotations  # Line 1: Future import
from typing import Any, Dict, Callable, Optional, Protocol
from abc import ABC, abstractmethod

class DomainGateway(ABC):
    """Base class for all domain gateways in UG architecture."""

    def __init__(
        self,
        domain_name: str,
        get_logger: LoggerFactory,
        get_metrics: MetricsFactory,
        call_operation: OperationCaller,
    ) -> None:
        # No string quotes needed for forward references
        self._call_operation: OperationCaller = call_operation
```

**Location:** `d:\Code\Project\EE\operations\object_pool\object_pool_factory.py`

```python
"""
Object Pool Factory - Operations Domain
"""

from __future__ import annotations  # Line 1: Future import
from typing import Any, Dict, Optional, Callable, List

class ObjectPoolFactory:
    @classmethod
    def get_instance(
        cls,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ) -> ObjectPoolFactory:  # Forward reference to same class
        """Get singleton instance of pool factory."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(logger, metrics, call_operation)
        return cls._instance
```

## Enforcement

### Pre-Commit Hook

```python
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-future-annotations
        name: Check for future annotations import
        entry: bash -c 'grep -L "from __future__ import annotations" "$@" || true'
        language: system
        files: ^.*\.py$
```

### Linter Rule

```python
# flake8 future annotations plugin
# Selects F401 for missing future annotations
```

## References

- PEP 563: Postponed Evaluation of Annotations
- PEP 585: Type Hinting Generics In Standard Collections
- PEP 586: Literal Types
- PEP 604: Allow writing union types as X | Y
- https://docs.python.org/3/whatsnew/3.7.html#pep-563-postponed-evaluation-of-annotations
