# SPEC-CONTINUATION.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Work continuation protocol for token management  
**Category:** Specifications

---

## PURPOSE

Define protocol for continuing work across sessions when approaching token limits, ensuring smooth transitions without loss of progress.

---

## TOKEN THRESHOLD

### Warning Level
**< 50,000 tokens remaining**

**Action:**
- Finish current artifact
- Prepare transition
- Create continuation prompt

### Critical Level
**< 30,000 tokens remaining**

**Action:**
- Stop new work immediately
- Create transition documents
- Prepare chat prompt

---

## TRANSITION DOCUMENTS

### Required Artifacts

**1. Progress Summary (< 100 lines)**
```markdown
# Migration-Progress-Session-[N].md

**Session:** [N]
**Date:** 2025-11-10
**Tokens Used:** [X] / 190,000
**Time:** [X] minutes

## COMPLETED
- [X] Item 1
- [X] Item 2

## IN PROGRESS
- [ ] Item 3 (50% complete)

## NEXT STEPS
1. Complete item 3
2. Start item 4
3. Verify item 5

## ARTIFACTS CREATED
- file1.md
- file2.md
```

**2. Chat Transition Prompt (< 50 lines)**
```markdown
# Session-[N+1]-Start.md

Continue migration work.

**Upload:**
1. File Server URLs.md
2. Knowledge-Migration-Plan.md
3. Migration-Progress-Session-[N].md

**Say:** "Continue from Session [N]. Start with [next task]."

**Current Status:** [Brief context]
**Next Task:** [Specific next step]
```

---

## WORK CONTINUATION PROTOCOL

### Step 1: Recognize Low Tokens
Monitor token count during work.

### Step 2: Finish Current Task
Complete current artifact or logical unit.

### Step 3: Create Progress Summary
Document what's done, what's in progress, what's next.

### Step 4: Create Transition Prompt
Simple, clear instructions for next session.

### Step 5: Brief Status Message
```
Token limit approaching. Created transition documents:
- Migration-Progress-Session-[N].md
- Session-[N+1]-Start.md

Upload these files in next session to continue.
```

---

## PROGRESS SUMMARY FORMAT

### Completed Section
```markdown
## COMPLETED

### Specification Files (11 files)
- [X] SPEC-FILE-STANDARDS.md
- [X] SPEC-LINE-LIMITS.md
- [X] SPEC-HEADERS.md
[... all completed items]
```

### In Progress Section
```markdown
## IN PROGRESS

### Directory Structure
- [~] /sima/entries/specifications/ (created)
- [ ] /sima/languages/python/architectures/suga/ (pending)

**Current Task:** Creating SUGA architecture directories
**Status:** 50% complete
**Next:** Create LMMS directories
```

### Next Steps Section
```markdown
## NEXT STEPS

1. **Create LMMS directories** (15 min)
2. **Create ZAPH directories** (15 min)
3. **Create DD directories** (15 min)
4. **Create LEE project config** (20 min)
```

---

## CHAT PROMPT FORMAT

### Minimal Template
```markdown
# Session-[N+1]-Start.md

**Purpose:** Continue migration work

**Upload Files:**
1. File Server URLs.md
2. Knowledge-Migration-Plan.md  
3. Migration-Progress-Session-[N].md

**Activation:**
Say: "Continue from Session [N]. Focus on [specific task]."

**Context:**
Previous session completed [X] items.
Next task: [Specific action]

**Work Mode:**
- Non-stop execution
- Minimal chatter
- Create transition at < 30k tokens
```

---

## BENEFITS

**Smooth transitions provide:**
- No lost work
- Clear context
- Immediate resumption
- Progress tracking
- Efficient token use

---

## QUALITY CHECKLIST

### Progress Summary
- [ ] Lists completed items
- [ ] Shows in-progress status
- [ ] Clear next steps
- [ ] Under 100 lines
- [ ] Includes artifact list

### Chat Prompt
- [ ] Lists required uploads
- [ ] Clear activation phrase
- [ ] Brief context
- [ ] Specific next task
- [ ] Under 50 lines

---

## EXAMPLE TRANSITION

### Session 2 Ending
```
Token limit approaching (28,000 remaining).

Created transition:
- Migration-Progress-Session-2.md (74 lines)
- Session-3-Start.md (38 lines)

Session 2 completed 11 specification files.
Session 3: Create architecture directories.

Upload transition files in next session.
```

### Session 3 Starting
User uploads:
- File Server URLs.md
- Knowledge-Migration-Plan.md
- Migration-Progress-Session-2.md

User says:
"Continue from Session 2. Create architecture directories."

Claude:
- Fetches fileserver.php
- Reviews progress summary
- Immediately starts work on directories
- No unnecessary chatter

---

**Related:**
- SPEC-FILE-STANDARDS.md
- SPEC-LINE-LIMITS.md
- Knowledge-Migration-Plan.md

**Version History:**
- v4.2.2-blank (2025-11-10): Blank slate version
- v1.0.0 (2025-11-06): Initial continuation protocol

---

**END OF FILE**