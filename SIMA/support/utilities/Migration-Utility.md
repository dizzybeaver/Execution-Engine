# Migration-Utility.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Generic migration utility guide  
**Type:** Support Utility

---

## MIGRATION UTILITY

**Purpose:** Guide for migrating between SIMA versions

---

## OVERVIEW

**What This Utility Does:**
- Helps migrate from older SIMA versions
- Validates migration readiness
- Provides step-by-step migration process
- Verifies migration success

**Supported Migrations:**
- SIMAv3 → SIMAv4
- SIMAv4.x → SIMAv4.y (minor versions)
- Future version migrations

---

## PRE-MIGRATION CHECKLIST

### Backup Current System
- [ ] Full backup created
- [ ] Backup tested
- [ ] Backup location documented
- [ ] Rollback plan ready

### Assess Current System
- [ ] Current version identified
- [ ] Total files counted
- [ ] Custom modifications documented
- [ ] Dependencies identified

### Prepare Destination
- [ ] Target version determined
- [ ] Blank SIMA downloaded
- [ ] Installation verified
- [ ] fileserver.example.com configured

---

## MIGRATION STRATEGIES

### Strategy 1: Clean Install + Import
**Best For:** Major version upgrades

**Process:**
1. Install blank target SIMA
2. Export knowledge from source
3. Import into target
4. Validate
5. Switch to target

**Pros:**
- Clean structure
- No legacy issues
- Full validation

**Cons:**
- Time intensive
- Requires manual review

### Strategy 2: In-Place Upgrade
**Best For:** Minor version upgrades

**Process:**
1. Backup current system
2. Apply upgrade scripts
3. Update file formats
4. Validate changes
5. Test functionality

**Pros:**
- Faster
- Preserves customizations

**Cons:**
- Risk of issues
- Harder to rollback

### Strategy 3: Parallel Migration
**Best For:** Critical systems

**Process:**
1. Run both versions
2. Migrate incrementally
3. Validate each batch
4. Switch when complete

**Pros:**
- Zero downtime
- Safe validation
- Gradual transition

**Cons:**
- Resource intensive
- Longer timeline

---

## MIGRATION STEPS (GENERIC)

### Step 1: Preparation
```
1. Review migration guide
2. Check compatibility
3. Create backups
4. Document current state
5. Set migration window
```

### Step 2: Export Current Knowledge
```
1. Activate export mode
2. Define export scope
3. Run export workflow
4. Validate export package
5. Store safely
```

### Step 3: Install Target Version
```
1. Download blank SIMA
2. Extract to destination
3. Configure fileserver
4. Verify structure
5. Test basic functionality
```

### Step 4: Import Knowledge
```
1. Activate import mode
2. Load export package
3. Run import workflow
4. Resolve conflicts
5. Update indexes
```

### Step 5: Validation
```
1. Verify all files imported
2. Check cross-references
3. Test navigation
4. Validate indexes
5. Run verification workflow
```

### Step 6: Cutover
```
1. Final backup of old system
2. Switch to new system
3. Update bookmarks
4. Notify users (if applicable)
5. Monitor for issues
```

---

## VERSION-SPECIFIC MIGRATIONS

### SIMAv3 → SIMAv4

**Major Changes:**
- Directory structure reorganized
- Domain separation introduced
- REF-ID format standardized
- File standards updated
- Mode system enhanced

**Migration Steps:**
```
1. Export all SIMAv3 knowledge
2. Install blank SIMAv4
3. Map SIMAv3 paths to SIMAv4 structure
4. Update REF-ID format
5. Update file headers
6. Import to SIMAv4
7. Update indexes
8. Verify structure
```

**Path Mapping:**
```
SIMAv3: /NM##/LESS-01.md
SIMAv4: /generic/lessons/generic-LESS-01.md

SIMAv3: /project/lesson.md
SIMAv4: /projects/[project]/lessons/[project]-LESS-##.md
```

---

## COMMON MIGRATION ISSUES

### Issue 1: Broken References
**Symptom:** REF-IDs not found  
**Cause:** Path changes  
**Fix:** Update cross-references with new paths

### Issue 2: Duplicate REF-IDs
**Symptom:** Multiple files with same REF-ID  
**Cause:** Merging multiple sources  
**Fix:** Renumber duplicates, update references

### Issue 3: Format Incompatibility
**Symptom:** Files fail validation  
**Cause:** Old format not compatible  
**Fix:** Update headers, encoding, line endings

### Issue 4: Missing Dependencies
**Symptom:** References to non-existent files  
**Cause:** Incomplete export  
**Fix:** Re-export with dependencies included

---

## ROLLBACK PROCEDURE

**If Migration Fails:**
```
1. Stop migration immediately
2. Document failure point
3. Restore from backup
4. Verify restore successful
5. Analyze root cause
6. Fix issues
7. Retry migration
```

---

## POST-MIGRATION TASKS

### Immediate
- [ ] Verify all functionality
- [ ] Test navigation
- [ ] Check indexes
- [ ] Validate references
- [ ] Monitor for issues

### Short-Term
- [ ] Update documentation
- [ ] Train users (if applicable)
- [ ] Archive old system
- [ ] Update bookmarks
- [ ] Document lessons learned

### Long-Term
- [ ] Monitor performance
- [ ] Optimize structure
- [ ] Add improvements
- [ ] Plan next migration
- [ ] Update migration guide

---

## MIGRATION CHECKLIST

### Pre-Migration
- [ ] Backup created
- [ ] Current version documented
- [ ] Target version determined
- [ ] Migration strategy selected
- [ ] Timeline established

### During Migration
- [ ] Export completed
- [ ] Import completed
- [ ] Conflicts resolved
- [ ] Indexes updated
- [ ] Validation passed

### Post-Migration
- [ ] All files present
- [ ] Navigation works
- [ ] References valid
- [ ] Users notified
- [ ] Old system archived

---

## SUPPORT

**If You Need Help:**
- Review migration documentation
- Check common issues section
- Consult version-specific guides
- Test in non-production first
- Document your process

---

**END OF UTILITY**

**Version:** 1.0.0  
**Lines:** 300 (within 400 limit)  
**Type:** Migration utility guide  
**Usage:** Reference when migrating SIMA versions