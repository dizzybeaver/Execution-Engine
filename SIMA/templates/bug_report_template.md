# bug_report_template.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Template for documenting bugs and their fixes  
**Category:** Template

---

## TEMPLATE

```markdown
# BUG-[NUMBER]-[Brief-Title].md

**Version:** 1.0.0  
**Date:** [YYYY-MM-DD]  
**Purpose:** [Brief description of the bug]  
**Category:** Bugs - [Subcategory]

---

## [BUG TITLE]

[One-sentence description of the bug]

---

## SYMPTOM

[What was observed? What behavior indicated a bug?]

[How did the bug manifest?]

[What error messages appeared?]

---

## REPRODUCTION

**Steps to reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected behavior:**
[What should have happened]

**Actual behavior:**
[What actually happened]

**Frequency:**
[Always|Sometimes|Rarely] - [percentage if known]

---

## IMPACT

**Severity:** [Critical|High|Medium|Low]

**Affected:**
- [What systems/components were affected]
- [What users/scenarios were impacted]

**Metrics:**
- Performance: [degradation if applicable]
- Errors: [error rate or count]
- Users: [number affected]
- Cost: [financial impact if applicable]

---

## ROOT CAUSE

[Explain what actually caused the bug]

[What was the underlying technical issue?]

[Why did this problem exist?]

**Location:** [File and line number where bug existed]

---

## EXAMPLE

```[language]
# BEFORE (buggy code)
[Code showing the bug]
```

**Why this failed:**
[Explanation of what was wrong]

---

## FIX

[Describe the solution]

[What was changed?]

[Why does this fix work?]

```[language]
# AFTER (fixed code)
[Code showing the fix]
```

**Key changes:**
- [Change 1]
- [Change 2]

---

## VALIDATION

[How was the fix verified?]

**Tests:**
- [Test 1]
- [Test 2]

**Verification:**
- [Method of verification]
- [Results confirming fix]

---

## PREVENTION

[How to prevent this type of bug in the future]

**Code patterns to use:**
[Patterns that prevent this]

**Checks to add:**
- [Validation 1]
- [Validation 2]

**Review focus:**
[What to look for in code review]

---

**Keywords:** [keyword1], [keyword2], [keyword3], [keyword4]

**Related:** [TYPE-ID], [TYPE-ID], [TYPE-ID]

**Version History:**
- v1.0.0 ([DATE]): Initial bug report

---

**END OF FILE**
```

---

## INSTRUCTIONS

1. Copy template
2. Fill all sections
3. Include code examples
4. Explain root cause clearly
5. Document prevention measures
6. Verify ≤400 lines

---

## RELATED

- SPEC-FILE-STANDARDS.md
- SPEC-HEADERS.md

---

**END OF TEMPLATE**