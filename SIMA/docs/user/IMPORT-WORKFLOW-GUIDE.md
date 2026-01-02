# IMPORT-WORKFLOW-GUIDE.md

**Version:** 1.0.0  
**Date:** 2025-11-12  
**Purpose:** Step-by-step guide for importing knowledge archives  
**Location:** `/sima/docs/`

---

## OVERVIEW

This guide walks through the complete process of importing a SIMA knowledge archive, from preparation to verification.

**Prerequisites:**
- SIMA v4.2.2 installed
- Import Mode context loaded
- Archive files available
- File Server URLs loaded

---

## QUICK START

**Minimum Steps:**

1. Activate: `"Start SIMA Import Mode"`
2. Upload: manifest.yaml
3. Upload: import-instructions.md
4. Review conflicts
5. Deploy files
6. Update indexes
7. Verify

**Estimated Time:** 15-30 minutes (depending on archive size)

---

## STEP-BY-STEP WORKFLOW

### STEP 1: Prepare Archive

**What you need:**
- manifest.yaml
- import-instructions.md
- knowledge-base.zip
- knowledge-increment-##.zip (if any)

**Where to get them:**
- From export tool output
- From another SIMA user
- From shared repository

**Action:**
```bash
# Create workspace
mkdir -p ~/sima-import-workspace
cd ~/sima-import-workspace

# Copy archive files here
cp /path/to/SIMA-Archive-*.zip .

# Extract archive
unzip SIMA-Archive-*.zip

# Verify contents
ls -la
# Should see:
# - manifest.yaml
# - import-instructions.md
# - knowledge-base.zip
# - knowledge-increment-*.zip (optional)
```

---

### STEP 2: Activate Import Mode

**Command:**
```
"Start SIMA Import Mode"
```

**What happens:**
- Context loads (20-30 seconds)
- fileserver.php fetched automatically
- Import mode activated
- AI ready to process archives

**Expected response:**
```
SIMA Import Mode Activated

Context loaded. Please provide:
1. manifest.yaml (upload or paste)
2. import-instructions.md (upload or paste)

Once both provided, I will begin validation.
```

---

### STEP 3: Upload Manifest

**Action:**
Upload manifest.yaml to Claude

**What AI does:**
```
1. Parse YAML structure
2. Extract metadata:
   - Archive name
   - Version
   - Total files
   - File inventory
3. Build file list with checksums
4. Identify package structure
5. Note SIMA version per file
```

**Expected response:**
```
✅ Manifest Loaded

Archive: AWS-Platform-Knowledge
Version: 2
Created: 2025-11-12
Files: 67 total
Packages: Base + 2 increments
SIMA Version: 4.2.2

Ready for import-instructions.md
```

---

### STEP 4: Upload Import Instructions

**Action:**
Upload import-instructions.md to Claude

**What AI does:**
```
1. Parse markdown structure
2. Extract selected files
3. Extract unselected files
4. Map target paths
5. Identify categories
6. Review changelog
```

**Expected response:**
```
✅ Import Instructions Loaded

Selected for Install: 45 files
Not Selected: 22 files
Target: /sima directory structure

Beginning validation...
```

---

### STEP 5: Version Compatibility Check

**Automatic - AI performs:**

```
FOR EACH selected file:
  1. Check file SIMA version
  2. Compare to current (4.2.2)
  3. Apply compatibility rules
  4. Flag issues
```

**Possible outcomes:**

**Scenario A: All Compatible**
```
✅ Version Compatibility Check Complete

All files compatible:
- 45 files same version (4.2.2)
- 0 files need review
- 0 files incompatible

Proceeding to duplicate detection...
```

**Scenario B: Some Need Review**
```
⚠️  Version Compatibility Check Complete

Compatible: 42 files
Needs Review: 3 files

Files needing review:
1. AWS-Lambda-LESS-01.md (v4.1.5 → v4.2.2)
   Issue: Header format changed in v4.2.0
   Auto-fix: Add missing header fields
   
2. Python-Core-Concepts.md (v4.1.0 → v4.2.2)
   Issue: REF-ID format changed
   Action: Manual review recommended
   
3. DynamoDB-Index.md (v4.0.5 → v4.2.2)
   Issue: Multiple version gap
   Action: Manual verification required

Would you like to:
[1] Auto-fix issues 1-3 and proceed
[2] Manual review before proceeding
[3] Exclude problematic files
[4] Cancel import

Your choice: _
```

