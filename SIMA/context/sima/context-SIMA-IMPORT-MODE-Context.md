# context-SIMA-IMPORT-MODE-Context.md

**Version:** 4.2.2-enhanced  
**Date:** 2025-11-12  
**Purpose:** Import knowledge from other SIMA instances (ENHANCED)  
**Activation:** "Start SIMA Import Mode"  
**Load time:** 20-30 seconds  
**Type:** SIMA Mode

---

## EXTENDS

[context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md) (Base context)

---

## WHAT THIS MODE IS

**Import Mode** integrates knowledge from exports into current SIMA instance.

**Purpose:** Merge external knowledge while checking for duplicates, version compatibility, and conflicts.

**Outputs:** Integrated knowledge, updated indexes, conflict reports, verification logs.

---

## IMPORT PROCESS (ENHANCED)

### Phase 1: Load and Validate

**User provides:**
1. manifest.yaml (uploaded)
2. import-instructions.md (uploaded)
3. Package files (extracted manually or referenced)

**AI parses:**
```
1. Read manifest.yaml structure:
   - Archive metadata (name, version, created)
   - File inventory (paths, checksums, REF-IDs)
   - Package list (base + increments)
   - SIMA version tags per file

2. Read import-instructions.md:
   - Selected files (install: true)
   - Unselected files (install: false)
   - Target paths for each file
   - Change history

3. Extract key data:
   - Total files available
   - Files selected for install
   - Expected packages
   - Source SIMA version
```

---

### Phase 2: Version Compatibility Check (NEW)

**For each selected file:**

```
1. Extract file's SIMA version from manifest
   Example: file.sima_version = "4.2.0"

2. Compare to current SIMA version (4.2.2)

3. Apply compatibility rules:

   IF file_version == current_version:
      → COMPATIBLE (no changes needed)
      
   ELSE IF file_version is patch difference (4.2.0 → 4.2.2):
      → COMPATIBLE (patch versions backward compatible)
      → No modifications needed
      
   ELSE IF file_version is minor difference (4.1.x → 4.2.x):
      → CHECK MATRIX (may need header updates)
      → Flag for review
      → Check breaking changes list
      
   ELSE IF file_version is major difference (3.x → 4.x):
      → INCOMPATIBLE (manual migration required)
      → Warn user
      → Do not proceed without user confirmation
      
   ELSE IF file_version > current_version:
      → VERSION TOO NEW
      → Warn user
      → May have features not supported
```

**Compatibility Matrix Reference:**
See `/sima/docs/VERSION-COMPATIBILITY-MATRIX.md`

**Report to user:**
```
Version Compatibility Check:
✅ Compatible: 45 files (same version or patch)
⚠️  Needs Review: 3 files (minor version difference)
❌ Incompatible: 0 files
⚠️  Too New: 0 files

Files needing review:
- AWS-Lambda-LESS-01.md (v4.1.0 → v4.2.2)
  Issue: Header format changed in v4.2.0
  Action: Will auto-upgrade header during import
  
- Python-LMMS-Core.md (v4.1.5 → v4.2.2)
  Issue: REF-ID format changed in v4.2.0
  Action: Manual review recommended
```

---

### Phase 3: Duplicate Detection (ENHANCED)

**For each selected file:**

```
1. Extract target path from import-instructions
   Example: /sima/platforms/aws/lambda/lessons/AWS-Lambda-LESS-01.md

2. Check if file exists (via fileserver.php)
   → Use cache-busted URL for fresh content

3. IF file exists:
   
   a. Fetch current file content
   
   b. Calculate current file checksum (MD5)
   
   c. Compare checksums:
   
      IF checksums match:
         → SKIP (files identical)
         → No action needed
         → Log: "Skipped (identical)"
         
      ELSE IF checksums differ:
         → CONFLICT detected
         → Present conflict resolution options:
         
         [1] Keep existing (skip import)
             - Preserve current version
             - No changes to system
             
         [2] Replace with import
             - Overwrite with archive version
             - Update all references
             
         [3] Keep both (rename import)
             - Rename import: LESS-01-import.md
             - Preserve both versions
             - Update import's cross-references
             
         [4] View diff
             - Show side-by-side comparison
             - Highlight changes
             - Then choose option 1-3
             
4. ELSE (file doesn't exist):
   → NEW file (safe to import)
   → No conflicts
   → Log: "New file"
```

