# TOOL-01-REF-ID-Directory.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** REF-ID directory structure  
**Type:** Support Tool

---

## REF-ID DIRECTORY

**Purpose:** Central directory of all REF-IDs in SIMA

**Usage:** Find and verify REF-ID references

---

## STRUCTURE

### By Type

**LESS (Lessons)**
```
/generic/lessons/
/platforms/[platform]/lessons/
/languages/[language]/lessons/
/projects/[project]/lessons/
```

**DEC (Decisions)**
```
/generic/decisions/
/platforms/[platform]/decisions/
/languages/[language]/decisions/
/projects/[project]/decisions/
```

**AP (Anti-Patterns)**
```
/generic/anti-patterns/
/platforms/[platform]/anti-patterns/
/languages/[language]/anti-patterns/
/projects/[project]/anti-patterns/
```

**BUG (Bugs)**
```
/generic/lessons/bugs/
/platforms/[platform]/lessons/bugs/
/languages/[language]/lessons/bugs/
/projects/[project]/lessons/bugs/
```

**WISD (Wisdom)**
```
/generic/lessons/wisdom/
/platforms/[platform]/lessons/wisdom/
/languages/[language]/lessons/wisdom/
/projects/[project]/lessons/wisdom/
```

**SPEC (Specifications)**
```
/generic/specifications/
```

---

## USAGE

### Finding REF-IDs

**Step 1:** Identify type (LESS, DEC, AP, etc.)

**Step 2:** Determine domain (generic, platform, language, project)

**Step 3:** Navigate to appropriate directory

**Step 4:** Check category index

**Step 5:** Locate specific entry

### Verifying REF-IDs

**Check:**
1. REF-ID exists in category index
2. File exists at path
3. REF-ID matches filename
4. Cross-references valid

---

## GENERIC REF-IDs

### Lessons (LESS-##)
**Location:** `/generic/lessons/`  
**Index:** `generic-lessons-Index.md`

### Decisions (DEC-##)
**Location:** `/generic/decisions/`  
**Index:** `generic-decisions-Index.md`

### Anti-Patterns (AP-##)
**Location:** `/generic/anti-patterns/`  
**Index:** `generic-anti-patterns-Index.md`

### Specifications (SPEC-##)
**Location:** `/generic/specifications/`  
**Index:** `generic-specifications-Index.md`

---

## PLATFORM REF-IDs

**Structure:**
```
/platforms/[platform]/[category]/[platform]-[category]-##.md
```

**Example:**
```
/platforms/aws/lessons/aws-LESS-01.md
```

---

## LANGUAGE REF-IDs

**Structure:**
```
/languages/[language]/[category]/[language]-[category]-##.md
```

**Example:**
```
/languages/python/lessons/python-LESS-01.md
```

---

## PROJECT REF-IDs

**Structure:**
```
/projects/[project]/[category]/[project]-[category]-##.md
```

**Example:**
```
/projects/myproject/lessons/myproject-LESS-01.md
```

---

## CROSS-REFERENCE VALIDATION

### Check Process

**Step 1:** Extract all REF-IDs from file

**Step 2:** For each REF-ID:
- Determine type and domain
- Navigate to category index
- Verify entry exists
- Check file exists
- Validate path

**Step 3:** Report broken references

**Step 4:** Update if needed

---

## MAINTENANCE

### Adding New REF-IDs

1. Create entry file
2. Assign next sequential number
3. Update category index
4. Add cross-references
5. Verify in directory

### Removing REF-IDs

1. Mark as deprecated
2. Update cross-references
3. Add redirect (if applicable)
4. Archive original
5. Update indexes

---

## TOOLS

### Automated Tools

**generate-ref-id-list.py** (if available)
- Scans all directories
- Extracts REF-IDs
- Generates directory
- Validates references

**verify-ref-ids.py** (if available)
- Checks all references
- Reports broken links
- Suggests fixes

---

**END OF TOOL**

**Version:** 1.0.0  
**Lines:** 200 (within 400 limit)  
**Type:** REF-ID directory structure  
**Usage:** Reference and validation tool