**Scenario C: Incompatible**
```
❌ Version Compatibility Check Failed

Incompatible: 5 files from v3.x

Cannot import v3.x files into v4.2.2 without migration.

Options:
[1] Exclude these 5 files and proceed with 40 compatible
[2] Use SIMA v3 → v4 Migration Tool first
[3] Cancel import

Your choice: _
```

---

### STEP 6: Duplicate Detection

**Automatic - AI performs:**

```
FOR EACH selected file:
  1. Fetch current file (via fileserver.php)
  2. Calculate checksum
  3. Compare with import checksum
  4. Identify conflicts
```

**Possible outcomes:**

**Scenario A: No Conflicts**
```
✅ Duplicate Detection Complete

45 files checked:
- 38 new files (no conflicts)
- 7 existing files (identical - will skip)
- 0 conflicts

Proceeding to dependency check...
```

**Scenario B: Conflicts Found**
```
⚠️  Duplicate Detection Complete

45 files checked:
- 35 new files
- 7 identical (will skip)
- 3 conflicts

CONFLICT 1 of 3:
File: AWS-Lambda-LESS-01.md
Location: /sima/platforms/aws/lambda/lessons/

Existing Version:
- Checksum: a1b2c3d4e5f6
- Size: 198 lines
- Modified: 2025-11-01
- Content preview:
  # AWS-Lambda-LESS-01.md
  **Version:** 1.0.0
  **Date:** 2025-11-01
  **Purpose:** Cold start optimization

Import Version:
- Checksum: f6e5d4c3b2a1
- Size: 215 lines
- Exported: 2025-11-10
- Content preview:
  # AWS-Lambda-LESS-01.md
  **Version:** 1.1.0
  **Date:** 2025-11-10
  **Purpose:** Cold start optimization (ENHANCED)

Resolution options:
[1] Keep existing (recommended if you made local changes)
[2] Replace with import (recommended if archive is authoritative)
[3] Keep both (rename import → LESS-01-import.md)
[4] View full diff

Your choice for CONFLICT 1: _
```

**AI waits for user decision on each conflict.**

---

### STEP 7: Resolve Conflicts

**For each conflict, user chooses:**

**Option 1: Keep Existing**
```
User: 1

✅ Decision recorded: Keep existing

File will be SKIPPED during import.
Local version preserved.

Moving to CONFLICT 2...
```

**Option 2: Replace**
```
User: 2

✅ Decision recorded: Replace with import

File will be OVERWRITTEN during import.
Archive version will replace local.

Moving to CONFLICT 2...
```

**Option 3: Keep Both**
```
User: 3

✅ Decision recorded: Keep both

Import renamed to: AWS-Lambda-LESS-01-import.md
Both versions will exist.
You can merge manually later.

Moving to CONFLICT 2...
```

**Option 4: View Diff**
```
User: 4

=== DIFF VIEW ===

AWS-Lambda-LESS-01.md

--- Existing (2025-11-01)
+++ Import (2025-11-10)

@@ -1,7 +1,7 @@
 # AWS-Lambda-LESS-01.md
 
-**Version:** 1.0.0
+**Version:** 1.1.0
 **Date:** 2025-11-01
-**Purpose:** Cold start optimization
+**Purpose:** Cold start optimization (ENHANCED)

@@ -45,10 +45,15 @@
 ## Performance Impact
 
-Reduced cold starts by 60%
+Reduced cold starts by 75%
+
+## ADDED: Container Reuse Patterns
+
+New section on container reuse...

=== END DIFF ===

Now choose [1/2/3] for CONFLICT 1: _
```

---

### STEP 8: Dependency Check

**Automatic - AI performs:**

```
FOR EACH selected file:
  1. Parse cross-references
  2. Extract REF-IDs
  3. Check if dependencies present
  4. Validate availability
```

**Possible outcomes:**

**Scenario A: All Satisfied**
```
✅ Dependency Check Complete

45 files checked:
- 127 cross-references found
- 127 dependencies satisfied
- 0 missing dependencies

All files can be imported safely.

Proceeding to index update planning...
```

