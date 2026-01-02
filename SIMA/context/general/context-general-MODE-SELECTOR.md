# context-general-MODE-SELECTOR.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** General Mode router  
**Type:** Mode Router

---

## ACTIVATION

**Phrase:** `"Please load context"`

**Loads:**
- [context-General-Mode-Context.md](context-General-Mode-Context.md) (Full)
- OR [context-General-Mode-START-Quick-Context.md](context-General-Mode-START-Quick-Context.md) (Quick)

---

## ROUTING

```
IF phrase = "Please load context"
    IF quick_mode_requested
        THEN load context-General-Mode-START-Quick-Context.md
    ELSE
        THEN load context-General-Mode-Context.md
```

---

## MODE CHARACTERISTICS

**Purpose:** Q&A, knowledge access, guidance  
**Output:** Answers with REF-IDs  
**Time:** 20-30 seconds (full) or 10-15 seconds (quick)  
**Modifications:** None (read-only)

---

## RELATED MODES

**Need to:**
- Create knowledge? → [Learning Mode](../sima/context-SIMA-LEARNING-MODE-Context.md)
- Update indexes? → [Maintenance Mode](../sima/context-SIMA-MAINTENANCE-MODE-Context.md)
- Write code? → [Project Mode](../projects/context-PROJECT-MODE-Context.md)
- Fix bugs? → [Debug Mode](../debug/context-DEBUG-MODE-Context.md)

---

**END OF SELECTOR**

**Up:** [context-MODE-SELECTOR.md](../context-MODE-SELECTOR.md)