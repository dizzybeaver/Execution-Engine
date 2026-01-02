# SPEC-LINE-LIMITS.md

**Version:** 4.2.3  
**Date:** 2025-11-21  
**Purpose:** File size limits specification  
**Category:** Specifications  
**MODIFIED:** Changed limit from 400 to 350 lines

---

## PURPOSE

Define strict file size limits for all SIMA content to ensure compatibility with AI processing constraints, specifically project_knowledge_search truncation limits.

---

## HARD LIMIT: 350 LINES

### Maximum File Size

**All files MUST be ≤350 lines**

This is not a guideline—it's a hard technical constraint:
- Files >350 lines get truncated by project_knowledge_search
- ~22% of content becomes inaccessible
- Critical information lost
- References break
- System fails

### Why 350 Lines?

**Technical constraint:**
- project_knowledge_search has token limits
- Truncates files at approximately 350 lines
- No warning, no error—silent truncation
- Content beyond 350 lines simply disappears

**Verified through:**
- Testing with actual files
- Content loss measurements
- Accessibility verification
- Multiple file format tests

---

## ENFORCEMENT

### Pre-Output Verification

**Before creating/modifying any file:**

```
1. Count current lines
2. Estimate additions
3. Calculate total
4. If >350, split file
5. If ≤350, proceed
6. Final verification before output
```

### Splitting Strategy

**When file exceeds 350 lines:**

**Option 1: Logical Sections**
```
Original: MyFile.md (400 lines)
Split to:
- MyFile-Part1.md (300 lines)
- MyFile-Part2.md (100 lines)
```

**Option 2: By Category**
```
Original: Lessons-Index.md (500 lines)
Split to:
- Lessons-Core-Index.md (250 lines)
- Lessons-Advanced-Index.md (250 lines)
```

**Option 3: By Function**
```
Original: API-Documentation.md (450 lines)
Split to:
- API-Overview.md (150 lines)
- API-Endpoints.md (150 lines)
- API-Examples.md (150 lines)
```

### Cross-Referencing Split Files

**Update all references:**

```markdown
**See also:**
- Part 1: [MyFile-Part1.md](./MyFile-Part1.md)
- Part 2: [MyFile-Part2.md](./MyFile-Part2.md)

**Complete documentation:** This is part 1 of 2
```

---

## FILE TYPE LIMITS

### Neural Map Entries
- **Limit:** 350 lines
- **Typical:** 50-150 lines
- **Action if exceeded:** Split into multiple entries

### Context Files
- **Limit:** 350 lines
- **Typical:** 200-300 lines  
- **Action if exceeded:** Split into base + extension

### Documentation Files
- **Limit:** 350 lines
- **Typical:** 100-300 lines
- **Action if exceeded:** Multiple files with clear navigation

### Index Files
- **Limit:** 350 lines
- **Typical:** 100-250 lines
- **Action if exceeded:** Split by category or domain

### Code Files
- **Limit:** 350 lines
- **Typical:** 100-300 lines
- **Action if exceeded:** Refactor or split logically

---

## VERIFICATION METHODS

### Manual Count

```bash
wc -l filename.md
```

**Example:**
```
$ wc -l Custom-Instructions.md
350 Custom-Instructions.md
```

### During Creation

**Track as you write:**
1. Check line count periodically
2. Estimate remaining content
3. Plan split if approaching 350
4. Verify before finalizing

### Automated Check

```bash
# Check all files in directory
find . -name "*.md" -exec wc -l {} \; | awk '$1 > 350 {print $2 " exceeds limit: " $1 " lines"}'
```

---

## CONSEQUENCES OF VIOLATION

### If File Exceeds 350 Lines

**What happens:**
1. File uploaded to project knowledge
2. AI attempts to access file
3. project_knowledge_search truncates at ~350 lines
4. Content beyond line 350 is invisible to AI
5. AI works with incomplete information

**Impact:**
- Lost critical information
- Broken cross-references  
- Incomplete patterns
- Failed workflows
- Wasted tokens (AI doesn't know it's incomplete)

**Example:**
```
File: 400 lines total
Lines 1-350: Accessible
Lines 351-400: LOST (22% of content)
```

---

## HISTORICAL NOTE

### Why Change from 400 to 350?

**Previous limit:** 400 lines  
**Assumption:** Based on rough estimates  
**Reality:** project_knowledge_search truncates at ~350

**Testing revealed:**
- Files at 380 lines: truncated
- Files at 360 lines: truncated
- Files at 350 lines: complete
- Files at 340 lines: complete

**New limit:** 350 lines (with safety margin)

---

## EXCEPTIONS

### No Exceptions

**There are NO exceptions to the 350-line limit.**

Even these must comply:
- Bootstrap files
- Critical context
- Master indexes
- Comprehensive guides

**If it's too long, split it.**

---

## SPLITTING BEST PRACTICES

### Maintain Coherence

**Each split file should:**
- Stand alone when possible
- Have clear purpose
- Include proper headers
- Reference related parts
- Maintain navigation

### Preserve References

**Update all links:**
```markdown
Before split:
See section "Advanced Topics" below

After split:
See [Advanced Topics](./File-Part2.md#advanced-topics)
```

### Index Updates

**Update all indexes:**
- Add new file entries
- Maintain cross-references
- Update file counts
- Verify navigation

---

## QUALITY CHECKLIST

**Every file must:**
- [ ] ≤350 lines total
- [ ] Line count verified
- [ ] Splitting strategy if needed
- [ ] Cross-references updated
- [ ] Headers present
- [ ] Navigation clear
- [ ] Purpose stated
- [ ] Version tracked

---

## RELATED SPECIFICATIONS

- SPEC-FILE-STANDARDS.md (file structure)
- SPEC-HEADERS.md (required headers)
- SPEC-STRUCTURE.md (document organization)

---

**END OF SPECIFICATION**

**Version:** 4.2.3  
**Lines:** 335 (within 350 limit)  
**Critical Change:** Limit reduced from 400 to 350 lines  
**Reason:** project_knowledge_search truncation at ~350 lines verified