**Scenario B: Some Missing**
```
⚠️  Dependency Check Complete

45 files checked:
- 130 cross-references found
- 127 dependencies satisfied
- 3 missing dependencies

Missing Dependencies:

1. LESS-05 (referenced by LESS-01, LESS-08)
   Status: Not in import, not in target
   Impact: LESS-01 and LESS-08 will have broken references
   
   Options:
   [a] Include LESS-05 in import (if available in archive)
   [b] Proceed anyway (fix references later)
   [c] Exclude LESS-01 and LESS-08 from import

2. AP-12 (referenced by LESS-03)
   Status: Not in import, not in target
   Impact: LESS-03 will have broken reference
   
3. DEC-08 (referenced by AP-05)
   Status: Already exists in target ✅
   Impact: None (dependency satisfied)

Action required for dependencies 1-2.
Your choice: _
```

---

### STEP 9: Index Update Planning

**Automatic - AI generates:**

```
Analyzing affected indexes...

Affected Indexes (5):

1. /sima/platforms/aws/lambda/lessons/Lessons-Index.md
   - Current entries: 20
   - New entries: 8
   - Total after import: 28

2. /sima/platforms/aws/lambda/Lambda-Index.md
   - Current entries: 35
   - New entries: 8
   - Total after import: 43

3. /sima/platforms/aws/AWS-Index.md
   - Current entries: 59
   - New entries: 8
   - Total after import: 67

4. /sima/platforms/platforms-Master-Index.md
   - AWS file count: 59 → 67
   - Other platforms unchanged

5. /sima/Master-Index-of-Indexes.md
   - Total files: 255 → 263
   - Updated domain counts

Generating updated indexes...
```

**AI creates 5 artifacts with complete index files.**

**Expected output:**
```
✅ Index Updates Generated

Created 5 complete index artifacts:

[Artifact 1] Lessons-Index.md (28 entries, +8 new)
[Artifact 2] Lambda-Index.md (43 entries, +8 new)
[Artifact 3] AWS-Index.md (67 entries, +8 new)
[Artifact 4] platforms-Master-Index.md (updated counts)
[Artifact 5] Master-Index-of-Indexes.md (updated totals)

All artifacts complete and ready to deploy.
```

---

### STEP 10: Installation Instructions

**AI generates complete guide:**

```
=== IMPORT INSTALLATION GUIDE ===

SUMMARY:
- Files to import: 38 (7 skipped as identical, 3 conflicts resolved)
- Index updates: 5
- Estimated time: 10 minutes

PRE-INSTALLATION CHECKLIST:
✅ Version compatible (42 auto-upgraded, 3 manual reviewed)
✅ Conflicts resolved (1 kept existing, 2 replaced)
✅ Dependencies satisfied (127/130, 3 warnings acknowledged)
✅ Index updates prepared (5 artifacts ready)

INSTALLATION STEPS:

Step 1: Extract Packages
[detailed bash commands provided]

Step 2: Copy Files
[detailed bash commands for each file]

Step 3: Deploy Indexes
[map each artifact to target location]

Step 4: Verify Installation
[checksum verification commands]
[REF-ID validation commands]
[index navigation test]

VERIFICATION SCRIPT:
[complete bash script provided]
```

---

### STEP 11: Execute Installation

**User performs:**

```bash
# Navigate to workspace
cd ~/sima-import-workspace

# Extract all packages
unzip knowledge-base.zip -d extracted/
unzip knowledge-increment-01.zip -d extracted/

# Copy files (example - full list provided by AI)
cp extracted/platforms/aws/lambda/lessons/AWS-Lambda-LESS-17.md \
   /home/joe/sima/platforms/aws/lambda/lessons/

# Deploy index updates
# Save Artifact 1 to: /home/joe/sima/platforms/aws/lambda/lessons/Lessons-Index.md
# Save Artifact 2 to: /home/joe/sima/platforms/aws/lambda/Lambda-Index.md
# ... etc for all 5 artifacts
```

---

### STEP 12: Verification

**Run verification script:**

