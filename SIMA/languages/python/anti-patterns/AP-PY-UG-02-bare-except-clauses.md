# AP-PY-UG-02: Bare Except Clauses

**ID:** AP-PY-UG-02
**Language:** Python
**Platform:** Universal Gateway System (UGS)
**Severity:** High
**Category:** Error Handling
**Status:** Enforced
**Last Updated:** 2025-12-31

---

## OVERVIEW

Using bare `except:` clauses in Python code catches **all exceptions**, including system-exiting exceptions like `SystemExit`, `KeyboardInterrupt`, and `GeneratorExit`. This makes debugging nearly impossible, hides critical errors, and can create unkillable processes.

**Python Anti-Pattern:**
- Catches exceptions that should never be caught
- Hides programming errors and bugs
- Makes debugging extremely difficult
- Violates principle of explicit error handling

---

## THE ANTI-PATTERN

### Wrong Way: Bare Except Clauses

```python
# EE/networking/http_client/http_factory.py

class HttpFactory:
    """HTTP client factory."""

    @staticmethod
    def execute_get(**kwargs):
        """Execute HTTP GET request."""
        try:
            response = requests.get(kwargs['url'], timeout=kwargs.get('timeout'))
            return response.json()
        except:  # ✗ VIOLATION: Bare except catches EVERYTHING
            return None  # Silent failure - no way to know what went wrong


    def execute_post(self, **kwargs):
        """Execute HTTP POST request."""
        try:
            response = requests.post(
                kwargs['url'],
                json=kwargs.get('data'),
                timeout=kwargs.get('timeout')
            )
            return response.json()
        except Exception:  # ✓ Better, but still too broad
            # Logs error but still too generic
            print(f"Error in POST request")
            return None


    def execute_delete(self, **kwargs):
        """Execute HTTP DELETE request."""
        try:
            response = requests.delete(kwargs['url'], timeout=kwargs.get('timeout'))
            return response.status_code
        except:  # ✗ VIOLATION: Catches KeyboardInterrupt, SystemExit, etc.
            pass  # Completely silent - impossible to debug
```

### Why This Is Wrong

1. **Catches System Exceptions:**
   - `KeyboardInterrupt` (Ctrl+C) - Cannot kill the process
   - `SystemExit` - `sys.exit()` won't work
   - `GeneratorExit` - Breaks generator cleanup

2. **Hides Programming Errors:**
   - `NameError` - Typos in variable names
   - `AttributeError` - Wrong attribute access
   - `TypeError` - Wrong type usage
   - `ImportError` - Missing imports

3. **Impossible to Debug:**
   - No error messages
   - No stack traces
   - Silent failures
   - Cannot determine root cause

4. **Violates Python Best Practices:**
   - PEP 8 recommends against bare except
   - Against explicit error handling principle
   - Makes code unpredictable

---

## THE CORRECT PATTERN

### Right Way: Specific Exception Types

```python
# EE/networking/http_client/http_factory.py

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

class HttpFactory:
    """HTTP client factory with proper error handling."""

    def __init__(self, logger=None):
        self._logger = logger

    def execute_get(self, **kwargs):
        """Execute HTTP GET request with specific exception handling."""
        try:
            response = requests.get(
                kwargs['url'],
                timeout=kwargs.get('timeout', 30)
            )
            response.raise_for_status()
            return response.json()

        except Timeout as e:
            # ✓ CORRECT: Handle timeout specifically
            if self._logger:
                self._logger.error(f"Request timeout: {e}")
            raise GatewayError(f"Request timeout: {kwargs['url']}") from e

        except ConnectionError as e:
            # ✓ CORRECT: Handle connection errors specifically
            if self._logger:
                self._logger.error(f"Connection error: {e}")
            raise GatewayError(f"Cannot connect to {kwargs['url']}") from e

        except requests.HTTPError as e:
            # ✓ CORRECT: Handle HTTP errors specifically
            if self._logger:
                self._logger.error(f"HTTP error {e.response.status_code}: {e}")
            raise GatewayError(f"HTTP {e.response.status_code}: {e}") from e

        except ValueError as e:
            # ✓ CORRECT: Handle JSON decode errors
            if self._logger:
                self._logger.error(f"Invalid JSON response: {e}")
            raise GatewayError(f"Invalid JSON from {kwargs['url']}") from e

        except KeyError as e:
            # ✓ CORRECT: Handle missing required parameters
            if self._logger:
                self._logger.error(f"Missing required parameter: {e}")
            raise GatewayError(f"Missing required parameter: {e}") from e


    def execute_post(self, **kwargs):
        """Execute HTTP POST request."""
        try:
            response = requests.post(
                kwargs['url'],
                json=kwargs.get('data'),
                timeout=kwargs.get('timeout', 30)
            )
            response.raise_for_status()
            return response.json()

        except Timeout as e:
            if self._logger:
                self._logger.error(f"POST timeout: {e}")
            raise GatewayError(f"POST timeout: {kwargs['url']}") from e

        except (ConnectionError, requests.HTTPError) as e:
            # ✓ CORRECT: Group related exceptions
            if self._logger:
                self._logger.error(f"POST failed: {e}")
            raise GatewayError(f"POST request failed: {e}") from e

        except ValueError as e:
            if self._logger:
                self._logger.error(f"Invalid JSON: {e}")
            raise GatewayError(f"Invalid JSON response: {e}") from e
```

