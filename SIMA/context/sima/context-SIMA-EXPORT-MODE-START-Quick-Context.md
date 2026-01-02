# context-SIMA-EXPORT-MODE-START-Quick-Context.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Quick Export Mode reference  
**Type:** Quick Context

---

## ACTIVATION

`"Start SIMA Export Mode"`

---

## EXTENDS

- [context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md)
- [context-SIMA-EXPORT-MODE-Context.md](context-SIMA-EXPORT-MODE-Context.md)

---

## EXPORT PROCESS

1. **Define Scope** - What to export
2. **Collect Files** - Gather all files
3. **Generate Manifest** - Create metadata
4. **Package** - Bundle with structure
5. **Import Instructions** - How to import

---

## PACKAGE STRUCTURE

```
export-[name]-[date]/
├── manifest.yaml
├── import-instructions.md
├── files/
└── indexes/
```

---

## KEY RULES

✅ All files complete  
✅ All REF-IDs valid  
✅ Manifest correct  
✅ Import instructions clear  

❌ Partial exports  
❌ Broken references

---

**END OF QUICK CONTEXT**

**Lines:** 50 (compact)