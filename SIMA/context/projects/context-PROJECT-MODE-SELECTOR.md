# context-PROJECT-MODE-SELECTOR.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Project Mode router  
**Type:** Mode Router

---

## ACTIVATION

**Phrase:** `"Start Project Mode for {PROJECT}"`

**Loads:**
- [context-PROJECT-MODE-Context.md](context-PROJECT-MODE-Context.md) (Base)
- `/sima/projects/{PROJECT}/modes/PROJECT-MODE-{PROJECT}.md` (Extension)

---

## ROUTING

```
IF phrase = "Start Project Mode for [PROJECT]"
    THEN load context-PROJECT-MODE-Context.md
    AND load /sima/projects/[PROJECT]/modes/PROJECT-MODE-[PROJECT].md
```

---

## MODE CHARACTERISTICS

**Purpose:** Active development, feature building  
**Output:** Code (complete file artifacts)  
**Time:** 20-30 seconds (plus project extension)  
**Modifications:** Complete file artifacts only

---

## AVAILABLE PROJECTS

- SIMA - [/sima/projects/sima/modes/PROJECT-MODE-SIMA.md](../../projects/sima/modes/PROJECT-MODE-SIMA.md)
- Additional projects added as created

---

**END OF SELECTOR**

**Up:** [../context-MODE-SELECTOR.md](../context-MODE-SELECTOR.md)