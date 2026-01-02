# SPEC-STRUCTURE.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Document structure and organization standards  
**Category:** Specifications

---

## PURPOSE

Define internal structure and organization for SIMA documents to ensure consistency and readability.

---

## DOCUMENT SECTIONS

### Standard Order
1. Header (required)
2. Purpose (required)
3. Content sections (variable)
4. Related links (optional)
5. Version history (optional)
6. End marker (optional)

---

## HEADER SECTION

**Format:**
```markdown
# filename.md

**Version:** (Year).(Month).(Day)-(Revision)
**Purpose:** Very Brief description  
**Category:** Category name

---
```

**Rules:**
- Always first in file
- Separated by horizontal rule
- No content before header
- See SPEC-HEADERS.md for details

---

## PURPOSE SECTION

**Format:**
```markdown
## PURPOSE

[Clear statement of document's purpose and scope]

---
```

**Rules:**
- H2 heading (##)
- 1-3 sentences
- What and why
- Separated by horizontal rule

**Example:**
```markdown
## PURPOSE

Define verification protocol to ensure code changes follow architectural patterns, avoid anti-patterns, and maintain system integrity before deployment.

---
```

---

## CONTENT SECTIONS

### Section Headers
**Use H2 (##) for major sections:**
```markdown
## MAJOR SECTION
```

**Use H3 (###) for subsections:**
```markdown
### Subsection
```

**Use H4 (####) sparingly:**
```markdown
#### Minor Detail
```

### Section Order
1. Overview/Introduction
2. Core concepts
3. Implementation details
4. Examples
5. Validation/Testing
6. Troubleshooting (if applicable)

### Section Spacing
- One blank line before header
- No blank line after header
- One blank line after section content
- Sections separated by horizontal rule (optional)

---

## CONTENT ELEMENTS

### Lists

**Unordered lists (-):**
```markdown
- First item
- Second item
  - Nested item
  - Another nested
```

**Ordered lists (1.):**
```markdown
1. First step
2. Second step
3. Third step
```

**Checklist ([]):**
```markdown
- [ ] Incomplete task
- [x] Completed task
- [OK] Alternative complete
- [X] Alternative incomplete
```

### Code Blocks

**With language:**
```markdown
```python
def function():
    return True
```
```

**Without language (plain):**
```markdown
```
Plain text or output
```
```

### Blockquotes

**Use for emphasis or quotes:**
```markdown
> Important note or quoted text
```

### Tables

**Simple format:**
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |
```

**Alignment:**
```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| L1   | C1     | R1    |
```

---

## EXAMPLES SECTION

### Format
```markdown
## EXAMPLES

### Example 1: [Description]
[Explanation]

```[language]
[code]
```

[Result or output]

### Example 2: [Description]
[Explanation]
```

### Rules
- H3 for each example
- Brief description
- Code in blocks
- Explain result
- 2-3 examples max

---

## CROSS-REFERENCES

### Internal Links
```markdown
[Link Text](relative/path/to/file.md)
```

### REF-ID References
```markdown
REF: TYPE-##, TYPE-##

Related:
- TYPE-##: Brief description
- TYPE-##: Brief description
```

### Related Section
**At document end:**
```markdown
**Related:**
- SPEC-FILE-STANDARDS.md
- SPEC-HEADERS.md
- LESS-15.md
```

---

## VERSION HISTORY

### Format
```markdown
**Version History:**
- v1.2.0 (2025-11-10): Added new section on X
- v1.1.0 (2025-11-01): Enhanced Y with examples
- v1.0.0 (2025-10-25): Initial creation
```

### Rules
- Newest first
- Date in ISO format
- Brief description of changes
- Major/minor changes only (not patches)

---

## END MARKER

### Format
```markdown
---

**END OF FILE**
```

### Rules
- Optional but recommended
- Horizontal rule before
- Clear termination point
- Helpful for long files

---

## FORMATTING GUIDELINES

### Emphasis
**Bold:** `**text**` for strong emphasis  
*Italic:* `*text*` for light emphasis  
`Code:` `` `text` `` for inline code

### Separators
**Horizontal rule:** `---` (triple dash)

**Use for:**
- After header
- Between major sections
- Before end marker

### Blank Lines
**Required:**
- After headers (one line)
- Between list items with sub-content
- Before/after code blocks
- Between major sections

**Not needed:**
- After section headers
- Between consecutive list items
- In code blocks

---

## DOCUMENTATION TYPES

### Neural Map Entry Structure
```markdown
# TYPE-##.md

**Header fields**

---

## TITLE

Brief overview

---

## PATTERN/PROBLEM

Description

---

## SOLUTION/APPROACH

Implementation

---

## EXAMPLE

Code or scenario

---

## PREVENTION/APPLICATION

How to apply

---

**Related:** [links]
**Version History:** [history]
```

### Specification Structure
```markdown
# SPEC-NAME.md

**Header fields**

---

## PURPOSE

What this spec defines

---

## STANDARD

The standard itself

---

## RULES

Specific rules

---

## EXAMPLES

Demonstrations

---

## VALIDATION

How to verify

---

**Related:** [links]
```

### Workflow Structure
```markdown
# Workflow-##-Name.md

**Header fields**

---

## PURPOSE

What workflow accomplishes

---

## PREREQUISITES

Required before starting

---

## STEPS

1. Step one
2. Step two
...

---

## VERIFICATION

How to confirm success

---

## TROUBLESHOOTING

Common issues

---

**Related:** [links]
```

---

## QUALITY CHECKLIST

- [ ] Header present and complete
- [ ] Purpose section clear
- [ ] Sections logically ordered
- [ ] Consistent heading levels
- [ ] Proper spacing throughout
- [ ] Code blocks have language
- [ ] Examples are clear
- [ ] Cross-references valid
- [ ] Version history (if applicable)
- [ ] End marker (optional)

---

## COMMON MISTAKES

**Mistake:** Inconsistent header levels  
**Fix:** Use H2 for main, H3 for sub, H4 sparingly

**Mistake:** Missing blank lines  
**Fix:** One line after headers, between sections

**Mistake:** Code without language  
**Fix:** Always specify language in code blocks

**Mistake:** Too many header levels  
**Fix:** Limit to H2, H3, rarely H4

**Mistake:** Walls of text  
**Fix:** Break into sections with headers

---

**Related:**
- SPEC-FILE-STANDARDS.md
- SPEC-HEADERS.md
- SPEC-MARKDOWN.md
- SPEC-LINE-LIMITS.md

**Version History:**
- v4.2.2-blank (2025-11-10): Blank slate version
- v1.0.0 (2025-11-06): Initial structure specification

---


**END OF FILE**
