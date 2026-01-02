# VERSION-COMPATIBILITY-MATRIX.md

**Version:** 1.0.0  
**Date:** 2025-11-12  
**Purpose:** SIMA version compatibility rules for imports  
**Location:** `/sima/docs/`

---

## OVERVIEW

This document defines compatibility rules between different SIMA versions when importing knowledge archives.

**Version Format:** MAJOR.MINOR.PATCH (e.g., 4.2.2)
- **MAJOR:** Breaking changes to core architecture
- **MINOR:** New features, non-breaking structure changes
- **PATCH:** Bug fixes, documentation updates, no structure changes

---

## COMPATIBILITY RULES

### Rule 1: Exact Version Match
**Pattern:** X.Y.Z → X.Y.Z

**Status:** ✅ **Fully Compatible**

**Action:** None required

**Example:** 4.2.2 → 4.2.2

**Reasoning:** Files exported and imported within same version have identical structure and standards.

---

### Rule 2: Patch Version Difference
**Pattern:** X.Y.A → X.Y.B (where A < B)

**Status:** ✅ **Fully Compatible**

**Action:** None required

**Example:** 4.2.0 → 4.2.2

**Reasoning:** Patch versions maintain backward compatibility. Changes are limited to:
- Bug fixes in documentation
- Typo corrections
- Clarifications
- Minor formatting improvements

**No structural changes in patch versions.**

---

### Rule 3: Minor Version Upgrade
**Pattern:** X.A.Z → X.B.Z (where A < B)

**Status:** ⚠️  **Needs Review**

**Action:** Check compatibility notes, may require minor modifications

**Example:** 4.1.x → 4.2.x

**Reasoning:** Minor versions may introduce:
- New file header fields
- Enhanced metadata formats
- New REF-ID patterns
- Additional file standards

**Usually backward compatible with automatic upgrades available.**

---

### Rule 4: Minor Version Downgrade
**Pattern:** X.A.Z → X.B.Z (where A > B)

**Status:** ⚠️  **Caution Required**

**Action:** Manual review required, some features may be lost

**Example:** 4.2.x → 4.1.x

**Reasoning:** Newer files may contain features not supported in older versions:
- Extended metadata
- New file types
- Enhanced cross-referencing

**Downgrade possible but may require stripping newer features.**

---

### Rule 5: Major Version Difference
**Pattern:** A.Y.Z → B.Y.Z (where A ≠ B)

**Status:** ❌ **Incompatible**

**Action:** Manual migration required, automated import blocked

**Example:** 3.x.x → 4.x.x

**Reasoning:** Major versions indicate breaking changes:
- Complete restructuring
- Different file organization
- Incompatible REF-ID formats
- Changed specifications

**Requires full migration process, not simple import.**

---

### Rule 6: Future Version
**Pattern:** X.Y.Z → X.Y.W (where W > Z significantly)

**Status:** ⚠️  **Version Too New**

**Action:** Warning issued, proceed with caution

**Example:** Importing 4.5.0 into 4.2.2

**Reasoning:** Source uses newer features that may not exist in current version:
- New file types not supported
- Enhanced features not available
- Possible data loss

**User must confirm understanding before proceeding.**

---

## VERSION HISTORY

### SIMA 4.2.x Series

#### v4.2.2 (Current)
**Released:** 2025-11-10  
**Changes:**
- Enhanced import mode with version checking
- Archive system implementation
- Improved duplicate detection

**Breaking:** None  
**Backward Compatible:** Yes (with 4.2.0, 4.2.1)

---

#### v4.2.1
**Released:** 2025-10-15  
**Changes:**
- Bug fixes in index generation
- Improved error messages
- Documentation clarifications

**Breaking:** None  
**Backward Compatible:** Yes (with 4.2.0)

---

#### v4.2.0
**Released:** 2025-09-01  
**Changes:**
- **New header fields added:**
  ```markdown
  **SIMA Version:** 4.2.0
  **Category:** lessons
  ```
- Enhanced file standards
- Improved cross-referencing

**Breaking:** Header format changed (minor)  
**Backward Compatible:** Yes (automatic upgrade from 4.1.x)  
**Migration Path:** Add new header fields automatically during import

---

### SIMA 4.1.x Series

#### v4.1.5
**Released:** 2025-07-20  
**Changes:**
- REF-ID format enhancement
- Better index organization
- Performance improvements

**Breaking:** None  
**Backward Compatible:** Yes (with 4.1.0-4.1.4)

---

#### v4.1.0
**Released:** 2025-05-01  
**Changes:**
- Domain-based organization introduced
- Multi-level hierarchical structure
- Enhanced specifications

**Breaking:** REF-ID format changed from TYPE-## to TYPE-##  
**Backward Compatible:** Partial (auto-upgrade available)  
**Migration Path:** REF-ID mapping required

---

### SIMA 4.0.x Series

#### v4.0.0
**Released:** 2025-01-15  
**Changes:**
- Complete rewrite from v3.x
- New file organization
- Standardized formats
- Generic/Platform/Language/Project separation

**Breaking:** Everything  
**Backward Compatible:** No  
**Migration Path:** Full manual migration from 3.x required

---

## COMPATIBILITY MATRIX TABLE

| From/To | 4.2.2 | 4.2.1 | 4.2.0 | 4.1.x | 4.0.x | 3.x |
|---------|-------|-------|-------|-------|-------|-----|
| **4.2.2** | ✅ | ⬇️ | ⬇️ | ⬇️ | ⬇️ | ❌ |
| **4.2.1** | ✅ | ✅ | ⬇️ | ⬇️ | ⬇️ | ❌ |
| **4.2.0** | ✅ | ✅ | ✅ | ⬇️ | ⬇️ | ❌ |
| **4.1.x** | ⚠️  | ⚠️  | ⚠️  | ✅ | ⬇️ | ❌ |
| **4.0.x** | ⚠️  | ⚠️  | ⚠️  | ⚠️  | ✅ | ❌ |
| **3.x**   | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

