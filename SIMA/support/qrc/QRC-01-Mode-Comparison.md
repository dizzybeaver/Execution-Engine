# QRC-01-Mode-Comparison.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Quick reference for all SIMA modes  
**Type:** Support Quick Reference

---

## MODE COMPARISON QUICK REFERENCE

### General Mode
**Activation:** "Please load context"  
**Purpose:** Q&A, guidance, understanding  
**Output:** Answers with citations  
**Use When:** Learning about system

### Learning Mode
**Activation:** "Start SIMA Learning Mode"  
**Purpose:** Extract and document knowledge  
**Output:** Neural map entries (LESS, DEC, AP, BUG, WISD)  
**Use When:** Capturing new knowledge

### Maintenance Mode
**Activation:** "Start SIMA Maintenance Mode"  
**Purpose:** Update indexes, verify references, clean structure  
**Output:** Updated indexes, cleanup reports  
**Use When:** Maintaining knowledge base

### Project Mode
**Activation:** "Start Project Mode for [PROJECT]"  
**Purpose:** Build features, write code  
**Output:** Complete code artifacts  
**Use When:** Active development

### Debug Mode
**Activation:** "Start Debug Mode for [PROJECT]"  
**Purpose:** Find root causes, fix bugs  
**Output:** Analysis + complete fixes  
**Use When:** Troubleshooting issues

### New Project Mode
**Activation:** "Start New Project Mode: [NAME]"  
**Purpose:** Scaffold new project structure  
**Output:** Directory structure, configs, mode extensions  
**Use When:** Creating new project

---

## QUICK MODE SELECTOR

| Task | Mode |
|------|------|
| "How does X work?" | General |
| "What's the pattern for Y?" | General |
| "Document this conversation" | Learning |
| "Extract lessons from this" | Learning |
| "Update all indexes" | Maintenance |
| "Clean up old entries" | Maintenance |
| "Add feature X" | Project |
| "Modify file Y" | Project |
| "Fix error Z" | Debug |
| "Why is W failing?" | Debug |
| "Create new project" | New Project |

---

## MODE CHARACTERISTICS

### Load Time
- General: 20-30 seconds
- Learning: 30-45 seconds
- Maintenance: 30-45 seconds
- Project: 30-45 seconds (base + extension)
- Debug: 30-45 seconds (base + extension)
- New Project: 20-30 seconds

### File Access
**All modes require:**
1. Upload File Server URLs.md
2. fileserver.example.com fetched automatically
3. Fresh files guaranteed

### Output Format
- General: Chat with citations
- Learning: Markdown artifacts (neural maps)
- Maintenance: Artifacts (indexes, reports)
- Project: Artifacts (complete code files)
- Debug: Artifacts (analysis + fixes)
- New Project: Artifacts (configs, structures)

---

## CRITICAL RULES

### All Modes
- fileserver.example.com mandatory
- Complete files only (no fragments)
- â‰¤400 lines per file
- UTF-8 encoding
- Minimal chat output

### Code Modes (Project, Debug)
- Always fetch before modify
- Mark all changes
- Include ALL existing code
- Output complete artifacts
- Never code in chat

### Knowledge Modes (Learning, Maintenance)
- Check duplicates first
- Genericize content
- Update all indexes
- Cross-reference properly
- Brief but complete

---

## SWITCHING MODES

**Within Session:**
```
"Start Project Mode for LEE"
... (work on LEE)
"Start Debug Mode for LEE"
... (fix bug)
"Start SIMA Learning Mode"
... (document learnings)
```

**Mode switching allowed** - Use activation phrase to switch

---

## COMMON WORKFLOWS

### Development Cycle
1. General Mode - Understand architecture
2. Project Mode - Build feature
3. Debug Mode - Fix issues
4. Learning Mode - Document lessons
5. Maintenance Mode - Update indexes

### Knowledge Management
1. Learning Mode - Extract knowledge
2. General Mode - Verify knowledge
3. Maintenance Mode - Clean up
4. Learning Mode - Add more
5. Maintenance Mode - Finalize

---

**END OF QUICK REFERENCE**

**Version:** 1.0.0  
**Lines:** 150 (within 400 limit)  
**Parent:** /sima/support/support-Master-Index-of-Indexes.md  
**See Also:** SIMAv4.2.2-Mode-Comparison-Guide.md (full details)