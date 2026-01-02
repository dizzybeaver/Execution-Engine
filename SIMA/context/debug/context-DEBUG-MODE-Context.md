# context-DEBUG-MODE-Context.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Project-agnostic debugging context  
**Activation:** "Start Debug Mode for {PROJECT}"  
**Load time:** 20-30 seconds (loads base + project extension)  
**Type:** Base Mode

---

## WHAT THIS MODE IS

**Debug Mode** enables troubleshooting for specific projects.

**Use for:**
- Finding root causes
- Analyzing errors
- Tracing execution
- Diagnosing failures
- Performance issues

**Not for:** Feature development (Project Mode), Q&A (General Mode)

---

## FILE RETRIEVAL

**Session Start:**
1. User uploads File Server URLs.md
2. Claude fetches fileserver.php automatically
3. Receives cache-busted URLs (69ms)
4. Fresh files guaranteed

**CRITICAL:** Debugging against old code = false conclusions.

**REF:** Shared knowledge

---

## DEBUG PRINCIPLES

### Principle 1: Systematic Investigation
**Don't guess. Follow evidence.**

```
1. Gather symptoms
2. Form hypotheses
3. Test hypotheses
4. Identify root cause
5. Verify fix
```

### Principle 2: Check Known Issues First
**Project extension lists known issues.**

Always check documented issues before investigating new ones.

### Principle 3: Trace Through Layers
**Follow execution path using fresh code.**

Fetch files via fileserver.php to see current implementation.

### Principle 4: Measure Don't Guess
**Use metrics and logs, not assumptions.**

- Logs
- Performance metrics
- Error traces
- Fresh file content

---

## FIX OUTPUT RULES

**MANDATORY for all fixes:**

### Always Complete Files
```
[OK] Complete file artifacts
[OK] ALL existing code included
[OK] Fix marked with # FIXED: comments
[OK] Immediately deployable
[OK] Filename in header
[X] Never code in chat
[X] Never fragments
[X] Never "change line X"
```

### Pre-Fix Checklist
```
[ ] Root cause identified?
[ ] Fetched current file? (fileserver.php)
[ ] Read complete file?
[ ] Including ALL existing code?
[ ] Marked fix with comments?
[ ] Creating artifact (not chat)?
[ ] Complete file (not fragment)?
[ ] Verified fix addresses root cause?
[ ] Filename in header?
[ ] Chat minimal?
```

**Complete Standards:** `/sima/context/shared/Artifact-Standards.md`

---

## GENERIC ERROR PATTERNS

### Pattern 1: Import Errors
**Symptoms:** ModuleNotFoundError, circular imports  
**Investigation:**
1. Check import statements
2. Look for circular dependencies
3. Verify correct imports used
4. Fetch via fileserver.php

**Generic Fix:**
```python
# FIXED: Changed to correct import
import required_module
return required_module.process()
```

### Pattern 2: Timeout Errors
**Symptoms:** Operation times out  
**Investigation:**
1. Check last log entry
2. Identify slow operation
3. Look for loops, waits, network calls
4. Fetch via fileserver.php

**Generic Fix:**
```python
# FIXED: Added timeout control
response = operation(timeout=5)
```

### Pattern 3: Performance Issues
**Symptoms:** Slow execution, high latency  
**Investigation:**
1. Profile operations
2. Identify bottlenecks
3. Check for unnecessary work
4. Fetch via fileserver.php

**Generic Fix:**
```python
# FIXED: Optimized approach
result = efficient_method()
```

### Pattern 4: Memory Issues
**Symptoms:** Out of memory, killed process  
**Investigation:**
1. Check memory metrics
2. Identify large data structures
3. Look for leaks
4. Fetch via fileserver.php

**Generic Fix:**
```python
# FIXED: Added memory management
if memory_high():
    clear_cache()
```

**Project-specific patterns in project extension.**

---

## DEBUG WORKFLOW

### Standard Troubleshooting Flow

```
1. User describes problem
   "Error X occurring when Y"

2. Claude checks known issues
   "Checking documented issues..."
   Uses project extension issue list

3. Claude investigates
   "Fetching current code via fileserver.php..."
   Uses fresh files
   Traces execution
   Forms hypotheses

4. Claude identifies root cause
   "Root cause: [brief statement]"

5. Claude provides fix
   "Creating fix artifact..."
   Fetches complete current file
   Implements fix
   Marks with # FIXED:
   Outputs complete artifact
   "Fix ready. Test with failing case."

6. User verifies
   Applies fix
   Tests with original failure
   Checks no regressions
```

---

## RED FLAGS

**Don't do this:**

| Flag | Why | What Instead |
|------|-----|--------------|
| Guess without logs | Wastes time | Check logs first |
| Change multiple things | Can't identify fix | One change, test |
| Skip known issues | Reinvent wheel | Check issues first |
| Not measure | No baseline | Use metrics |
| Treat symptoms | Temporary | Find root cause |
| Code in chat | Fragments | Complete artifacts |
| Skip fileserver.php | Old code | Fresh files always |

**Complete List:** `/sima/context/shared/RED-FLAGS.md`

---

## PROJECT EXTENSIONS

**Debug Mode combines:**
1. This base file (generic debugging)
2. Project extension (project-specific)

**Extension provides:**
- Known issues (documented bugs)
- Error patterns (project-specific)
- Debug tools (project-specific)
- Common fixes (project-specific)

---

## COMMON FIX PATTERNS

**Import Fix:**
```python
# FIXED: Corrected import
import correct_module
```

**Timeout Fix:**
```python
# FIXED: Added timeout
result = operation(timeout=5)
```

**Error Handling Fix:**
```python
# FIXED: Specific exception
try:
    operation()
except SpecificError as e:
    log_error(f"Error: {e}")
    raise
```

**Memory Fix:**
```python
# FIXED: Memory management
if memory_high():
    clear_cache()
```

**Complete Patterns:** `/sima/context/shared/Common-Patterns.md`

---

## SUCCESS METRICS

**Effective debugging when:**
- ✅ Root cause identified (not symptoms)
- ✅ Fix verified with failing case
- ✅ Performance measured before/after
- ✅ No regressions
- ✅ Fix in complete file artifact
- ✅ Chat output minimal
- ✅ Used fileserver.php (fresh files)

---

## VERIFICATION CHECKLIST

**Before every fix:**

1. ✅ fileserver.php fetched?
2. ✅ Known issues checked?
3. ✅ Current file fetched?
4. ✅ Complete file read?
5. ✅ Root cause identified?
6. ✅ Fix marked clearly?
7. ✅ Complete artifact?
8. ✅ Verified fix works?
9. ✅ Header included?
10. ✅ Chat minimal?

---

## READY

**Context loaded when you remember:**
- ✅ fileserver.php fetched (automatic)
- ✅ Systematic process (4 principles)
- ✅ Complete files ONLY (never fragments)
- ✅ Always fetch first (fileserver.php URLs)
- ✅ Fix marked (# FIXED:)
- ✅ Known issues from project extension
- ✅ Error patterns from project extension
- ✅ Code ALWAYS in artifacts
- ✅ Chat output minimal

**Now await project-specific extension load!**

---

**END OF DEBUG MODE CONTEXT (BASE)**

**Version:** 4.2.2-blank  
**Lines:** 350 (target achieved)  
**Load time:** 20-30 seconds (plus project extension)  
**References:** Shared knowledge in `/sima/context/shared/`  
**Note:** Must be combined with project extension for full context