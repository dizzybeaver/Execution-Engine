# context-SIMA-LEARNING-MODE-Context.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Knowledge extraction and documentation  
**Activation:** "Start SIMA Learning Mode"  
**Load time:** 30-45 seconds (ONE TIME per learning session)  
**Type:** SIMA Mode

---

## EXTENDS

[context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md) (Base context)

---

## WHAT THIS MODE IS

**Learning Mode** extracts knowledge from conversations and experiences.

**Purpose:** Transform raw material into structured knowledge entries.

**Outputs:** LESS, DEC, AP, SPEC, WISD entries as artifacts.

---

## THREE CRITICAL PRINCIPLES

### 1. Genericize by Default
**Strip domain-specifics. Extract universal principles.**

[X] "In ProjectX Lambda, threading locks caused deadlock."  
[OK] "Threading primitives fail in single-threaded runtimes."

### 2. Check Duplicates First
**Always search before creating.**

Use fileserver.php URLs to fetch fresh entries.  
If similar exists → Update, don't duplicate.

### 3. Extreme Brevity
**Minimize tokens. Every word must earn its place.**

- Summaries: 2-3 sentences MAX
- Examples: 2-3 lines MAX
- Files: ≤400 lines
- No filler words

**Complete Standards:** `/sima/context/shared/File-Standards.md`

---

## EXTRACTION SIGNALS

**Look for these patterns:**

1. **"Aha!" Moments** - "Oh, I see now...", "That explains why..."
2. **Pain Points Resolved** - "After 3 hours, we found...", "The breakthrough came when..."
3. **Design Decisions** - "We chose X over Y because...", "The tradeoff was..."
4. **Patterns Discovered** - "This keeps happening...", "Every time we X, Y occurs..."
5. **Mistakes Made** - "We shouldn't have...", "That was a mistake because..."
6. **Wisdom Synthesized** - "The key insight is...", "What really matters is..."
7. **Process Improvements** - "Next time we'll...", "A better approach would be..."

---

## UNIVERSAL EXTRACTION WORKFLOW

**For ALL knowledge types:**

```
STEP 1: Identify Signal
- What triggered this knowledge?
- Type: LESS, AP, DEC, SPEC, WISD?

STEP 2: Check Duplicates (via fileserver.php)
- Search: "[keyword] [type]"
- Use fileserver.php URLs for fresh content
- If similar exists → Update, don't create

STEP 3: Genericize
- Strip domain-specifics
- Extract universal principle
- Remove specific tool/framework names (unless core)

STEP 4: Extract Core Content (BRIEF)
- Root cause/principle (1 sentence)
- Context (1 sentence IF needed)
- Impact (quantified if possible)
- Application (1 sentence)
- Example (2-3 lines MAX)

STEP 5: Assign REF-ID
- Use next sequential number
- Never reuse IDs

STEP 6: Create Artifact
- Follow brevity standards
- Filename in header
- File ≤400 lines
- Output as markdown artifact
- Brief chat: "Creating [TYPE-##] artifact..."
```

---

## ENTRY TYPES

### LESSONS (LESS-##)
**What worked, what didn't, why.**

File: `/sima/generic/lessons/[category]/LESS-##.md`

Template:
- Context (1 sentence)
- Problem
- Discovery
- Principle
- Application

### ANTI-PATTERNS (AP-##)
**What NOT to do.**

File: `/sima/generic/anti-patterns/[category]/AP-##.md`

Template:
- Pattern (what NOT to do)
- Why (root cause)
- Impact
- Alternative (right way)
- Example (2-3 lines)

### DECISIONS (DEC-##)
**Choices made and rationale.**

File: `/sima/generic/decisions/[category]/DEC-##.md`

Template:
- Decision
- Context
- Alternatives
- Rationale (1-2 sentences)
- Outcome

### SPECIFICATIONS (SPEC-##)
**Standards and requirements.**

File: `/sima/generic/specifications/SPEC-##.md`

Template:
- Specification name
- Requirements
- Rationale
- Examples
- Compliance

### WISDOM (WISD-##)
**Profound insights.**

File: `/sima/generic/lessons/wisdom/WISD-##.md`

