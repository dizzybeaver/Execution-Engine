# get_http_client_manager()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_manager  
**Type:** Singleton Factory Function

---

## Purpose

Get the singleton HTTP client manager instance. Implements singleton pattern via gateway registry with module-level fallback.

---

## Signature

```python
def get_http_client_manager() -> HTTPClientCore:
```

---

## Parameters

**None**

---

## Returns

**Type:** `HTTPClientCore`

**Description:** The singleton HTTP client manager instance

**Attributes:**
- `http` - urllib3 PoolManager instance
- `_stats` - Request statistics dictionary
- `_retry_config` - Retry configuration dictionary
- `_rate_limiter` - Rate limiting deque
- `_rate_limited_count` - Rate limit violation counter

---

## Behavior

1. **Check gateway singleton registry** (preferred path)
   - Import `gateway.singleton_get()` and `gateway.singleton_register()`
   - Check if `'http_client_manager'` exists in registry
   - If exists, return registered instance

2. **Create new instance if needed**
   - Create `HTTPClientCore()` if `_http_client_core` is None
   - Register in gateway singleton registry
   - Store in module-level `_http_client_core`

3. **Fallback to module-level singleton**
   - If gateway unavailable (ImportError)
   - Use module-level `_http_client_core`
   - Create if doesn't exist

4. **Return instance**

---

## Usage

```python
from http_client.http_client_manager import get_http_client_manager

# Get singleton instance
client = get_http_client_manager()

# Use client
result = client.make_request('GET', 'https://api.example.com/data')
stats = client.get_stats()
```

---

## Singleton Pattern

**Primary:** Gateway singleton registry  
**Fallback:** Module-level singleton

**Key:** `'http_client_manager'`

**Lifecycle:**
- Created on first access
- Persists across Lambda invocations (if container reused)
- Resettable via `client.reset()`

---

## Gateway Integration

```python
# Via gateway singleton
from gateway import singleton_get

client = singleton_get('http_client_manager')
```

---

## Performance

**Cold Start:** ~5ms (includes urllib3 PoolManager creation)  
**Warm Path:** ~0.1ms (singleton lookup)

---

## Error Scenarios

| Scenario | Behavior |
|----------|----------|
| Gateway unavailable | Falls back to module-level singleton |
| First call | Creates new HTTPClientCore instance |
| Subsequent calls | Returns existing instance |

---

## Related Functions

- `get_http_client()` - Legacy compatibility wrapper
- `HTTPClientCore()` - Core client class constructor
- `gateway.singleton_get()` - Gateway singleton access
- `gateway.singleton_register()` - Gateway singleton registration

---

## Notes

- **REF:** LESS-18 (Singleton pattern for lifecycle management)
- **REF:** RULE-01 (Gateway-first approach)
- Ensures single HTTP connection pool across all operations
- Module-level fallback for environments without gateway
- Safe for concurrent access (Lambda is single-threaded)

---

**Lines:** 120
