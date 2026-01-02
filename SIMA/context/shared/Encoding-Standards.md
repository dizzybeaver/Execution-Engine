# Encoding-Standards.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** UTF-8 encoding and special character standards  
**Location:** `/sima/context/shared/`

---

## UTF-8 REQUIREMENT

**All text files must use UTF-8 encoding**

**Includes:**
- Markdown files
- Source code files
- Configuration files
- Documentation files
- YAML/JSON files

---

## EMOJI SUPPORT

### Standard Emoji

**Commonly used:**
- âœ… Success/correct
- âŒ Failure/wrong
- âš ï¸ Warning/caution
- 🎯 Target/goal
- ðŸ"‚ Directory/folder
- ðŸ"„ File/document
- 🔧 Tool/utility
- ðŸš€ Launch/deploy
- ðŸ› Bug/issue
- âï¸ Time/performance

### Verification

**Test emoji rendering:**
```markdown
âœ… This should show a checkmark
âŒ This should show an X
🎯 This should show a target
```

**If broken:**
- Check file encoding (must be UTF-8)
- Verify editor settings
- Test in different viewer

---

## SPECIAL CHARACTERS

### Allowed Characters

**Arrows:**
- â†' (right arrow)
- â†

 (left arrow)
- ↑ (up arrow)
- ↓ (down arrow)

**Bullets:**
- • (bullet point)
- â—¦ (hollow bullet)
- ‣ (triangular bullet)

**Symbols:**
- © (copyright)
- ® (registered)
- â„¢ (trademark)
- § (section)

### Verification

**Test special characters:**
```
Gateway â†' Interface â†' Core
Item • Subitem â—¦ Detail
```

---

## CHARTS AND DIAGRAMS

### Markdown Tables

**Format:**
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value A  | Value B  | Value C  |
```

**Verification:**
- Columns align correctly
- Borders render
- Content displays

### ASCII Diagrams

**Format:**
```
┌─────────────┐
│   Gateway   │
└──────┬──────┘
       │
┌──────â–¼──────┐
│  Interface  │
└──────┬──────┘
       │
┌──────â–¼──────┐
│    Core     │
└─────────────┘
```

**Verification:**
- Box drawing characters work
- Layout preserved
- Arrows display

---

## COMMON ISSUES

### Problem: Broken Emoji

**Cause:** File not UTF-8 encoded

**Solution:**
1. Convert file to UTF-8
2. Re-save with UTF-8 encoding
3. Verify emoji display

### Problem: Garbled Text

**Cause:** Mixed encodings

**Solution:**
1. Identify encoding (usually Latin-1 or Windows-1252)
2. Convert to UTF-8
3. Re-save all files

### Problem: Charts Don't Render

**Cause:** Markdown formatting errors

**Solution:**
1. Check table syntax
2. Verify column alignment
3. Test in markdown previewer

---

## RELATED STANDARDS

**Complete Details:**
- SPEC-ENCODING.md - Full encoding requirements
- SPEC-MARKDOWN.md - Markdown standards
- SPEC-FILE-STANDARDS.md - File requirements

**Location:** `/sima/generic/specifications/`

---

**END OF FILE**

**Summary:** UTF-8 encoding required, emoji support verified, special characters tested, charts formatted correctly.