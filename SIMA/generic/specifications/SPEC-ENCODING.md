# SPEC-ENCODING.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Character encoding and line ending standards  
**Category:** Specifications

---

## PURPOSE

Define character encoding, line endings, and special character handling for all SIMA files.

---

## CHARACTER ENCODING

### Standard
**UTF-8** (Unicode Transformation Format - 8 bit)

### Rules
- All text files MUST be UTF-8
- BOM (Byte Order Mark) optional
- No other encodings allowed
- Verify encoding before commit

### Why UTF-8
- Universal support
- ASCII compatible
- Efficient storage
- Handles all languages
- Standard for modern systems

---

## LINE ENDINGS

### Standard
**LF** (Line Feed, `\n`, Unix-style)

### Rules
- Use LF for all files
- Never CRLF (Windows style)
- Configure editor/IDE
- Git auto-conversion off

### Git Configuration
```bash
# .gitattributes
* text=auto eol=lf
*.md text eol=lf
*.py text eol=lf
```

### Why LF
- Unix/Linux standard
- Smaller file size
- Consistent across platforms
- Modern editors support
- Standard for deployment

---

## SPECIAL CHARACTERS

### Emojis
**Allowed:** Yes, with proper UTF-8 encoding

**Rules:**
- Test rendering in artifacts
- Verify display on all platforms
- Use standard emoji codes
- Avoid custom/proprietary emojis

**Examples:**
```markdown
✅ Check mark
❌ Cross mark
⚠️ Warning
🎯 Target
🔄 Refresh
📂 Folder
🛠️ Tools
```

### Unicode Characters
**Allowed:** Yes, sparingly

**Preferred characters:**
- Arrows: → ← ↑ ↓
- Math: ≤ ≥ ≠ ±
- Symbols: • ° ™ © ®

**Avoid:**
- Obscure characters
- Platform-specific symbols
- Decorative unicode

### ASCII Art
**Allowed:** Simple diagrams

**Rules:**
- Keep simple
- Use for clarity
- Test rendering
- Provide text alternative

**Example:**
```
Gateway → Interface → Core
   |         |          |
   +--- Lazy imports ---+
```

---

## WHITESPACE

### Spaces vs Tabs
**Standard:** Spaces only

**Rules:**
- No tab characters
- 2 spaces for indentation
- Consistent across file
- Configure editor

### Trailing Whitespace
**Rule:** Never allowed

**Why:**
- Causes diff noise
- No functional purpose
- Professional standard
- Cleaner files

### Final Newline
**Rule:** Always required

**Why:**
- POSIX standard
- Better git diffs
- Expected by tools
- Professional standard

---

## QUOTES

### Markdown
**Use:** Double quotes for emphasis
```markdown
"quoted text"
```

### Code
**Use quotes appropriate to language:**
```python
# Python - single quotes
name = 'value'

# Python - double quotes for f-strings
message = f"Hello {name}"

# Python - triple quotes for docstrings
"""
Multi-line docstring
"""
```

### Inline Code
**Use:** Backticks
```markdown
Use `function_name()` in your code
```

---

## SPECIAL SEQUENCES

### Line Breaks
**Markdown:** Two spaces + newline OR blank line

**Example:**
```markdown
Line 1  
Line 2

Paragraph break
```

### Non-Breaking Spaces
**Avoid** unless absolutely necessary

**Alternative:** Use `&nbsp;` in HTML context only

### Escape Characters
**Use:** Backslash when needed

**Example:**
```markdown
\* Not a bullet point
\# Not a header
```

---

## VALIDATION

### Encoding Check
```bash
# Check file encoding
file -I filename.md

# Should show: text/plain; charset=utf-8
```

### Line Ending Check
```bash
# Check line endings
file filename.md

# Should show: ASCII text (no CRLF)

# Or use dos2unix
dos2unix -ih filename.md
```

### Whitespace Check
```bash
# Find trailing whitespace
grep -n '[[:space:]]$' filename.md

# Find tabs
grep -n $'\t' filename.md
```

### Emoji Test
Create artifact:
1. Include emoji in artifact
2. Verify displays correctly
3. Check no encoding errors

---

## EDITOR CONFIGURATION

### VS Code
```json
{
  "files.encoding": "utf8",
  "files.eol": "\n",
  "files.insertFinalNewline": true,
  "files.trimTrailingWhitespace": true,
  "editor.tabSize": 2,
  "editor.insertSpaces": true
}
```

### .editorconfig
```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
indent_style = space
indent_size = 2

[*.py]
indent_style = space
indent_size = 4
```

---

## COMMON ISSUES

### Issue: Emoji Not Rendering
**Cause:** Incorrect UTF-8 encoding  
**Fix:** Save file as UTF-8, verify encoding

### Issue: Line Ending Mismatch
**Cause:** Editor converting to CRLF  
**Fix:** Configure editor for LF, update .gitattributes

### Issue: Trailing Whitespace
**Cause:** Editor not configured  
**Fix:** Enable trim-on-save in editor

### Issue: Missing Final Newline
**Cause:** Editor setting  
**Fix:** Enable insert-final-newline

### Issue: Tabs Instead of Spaces
**Cause:** Editor default  
**Fix:** Configure indent-with-spaces

---

## MIGRATION

### Converting Existing Files
```bash
# Convert CRLF to LF
dos2unix filename.md

# Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 filename.md > filename_utf8.md

# Remove trailing whitespace
sed -i 's/[[:space:]]*$//' filename.md

# Add final newline
echo >> filename.md
```

---

## QUALITY CHECKLIST

- [ ] UTF-8 encoding verified
- [ ] LF line endings (no CRLF)
- [ ] No trailing whitespace
- [ ] Final newline present
- [ ] No tab characters (spaces only)
- [ ] Emojis render correctly
- [ ] Special characters display
- [ ] Editor configured correctly

---

## BENEFITS

**Proper encoding provides:**
- Cross-platform compatibility
- Consistent rendering
- Smaller diffs
- Professional appearance
- Tool compatibility
- No encoding errors
- Universal emoji support

---

**Related:**
- SPEC-FILE-STANDARDS.md
- SPEC-MARKDOWN.md
- SPEC-HEADERS.md

**Version History:**
- v4.2.2-blank (2025-11-10): Blank slate version
- v1.0.0 (2025-11-06): Initial encoding specification

---

**END OF FILE**