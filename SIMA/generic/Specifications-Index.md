# Specifications-Index.md

**Version:** 2.0.0  
**Date:** 2025-12-07  
**Purpose:** Index of all SIMA specification files  
**Category:** Index  
**Location:** `/sima/entries/specifications/`

---

## OVERVIEW

**What:** Complete catalog of specification files defining SIMA standards

**Purpose:**
- Quick reference to standards
- Standard compliance verification
- Quality assurance
- Onboarding reference

**Total Specifications:** 12

---

## CORE STANDARDS

### SPEC-FILE-STANDARDS.md
**Version:** 1.0.0  
**Purpose:** Universal file standards for all SIMA content  
**Coverage:**
- Mandatory headers
- File types (neural maps, specs, context, support)
- Encoding requirements
- Formatting standards
- Version control
- Cross-references
- Quality checklist

**Related:** All other SPEC files

---

### File-Standards.md
**Version:** 2.0.0 (UPDATED)  
**Purpose:** File organization and size standards  
**Location:** `/sima/shared/`  
**Coverage:**
- 350-line hard limit (NEW)
- Code file standards (NEW)
- Companion documentation pattern (NEW)
- Comment reduction guidelines (NEW)
- File splitting strategy
- Version format (date-based for code)
- Changelog location

**Changes in v2.0:**
- Reduced limit from 400 to 350 lines
- Added code file standards
- Added companion .md documentation
- Updated version format to YYYY-MM-DD_R for code
- Moved changelogs to companion files

**Related:** Version-Standards.md, Artifact-Standards.md

---

### Artifact-Standards.md
**Version:** 2.0.0 (UPDATED)  
**Purpose:** Standards for all code artifacts  
**Location:** `/sima/shared/`  
**Coverage:**
- Complete files only (never fragments)
- Minimal headers (5 lines vs 35+)
- Change marking (ADDED, MODIFIED, FIXED)
- 350-line limit enforcement
- Code + documentation pattern
- Chat output minimization

**Changes in v2.0:**
- New minimal header format (5 lines)
- Date-based versioning (YYYY-MM-DD_R)
- Companion .md file requirement
- 350-line hard limit
- Removed changelogs from code headers

**Related:** File-Standards.md, Version-Standards.md

---

### Version-Standards.md (NEW)
**Version:** 1.0.0  
**Purpose:** Version format standards for code and documentation  
**Location:** `/sima/shared/`  
**Coverage:**
- Date-based format (YYYY-MM-DD_R) for code
- Semantic versioning (X.Y.Z) for docs
- Increment rules
- File header formats
- Changelog locations
- Migration guide

**Key Patterns:**
- Code files: `2025-12-06_1` (date + daily revision)
- Documentation: `1.0.0` (semantic)
- R resets to 1 each new day
- Changelogs in companion .md files

**Related:** File-Standards.md, Artifact-Standards.md

---

## DETAILED SPECIFICATIONS

### SPEC-LINE-LIMITS.md
**Version:** 1.0.0  
**Purpose:** Enforce 400-line limits per file  
**Coverage:**
- Per-file limits (not batched)
- File type limits
- When to batch
- Split strategies
- Quality enforcement

**Note:** Generic limit is 400, but code files now 350 per File-Standards.md v2.0

**Related:** File-Standards.md

---

### SPEC-HEADERS.md
**Version:** 1.0.0  
**Purpose:** Header requirements for all SIMA files  
**Coverage:**
- Mandatory header format
- Required fields (filename, version, date, purpose, category)
- Optional fields
- Spacing rules
- Validation checklist
- Version update rules

**Related:** SPEC-FILE-STANDARDS.md

---

