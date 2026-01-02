# Templates-Index.md

**Version:** 2.0.0  
**Date:** 2025-12-07  
**Purpose:** Complete catalog of SIMA templates  
**Category:** Index  
**Location:** `/sima/support/templates/`

---

## OVERVIEW

**What:** Centralized index of all template files in SIMA system

**Purpose:**
- Quick access to templates
- Template selection guidance
- Usage examples
- Cross-references

**Total Templates:** 4

---

## AVAILABLE TEMPLATES

### Documentation Templates

#### TMPL-01: Neural Map Entry Template

**File:** TMPL-01-Neural-Map-Entry.md  
**REF-ID:** TMPL-01  
**Version:** 1.0.0  
**Category:** Entry Creation  
**Purpose:** Standard structure for all neural map entries

**Use For:**
- Creating LESS (Lessons)
- Creating AP (Anti-Patterns)
- Creating DEC (Decisions)
- Creating BUG (Bug Reports)
- Creating WISD (Wisdom)
- Creating any neural map entry type

**Sections Included:**
- Header Block (REF-ID, metadata)
- Overview (summary, context, impact)
- Core Content (type-specific)
- Examples (good/bad)
- Keywords & Cross-References
- Quality Checklist

**When to Use:**
- ✅ Creating any new neural map entry
- ✅ Documenting lessons learned
- ✅ Recording anti-patterns
- ✅ Capturing decisions
- ❌ Creating project documentation
- ❌ Writing general docs

**Example Output:** LESS-42, AP-25, DEC-15

**Related:** SPEC-FILE-STANDARDS.md, SPEC-HEADERS.md

---

#### TMPL-02: Project Documentation Template

**File:** TMPL-02-Project-Documentation.md  
**REF-ID:** TMPL-02  
**Version:** 1.0.0  
**Category:** Project Setup  
**Purpose:** Standard structure for project-specific documentation (NMP)

**Use For:**
- Starting new project
- Documenting existing project
- Creating project neural maps
- Establishing project standards

**Sections Included:**
- Project README structure
- project.md (configuration)
- NMP00-Master-Index structure
- Directory layout
- Standards and conventions

**When to Use:**
- ✅ Starting new project
- ✅ Setting up project docs
- ✅ Creating NMP structure
- ✅ Establishing project standards
- ❌ Creating individual entries
- ❌ General documentation

**Example Output:** Project README, project.md, NMP00 indexes

**Related:** Project setup workflow

---

### Code Templates (NEW)

#### code-file-header.txt

**File:** code-file-header.txt  
**Version:** 1.0.0  
**Category:** Code Standards  
**Purpose:** Minimal 5-line code file header template

**Format:**
```python
"""
{filename}.py
Version: {YYYY-MM-DD_R}
Purpose: {One-line description}
License: {License name}
"""
```

**Use For:**
- Python files
- JavaScript files (adapt to /** ... */)
- Any source code files
- Configuration files

**When to Use:**
- ✅ Creating new code file
- ✅ Updating file headers to new format
- ✅ Migrating from verbose headers
- ❌ Documentation files (use SPEC-HEADERS.md format)

**Benefits:**
- 5 lines vs 35+ lines (86% reduction)
- Date-based versioning (YYYY-MM-DD_R)
- No changelog clutter
- Clean, minimal format

**Example:**
```python
"""
lambda_function.py
Version: 2025-12-06_2
Purpose: AWS Lambda entry point for LEE
License: Apache 2.0
"""
```

**Related:** Version-Standards.md, Artifact-Standards.md, File-Standards.md

---

#### companion-file-template.md

**File:** companion-file-template.md  
**Version:** 1.0.0  
**Category:** Documentation  
**Purpose:** Comprehensive documentation template for code files

**Use For:**
- Code file documentation
- Function documentation
- Module documentation
- API documentation

**Sections Included:**
1. **Purpose** - Module overview
2. **Architecture** - Module position and integration
3. **Functions** - Detailed function documentation
4. **Usage Examples** - Code examples (basic, advanced, error handling)
5. **Error Handling** - Exception types and recovery
6. **Performance** - Timing and optimization
7. **Testing** - Test coverage and scenarios
8. **Dependencies** - External and internal dependencies
9. **Configuration** - Environment variables and parameters
10. **Debugging** - Debug flags and common issues
11. **Changelog** - Version history
12. **Related** - Related modules and documentation

**When to Use:**
- ✅ Every code file needs companion .md
- ✅ Documenting complex modules
- ✅ API documentation
- ✅ Function catalogs
- ❌ Simple scripts (<50 lines)
- ❌ Throwaway code

**Benefits:**
- Separates code from documentation
- Comprehensive function documentation
- Usage examples included
- Changelog outside code
- ≤350 lines (same as code)

**Example:**
```
ha_alexa_core.py         (280 lines) - Code only
ha_alexa_core.md         (300 lines) - Full docs
```

