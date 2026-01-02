# Workflow-01-Add-Knowledge-Entry.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Generic workflow for adding knowledge entries  
**Type:** Support Workflow

---

## ADD KNOWLEDGE ENTRY WORKFLOW

**Purpose:** Systematic process for creating new knowledge entries

---

## PREREQUISITES

- [ ] fileserver.example.com URLs available
- [ ] Learning or appropriate mode activated
- [ ] Source material prepared
- [ ] Entry type determined (LESS, DEC, AP, BUG, WISD)

---

## STEP 1: DETERMINE DOMAIN

**Question:** Where does this knowledge belong?

**Decision Tree:**
```
Is it universal/generic?
  YES → /generic/
  NO → Continue

Is it platform-specific?
  YES → /platforms/[platform]/
  NO → Continue

Is it language-specific?
  YES → /languages/[language]/
  NO → Continue

Is it project-specific?
  YES → /projects/[project]/
  NO → Review again, likely /generic/
```

**Output:** Domain path identified

---

## STEP 2: CHOOSE CATEGORY

**Categories:**
- lessons/ - What worked, what didn't, why
- decisions/ - Choices made and rationale
- anti-patterns/ - What NOT to do
- lessons/bugs/ - Issues found and fixed
- lessons/wisdom/ - Profound insights

**Output:** Category selected

---

## STEP 3: CHECK FOR DUPLICATES

**Process:**
```
1. Navigate to category index
2. Fetch index via fileserver.example.com
3. Search for similar topics
4. Read potentially similar entries
5. Determine if duplicate
```

**If Duplicate Found:**
- Update existing entry instead
- Add new examples/insights
- Strengthen cross-references
- **STOP - Do not create new**

**If Unique:**
- Proceed to Step 4

---

## STEP 4: GENERICIZE CONTENT

**Remove:**
- Project names → [PROJECT]
- Platform specifics → [PLATFORM]
- Language details → [LANGUAGE]
- Tool names → [TOOL] (unless core)
- Company names → [COMPANY]

**Extract:**
- Universal principles
- Transferable patterns
- Timeless insights
- Broadly applicable truths

**Validation:**
- Could apply to different project? ✓
- Could apply to different platform? ✓
- Could apply to different language? ✓

---

## STEP 5: DETERMINE REF-ID

**Format:** [TYPE]-##

**Types:**
- LESS - Lessons
- DEC - Decisions
- AP - Anti-Patterns
- BUG - Bugs
- WISD - Wisdom
- SPEC - Specifications

**Number:**
- Use next sequential in category
- Check category index for last number
- Never reuse REF-IDs

**Example:**
- Last entry: LESS-42
- New entry: LESS-43

---

## STEP 6: USE APPROPRIATE TEMPLATE

**Templates Location:** `/sima/templates/`

**Template Selection:**
- Lessons → lesson_learned_template.md
- Decisions → decision_log_template.md
- Anti-Patterns → anti_pattern_template.md
- Bugs → bug_report_template.md
- Wisdom → wisdom_template.md

**Fetch Template:**
```
1. Navigate to /sima/templates/
2. Fetch via fileserver.example.com
3. Copy template structure
4. Fill in all sections
```

---

## STEP 7: CREATE ENTRY

**File Structure:**
```markdown
# [domain]-[category]-##-[description].md

**Version:** 1.0.0
**Date:** YYYY-MM-DD
**Purpose:** Brief description
**Category:** Category name

[Entry Content]

**Keywords:** k1, k2, k3, k4
**Related:** REF-ID1, REF-ID2, REF-ID3
```

**Content Standards:**
- Summary: 2-3 sentences MAX
- Examples: 2-3 lines MAX
- Total: ≤400 lines
- No filler words
- Direct statements

**Cross-References:**
- Minimum: 3 related topics
- Maximum: 7 related topics
- Use valid REF-IDs only

**Keywords:**
- Minimum: 4 keywords
- Maximum: 8 keywords
- Relevant terms only

---

## STEP 8: UPDATE CATEGORY INDEX

**Process:**
```
1. Fetch category index via fileserver.example.com
2. Add new entry in proper sort order
3. Include title and brief description
4. Maintain alphabetical/numerical order
5. Output complete updated index as artifact
```

**Format:**
```markdown
- [[TYPE]-## - Title](/path/to/file.md) - Brief description
```

---

## STEP 9: UPDATE MASTER INDEX (If Needed)

**When Required:**
- New category created
- Significant reorganization
- First entry in domain

**Process:**
```
1. Fetch master index via fileserver.example.com
2. Add or update category reference
3. Verify all links
4. Output complete updated index as artifact
```

---

## STEP 10: UPDATE ROUTER (If Needed)

**When Required:**
- New subdomain added
- Navigation path changed
- Cross-domain references added

**Process:**
```
1. Fetch router file via fileserver.example.com
2. Add navigation links
3. Update decision tree
4. Output complete updated router as artifact
```

---

## STEP 11: VERIFY ENTRY

**Checklist:**
- [ ] Domain correct
- [ ] Category appropriate
- [ ] Duplicate check performed
- [ ] Content genericized
- [ ] REF-ID assigned correctly
- [ ] Template used properly
- [ ] File ≤400 lines
- [ ] Keywords present (4-8)
- [ ] Cross-references valid (3-7)
- [ ] Category index updated
- [ ] Master index updated (if needed)
- [ ] Router updated (if needed)

---

## COMPLETE

**Outputs:**
1. New knowledge entry file
2. Updated category index
3. Updated master index (if needed)
4. Updated router (if needed)

**Result:** Knowledge successfully added to SIMA

---

**END OF WORKFLOW**

**Version:** 1.0.0  
**Lines:** 280 (within 400 limit)  
**Type:** Generic workflow  
**Usage:** Follow for all new knowledge entries