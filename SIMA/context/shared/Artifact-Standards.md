# Artifact-Standards.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Standards for creating artifacts in all modes  
**Location:** `/sima/context/shared/`

---

## WHEN TO USE ARTIFACTS

**MANDATORY for:**
- Code snippets > 20 lines
- ANY file modification
- New file creation
- Configuration files
- Neural map files
- Structured content (plans, outlines, etc.)

**NEVER output code in chat**

---

## COMPLETE FILES ONLY

**Rule: Never create fragments**

âœ… **CORRECT:**
- Include ALL existing code
- Add your modifications
- Mark changes with comments
- Complete, deployable file

âŒ **WRONG:**
- Partial snippets
- "Add this to line X" instructions
- Excerpts without context
- Fragmented code

---

## CHANGE MARKING

**Mark all modifications:**

```python
# ADDED: New cache warming function for cold start
def warm_cache():
    """Pre-load frequently accessed data."""
    # Implementation...

# MODIFIED: Enhanced error handling and validation
def existing_function(data):
    """Process data with improvements."""
    # ADDED: Input validation
    if not validate_data(data):
        raise ValueError("Invalid input")
    
    # Original logic continues...
```

**Change markers:**
- `# ADDED:` - New code/functions
- `# MODIFIED:` - Changed existing code
- `# FIXED:` - Bug fixes
- `# REMOVED:` - Deleted code (show in comment)

---

## FILE HEADERS

**MANDATORY in every artifact:**

```markdown
# filename.md

**Version:** 1.0.0
**Date:** 2025-11-10
**Purpose:** [Brief description]
```

**For code files:**
```python
# filename.py
"""
Brief description of module.

Version: 1.0.0
Date: 2025-11-10
"""
```

---

## FILE SIZE LIMITS

**Strict limits:**
- Source code: â‰¤400 lines
- Neural maps: â‰¤400 lines
- Summaries: â‰¤100 lines
- Plans: â‰¤50 lines

**If exceeding:**
- Split into multiple files
- Create separate focused files
- Never condense multiple topics

---

## ENCODING STANDARDS

**UTF-8 required:**
- All text files
- Emoji support
- Special characters

**Verification:**
- Test emoji rendering: âœ… âŒ 🎯
- Check charts display
- Validate markdown

---

## PRE-OUTPUT CHECKLIST

**MANDATORY before EVERY artifact:**

```
[ ] Fetched current file? (if modifying)
[ ] Read complete file?
[ ] Including ALL existing code?
[ ] Marked changes with comments?
[ ] Creating artifact (not chat)?
[ ] Complete file (not fragment)?
[ ] Filename in header?
[ ] File ≤400 lines?
[ ] Emojis/charts encoded correctly?
[ ] Chat output minimal?
```

---

## CHAT OUTPUT RULES

**Keep minimal:**

âœ… **CORRECT:**
- "Creating artifact..."
- "Fix complete. Test with original case."
- Brief status (2-3 sentences max)

âŒ **WRONG:**
- Long explanations in chat
- Verbose commentary
- Narrative descriptions
- Code in chat

**Let artifacts speak for themselves**

---

## EXAMPLE: FILE MODIFICATION

**Process:**
1. Fetch current file via fileserver.php URL
2. Read ENTIRE file
3. Create artifact with:
   - ALL existing code
   - Your modifications marked
   - Complete from line 1 to end
4. Brief chat: "Modified X. Ready to deploy."

**Never:**
- Output partial file
- Say "add this code"
- Show snippets in chat
- Skip fetching current version

---

## EXAMPLE: NEW FILE

**Process:**
1. Create complete file
2. Include all necessary:
   - Header with version/date
   - Imports
   - Implementation
   - Documentation
3. Mark as: `# ADDED: [Description]`
4. Brief chat: "Created X. Ready to deploy."

---

## QUALITY STANDARDS

**Every artifact must be:**

1. **Complete** - Immediately deployable
2. **Marked** - Changes clearly indicated
3. **Documented** - Headers and docstrings
4. **Size-Limited** - â‰¤400 lines (source/neural maps)
5. **Encoded Correctly** - UTF-8, emojis work
6. **Properly Formatted** - Markdown/code standards

---

## SELF-CORRECTION

**If you catch yourself typing code in chat:**

1. STOP immediately
2. Delete code from chat
3. Create artifact instead
4. Include ALL existing code
5. Mark changes
6. Keep chat brief

---

## RELATED STANDARDS

**File Standards:** SPEC-FILE-STANDARDS.md  
**Line Limits:** SPEC-LINE-LIMITS.md  
**Headers:** SPEC-HEADERS.md  
**Encoding:** SPEC-ENCODING.md  
**Markdown:** SPEC-MARKDOWN.md

**Location:** `/sima/generic/specifications/`

---

**END OF FILE**

**Summary:** All code in complete file artifacts, marked changes, â‰¤400 lines, minimal chat.