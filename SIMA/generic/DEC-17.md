# DEC-17.md

**REF-ID:** DEC-17  
**Category:** Technical Decision  
**Priority:** High  
**Status:** Active  
**Date Decided:** 2025-12-07 (Reversed)  
**Original Date:** 2024-04-15  
**Last Updated:** 2025-12-07

---

## 📋 SUMMARY

Organize files into logical subdirectories (gateway/, interfaces/, cores/, home_assistant/) for scalability and clarity. Directory prefix imports ensure Lambda compatibility.

**Decision:** Directory-based organization with explicit imports  
**Impact Level:** High  
**Reversibility:** Easy (migration path defined)

---

## 🎯 CONTEXT

### Problem Statement
Flat structure with 93 Python files in root directory creates navigation and scalability challenges. Need organized structure that works in AWS Lambda while maintaining clear architecture boundaries.

### Background
- Lambda project has 93+ Python files
- 12 interfaces, 12 core implementations
- Gateway layer, fast path, diagnostics
- Home Assistant extension (17+ files)
- Growing codebase needs better organization

### Requirements
- Clear layer separation
- Easy file discovery
- Lambda-compatible imports
- Scalable structure
- Simple navigation

---

## 💡 DECISION

### What We Chose
Directory-based organization with subdirectories for each architectural layer. Import paths use directory prefixes with sys.path setup in lambda_function.py for Lambda compatibility.

### Critical Requirement: sys.path Setup

**REQUIRED in lambda_function.py for subdirectory imports:**
```python
# ===== CRITICAL: sys.path fix for subdirectory imports =====
# This MUST be FIRST, before any imports
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
```

**Without this setup:**
- ❌ ALL subdirectory imports FAIL in Lambda
- ❌ Cannot import from gateway/, interfaces/, cores/, home_assistant/
- ❌ Lambda cannot resolve package paths

**With this setup:**
- ✅ All subdirectory imports work
- ✅ Standard Python package structure works
- ✅ No additional path manipulation needed

### Implementation
```
/src/
├── lambda_function.py
├── gateway/
│   ├── __init__.py
│   ├── gateway.py
│   ├── gateway_core.py
│   └── gateway_wrappers.py
├── interfaces/
│   ├── __init__.py
│   ├── interface_cache.py
│   ├── interface_logging.py
│   ├── interface_http.py
│   ├── interface_config.py
│   └── ... (12 total)
├── cores/
│   ├── __init__.py
│   ├── cache_core.py
│   ├── logging_core.py
│   ├── http_client_core.py
│   ├── config_core.py
│   └── ... (12 total)
└── home_assistant/
    ├── __init__.py
    ├── ha_core.py
    ├── ha_alexa_core.py
    ├── ha_devices_core.py
    ├── ha_websocket_core.py
    └── ... (17 total)
```

### Lambda-Compatible Import Pattern

**CRITICAL: NEVER use relative imports in Lambda - they FAIL**