**Related:** File-Standards.md, Artifact-Standards.md

---

## TEMPLATE COVERAGE

| Entry Type | Template Available | Template ID |
|------------|-------------------|-------------|
| LESS | ✅ YES | TMPL-01 |
| AP | ✅ YES | TMPL-01 |
| DEC | ✅ YES | TMPL-01 |
| BUG | ✅ YES | TMPL-01 |
| WISD | ✅ YES | TMPL-01 |
| ARCH | ⚠️ Use existing | - |
| INT | ⚠️ Use existing | - |
| LANG | ⚠️ Use existing | - |
| **Project Docs** | **✅ YES** | **TMPL-02** |
| **NMP** | **✅ YES** | **TMPL-02** |
| **Code Headers** | **✅ YES (NEW)** | **code-file-header.txt** |
| **Code Docs** | **✅ YES (NEW)** | **companion-file-template.md** |

---

## TEMPLATE SELECTION GUIDE

### Decision Tree

```
Need to create documentation?
    ↓
    ├──> Is it a neural map entry (LESS, AP, DEC, etc.)?
    │    └──> YES: Use TMPL-01 (Neural Map Entry Template)
    │
    ├──> Is it project-level documentation?
    │    └──> YES: Use TMPL-02 (Project Documentation Template)
    │
    ├──> Is it a code file?
    │    ├──> Header only? Use code-file-header.txt
    │    └──> Full documentation? Use companion-file-template.md
    │
    └──> Other documentation?
         └──> Use SPEC-FILE-STANDARDS.md for guidance
```

### Quick Selection

**For entries:** TMPL-01  
**For projects:** TMPL-02  
**For code headers:** code-file-header.txt  
**For code docs:** companion-file-template.md

---

## TEMPLATE USAGE

### Neural Map Entry (TMPL-01)

**Steps:**
1. Copy TMPL-01-Neural-Map-Entry.md
2. Rename to TYPE-##.md (e.g., LESS-42.md)
3. Fill in header (version, date, purpose)
4. Complete all sections
5. Add keywords and cross-references
6. Run quality checklist
7. Update relevant indexes

**Time:** 15-30 minutes

---

### Project Documentation (TMPL-02)

**Steps:**
1. Copy TMPL-02-Project-Documentation.md
2. Create project directory structure
3. Fill in project metadata
4. Customize sections for project
5. Create indexes
6. Link to master indexes

**Time:** 1-2 hours

---

### Code File Header (code-file-header.txt)

**Steps:**
1. Copy header template
2. Replace {filename} with actual filename
3. Set version to current date (YYYY-MM-DD_1)
4. Write one-line purpose
5. Set license
6. Paste at top of code file

**Time:** 1 minute

**Example:**
```python
"""
cache_core.py
Version: 2025-12-06_1
Purpose: Core cache operations implementation
License: Apache 2.0
"""
```

---

### Code Documentation (companion-file-template.md)

**Steps:**
1. Copy companion-file-template.md
2. Rename to {code_filename}.md
3. Fill in module info
4. Document each function
5. Add usage examples
6. Include changelog
7. Link related items

**Time:** 30-60 minutes per module

**Example:**
```
cache_core.py           (250 lines) - Implementation
cache_core.md           (280 lines) - Documentation
```

---

## MAINTAINING TEMPLATES

### Update Process

**When to Update:**
- Structure changes in entry format
- New required sections added
- Quality standards change
- Examples become outdated
- New features added

**How to Update:**
1. Open template file
2. Make changes
3. Update "Last Updated" date
4. Update version number
5. Test with new entry creation
6. Update this index
7. Notify team

**Version Control:**
- Templates use semantic versioning (X.Y.Z)
- MAJOR: Breaking changes to structure
- MINOR: New sections or examples
- PATCH: Corrections and clarifications

---

## QUALITY ASSURANCE

### Template Validation

**Before using template:**
- [ ] Template file exists
- [ ] Version current
- [ ] All sections present
- [ ] Examples included
- [ ] Instructions clear
- [ ] ≤350 lines (if applicable)

**After using template:**
- [ ] All sections filled
- [ ] Cross-references added
- [ ] Keywords included
- [ ] Quality checklist passed
- [ ] Indexes updated

---

## RELATED DOCUMENTATION

**Standards:**
- SPEC-FILE-STANDARDS.md - Universal file standards
- SPEC-HEADERS.md - Header requirements
- Version-Standards.md - Version format
- File-Standards.md - File organization
- Artifact-Standards.md - Code artifacts

**Indexes:**
- Specifications-Index.md - All specifications
- Master-Index-of-Indexes.md - All indexes
- Support-Master-Index.md - Support resources

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-12-07 | Added code-file-header.txt and companion-file-template.md |
| 1.0.0 | 2025-11-01 | Initial templates index with TMPL-01 and TMPL-02 |

---

**END OF FILE**

**Summary:** 4 templates covering neural maps, projects, code headers, and code documentation.
