# context-DEBUG-MODE-START-Quick-Context.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Quick Debug Mode reference  
**Type:** Quick Context

---

## ACTIVATION

`"Start Debug Mode for {PROJECT}"`

---

## EXTENDS

- Base: [context-DEBUG-MODE-Context.md](context-DEBUG-MODE-Context.md)
- Project-specific extension (loaded automatically)

---

## FOUR PRINCIPLES

1. **Systematic** - Follow evidence, don't guess
2. **Check Known** - Review documented issues first
3. **Trace Layers** - Use fresh code (fileserver.php)
4. **Measure** - Use logs and metrics

---

## WORKFLOW

```
1. Check known issues
2. Fetch fresh code (fileserver.php)
3. Identify root cause
4. Create fix artifact (complete file)
5. Mark with # FIXED:
6. Verify fix
```

---

## KEY RULES

✅ Complete files only  
✅ fileserver.php URLs  
✅ Mark fixes (# FIXED:)  
✅ Root cause focus  
✅ Verify with test case  

❌ Code in chat  
❌ Fragments  
❌ Old code  
❌ Treat symptoms

---

**END OF QUICK CONTEXT**

**Lines:** 50 (compact)