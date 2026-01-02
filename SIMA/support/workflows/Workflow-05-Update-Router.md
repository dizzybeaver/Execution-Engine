# Workflow-05-Update-Router.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Generic workflow for updating router files  
**Type:** Support Workflow

---

## UPDATE ROUTER WORKFLOW

**Purpose:** Maintain router files for domain navigation

---

## PREREQUISITES

- [ ] Router file identified
- [ ] fileserver.example.com URLs available
- [ ] Changes documented
- [ ] Maintenance mode activated (if applicable)

---

## STEP 1: IDENTIFY ROUTER TYPE

**Router Types:**

**Domain Router:**
- Routes between subdomains
- Example: `/generic/generic-Router.md`
- Links to category routers

**Category Router:**
- Routes within category
- Example: `/generic/lessons/lessons-Router.md`
- Links to specific entries

**Mode Router:**
- Routes between modes
- Example: `/context/context-MODE-SELECTOR.md`
- Links to mode contexts

**Type:** _____________

---

## STEP 2: FETCH CURRENT ROUTER

**Process:**
```
1. Navigate to router location
2. Fetch via fileserver.example.com
3. Read complete file
4. Understand current structure
5. Note existing links
```

---

## STEP 3: IDENTIFY REQUIRED CHANGES

**Change Types:**

**Add Navigation Link:**
- New subdomain added
- New category created
- New mode added

**Update Existing Link:**
- Path changed
- Description updated
- Priority changed

**Remove Link:**
- Subdomain deprecated
- Category removed
- Mode obsolete

**Restructure:**
- Organization changed
- Decision tree modified
- Navigation optimized

---

## STEP 4: UPDATE ROUTER STRUCTURE

**Standard Router Format:**
```markdown
# [domain]-Router.md

**Version:** X.Y.Z
**Date:** YYYY-MM-DD
**Purpose:** Navigation router for [domain]
**Type:** Router

---

## NAVIGATION

**Select Category:**

- [Category 1](/path/to/category1/index.md) - Description
- [Category 2](/path/to/category2/index.md) - Description

---

## DECISION TREE

**Question:** [Navigation decision]

**If [condition]:**
→ Go to [destination1]

**Else if [condition]:**
→ Go to [destination2]

**Else:**
→ Go to [default]

---

## QUICK PATHS

**Common destinations:**
- [Frequent item 1](/path/)
- [Frequent item 2](/path/)
```

---

## STEP 5: ADD/UPDATE LINKS

**Add New Link:**
```markdown
### Before
- [Category A](/path/A/index.md) - Description A
- [Category C](/path/C/index.md) - Description C

### After
- [Category A](/path/A/index.md) - Description A
- [Category B](/path/B/index.md) - Description B (NEW)
- [Category C](/path/C/index.md) - Description C
```

**Update Existing:**
```markdown
### Before
- [Old Name](/old/path/index.md) - Old description

### After
- [New Name](/new/path/index.md) - Updated description
```

---

## STEP 6: UPDATE DECISION TREE

**Decision Tree Example:**
```markdown
## DECISION TREE

**Question:** What type of knowledge?

**If Generic Pattern:**
→ [Generic Domain](/generic/generic-Router.md)

**Else If Platform-Specific:**
→ [Platform Domain](/platforms/platforms-Router.md)

**Else If Language-Specific:**
→ [Language Domain](/languages/languages-Router.md)

**Else If Project-Specific:**
→ [Project Domain](/projects/projects-Router.md)

**Else:**
→ Review classification
```

**Update Rules:**
- Add new decision points
- Update conditions
- Modify destinations
- Maintain logic flow

---

## STEP 7: UPDATE QUICK PATHS

**Purpose:** Provide shortcuts to frequent destinations

**Example:**
```markdown
## QUICK PATHS

**Most Referenced:**
- [Lessons Index](/generic/lessons/index.md)
- [Decisions Index](/generic/decisions/index.md)
- [Anti-Patterns Index](/generic/anti-patterns/index.md)

**Recently Updated:**
- [LESS-43](/generic/lessons/LESS-43.md) (2025-11-10)
- [DEC-28](/generic/decisions/DEC-28.md) (2025-11-09)
```

---

## STEP 8: ADD METADATA

**Include:**
```markdown
## METADATA

**Total Categories:** ##
**Total Entries:** ##
**Last Updated:** YYYY-MM-DD
**Maintained By:** [Role/Person]

## NAVIGATION TIPS

- Use decision tree for classification
- Use quick paths for frequent access
- Check master index for comprehensive view
```

---

## STEP 9: VERIFY ALL LINKS

**Process:**
```
For each link in router:
  1. Extract path
  2. Verify file exists
  3. Check path accuracy
  4. Validate description
  5. Test navigation
```

**Checklist:**
- [ ] All internal links valid
- [ ] All external links valid
- [ ] Paths correct
- [ ] Descriptions accurate
- [ ] Decision logic sound

---

## STEP 10: TEST NAVIGATION

**Test Cases:**

**From Master Index:**
```
1. Start at master index
2. Click router link
3. Verify router loads
4. Follow navigation links
5. Reach destination
```

**Decision Tree:**
```
1. Start at router
2. Follow decision tree
3. Verify correct routing
4. Test all branches
5. Confirm destinations
```

**Quick Paths:**
```
1. Access quick paths
2. Click each link
3. Verify destinations correct
4. Check shortcuts work
```

---

## STEP 11: OUTPUT UPDATED ROUTER

**Requirements:**
- Complete file as artifact
- All existing content included
- Changes marked
- Filename in header
- Within 400 line limit

**Mark Changes:**
```markdown
# ADDED: New category link
- [New Category](/path/new/index.md) - Description

# MODIFIED: Updated path
- [Updated Category](/new/path/index.md) - Updated description
```

---

## STEP 12: UPDATE PARENT INDEXES

**If Router Structure Changed:**
```
1. Identify parent indexes
2. Fetch via fileserver.example.com
3. Update router references
4. Verify navigation chain
5. Output updated indexes
```

---

## MAINTENANCE

**Update Router When:**
- New subdomain added
- Subdomain removed
- Category reorganized
- Navigation optimized
- Links changed

**Review Frequency:**
- After major changes: Immediate
- Regular maintenance: Monthly
- Comprehensive review: Quarterly

---

## COMPLETE

**Outputs:**
1. Updated router file
2. Updated parent indexes (if applicable)
3. Verification test results

**Result:** Navigation maintained

---

**END OF WORKFLOW**

**Version:** 1.0.0  
**Lines:** 280 (within 400 limit)  
**Type:** Generic workflow  
**Usage:** Follow when updating router files