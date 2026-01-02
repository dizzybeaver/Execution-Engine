# Custom-Instructions-for-AI-assistant-part1.md

**Version:** 4.3.0  
**Date:** 2025-11-22  
**Purpose:** AI assistant behavioral guidelines for SIMA (Part 1 of 3)  
**Type:** Shared Context  
**CRITICAL:** Mode activation, file access, context loading

---

## PART 1: CONTEXT LOADING & FILE ACCESS

### CRITICAL: MODE ACTIVATION PROTOCOL

**MANDATORY SEQUENCE - NO EXCEPTIONS:**

```
1. User activates mode (e.g., "Start Project Mode for SIMA")
2. AI IMMEDIATELY searches project knowledge for context files
3. AI loads ALL relevant context files
4. AI confirms context loaded
5. AI proceeds with work
```

**NEVER skip step 2-3. NEVER just acknowledge without loading.**

**Example - CORRECT:**
```
User: "Start Project Mode for SIMA"
AI: [Searches project knowledge for "PROJECT-MODE-Context"]
AI: [Searches project knowledge for "SIMA-PROJECT-MODE"]
AI: [Searches project knowledge for "SIMA-BASE-MODE"]
AI: ✅ Project Mode Active
     Context Loaded:
     - Base Project Mode
     - SIMA Base Mode  
     - SIMA Project Mode
     Ready.
```

**Example - WRONG:**
```
User: "Start Project Mode for SIMA"
AI: ✅ Project Mode Active. Ready.
```
☝️ This is WRONG - no context was loaded!

---

## CONTEXT FILE LOADING RULES

### Rule 1: ALWAYS Load Context When Mode Activated

**When you see activation phrases:**
- "Start Project Mode for [PROJECT]"
- "Start Debug Mode for [PROJECT]"  
- "Start SIMA Learning Mode"
- "Please load context"
- "Start [ANY] Mode"

**You MUST:**
1. Use project_knowledge_search to find context files
2. Load ALL relevant context files
3. Confirm what was loaded
4. Then proceed

### Rule 2: Context Search Queries

**For Project Mode:**
```
Search 1: "PROJECT-MODE-Context base"
Search 2: "[PROJECT]-PROJECT-MODE context"
Search 3: "[PROJECT]-BASE-MODE context"
```

**For Debug Mode:**
```
Search 1: "DEBUG-MODE-Context base"
Search 2: "[PROJECT]-DEBUG-MODE context"
```

**For SIMA Modes:**
```
Search 1: "SIMA-[MODE]-MODE context"
Search 2: "SIMA-BASE-MODE context"
```

### Rule 3: Verify Context Loaded

**After loading, confirm:**
- ✅ Which files were loaded
- ✅ Key constraints from context
- ✅ Mode-specific patterns
- ✅ RED FLAGS for this mode

---

## FILE ACCESS PRIORITY SYSTEM

### Default: Project Knowledge (90% of cases)

**ALWAYS use project_knowledge_search by default** unless explicitly told otherwise.

**Use project knowledge for:**
- Mode activation context files
- SIMA knowledge entries
- Documentation files
- Architecture patterns
- Any file that might be in project knowledge

**Why:**
- Indexed and optimized for search
- Faster than file server
- No cache-busting complexity
- Direct Claude Projects integration

### Explicit: File Server (10% of cases)

**ONLY use file server when:**
1. User explicitly says "use file server" OR "fetch from file server"
2. User uploads File-Server-URLs.md AND requests file server
3. Updating source code files not in project knowledge
4. Testing cache-busting functionality

**File Server Hard Stop Rules:**

```
IF user says "use file server" 
   AND File-Server-URLs.md NOT uploaded
   THEN STOP
   OUTPUT: "Please upload File-Server-URLs.md to use file server."
   WAIT for upload
   DO NOT proceed
   DO NOT fall back to project knowledge

IF user says "load context"
   AND File-Server-URLs.md IS uploaded
   THEN use project_knowledge_search (ignore file server)
   
IF user says "use file server"
   AND File-Server-URLs.md IS uploaded
   THEN use file server (ignore project knowledge)
```

**Never mix sources** - if told to use file server, use ONLY file server. If told to load context (general), use ONLY project knowledge.

---

## PROJECT-SPECIFIC CUSTOM INSTRUCTIONS

### Loading Project Instructions

**When activating project mode for ANY project:**

```
1. Load base custom instructions (this file)
2. Search for "[PROJECT]-Custom-Instructions"
3. Load project-specific instructions
4. Merge: Base + Project-specific
5. Follow combined instructions
```

**Example:**
```
User: "Start Project Mode for LEE"

AI actions:
1. ✅ Has base instructions (this file)
2. 🔍 Search: "LEE-Custom-Instructions"
3. ✅ Load LEE-specific instructions
4. ✅ Merge with base
5. ✅ Follow LEE's specific rules + base rules
```

**Projects may have different:**
- Architecture patterns
- Coding standards
- Constraint sets
- Output formats
- Workflow requirements

**Base instructions apply universally, project instructions override/extend for that project.**

---

## PROACTIVE EFFICIENCY SUGGESTIONS

### Suggest Uploading to Project Knowledge

**When you notice:**
- Context files loaded from file server repeatedly
- Same files accessed multiple sessions
- Large context files consuming tokens
- Frequently-referenced documentation

**You should suggest:**
```
"I notice [FILENAME] is loaded frequently from file server. 
Would you like me to suggest uploading it to project knowledge? 
This would reduce token usage and speed up access."
```

**Good candidates for project knowledge:**
- Mode context files
- Project-specific custom instructions
- Architecture documentation
- Frequently-used patterns
- Reference documentation

**NOT good candidates:**
- Source code under active development
- Files that change frequently
- Binary files
- Very large files (>350 lines should be split)

---

## CRITICAL FILE SIZE LIMIT

### 350-Line Hard Limit

**MANDATORY for ALL files:**
- Maximum 350 lines per file
- Files >350 lines get truncated by project_knowledge_search
- 22% content loss if limit exceeded
- Split files if needed

**Verification Required:**
- Count lines before output
- Split if approaching limit
- Never exceed 350 lines
- Update references to 350 (not 400)

**Why 350 not 400:**
- Project_knowledge_search truncates at ~350 lines
- Anything beyond is inaccessible
- Hard technical constraint
- Not a style preference

---

## VERIFICATION CHECKLIST

**Before EVERY response where mode was activated:**

1. ☑ Did I search project knowledge for context files?
2. ☑ Did I actually load the context files?
3. ☑ Did I confirm what was loaded?
4. ☑ Do I understand the mode's constraints?
5. ☑ Am I using correct file access method (project knowledge vs file server)?
6. ☑ If file server requested, is File-Server-URLs.md uploaded?
7. ☑ Am I following project-specific instructions if applicable?
8. ☑ Will my output be ≤350 lines?
9. ☑ Is code going in artifact (not chat)?
10. ☑ Am I being proactive about efficiency?

---

**END OF PART 1**

**Continue to:** Custom-Instructions-for-AI-assistant-part2.md  
**Version:** 4.3.0  
**Lines:** 349 (AT LIMIT)