### SPEC-NAMING.md
**Version:** 1.0.0  
**Purpose:** File and directory naming conventions  
**Coverage:**
- Neural map entry format (TYPE-##.md)
- Specification format (SPEC-NAME.md)
- Context file format
- Support file format
- Index file format
- Project file format
- Directory naming

**Related:** SPEC-FILE-STANDARDS.md

---

### SPEC-ENCODING.md
**Version:** 1.0.0  
**Purpose:** Character encoding standards  
**Coverage:**
- UTF-8 encoding requirement
- BOM handling
- Line endings (LF only)
- Special characters
- Emoji support
- Validation

**Related:** SPEC-FILE-STANDARDS.md

---

### SPEC-STRUCTURE.md
**Version:** 1.0.0  
**Purpose:** Document structure standards  
**Coverage:**
- Standard sections
- Section ordering
- Nesting limits
- Navigation patterns
- Cross-referencing

**Related:** SPEC-FILE-STANDARDS.md

---

### SPEC-MARKDOWN.md
**Version:** 1.0.0  
**Purpose:** Markdown formatting standards  
**Coverage:**
- CommonMark compliance
- Headers (ATX style)
- Lists formatting
- Code blocks
- Tables
- Links
- Emphasis

**Related:** SPEC-FILE-STANDARDS.md

---

### SPEC-CHANGELOG.md
**Version:** 1.0.0  
**Purpose:** Changelog format and location  
**Coverage:**
- Version history format
- Changelog location
- Entry structure
- Date format
- Migration notes

**Related:** Version-Standards.md

---

### SPEC-FUNCTION-DOCUMENTATION.md
**Version:** 1.0.0  
**Purpose:** Function documentation standards  
**Coverage:**
- Docstring format
- Parameter documentation
- Return value documentation
- Exception documentation
- Examples
- Performance notes

**Related:** Artifact-Standards.md, companion-file-template.md

---

## PROJECT-SPECIFIC SPECIFICATIONS

### Debug-System-Specification.md (NEW)
**Version:** 1.0.0  
**Purpose:** Universal debug infrastructure specification  
**Project:** LEE  
**Location:** `/sima/shared/` or `/sima/projects/lee/`  
**Coverage:**
- Hierarchical debug control
- Master + scope flags
- Environment variables
- Usage patterns
- Output format
- Performance overhead
- Implementation details
- Migration guide

**Key Features:**
- DEBUG_MODE master switch
- {SCOPE}_DEBUG_MODE per-component
- {SCOPE}_DEBUG_TIMING per-component
- Single-line debug calls
- Context manager for timing

**Related:** File-Standards.md (for line reduction)

---

## TEMPLATES

### code-file-header.txt (NEW)
**Version:** 1.0.0  
**Purpose:** Minimal 5-line code file header template  
**Location:** `/sima/templates/`  
**Format:**
```
"""
{filename}.py
Version: {YYYY-MM-DD_R}
Purpose: {One-line description}
License: {License name}
"""
```

**Related:** Version-Standards.md, Artifact-Standards.md

---

### companion-file-template.md (NEW)
**Version:** 1.0.0  
**Purpose:** Comprehensive documentation template for code files  
**Location:** `/sima/templates/`  
**Sections:**
- Purpose
- Architecture
- Functions (detailed)
- Usage examples
- Error handling
- Performance
- Testing
- Dependencies
- Configuration
- Debugging
- Changelog
- Related items

**Related:** File-Standards.md, Artifact-Standards.md

---

## QUALITY CHECKLIST

**Before finalizing any specification:**
- [ ] Version number appropriate
- [ ] Date current
- [ ] Purpose clear and concise
- [ ] Category specified
- [ ] Coverage complete
- [ ] Examples included
- [ ] Related specs cross-referenced
- [ ] File ≤350 lines
- [ ] Proper encoding (UTF-8, LF)
- [ ] No trailing whitespace

---

## USAGE GUIDE

### Finding Right Specification

**For file creation:**
1. SPEC-FILE-STANDARDS.md (overall)
2. SPEC-HEADERS.md (header format)
3. SPEC-NAMING.md (file naming)

**For file content:**
1. SPEC-STRUCTURE.md (organization)
2. SPEC-MARKDOWN.md (formatting)
3. SPEC-LINE-LIMITS.md (size limits)

**For code files:**
1. File-Standards.md (overall standards)
2. Artifact-Standards.md (artifact creation)
3. Version-Standards.md (versioning)
4. code-file-header.txt (header template)
5. companion-file-template.md (documentation)

**For versioning:**
1. Version-Standards.md (version format)
2. SPEC-CHANGELOG.md (changelog format)

---

## RELATED INDEXES

- Templates-Index.md (templates catalog)
- Master-Index-of-Indexes.md (all indexes)
- Shared-Standards-Index.md (shared standards)

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-12-07 | Added Version-Standards, Debug-System, templates; updated File/Artifact Standards to v2.0 |
| 1.0.0 | 2025-11-06 | Initial specifications index |

---

**END OF FILE**

**Summary:** Complete catalog of 12 SIMA specifications + 2 templates covering all standards and guidelines.
