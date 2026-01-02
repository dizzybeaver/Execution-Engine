# context-DEBUG-MODE-SELECTOR.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Debug Mode router  
**Type:** Mode Router

---

## ACTIVATION

**Phrase:** `"Start Debug Mode for {PROJECT}"`

**Loads:**
- [context-DEBUG-MODE-Context.md](context-DEBUG-MODE-Context.md) (Base)
- `/sima/projects/{PROJECT}/modes/DEBUG-MODE-{PROJECT}.md` (Extension)

---

## ROUTING

```
IF phrase = "Start Debug Mode for [PROJECT]"
    THEN load context-DEBUG-MODE-Context.md
    AND load /sima/projects/[PROJECT]/modes/DEBUG-MODE-[PROJECT].md
```

---

## MODE CHARACTERISTICS

**Purpose:** Troubleshooting, root cause analysis  
**Output:** Fixes (complete file artifacts)  
**Time:** 20-30 seconds (plus project extension)  
**Modifications:** Complete file artifacts only

---

## AVAILABLE PROJECTS

- SIMA - [/sima/projects/sima/modes/DEBUG-MODE-SIMA.md](../../projects/sima/modes/DEBUG-MODE-SIMA.md)
- Additional projects added as created

---

**END OF SELECTOR**

**Up:** [../context-MODE-SELECTOR.md](../context-MODE-SELECTOR.md)