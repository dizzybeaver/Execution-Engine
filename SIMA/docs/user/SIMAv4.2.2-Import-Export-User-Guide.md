# SIMAv4.2.2-Import-Export-User-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-12  
**Purpose:** Complete guide to SIMA Import and Export functionality  
**Type:** User Guide

---

## 📚 OVERVIEW

SIMA's Import and Export modes enable knowledge sharing between SIMA instances. Export packages knowledge into portable bundles, and Import integrates knowledge from others into your instance.

**Use cases:**
- Share generic patterns with team members
- Distribute platform-specific knowledge
- Backup and restore knowledge
- Merge knowledge from multiple sources
- Onboard new team members with curated knowledge

---

## 🎯 EXPORT MODE

### What Export Does

Export Mode creates portable knowledge packages that include:
- Knowledge entries (markdown files)
- Dependency files (cross-referenced entries)
- Index files (category organization)
- Manifest file (metadata and checksums)
- Import instructions (step-by-step guide)

### Activating Export Mode

**Command:** `"Start SIMA Export Mode"`

**What happens:**
1. Export Mode context loads (20-30 seconds)
2. Claude is ready to package knowledge
3. You specify what to export

### Export Workflows

#### Workflow 1: Export Entire Domain

**Best for:** Sharing all knowledge from one domain

**Steps:**
```
1. "Start SIMA Export Mode"
2. "Export the generic domain"
3. Claude scans /sima/generic/ directory
4. Collects all files (lessons, decisions, anti-patterns, etc.)
5. Generates manifest and package
6. Outputs complete bundle as artifacts
```

**Result:** Complete domain in portable format

**Example domains:**
- `generic` - Universal patterns
- `platforms/aws` - AWS-specific knowledge
- `languages/python` - Python patterns
- `projects/myproject` - Project-specific knowledge

---

#### Workflow 2: Export Specific Category

**Best for:** Sharing focused knowledge set

**Steps:**
```
1. "Start SIMA Export Mode"
2. "Export all lessons from the generic domain"
3. Claude scans /sima/generic/lessons/
4. Collects lesson files plus dependencies
5. Generates manifest and package
6. Outputs bundle as artifacts
```

**Available categories:**
- `lessons` - Lessons learned
- `decisions` - Decision logs
- `anti-patterns` - Anti-patterns
- `specifications` - Specifications
- `wisdom` - Wisdom entries

---

#### Workflow 3: Export by REF-ID List

**Best for:** Curated knowledge sharing

**Steps:**
```
1. "Start SIMA Export Mode"
2. "Export LESS-01, LESS-05, DEC-03, and AP-02"
3. Claude fetches specified entries
4. Identifies dependencies (cross-references)
5. Includes all related files
6. Generates manifest and package
7. Outputs bundle as artifacts
```

**Why dependencies matter:**
- LESS-01 might reference DEC-10
- DEC-10 becomes part of export automatically
- Ensures complete, working knowledge set

---

### Export Package Structure

```
export-[name]-[date]/
├── manifest.yaml
│   ├── version: 4.2.2
│   ├── date: 2025-11-12
│   ├── source_instance: [your_instance]
│   ├── scope: [domain/category/ref-ids]
│   ├── count: [number_of_files]
│   └── files: [list with checksums]
│
├── import-instructions.md
│   ├── Target directories
│   ├── Conflict resolution steps
│   ├── Dependency requirements
│   └── Verification steps
│
├── files/
│   ├── LESS-01.md
│   ├── LESS-05.md
│   ├── DEC-03.md
│   └── [other entries]
│
└── indexes/
    ├── Lessons-Index.md
    ├── Decisions-Index.md
    └── [other indexes]
```

---

### Export Best Practices

**Before exporting:**
- ✅ Verify fileserver.php loaded (fresh files)
- ✅ Check all entries are current
- ✅ Update indexes if needed
- ✅ Review what will be included

**Choosing scope:**
- **Broad export** (domain) - Complete knowledge sharing
- **Focused export** (category) - Specific topic sharing
- **Curated export** (REF-IDs) - Handpicked knowledge

**After export:**
- ✅ Review manifest for completeness
- ✅ Check import instructions clarity
- ✅ Verify file count matches expectations
- ✅ Test import in clean SIMA instance (recommended)

---

## 📥 IMPORT MODE

### What Import Does

Import Mode integrates external knowledge packages by:
- Validating package integrity
- Checking for duplicate content
- Resolving REF-ID conflicts
- Placing files in correct locations
- Updating indexes automatically
- Generating import report

### Activating Import Mode

**Command:** `"Start SIMA Import Mode"`

**What happens:**
1. Import Mode context loads (20-30 seconds)
2. Claude is ready to integrate knowledge
3. You provide the export package

