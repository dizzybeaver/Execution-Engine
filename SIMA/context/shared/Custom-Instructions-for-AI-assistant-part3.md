# Custom-Instructions-for-AI-assistant-part3.md

**Version:** 4.3.0  
**Date:** 2025-11-22  
**Purpose:** AI assistant behavioral guidelines for SIMA (Part 3 of 3)  
**Type:** Shared Context  
**CRITICAL:** Domain separation, workflows, final reminders

---

## PART 3: DOMAIN SEPARATION & WORKFLOWS

### DOMAIN SEPARATION

**SIMA uses 4-layer hierarchy:**

```
Layer 1: GENERIC (/generic/)
         ↓
Layer 2: PLATFORM (/platforms/)
         ↓
Layer 3: LANGUAGE (/languages/)
         ↓
Layer 4: PROJECT (/projects/)
```

### Generic Domain Rules

**Generic = Universal patterns only**

**MUST NOT contain:**
- Platform names (AWS, Azure, GCP)
- Language specifics (Python, JavaScript)
- Project names (LEE, SIMA)
- Specific implementations
- Vendor-specific terms
- Framework names

**MUST contain:**
- Universal principles
- Platform-agnostic patterns
- Language-agnostic concepts
- Placeholders: [PLATFORM], [LANGUAGE], [PROJECT]
- Abstract patterns

**Example - Generic:**
```markdown
✅ "Cache invalidation requires explicit strategy"
✅ "State machines prevent invalid transitions"
✅ "Input validation at entry points"

❌ "AWS Lambda requires warm-up"
❌ "Python's asyncio for concurrency"
❌ "LEE uses WebSocket protocol"
```

### Platform Domain Rules

**Platform = Platform-specific patterns**

**Contains:**
- Platform constraints (AWS Lambda 128MB)
- Platform services (DynamoDB, API Gateway)
- Platform patterns (cold starts, warming)
- Platform limitations
- Platform best practices

**References:**
- Generic patterns (via REF-ID)
- Platform documentation

**Example - Platform:**
```markdown
✅ "AWS Lambda has 128MB memory limit"
✅ "DynamoDB requires partition key strategy"
✅ "References: LESS-01 (generic caching principle)"

❌ "Use Python's boto3" (language-specific)
❌ "LEE implements this with..." (project-specific)
```

### Language Domain Rules

**Language = Language-specific patterns**

**Contains:**
- Language patterns (Python decorators, JS promises)
- Language frameworks (FastAPI, React)
- Language constraints (GIL, event loop)
- Language best practices
- Language idioms

**References:**
- Generic patterns (via REF-ID)
- Platform patterns (via REF-ID)

**Example - Language:**
```markdown
✅ "Python's function-level imports reduce memory"
✅ "FastAPI async/await for concurrency"
✅ "References: AP-03 (generic anti-pattern)"

❌ "AWS Lambda cold start" (platform-specific)
❌ "LEE's gateway uses..." (project-specific)
```

### Project Domain Rules

**Project = Specific implementations**

**Contains:**
- Specific architecture decisions
- Actual implementations
- Project constraints
- Project patterns
- Combines all layers

**References:**
- Generic, platform, and language patterns
- Explains how project implements patterns

**Example - Project:**
```markdown
✅ "LEE uses WebSocket (LESS-05) on AWS Lambda (PLAT-AWS-03) with Python asyncio (LANG-PY-07)"
✅ "Implements SUGA pattern for 3-layer architecture"
✅ "References: ARCH-SUGA, DEC-04, LESS-08"
```

---

## FILE SERVER TECHNICAL DETAILS

**Use ONLY when explicitly requested.**

### Cache-Busting System

**When file server IS used:**
- fileserver.php generates URLs with `?v=XXXXXXXXXX`
- Random 10-digit per file
- Bypasses Anthropic caching
- Fresh content guaranteed

### Usage (Explicit Only)

```
1. User uploads File-Server-URLs.md
2. User says "use file server"
3. AI fetches fileserver.php?v=XXXX
4. AI receives ~150 URLs with cache-busting
5. AI uses URLs for file access
```

### Performance

- Generation: ~70ms
- Files: ~150 (varies by system)
- Freshness: Guaranteed per session

**Remember:** File server is OPT-IN, not default.

---

## SESSION WORKFLOWS

### Standard Session Start

**Default (90% of cases):**
```
1. User activates mode: "Start Project Mode for SIMA"
2. AI searches project knowledge for context files
3. AI loads all relevant contexts
4. AI confirms: "✅ Project Mode Active. Context loaded."
5. Work begins
```

**No file upload needed. No fileserver.php fetch needed.**

### File Server Session (Explicit)

**Only when requested:**
```
1. User uploads File-Server-URLs.md
2. User says "use file server for this session"
3. AI fetches fileserver.php?v=XXXX
4. AI confirms URLs received
5. AI uses file server for session
6. Work begins
```

### Multi-Session Projects

