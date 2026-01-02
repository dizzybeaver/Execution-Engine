# AP-EE-08: Unsafe Pooling

**Category:** Anti-Pattern
**Type:** Concurrency Pattern
**Severity:** HIGH
**Scope:** EE Object Pooling
**REF-ID:** AP-EE-08
**Date:** 2025-12-31
**Status:** Active (EE 2.1 - FORBIDDEN)

---

## Overview

**Unsafe object pooling causes race conditions, data corruption, and unpredictable behavior**. EE 2.1 requires all pools to be safe, deterministic, and free of shared mutable state.

---

## The Anti-Pattern

### ❌ FORBIDDEN: Unsafe Pooling

```python
# ❌ WRONG - Unsafe pooling with shared mutable state
class UnsafeInterface:
    def __init__(self):
        self._pool = []  # Shared state across instances
        self._cache = {}  # Mutable state in pool

    def _get_from_pool(self):
        if self._pool:
            obj = self._pool.pop()
            obj.last_used = datetime.now()  # ❌ Mutating shared object
            return obj
        return Factory()
```

**Problems:**
1. Shared mutable state in pooled objects
2. Non-deterministic pool behavior
3. Race conditions in concurrent access
4. Objects carry state between uses
5. Unpredictable behavior

---

## The Correct Pattern (EE 2.1)

### ✅ REQUIRED: Safe, Deterministic Pooling

```python
# ✅ CORRECT - Safe pooling
class SafeInterface:
    def __init__(self, factory_class, max_pool_size=10):
        self._factory_class = factory_class
        self._pool = []
        self._max_pool_size = max_pool_size

    def _get_from_pool(self):
        if self._pool:
            obj = self._pool.pop()  # ✅ Get clean object
            return obj
        return self._factory_class()  # ✅ Or create new

    def _return_to_pool(self, obj):
        if len(self._pool) < self._max_pool_size:
            self._pool.append(obj)  # ✅ Return to pool
        # Pool full, object will be GC'd

# Factory must be stateless
class StatelessFactory:
    def __init__(self, **deps):
        self._deps = deps
        # ✅ NO mutable instance variables

    def process(self, data):
        # ✅ All state passed as parameters
        # ✅ NO stored state between calls
        result = do_work(data)
        return result
```

**Benefits:**
- No shared mutable state
- Deterministic behavior
- Thread-safe for read operations
- Predictable performance
- Easy to reason about

---

## Pooling Safety Rules

### ✅ Safe Pooling Practices:

1. **Stateless Pooled Objects**
   ```python
   class GoodFactory:
       def __init__(self, logger, metrics):
           self._logger = logger
           self._metrics = metrics
           # ✅ Only immutable deps
   ```

2. **Clean State Between Uses**
   ```python
   def _return_to_pool(self, obj):
       # ✅ Reset any state (if object has any)
       obj.reset()
       if len(self._pool) < self._max_size:
           self._pool.append(obj)
   ```

3. **Deterministic Pool Sizes**
   ```python
   # ✅ Explicit max size
   self._max_pool_size = 10
   self._pool = []
   ```

### ❌ Unsafe Pooling Practices:

1. **Shared Mutable State**
   ```python
   class BadFactory:
       def __init__(self):
           self._cache = {}  # ❌ Mutable state
           self._counter = 0  # ❌ Mutable state
   ```

2. **State Carry-Over**
   ```python
   def process(self, data):
       self._last_result = data  # ❌ State carried over
       return self._last_result
   ```

3. **Unbounded Pools**
   ```python
   def _return_to_pool(self, obj):
       self._pool.append(obj)  # ❌ No size limit
   ```

---

## Pooling Checklist

Before implementing a pool, verify:

- [ ] Pooled objects are stateless or have reset() method
- [ ] Pool has maximum size limit
- [ ] Pool behavior is deterministic
- [ ] No shared mutable state in pool
- [ ] Thread-safe for concurrent access
- [ ] Objects can be safely reused

---

## Examples

### ✅ SAFE: HTTP Session Pool

```python
class HttpClientInterface:
    def __init__(self, logger, metrics, config, call_operation):
        self._logger = logger
        self._metrics = metrics
        self._config = config
        self._call_operation = call_operation
        self._pool = []
        self._max_pool_size = 10

    def _get_factory(self):
        if self._pool:
            return self._pool.pop()
        return HttpClientFactory(
            logger=self._logger,
            metrics=self._metrics,
        )

    def _return_factory(self, factory):
        if len(self._pool) < self._max_pool_size:
            # ✅ Factory has no state, safe to pool
            self._pool.append(factory)

# Factory is stateless
class HttpClientFactory:
    def __init__(self, logger, metrics):
        self._logger = logger
        self._metrics = metrics
        # ✅ Only immutable deps, no state

    def get(self, url, **kwargs):
        # ✅ All state passed as params
        with requests.Session() as session:
            return session.get(url, **kwargs)
```

### ❌ UNSAFE: Stateful Cache Pool

```python
# ❌ WRONG - Stateful factory
class BadCacheFactory:
    def __init__(self):
        self._cache = {}  # ❌ Mutable state

    def get(self, key):
        if key not in self._cache:  # ❌ State carried over
            self._cache[key] = load_from_db(key)
        return self._cache[key]

# Pooling this would cause cache sharing between calls
```

---

## Related Patterns

- **AP-EE-05:** Interface Logic
- **ARCH-EE-09:** Object Pooling Pattern

---

**END OF AP-EE-08**
