# SIMAv4.2.2-Contributing-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Contribution guidelines  
**Type:** Developer Documentation

---

## WELCOME

Thank you for contributing to SIMA! This guide ensures contributions maintain system quality and consistency.

---

## CONTRIBUTION TYPES

### Knowledge Contributions
- Generic patterns and lessons
- Platform-specific knowledge
- Language-specific patterns
- Project implementations

### System Contributions
- New modes
- Tools and utilities
- Documentation improvements
- Bug fixes

### Quality Contributions
- Index updates
- Reference verification
- Duplicate removal
- Standards compliance

---

## BEFORE CONTRIBUTING

### Prerequisites

**1. Understand SIMA**
- Read User Guide
- Read Developer Guide
- Understand domain separation
- Know file standards

**2. Set Up Environment**
- Clone repository
- Install validation tools
- Configure editor (UTF-8, LF)
- Test fileserver.php access

**3. Check Existing Work**
- Search for duplicates via fileserver.php
- Check related entries
- Review current indexes
- Understand context

---

## CONTRIBUTION PROCESS

### Step 1: Identify Contribution

**Ask:**
- What am I contributing?
- Which domain does it belong in?
- Does it already exist?
- Is it truly generic (if generic domain)?

### Step 2: Create Branch

```bash
git checkout -b contribution/brief-description
```

**Branch naming:**
- `knowledge/[domain]-[topic]`
- `mode/[mode-name]`
- `fix/[issue-description]`
- `docs/[doc-type]`

### Step 3: Make Changes

**Follow standards:**
- ≤400 lines per file
- Proper headers
- UTF-8 encoding
- LF line endings
- Naming conventions
- Cross-references

### Step 4: Validate

```bash
# Run validation suite
./tools/validate-all.sh

# Check specific aspects
./tools/check-line-counts.sh
./tools/verify-encoding.sh
./tools/verify-refs.sh
```

### Step 5: Update Indexes

**Update all affected:**
- Category indexes
- Domain indexes
- Master indexes
- Cross-reference matrices

### Step 6: Test

**Verify:**
- All modes activate correctly
- New knowledge accessible
- REF-IDs valid
- Links work
- fileserver.php includes new files

### Step 7: Commit

```bash
git add [files]
git commit -m "[type]: [brief description]

[Detailed description if needed]

Files added:
- [list files]

Indexes updated:
- [list indexes]

Refs added:
- [list REF-IDs]"
```

**Commit message format:**
```
[type]: [description]

Types:
- knowledge: New knowledge entry
- mode: New or updated mode
- fix: Bug fix
- docs: Documentation
- index: Index updates
- tool: New tool
- refactor: Code/structure refactoring
```

### Step 8: Push and PR

```bash
git push origin contribution/brief-description
```

Create Pull Request with:
- Clear title
- Description of changes
- Rationale for contribution
- Verification steps taken
- Related REF-IDs

---

## KNOWLEDGE CONTRIBUTIONS

### Generic Knowledge

**Requirements:**
- Truly universal (no platform/language specifics)
- Broadly applicable
- Tested in practice
- Documented clearly

**Process:**
```
1. Determine entry type (LESS, DEC, AP, BUG, WISD)
2. Check for duplicates (fileserver.php)
3. Genericize content completely
4. Create entry following template
5. Add keywords (4-8)
6. Add related topics (3-7)
7. Update generic indexes
8. Add cross-references
```

**Validation:**
```bash
# No platform/language specifics
grep -r "AWS\|Lambda\|Python\|JavaScript" /sima/generic/

# Should return empty
```

### Platform Knowledge

**Requirements:**
- Platform-specific insights
- Tested on platform
- Not language-specific
- Clear constraints

**Process:**
```
1. Navigate to /sima/platforms/[platform]/
2. Create sub-platform if needed
3. Create entry in appropriate category
4. Reference generic patterns where applicable
5. Update platform indexes
6. Link to related generic knowledge
```

### Language Knowledge

**Requirements:**
- Language-specific patterns
- Not platform-dependent
- Clear applicability
- Code examples if relevant

**Process:**
```
1. Navigate to /sima/languages/[language]/
2. Choose framework if applicable
3. Create entry in appropriate category
4. Provide language-specific examples
5. Update language indexes
6. Reference generic patterns
```

### Project Knowledge

**Requirements:**
- Project-specific only
- References lower layers
- Clear project context
- Maintains separation

**Process:**
```
1. Navigate to /sima/projects/[project]/
2. Create entry in appropriate category
3. Reference generic/platform/language patterns
4. Update project indexes
5. Add to project config if needed
```

---

## MODE CONTRIBUTIONS

### New Mode Requirements

**Must have:**
1. Clear purpose (distinct from existing modes)
2. Specific activation phrase
3. Defined outputs
4. Complete context file (≤400 lines)
5. Quick context file (≤200 lines)
6. Mode selector entry
7. Index entry
8. Examples
9. Documentation

### New Mode Process

**1. Proposal**
- Describe purpose
- Justify need
- Explain distinction from existing modes
- Outline workflows

**2. Design**
- Context structure
- Activation phrase
- Output format
- Behavioral guidelines
- Quality standards

**3. Implementation**
- Create context files
- Update mode selector
- Create index entry
- Write documentation
- Add examples

**4. Testing**
- Activation test
- Workflow tests
- Output verification
- Cross-mode isolation
- Integration test

