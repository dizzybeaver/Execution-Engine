# Extension-Structure-Pattern.md

**Version:** 1.0.0  
**Date:** 2025-12-07  
**Purpose:** Standard structure for domain extensions  
**Category:** Architecture Pattern  
**Project:** LEE

---

## LAMBDA IMPORT RULES

### Rule 1: sys.path Setup Required

**MUST be in lambda_function.py:**
```python
import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
```

### Rule 2: NEVER Use Relative Imports

**❌ These NEVER work:**
- `from . import module`
- `from .module import func`
- `from ..package import module`
- `import .module`

**✅ These ALWAYS work:**
- `from package.module import func`
- `import package.module as alias`
- `from package.subpackage.module import func`

### Rule 3: Full Path ONLY

**Pattern:**
```
from {directory}.{subdirectory}.{file} import {function}
import {directory}.{subdirectory}.{file} as {alias}
```

**Examples:**
```python
from home_assistant.ha_config import HA_ENABLED
import home_assistant.ha_interconnect as ha_interconnect
from home_assistant.ha_alexa.ha_interface_alexa import handle_directive
```

### Rule 4: Applies to ALL Files

**Even within subdirectories:**
```python
# In home_assistant/ha_alexa/ha_alexa_core.py
# ❌ WRONG
from .ha_alexa_helpers import func

# ✅ CORRECT
from home_assistant.ha_alexa.ha_alexa_helpers import func
```

---

## OVERVIEW

Extensions mirror LEE's core architecture with subdirectories for each interface, maintaining consistency between core and extension modules.

---

## CRITICAL: Lambda sys.path Requirement

**REQUIRED in lambda_function.py for ANY subdirectory imports to work:**

```python
# ===== CRITICAL: sys.path fix for subdirectory imports =====
# This MUST be FIRST, before any imports
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
```

**Without this:**
- ❌ ALL subdirectory imports FAIL
- ❌ `from home_assistant.ha_config import` FAILS
- ❌ `import home_assistant.ha_interconnect` FAILS
- ❌ Lambda cannot find subdirectory modules

**With this:**
- ✅ All subdirectory imports work
- ✅ Standard Python package structure works
- ✅ No other path manipulation needed

**Location:** Top of lambda_function.py, before ALL other imports

---

## CORE LEE STRUCTURE

```
/src/
├── lambda_function.py
├── gateway/
│   ├── __init__.py
│   ├── gateway.py              # Main router/registry
│   └── gateway_core.py
├── interfaces/
│   ├── __init__.py
│   ├── interface_cache.py      # Interface layer
│   ├── interface_logging.py
│   ├── interface_http.py
│   └── ... (12 interfaces)
└── cores/
    ├── __init__.py
    ├── cache_core.py           # Core implementation
    ├── logging_core.py
    └── ... (12 cores)
```

**Key Pattern:**
- `gateway.py` - Central router/registry
- `interfaces/` - Each interface in subdirectory
- `cores/` - Each core implementation in subdirectory

---

## EXTENSION STRUCTURE (Home Assistant)

**Mirror LEE's pattern:**

```
home_assistant/
├── __init__.py
├── ha_interconnect.py          # Like gateway.py - main router
├── ha_config.py                # Extension config
├── ha_alexa/                   # Alexa interface (like interfaces/)
│   ├── __init__.py
│   ├── ha_interface_alexa.py  # Interface layer
│   ├── ha_alexa_core.py       # Core implementation
│   ├── ha_alexa_helpers.py    # Helpers
│   ├── ha_alexa_properties.py # Property builders
│   └── ha_alexa_templates.py  # Templates
├── ha_devices/                 # Devices interface
│   ├── __init__.py
│   ├── ha_interface_devices.py
│   ├── ha_devices_core.py
│   ├── ha_devices_cache.py
│   └── ha_devices_discovery.py
├── ha_websocket/               # WebSocket interface
│   ├── __init__.py
│   ├── ha_interface_websocket.py
│   ├── ha_websocket_core.py
│   └── ha_websocket_client.py
└── ha_http/                    # HTTP client interface
    ├── __init__.py
    ├── ha_interface_http.py
    └── ha_http_client_core.py
```

