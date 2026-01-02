# SPEC-MARKDOWN.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Markdown formatting standards for SIMA  
**Category:** Specifications

---

## PURPOSE

Define markdown formatting standards to ensure consistency, readability, and proper rendering across all SIMA documentation.

---

## MARKDOWN FLAVOR

**Standard:** CommonMark

**Why CommonMark:**
- Unambiguous specification
- Wide tool support
- Consistent rendering
- Standard for modern systems

---

## HEADERS

### ATX Style (Preferred)
```markdown
# H1 Header
## H2 Header
### H3 Header
#### H4 Header
```

**Rules:**
- Use ATX style (# symbols)
- Space after # required
- H1 for filename only
- H2 for major sections
- H3 for subsections
- H4 sparingly

**Not allowed:**
```markdown
Header 1
========

Header 2
--------
```

---

## LISTS

### Unordered Lists
```markdown
- First item
- Second item
  - Nested item (2 spaces)
  - Another nested
- Third item
```

**Rules:**
- Use dash (-)
- Space after dash
- 2 spaces for nesting
- Blank line before/after list

### Ordered Lists
```markdown
1. First item
2. Second item
3. Third item
```

**Rules:**
- Use numbers with period
- Space after period
- Sequential numbering
- Blank line before/after

### Checklists
```markdown
- [ ] Incomplete
- [x] Complete (lowercase x)
- [OK] Alternative complete
- [X] Alternative incomplete
```

---

## EMPHASIS

### Bold
```markdown
**bold text**
```

**Use for:**
- Strong emphasis
- Field labels
- Important terms

### Italic
```markdown
*italic text*
```

**Use for:**
- Light emphasis
- Variable names
- Foreign terms

### Inline Code
```markdown
`code text`
```

**Use for:**
- Function names
- Variable names
- File names
- Commands
- Code snippets

### Combined
```markdown
**`bold code`**
*`italic code`*
```

---

## CODE BLOCKS

### Fenced Code Blocks
```markdown
```python
def function():
    return True
```
```

**Rules:**
- Use triple backticks
- Always specify language
- Blank line before/after
- Proper indentation maintained

### Supported Languages
```
python
javascript
bash
json
yaml
markdown
html
css
sql
```

### Inline Code
```markdown
Use `function()` to call it.
```

**Rules:**
- Single backticks
- No spaces inside
- For short code references

---

## LINKS

### Inline Links
```markdown
[Link Text](https://example.com)
[Link Text](relative/path/to/file.md)
```

**Rules:**
- Descriptive link text
- No bare URLs
- Relative paths for internal

### Reference Links
```markdown
[Link Text][reference-id]

[reference-id]: https://example.com
```

**Use for:**
- Multiple references to same URL
- Keeping text clean

---

## IMAGES

### Format
```markdown
![Alt Text](path/to/image.png)
```

**Rules:**
- Descriptive alt text
- Relative paths preferred
- Size via HTML if needed:
  `<img src="image.png" width="500">`

---

## BLOCKQUOTES

### Format
```markdown
> This is a blockquote
> It can span multiple lines
```

**Use for:**
- Important notes
- Quoted text
- Emphasis blocks

### Nested
```markdown
> Level 1
>> Level 2
```

---

## TABLES

### Basic Table
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |
```

### Alignment
```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| L1   | C1     | R1    |
| L2   | C2     | R2    |
```

**Rules:**
- Pipes align for readability
- Headers always present
- Separator row required
- Alignment with colons

---

## HORIZONTAL RULES

### Format
```markdown
---
```

**Rules:**
- Use triple dash
- Blank line before/after
- No other characters

**Use for:**
- After header
- Between major sections
- Before end marker

---

## LINE BREAKS

### Hard Break
```markdown
Line 1  
Line 2
```
(Two spaces at end of line 1)

### Paragraph Break
```markdown
Paragraph 1

Paragraph 2
```
(Blank line between)

**Rules:**
- Hard break: Two spaces + newline
- Paragraph: Blank line
- Prefer blank lines for clarity

---

## ESCAPING

### Escape Characters
```markdown
\* Not a bullet
\# Not a header
\[ Not a link
\` Not code
```

**Common escapes:**
- `\*` - Asterisk
- `\_` - Underscore
- `\#` - Hash
- `\[` - Bracket
- `\`` - Backtick

---

## HTML IN MARKDOWN

### Allowed (Minimal)
```html
<br>              <!-- Line break -->
<img>             <!-- Images with sizing -->
<details>         <!-- Collapsible sections -->
<summary>         <!-- Section headers -->
```

### Not Recommended
- Avoid HTML when markdown works
- Keep documents portable
- Prefer markdown tables over HTML

---

## SPECIAL FORMATTING

### Definition Lists
```markdown
Term
: Definition

Another Term
: Another definition
```

### Task Lists
```markdown
- [ ] Task 1
- [x] Task 2
- [ ] Task 3
```

---

## FORMATTING DON'TS

**Don't:**
- Mix header styles (# vs underline)
- Use HTML for basic formatting
- Create overly complex tables
- Nest lists too deeply (3+ levels)
- Use bare URLs (always use [text](url))
- Forget blank lines around blocks
- Use spaces for alignment (except lists)

---

## QUALITY CHECKLIST

- [ ] ATX-style headers (# ## ###)
- [ ] Dash (-) for unordered lists
- [ ] Language specified in code blocks
- [ ] Blank lines around code blocks
- [ ] Proper link formatting
- [ ] Tables aligned and formatted
- [ ] Horizontal rules (---)
- [ ] Consistent emphasis style
- [ ] No bare URLs
- [ ] Escape special characters

---

## COMMON MISTAKES

**Mistake:** No language in code block  
**Fix:** Always add language: ` ```python `

**Mistake:** Missing blank lines  
**Fix:** Add blank before/after blocks

**Mistake:** Bare URLs  
**Fix:** Use `[text](url)` format

**Mistake:** Inconsistent list markers  
**Fix:** Use dash (-) consistently

**Mistake:** Mixed header styles  
**Fix:** Use ATX style (# symbols) only

---

## RENDERING VERIFICATION

### Test Rendering
1. Create artifact
2. Verify all elements display
3. Check code highlighting
4. Confirm links work
5. Validate tables align

### Common Rendering Issues
- **Missing blank lines:** Blocks not rendering
- **Wrong code fence:** No syntax highlighting
- **Bare URLs:** Not clickable
- **Misaligned tables:** Extra/missing pipes

---

## BENEFITS

**Proper markdown provides:**
- Consistent rendering
- Better readability
- Tool compatibility
- Easy maintenance
- Professional appearance
- Copy-paste friendly

---

**Related:**
- SPEC-FILE-STANDARDS.md
- SPEC-STRUCTURE.md
- SPEC-ENCODING.md

**Version History:**
- v4.2.2-blank (2025-11-10): Blank slate version
- v1.0.0 (2025-11-06): Initial markdown specification

---

**END OF FILE**