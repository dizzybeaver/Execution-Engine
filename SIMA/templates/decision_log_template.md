# decision_log_template.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Template for documenting architectural and technical decisions  
**Category:** Template

---

## TEMPLATE USAGE

This template provides structure for documenting significant decisions made during project development, including context, alternatives, rationale, and outcomes.

**Target:** DEC-## entries in `/sima/generic/entries/decisions/`

---

## TEMPLATE

```markdown
# DEC-[NUMBER]-[Brief-Title].md

**Version:** 1.0.0  
**Date:** [YYYY-MM-DD]  
**Purpose:** [Brief description of the decision]  
**Category:** Decisions - [Subcategory]

---

## [DECISION TITLE]

[Brief statement of the decision made]

---

## CONTEXT

[Describe the situation requiring a decision]

[What problem needed solving?]

[What constraints existed?]

[What triggered the need for this decision?]

---

## DECISION

[State the decision clearly and explicitly]

[What was chosen?]

[What specific approach/technology/pattern was selected?]

---

## ALTERNATIVES CONSIDERED

### Option 1: [Name]
**Description:** [What this option involved]  
**Pros:**
- [Advantage 1]
- [Advantage 2]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

### Option 2: [Name]
**Description:** [What this option involved]  
**Pros:**
- [Advantage 1]
- [Advantage 2]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

### Option 3: [Name]
**Description:** [What this option involved]  
**Pros:**
- [Advantage 1]
- [Advantage 2]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

---

## RATIONALE

[Explain why the chosen option was selected]

[What factors were most important?]

[How did constraints influence the decision?]

[What trade-offs were accepted?]

---

## CONSEQUENCES

### Positive
- [Expected benefit 1]
- [Expected benefit 2]
- [Expected benefit 3]

### Negative
- [Expected drawback 1]
- [Expected drawback 2]

### Risks
- [Risk 1 and mitigation]
- [Risk 2 and mitigation]

---

## IMPLEMENTATION

[Describe how to implement this decision]

[What changes are required?]

[What steps should be taken?]

---

## VALIDATION

[How to verify the decision was correct]

[What metrics indicate success?]

[What would indicate the decision should be reconsidered?]

---

## OUTCOME

[After implementation, document actual results]

**Metrics:**
- [Actual metric 1]
- [Actual metric 2]
- [Actual metric 3]

**Lessons:**
- [What worked well]
- [What didn't work as expected]
- [What was surprising]

[Update this section after sufficient time has passed]

---

## RELATED DECISIONS

**Builds on:**
- [DEC-ID]: [Brief description]

**Supersedes:**
- [DEC-ID]: [What this replaces]

**Related to:**
- [DEC-ID]: [How they're related]

---

**Keywords:** [keyword1], [keyword2], [keyword3], [keyword4]

**Related:** [TYPE-ID], [TYPE-ID], [TYPE-ID]

**Status:** [Active|Superseded|Under Review]

**Version History:**
- v1.1.0 ([DATE]): Added outcome results
- v1.0.0 ([DATE]): Initial decision

---

**END OF FILE**
```

---

## INSTRUCTIONS

### Step 1: Copy Template
Copy the markdown template above

### Step 2: Fill Placeholders
Replace all `[PLACEHOLDER]` text

### Step 3: Document Alternatives
List ALL alternatives seriously considered (minimum 2, typically 3-4)

### Step 4: Explain Rationale
Be explicit about why the decision was made:
- What factors were weighted most heavily?
- What constraints were binding?
- What trade-offs were acceptable?

### Step 5: Update Outcome
Return after implementation to document actual results

### Step 6: Verify Standards
- [ ] Header complete
- [ ] All alternatives documented
- [ ] Rationale clear and specific
- [ ] File ≤400 lines
- [ ] Keywords present

---

## GUIDELINES

### Decision Statement
- Clear and unambiguous
- Actionable (teams know what to do)
- Specific (not vague or general)

### Alternatives
- Be fair to rejected options
- Document genuine pros and cons
- Show you considered trade-offs seriously

### Rationale
- Focus on factors that tipped the scale
- Explain why pros outweighed cons
- Acknowledge accepted trade-offs
- Link to constraints and requirements

### Outcome
- Update after 1-3 months of use
- Be honest about what worked/didn't
- Quantify results where possible
- Document lessons learned

---

## EXAMPLE USAGE

**Input:** Decided to use gateway pattern instead of direct imports

**Output:** DEC-01-Gateway-Pattern.md documenting:
- Context: Need to manage dependencies and prevent circular imports
- Decision: All cross-interface communication via gateway
- Alternatives: Direct imports, service locator, dependency injection
- Rationale: Gateway provides centralization, lazy loading, clear boundaries
- Consequences: Extra indirection, but prevents circular imports
- Implementation: Create gateway.py, wrapper files, update all imports
- Outcome: 100% elimination of circular imports, slight overhead acceptable

---

## RELATED

- SPEC-FILE-STANDARDS.md
- SPEC-HEADERS.md
- SPEC-STRUCTURE.md

---

**END OF TEMPLATE**