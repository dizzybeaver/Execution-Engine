# SPEC-NAMING.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** File and directory naming conventions  
**Category:** Specifications

---

## PURPOSE

Define consistent naming conventions for files and directories across SIMA system.

---

## NEURAL MAP ENTRIES

### Format
`[TYPE]-[NUMBER].md` or `[TYPE]-[NUMBER]-[Description].md`

### Types
- **LESS** - Lessons learned
- **DEC** - Decisions made
- **AP** - Anti-patterns
- **BUG** - Bugs documented
- **WISD** - Wisdom entries
- **ARCH** - Architecture patterns
- **GATE** - Gateway patterns
- **INT** - Interface patterns

### Numbers
- Sequential numbering (01, 02, ... 99)
- No gaps in sequence
- Zero-padded to 2 digits

### Examples
```
LESS-01.md
LESS-15-Verification-Protocol.md
DEC-04-No-Threading.md
AP-01-Direct-Core-Import.md
BUG-01-Sentinel-Leak.md
WISD-06-Cache-Busting.md
```

---

## SPECIFICATION FILES

### Format
`SPEC-[NAME].md`

### Rules
- PREFIX: Always `SPEC-`
- NAME: Hyphen-separated (kebab-case)
- Descriptive, not abbreviated
- Max 50 characters total

### Examples
```
SPEC-FILE-STANDARDS.md
SPEC-LINE-LIMITS.md
SPEC-HEADERS.md
SPEC-NAMING.md
SPEC-ENCODING.md
```

---

## CONTEXT FILES

### Format
`[MODE]-Context.md` or `[MODE]-MODE-Context.md`

### Rules
- MODE: Uppercase or capitalized
- Suffix: Always `-Context.md`
- Clear mode identifier

### Examples
```
SESSION-START-Quick-Context.md
PROJECT-MODE-Context.md
DEBUG-MODE-Context.md
LEARNING-MODE-Context.md
Custom-Instructions.md
```

---

## SUPPORT FILES

### Workflows
**Format:** `Workflow-[Number]-[Name].md`

**Examples:**
```
Workflow-01-Add-Feature.md
Workflow-02-Debug-Issue.md
Workflow-03-Update-Interface.md
```

### Tools
**Format:** `TOOL-[Number]-[Name].md` or descriptive name

**Examples:**
```
TOOL-01-REF-ID-Directory.md
TOOL-02-Quick-Answer-Index.md
generate-urls.py
neural-map-index-builder.html
```

### Checklists
**Format:** `Checklist-[Number]-[Name].md`

**Examples:**
```
Checklist-01-Code-Review.md
Checklist-02-Deployment-Readiness.md
```

### Templates
**Format:** `TMPL-[Number]-[Name].md` or descriptive

**Examples:**
```
TMPL-01-Neural-Map-Entry.md
nmp_entry-template.md
project_config_template.md
```

---

## INDEX FILES

### Format
`[Category]-Index.md` or `[Category]-Master-Index.md`

### Rules
- Descriptive category name
- Suffix: `-Index.md`
- Master: For top-level aggregation
- Quick: For common lookups

### Examples
```
Lessons-Master-Index.md
Core-Architecture-Quick-Index.md
Anti-Patterns-Master-Index.md
Gateway-Quick-Index.md
Concurrency-Index.md
```

---

## PROJECT FILES

### Format
Project-specific conventions in `/sima/projects/[project-name]/`

### Example Project Files
```
project-index.md
project-cross-reference-matrix.md
project_config.md
README.md
```

---

## DIRECTORY NAMES

### Rules
- Lowercase preferred
- Hyphen-separated (kebab-case)
- Descriptive
- No spaces
- No special characters

### Examples
```
/generic/
/anti-patterns/
/core-architecture/
/error-handling/
/import/
/platforms/aws/lambda/
/languages/python/architectures/
/projects/myproject/
```

### Exceptions
- Project names: May use uppercase
- Platform names: Standard casing (AWS, Azure, GCP)

---

## SOURCE FILES

### Format
Follow language-specific conventions

### Python (PEP 8)
- Lowercase
- Underscore-separated (snake_case)
- Descriptive names
- Module names short

### Examples
```
gateway.py
gateway_core.py
gateway_wrappers.py
interface_cache.py
cache_core.py
lambda_function.py
```

---

## CASE CONVENTIONS

### kebab-case (Hyphen-separated)
**Use for:** Documentation, directories
```
anti-patterns/
error-handling/
LESS-15-Verification-Protocol.md
```

### snake_case (Underscore-separated)
**Use for:** Code files (Python, etc.)
```
gateway_wrappers.py
cache_core.py
```

### PascalCase
**Use for:** Rare, special files
```
README.md (exception)
LICENSE (exception)
```

### SCREAMING_SNAKE_CASE
**Use for:** Constants (in code only)
```python
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
```

---

## SPECIAL CHARACTERS

### Allowed
- Hyphen (-): Primary separator in docs
- Underscore (_): Code files, code entities
- Period (.): File extension delimiter
- Numbers (0-9): Versioning, sequencing

### Prohibited
- Spaces: Never in filenames
- Special chars: / \ * ? " < > | : #
- Unicode: Stick to ASCII for compatibility

---

## LENGTH LIMITS

**Filenames:**
- Preferred: Under 50 characters
- Maximum: 80 characters
- Include extension in count

**Directories:**
- Preferred: Under 30 characters
- Maximum: 50 characters
- Descriptive but concise

---

## CONSISTENCY RULES

### Prefixes
Use consistent prefixes within categories:
- Specs: `SPEC-`
- Lessons: `LESS-`
- Decisions: `DEC-`
- Anti-Patterns: `AP-`
- Tools: `TOOL-`

### Suffixes
Use consistent suffixes:
- Context: `-Context.md`
- Index: `-Index.md`
- Template: `-template.md`

### Numbers
- Always zero-pad to 2 digits (01 not 1)
- Sequential within type
- No reuse of numbers

---

## VALIDATION

### Checklist
- [ ] Correct prefix for type
- [ ] Proper case convention
- [ ] Number zero-padded (if applicable)
- [ ] Descriptive name
- [ ] No spaces
- [ ] No special characters
- [ ] Under length limit
- [ ] Matches header filename

### Automated Check
```python
import re

def validate_filename(filename):
    # Check no spaces
    if ' ' in filename:
        return False, "Contains spaces"
    
    # Check length
    if len(filename) > 80:
        return False, "Too long"
    
    # Check extension
    if not filename.endswith('.md'):
        return False, "Must be .md"
    
    # Check case
    if filename.isupper() and not filename.startswith(('SPEC-', 'LESS-', 'DEC-')):
        return False, "Invalid case"
    
    return True, "Valid filename"
```

---

## MIGRATION FROM OLD NAMES

If renaming files:
1. Update filename
2. Update H1 header in file
3. Update all cross-references
4. Update indexes
5. Create redirect (if needed)
6. Test all links

---

**Related:**
- SPEC-FILE-STANDARDS.md
- SPEC-HEADERS.md
- SPEC-STRUCTURE.md

**Version History:**
- v4.2.2-blank (2025-11-10): Blank slate version
- v1.0.0 (2025-11-06): Initial naming conventions

---

**END OF FILE**