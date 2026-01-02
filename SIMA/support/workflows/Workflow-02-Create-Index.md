# Workflow-02-Create-Index.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Generic workflow for creating indexes  
**Type:** Support Workflow

---

## CREATE INDEX WORKFLOW

**Purpose:** Create or update index files systematically

---

## PREREQUISITES

- [ ] Directory to index identified
- [ ] fileserver.example.com URLs available
- [ ] Maintenance or appropriate mode activated

---

## STEP 1: IDENTIFY INDEX TYPE

**Types:**
- Category Index - Lists entries in category
- Master Index - Lists all category indexes
- Quick Index - Abbreviated navigation
- Router - Navigation decision tree

**Select Type:** _____________

---

## STEP 2: SCAN DIRECTORY

**Process:**
```
1. Navigate to target directory
2. Fetch directory listing via fileserver.example.com
3. List all entry files (*.md)
4. Exclude index and router files
5. Extract metadata from each file
```

**Metadata to Extract:**
- REF-ID (if applicable)
- Title
- Purpose/Description
- Date
- Version

---

## STEP 3: ORGANIZE ENTRIES

**Sorting Options:**

**Alphabetical:**
```
- By title (A-Z)
- By REF-ID type
- By filename
```

**Numerical:**
```
- By REF-ID number
- By date (newest/oldest)
- By version
```

**Categorical:**
```
- By subdomain
- By type
- By priority
```

**Choose Appropriate Sort:** _____________

---

## STEP 4: CREATE INDEX HEADER

**Standard Header:**
```markdown
# [domain]-[subdomain]-[category]-Index.md

**Version:** 1.0.0
**Date:** YYYY-MM-DD
**Purpose:** Index of [category] in [domain]/[subdomain]
**Location:** /sima/[domain]/[subdomain]/[category]/

---

## [CATEGORY] INDEX

**Total Entries:** ##

---
```

---

## STEP 5: ADD ENTRIES

**Entry Format:**
```markdown
### [Subcategory] (if applicable)

- [[TYPE]-## - Title](/path/to/file.md) - Brief description
- [[TYPE]-## - Title](/path/to/file.md) - Brief description
```

**Example:**
```markdown
### Core Practices

- [LESS-01 - Read Complete Files](/generic/lessons/LESS-01.md) - Always read files entirely before modification
- [LESS-02 - Measure Don't Guess](/generic/lessons/LESS-02.md) - Use metrics instead of assumptions
```

---

## STEP 6: ADD METADATA SECTIONS

**Optional Sections:**

**Categories Breakdown:**
```markdown
## By Category

**Critical:** 5 entries
**Performance:** 8 entries
**Documentation:** 12 entries
```

**Recent Additions:**
```markdown
## Recent Additions

- LESS-45 (2025-11-10)
- LESS-44 (2025-11-09)
- LESS-43 (2025-11-08)
```

**Most Referenced:**
```markdown
## Most Referenced

- LESS-01 (Referenced by 15 entries)
- LESS-15 (Referenced by 12 entries)
- LESS-02 (Referenced by 10 entries)
```

---

## STEP 7: ADD NAVIGATION

**Include:**
```markdown
## Navigation

**Parent:** /sima/[domain]/[domain]-Master-Index-of-Indexes.md
**Siblings:** 
- /[category1]/[domain]-[category1]-Index.md
- /[category2]/[domain]-[category2]-Index.md

**Related:**
- /other-domain/[category]/other-domain-[category]-Index.md
```

---

## STEP 8: ADD USAGE GUIDELINES

**Example:**
```markdown
## Usage Guidelines

**When to Reference:**
- Finding lesson by topic
- Checking for duplicates
- Cross-referencing entries
- Understanding category scope

**How to Use:**
1. Scan category list
2. Identify relevant entry
3. Follow link to full entry
4. Review related topics
```

---

## STEP 9: VERIFY INDEX

**Checklist:**
- [ ] All entries listed
- [ ] No duplicates
- [ ] Sort order correct
- [ ] Links functional
- [ ] Paths accurate
- [ ] Descriptions brief
- [ ] Count accurate
- [ ] Header complete
- [ ] Navigation present
- [ ] File ≤400 lines

---

## STEP 10: OUTPUT INDEX

**Format:**
- Complete file as artifact
- Markdown format
- Filename in header
- Proper structure

---

## STEP 11: UPDATE PARENT INDEX

**If Creating Category Index:**
```
1. Fetch master index
2. Add reference to new category index
3. Update entry count
4. Output updated master index
```

**If Creating Master Index:**
```
1. Fetch parent domain index
2. Add reference to new master index
3. Update navigation
4. Output updated parent index
```

---

## STEP 12: TEST NAVIGATION

**Verify:**
- [ ] Links work from master index
- [ ] Links work to entries
- [ ] Back navigation works
- [ ] Cross-references valid
- [ ] Router updated (if needed)

---

## MAINTENANCE

**Update When:**
- New entry added
- Entry deleted
- Entry moved
- Description changed
- Organization changed

**Update Process:**
```
1. Fetch current index via fileserver.example.com
2. Make changes
3. Verify all links
4. Output complete updated index
```

---

## COMPLETE

**Outputs:**
1. New or updated index file
2. Updated parent index (if applicable)
3. Updated router (if applicable)

**Result:** Navigation structure maintained

---

**END OF WORKFLOW**

**Version:** 1.0.0  
**Lines:** 240 (within 400 limit)  
**Type:** Generic workflow  
**Usage:** Follow when creating or updating any index