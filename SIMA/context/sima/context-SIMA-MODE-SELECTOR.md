# context-SIMA-MODE-SELECTOR.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** SIMA Mode router  
**Type:** Mode Router

---

## SIMA MODES

### Base Mode
**Loaded by:** All SIMA modes automatically  
**File:** [context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md)

### Project Mode
**Phrase:** `"Start SIMA Project Mode"`  
**Loads:**
- [context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md)
- [context-SIMA-PROJECT-MODE.md](context-SIMA-PROJECT-MODE.md)
- [../projects/context-PROJECT-MODE-Context.md](../projects/context-PROJECT-MODE-Context.md)

### Learning Mode
**Phrase:** `"Start SIMA Learning Mode"`  
**Loads:**
- [context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md)
- [context-SIMA-LEARNING-MODE-Context.md](context-SIMA-LEARNING-MODE-Context.md)

### Maintenance Mode
**Phrase:** `"Start SIMA Maintenance Mode"`  
**Loads:**
- [context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md)
- [context-SIMA-MAINTENANCE-MODE-Context.md](context-SIMA-MAINTENANCE-MODE-Context.md)

### Export Mode
**Phrase:** `"Start SIMA Export Mode"`  
**Loads:**
- [context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md)
- [context-SIMA-EXPORT-MODE-Context.md](context-SIMA-EXPORT-MODE-Context.md)

### Import Mode
**Phrase:** `"Start SIMA Import Mode"`  
**Loads:**
- [context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md)
- [context-SIMA-IMPORT-MODE-Context.md](context-SIMA-IMPORT-MODE-Context.md)

---

## ROUTING

```
IF phrase = "Start SIMA Project Mode"
    THEN load BASE + PROJECT + PROJECT-MODE-Context
    
ELSE IF phrase = "Start SIMA Learning Mode"
    THEN load BASE + LEARNING
    
ELSE IF phrase = "Start SIMA Maintenance Mode"
    THEN load BASE + MAINTENANCE
    
ELSE IF phrase = "Start SIMA Export Mode"
    THEN load BASE + EXPORT
    
ELSE IF phrase = "Start SIMA Import Mode"
    THEN load BASE + IMPORT
```

---

## MODE CHARACTERISTICS

| Mode | Purpose | Output | Time |
|------|---------|--------|------|
| Project | Build SIMA | Entries | 30-45s |
| Learning | Extract | Knowledge | 30-45s |
| Maintenance | Clean | Indexes | 20-30s |
| Export | Package | Bundle | 20-30s |
| Import | Integrate | Report | 20-30s |

---

**END OF SELECTOR**

**Up:** [../context-MODE-SELECTOR.md](../context-MODE-SELECTOR.md)