**Conflict Resolution Dialog:**
```
⚠️  CONFLICT DETECTED

File: AWS-Lambda-LESS-01.md
Location: /sima/platforms/aws/lambda/lessons/

Existing Version:
- Checksum: a1b2c3d4e5f6
- Size: 198 lines
- Last Modified: 2025-11-01
- SIMA Version: 4.2.2

Import Version:
- Checksum: f6e5d4c3b2a1
- Size: 215 lines  
- Exported: 2025-11-10
- SIMA Version: 4.2.0

Options:
[1] Keep existing (recommended if you made local changes)
[2] Replace with import (recommended if archive is authoritative)
[3] Keep both (useful for comparison)
[4] View diff (see what changed)

Please select option (1/2/3/4): _
```

---

### Phase 4: Dependency Check (ENHANCED)

**For each selected file:**

```
1. Fetch file content (via fileserver.php)

2. Parse cross-references:
   - Lines containing "**REF:**"
   - Lines containing "**Related:**"
   - Lines containing "**See also:**"
   
3. Extract REF-IDs:
   Example: **REF:** LESS-01, AP-05, DEC-12
   → Extract: [LESS-01, AP-05, DEC-12]

4. For each referenced REF-ID:

   a. Check if REF-ID is in import package:
      
      IF referenced file in manifest:
         IF referenced file is selected:
            → ✅ OK (will be imported together)
         ELSE:
            → ⚠️  WARN (dependency not selected)
            → Suggest: "Add AWS-Lambda-LESS-05.md to selection?"
            
   b. ELSE check if REF-ID exists in target SIMA:
      
      Search target directories (via fileserver.php)
      
      IF file found:
         → ✅ OK (dependency already exists)
      ELSE:
         → ❌ ERROR (missing dependency)
         → Block import OR require user confirmation

5. Generate dependency report:

   Dependencies Satisfied: 42/45 references
   
   Missing Dependencies (3):
   - LESS-05 (referenced by LESS-01, LESS-08)
     Action: Include in import OR already exists
     
   - AP-12 (referenced by LESS-03)
     Status: Not in archive, not in target
     Resolution: Import will have broken reference
     
   - DEC-08 (referenced by AP-05)
     Status: Already exists in target ✅
```

---

### Phase 5: Index Update Planning (NEW)

**Identify affected indexes:**

```
1. Build list of target directories from selected files
   Example: /sima/platforms/aws/lambda/lessons/

2. For each directory:
   
   a. Check for index file:
      - [Category]-Index.md
      - [Domain]-Index.md
      - Master indexes
      
   b. IF index exists:
      → Mark for update
      → Add to update queue
      
   c. ELSE:
      → Flag missing index
      → Offer to create

3. Fetch current indexes (via fileserver.php)

4. For each index:
   
   a. Parse current entries
   
   b. Identify new entries to add:
      - From imported files
      - Extract title, REF-ID, description
      
   c. Determine insertion points:
      - Alphabetical order
      - Numerical order (for REF-IDs)
      - Category grouping
      
   d. Generate updated index:
      - Complete file (not fragment)
      - All existing entries + new entries
      - Properly formatted
      - Sorted correctly
      
   e. Create as artifact:
      - Mark additions with # ADDED: comments
      - Complete file ready to deploy
      - Filename in header

5. Present index updates to user:

   Index Updates Required (5 files):
   
   ✅ platforms/aws/lambda/lessons/Lessons-Index.md
      - Adding 8 new entries
      - Artifact 1 ready
      
   ✅ platforms/aws/AWS-Index.md
      - Adding 8 new entries
      - Artifact 2 ready
      
   ✅ platforms/platforms-Master-Index.md
      - Updating file counts
      - Artifact 3 ready
      
   ✅ Master-Index-of-Indexes.md
      - Updating totals
      - Artifact 4 ready
      
   ⚠️  platforms/aws/dynamodb/DynamoDB-Index.md
      - Missing - create? (y/n)
```

---

### Phase 6: Installation Instructions (ENHANCED)

**Generate complete installation guide:**

