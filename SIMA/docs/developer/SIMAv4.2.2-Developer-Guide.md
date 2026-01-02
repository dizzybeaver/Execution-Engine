# SIMAv4.2.2-Developer-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** SIMA development guide  
**Type:** Developer Documentation

---

## INTRODUCTION

This guide covers extending SIMA with new knowledge, features, modes, and capabilities while maintaining system integrity.

---

## DEVELOPMENT PRINCIPLES

### 1. Domain Separation
Knowledge flows: Generic → Platform → Language → Project

**Never:**
- Put project specifics in generic
- Put language specifics in platform
- Mix domains inappropriately

**Always:**
- Place knowledge at correct level
- Reference lower layers from higher
- Keep generic truly generic

### 2. File Standards
**Every file must:**
- Have header (version, date, purpose)
- Be ≤400 lines
- Use UTF-8 encoding
- Have LF line endings
- Include filename in header

**Markdown files need:**
- Proper structure
- Cross-references (REF-IDs)
- Keywords (4-8)
- Related topics (3-7)

### 3. Naming Conventions

**Knowledge Entries:**
```
(Domain)-(SubDomain)-TYPE-##-(Description).md

Examples:
generic-LESS-01-read-complete-files.md
platform-aws-lambda-DEC-01-stateless.md
language-python-suga-ARCH-01-gateway.md
project-sima-LESS-01-fresh-content.md
```

**Indexes:**
```
(domain)-(subdomain)-(category)-Index.md

Examples:
generic-lessons-Index.md
platform-aws-lambda-Index.md
language-python-Index.md
project-sima-Index.md
```

**Routers:**
```
(domain)-Router.md

Examples:
generic-Router.md
languages-Router.md
platforms-Router.md
projects-Router.md
```

### 4. Cross-Referencing
**Use REF-IDs consistently:**
```markdown
**REF:** LESS-01, DEC-04, AP-08

**Related:** LESS-15, WISD-06, BUG-01

**See also:** ARCH-01, GATE-03
```

---

## ADDING KNOWLEDGE

### Process

**1. Determine Domain**
- Is it universal? → Generic
- Platform-specific? → Platform
- Language-specific? → Language
- Project-specific? → Project

**2. Check for Duplicates**
```
Use fileserver.php URLs to fetch fresh entries
Search: "topic keyword type"
If exists: Update that entry
If new: Proceed with creation
```

**3. Choose Entry Type**
- LESS = Lesson learned
- DEC = Decision made
- AP = Anti-pattern (what NOT to do)
- BUG = Bug discovered and fixed
- WISD = Profound insight

**4. Genericize Content**
```
Remove: Project names, specific tools
Keep: Universal principles, patterns
Transform: "In Lambda..." → "In serverless..."
Focus: Transferable knowledge
```

**5. Create Entry**
```markdown
# TYPE-##.md

**Version:** 1.0.0
**Date:** YYYY-MM-DD
**Purpose:** Brief description

[Content following template]

**Keywords:** k1, k2, k3, k4
**Related:** REF-ID1, REF-ID2
```

**6. Update Indexes**
- Add to category index
- Add to domain index
- Update master index if needed

**7. Add Cross-References**
- Link from related entries
- Update cross-reference matrix
- Verify all REF-IDs valid

---

## CREATING NEW MODE

### Requirements

**Mode Must Have:**
1. Full context file (≤400 lines)
2. Quick context file (≤200 lines)
3. Mode selector entry
4. Clear activation phrase
5. Specific purpose
6. Distinct outputs

### Process

**1. Define Mode**
```yaml
Name: [MODE_NAME]
Purpose: [What it does]
Activation: "Start [MODE_NAME]"
Output: [Type of artifacts]
Scope: [What it accesses]
```

**2. Create Context File**
```
/sima/context/[category]/context-[MODE]-Context.md
```

