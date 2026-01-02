# context-SIMA-IMPORT-MODE-START-Quick-Context.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Quick Import Mode reference  
**Type:** Quick Context

---

## ACTIVATION

`"Start SIMA Import Mode"`

---

## EXTENDS

- [context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md)
- [context-SIMA-IMPORT-MODE-Context.md](context-SIMA-IMPORT-MODE-Context.md)

---

## IMPORT PROCESS

1. **Load Package** - Validate manifest
2. **Check Duplicates** - Scan via fileserver.php
3. **Resolve Conflicts** - Handle collisions
4. **Integrate** - Import files
5. **Update System** - Regenerate indexes

---

## CONFLICT TYPES

- **REF-ID Collision** - Renumber import
- **Content Duplicate** - Keep better version
- **Dependency Missing** - Flag for resolution

---

## KEY RULES

✅ Validate manifest  
✅ Check duplicates (fileserver.php)  
✅ Resolve all conflicts  
✅ Update indexes  
✅ Generate report  

❌ Partial imports  
❌ Unresolved conflicts  
❌ Broken links

---

**END OF QUICK CONTEXT**

**Lines:** 50 (compact)