**Legend:**
- ✅ Fully compatible (direct import)
- ⚠️  Needs review (check compatibility notes)
- ⬇️ Downgrade (caution, possible feature loss)
- ❌ Incompatible (manual migration required)

---

## IMPORT DECISION FLOW

```
START: Check file version

IF file_version == current_version:
   → PROCEED (no checks needed)
   
ELSE IF (file_version and current_version) in same MINOR:
   → CHECK patch difference
   → IF patch_diff ≤ 2:
      → PROCEED (compatible)
   → ELSE:
      → WARN (significant patch gap)
      → Suggest upgrade
      
ELSE IF (file_version and current_version) in same MAJOR:
   → CHECK minor difference
   → IF minor_diff == 1:
      → REVIEW breaking changes list
      → APPLY auto-upgrades
      → PROCEED with modifications
   → ELSE IF minor_diff > 1:
      → WARN (multiple versions gap)
      → Manual review recommended
   → ELSE IF minor_diff < 0: # Downgrade
      → WARN (features may be lost)
      → Require user confirmation
      
ELSE: # Different MAJOR version
   → BLOCK import
   → Require manual migration
   → Provide migration guide
```

---

## BREAKING CHANGES LOG

### 4.2.0 Breaking Changes
**Date:** 2025-09-01

**Change 1: Enhanced Headers**
- **What Changed:** Added mandatory fields to file headers
- **Old Format:**
  ```markdown
  **Version:** 1.0.0
  **Date:** 2025-08-01
  **Purpose:** Description
  ```
- **New Format:**
  ```markdown
  **Version:** 1.0.0
  **Date:** 2025-08-01
  **Purpose:** Description
  **Category:** lessons
  **SIMA Version:** 4.2.0
  ```
- **Migration:** Auto-add missing fields during import
- **Impact:** Low (auto-upgrade available)

---

### 4.1.0 Breaking Changes
**Date:** 2025-05-01

**Change 1: REF-ID Format Enhancement**
- **What Changed:** REF-ID format standardization
- **Old Format:** Inconsistent (LESS-1, LESS-01, LESS-001)
- **New Format:** Consistent (LESS-01, always 2-digit)
- **Migration:** REF-ID remapping table required
- **Impact:** Medium (requires mapping)

**Change 2: Domain Organization**
- **What Changed:** Introduced domain hierarchy
- **Old Format:** Flat `/lessons/LESS-01.md`
- **New Format:** `/generic/lessons/LESS-01.md`
- **Migration:** Move files to correct domain
- **Impact:** High (file relocation required)

---

### 4.0.0 Breaking Changes
**Date:** 2025-01-15

**Change 1: Complete Restructure**
- **What Changed:** Everything
- **Migration:** Manual, file-by-file
- **Impact:** Critical (no auto-upgrade)

---

## AUTO-UPGRADE PATHS

### 4.1.x → 4.2.x
**Automatic Upgrades Available:**

1. **Header Enhancement**
   ```python
   def upgrade_header_4_1_to_4_2(content):
       lines = content.split('\n')
       header_end = find_header_end(lines)
       
       # Add new fields
       new_fields = [
           "**Category:** " + extract_category_from_path(),
           "**SIMA Version:** 4.2.0"
       ]
       
       lines.insert(header_end, new_fields)
       return '\n'.join(lines)
   ```

2. **REF-ID Validation**
   - Ensure all REF-IDs are 2-digit format
   - Update references automatically

---

### 4.0.x → 4.1.x
**Automatic Upgrades Available:**

1. **Domain Assignment**
   ```python
   def upgrade_domain_4_0_to_4_1(file_path):
       # Determine appropriate domain
       if is_generic_content(file_path):
           return '/generic/' + file_path
       elif is_platform_specific(file_path):
           return '/platforms/' + detect_platform() + '/' + file_path
       # etc.
   ```

---

## COMPATIBILITY TESTING

### Test Cases

**Test 1: Same Version Import**
```
Source: 4.2.2
Target: 4.2.2
Expected: ✅ Direct import, no warnings
```

**Test 2: Patch Upgrade**
```
Source: 4.2.0
Target: 4.2.2
Expected: ✅ Direct import, no modifications
```

**Test 3: Minor Upgrade**
```
Source: 4.1.5
Target: 4.2.2
Expected: ⚠️  Auto-upgrade, headers enhanced
```

**Test 4: Major Version Gap**
```
Source: 3.x
Target: 4.2.2
Expected: ❌ Blocked, migration required
```

---

## FUTURE VERSION PLANNING

### Proposed 4.3.0 (Future)
**Planned Features:**
- Enhanced metadata
- New file types
- Improved cross-referencing

**Compatibility Plan:** Backward compatible with 4.2.x

---

### Proposed 5.0.0 (Future)
**Planned Changes:**
- New architecture
- Different organization

**Compatibility Plan:** Breaking changes, manual migration required

---

## REFERENCE

**Import Mode Context:** `/sima/context/sima/context-SIMA-IMPORT-MODE-Context.md`  
**Implementation Plan:** SIMA Knowledge Archive System - Implementation Plan.md  
**Related:** IMPORT-WORKFLOW-GUIDE.md

---

**END OF VERSION COMPATIBILITY MATRIX**

**Purpose:** Define version compatibility rules  
**Scope:** All SIMA imports  
**Maintenance:** Update with each version release
