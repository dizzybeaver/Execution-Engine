# Shared-Standards-Index.md

**Version:** 2.0.0  
**Date:** 2025-12-07  
**Purpose:** Index of shared knowledge and standards files  
**Category:** Index  
**Location:** `/sima/shared/`

---

## OVERVIEW

**What:** Catalog of shared standards, patterns, and reference files

**Purpose:**
- Quick access to universal standards
- Cross-project reference
- Quality guidelines
- Best practices

**Total Files:** 5 core standards + supporting files

---

## CORE STANDARDS

### File-Standards.md
**Version:** 2.0.0 (UPDATED)  
**Date:** 2025-12-07  
**Purpose:** File organization and size standards  

**Coverage:**
- **350-line hard limit** (reduced from 400)
- Code file standards (NEW)
- Companion documentation (NEW)
- Comment reduction (NEW)
- File splitting strategy
- Version format (date-based for code)
- Changelog location

**Major Changes in v2.0:**
- Hard limit reduced to 350 lines (was 400)
- Added code-specific standards
- Introduced companion .md pattern
- Minimal headers for code (5 lines)
- Date-based versioning for code files
- Changelogs moved to companion files

**Impact:**
- 86% reduction in header size (35→5 lines)
- Cleaner code files
- Better Claude visibility (<400 lines)
- Separate documentation

**Related:** Artifact-Standards.md, Version-Standards.md

---

### Artifact-Standards.md
**Version:** 2.0.0 (UPDATED)  
**Date:** 2025-12-07  
**Purpose:** Standards for all code artifacts

**Coverage:**
- Complete files only (never fragments)
- Minimal headers (NEW: 5 lines)
- Change marking (ADDED, MODIFIED, FIXED)
- 350-line limit enforcement (NEW)
- Code + documentation pattern (NEW)
- Chat output minimization

**Major Changes in v2.0:**
- New minimal header format (5 lines vs 35+)
- Date-based versioning (YYYY-MM-DD_R)
- Companion .md requirement
- 350-line hard limit
- Removed changelogs from code

**Impact:**
- Cleaner artifacts
- Easier to review
- Better maintainability
- Reduced token usage

**Related:** File-Standards.md, Version-Standards.md

---

### Version-Standards.md (NEW)
**Version:** 1.0.0  
**Date:** 2025-12-07  
**Purpose:** Version format standards for code and documentation

**Coverage:**
- Date-based format (YYYY-MM-DD_R) for code
- Semantic versioning (X.Y.Z) for docs
- Increment rules
- File header formats
- Changelog locations
- Migration guide

**Key Patterns:**
```
Code:    2025-12-06_1 (date + daily revision)
Docs:    1.0.0 (semantic versioning)
```

**Rules:**
- R (revision) resets to 1 each new day
- R increments for same-day changes
- Changelogs in companion .md files (code)
- Changelogs in file or CHANGELOG.md (docs)

**Benefits:**
- Chronological sorting automatic
- Clear deployment timeline
- No arbitrary versions
- Multiple revisions per day supported

**Related:** File-Standards.md, Artifact-Standards.md

---

### Encoding-Standards.md
**Version:** 1.0.0  
**Date:** 2025-11-06  
**Purpose:** Character encoding standards

**Coverage:**
- UTF-8 encoding requirement
- BOM handling (optional)
- Line endings (LF only, no CRLF)
- Special characters
- Emoji support
- Validation

**Critical Rules:**
- UTF-8 encoding mandatory
- LF line endings only (Unix style)
- No trailing whitespace
- Final newline required

**Related:** SPEC-ENCODING.md, SPEC-FILE-STANDARDS.md

---

### Common-Patterns.md
**Version:** 1.0.0  
**Date:** 2025-11-06  
**Purpose:** Reusable patterns across projects

**Coverage:**
- Import patterns (lazy loading)
- Error handling patterns
- Validation patterns
- Logging patterns
- Configuration patterns
- Testing patterns

**Use Cases:**
- Quick pattern reference
- Implementation examples
- Best practices
- Code templates

**Related:** Architecture-specific patterns in `/languages/` and `/platforms/`

---

## SUPPORTING FILES

### RED-FLAGS.md
**Version:** 1.0.0  
**Purpose:** Universal anti-patterns and warnings

**Content:**
- Critical mistakes to avoid
- Common pitfalls
- Security risks
- Performance issues

**Examples:**
- ❌ Threading in Lambda
- ❌ Direct core imports
- ❌ Bare except clauses
- ❌ Module-level imports (cold path)

**Related:** Anti-Patterns entries, SUGA architecture

---

### SUGA-Architecture.md
**Version:** 1.0.0  
**Purpose:** SUGA pattern reference

**Content:**
- Gateway layer pattern
- Interface layer pattern
- Core layer pattern
- Import rules
- Dependency flow