### Import Workflows

#### Workflow 1: Full Import

**Best for:** Trusted source, non-overlapping knowledge

**Steps:**
```
1. "Start SIMA Import Mode"
2. Provide export package (copy/paste or upload)
3. Claude validates manifest
4. Checks for duplicates (via fileserver.php)
5. Reports any conflicts
6. Imports all files
7. Updates all indexes
8. Generates import report
```

**When to use:** New domain, trusted content, minimal conflicts expected

---

#### Workflow 2: Selective Import

**Best for:** Partial integration from larger package

**Steps:**
```
1. "Start SIMA Import Mode"
2. Provide export package
3. "Import only the lessons, skip decisions"
4. Claude filters to specified categories
5. Checks those files for duplicates
6. Resolves conflicts
7. Imports selected only
8. Updates relevant indexes
9. Generates import report
```

**When to use:** Large package, only need subset, storage concerns

---

#### Workflow 3: Merge Import

**Best for:** Overlapping knowledge, careful integration

**Steps:**
```
1. "Start SIMA Import Mode"
2. Provide export package
3. Claude identifies duplicates
4. For each duplicate:
   - Shows both versions
   - Asks which to keep
   - Or merge both
5. Imports new content
6. Updates merged entries
7. Updates indexes
8. Generates detailed merge report
```

**When to use:** Similar knowledge domains, quality comparison needed

---

### Conflict Resolution

#### Type 1: REF-ID Collision

**Problem:** Import has LESS-01, you already have LESS-01

**Solutions:**
- **Renumber import** - Changes import to LESS-25 (next available)
- **Skip import** - Keep yours, ignore import
- **Replace yours** - Import overwrites (rare)

**What happens:**
- Claude renumbers automatically
- Updates all cross-references in import
- Documents mapping in report (LESS-01 → LESS-25)
- No manual work required

---

#### Type 2: Content Duplicate

**Problem:** Different REF-IDs, same/similar content

**Solutions:**
- **Keep yours** - Skip import entry
- **Keep import** - Use their version
- **Merge both** - Combine best parts

**What happens:**
- Claude shows both for comparison
- You decide which to keep
- Winning entry gets all cross-references
- Losing entry documented in report

---

#### Type 3: Dependency Missing

**Problem:** Import references LESS-99, you don't have it

**Solutions:**
- **Import anyway** - Accept broken link temporarily
- **Skip this entry** - Wait for complete package
- **Import dependency first** - If available in package

**What happens:**
- Claude flags the missing dependency
- You choose approach
- Decision documented in report
- Can fix later with another import

---

### Import Package Validation

**Before integration, Claude checks:**
1. ✅ manifest.yaml present and valid
2. ✅ Version compatibility (4.2.2)
3. ✅ All listed files present
4. ✅ Checksums match (integrity)
5. ✅ File formats correct (.md)
6. ✅ Headers present in files
7. ✅ REF-IDs follow standards

**If validation fails:**
- Import stops
- Error report generated
- No files modified
- Safe to retry after package fix

---

### Import Best Practices

**Before importing:**
- ✅ Backup current knowledge (export your own)
- ✅ Review package manifest
- ✅ Check source trustworthiness
- ✅ Understand package scope
- ✅ Plan for conflicts

**During import:**
- ✅ Read conflict descriptions carefully
- ✅ Compare content quality when merging
- ✅ Document any skip decisions
- ✅ Note REF-ID mappings

**After import:**
- ✅ Review import report
- ✅ Verify indexes updated
- ✅ Test cross-references work
- ✅ Check no broken links
- ✅ Update project configs if needed

---

## 🔄 COMPLETE WORKFLOW EXAMPLE

### Scenario: Sharing AWS Lambda Knowledge

**Team Member A (Exporter):**
```
1. Has extensive AWS Lambda knowledge in SIMA
2. "Start SIMA Export Mode"
3. "Export the platforms/aws domain"
4. Receives export package (20 files)
5. Shares package with Team Member B
```

**Team Member B (Importer):**
```
1. Receives export package
2. "Start SIMA Import Mode"
3. Provides package to Claude
4. Claude finds:
   - 15 new files (no conflicts)
   - 3 REF-ID collisions (B already has some AWS knowledge)
   - 2 content duplicates
5. Claude auto-renumbers collisions
6. B reviews duplicates, keeps better versions
7. Import completes
8. 20 AWS Lambda lessons now in B's SIMA
9. All indexes updated automatically
```

**Result:** Knowledge successfully transferred with conflicts resolved

---

## 📊 IMPORT REPORT EXAMPLE