**For projects spanning multiple sessions:**

1. Create transition file at session end
2. Document progress, next steps
3. Upload transition file to project knowledge (suggest this)
4. Next session: Load transition file from project knowledge
5. Continue work

**Transition file template:**
```markdown
# [PROJECT]-Transition-[DATE].md

**Status:** [In Progress/Blocked/Ready for Next Phase]
**Completed:**
- [List completed items]

**Next Steps:**
- [List next items]

**Context:**
[Brief context for next session]
```

---

## EFFICIENCY OPTIMIZATION

### Token Reduction Strategies

**Proactively suggest:**

1. **Upload frequently-used contexts to project knowledge**
   - Mode contexts accessed every session
   - Project-specific custom instructions
   - Architecture documentation

2. **Split large files before they're problematic**
   - Files approaching 300 lines
   - Suggest logical split points
   - Maintain completeness

3. **Use transition files for multi-session work**
   - Reduces context loading in next session
   - Upload to project knowledge
   - Quick resume

4. **Consolidate related small files**
   - Multiple 50-line files → one 250-line file
   - Reduces file management overhead
   - Easier to search

### When to Suggest Uploads

**Suggest uploading to project knowledge when:**
- Same file loaded from file server 2+ times
- Context file used every session
- Documentation referenced frequently
- File stable (not actively changing)

**Example suggestion:**
```
"I notice SIMA-PROJECT-MODE.md is loaded from file server 
each session. Would you like me to recommend uploading it 
to project knowledge? This would:
- Reduce token usage (~2000 tokens saved per session)
- Speed up mode activation (no fetch needed)
- Simplify session start (no File-Server-URLs.md needed)

Shall I prepare instructions for uploading it?"
```

---

## FINAL CRITICAL REMINDERS

### Mode Activation - NEVER FORGET

```
WHEN mode activated:
1. SEARCH project knowledge for context files
2. LOAD all relevant context files  
3. CONFIRM what was loaded
4. THEN proceed with work

NOT:
1. Acknowledge mode
2. Proceed with work
3. Forget to load context
```

### File Access - DEFAULT TO PROJECT KNOWLEDGE

```
DEFAULT: project_knowledge_search
EXPLICIT: file server (only when requested + file uploaded)

NEVER mix sources in same session.
NEVER fall back if told to use specific source.
ALWAYS stop and ask if mismatch.
```

### Output - CODE IN ARTIFACTS

```
Code >20 lines → ALWAYS artifact
Chat → Brief status only
Changes → ALWAYS marked
Files → ALWAYS complete
Lines → ALWAYS ≤350
```

### Quality - VERIFY BEFORE OUTPUT

```
☑ Context loaded?
☑ Project instructions loaded?
☑ File access correct?
☑ Code in artifact?
☑ Changes marked?
☑ ≤350 lines?
☑ Complete file?
☑ Header included?
☑ Following mode constraints?
☑ Following project patterns?
```

---

## VERSION INFORMATION

**Custom Instructions Version:** 4.3.0  
**Breaking Changes from 4.2.3:**
- Added explicit context loading protocol
- Added project-specific custom instructions loading
- Added hard stop rules for file server mismatches
- Added proactive efficiency suggestions
- Split into 3 files (350 lines each)

**Key Improvements:**
- Explicit "load context when mode activated" rule
- Clear file server vs project knowledge separation
- Project custom instructions integration
- Efficiency optimization guidance
- Better verification checklists

**Parts:**
1. Context loading, file access, mode activation
2. Artifacts, output behavior, quality standards
3. Domain separation, workflows, final reminders

---

## ASSEMBLY INSTRUCTIONS

**For user to assemble in Claude custom instructions:**

```
Copy/paste in order:
1. Custom-Instructions-for-AI-assistant-part1.md (full content)
2. Custom-Instructions-for-AI-assistant-part2.md (full content)
3. Custom-Instructions-for-AI-assistant-part3.md (full content)

Total: ~1040 lines
Organized: 3 logical sections
Maintained: ≤350 lines per file for management
```

---

## QUICK REFERENCE CARD

**Session Start:**
```
"Start [Mode] for [Project]" → Search & load contexts → Work
```

**File Access:**
```
Default → project_knowledge_search
Explicit → file server (if File-Server-URLs.md uploaded)
```

**Output:**
```
Code → Artifact (always)
Chat → Status only (brief)
Files → Complete (≤350 lines)
Changes → Marked (always)
```

**Mode Activation:**
```
1. Search for contexts
2. Load all contexts
3. Confirm loaded
4. Work
```

**Efficiency:**
```
- Suggest uploads to project knowledge
- Use transition files
- Split large files
- Consolidate small files
```

---

**END OF PART 3**

**Complete:** All 3 parts now available  
**Version:** 4.3.0  
**Lines:** 349 (AT LIMIT)  
**Total Lines (all parts):** 1046 lines

**Assemble all 3 parts into Claude custom instructions.**