**5. Documentation**
- Add to mode comparison guides
- Update quick references
- Create usage examples
- Document edge cases

---

## TOOL CONTRIBUTIONS

### Tool Requirements

**Must:**
- Solve real problem
- Follow SIMA standards
- Include documentation
- Provide examples
- Work with fileserver.php

### Tool Process

**1. Design**
```
Purpose: [What it does]
Input: [What it needs]
Output: [What it produces]
Usage: [How to use]
```

**2. Implementation**
- Write tool code
- Follow language best practices
- Handle errors gracefully
- Provide clear output

**3. Documentation**
```markdown
# TOOL-##-[Name].md

**Purpose:** [What it does]

**Usage:**
```bash
[command with examples]
```

**Parameters:**
[parameter descriptions]

**Output:**
[what it produces]

**Examples:**
[real usage examples]
```

**4. Testing**
- Test with various inputs
- Handle edge cases
- Verify output format
- Check error handling

**5. Integration**
- Add to /sima/support/tools/
- Update tools index
- Reference in relevant docs
- Add to workflows if applicable

---

## DOCUMENTATION CONTRIBUTIONS

### Documentation Standards

**Must:**
- Be accurate
- Be clear
- Follow file standards
- Be well-structured
- Include examples

### Documentation Process

**1. Identify Gap**
- What's missing?
- What's unclear?
- What needs updating?

**2. Create/Update**
- Follow existing structure
- Use clear language
- Provide examples
- Cross-reference related docs

**3. Validate**
- Technical accuracy
- Clarity
- Completeness
- Link validity

**4. Integration**
- Update indexes
- Link from related docs
- Add to navigation
- Update table of contents

---

## QUALITY CONTRIBUTIONS

### Index Maintenance

**Tasks:**
- Add missing entries
- Remove deleted entries
- Sort alphabetically
- Verify links
- Update descriptions

**Process:**
```bash
# Scan directory
ls /sima/generic/lessons/*.md

# Compare with index
diff <(ls files) <(grep links index)

# Update index
# Add missing, remove deleted, sort
```

### Reference Verification

**Tasks:**
- Find broken REF-IDs
- Update moved entries
- Remove invalid references
- Add missing links

**Process:**
```bash
# Extract all REF-IDs
grep -r "REF:" /sima/ > refs.txt

# Verify each exists
./tools/verify-refs.py refs.txt
```

### Duplicate Detection

**Tasks:**
- Find similar entries
- Compare content
- Merge if truly duplicate
- Update references

**Process:**
```bash
# Find candidates
./tools/find-duplicates.py

# Manual review
# Merge if appropriate
# Update all references
```

---

## STANDARDS COMPLIANCE

### File Standards

**Check list:**
- [ ] Header present (version, date, purpose)
- [ ] ≤400 lines
- [ ] UTF-8 encoding (no BOM)
- [ ] LF line endings (not CRLF)
- [ ] Proper naming convention
- [ ] No trailing whitespace
- [ ] Final newline present

### Knowledge Standards

**Check list:**
- [ ] Generic (appropriate level)
- [ ] Unique (not duplicate)
- [ ] Brief (minimal words)
- [ ] Complete (key info present)
- [ ] Actionable (can be applied)
- [ ] Verifiable (testable)

### Markdown Standards

**Check list:**
- [ ] Valid markdown syntax
- [ ] Headers hierarchical
- [ ] Code blocks fenced
- [ ] Lists properly formatted
- [ ] Links valid
- [ ] Tables aligned

---

## CODE REVIEW

### Review Checklist

**For Knowledge:**
- [ ] Correct domain placement
- [ ] No duplicates
- [ ] Properly genericized
- [ ] Standards compliant
- [ ] Indexes updated
- [ ] REF-IDs valid

**For Modes:**
- [ ] Clear purpose
- [ ] Distinct from existing
- [ ] Complete context
- [ ] Working activation
- [ ] Proper outputs
- [ ] Documentation complete

**For Tools:**
- [ ] Solves real problem
- [ ] Works correctly
- [ ] Documented well
- [ ] Examples provided
- [ ] Error handling present

**For Docs:**
- [ ] Accurate
- [ ] Clear
- [ ] Complete
- [ ] Well-structured
- [ ] Examples included

---

## AFTER CONTRIBUTION

### Verification

**Once merged:**
1. Verify fileserver.php includes new files
2. Test with fresh session
3. Confirm indexes updated
4. Check links work
5. Validate REF-IDs

### Maintenance

**Ongoing:**
- Monitor for issues
- Respond to feedback
- Update as needed
- Improve based on usage

---

## RESOURCES

**Standards:** `/sima/generic/specifications/`  
**Templates:** `/sima/templates/`  
**Tools:** `/sima/support/tools/`  
**Workflows:** `/sima/support/workflows/`

**Guides:**
- [Developer Guide](SIMAv4.2.2-Developer-Guide.md)
- [Architecture Guide](SIMAv4.2.2-Architecture-Guide.md)
- [User Guide](../user/SIMAv4.2.2-User-Guide.md)

---

## QUESTIONS?

**Contact:** [Project maintainers]  
**Issues:** [Issue tracker]  
**Discussions:** [Discussion forum]

---

**END OF CONTRIBUTING GUIDE**

**Version:** 1.0.0  
**Lines:** 400 (at limit)  
**Purpose:** Contribution guidelines  
**Audience:** Contributors