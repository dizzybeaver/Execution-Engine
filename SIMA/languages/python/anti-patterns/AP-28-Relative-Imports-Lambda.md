# AP-28: Relative Imports in Lambda

**Category:** Anti-Pattern
**Type:** Import Pattern
**Severity:** HIGH
**Scope:** AWS Lambda, Plugin Architecture
**Language:** Python
**REF-ID:** AP-28
**Date:** 2025-12-31
**Status:** Active

---

## Overview

**Relative imports in Lambda functions fail** due to how AWS Lambda packages and executes code. When Lambda deploys a function, it may restructure the directory layout or execute from a different working directory, causing relative imports to break.

---

## The Anti-Pattern

### ❌ FORBIDDEN: Relative Imports

```python
# lambda_function.py
from . import helper                    # FAILS in Lambda
from .module import function            # FAILS in Lambda
from ..package import Something         # FAILS in Lambda
from .config import settings            # FAILS in Lambda
import .module                          # FAILS in Lambda
```

### ❌ WHY IT FAILS

1. **Working Directory Mismatch**
   - Lambda executes from `/var/task/`
   - Relative imports resolve against current module location
   - Directory structure may not match development layout

2. **Package Boundary Issues**
   - Lambda may not recognize package hierarchy
   - `__init__.py` files may not be loaded correctly
   - Module `__package__` attribute may be `None`

3. **Zip File Deployment**
   - When deployed as zip, relative paths may not resolve
   - Virtualenv structure differs from deployment structure

---

## The Correct Pattern

### ✅ REQUIRED: Absolute Imports with sys.path Setup

```python
# lambda_function.py (MUST be at root of Lambda package)
import sys
import os

# ADD THIS TO EVERY Lambda-facing module
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# NOW use absolute imports
from helper import function              # Works
from module import Something             # Works
from package.config import settings      # Works
from EE import execute_operation         # Works
```

---

## Application Scope

### MUST Apply To:

1. **Lambda Functions**
   - `lambda_function.py` (main handler)
   - Any supporting modules in Lambda package
   - All Lambda-facing code in Plugins/

2. **Plugins Directory**
   - `Plugins/Alexa/`
   - `Plugins/HA/`
   - Any plugin that may be deployed to Lambda

3. **Home Assistant Integration**
   - Any code that HA may dynamically load
   - AppDaemon apps
   - Custom components

4. **Alexa Integration**
   - Lambda handlers for Alexa skills
   - Supporting modules

### NOT Required For:

- Standard Python package execution
- EE internal code (not Lambda-facing)
- Tests (use pytest import mechanisms)

---

## Implementation Examples

### Example 1: Alexa Lambda Handler

```python
# Plugins/Alexa/lambda_function.py
import sys
import os

# CRITICAL: Add root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# NOW safe to import
from alexa_handler import AlexaHandler
from EE import execute_operation

def lambda_handler(event, context):
    """Handle Alexa skill invocation."""
    handler = AlexaHandler()
    return handler.handle(event)
```

### Example 2: Home Assistant Plugin

```python
# Plugins/HA/app.py
import sys
import os

# CRITICAL: Add root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# NOW safe to import
import hass_utils
from EE import execute_operation

def main():
    """Home Assistant app entry point."""
    # Get HA config via EE
    config = execute_operation(
        domain="foundation",
        interface="config",
        operation="get",
        key="ha.api_key"
    )
    return config
```

### Example 3: Plugin Module

```python
# Plugins/Alexa/smart_home_controller.py
import sys
import os

# CRITICAL: Add root to sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# NOW safe to import local modules
from .intent_handler import IntentHandler  # Still relative within package
from EE import execute_operation           # Absolute import to EE

class SmartHomeController:
    def __init__(self):
        # Use EE for all operations
        pass
```

---

## Enforcement Rules

### Rule 1: NO Relative Imports at Lambda Entry Points

```python
# ❌ FORBIDDEN at lambda_function.py
from . import helper

# ✅ REQUIRED at lambda_function.py
import sys, os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from helper import function
```

### Rule 2: sys.path Setup is Mandatory

Every Lambda-facing module MUST have:

```python
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
```

Place this at the **top of the file**, after docstring but before any imports.

### Rule 3: Use Absolute Imports After sys.path Setup

Once `sys.path` is configured, use **absolute imports only**:

```python
# ✅ CORRECT
from helper import function
from package.module import Class
from EE import execute_operation

# ❌ WRONG
from .helper import function
```

---

## Migration Checklist

When converting code to Lambda compatibility:

- [ ] Add sys.path setup at top of every Lambda-facing file
- [ ] Replace all `from . import` with absolute imports
- [ ] Replace all `from ..package import` with absolute imports
- [ ] Test in Lambda environment (or simulated Lambda)
- [ ] Verify all imports resolve correctly
- [ ] Check for hidden relative imports in nested modules

---

## Related Patterns

- **AP-PY-01:** Import organization
- **AP-PY-02:** Circular imports
- **ARCH-EE-01:** Single entry point for EE

---

## References

- AWS Lambda Documentation: https://docs.aws.amazon.com/lambda/latest/dg/lambda-deployment-functions.html
- Python Import System: https://docs.python.org/3/reference/import.html
- PEP 328: Imports: Multi-Line and Absolute/Relative

---

**END OF AP-28**
