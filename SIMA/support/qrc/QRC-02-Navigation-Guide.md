# QRC-02-Navigation-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Quick directory navigation reference  
**Type:** Support Quick Reference

---

## SIMA NAVIGATION QUICK REFERENCE

### Root Entry Points

**Start Here:**
- `/sima/README.md` - System overview
- `/sima/Master-Index-of-Indexes.md` - All domain indexes
- `/sima/SIMA-Navigation-Hub.md` - Navigation guide
- `/sima/SIMA-Quick-Reference-Card.md` - Quick reference

---

## DOMAIN STRUCTURE

### Knowledge Hierarchy
```
Generic (generic/)
  â†"
Platform (platforms/)
  â†"
Language (languages/)
  â†"
Project (projects/)
```

**Rule:** Start generic, get specific as needed

---

## KEY DIRECTORIES

### /sima/context/
**Purpose:** Mode activation contexts  
**Entry:** context-Master-Index-of-Indexes.md  
**Contents:** Mode contexts, shared standards

### /sima/docs/
**Purpose:** User guides and documentation  
**Entry:** docs-Master-Index-of-Indexes.md  
**Contents:** User, developer, install, deployment, migration guides

### /sima/generic/
**Purpose:** Universal knowledge  
**Entry:** generic-Master-Index-of-Indexes.md  
**Contents:** Lessons, decisions, anti-patterns, specifications

### /sima/languages/
**Purpose:** Language-specific patterns  
**Entry:** languages-Master-Index-of-Indexes.md  
**Contents:** Language implementations, frameworks

### /sima/platforms/
**Purpose:** Platform-specific knowledge  
**Entry:** platforms-Master-Index-of-Indexes.md  
**Contents:** Platform implementations

### /sima/projects/
**Purpose:** Project implementations  
**Entry:** projects-Master-Index-of-Indexes.md  
**Contents:** Project configs, knowledge, modes

### /sima/support/
**Purpose:** Tools and workflows  
**Entry:** support-Master-Index-of-Indexes.md  
**Contents:** Checklists, QRCs, tools, workflows

### /sima/templates/
**Purpose:** Entry templates  
**Entry:** templates-Master-Index.md  
**Contents:** All entry type templates

---

## FINDING KNOWLEDGE

### By Type
- Lessons: `/generic/lessons/`, `/[domain]/lessons/`
- Decisions: `/generic/decisions/`, `/[domain]/decisions/`
- Anti-Patterns: `/generic/anti-patterns/`, `/[domain]/anti-patterns/`
- Specifications: `/generic/specifications/`

### By Domain
1. Check `/generic/` first (universal patterns)
2. Check `/platforms/[platform]/` (platform-specific)
3. Check `/languages/[language]/` (language-specific)
4. Check `/projects/[project]/` (project-specific)

### By Mode
- General Mode: All domains accessible
- Learning Mode: Creates in appropriate domain
- Maintenance Mode: Updates all domains
- Project Mode: Focuses on project domain
- Debug Mode: Accesses all relevant domains

---

## INDEX SYSTEM

### Master Indexes
- `/Master-Index-of-Indexes.md` - Root
- `/[domain]/[domain]-Master-Index-of-Indexes.md` - Domain

### Category Indexes
- `/[domain]/[category]/[domain]-[category]-Index.md`
- Example: `/generic/lessons/generic-lessons-Index.md`

### Router Files
- `/[domain]/[domain]-Router.md` - Domain navigation
- Example: `/generic/generic-Router.md`

---

## QUICK PATHS

### Common Tasks

**Find generic lesson:**
```
/generic/lessons/generic-lessons-Index.md
```

**Find platform knowledge:**
```
/platforms/[platform]/[platform]-Index.md
```

**Find project config:**
```
/projects/[project]/config/
```

**Access mode contexts:**
```
/context/[mode]/context-[mode]-Index.md
```

**Use templates:**
```
/templates/templates-Master-Index.md
```

**Find tools:**
```
/support/tools/support-tools-Index.md
```

---

## FILE NAMING

### Entry Files
```
[domain]-[category]-##-[description].md
```
**Example:** `generic-LESS-01-read-complete-files.md`

### Index Files
```
[domain]-[subdomain]-[category]-Index.md
```
**Example:** `generic-lessons-Index.md`

### Router Files
```
[domain]-Router.md
```
**Example:** `generic-Router.md`

---

## CROSS-REFERENCING

### REF-ID Format
```
[TYPE]-##
```
**Examples:**
- LESS-01 (Lesson)
- DEC-05 (Decision)
- AP-14 (Anti-Pattern)
- BUG-01 (Bug)
- WISD-06 (Wisdom)
- SPEC-01 (Specification)

### Finding REF-IDs
1. Use appropriate category index
2. Search by REF-ID
3. Follow cross-references
4. Check router files

---

## NAVIGATION TIPS

### Efficient Navigation
1. Start at Master Index
2. Identify domain
3. Use category index
4. Find specific entry
5. Follow cross-references

### Lost?
1. Go to `/Master-Index-of-Indexes.md`
2. Identify what you need
3. Follow index chain
4. Use router if needed

### Adding Content?
1. Determine domain (generic/platform/language/project)
2. Choose category (lessons/decisions/anti-patterns/etc.)
3. Use appropriate template
4. Update category index
5. Add cross-references

---

**END OF QUICK REFERENCE**

**Version:** 1.0.0  
**Lines:** 200 (within 400 limit)  
**Parent:** /sima/support/support-Master-Index-of-Indexes.md  
**See Also:** SIMA-Navigation-Hub.md (full navigation guide)