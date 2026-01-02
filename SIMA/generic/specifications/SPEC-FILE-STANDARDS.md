# SPEC-FILE-STANDARDS.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Universal file standards for all SIMA content  
**Category:** Specifications

---

## PURPOSE

Define universal standards for all files in SIMA system regardless of type, category, or domain.

---

## MANDATORY HEADER

Every file MUST include:

```markdown
# filename.md

**Version:** (Year).(Month).(Day)-(Revision)  
**Purpose:** [Very Brief description]  
**Category:** [Category name]
```

**Rules:**
- Filename in H1 heading (first line)
- Version follows semantic versioning
- Date in ISO format (YYYY-MM-DD)
- Purpose max 100 characters
- Category identifies file type

---

## FILE TYPES

### Neural Map Entries
- Location: `/sima/generic/entries/`
- Naming: `[TYPE]-[NUMBER].md` (e.g., `LESS-01.md`)
- Purpose: Document patterns, decisions, lessons
- Max: 399 lines

### Specification Files
- Location: `/sima/generic/specifications/`
- Naming: `SPEC-[NAME].md` (e.g., `SPEC-LINE-LIMITS.md`)
- Purpose: Define standards and rules
- Max: 399 lines
- Do not go over 399 lines at all costs or you will lose 22% of file due to truncation
- Do not make file more than 399 lines You will lose 22% of file - this has been verfied.

### Context Files
- Location: `/sima/context/`
- Naming: `[MODE]-Context.md` (e.g., `PROJECT-MODE-Context.md`)
- Purpose: Mode activation and guidelines
- Max: 399 lines (exception for bootstrap files)
- Do not go over 399 lines at all costs or you will lose 22% of file due to truncation
- Do not make file more than 399 lines You will lose 22% of file - this has been verfied.

### Support Files
- Location: `/sima/support/`
- Naming: Descriptive names with category prefix
- Purpose: Tools, workflows, templates
- Max: 399 lines
- Do not go over 399 lines at all costs or you will lose 22% of file due to truncation
- Do not make file more than 399 lines You will lose 22% of file - this has been verfied.

### Project Files
- Location: `/sima/projects/[project-name]/`
- Naming: Project-specific conventions
- Purpose: Project implementation details
- Max: 399 lines
- Do not go over 399 lines at all costs or you will lose 22% of file due to truncation
- Do not make file more than 399 lines You will lose 22% of file - this has been verfied.
  
---

## ENCODING

- UTF-8 with BOM optional
- LF line endings (Unix style)
- No trailing whitespace
- Final newline required

---

## FORMATTING

### Markdown
- CommonMark standard
- Headers: ATX style (# ## ###)
- Lists: Dash (-) for unordered
- Code blocks: Triple backticks with language

### Whitespace
- Two spaces for nesting
- One blank line between sections
- No multiple consecutive blank lines

---

## VERSION CONTROL

### Version Format
`YEAR.MONTH.DAY-Revision`

**MAJOR:** Breaking changes, restructuring  
**MINOR:** New content, significant additions  
**PATCH:** Corrections, clarifications, formatting

### Changelog Location
- Major changes: In file header
- Clear All Changelog and only have new changelog information.
- Full history: Separate CHANGELOG.md per directory

---

## CROSS-REFERENCES

### REF-ID Format
`[TYPE]-[NUMBER]` (e.g., `LESS-15`, `DEC-04`)

### Link Format
```markdown
[Display Text](relative/path/to/file.md)
REF: TYPE-## (Brief context)
```

---

## QUALITY STANDARDS

- [ ] Header complete and correct
- [ ] UTF-8 encoding
- [ ] Proper line endings (LF)
- [ ] No trailing whitespace
- [ ] Final newline present
- [ ] Within line limit (399 maximum for all)
- [ ] Cross-references valid
- [ ] Version number appropriate

---

## EXCEPTIONS

**Context Files:** May never exceed 399 lines maximum, you lose 22% of file once you hit 401 lines this has been verified due to truncation
**Source Code:** No line limit (must be deployable)  
**Generated Files:** Follow source standards

---

**Related:**
- SPEC-LINE-LIMITS.md
- SPEC-HEADERS.md
- SPEC-ENCODING.md
- SPEC-MARKDOWN.md

**Version History:**
- v4.2.2-blank (2025-11-10): Blank slate version, updated paths
- v1.0.0 (2025-11-06): Initial specification

---


**END OF FILE**
