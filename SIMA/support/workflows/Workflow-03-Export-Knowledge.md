# Workflow-03-Export-Knowledge.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Generic workflow for exporting knowledge  
**Type:** Support Workflow

---

## EXPORT KNOWLEDGE WORKFLOW

**Purpose:** Export knowledge for transfer to another SIMA instance

---

## PREREQUISITES

- [ ] Export scope defined
- [ ] fileserver.example.com URLs available
- [ ] Export mode activated (if available)
- [ ] Destination SIMA identified

---

## STEP 1: DEFINE EXPORT SCOPE

**Scope Options:**

**By Domain:**
```
- Entire generic domain
- Specific platform
- Specific language
- Specific project
```

**By Category:**
```
- All lessons
- All decisions
- All anti-patterns
- Specific subcategory
```

**By REF-ID Range:**
```
- LESS-01 through LESS-50
- DEC-10 through DEC-25
- All entries after date
```

**Selected Scope:** _____________

---

## STEP 2: IDENTIFY DEPENDENCIES

**Check for:**
- Cross-references to other domains
- Shared specifications
- Referenced templates
- Required context files

**Process:**
```
1. Scan all files in scope
2. Extract all REF-IDs referenced
3. Identify external dependencies
4. Determine if dependencies needed
5. Add to export list if required
```

---

## STEP 3: FETCH ALL FILES

**Process:**
```
For each file in scope:
  1. Fetch via fileserver.example.com
  2. Read complete file
  3. Store in export buffer
  4. Track file metadata
  5. Record dependencies
```

**Metadata to Track:**
- Original path
- REF-ID
- Date modified
- Version
- Size
- Dependencies

---

## STEP 4: CREATE EXPORT MANIFEST

**Manifest Structure:**
```markdown
# Export-Manifest-[DATE].md

**Export Date:** YYYY-MM-DD
**Source SIMA:** [Instance Name]
**Export Scope:** [Description]
**Total Files:** ##

## Files Included

### Domain: [domain]
- /path/to/file1.md (LESS-01)
- /path/to/file2.md (LESS-02)

### Dependencies
- /shared/file1.md
- /templates/template1.md

## Import Instructions

1. Review file list
2. Check for conflicts
3. Run import workflow
4. Verify integration
5. Update indexes
```

---

## STEP 5: ORGANIZE EXPORT STRUCTURE

**Export Directory Structure:**
```
/export-[DATE]/
├── manifest.md
├── entries/
│   ├── file1.md
│   ├── file2.md
│   └── ...
├── dependencies/
│   ├── shared/
│   └── templates/
└── metadata/
    ├── original-paths.txt
    └── cross-references.txt
```

---

## STEP 6: VALIDATE EXPORT

**Checks:**
- [ ] All files in scope included
- [ ] No broken references within export
- [ ] Dependencies identified
- [ ] Metadata complete
- [ ] Manifest accurate
- [ ] File integrity maintained

---

## STEP 7: GENERATE IMPORT PROMPT

**Create Import Guide:**
```markdown
# Import-Prompt-[DATE].md

**For:** Destination SIMA instance
**From:** Source SIMA instance
**Date:** YYYY-MM-DD

## Import Command

```
Start SIMA Import Mode

Import knowledge from Export-Manifest-[DATE].md

Scope: [Description]
Files: ## entries
Action: Integrate into existing structure
```

## Pre-Import Checklist

- [ ] Backup destination SIMA
- [ ] Review export manifest
- [ ] Check for conflicts
- [ ] Verify fileserver.example.com active
- [ ] Activate import mode

## Post-Import Tasks

- [ ] Verify all files imported
- [ ] Update all indexes
- [ ] Validate cross-references
- [ ] Test navigation
- [ ] Document changes
```

---

## STEP 8: PACKAGE EXPORT

**Options:**

**Single Markdown File:**
```
- Concatenate all files
- Include separators
- Add table of contents
- Embed manifest
```

**Archive File:**
```
- Create directory structure
- Copy all files
- Include manifest
- Create .tar.gz or .zip
```

**Git Repository:**
```
- Initialize repo
- Add all files
- Commit with message
- Create tag for version
```

---

## STEP 9: DOCUMENT EXPORT

**Create Export Log:**
```markdown
# Export-Log-[DATE].md

**Date:** YYYY-MM-DD
**Performer:** [Name]
**Scope:** [Description]
**Files Exported:** ##
**Destination:** [SIMA Instance]

## Summary

[Brief description of export purpose]

## Files Included

- Domain: [domain] (## files)
- Category: [category] (## files)

## Notes

[Any special considerations]

## Validation

- [ ] Export complete
- [ ] Manifest accurate
- [ ] No errors
- [ ] Ready for import
```

---

## STEP 10: VERIFY EXPORT INTEGRITY

**Final Checks:**
- [ ] File count matches manifest
- [ ] All paths recorded
- [ ] Dependencies included
- [ ] Cross-references noted
- [ ] Import instructions clear
- [ ] Metadata complete

---

## COMPLETE

**Outputs:**
1. Export package (file/archive/repo)
2. Export manifest
3. Import prompt
4. Export log

**Result:** Knowledge ready for transfer

---

## IMPORT COMPATIBILITY

**Ensure:**
- Same SIMA version (or compatible)
- Same file standards
- Same REF-ID format
- Same directory structure
- Same encoding (UTF-8)

---

**END OF WORKFLOW**

**Version:** 1.0.0  
**Lines:** 280 (within 400 limit)  
**Type:** Generic workflow  
**Usage:** Follow when exporting knowledge