```markdown
# Import Installation Guide

**Archive:** AWS-Platform-Knowledge
**Selected Files:** 45
**Status:** Ready to install

## Pre-Installation Checklist

✅ Version compatible (45 files)
✅ Conflicts resolved (3 kept existing, 0 replaced, 0 both)
✅ Dependencies satisfied (42/45, 3 warnings acknowledged)
✅ Index updates prepared (5 artifacts)

## Installation Steps

### Step 1: Extract Packages

Extract these packages to temporary location:

```bash
mkdir -p /tmp/sima-import
cd /tmp/sima-import

# Extract base package
unzip knowledge-base.zip

# Extract increments (if any)
unzip knowledge-increment-01.zip
unzip knowledge-increment-02.zip
```

**Note:** Increments will overwrite base files (this is expected for modified files).

### Step 2: Copy Selected Files

Copy only selected files to target locations:

```bash
# AWS Lambda Core (5 files)
cp -v platforms/aws/lambda/core/AWS-Lambda-Core-Concepts.md \
   /home/joe/sima/platforms/aws/lambda/core/

cp -v platforms/aws/lambda/core/AWS-Lambda-Execution-Model.md \
   /home/joe/sima/platforms/aws/lambda/core/

... (all 45 files listed)
```

**Skip these files (conflicts resolved):**
- AWS-Lambda-LESS-01.md (kept existing)
- AWS-Lambda-LESS-03.md (kept existing)
- AWS-Lambda-AP-02.md (kept existing)

### Step 3: Deploy Index Updates

Save and deploy these 5 index update artifacts:

```bash
# Artifact 1 → /home/joe/sima/platforms/aws/lambda/lessons/Lessons-Index.md
# Artifact 2 → /home/joe/sima/platforms/aws/AWS-Index.md
# Artifact 3 → /home/joe/sima/platforms/platforms-Master-Index.md
# Artifact 4 → /home/joe/sima/Master-Index-of-Indexes.md
# Artifact 5 → /home/joe/sima/platforms/aws/dynamodb/DynamoDB-Index.md
```

### Step 4: Verify Installation

Run these verification checks:

**A. Checksum Verification**

Verify imported files match expected checksums:

```bash
# Check a sample of files
md5sum /home/joe/sima/platforms/aws/lambda/core/AWS-Lambda-Core-Concepts.md
# Expected: a1b2c3d4e5f6

md5sum /home/joe/sima/platforms/aws/lambda/lessons/AWS-Lambda-LESS-17.md
# Expected: 1a2b3c4d5e6f
```

**B. REF-ID Validation**

Verify all cross-references resolve:

```bash
# Test a few REF-IDs
grep -r "LESS-01" /home/joe/sima/generic/lessons/
# Should find: LESS-01.md

grep -r "AWS-Lambda-Core" /home/joe/sima/platforms/aws/
# Should find: AWS-Lambda-Core-Concepts.md
```

**C. Index Navigation**

Test navigation through indexes:

```
1. Open: /home/joe/sima/Master-Index-of-Indexes.md
2. Follow: platforms → aws → lambda → lessons
3. Verify: All 8 new lessons listed
4. Check: REF-IDs link correctly
```

### Step 5: Post-Import Cleanup

```bash
# Remove temporary files
rm -rf /tmp/sima-import

# Optional: backup original files
tar -czf ~/sima-backup-2025-11-12.tar.gz /home/joe/sima
```

## Import Complete! ✅

**Imported:** 45 files
**Indexes Updated:** 5 files
**Conflicts:** 3 (resolved)
**Dependencies:** 42/45 satisfied

**Next Steps:**
- Test navigation through new knowledge
- Verify cross-references work
- Update any project-specific configs if needed
```

---

### Phase 7: Post-Import Verification

**Provide automated verification commands:**