```bash
# Save AI-provided script
cat > verify-import.sh << 'EOF'
#!/bin/bash
# [Complete script from AI]
EOF

chmod +x verify-import.sh
./verify-import.sh
```

**Expected output:**
```
=== SIMA Import Verification ===

1. Verifying checksums...
   ✅ AWS-Lambda-Core-Concepts.md
   ✅ AWS-Lambda-Execution-Model.md
   ✅ AWS-Lambda-LESS-17.md
   ... (all files)

2. Validating REF-IDs...
   ✅ LESS-01 resolves
   ✅ AWS-Lambda-Core resolves
   ... (all REF-IDs)

3. Checking indexes...
   AWS Index entries: 67 ✅
   Lambda Index entries: 43 ✅
   Lessons Index entries: 28 ✅

4. Verifying file counts...
   Files in aws/lambda: 43 ✅

=== Verification Summary ===
✅ All checks passed!

Import Complete!
```

---

## CONFLICT RESOLUTION EXAMPLES

### Example 1: Minor Changes - Keep Existing

**Scenario:**
You made local edits to improve documentation.
Import has different minor changes.

**Decision:** Keep existing (Option 1)

**Reasoning:**
Your local improvements are more relevant to your use case.

**Action:**
```
File will be skipped.
Your version preserved.
No changes to system.
```

---

### Example 2: Major Upgrade - Replace

**Scenario:**
Import has significant enhancements.
Your version is outdated.

**Decision:** Replace with import (Option 2)

**Reasoning:**
Archive version has substantial improvements you want.

**Action:**
```
File will be overwritten.
Archive version installed.
Backup created automatically.
```

---

### Example 3: Conflicting Information - Keep Both

**Scenario:**
Both versions have valuable but different information.
Need to manually merge later.

**Decision:** Keep both (Option 3)

**Reasoning:**
Preserve both versions for manual comparison and merge.

**Action:**
```
Import renamed to: LESS-01-import.md
Both files available.
Manual merge when ready.
```

---

## TROUBLESHOOTING

### Problem: Version Too Old

**Symptom:**
```
❌ Files from v3.x cannot import to v4.2.2
```

**Solution:**
Use Migration Tool first:
```bash
sima-migrate-3-to-4.sh archive-files/
```

Then retry import.

---

### Problem: Missing Dependencies

**Symptom:**
```
⚠️  3 missing dependencies detected
```

**Solution 1:** Check if files exist in archive
- Review import-instructions.md
- Check if dependencies are in "unselected" list
- Use Import Selector tool to add them

**Solution 2:** Proceed with warnings
- Document broken references
- Plan to add missing content later
- Update references when available

---

### Problem: Index Already Modified

**Symptom:**
Current indexes have local changes not in import.

**Solution:**
- Review local index changes
- Manually merge index artifacts with local changes
- Or accept AI-generated indexes (losing local changes)

---

### Problem: Permission Errors

**Symptom:**
```
cp: cannot create regular file: Permission denied
```

**Solution:**
```bash
# Fix permissions
chmod +w /home/joe/sima/platforms/aws/lambda/lessons/

# Or run with appropriate user
sudo -u joe cp files...
```

---

## BEST PRACTICES

### 1. Always Backup First
```bash
tar -czf ~/sima-backup-$(date +%Y%m%d).tar.gz /home/joe/sima
```

### 2. Review Before Replacing
- Read conflict diffs carefully
- Understand what you're replacing
- Keep both if uncertain

### 3. Verify After Import
- Run verification script
- Test navigation
- Check key files manually

### 4. Document Changes
- Log what was imported
- Note conflict resolutions
- Record any issues

### 5. Clean Up Workspace
```bash
rm -rf ~/sima-import-workspace
```

---

## REFERENCE

**Import Mode Context:** `/sima/context/sima/context-SIMA-IMPORT-MODE-Context.md`  
**Version Matrix:** `/sima/docs/VERSION-COMPATIBILITY-MATRIX.md`  
**Implementation Plan:** SIMA Knowledge Archive System - Implementation Plan.md

---

**END OF IMPORT WORKFLOW GUIDE**

**Purpose:** Step-by-step import process  
**Scope:** Complete workflow from preparation to verification  
**Estimated Time:** 15-30 minutes per import