**Key Pattern:**
- `ha_interconnect.py` - Extension router (like gateway.py)
- `ha_config.py` - Extension configuration
- `ha_{interface}/` - Each interface in own subdirectory
- Mirrors LEE's interfaces/cores pattern

---

## IMPORT PATTERNS

### CRITICAL: NO Relative Imports in Lambda

**❌ NEVER use relative imports - they FAIL in Lambda:**
```python
# ❌ WRONG: These ALL FAIL in Lambda
from .ha_config import HA_ENABLED
from . import ha_interconnect
from ..ha_alexa import ha_interface_alexa
import .ha_config
```

**✅ ALWAYS use full path imports:**
```python
# ✅ CORRECT: Full path imports ONLY
from home_assistant.ha_config import HA_ENABLED
import home_assistant.ha_interconnect as ha_interconnect
from home_assistant.ha_alexa.ha_interface_alexa import handle_directive
```

**Why:**
- Relative imports don't resolve correctly in Lambda
- Lambda's import system requires absolute paths
- User has tested extensively - only full paths work

### LEE Core Imports

```python
# Gateway
from gateway.gateway import cache_get

# Interface
from interfaces.interface_cache import execute_cache_operation

# Core
from cores.cache_core import get_impl
```

### Extension Imports (Home Assistant)

```python
# Extension router (like gateway)
import home_assistant.ha_interconnect as ha_interconnect

# Extension config
from home_assistant.ha_config import HA_ENABLED, HA_DEBUG_MODE

# Extension interface
import home_assistant.ha_alexa.ha_interface_alexa as ha_interface_alexa
from home_assistant.ha_alexa.ha_alexa_core import handle_directive

# Extension helpers
from home_assistant.ha_alexa.ha_alexa_helpers import build_response
from home_assistant.ha_alexa.ha_alexa_properties import build_properties

# Other extension interfaces
from home_assistant.ha_devices.ha_devices_core import discover_devices
from home_assistant.ha_websocket.ha_websocket_core import connect
```

---

## LAZY IMPORT PATTERN

### Extension Module Imports

```python
def handle_alexa_request(directive, context, correlation_id):
    """Handle Alexa request with lazy HA import."""
    try:
        # LAZY IMPORT: Extension interface
        import home_assistant.ha_alexa.ha_interface_alexa as ha_interface_alexa
    except ImportError as e:
        log_error(f"[{correlation_id}] HA Alexa unavailable: {e}")
        return error_response('INTERNAL_ERROR')
    
    return ha_interface_alexa.handle_directive(directive, context, correlation_id)
```

### Extension Helper Imports

```python
def build_alexa_response(state, entity_id):
    """Build Alexa response with lazy import."""
    try:
        # LAZY IMPORT: Extension helpers
        from home_assistant.ha_alexa.ha_alexa_helpers import format_state
        from home_assistant.ha_alexa.ha_alexa_properties import build_properties
    except ImportError as e:
        log_error(f"HA Alexa helpers unavailable: {e}")
        return None
    
    formatted = format_state(state, entity_id)
    properties = build_properties(formatted)
    return properties
```

---

## CONDITIONAL EXPORTS

### Extension __init__.py

```python
# home_assistant/__init__.py
from .ha_config import HA_ENABLED

if HA_ENABLED:
    # HA enabled - export all interfaces
    from . import ha_interconnect
    from .ha_alexa import ha_interface_alexa
    from .ha_devices import ha_interface_devices
    from .ha_websocket import ha_interface_websocket
    
    __all__ = [
        'ha_interconnect',
        'ha_interface_alexa',
        'ha_interface_devices',
        'ha_interface_websocket',
        'HA_ENABLED'
    ]
else:
    # HA disabled - minimal exports
    __all__ = ['HA_ENABLED']
```

### Interface __init__.py

```python
# home_assistant/ha_alexa/__init__.py
from .ha_interface_alexa import handle_directive, build_response

__all__ = [
    'handle_directive',
    'build_response'
]
```