```markdown
# Import Report - AWS Lambda Knowledge
Date: 2025-11-12
Source: TeamMemberA-SIMA
Package: export-aws-lambda-2025-11-10

## Summary
- Files in package: 20
- Successfully imported: 18
- Skipped (duplicates): 2
- REF-IDs renumbered: 3
- Broken links: 0

## REF-ID Mappings
- AWS-LESS-01 → AWS-LESS-15 (collision)
- AWS-LESS-02 → AWS-LESS-16 (collision)
- AWS-DEC-03 → AWS-DEC-08 (collision)

## Skipped Files
- AWS-LESS-05.md (identical to existing)
- AWS-AP-02.md (lower quality than existing)

## Actions Taken
1. Imported 15 new files to /sima/platforms/aws/
2. Renumbered 3 files for REF-ID conflicts
3. Updated 5 index files
4. Verified all cross-references
5. No broken links detected

## Next Steps
- Review imported content
- Update project configs if AWS patterns used
- Consider merging skipped duplicates manually if needed
```

---

## ⚠️ IMPORTANT NOTES

### Version Compatibility

**SIMAv4.2.2 exports compatible with:**
- ✅ SIMAv4.2.x (same major/minor version)
- ⚠️ SIMAv4.1.x (may need format conversion)
- ❌ SIMAv3.x (requires migration first)

**Always check:** manifest.yaml `version:` field

### Security Considerations

**Export contains:**
- ✅ Knowledge entries (safe to share)
- ✅ Patterns and lessons (safe to share)
- ❌ Should NOT contain sensitive data
- ❌ Should NOT contain credentials

**Before sharing exports:**
- Review all files for sensitive info
- Check examples don't expose secrets
- Verify no internal system details
- Consider audience trust level

### Storage Considerations

**Package sizes:**
- Small export (5-10 files): ~50-100 KB
- Medium export (20-50 files): ~200-500 KB
- Large export (100+ files): ~1-2 MB
- Full domain: ~2-5 MB

**Your SIMA instance:**
- No hard storage limits
- Keep total files under 1000 for performance
- Split large domains if needed

---

## 🆘 TROUBLESHOOTING

### Problem: Export Fails

**Symptoms:** Export mode times out or errors

**Causes:**
- fileserver.php not loaded
- Files missing on server
- Permissions issues

**Solutions:**
1. Verify fileserver.php loaded at session start
2. Check all referenced files exist
3. Try smaller export scope
4. Retry in new session

---

### Problem: Import Finds Many Conflicts

**Symptoms:** Too many REF-ID collisions

**Causes:**
- Similar knowledge already exists
- Package from related instance
- Overlapping domains

**Solutions:**
1. Use Merge Import workflow instead
2. Review duplicates carefully
3. Consider selective import
4. May indicate redundant content

---

### Problem: Broken Links After Import

**Symptoms:** Cross-references don't work

**Causes:**
- Dependency not imported
- REF-ID mapping failed
- Index not updated

**Solutions:**
1. Review import report for skipped dependencies
2. Import missing dependencies
3. Run Maintenance Mode to rebuild indexes
4. Verify REF-ID mappings applied

---

### Problem: Can't Find Import Instructions

**Symptoms:** Don't know how to use package

**Causes:**
- import-instructions.md not included
- Package incomplete

**Solutions:**
1. Request complete package from source
2. Follow this guide's Import workflow
3. Validate manifest.yaml first

---

## 📖 RELATED DOCUMENTATION

**Mode Documentation:**
- `/sima/context/sima/context-SIMA-EXPORT-MODE-Context.md`
- `/sima/context/sima/context-SIMA-IMPORT-MODE-Context.md`

**Related Modes:**
- Maintenance Mode - Update indexes after import
- Learning Mode - Create knowledge to export
- General Mode - Query imported knowledge

**Specifications:**
- SPEC-FILE-STANDARDS.md - File format requirements
- SPEC-HEADERS.md - Required file headers
- SPEC-NAMING.md - REF-ID naming conventions

---

## ✅ QUICK CHECKLIST

### Exporting Knowledge

- [ ] fileserver.php loaded
- [ ] Scope defined (domain/category/REF-IDs)
- [ ] Files verified current
- [ ] Indexes updated
- [ ] Export Mode activated
- [ ] Package generated
- [ ] Manifest reviewed
- [ ] Import instructions clear

### Importing Knowledge

- [ ] Package received and complete
- [ ] Backup created (your knowledge)
- [ ] Source trusted
- [ ] Import Mode activated
- [ ] Manifest validated
- [ ] Duplicates checked
- [ ] Conflicts resolved
- [ ] Import report reviewed
- [ ] Indexes verified
- [ ] Cross-references tested

---

**END OF USER GUIDE**

**Summary:** Export packages knowledge for sharing, Import integrates external knowledge, both handle conflicts automatically while maintaining data integrity.
