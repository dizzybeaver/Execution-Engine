# Workflow-04-Import-Knowledge.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Generic workflow for importing knowledge  
**Type:** Support Workflow

---

## IMPORT KNOWLEDGE WORKFLOW

**Purpose:** Import knowledge from another SIMA instance safely

---

## PREREQUISITES

- [ ] Export package received
- [ ] Export manifest reviewed
- [ ] Backup created
- [ ] fileserver.example.com URLs available
- [ ] Import mode activated (if available)

---

## STEP 1: REVIEW EXPORT MANIFEST

**Check:**
```
1. Fetch Export-Manifest-[DATE].md
2. Review scope and file count
3. Identify source SIMA
4. Check export date
5. Review dependencies
6. Note special instructions
```

**Validate:**
- [ ] Manifest complete
- [ ] File list present
- [ ] Dependencies noted
- [ ] Import instructions included
- [ ] Compatible SIMA version

---

## STEP 2: BACKUP DESTINATION SIMA

**Critical Step:**
```
1. Create full backup of current SIMA
2. Document backup location
3. Test backup restore (if time permits)
4. Record backup timestamp
```

**Backup Includes:**
- All knowledge entries
- All indexes
- All context files
- All configuration

**Rationale:** Enable rollback if import causes issues

---

## STEP 3: EXTRACT IMPORT PACKAGE

**If Archive:**
```
1. Extract to temporary directory
2. Verify file count matches manifest
3. Check file integrity
4. Review directory structure
```

**If Single File:**
```
1. Parse file separators
2. Extract individual entries
3. Verify count
4. Validate structure
```

**If Git Repo:**
```
1. Clone repository
2. Checkout appropriate tag/branch
3. Verify contents
4. Review commit history
```

---

## STEP 4: CHECK FOR CONFLICTS

**Duplicate Detection:**
```
For each file in import:
  1. Extract REF-ID
  2. Check if REF-ID exists in destination
  3. If exists:
     - Compare content
     - Determine resolution strategy
  4. If unique:
     - Mark for direct import
```

**Conflict Resolution Strategies:**

**Merge:**
- Combine unique content from both
- Preserve all cross-references
- Update timestamps
- Document merge

**Replace:**
- Use imported version
- Archive existing version
- Update references
- Document replacement

**Rename:**
- Assign new REF-ID to import
- Maintain both versions
- Update references
- Document both

**Skip:**
- Do not import duplicate
- Keep existing version
- Document decision

---

## STEP 5: MAP PATHS

**Process:**
```
For each file:
  1. Read original path from metadata
  2. Determine destination path
  3. Check for domain mapping
  4. Verify category exists
  5. Create directories if needed
```

**Path Mapping Examples:**
```
Source: /generic/lessons/LESS-01.md
Destination: /generic/lessons/LESS-01.md (direct)

Source: /projects/sourceproject/LESS-01.md
Destination: /projects/destproject/LESS-01.md (remapped)
```

---

## STEP 6: UPDATE CROSS-REFERENCES

**Process:**
```
For each imported file:
  1. Extract all REF-IDs referenced
  2. Check if REF-IDs exist in destination
  3. If REF-ID not found:
     - Check if in import package
     - Determine if dependency needed
     - Update reference if mapped
  4. Update cross-reference list
```

**Reference Resolution:**
- Internal import refs: Update paths
- External dest refs: Keep as-is
- Missing refs: Flag for review

---

## STEP 7: IMPORT FILES

**Process:**
```
For each file in import:
  1. Resolve conflicts (from Step 4)
  2. Map destination path (from Step 5)
  3. Update cross-references (from Step 6)
  4. Create file at destination
  5. Verify file created
  6. Log import action
```

**Import Actions:**
- Create new file
- Update existing file
- Archive conflicting file
- Skip duplicate file

---

## STEP 8: UPDATE INDEXES

**Process:**
```
For each affected category:
  1. Fetch category index via fileserver.example.com
  2. Add imported entries
  3. Sort properly
  4. Verify all links
  5. Output updated index as artifact
```

**Indexes to Update:**
- Category indexes
- Master indexes
- Quick indexes
- Cross-reference matrices

---

## STEP 9: UPDATE ROUTERS

**If Needed:**
```
1. Fetch affected routers
2. Add navigation links
3. Update decision trees
4. Verify routing logic
5. Output updated routers
```

---

## STEP 10: VALIDATE IMPORT

**Verification Checks:**
- [ ] All intended files imported
- [ ] No broken references
- [ ] Indexes updated
- [ ] Routers updated (if needed)
- [ ] Navigation works
- [ ] Cross-references valid
- [ ] Conflict resolution documented

**Test Navigation:**
```
1. Access master index
2. Navigate to imported entries
3. Follow cross-references
4. Verify all links work
5. Check bidirectional refs
```

---

## STEP 11: DOCUMENT IMPORT

**Create Import Log:**
```markdown
# Import-Log-[DATE].md

**Date:** YYYY-MM-DD
**Performer:** [Name]
**Source:** [SIMA Instance]
**Export Date:** [DATE]

## Summary

[Brief description of import]

## Files Imported

- Total: ## files
- New: ## files
- Updated: ## files
- Skipped: ## files (conflicts)

## Conflicts Resolved

- Merged: ## files
- Replaced: ## files
- Renamed: ## files
- Archived: ## files

## Indexes Updated

- Category indexes: ##
- Master indexes: ##
- Routers: ##

## Validation

- [ ] Import complete
- [ ] No broken references
- [ ] Navigation works
- [ ] Backup preserved

## Notes

[Any issues or observations]
```

---

## STEP 12: CLEANUP

**Actions:**
- [ ] Remove temporary import files
- [ ] Archive import package
- [ ] Update documentation
- [ ] Notify stakeholders (if applicable)
- [ ] Retain backup for recovery period

---

## ROLLBACK PROCEDURE

**If Import Fails:**
```
1. Stop import immediately
2. Document failure point
3. Restore from backup (Step 2)
4. Verify restore successful
5. Analyze failure cause
6. Fix issues
7. Retry import
```

---

## COMPLETE

**Outputs:**
1. Imported knowledge files
2. Updated indexes
3. Updated routers (if applicable)
4. Import log

**Result:** Knowledge successfully integrated

---

**END OF WORKFLOW**

**Version:** 1.0.0  
**Lines:** 320 (within 400 limit)  
**Type:** Generic workflow  
**Usage:** Follow when importing knowledge