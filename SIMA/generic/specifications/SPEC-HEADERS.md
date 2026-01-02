# SPEC-HEADERS.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Header requirements for all SIMA files  
**Category:** Specifications

---

## PURPOSE

Define mandatory header format for all SIMA files to ensure consistency, traceability, and discoverability.

---

## MANDATORY HEADER FORMAT

```markdown
# filename.md

**Version:** (Year).(Month).(Day)-(Revision)
**Purpose:** [Very Brief description]  
**Category:** [Category name]
```

---

## HEADER FIELDS

### Filename (Required)
**Format:** `# filename.md`  
**Rules:**
- H1 heading (single #)
- Must match actual filename
- Include file extension
- First line of file

**Example:**
```markdown
# LESS-15-Verification-Protocol.md
```

### Version (Required)
**Format:** `**Version:** (Year).(Month).(Day)-(Revision)'
**Rules:**
- Semantic versioning (MAJOR.MINOR.PATCH)
- Bold label, regular version number
- Start at current date only for new files
- Increment according to change type

**Examples:**
```markdown
**Version:** 2025.11.10  (Initial)
**Version:** 2025.11.10-1  (Patch/fix)
**Version:** 2025.11.10-2  (Minor addition)
**Version:** 2025.11.10-3  (Breaking change)
```

### Date (Required)
**Format:** `**Date:** YYYY-MM-DD`  
**Rules:**
- ISO 8601 format
- Date of last significant update
- Bold label, regular date
- Use UTC/local consistently

**Examples:**
```markdown
**Date:** 2025-11-10
**Date:** 2025-01-15
```

### Purpose (Required)
**Format:** `**Purpose:** [Very Brief description]`  
**Rules:**
- Max 100 characters
- Describes what file does
- Action-oriented language
- No period at end

**Examples:**
```markdown
**Purpose:** Define verification protocol for code changes
**Purpose:** Document cache sanitization bug and fix
**Purpose:** Gateway pattern implementation guide
```

### Category (Required)
**Format:** `**Category:** [Category name]`  
**Rules:**
- Identifies file type/domain
- Helps with organization
- Used for filtering/search

**Categories:**
- Specifications
- Core Architecture
- Gateways
- Interfaces
- Lessons
- Decisions
- Anti-Patterns
- Bugs
- Wisdom
- Platform Specific
- Language Specific
- Project Specific
- Support
- Tools
- Workflows

**Examples:**
```markdown
**Category:** Specifications
**Category:** Core Architecture
**Category:** Lessons - Operations
```

---

## OPTIONAL HEADER FIELDS

### Status (Optional)
**Format:** `**Status:** [Status value]`  
**Values:**
- Draft
- Active
- Deprecated
- Archived
- Under Review

**When to use:**
- Draft: Work in progress
- Deprecated: Superseded by newer entry
- Archived: Historical reference only

### Author (Optional)
**Format:** `**Author:** [Name]`  
**When to use:** Attribution needed

### Related (Optional)
**Format:** `**Related:** REF-ID-1, REF-ID-2`  
**When to use:** Strong dependencies on other entries

---

## SPACING

```markdown
# filename.md

**Version:** 2025.11.10
**Purpose:** Very Brief description  
**Category:** Category name

---

## FIRST SECTION
```

**Rules:**
- Blank line after H1
- Two spaces after each field for alignment
- Horizontal rule (---) after header
- Blank line before first section

---

## VALIDATION

### Checklist
- [ ] H1 heading with filename
- [ ] Version in (Year).(Month).(Day)-(Revision) format
- [ ] Purpose under 100 chars
- [ ] Category specified
- [ ] Proper spacing
- [ ] Horizontal rule present

### Automated Checks
```python
def validate_header(file_content):
    lines = file_content.split('\n')
    
    # Check H1
    if not lines[0].startswith('# '):
        return False, "Missing H1 heading"
    
    # Check version
    if '**Version:**' not in lines[2]:
        return False, "Missing version"
    
    # Check purpose
    if '**Purpose:**' not in lines[4]:
        return False, "Missing purpose"
    
    # Check category
    if '**Category:**' not in lines[5]:
        return False, "Missing category"
    
    return True, "Header valid"
```

---

## VERSION UPDATES

### When to Update Version

**PATCH (Year.Month.Day → Year.Month.Day-Revision+1):**
- Typo fixes
- Clarifications
- Formatting improvements
- Minor corrections

**MINOR (Year.Month.Day → Year.Month.Day-Revision+1):**
- New sections added
- Significant examples added
- Related content expanded
- Non-breaking enhancements

**MAJOR (Year.Month.Day → Year.Month.Day-Revision+1):**
- Complete restructuring
- Breaking changes
- Different approach
- Incompatible updates

### Update Both
When updating version, also update date:
```markdown
**Version:** 2025.11.10
```

---

## EXAMPLES

### Neural Map Entry
```markdown
# LESS-15-Verification-Protocol.md

**Version:** 2025.11.10
**Purpose:** 5-step verification checklist for code changes  
**Category:** Lessons - Operations

---
```

### Specification File
```markdown
# SPEC-HEADERS.md

**Version:** 2025.11.10
**Purpose:** Header requirements for all SIMA files  
**Category:** Specifications

---
```

### Decision Entry
```markdown
# DEC-04-No-Threading.md

**Version:** 2025.11.10
**Purpose:** Why threading is prohibited in environments  
**Category:** Decisions - Architecture

---
```

### With Optional Fields
```markdown
# ARCH-SUGA.md

**Version:** 2025-11-10
**Purpose:** Complete SUGA architecture pattern documentation  
**Category:** Core Architecture  
**Status:** Active  
**Related:** GATE-01, GATE-02, INT-01

---
```

---

## BENEFITS

**Consistent headers provide:**
- Quick identification (filename visible)
- Version tracking (know what changed)
- Freshness indicator (date shows currency)
- Clear purpose (understand at glance)
- Proper categorization (filtering/search)
- Professional appearance

---

**Related:**
- SPEC-FILE-STANDARDS.md
- SPEC-MARKDOWN.md
- SPEC-CHANGELOG.md

**Version History:**
- v4.2.2-blank (2025-11-10): Blank slate version
- v1.0.0 (2025-11-06): Initial header specification

---


**END OF FILE**
