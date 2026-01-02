# context-SIMA-BASE-MODE.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Base SIMA Mode context for all SIMA operations  
**Type:** Base Context

---

## WHAT THIS IS

**SIMA Base Mode** provides common context for all SIMA-specific operations.

**Loaded by:** All SIMA modes (Project, Learning, Maintenance, Export, Import)

---

## SIMA PROJECT

**Name:** SIMA (Structured Intelligence Memory Architecture)  
**Type:** Knowledge Management System  
**Platform:** Documentation (Markdown)  
**Organization:** Domain-based (generic/platform/language/project)

---

## CONSTRAINTS

**File Standards:**
- Markdown only (.md)
- ≤400 line limit (strict)
- UTF-8 encoding
- LF line endings
- Headers required

**Organization:**
- Domain separation mandatory
- No project-specifics in generic
- Atomic focused files
- Cross-reference with REF-IDs

**Quality:**
- Check duplicates before creating
- Update indexes after changes
- Verify all REF-IDs exist
- Split files >400 lines

---

## ARCHITECTURE

### Domain Separation
```
Generic (/generic/)
  ↓
Platform (/platforms/)
  ↓
Language (/languages/)
  ↓
Project (/projects/)
```

### Knowledge Organization
- Hierarchical 4-layer system
- Atomic files (≤400 lines)
- Categories: lessons, decisions, anti-patterns, specifications
- Cross-reference with REF-IDs
- Index maintenance required

### Mode System
- General Mode: Q&A and guidance
- Learning Mode: Extract knowledge
- Maintenance Mode: Update indexes
- Project Mode: Build features
- Export Mode: Export knowledge
- Import Mode: Import knowledge

---

## PATTERNS

### File Header
```markdown
# FILENAME.md

**Version:** X.Y.Z
**Date:** YYYY-MM-DD
**Purpose:** [Brief description]
**Category:** [Category name]
```

### Index Entry
```markdown
- [TYPE-## - Title](/path/to/TYPE-##.md) - Brief description
```

### Cross-Reference
```markdown
**REF:** TYPE-ID1, TYPE-ID2, TYPE-ID3
```

---

## RED FLAGS

**SIMA-Specific:**
- ❌ Project-specifics in generic entries
- ❌ Files exceeding 400 lines
- ❌ Condensed multi-topic files
- ❌ Missing cross-references
- ❌ Broken REF-IDs
- ❌ Outdated indexes
- ❌ Duplicate entries
- ❌ Missing headers
- ❌ Wrong encoding (not UTF-8)
- ❌ Wrong line endings (CRLF)

---

## SHARED STANDARDS

[Artifact-Standards.md](../shared/Artifact-Standards.md)  
[File-Standards.md](../shared/File-Standards.md)  
[Encoding-Standards.md](../shared/Encoding-Standards.md)  
[RED-FLAGS.md](../shared/RED-FLAGS.md)  
[Common-Patterns.md](../shared/Common-Patterns.md)

---

## READY

**Base context loaded when SIMA mode activated.**

---

**END OF SIMA BASE MODE**

**Version:** 4.2.2-blank  
**Lines:** 150 (compact base)  
**Purpose:** Common SIMA context for all modes