**Related:** `/languages/python/architectures/suga/`

---

## PROJECT-SPECIFIC STANDARDS

### Debug-System-Specification.md (NEW)
**Version:** 1.0.0  
**Date:** 2025-12-07  
**Purpose:** Universal debug infrastructure specification

**Project:** LEE (applicable to others)  
**Location:** `/sima/shared/` or project-specific

**Coverage:**
- Hierarchical debug control
- Master + scope-specific flags
- Environment variables (DEBUG_MODE, etc.)
- Usage patterns
- Output format
- Performance overhead
- Implementation details
- Migration guide

**Key Features:**
- Single-line debug calls
- Master switch (DEBUG_MODE)
- Per-component flags ({SCOPE}_DEBUG_MODE)
- Timing measurement ({SCOPE}_DEBUG_TIMING)
- Minimal overhead when disabled

**Impact:**
- 26% file size reduction (typical)
- 10+ lines → 1 line per debug point
- Granular component debugging
- Production-safe operation

**Related:** File-Standards.md (line reduction)

---

## TEMPLATES

### code-file-header.txt (NEW)
**Version:** 1.0.0  
**Location:** `/sima/templates/`  
**Purpose:** Minimal code file header

**Format:**
```python
"""
{filename}.py
Version: {YYYY-MM-DD_R}
Purpose: {One-line description}
License: {License name}
"""
```

**Benefits:**
- 5 lines (vs 35+ previously)
- Clean, minimal
- Date-based versioning
- No changelog clutter

**Related:** Version-Standards.md, Artifact-Standards.md

---

### companion-file-template.md (NEW)
**Version:** 1.0.0  
**Location:** `/sima/templates/`  
**Purpose:** Comprehensive code documentation template

**Sections:**
- Purpose, Architecture, Functions
- Usage Examples, Error Handling
- Performance, Testing, Dependencies
- Configuration, Debugging
- Changelog, Related items

**Usage:**
- One .md per .py file
- Detailed function docs
- Usage examples
- Version history

**Benefits:**
- Separates docs from code
- Comprehensive documentation
- ≤350 lines (same as code)
- Easy to maintain

**Related:** File-Standards.md, Artifact-Standards.md

---

## QUICK REFERENCE

### For File Creation

**Code files:**
1. File-Standards.md (overall)
2. code-file-header.txt (header)
3. companion-file-template.md (documentation)
4. Version-Standards.md (versioning)

**Documentation files:**
1. File-Standards.md (overall)
2. SPEC-HEADERS.md (header format)
3. SPEC-FILE-STANDARDS.md (complete standards)

**All files:**
1. Encoding-Standards.md (encoding/line endings)
2. Artifact-Standards.md (if code)

---

### For Standards Compliance

**Checklist:**
- [ ] File ≤350 lines
- [ ] UTF-8 encoding
- [ ] LF line endings
- [ ] No trailing whitespace
- [ ] Final newline present
- [ ] Proper header format
- [ ] Version format correct
- [ ] Companion .md exists (code files)
- [ ] Changelog in right location

---

### Version Format Quick Guide

**Code:**
```
Format: YYYY-MM-DD_R
Example: 2025-12-06_2
R resets daily
```

**Documentation:**
```
Format: X.Y.Z
Example: 1.2.0
Semantic versioning
```

---

## RELATED INDEXES

**Main Indexes:**
- Specifications-Index.md - All SPEC files
- Templates-Index.md - All templates
- Master-Index-of-Indexes.md - All indexes

**Category Indexes:**
- Anti-Patterns-Master-Index.md
- Lessons-Master-Index.md
- Decisions-Master-Index.md

---

## MIGRATION GUIDE

### Updating to v2.0 Standards

**For existing code files:**

**Step 1:** Update header
```python
# Old (35+ lines)
"""
filename.py - Long Description (INT-XX-XX)
Version: 4.3.0
... [many lines of changelog] ...
"""

# New (5 lines)
"""
filename.py
Version: 2025-12-06_1
Purpose: One-line description
License: Apache 2.0
"""
```

**Step 2:** Create companion .md
- Use companion-file-template.md
- Move detailed docs from code
- Move changelog from code
- Document all functions

**Step 3:** Check file size
- If >300 lines, plan split
- If >350 lines, split immediately
- Use logical module boundaries

**Step 4:** Update indexes
- Update relevant indexes
- Cross-reference new files
- Verify all links

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-12-07 | Updated File/Artifact Standards to v2.0; added Version-Standards, Debug-System, templates |
| 1.0.0 | 2025-11-06 | Initial shared standards index |

---

**END OF FILE**

**Summary:** 5 core standards (3 updated to v2.0) + debug spec + 2 templates for universal code and documentation standards.
