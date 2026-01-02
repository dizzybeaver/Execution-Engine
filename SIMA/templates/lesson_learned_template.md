# lesson_learned_template.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Template for creating lesson learned entries  
**Category:** Template

---

## TEMPLATE USAGE

This template provides structure for documenting lessons learned from experience, problems solved, or insights gained during development.

**Target:** LESS-## entries in `/sima/generic/entries/lessons/`

---

## TEMPLATE

```markdown
# LESS-[NUMBER]-[Brief-Title].md

**Version:** 1.0.0  
**Date:** [YYYY-MM-DD]  
**Purpose:** [Brief description of what this lesson teaches]  
**Category:** Lessons - [Subcategory]

---

## [LESSON TITLE]

[Brief overview of the lesson in 1-2 sentences]

---

## CONTEXT

[Describe the situation or problem that led to this lesson]

[What were you trying to accomplish?]

[What constraints or requirements existed?]

---

## PROBLEM/CHALLENGE

[Describe the specific problem or challenge encountered]

[What went wrong or what obstacle was faced?]

[Why was this problematic?]

---

## DISCOVERY/SOLUTION

[Describe how the insight was discovered or the solution found]

[What approach was taken?]

[What worked and what didn't?]

---

## KEY INSIGHT

[State the core lesson learned in clear, actionable terms]

[What is the universal principle?]

[Why does this matter?]

---

## APPLICATION

[Describe when and how to apply this lesson]

[What situations does this apply to?]

[How can others benefit from this knowledge?]

---

## EXAMPLE

[Provide a concrete code or scenario example]

```[language]
[Code demonstrating the lesson]
```

[Explain the example briefly]

---

## IMPACT

[Quantify the impact if possible]

**Metrics:**
- Performance: [improvement achieved]
- Time saved: [time savings]
- Errors avoided: [error reduction]
- Other benefits: [list]

---

## PREVENTION

[How to avoid the original problem in the future]

[What practices prevent this issue?]

[What checks or validations help?]

---

## RELATED LESSONS

**See also:**
- [REF-ID]: [Brief description]
- [REF-ID]: [Brief description]

**Contrasts with:**
- [REF-ID]: [How this differs]

---

**Keywords:** [keyword1], [keyword2], [keyword3], [keyword4]

**Related:** [TYPE-ID], [TYPE-ID], [TYPE-ID]

**Version History:**
- v1.0.0 ([DATE]): Initial lesson

---

**END OF FILE**
```

---

## INSTRUCTIONS

### Step 1: Copy Template
Copy the markdown template above

### Step 2: Fill Placeholders
Replace all `[PLACEHOLDER]` text with actual content:
- `[NUMBER]`: Sequential LESS number (01, 02, etc.)
- `[Brief-Title]`: Short descriptive title
- `[YYYY-MM-DD]`: Current date
- `[Subcategory]`: Lesson category (operations, architecture, etc.)
- `[language]`: Programming language for code examples

### Step 3: Write Content
Fill each section with relevant content:
- Keep descriptions brief and focused
- Use concrete examples
- Quantify impact when possible
- Cross-reference related entries

### Step 4: Verify Standards
Check compliance:
- [ ] Header complete (filename, version, date, purpose, category)
- [ ] All sections filled
- [ ] File ≤400 lines
- [ ] UTF-8 encoding, LF line endings
- [ ] Code blocks have language specified
- [ ] Keywords present (4-8)
- [ ] Related entries linked

### Step 5: Save File
Save as: `LESS-[NUMBER]-[Brief-Title].md`
Location: `/sima/generic/entries/lessons/[subcategory]/`

---

## GUIDELINES

### Content Quality
- **Be specific:** Concrete examples over vague statements
- **Be brief:** Every word must add value
- **Be actionable:** Readers should know what to do
- **Be measurable:** Quantify impact when possible

### Section Lengths
- Context: 2-3 sentences
- Problem: 2-3 sentences
- Discovery: 3-5 sentences
- Key Insight: 1-2 sentences (critical)
- Application: 2-3 sentences
- Example: 3-10 lines of code + brief explanation
- Impact: Bulleted metrics
- Prevention: 2-3 sentences

### Tone
- Direct and professional
- Focus on facts, not emotions
- Share insights, not blame
- Help others learn

---

## EXAMPLE USAGE

**Input:** Discovered that reading complete files before modifying prevents errors

**Output:** LESS-01-Read-Complete-Files.md documenting:
- Context: Modifying files without full understanding
- Problem: Incomplete changes, broken references
- Discovery: Reading entire file first prevents mistakes
- Key Insight: Complete state understanding essential
- Application: Always fetch and read full file before modifying
- Example: Code showing fetch → read → modify workflow
- Impact: 90% reduction in broken references
- Prevention: Make file reading mandatory first step

---

## RELATED

- SPEC-FILE-STANDARDS.md
- SPEC-HEADERS.md
- SPEC-LINE-LIMITS.md
- SPEC-STRUCTURE.md

---

**END OF TEMPLATE**