**Contents:**
- What This Mode Is
- File Retrieval (fileserver.php)
- Critical Rules/Principles
- Workflows
- Artifact Rules
- Quality Standards
- Examples
- Ready Checklist

**3. Create Quick Context**
```
/sima/context/[category]/context-[MODE]-START-Quick-Context.md
```

**Contents:**
- Quick overview
- Key rules
- Fast workflows
- Minimal examples

**4. Add to Mode Selector**
```markdown
## Mode X: [Name]
**Phrase:** "Start [MODE_NAME]"
**Loads:** context-[MODE]-Context.md
**Purpose:** [Brief description]
**Time:** [Load time]
```

**5. Update Decision Logic**
```
ELSE IF phrase = "Start [MODE_NAME]"
    THEN load context-[MODE]-Context.md
```

**6. Create Index Entry**
```
/sima/context/[category]/context-[CATEGORY]-Index.md
```

**7. Test Mode**
- Activate with phrase
- Verify correct context loads
- Verify behaviors work
- Check no cross-mode leakage

---

## EXTENDING PLATFORM

### Adding New Platform

**1. Create Directory Structure**
```
/sima/platforms/[platform]/
├── anti-patterns/
├── core/
├── decisions/
├── lessons/
├── workflows/
├── [platform]-Router.md
└── [platform]-Master-Index.md
```

**2. Create Sub-Platforms (if needed)**
```
/sima/platforms/[platform]/[sub-platform]/
├── anti-patterns/
├── core/
├── decisions/
├── lessons/
├── workflows/
├── [platform]-[sub]-Router.md
└── [platform]-[sub]-Master-Index.md
```

**3. Create Knowledge Entries**
Follow entry creation process above.

**4. Create Indexes**
- Master index for platform
- Category indexes
- Sub-platform indexes

**5. Update Platform Router**
Link to all sub-platforms and categories.

**6. Update Master Platform Index**
Add new platform to listing.

---

## EXTENDING LANGUAGE

### Adding New Language

**1. Create Directory Structure**
```
/sima/languages/[language]/
├── anti-patterns/
├── decisions/
├── lessons/
├── wisdom/
├── workflows/
└── frameworks/
```

**2. Create Framework Support**
```
/sima/languages/[language]/frameworks/[framework]/
├── anti-patterns/
├── decisions/
├── lessons/
├── wisdom/
├── [other directories]
└── [framework]-Index.md
```

**3. Create Language Knowledge**
Language-specific patterns, decisions, lessons.

**4. Create Framework Knowledge**
Framework-specific patterns within language.

**5. Create Indexes**
- Language master index
- Framework indexes
- Category indexes

**6. Update Language Router**
Link to language and frameworks.

**7. Update Master Language Index**
Add new language to listing.

---

## CREATING NEW PROJECT

### Use New Project Mode

**Automated:**
```
"Start New Project Mode: [PROJECT_NAME]"
```

Generates:
- Directory structure
- Config files
- Mode extensions
- Indexes
- README

### Manual Setup

**1. Create Structure**
```
/sima/projects/[project]/
├── config/
│   └── knowledge-config.yaml
├── anti-patterns/
├── core/
├── decisions/
├── lessons/
├── workflows/
├── [project]-Router.md
├── [project]-Master-Index.md
└── README.md
```

**2. Create Config**
```yaml
project:
  name: "[PROJECT_NAME]"
  description: "[DESCRIPTION]"
  platform: "[PLATFORM]"
  language: "[LANGUAGE]"
  architectures: [LIST]
```

**3. Create Mode Extensions**
```
PROJECT-MODE-[PROJECT].md
DEBUG-MODE-[PROJECT].md
Custom-Instructions-[PROJECT].md
```

**4. Create Indexes**
All category indexes plus master.

**5. Update Project Router**
Link to all categories.

**6. Update Master Project Index**
Add new project to listing.

---

## FILE VALIDATION

### Pre-Commit Checks

