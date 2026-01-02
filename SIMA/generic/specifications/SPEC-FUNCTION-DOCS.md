# SPEC-FUNCTION-DOCS.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Function documentation standards  
**Category:** Specifications

---

## PURPOSE

Define documentation standards for functions at different levels: helper functions, internal functions, and public API functions.

---

## DOCUMENTATION LEVELS

### Level 1: Helper Functions
**Minimal documentation required**

**Criteria:**
- Internal use only
- Called by single module
- Simple, obvious purpose
- Not in public interfaces

**Documentation:**
```python
def _validate_key(key):
    """Check key is valid string."""
    return isinstance(key, str) and len(key) > 0
```

**Rules:**
- Single-line docstring
- No Args/Returns sections
- Brief description only
- Leading underscore naming

---

### Level 2: Internal Functions
**Moderate documentation required**

**Criteria:**
- Used within module/interface
- Not exposed publicly
- Multiple call sites
- Non-trivial logic

**Documentation:**
```python
def sanitize_sentinels(data):
    """
    Replace sentinel objects with None for JSON serialization.
    
    Args:
        data: Value to sanitize (any type)
    
    Returns:
        Sanitized value safe for JSON
    """
    if data is _CacheMiss or data is _NotFound:
        return None
    return data
```

**Rules:**
- Multi-line docstring
- Args section (brief)
- Returns section (brief)
- Example optional

---

### Level 3: Public API Functions
**Complete documentation required**

**Criteria:**
- Exposed publicly
- Public API
- Used by external code
- Part of interface contract

**Documentation:**
```python
def cache_get(key, default=None, namespace=None):
    """
    Retrieve value from cache by key.
    
    Provides fast in-memory caching with automatic expiration and
    namespace support for key isolation.
    
    Args:
        key (str): Cache key identifier
        default (any, optional): Value if key not found. Defaults to None.
        namespace (str, optional): Key namespace for isolation
    
    Returns:
        any: Cached value if exists, default otherwise.
        Returns sentinel if not found and no default.
    
    Raises:
        ValueError: If key is not string or empty
        TypeError: If namespace not string
    
    Example:
        value = cache_get('user:123', default='unknown')
        if value != 'unknown':
            process(value)
    
    REF: INT-01
    """
    import cache_core
    return cache_core.get_impl(key, default, namespace)
```

**Rules:**
- Multi-line docstring
- Overview (1-2 sentences)
- All sections complete
- Example required
- REF-ID included
- Type hints in Args

---

## DOCSTRING FORMAT

### Standard Style
```python
def function(arg1, arg2):
    """
    Brief summary line.
    
    Extended description if needed.
    More details here.
    
    Args:
        arg1: Description
        arg2: Description
    
    Returns:
        Description
    """
```

**Rules:**
- Triple double quotes
- Summary on first line
- Blank line after summary
- Sections separated by blank lines

---

## SECTIONS

### Args
```python
Args:
    key (str): Cache key identifier
    default (any, optional): Default value. Defaults to None.
    **kwargs: Additional options
```

**Rules:**
- One arg per line
- Type in parentheses
- Optional noted with "optional"
- Default values specified

### Returns
```python
Returns:
    dict: Configuration dictionary with keys 'timeout', 'retries'.
    None if configuration not found.
```

**Rules:**
- Type first
- Description
- Multiple return cases noted

### Raises
```python
Raises:
    ValueError: If key empty or invalid
    TypeError: If key not string
    ConnectionError: If cache unavailable
```

**Rules:**
- Exception type first
- When it's raised
- One per line

### Example
```python
Example:
    result = cache_get('user:123')
    if result:
        print(result)
```

**Rules:**
- Indented code block
- Working example
- Shows typical usage
- Brief (3-5 lines max)

### REF
```python
REF: INT-01, LESS-15
```

**Rules:**
- Related REF-IDs
- At end of docstring
- Comma-separated

---

## TYPE HINTS

### Use Type Hints
```python
def cache_get(key: str, default: any = None) -> any:
    """Retrieve value from cache."""
```

**Rules:**
- All public functions
- Optional for internal
- Use typing module for complex

### Complex Types
```python
from typing import Optional, Dict, List, Union

def get_config(key: str) -> Optional[Dict[str, any]]:
    """Get configuration dictionary."""
```

---

## FUNCTION REFERENCE SYSTEM

### Purpose
Track all functions per interface to:
- Prevent duplicate work
- Increase cross-interface utilization
- Document complete API surface

### Format
**File:** `/sima/projects/[project]/function-references/INT-##-Functions.md`

```markdown
# INT-01-Functions.md

**Version:** v2025.11.10-1  
**Purpose:** Complete function catalog for interface

---

## PUBLIC FUNCTIONS

### cache_get
**Purpose:** Retrieve value from cache  
**Params:** key, default, namespace  
**Returns:** Cached value or default  
**File:** gateway_wrappers_cache.py  
**REF:** INT-01

### cache_set
**Purpose:** Store value in cache  
**Params:** key, value, ttl, namespace  
**Returns:** bool (success)  
**File:** gateway_wrappers_cache.py  
**REF:** INT-01

## INTERNAL FUNCTIONS

### sanitize_sentinels
**Purpose:** Remove sentinel objects  
**File:** cache_core.py  
**Used by:** cache_get, cache_list

---
```

---

## BREVITY IN DOCS

### Keep Concise
**Bad:**
```python
"""
This function is designed to retrieve a value from the cache system
by looking up the provided key identifier in the internal cache store
and returning either the cached value if it exists or the default
value that was provided if the key is not found in the cache.
"""
```

**Good:**
```python
"""
Retrieve value from cache by key.
Returns default if key not found.
"""
```

### Guidelines
- 1-2 sentence summary
- Args: One line each
- Returns: One line
- Example: 3-5 lines max

---

## WHEN NOT TO DOCUMENT

### Skip Docstrings For
- Magic methods (`__init__`, `__str__`)
- Property getters/setters (obvious)
- Test functions (name explains)
- Overridden methods (use parent docs)

### Example
```python
def __init__(self, name):
    self.name = name  # No docstring needed

@property
def name(self):
    return self._name  # No docstring needed
```

---

## UPDATING DOCS

### When to Update
- Function signature changes
- New parameters added
- Return type changes
- New exceptions raised
- Behavior changes

### Process
1. Update function docstring
2. Update function reference file
3. Update related REF-IDs
4. Update examples

---

## QUALITY CHECKLIST

### Helper Functions
- [ ] Single-line docstring
- [ ] Brief description

### Internal Functions
- [ ] Multi-line docstring
- [ ] Args section
- [ ] Returns section

### Public Functions
- [ ] Complete docstring
- [ ] Overview + extended description
- [ ] All Args with types
- [ ] Returns with type
- [ ] Raises section
- [ ] Example included
- [ ] REF-ID present
- [ ] Function reference updated

---

## VALIDATION

### Automated Check
```python
import ast

def check_function_docs(file_path):
    with open(file_path) as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check public functions
            if not node.name.startswith('_'):
                if not ast.get_docstring(node):
                    print(f"Missing docstring: {node.name}")
```

---

**Related:**
- SPEC-FILE-STANDARDS.md
- SPEC-LINE-LIMITS.md

**Version History:**
- v4.2.2-blank (2025-11-10): Blank slate version, genericized
- v1.0.0 (2025-11-06): Initial function docs spec

---


**END OF FILE**
