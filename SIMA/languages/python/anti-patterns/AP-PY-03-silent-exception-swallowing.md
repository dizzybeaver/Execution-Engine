# AP-PY-03: Silent Exception Swallowing

**Category:** Python Anti-Pattern
**Severity:** High
**Detection:** Static analysis, code review

---

## Overview

Catching exceptions and silently continuing without logging, re-raising, or proper handling. This hides errors and makes debugging extremely difficult.

## Anti-Pattern

### Basic Silent Swallowing

```python
# ANTI-PATTERN - Silent exception swallowing
try:
    result = risky_operation()
except Exception:
    pass  # Error completely hidden!

# Variations
try:
    result = risky_operation()
except:
    pass  # Even worse - bare except!

try:
    result = risky_operation()
except Exception:
    return None  # Returns None, caller doesn't know why
```

### Conditional Silent Swallowing

```python
# ANTI-PATTERN - Conditional but still silent
try:
    result = risky_operation()
except Exception as e:
    if debug_mode:
        print(e)
    # Otherwise, completely hidden
```

### Swallowing in Loops

```python
# ANTI-PATTERN - Silent failures in loops
for item in items:
    try:
        process(item)
    except Exception:
        pass  # Which items failed? Why? No way to know!
```

### Swallowing with Comment

```python
# ANTI-PATTERN - Comment doesn't make it better
try:
    result = risky_operation()
except Exception:
    pass  # Ignore errors - THIS IS STILL BAD
```

## Correct Patterns

### Pattern 1: Log with Context

```python
# GOOD - Log the exception with context
import logging

logger = logging.getLogger(__name__)

try:
    result = risky_operation()
except Exception as e:
    logger.error(
        f"Failed to execute risky_operation: {e}",
        exc_info=True  # Includes full traceback
    )
    # Re-raise if operation is critical
    raise

# Or for non-critical operations
try:
    result = risky_operation()
except Exception as e:
    logger.warning(f"Non-critical failure in risky_operation: {e}")
    return default_value
```

### Pattern 2: Re-raise with Context

```python
# GOOD - Re-raise with additional context
class OperationError(Exception):
    """Base exception for operation errors."""
    pass

try:
    result = risky_operation()
except ValueError as e:
    # Preserve original exception with context
    raise OperationError(
        f"Failed to process value in risky_operation: {e}"
    ) from e

# Or simply re-raise
try:
    result = risky_operation()
except Exception:
    logger.error("risky_operation failed, re-raising")
    raise  # Re-raises same exception with traceback
```

### Pattern 3: Handle Specific Exceptions

```python
# GOOD - Handle only specific, expected exceptions
import json

try:
    data = json.loads(json_string)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {e}")
    return None  # Expected failure mode
# Other exceptions will propagate

try:
    config = read_config(path)
except FileNotFoundError as e:
    logger.warning(f"Config file not found, using defaults: {path}")
    config = default_config
except PermissionError as e:
    logger.error(f"Permission denied reading config: {path}")
    raise  # Re-raise - this is critical
```

### Pattern 4: Exception Aggregation in Loops

```python
# GOOD - Aggregate errors from loop iterations
from typing import List

errors: List[Exception] = []
results = []

for item in items:
    try:
        result = process(item)
        results.append(result)
    except Exception as e:
        logger.error(f"Failed to process item {item}: {e}")
        errors.append(e)

# After loop, report aggregate status
if errors:
    logger.error(f"Failed to process {len(errors)} out of {len(items)} items")
    raise Exception(
        f"Processing completed with {len(errors)} errors: "
        f"{len(results)} succeeded, {len(errors)} failed"
    )

return results
```

### Pattern 5: Context Manager Pattern

```python
# GOOD - Use context managers for cleanup
class OperationContext:
    """Context manager for operation with proper error handling."""

    def __enter__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting operation")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.error(
                f"Operation failed: {exc_val}",
                exc_info=(exc_type, exc_val, exc_tb)
            )
            # Don't suppress - return False to propagate
            return False
        self.logger.info("Operation completed successfully")
        return False

# Usage
with OperationContext():
    risky_operation()
```

## Examples from EE Codebase

### Good Example 1: Logging with Context

```python
# Location: d:\Code\Project\EE\operations\object_pool\object_pool_factory.py

def _create_object(self) -> Optional[PoolEntry]:
    """Create new pool entry."""
    if self.config.factory_func is None:
        return None

    try:
        obj = self.config.factory_func()
        entry = PoolEntry(obj=obj)
        self._stats.total_created += 1
        return entry
    except Exception as e:
        # GOOD - Logs error with context
        logging.getLogger(__name__).error(
            f"Failed to create object for pool {self.name}: {e}"
        )
        return None  # Returns None for graceful degradation
```

### Good Example 2: Re-raising with Context

```python
# Location: d:\Code\Project\EE\cli\unified_cli.py

def main(args):
    """Main CLI entry point."""
    try:
        # CLI logic
        return 0
    except CLIGatewayError as e:
        # GOOD - Handle expected error
        renderer = CLIOutputRenderer(json_output=False)
        renderer.render_error(e)
        return 1
    except KeyboardInterrupt:
        # GOOD - Handle user interrupt
        print("\nInterrupted by user")
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        # GOOD - Log and display unexpected errors
        renderer = CLIOutputRenderer(json_output=False)
        renderer.render_error(e)
        logger = logging.getLogger(__name__)
        logger.exception("Unexpected error in CLI")  # exc_info=True
        return 1
```

