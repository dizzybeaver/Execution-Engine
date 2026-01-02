# RED-FLAGS.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Never-suggest patterns across all contexts  
**Location:** `/sima/context/shared/`

---

## UNIVERSAL RED FLAGS

**These apply to ALL projects, ALL modes**

---

### ðŸš« Code in Chat

**Never:** Output code in chat messages  
**Always:** Create complete file artifacts

**Why:** Token waste, fragments, errors

**REF:** Artifact-Standards.md

---

### ðŸš« File Fragments

**Never:** Partial code, "add to line X"  
**Always:** Complete files, all existing code

**Why:** Incomplete, not deployable, breaks context

**REF:** Artifact-Standards.md

---

### ðŸš« Files > 350 Lines

**Never:** Create files exceeding 350 lines  
**Always:** Split into focused separate files

**Why:** AI processing constraints, readability

**REF:** File-Standards.md, SPEC-LINE-LIMITS.md

---

### ðŸš« Missing Headers

**Never:** Files without version/date/purpose  
**Always:** Include proper headers

**Why:** Organization, tracking, documentation

**REF:** File-Standards.md, SPEC-HEADERS.md

---

### ðŸš« Broken Encoding

**Never:** Non-UTF-8, broken emoji/charts  
**Always:** UTF-8 encoding, test rendering

**Why:** Display issues, data corruption

**REF:** Encoding-Standards.md

---

### ðŸš« Skip File Fetch

**Never:** Modify without fetching current version  
**Always:** Fetch via fileserver.php URLs first

**Why:** Working against stale/cached code, errors

**REF:** File retrieval standards

---

### ðŸš« Bare Except Clauses

**Never:** `except:` without exception type  
**Always:** `except SpecificError as e:`

**Why:** Swallows errors, hides bugs

**REF:** Common-Patterns.md

---

### ðŸš« Skip Verification

**Never:** Deploy without checklist  
**Always:** Run verification protocol

**Why:** Prevents majority of mistakes

**REF:** Process standards

---

### ðŸš« Guess Without Data

**Never:** Assume root cause  
**Always:** Check logs, measure, verify

**Why:** Wastes time, wrong fixes

**REF:** Debug principles

---

### ðŸš« Change Multiple Things

**Never:** Modify several variables at once  
**Always:** Change one thing, test, iterate

**Why:** Can't identify what fixed/broke

**REF:** Debug principles

---

### ðŸš« Condense Multiple Topics

**Never:** Combine unrelated content in one file  
**Always:** Separate files for separate topics

**Why:** Focus, maintainability, findability

**REF:** File-Standards.md

---

### ðŸš« Output in Wrong Format

**Never:** Neural maps in chat, code without artifacts  
**Always:** Use appropriate output format

**Why:** Consistency, usability, standards

**REF:** Artifact-Standards.md

---

## PLATFORM-SPECIFIC RED FLAGS

**Note:** Platform-specific red flags are documented in platform knowledge.

**See:** `/sima/platforms/[platform]/` for platform-specific constraints

**Examples:**
- Serverless: Threading primitives
- Databases: Scan operations
- Storage: Hotspot patterns

---

## ARCHITECTURE-SPECIFIC RED FLAGS

**Note:** Architecture-specific red flags are documented in architecture knowledge.

**See:** `/sima/languages/[language]/architectures/` for architecture-specific patterns

**Examples:**
- Gateway patterns: Direct imports
- Layer separation: Cross-layer violations
- Module loading: Heavy top-level imports

---

## QUICK REFERENCE

**Before suggesting any solution, check:**
1. âŒ Code in chat?
2. âŒ File fragment?
3. âŒ >350 lines?
4. âŒ Missing header?
5. âŒ Skip fileserver.php?
6. âŒ Bare except?
7. âŒ Skip verification?
8. âŒ Multiple changes?
9. âŒ Broken encoding?
10. âŒ Condensed topics?
11. âŒ Platform violation? (check platform knowledge)
12. âŒ Architecture violation? (check architecture knowledge)

**If ANY âŒ triggered: DO NOT SUGGEST**

---

## RELATED DOCUMENTS

**Anti-Patterns:** `/sima/generic/anti-patterns/`  
**Decisions:** `/sima/generic/decisions/`  
**Lessons:** `/sima/generic/lessons/`  
**Specifications:** `/sima/generic/specifications/`  
**Platform Knowledge:** `/sima/platforms/`  
**Architecture Knowledge:** `/sima/languages/[language]/architectures/`

---

**END OF FILE**


**Summary:** Never suggest code in chat, fragments, >350 lines, bare except, skip verification, multiple changes, condense topics. Check platform/architecture knowledge for specific constraints.