```bash
#!/bin/bash
# SIMA Import Verification Script

echo "=== SIMA Import Verification ==="
echo ""

# 1. Checksum Verification
echo "1. Verifying checksums..."
md5sum /home/joe/sima/platforms/aws/lambda/core/*.md > /tmp/checksums.txt

# Compare with manifest (user provides expected checksums)
ERRORS=0

# Check sample files
if [ "$(md5sum /home/joe/sima/platforms/aws/lambda/core/AWS-Lambda-Core-Concepts.md | cut -d' ' -f1)" != "a1b2c3d4e5f6" ]; then
    echo "   ❌ Checksum mismatch: AWS-Lambda-Core-Concepts.md"
    ERRORS=$((ERRORS + 1))
else
    echo "   ✅ AWS-Lambda-Core-Concepts.md"
fi

# 2. REF-ID Validation
echo ""
echo "2. Validating REF-IDs..."

# Check if key REF-IDs resolve
if grep -q "LESS-01" /home/joe/sima/generic/lessons/LESS-01.md 2>/dev/null; then
    echo "   ✅ LESS-01 resolves"
else
    echo "   ❌ LESS-01 missing"
    ERRORS=$((ERRORS + 1))
fi

# 3. Index Completeness
echo ""
echo "3. Checking indexes..."

# Count entries in updated indexes
AWS_COUNT=$(grep -c "^- \[" /home/joe/sima/platforms/aws/AWS-Index.md)
echo "   AWS Index entries: $AWS_COUNT"

# 4. File Count
echo ""
echo "4. Verifying file counts..."
IMPORTED_COUNT=$(find /home/joe/sima/platforms/aws/lambda -name "*.md" -not -name "*Index*" | wc -l)
echo "   Files in aws/lambda: $IMPORTED_COUNT"

# Summary
echo ""
echo "=== Verification Summary ==="
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed!"
else
    echo "❌ $ERRORS errors found"
    echo "Review errors above and fix as needed"
fi
```

---

## ARTIFACT RULES

**Import outputs:**

```
[OK] Integrated files - Complete entries with version tags
[OK] Updated indexes - All affected indexes as complete files
[OK] Import report - Detailed log of all actions
[OK] Conflict resolutions - Documented decisions
[OK] Verification script - Automated checks
[X] Never partial imports
[X] Never unresolved conflicts
[X] Never missing dependencies (without warning)
```

**Complete Standards:** `/sima/context/shared/Artifact-Standards.md`

---

## QUALITY CHECKLIST

**Before import:**
1. ✅ manifest.yaml parsed correctly
2. ✅ import-instructions.md loaded
3. ✅ Version compatibility verified
4. ✅ All selected files validated
5. ✅ Duplicates scanned (via fileserver.php)

**During import:**
6. ✅ All conflicts resolved (user decisions recorded)
7. ✅ REF-IDs mapped correctly
8. ✅ Files placed in correct locations
9. ✅ References updated if needed
10. ✅ No broken links

**After import:**
11. ✅ All indexes updated (as artifacts)
12. ✅ Cross-references validated
13. ✅ Import report generated
14. ✅ Verification commands provided
15. ✅ System fully functional

---

## VERSION COMPATIBILITY MATRIX

**Quick Reference:**

| From Version | To Version | Status | Action |
|--------------|------------|--------|--------|
| 4.2.0 | 4.2.2 | ✅ Compatible | None |
| 4.2.1 | 4.2.2 | ✅ Compatible | None |
| 4.1.x | 4.2.x | ⚠️  Review | Check headers |
| 4.0.x | 4.2.x | ⚠️  Review | Check REF-IDs |
| 3.x | 4.2.x | ❌ Incompatible | Manual migration |
| Future | 4.2.2 | ⚠️  Too New | Check features |

**Complete Matrix:** `/sima/docs/VERSION-COMPATIBILITY-MATRIX.md`

---

## SUCCESS METRICS

**Successful import when:**
- ✅ All selected files integrated
- ✅ Zero unresolved conflicts
- ✅ All indexes updated (as artifacts)
- ✅ All REF-IDs validated
- ✅ Complete audit trail
- ✅ System passes verification
- ✅ All artifacts complete (no chat code)

---

## READY

**Context loaded when you remember:**
- ✅ fileserver.php fetched (automatic)
- ✅ 7-phase import process (enhanced)
- ✅ Version compatibility checking (NEW)
- ✅ Enhanced duplicate detection (checksums)
- ✅ Dependency validation (cross-refs)
- ✅ Automatic index generation (NEW)
- ✅ Complete verification script (NEW)
- ✅ All outputs as artifacts

**Now ready to import knowledge with full validation!**

---

**END OF ENHANCED IMPORT MODE CONTEXT**

**Version:** 4.2.2-enhanced  
**Lines:** 400 (target achieved)  
**Enhancements:**
- Version compatibility checking
- Enhanced duplicate detection
- Automatic index generation
- Dependency validation
- Complete verification workflow
