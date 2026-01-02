# context-MODE-SELECTOR.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Root context router for all SIMA modes  
**Type:** Mode Router

---

## 🎯 WHAT THIS FILE IS

Root mode selector that routes to appropriate context files based on activation phrase.

**DO NOT load this file directly for work.** This is ONLY a router.

---

## 🚀 ACTIVATION PHRASES

### Mode 1: General Purpose Mode
**Phrase:** `"Please load context"`  
**Loads:** [context-General-Mode-Context.md](general/context-General-Mode-Context.md)  
**Purpose:** Q&A, architecture queries, knowledge access  
**Time:** 20-30 seconds

### Mode 2: Learning Mode
**Phrase:** `"Start SIMA Learning Mode"`  
**Loads:** [context-SIMA-LEARNING-MODE-Context.md](sima/context-SIMA-LEARNING-MODE-Context.md)  
**Purpose:** Knowledge extraction and integration  
**Time:** 30-45 seconds

### Mode 3: Maintenance Mode
**Phrase:** `"Start SIMA Maintenance Mode"`  
**Loads:** [context-SIMA-MAINTENANCE-MODE-Context.md](sima/context-SIMA-MAINTENANCE-MODE-Context.md)  
**Purpose:** Update indexes, clean structure  
**Time:** 30-45 seconds

### Mode 4: Project Mode
**Phrase:** `"Start Project Mode for {PROJECT}"`  
**Examples:**
- `"Start Project Mode for SIMA"`

**Loads:**
- [context-PROJECT-MODE-Context.md](projects/context-PROJECT-MODE-Context.md) (base)
- Project-specific extension

**Purpose:** Active development  
**Time:** 30-45 seconds

### Mode 5: Debug Mode
**Phrase:** `"Start Debug Mode for {PROJECT}"`  
**Examples:**
- `"Start Debug Mode for SIMA"`

**Loads:**
- [context-DEBUG-MODE-Context.md](debug/context-DEBUG-MODE-Context.md) (base)
- Project-specific extension

**Purpose:** Troubleshooting  
**Time:** 30-45 seconds

### Mode 6: New Project Mode
**Phrase:** `"Create New Project with {NAME}"`  
**Example:** `"Create New Project with MyProject"`  
**Loads:** [context-new-Project-Context.md](new/context-new-Project-Context.md)  
**Purpose:** Scaffold new project  
**Time:** 30-45 seconds

### Mode 7: New Platform Mode
**Phrase:** `"Create New Platform with {NAME}"`  
**Example:** `"Create New Platform with Azure"`  
**Loads:** [context-new-Platform-Context.md](new/context-new-Platform-Context.md)  
**Purpose:** Scaffold new platform  
**Time:** 30-45 seconds

### Mode 8: New Language Mode
**Phrase:** `"Create New Language with {NAME}"`  
**Example:** `"Create New Language with JavaScript"`  
**Loads:** [context-new-Languages-Context.md](new/context-new-Languages-Context.md)  
**Purpose:** Scaffold new language  
**Time:** 30-45 seconds

---

## 🔧 HOW IT WORKS

```
IF phrase = "Please load context"
    THEN load context-General-Mode-Context.md
    
ELSE IF phrase = "Start SIMA Learning Mode"
    THEN load context-SIMA-LEARNING-MODE-Context.md
    
ELSE IF phrase = "Start SIMA Maintenance Mode"
    THEN load context-SIMA-MAINTENANCE-MODE-Context.md
    
ELSE IF phrase = "Start SIMA Project Mode"
    THEN load context-SIMA-PROJECT-MODE.md
    
ELSE IF phrase = "Start Project Mode for [PROJECT]"
    THEN load context-PROJECT-MODE-Context.md
    AND load PROJECT-specific extension
    
ELSE IF phrase = "Start Debug Mode for [PROJECT]"
    THEN load context-DEBUG-MODE-Context.md
    AND load PROJECT-specific extension
    
ELSE IF phrase = "Create New Project with [NAME]"
    THEN load context-new-Project-Context.md
    SET project_name = [NAME]
    
ELSE IF phrase = "Create New Platform with [NAME]"
    THEN load context-new-Platform-Context.md
    SET platform_name = [NAME]
    
ELSE IF phrase = "Create New Language with [NAME]"
    THEN load context-new-Languages-Context.md
    SET language_name = [NAME]
    
ELSE
    ERROR: Invalid activation phrase
    SHOW: Valid phrases list
```

---

## 📊 MODE COMPARISON

| Mode | Purpose | Output | Time |
|------|---------|--------|------|
| General | Q&A | Answers | 20-30s |
| Learning | Extract | Neural Maps | 30-45s |
| Maintenance | Clean | Updated Indexes | 30-45s |
| Project | Build | Code | 30-45s |
| Debug | Fix | Root Causes | 30-45s |
| New | Scaffold | Structure | 30-45s |

---

## 🎯 QUICK REFERENCE

**Choose Your Mode:**

- 🤔 **Learning about system?** → General Mode
- 📚 **Capturing knowledge?** → Learning Mode
- 🧹 **Cleaning up knowledge?** → Maintenance Mode
- 🔨 **Writing code?** → Project Mode
- 🐛 **Fixing bugs?** → Debug Mode
- 🆕 **Creating new?** → New Mode

---

## 📋 MODE-SPECIFIC ROUTERS

[context-general-MODE-SELECTOR.md](general/context-general-MODE-SELECTOR.md)  
[context-SIMA-MODE-SELECTOR.md](sima/context-SIMA-MODE-SELECTOR.md)  
[context-DEBUG-MODE-SELECTOR.md](debug/context-DEBUG-MODE-SELECTOR.md)  
[context-PROJECT-MODE-SELECTOR.md](projects/context-PROJECT-MODE-SELECTOR.md)  
[context-new-MODE-SELECTOR.md](new/context-new-MODE-SELECTOR.md)

---

**END OF MODE SELECTOR**

**This file is a ROUTER ONLY. Do not use for actual work.**  
**Choose your mode and activate with the correct phrase.**

**Current Modes:** 8  
**Purpose:** Route to appropriate context