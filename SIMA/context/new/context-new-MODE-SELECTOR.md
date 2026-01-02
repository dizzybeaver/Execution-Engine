# context-new-MODE-SELECTOR.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** New Mode router  
**Type:** Mode Router

---

## NEW MODES

### Base Mode
**Loaded by:** All New modes automatically  
**File:** [context-new-Context.md](context-new-Context.md)

### New Project Mode
**Phrase:** `"Create New Project with {NAME}"`  
**Loads:**
- [context-new-Context.md](context-new-Context.md)
- [context-new-Project-Context.md](context-new-Project-Context.md)

### New Platform Mode
**Phrase:** `"Create New Platform with {NAME}"`  
**Loads:**
- [context-new-Context.md](context-new-Context.md)
- [context-new-Platform-Context.md](context-new-Platform-Context.md)

### New Language Mode
**Phrase:** `"Create New Language with {NAME}"`  
**Loads:**
- [context-new-Context.md](context-new-Context.md)
- [context-new-Languages-Context.md](context-new-Languages-Context.md)

---

## ROUTING

```
IF phrase = "Create New Project with [NAME]"
    THEN load BASE + PROJECT
    SET project_name = [NAME]
    
ELSE IF phrase = "Create New Platform with [NAME]"
    THEN load BASE + PLATFORM
    SET platform_name = [NAME]
    
ELSE IF phrase = "Create New Language with [NAME]"
    THEN load BASE + LANGUAGE
    SET language_name = [NAME]
```

---

## MODE CHARACTERISTICS

| Mode | Purpose | Output | Files |
|------|---------|--------|-------|
| Project | Create project | Structure | 8 |
| Platform | Create platform | Structure | 8 |
| Language | Create language | Structure | 10 |

---

**END OF SELECTOR**

**Up:** [../context-MODE-SELECTOR.md](../context-MODE-SELECTOR.md)