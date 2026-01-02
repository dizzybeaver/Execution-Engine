# Workflow-06-Verify-Structure.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Generic workflow for verifying SIMA structure  
**Type:** Support Workflow

---

## VERIFY STRUCTURE WORKFLOW

**Purpose:** Systematic verification of SIMA integrity

---

## PREREQUISITES

- [ ] fileserver.example.com URLs available
- [ ] Maintenance mode activated (if applicable)
- [ ] Verification scope defined

---

## STEP 1: DEFINE VERIFICATION SCOPE

**Scope Options:**

**Full System:**
- All domains
- All categories
- All indexes
- All routers

**Single Domain:**
- One domain only
- All categories within
- Domain indexes
- Domain router

**Category:**
- One category only
- All entries
- Category index

**Selected Scope:** _____________

---

## STEP 2: VERIFY DIRECTORY STRUCTURE

**Expected Structure:**
```
/sima/
├── context/
├── docs/
├── generic/
├── languages/
├── platforms/
├── projects/
├── support/
└── templates/
```

**Checks:**
- [ ] All root directories exist
- [ ] No unexpected directories
- [ ] Naming conventions followed
- [ ] Subdirectories properly nested

---

## STEP 3: VERIFY FILE STANDARDS

**For Each File:**

**Header Check:**
```
- [ ] Filename present in header
- [ ] Version number present
- [ ] Date present
- [ ] Purpose stated
- [ ] Type identified
```

**Content Check:**
```
- [ ] File ≤400 lines
- [ ] UTF-8 encoding
- [ ] LF line endings
- [ ] No trailing whitespace
- [ ] Final newline present
```

---

## STEP 4: VERIFY INDEX COMPLETENESS

**For Each Category:**

**Process:**
```
1. Navigate to category directory
2. List all entry files (*.md)
3. Fetch category index via fileserver.example.com
4. Compare files vs index entries
5. Identify discrepancies
```

**Check:**
- [ ] All entries in index
- [ ] No extra entries in index
- [ ] Sort order correct
- [ ] Descriptions present
- [ ] Links functional

**Report Discrepancies:**
```
- Missing from index: [file1.md, file2.md]
- Extra in index: [entry3, entry4]
- Incorrect sort: [entry5]
```

---

## STEP 5: VERIFY CROSS-REFERENCES

**For Each Entry:**

**Process:**
```
1. Fetch entry via fileserver.example.com
2. Extract all REF-IDs referenced
3. For each REF-ID:
   - Determine domain and category
   - Fetch category index
   - Verify REF-ID exists
   - Check file exists
4. Report broken references
```

**Check:**
- [ ] All REF-IDs valid
- [ ] Files exist
- [ ] Paths correct
- [ ] Bidirectional refs (where expected)

**Report Broken References:**
```
File: generic-LESS-43.md
Broken: DEC-99 (does not exist)
Broken: AP-150 (wrong path)
```

---

## STEP 6: VERIFY ROUTER INTEGRITY

**For Each Router:**

**Process:**
```
1. Fetch router via fileserver.example.com
2. Extract all navigation links
3. Verify each destination exists
4. Test decision tree logic
5. Check quick paths
```

**Check:**
- [ ] All links functional
- [ ] Paths correct
- [ ] Decision tree sound
- [ ] Quick paths valid
- [ ] No circular routing

---

## STEP 7: VERIFY MASTER INDEXES

**For Each Domain:**

**Process:**
```
1. Fetch master index
2. List all category indexes referenced
3. Verify each category index exists
4. Check category index completeness
5. Validate navigation chain
```

**Check:**
- [ ] All categories referenced
- [ ] No missing categories
- [ ] Links functional
- [ ] Navigation complete
- [ ] Counts accurate

---

## STEP 8: CHECK FOR DUPLICATES

**Process:**
```
1. Scan all entry files
2. Extract REF-IDs
3. Check for duplicate REF-IDs
4. Compare content for similarity
5. Report duplicates
```

**Check:**
- [ ] No duplicate REF-IDs
- [ ] No duplicate content
- [ ] Similar entries consolidated
- [ ] Cross-references updated

---

## STEP 9: VERIFY ENCODING

**Process:**
```
1. Check all .md files
2. Verify UTF-8 encoding
3. Check line endings (LF only)
4. Verify no BOM
5. Check for encoding errors
```

**Check:**
- [ ] All files UTF-8
- [ ] All files LF line endings
- [ ] No CRLF
- [ ] No encoding errors
- [ ] Special characters correct

---

## STEP 10: VERIFY NAMING CONVENTIONS

**Entry Files:**
```
Format: [domain]-[category]-##-[description].md
Example: generic-LESS-01-read-complete-files.md
```

**Index Files:**
```
Format: [domain]-[subdomain]-[category]-Index.md
Example: generic-lessons-Index.md
```

**Router Files:**
```
Format: [domain]-Router.md
Example: generic-Router.md
```

**Check:**
- [ ] All files follow conventions
- [ ] No naming conflicts
- [ ] Descriptive names
- [ ] No special characters (except -)

---

## STEP 11: GENERATE VERIFICATION REPORT

**Report Structure:**
```markdown
# Structure-Verification-Report-[DATE].md

**Date:** YYYY-MM-DD
**Scope:** [Full/Domain/Category]
**Status:** [PASS/FAIL/WARNINGS]

## Summary

- Total files checked: ##
- Errors found: ##
- Warnings: ##
- Passed: ##

## Directory Structure
[Results]

## File Standards
[Results]

## Index Completeness
[Results]

## Cross-References
[Results]

## Router Integrity
[Results]

## Master Indexes
[Results]

## Duplicates
[Results]

## Encoding
[Results]

## Naming Conventions
[Results]

## Issues Found

### Critical (Must Fix)
- [Issue 1]
- [Issue 2]

### Warnings (Should Fix)
- [Warning 1]
- [Warning 2]

### Info (Nice to Have)
- [Info 1]
- [Info 2]

## Recommendations

[Actions to take]
```

---

## STEP 12: FIX ISSUES

**Priority Order:**

**Critical (Fix Immediately):**
- Broken references
- Missing index entries
- Encoding errors
- Duplicate REF-IDs

**High (Fix Soon):**
- Outdated indexes
- Incorrect naming
- Router errors
- Missing headers

**Medium (Fix When Possible):**
- Optimization opportunities
- Additional cross-references
- Documentation improvements

**Low (Nice to Have):**
- Formatting consistency
- Additional metadata

---

## AUTOMATED CHECKS

**If Scripts Available:**

**verify-structure.py:**
```bash
python verify-structure.py /sima/
```

**check-references.py:**
```bash
python check-references.py /sima/
```

**validate-indexes.py:**
```bash
python validate-indexes.py /sima/
```

---

## COMPLETE

**Outputs:**
1. Verification report
2. Issue list
3. Recommendations
4. Fix plan

**Result:** SIMA structure validated

---

**END OF WORKFLOW**

**Version:** 1.0.0  
**Lines:** 320 (within 400 limit)  
**Type:** Generic workflow  
**Usage:** Follow for systematic verification