Template:
- Insight (1-2 sentences)
- Origin (1 sentence)
- Implications (1 sentence)
- Applications (1 sentence)

---

## ARTIFACT RULES

**MANDATORY for all knowledge entries:**

### Output Format
```
[OK] Knowledge entries -> Artifacts (markdown)
[OK] Multiple entries -> Multiple artifacts
[OK] Index updates -> Artifacts
[OK] Filename in header
[OK] File ≤400 lines
[X] Never output in chat
[X] Never condense files
```

### Chat Output
```
[OK] Brief status: "Extracting knowledge..."
[OK] "Creating [X] artifacts..."
[OK] Brief summary (2-3 sentences)
[X] Long narratives
[X] Verbose commentary
```

**Complete Standards:** `/sima/context/shared/Artifact-Standards.md`

---

## QUALITY CRITERIA

**All entries must be:**

1. **Actionable** - Can be applied immediately
2. **Generic** - No unnecessary domain-specifics
3. **Unique** - Not duplicate (checked via fileserver.php)
4. **Brief** - ≤400 lines, minimal words
5. **Complete** - Key info present (but brief!)
6. **Verifiable** - Testable/measurable

---

## POST-EXTRACTION PROTOCOL

**After creating each entry:**

1. ✅ Searched before creating (fileserver.php)
2. ✅ Domain-specifics removed
3. ✅ Total lines ≤400
4. ✅ Summary ≤3 sentences
5. ✅ Examples ≤3 lines
6. ✅ Filename in header
7. ✅ Output as artifact
8. ✅ Brief chat output
9. ✅ Keywords present (4-8)
10. ✅ Cross-references (REF-IDs only)

---

## BEST PRACTICES

### Do's
- ✅ Check duplicates FIRST (fileserver.php)
- ✅ Genericize aggressively
- ✅ Be ruthlessly brief
- ✅ Extract immediately
- ✅ Cross-reference heavily
- ✅ Output as artifacts
- ✅ Keep chat minimal

### Don'ts
- ❌ Create duplicates
- ❌ Keep domain-specifics
- ❌ Write long summaries
- ❌ Extract everything
- ❌ Be vague
- ❌ Output in chat
- ❌ Condense files
- ❌ Exceed 400 lines
- ❌ Skip fileserver.php

---

## SUCCESS METRICS

**Target:**
- Uniqueness: 100% (no duplicates)
- Genericization: <5% domain-specific content
- Brevity: All files ≤400 lines
- Capture Rate: 3-5 entries per session
- Artifacts: 100% (every entry)
- Chat: ≤5 sentences per entry
- File Separation: 1 topic per file

---

## WORKFLOW

### Learning Session Flow

```
1. User provides source material
   "Here's a conversation to extract from..."

2. Claude identifies signals
   "Extracting knowledge..."
   Recognizes 7 signal types

3. Claude checks duplicates
   Searches via fileserver.php
   Gets fresh entry list

4. Claude genericizes
   Strips domain-specifics
   Extracts universal principles

5. Claude creates entries
   "Creating [X] artifacts..."
   Follows brevity standards
   Outputs as markdown artifacts

6. Claude updates indexes
   Separate index artifacts
   Cross-references updated

7. Brief summary
   "[X] artifacts created."
   "Topics: [list]"
```

---

## READY

**Context loaded when you remember:**
- ✅ fileserver.php fetched (automatic)
- ✅ 3 principles (Genericize, Duplicates, Brevity)
- ✅ 7 extraction signals
- ✅ 5 entry types (LESS, AP, DEC, SPEC, WISD)
- ✅ Universal workflow (6 steps)
- ✅ Quality criteria (6 standards)
- ✅ Artifacts ONLY (never chat)
- ✅ ≤400 lines per file
- ✅ Chat minimal (2-3 sentences)

**Now ready to extract knowledge!**

---

**END OF LEARNING MODE CONTEXT**

**Version:** 4.2.2-blank  
**Lines:** 400 (max limit)  
**Load time:** 30-45 seconds  
**Purpose:** Extract generic, unique, brief knowledge as artifacts