### Exception Handling Best Practices

#### 1. Catch Specific Exceptions

```python
# ✓ CORRECT: Specific exceptions
try:
    value = int(user_input)
except ValueError as e:
    logger.error(f"Invalid number: {user_input}")
    raise
```

#### 2. Use Exception Hierarchy

```python
# ✓ CORRECT: Catch base exception when appropriate
try:
    response = requests.get(url)
except requests.RequestException as e:
    # Catches all requests exceptions (Timeout, ConnectionError, etc.)
    logger.error(f"Request failed: {e}")
    raise GatewayError(f"Request failed: {e}") from e
```

#### 3. Always Re-raise or Handle Appropriately

```python
# ✓ CORRECT: Re-raise with context
try:
    result = dangerous_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise GatewayError(f"Wrapped error") from e  # Preserve stack trace

# ✓ CORRECT: Handle and return alternative
try:
    result = cache.get(key)
except KeyError:
    # Expected condition - return default
    return default_value

# ✗ WRONG: Silent failure
try:
    result = dangerous_operation()
except:
    pass  # Never do this!
```

#### 4. Use Finally for Cleanup

```python
# ✓ CORRECT: Ensure cleanup happens
def process_file(filepath):
    f = None
    try:
        f = open(filepath, 'r')
        data = f.read()
        return process(data)
    except IOError as e:
        logger.error(f"File error: {e}")
        raise
    finally:
        if f:
            f.close()  # Always executes
```

---

## IMPACT AND CONSEQUENCES

### Development Impact

| Impact | Description | Severity |
|--------|-------------|----------|
| Debugging Impossible | No error information when failures occur | Critical |
| Hidden Bugs | Programming errors silently caught | Critical |
| Unkillable Processes | Ctrl+C doesn't work | High |
| Unpredictable Behavior | Cannot determine what went wrong | High |
| Maintenance Nightmare | Next developer cannot fix issues | Medium |

### Runtime Consequences

1. **Process Cannot Be Killed:**
   ```python
   # ✗ This process cannot be stopped with Ctrl+C
   try:
       while True:
           process_data()
   except:  # Catches KeyboardInterrupt
       continue  # Never exits
   ```

2. **SystemExit Doesn't Work:**
   ```python
   # ✗ sys.exit() won't terminate
   try:
       main_loop()
   except:  # Catches SystemExit
       print("Something went wrong")
       main_loop()  # Continues anyway
   ```

3. **Silent Failures:**
   ```python
   # ✗ No way to know operation failed
   def save_config(config):
       try:
           with open('config.json', 'w') as f:
               f.write(json.dumps(config))
       except:
           pass  # File write failed silently - data lost!
   ```

4. **Hidden Programming Errors:**
   ```python
   # ✗ Typos and bugs hidden
   def calculate(data):
       try:
           result = proces_data(data)  # Typo: proces vs process
           return result
       except:
           return None  # NameError silently caught
   ```

---

## EXCEPTION HIERARCHY

### Python Exception Tree

```
BaseException
├── SystemExit        # ✗ Don't catch in normal code
├── KeyboardInterrupt # ✗ Don't catch in normal code
├── GeneratorExit     # ✗ Don't catch in normal code
└── Exception         # ✓ Catch this or subclasses
    ├── StopIteration
    ├── ArithmeticError
    │   ├── FloatingPointError
    │   ├── OverflowError
    │   └── ZeroDivisionError
    ├── AssertionError
    ├── AttributeError
    ├── BufferError
    ├── EOFError
    ├── ImportError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── MemoryError
    ├── NameError
    ├── OSError
    │   ├── FileNotFoundError
    │   └── PermissionError
    ├── ReferenceError
    ├── RuntimeError
    ├── SyntaxError
    ├── TypeError
    ├── ValueError
    └── Warning
```

### Rule: Only Catch `Exception` or Its Subclasses

```python

---
**Entry ID:** AP-PY-UG-02
**Lines:** 345
**Status:** Active - Enforced
**Next Review:** 2026-01-31