### Good Example 3: Specific Exception Handling

```python
# Location: d:\Code\Project\EE\universal_gateway\gateway.py

def execute_operation(
    self,
    domain: str,
    interface: str,
    operation: str,
    **kwargs: Any,
) -> Any:
    """Execute operation using UG pattern."""
    # Validate domain exists
    if domain not in self._domains:
        available = list(self._domains.keys())
        # GOOD - Raise specific exception with context
        raise DomainNotFoundError(
            f"Unknown domain: '{domain}'. "
            f"Available domains: {available}"
        )

    # Execute operation
    try:
        result = gateway.execute_domain_operation(
            interface=interface,
            operation=operation,
            **kwargs
        )
        return result
    except Exception as e:
        # GOOD - Wrap with context, preserve original
        raise InvalidOperationError(
            f"Failed to execute operation "
            f"'{domain}.{interface}.{operation}()': {e}"
        ) from e
```

### Anti-Pattern Example (from scanner)

```python
# Location: d:\Code\Project\EE\scanner\scanner_gateway.py
# BAD - Silent exception swallowing
try:
    return execute("config.get", {"key": key, "default": default})
except Exception:
    # ANTI-PATTERN - Silent fallback
    # Fallback to default if gateway not available
    return default
```

**Better version:**
```python
# GOOD - Log before fallback
try:
    return execute("config.get", {"key": key, "default": default})
except Exception as e:
    # GOOD - Log why we're falling back
    logger.warning(
        f"Gateway unavailable for config.get('{key}'), "
        f"using default: {default}. Error: {e}"
    )
    return default
```

## Detection Rules

### Static Analysis

```python
# pylint: W0702 - No exception type specified
# pylint: W0703 - Catching too general exception
# pylint: W0718 - Catching too general exception (Python 3.0+)

# pyflakes
# bare-except

# bandit
# B110: Try, Except, Pass detected.
```

### Linter Configuration

```ini
# .pylintrc
[DESIGN]
# Warn about bare except
bare-except=bare-except

# Warn about catching Exception
broad-except=broad-except

# Warn about catching BaseException
base-except=base-except

[LOGGING]
# Check for logging in except blocks
logging-not-lazy=logging-not-lazy
```

### Pre-commit Hook

```python
#!/usr/bin/env python3
"""Check for silent exception swallowing."""

import ast
import sys

class ExceptionSwallowingChecker(ast.NodeVisitor):
    """AST visitor to find silent exception swallowing."""

    def __init__(self):
        self.violations = []

    def visit_ExceptHandler(self, node):
        """Check exception handler for silent swallowing."""
        if not node.body:
            # Empty except block
            self.violations.append((
                node.lineno,
                "Empty exception handler"
            ))
        elif len(node.body) == 1:
            stmt = node.body[0]
            if isinstance(stmt, (ast.Pass, ast.Expr)):
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                    if not stmt.value.value:
                        self.violations.append((
                            node.lineno,
                            "Silent exception swallowing with pass/empty statement"
                        ))

        self.generic_visit(node)

def check_file(filepath):
    """Check Python file for silent exception swallowing."""
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read(), filename=filepath)

    checker = ExceptionSwallowingChecker()
    checker.visit(tree)

    return checker.violations

if __name__ == "__main__":
    violations = check_file(sys.argv[1])
    for lineno, message in violations:
        print(f"{sys.argv[1]}:{lineno}: {message}")
    sys.exit(len(violations))
```

## Best Practices Summary

### DO:
1. **Always log exceptions** with context (logger.error with exc_info=True)
2. **Re-raise critical errors** after logging
3. **Handle specific exceptions** that you expect and can handle
4. **Use exception chaining** (`raise ... from e`) to preserve traceback
5. **Aggregate errors** in loops rather than swallowing them
6. **Document why** an exception is intentionally not propagated

### DON'T:
1. **Use bare `except:`** - catches everything including KeyboardInterrupt
2. **Use `except Exception: pass`** - completely hides errors
3. **Return None/False without logging** - caller doesn't know why it failed
4. **Swallow exceptions in loops** - you lose all error information
5. **Use comments to justify** - logging is better

## Exception Handling Strategy

### Decision Tree

```
Exception occurs
    │
    ├─ Can this error be handled locally?
    │   ├─ Yes → Is it a specific, expected error?
    │   │   ├─ Yes → Handle it, log warning, return default/continue
    │   │   └─ No → Re-raise with context
    │   └─ No → Re-raise with context
    │
    ├─ Is this operation critical?
    │   ├─ Yes → Log error, re-raise
    │   └─ No → Log error, return default/continue
    │
    └─ In loop/iteration?
        ├─ Yes → Aggregate errors, report at end
        └─ No → Handle immediately
```

## Cross-References

- **Generic Principles**: Fail Fast, Error Handling, Defensive Programming
- **DEC-PY-01**: Use Protocol-based exceptions for type safety
- **LESS-PY-02**: Document exception handling in docstrings

## References

- PEP 3134: Exception Chaining and Embedded Tracebacks
- Python: Catching Exceptions - Best Practices
- "Mastering Object-Oriented Python" - Chapter on Error Handling
- https://docs.python.org/3/tutorial/errors.html
- https://docs.python.org/3/library/exceptions.html
