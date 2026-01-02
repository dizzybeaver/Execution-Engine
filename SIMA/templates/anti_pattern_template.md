# anti_pattern_template.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Template for documenting anti-patterns to avoid  
**Category:** Template

---

## TEMPLATE USAGE

This template provides structure for documenting patterns that should be avoided, explaining why they're problematic and what to do instead.

**Target:** AP-## entries in `/sima/generic/entries/anti-patterns/`

---

## TEMPLATE

```markdown
# AP-[NUMBER]-[Brief-Title].md

**Version:** 1.0.0  
**Date:** [YYYY-MM-DD]  
**Purpose:** [Brief description of the anti-pattern]  
**Category:** Anti-Patterns - [Subcategory]

---

## [ANTI-PATTERN NAME]

[One-sentence description of the anti-pattern]

---

## THE PATTERN

[Describe what people typically do that constitutes this anti-pattern]

[What does this look like in practice?]

[Why might someone be tempted to do this?]

---

## WHY IT'S WRONG

[Explain why this pattern causes problems]

**Root Cause:**
[What fundamental issue makes this problematic?]

**Consequences:**
- [Problem 1]
- [Problem 2]
- [Problem 3]

**Technical Impact:**
- Performance: [How it affects performance]
- Maintainability: [How it affects maintenance]
- Reliability: [How it affects reliability]
- Security: [How it affects security if applicable]

---

## EXAMPLE

### Bad Code (Anti-Pattern)
```[language]
[Code example showing the anti-pattern]
```

**Problems with this code:**
- [Issue 1]
- [Issue 2]
- [Issue 3]

---

## THE RIGHT WAY

[Describe the correct approach]

[What pattern should be used instead?]

[Why is this better?]

### Good Code (Correct Pattern)
```[language]
[Code example showing the correct approach]
```

**Benefits of this approach:**
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

---

## DETECTION

[How to identify this anti-pattern in existing code]

**Warning Signs:**
- [Sign 1]
- [Sign 2]
- [Sign 3]

**Search Patterns:**
```bash
[grep or search commands to find instances]
```

---

## MIGRATION

[How to fix existing code that uses this anti-pattern]

**Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Risks:**
- [Risk during migration 1]
- [Risk during migration 2]

**Testing:**
- [What to test after migration]
- [How to verify correctness]

---

## PREVENTION

[How to prevent this anti-pattern in new code]

**Code Review Checklist:**
- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]

**Automated Checks:**
```[language]
[Linter rules or automated checks]
```

**Best Practices:**
- [Practice 1]
- [Practice 2]

---

## EXCEPTIONS

[Are there legitimate cases where this pattern is acceptable?]

[If yes, describe the specific circumstances]

[If no, state "No exceptions - always wrong"]

---

## RELATED ANTI-PATTERNS

**Similar:**
- [AP-ID]: [How they're similar]

**Often Seen With:**
- [AP-ID]: [Why they appear together]

**Alternative Mistakes:**
- [AP-ID]: [How someone might make a different mistake]

---

**Keywords:** [keyword1], [keyword2], [keyword3], [keyword4]

**Related:** [TYPE-ID], [TYPE-ID], [TYPE-ID]

**Severity:** [Critical|High|Medium|Low]

**Version History:**
- v1.0.0 ([DATE]): Initial anti-pattern

---

**END OF FILE**
```

---

## INSTRUCTIONS

### Step 1: Copy Template
Copy the markdown template above

### Step 2: Fill Placeholders
Replace all `[PLACEHOLDER]` text

### Step 3: Document Impact
Be specific about consequences:
- Real problems, not theoretical
- Quantify impact when possible
- Explain root cause clearly

### Step 4: Provide Alternatives
Always show the right way:
- Concrete code examples
- Explain why it's better
- Show side-by-side comparison

### Step 5: Enable Prevention
Help others avoid the mistake:
- Detection methods
- Migration paths
- Prevention strategies

### Step 6: Verify Standards
- [ ] Header complete
- [ ] Clear code examples
- [ ] File ≤400 lines
- [ ] Keywords present

---

## GUIDELINES

### Pattern Description
- Show concrete example first
- Explain why it seems appealing
- Don't judge those who made mistake

### Why It's Wrong
- Focus on technical problems
- Quantify impact when possible
- Explain root cause
- List specific consequences

### Code Examples
- Show both bad and good
- Keep examples minimal (5-10 lines)
- Comment key differences
- Use realistic scenarios

### Severity Levels
- **Critical:** Can cause data loss, security breach, system failure
- **High:** Significant performance/reliability impact
- **Medium:** Maintenance burden, technical debt
- **Low:** Style issue, minor inefficiency

---

## EXAMPLE USAGE

**Input:** Using bare except clauses that catch all exceptions

**Output:** AP-14-Bare-Except.md documenting:
- Pattern: `except:` without exception type
- Why Wrong: Hides real errors, catches system exits, debugging nightmare
- Example: Bad code with bare except, good code with specific exceptions
- Right Way: Catch specific exceptions, let real errors propagate
- Detection: Search for `except:` in codebase
- Migration: Identify what exceptions actually occur, catch specifically
- Prevention: Code review, linter rules

---

## RELATED

- SPEC-FILE-STANDARDS.md
- SPEC-HEADERS.md
- SPEC-STRUCTURE.md

---

**END OF TEMPLATE**