**Run:**
```bash
# Check line counts
find /sima -name "*.md" -exec wc -l {} \; | awk '$1 > 400'

# Check encoding
find /sima -name "*.md" -exec file -b --mime-encoding {} \; | grep -v utf-8

# Check line endings
find /sima -name "*.md" -exec file {} \; | grep CRLF

# Verify REF-IDs
python tools/verify-refs.py
```

### Standards Compliance

**Every file must pass:**
- [ ] Header present
- [ ] ≤400 lines
- [ ] UTF-8 encoding
- [ ] LF line endings
- [ ] Proper naming
- [ ] Valid REF-IDs
- [ ] Index updated

---

## TESTING

### Mode Testing

**Test each mode:**
```
1. Activate with phrase
2. Verify context loads
3. Test core workflows
4. Check artifact output
5. Verify standards compliance
```

### Knowledge Testing

**Verify entries:**
- Accessible via indexes
- REF-IDs valid
- Cross-references work
- Keywords accurate
- Related topics linked

### Integration Testing

**Full system:**
- All modes activate
- All routers work
- All indexes complete
- No broken links
- Fresh content via fileserver.php

---

## DEPLOYMENT

### Pre-Deployment

**1. Validation**
```bash
# Run all checks
./tools/validate-structure.sh
```

**2. Verification**
- All files ≤400 lines
- All indexes updated
- All REF-IDs valid
- All routers correct

**3. Testing**
Test each mode activation.

### Deployment

**1. Update fileserver.php**
Ensure new files included in scan.

**2. Update File-Server-URLs.md**
Verify version current.

**3. Deploy Files**
Copy to production.

**4. Verify**
Test with fresh session:
```
1. Upload File-Server-URLs.md
2. Activate each mode
3. Verify functionality
```

---

## TROUBLESHOOTING DEVELOPMENT

### Issue: File Too Large

**Problem:** Entry exceeds 400 lines  
**Solution:** Split into multiple files  
**Pattern:**
```
Original: TYPE-##.md (500 lines)
Split to:
- TYPE-##.md (250 lines) - Core
- TYPE-##-Examples.md (250 lines) - Examples
```

### Issue: Duplicate REF-ID

**Problem:** REF-ID already used  
**Solution:** Use next sequential number  
**Check:** Search all files for REF-ID before assigning

### Issue: Broken Cross-Reference

**Problem:** REF-ID points to non-existent file  
**Solution:** Update REF-ID or create missing entry  
**Prevention:** Verify all REF-IDs before committing

### Issue: Wrong Domain

**Problem:** Knowledge in incorrect directory  
**Solution:** Move to correct domain, update indexes  
**Check:** Is it truly generic? Or platform/language specific?

---

## BEST PRACTICES

### Knowledge Creation
- Check duplicates FIRST (via fileserver.php)
- Genericize by default
- Be ruthlessly brief
- Extract immediately
- Cross-reference heavily

### File Management
- One topic per file
- ≤400 lines always
- Headers always
- UTF-8 always
- LF endings always

### Index Maintenance
- Update immediately after changes
- Keep alphabetically sorted
- Brief descriptions
- Valid links only

### Quality
- Actionable content
- Generic principles
- Unique entries
- Brief expression
- Complete information
- Verifiable claims

---

## RESOURCES

**Templates:** `/sima/templates/`  
**Tools:** `/sima/support/tools/`  
**Workflows:** `/sima/support/workflows/`  
**Standards:** `/sima/generic/specifications/`

**Related Docs:**
- [Contributing Guide](SIMAv4.2.2-Contributing-Guide.md)
- [Architecture Guide](SIMAv4.2.2-Architecture-Guide.md)
- [User Guide](../user/SIMAv4.2.2-User-Guide.md)

---

**END OF DEVELOPER GUIDE**

**Version:** 1.0.0  
**Lines:** 400 (at limit)  
**Purpose:** Development practices  
**Audience:** SIMA developers and contributors