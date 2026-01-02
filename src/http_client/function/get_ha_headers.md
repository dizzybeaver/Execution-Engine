# get_ha_headers()

**Version:** 2025-12-10_1  
**Module:** http_client.http_client_utilities  
**Type:** Utility Function

---

## Purpose

Get Home Assistant specific headers with Bearer token authentication. Extends standard headers with Authorization header.

---

## Signature

```python
def get_ha_headers(token: str) -> Dict[str, str]:
```

---

## Parameters

- **token** (`str`) - Home Assistant long-lived access token
  - Format: Long alphanumeric string
  - Source: Home Assistant user profile
  - Required for HA API authentication

---

## Returns

**Type:** `Dict[str, str]`

**Headers:**
```python
{
    'Content-Type': 'application/json',
    'User-Agent': 'LambdaExecutionEngine/1.0',
    'Authorization': 'Bearer {token}'
}
```

---

## Behavior

1. **Get Standard Headers**
   - Call `get_standard_headers()`
   - Returns `{'Content-Type': 'application/json', 'User-Agent': 'LambdaExecutionEngine/1.0'}`

2. **Add Authorization**
   - Format: `f'Bearer {token}'`
   - Add to headers dict

3. **Return Headers**
   - Complete headers with authentication

---

## Usage

### Basic Usage

```python
from http_client.http_client_utilities import get_ha_headers

token = 'eyJ0eXAiOiJKV1QiLCJhbGc...'
headers = get_ha_headers(token)

# Returns:
{
    'Content-Type': 'application/json',
    'User-Agent': 'LambdaExecutionEngine/1.0',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGc...'
}
```

### With HTTP Request

```python
from http_client import get_http_client_manager, get_ha_headers

client = get_http_client_manager()
token = 'long_lived_access_token'

# Get HA entity state
headers = get_ha_headers(token)
result = client.make_request(
    'GET',
    'https://ha.example.com/api/states/light.living_room',
    headers=headers
)
```

### Via Gateway

```python
import gateway
from http_client import get_ha_headers

# Get token from SSM
token = gateway.config_get('/lee/ha/token')

# Build headers
headers = get_ha_headers(token)

# Make HA API request
result = gateway.http_get(
    'https://ha.example.com/api/states',
    headers=headers
)
```

---

## Home Assistant Authentication

### Token Types

**Long-Lived Access Token:**
- Generated in HA user profile
- Never expires (until revoked)
- Full API access
- **Used by LEE**

**OAuth Token:**
- Short-lived (minutes-hours)
- Requires refresh
- Alexa integration
- Not used for direct API calls

### Token Format

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkZjk4...
```

**Characteristics:**
- Base64-encoded JWT
- 200-400 characters typical
- No spaces or special characters
- Case-sensitive

---

## Authorization Header

### Format

```
Authorization: Bearer {token}
```

**Components:**
- **Scheme:** `Bearer`
- **Token:** Long-lived access token
- **Separator:** Single space

### Example

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## Complete HA API Request Example

```python
from http_client import get_http_client_manager, get_ha_headers
import gateway

# Get HA configuration
ha_url = gateway.config_get('/lee/ha/url')
ha_token = gateway.config_get('/lee/ha/token')

# Build headers
headers = get_ha_headers(ha_token)

# Get HTTP client
client = get_http_client_manager()

# Call HA API
result = client.make_request(
    'GET',
    f'{ha_url}/api/states/light.living_room',
    headers=headers
)

if result['success']:
    entity_state = result['data']
    print(f"State: {entity_state['state']}")
else:
    print(f"Error: {result.get('error')}")
```

---

## HA API Endpoints

### Common Endpoints

**Get All States:**
```python
GET /api/states
headers = get_ha_headers(token)
```

**Get Entity State:**
```python
GET /api/states/{entity_id}
headers = get_ha_headers(token)
```

**Call Service:**
```python
POST /api/services/{domain}/{service}
headers = get_ha_headers(token)
body = {'entity_id': 'light.living_room', 'brightness': 255}
```

**Fire Event:**
```python
POST /api/events/{event_type}
headers = get_ha_headers(token)
body = {'event_data': {...}}
```

---

## Token Security

### Storage

**Recommended:**
```python
# Store in AWS SSM Parameter Store (encrypted)
token = gateway.config_get('/lee/ha/token')
```

**Not Recommended:**
```python
# ❌ Hardcoded in code
token = 'eyJ0eXAiOiJKV1QiLCJhbGc...'

# ❌ Plain text environment variable
token = os.getenv('HA_TOKEN')
```

### Best Practices

1. **Use SSM Parameter Store** with encryption
2. **Rotate tokens** periodically
3. **Revoke old tokens** in HA
4. **Never log tokens** (redact in logs)
5. **Use HTTPS only** for HA API

---

## Error Handling

```python
from http_client import get_ha_headers
import gateway

try:
    # Get token
    token = gateway.config_get('/lee/ha/token')
    
    if not token:
        raise ValueError("HA token not configured")
    
    # Build headers
    headers = get_ha_headers(token)
    
    # Make request
    result = gateway.http_get(ha_url, headers=headers)
    
    if result.get('status_code') == 401:
        gateway.log_error("HA authentication failed - token invalid or expired")
    
except Exception as e:
    gateway.log_error(f"HA request failed: {e}")
```

---

## Performance

**Time:** <0.001ms (string formatting)  
**Memory:** ~500 bytes (3 headers + token)  
**Cached:** No (recreated each call)

---

## Related Functions

- `get_standard_headers()` - Base headers without auth
- `gateway.config_get()` - Retrieve HA token
- `http_get()` / `http_post()` - Make HA API requests

---

## Common Patterns

### Reuse Headers

```python
# Create once, use many times
headers = get_ha_headers(token)

result1 = gateway.http_get(f'{ha_url}/api/states/light.1', headers=headers)
result2 = gateway.http_get(f'{ha_url}/api/states/light.2', headers=headers)
result3 = gateway.http_get(f'{ha_url}/api/states/light.3', headers=headers)
```

### Add Custom Headers

```python
headers = get_ha_headers(token)
headers['X-Custom-Header'] = 'value'
headers['Accept-Language'] = 'en-US'
```

### Override Content-Type

```python
headers = get_ha_headers(token)
headers['Content-Type'] = 'application/x-www-form-urlencoded'
```

---

## Notes

- **Extends standard headers:** Includes Content-Type and User-Agent
- **Bearer scheme:** Required by HA API
- **Token sensitive:** Never log or expose token
- **HTTPS required:** HA API requires encrypted connection
- **Simple function:** No validation or error handling
- **Stateless:** No side effects

---

**Lines:** 280