**❌ WRONG: Relative imports (DON'T WORK):**
```python
from .ha_config import HA_ENABLED
from . import ha_interconnect  
from ..interfaces import interface_cache
```

**✅ CORRECT: Full path imports ONLY:**
```python
# Directory prefix required
from home_assistant.ha_config import (
    HA_ENABLED,
    HA_CACHE_ENABLED,
    HA_DEBUG_MODE,
    HA_CACHE_TTL_STATE,
    HA_API_TIMEOUT
)

# Module import with full path
import home_assistant.ha_interconnect as ha_interconnect

# From interfaces with full path
from interfaces.interface_cache import execute_cache_operation
from cores.cache_core import get_impl

# ❌ WRONG: No directory prefix (won't work in Lambda)
from ha_config import HA_ENABLED
import ha_interconnect
from interface_cache import execute_cache_operation
```

**Why full paths required:**
- Relative imports don't resolve in Lambda
- Lambda requires absolute package paths
- Extensively tested - only full paths work
- Applies to ALL files, even within subdirectories

### Lazy Import Pattern

**Function-level with directory prefix:**
```python
def handle_alexa_directive(directive, context, correlation_id):
    """Handle Alexa directive with lazy HA import."""
    try:
        # LAZY IMPORT: Only load when needed
        import home_assistant.ha_interconnect as ha_interconnect
    except ImportError as e:
        log_error(f"[{correlation_id}] ha_interconnect not available: {e}")
        return _create_error_response({}, 'INTERNAL_ERROR', 'HA unavailable')
    
    return ha_interconnect.route_directive(directive, context, correlation_id)
```

### Conditional Exports in __init__.py

**Feature flag support (NO relative imports):**
```python
# home_assistant/__init__.py
# ❌ WRONG: Relative imports FAIL in Lambda
# from .ha_config import HA_ENABLED
# from . import ha_interconnect

# ✅ CORRECT: Full path imports ONLY
from home_assistant.ha_config import HA_ENABLED

if HA_ENABLED:
    # HA enabled - export modules (full paths)
    import home_assistant.ha_interconnect as ha_interconnect
    import home_assistant.ha_alexa.ha_interface_alexa as ha_interface_alexa
    import home_assistant.ha_devices.ha_interface_devices as ha_interface_devices
    
    __all__ = ['ha_interconnect', 'ha_interface_alexa', 'ha_interface_devices', 'HA_ENABLED']
else:
    # HA disabled - minimal exports
    __all__ = ['HA_ENABLED']
```

### Extension Structure Pattern

**Extensions mirror LEE's core structure:**
- Extension router (e.g., `ha_interconnect.py`) mirrors `gateway.py`
- Each interface in own subdirectory (e.g., `ha_alexa/`)
- Interface files: `ha_interface_{name}.py` (like `interface_cache.py`)
- Core files: `ha_{name}_core.py` (like `cache_core.py`)
- Maintains consistency between core and extensions

**See:** Extension-Structure-Pattern.md for complete details

---

## 📄 RATIONALE

### 1. Clear Layer Separation

**Physical boundaries match architecture:**
```
gateway/     → Gateway layer (SUGA)
interfaces/  → Interface layer (SUGA)
cores/       → Core implementations (SUGA)
home_assistant/ → Domain extension
```

**Benefits:**
- Visual architecture alignment
- Clear file organization
- Easier onboarding
- Obvious layer boundaries

### 2. Scalable Navigation

**3-5 directories vs 93 files:**
- IDE file tree manageable
- Quick layer identification
- Related files grouped
- Less scrolling

**File discovery:**
```bash
# Find all cache-related files
ls -1 interfaces/interface_cache.py
ls -1 cores/cache_core.py

# vs flat (mixed with 90 other files)
ls -1 | grep cache
```

### 3. Lambda Compatibility

**sys.path setup enables subdirectory imports:**
```python
# In lambda_function.py (REQUIRED)
import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Now subdirectory imports work
from gateway.gateway import cache_get  # ✅ Works
from interfaces.interface_cache import execute_cache_operation  # ✅ Works
```

**No relative imports ever:**
- Lambda doesn't support relative imports
- Only full path imports work
- Applies to ALL files in ALL subdirectories

**Standard Python package imports:**
- Works in Lambda natively after sys.path setup
- No other path manipulation needed
- Deployment is straightforward

### 4. Import Clarity

**Import clarity with extensions:**
```python
# Core LEE layers
from gateway.gateway import cache_get          # Gateway layer
from interfaces.interface_cache import execute # Interface layer
from cores.cache_core import get_impl         # Core layer

# Extension layers (mirrors core)
import home_assistant.ha_interconnect as ha_interconnect  # Extension router
from home_assistant.ha_alexa.ha_interface_alexa import handle_directive  # Extension interface
from home_assistant.ha_alexa.ha_alexa_core import process  # Extension core
```

---

## 📄 ALTERNATIVES CONSIDERED

### Alternative 1: Flat Structure (Previous Decision)
**Pros:**
- No directory navigation
- Simple imports (without prefix)
- Fast file search

**Cons:**
- 93 files in one directory overwhelming
- No layer separation
- Hard to navigate in IDE
- Doesn't scale beyond 100 files
- Unclear architecture boundaries

**Why Rejected:** Scalability issues, no clear separation.

---

### Alternative 2: Deep Nesting (core/implementations/cache/)
**Pros:**
- Very granular organization

**Cons:**
- Import paths too long
- Over-engineered for size
- Navigation overhead high
- Unnecessary complexity

**Why Rejected:** Too much nesting for project size.

---

### Alternative 3: Group by Feature (cache/, http/, config/)
**Pros:**
- Feature cohesion

**Cons:**
- Gateway files scattered
- Breaks SUGA layer pattern
- Duplicate structure per feature

**Why Rejected:** Doesn't align with SUGA architecture.

---

## ⚖️ TRADE-OFFS

### What We Gained
- Clear layer separation (physical matches logical)
- Scalable organization (works to 500+ files)
- Easy navigation (3-5 dirs vs 93 files)
- Obvious architecture (directories show layers)
- Better IDE performance

### What We Accepted
- Directory prefix in imports (small overhead)
- __init__.py files (minimal maintenance)
- One extra directory level (negligible cost)
- Migration effort (one-time cost)

---

## 📊 IMPACT ANALYSIS

### Technical Impact
- **Navigation:** Faster (3-5 dirs vs 93 files)
- **Imports:** Slightly longer (directory prefix)
- **Refactoring:** Easier (layer boundaries clear)
- **IDE:** Better performance
- **Lambda:** Native compatibility (no sys.path hacks)

### Developer Impact
- **Learning:** Clear structure, faster onboarding
- **Productivity:** Easier file discovery
- **Mistakes:** Layer violations more obvious
- **Maintenance:** Related files grouped

### Migration Impact
- One-time effort (2-3 hours)
- Import updates systematic
- Testable incrementally
- Low risk

---

## 🔄 MIGRATION GUIDE

### Phase 1: Create Structure

```bash
# Create directories
mkdir -p gateway interfaces cores

# Create __init__.py
touch gateway/__init__.py
touch interfaces/__init__.py
touch cores/__init__.py
# home_assistant/ already exists
```

### Phase 2: Move Files by Layer

```bash
# Move gateway files
mv gateway*.py gateway/

# Move interface files
mv interface_*.py interfaces/

# Move core files
mv *_core.py cores/

# lambda_function.py stays in root
```

### Phase 3: Update Imports

**Pattern: Add directory prefix to all imports**

```python
# Before (flat)
from interface_cache import execute_cache_operation
from cache_core import get_impl
import ha_interconnect

# After (directory-based)
from interfaces.interface_cache import execute_cache_operation
from cores.cache_core import get_impl
import home_assistant.ha_interconnect as ha_interconnect
```

### Phase 4: Update Lazy Imports

```python
# Before
def function():
    import cache_core
    
# After
def function():
    from cores import cache_core
    # or
    import cores.cache_core as cache_core
```

### Phase 5: Test Incrementally

```bash
# Test after each layer migration
python -m pytest tests/

# Deploy to Lambda test environment
# Verify imports work
# Run integration tests
```

---

## 🔮 FUTURE CONSIDERATIONS

### When Structure Works Well
- Current size: 93 files
- Expected growth: 150+ files
- Scalable to 500+ files
- No restructuring needed

### Potential Extensions
- Additional domain subdirectories (e.g., alexa/)
- Feature modules as subdirectories
- Keep core layers stable

---

## 🔗 RELATED

### Related Decisions
- **DEC-02:** Gateway Centralization (all access via gateway)
- **File-Standards.md:** 350-line limit with splitting

### SIMA Entries
- **AP-05:** Flat File Structure anti-pattern (updated)
- **ARCH-01:** Gateway Trinity (layer architecture)
- **Extension-Structure-Pattern.md:** Extension organization standard

---

## 🏷️ KEYWORDS

`directory-organization`, `layer-separation`, `lambda-compatible`, `scalable-structure`, `import-patterns`, `suga-architecture`

---

## 📝 VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 4.0.0 | 2025-12-07 | REVERSED: Directory-based now preferred (major change) |
| 3.0.0 | 2025-10-30 | SIMAv4 migration |
| 2.0.0 | 2025-10-24 | SIMA v3 format |
| 1.0.0 | 2024-04-15 | Original decision (flat structure) |

---

**END OF DECISION**

**Status:** Active - Directory-based organization  
**Effectiveness:** Scalable, clear, Lambda-compatible  
**Reversal Reason:** Scalability and architecture clarity