---

## FILE ORGANIZATION

### Interface Subdirectory Pattern

**Each interface subdirectory contains:**
- `ha_interface_{name}.py` - Interface layer (router/dispatcher)
- `ha_{name}_core.py` - Core implementation
- `ha_{name}_helpers.py` - Helper functions (if needed)
- `ha_{name}_{specific}.py` - Domain-specific modules

**Example: ha_alexa/**
```
ha_alexa/
├── __init__.py                # Interface exports
├── ha_interface_alexa.py      # Interface layer (like interface_cache.py)
├── ha_alexa_core.py           # Core implementation (like cache_core.py)
├── ha_alexa_helpers.py        # Helper functions
├── ha_alexa_properties.py     # Property builders
└── ha_alexa_templates.py      # Response templates
```

### File Size Management

**All files ≤350 lines:**
- Split large implementations into helpers
- Use companion .md for documentation
- Keep interface layer minimal

**Example split:**
```
ha_alexa_core.py         (300 lines) - Main handlers
ha_alexa_helpers.py      (200 lines) - Helper functions
ha_alexa_properties.py   (150 lines) - Property builders
ha_alexa_templates.py    (100 lines) - Templates
```

---

## MIGRATION FROM FLAT STRUCTURE

### Current Flat Structure

```
home_assistant/
├── __init__.py
├── ha_interconnect.py
├── ha_config.py
├── ha_alexa_core.py           # All in root
├── ha_alexa_helpers.py
├── ha_alexa_properties.py
├── ha_devices_core.py
├── ha_devices_cache.py
├── ha_websocket_core.py
└── ha_http_client_core.py
```

### Target Organized Structure

```
home_assistant/
├── __init__.py
├── ha_interconnect.py
├── ha_config.py
├── ha_alexa/
│   ├── __init__.py
│   ├── ha_interface_alexa.py  # NEW: Interface layer
│   ├── ha_alexa_core.py       # MOVED
│   ├── ha_alexa_helpers.py    # MOVED
│   └── ha_alexa_properties.py # MOVED
├── ha_devices/
│   ├── __init__.py
│   ├── ha_interface_devices.py # NEW
│   ├── ha_devices_core.py      # MOVED
│   └── ha_devices_cache.py     # MOVED
├── ha_websocket/
│   ├── __init__.py
│   ├── ha_interface_websocket.py # NEW
│   └── ha_websocket_core.py      # MOVED
└── ha_http/
    ├── __init__.py
    ├── ha_interface_http.py   # NEW
    └── ha_http_client_core.py # MOVED
```

### Migration Steps

**Step 1: Create subdirectories**
```bash
cd home_assistant
mkdir -p ha_alexa ha_devices ha_websocket ha_http
touch ha_alexa/__init__.py
touch ha_devices/__init__.py
touch ha_websocket/__init__.py
touch ha_http/__init__.py
```

**Step 2: Create interface layers**
```python
# Create ha_alexa/ha_interface_alexa.py
# Create ha_devices/ha_interface_devices.py
# Create ha_websocket/ha_interface_websocket.py
# Create ha_http/ha_interface_http.py
```

**Step 3: Move files**
```bash
# Move alexa files
mv ha_alexa_*.py ha_alexa/

# Move devices files
mv ha_devices_*.py ha_devices/

# Move websocket files
mv ha_websocket_*.py ha_websocket/

# Move HTTP files
mv ha_http_*.py ha_http/
```

**Step 4: Update imports**
```python
# Before
from home_assistant.ha_alexa_core import handle_directive

# After
from home_assistant.ha_alexa.ha_alexa_core import handle_directive
# or
import home_assistant.ha_alexa.ha_interface_alexa as ha_interface_alexa
```

---

## CONSISTENCY RULES

### Universal Pattern

**All extensions follow same structure:**

```
{extension_name}/
├── __init__.py
├── {ext}_interconnect.py      # Router (like gateway.py)
├── {ext}_config.py             # Configuration
├── {ext}_{interface1}/         # Interface subdirectory
│   ├── __init__.py
│   ├── {ext}_interface_{name}.py
│   ├── {ext}_{name}_core.py
│   └── {ext}_{name}_*.py
├── {ext}_{interface2}/
│   └── ...
└── {ext}_{interfaceN}/
    └── ...
```

### Naming Conventions

**Router/Registry:**
- Core: `gateway.py`
- Extension: `{ext}_interconnect.py`
- Purpose: Route operations to interfaces

**Interface Layer:**
- Core: `interface_{name}.py`
- Extension: `{ext}_interface_{name}.py`
- Location: `{ext}_{name}/` subdirectory

**Core Implementation:**
- Core: `{name}_core.py`
- Extension: `{ext}_{name}_core.py`
- Location: Same subdirectory as interface

**Helpers:**
- Pattern: `{ext}_{name}_{purpose}.py`
- Examples: `ha_alexa_helpers.py`, `ha_alexa_properties.py`
- Location: Same subdirectory as interface/core

---

## LAMBDA DEPLOYMENT

### Deployment Package Structure

```
lambda_deployment.zip
├── lambda_function.py
├── gateway/
│   └── gateway.py
├── interfaces/
│   └── interface_*.py
├── cores/
│   └── *_core.py
└── home_assistant/
    ├── ha_interconnect.py
    ├── ha_alexa/
    │   ├── ha_interface_alexa.py
    │   └── ha_alexa_core.py
    ├── ha_devices/
    │   └── ...
    └── ha_websocket/
        └── ...
```

**Import compatibility:**
- All imports use full paths
- No sys.path manipulation needed
- Standard Python package structure
- Works natively in Lambda

---

## BENEFITS

### Consistency
- Extensions mirror core structure
- Same patterns everywhere
- Easy to understand
- Predictable organization

### Scalability
- Each interface isolated
- Related files grouped
- Easy to add new interfaces
- Clear boundaries

### Maintainability
- Interface layer clearly defined
- Core implementations separated
- Helpers logically grouped
- Documentation co-located

### Navigation
- IDE-friendly structure
- Quick interface location
- Related files together
- Clear purpose from path

---

## EXAMPLES

### Gateway Call to Extension

```python
# In gateway/gateway.py
def ha_alexa_directive(directive, context, correlation_id):
    """Route Alexa directive to HA extension."""
    # LAZY IMPORT: HA Alexa interface
    import home_assistant.ha_alexa.ha_interface_alexa as ha_alexa
    
    return ha_alexa.handle_directive(directive, context, correlation_id)
```

### Extension Interface Call to Core

```python
# In home_assistant/ha_alexa/ha_interface_alexa.py
from .ha_alexa_core import handle_power_controller
from .ha_alexa_helpers import build_response

def handle_directive(directive, context, correlation_id):
    """Handle Alexa directive (interface layer)."""
    namespace = directive['header']['namespace']
    
    if namespace == 'Alexa.PowerController':
        result = handle_power_controller(directive, context, correlation_id)
        return build_response(result)
```

### Extension Core Implementation

```python
# In home_assistant/ha_alexa/ha_alexa_core.py
# ❌ WRONG: Relative imports
# from .ha_alexa_helpers import extract_entity_id
# from ..ha_devices.ha_devices_core import control_device

# ✅ CORRECT: Full path imports
from home_assistant.ha_alexa.ha_alexa_helpers import extract_entity_id
from home_assistant.ha_devices.ha_devices_core import control_device

def handle_power_controller(directive, context, correlation_id):
    """Handle PowerController directive (core implementation)."""
    entity_id = extract_entity_id(directive)
    action = directive['header']['name']  # TurnOn/TurnOff
    
    # Call devices interface
    result = control_device(entity_id, action, correlation_id)
    return result
```

---

## RELATED

- DEC-17 - Directory organization decision
- AP-05 - Flat file structure anti-pattern
- File-Standards.md - 350-line limit

---

**END OF FILE**

**Summary:** Extensions mirror LEE's structure with subdirectories per interface, maintaining consistency and scalability.
