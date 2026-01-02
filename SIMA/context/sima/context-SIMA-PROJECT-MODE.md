# context-SIMA-PROJECT-MODE.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** SIMA project-specific development context  
**Project:** SIMA (Structured Intelligence Memory Architecture)  
**Type:** Project Mode

---

## EXTENDS

[context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md) (Base context)

---

## PROJECT: SIMA

**Name:** SIMA (Structured Intelligence Memory Architecture)  
**Type:** Knowledge Management System  
**Platform:** Documentation (Markdown)  
**Language:** Markdown  
**Architecture:** Domain-based organization

---

## WORKFLOWS

### Add Knowledge Entry
1. Identify entry type (LESS, DEC, AP, SPEC, etc.)
2. Check for duplicates (via fileserver.php)
3. Genericize content appropriately
4. Create entry (≤350 lines)
5. Update indexes
6. Add cross-references

### Create New Domain
1. Define domain structure
2. Create directory hierarchy
3. Generate index files
4. Document organization
5. Update master indexes

### Update Index
1. Scan directory for entries
2. Compare with current index
3. Add missing entries
4. Remove deleted entries
5. Sort alphabetically/numerically
6. Output updated index

### Migrate Entry Format
1. Fetch entry via fileserver.php
2. Check against SPEC standards
3. Fix header, encoding, naming
4. Split if >350 lines
5. Output migrated entry
6. Update indexes

---

## EXAMPLES

### Generic Entry
```markdown
# TYPE-##.md

**Version:** 1.0.0
**Date:** 2025-11-10
**Purpose:** [Generic description]

[Generic content - no project specifics]

**Keywords:** k1, k2, k3, k4
**Related:** REF-ID1, REF-ID2
```

### Domain Organization
```
/generic/lessons/LESS-01.md (generic)
/platforms/[platform]/LESS-01.md (platform)
/languages/[language]/LESS-01.md (language)
/projects/[project]/LESS-01.md (project)
```

---

**END OF SIMA PROJECT MODE**

**Version:** 4.2.2-blank  
**Lines:** 100 (target achieved)  

**Combine with:** Base context + Project Mode Context (base)
