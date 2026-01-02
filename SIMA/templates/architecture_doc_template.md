# architecture_doc_template.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Template for documenting architectural patterns  
**Category:** Template

---

## TEMPLATE

```markdown
# ARCH-[NAME]-[Brief-Title].md

**Version:** 1.0.0  
**Date:** [YYYY-MM-DD]  
**Purpose:** [Brief description of architecture]  
**Category:** Architecture

---

## [ARCHITECTURE NAME]

[Brief overview of the architecture pattern]

---

## CORE CONCEPT

[Explain the fundamental idea behind this architecture]

[What problem does it solve?]

[What makes it distinctive?]

---

## STRUCTURE

[Describe the architectural components]

**Components:**
- [Component 1]: [Purpose and role]
- [Component 2]: [Purpose and role]
- [Component 3]: [Purpose and role]

**Relationships:**
```
[ASCII diagram showing component relationships]

Example:
Component A → Component B → Component C
    |             |             |
    +-------------+-------------+
```

---

## KEY PRINCIPLES

[List the core principles this architecture follows]

### Principle 1: [Name]
[Explanation]

### Principle 2: [Name]
[Explanation]

### Principle 3: [Name]
[Explanation]

---

## BENEFITS

**Advantages:**
- [Benefit 1]: [Explanation]
- [Benefit 2]: [Explanation]
- [Benefit 3]: [Explanation]

**Solves:**
- [Problem 1 it addresses]
- [Problem 2 it addresses]

---

## TRADE-OFFS

**Costs:**
- [Trade-off 1]
- [Trade-off 2]

**When NOT to use:**
- [Scenario 1]
- [Scenario 2]

---

## IMPLEMENTATION

[How to implement this architecture]

**Setup Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**File Structure:**
```
/project/
├── [directory1]/
│   ├── [file1]
│   └── [file2]
├── [directory2]/
│   ├── [file1]
│   └── [file2]
```

---

## EXAMPLE

```[language]
[Code example showing the architecture]

[Component 1 example]

[Component 2 example]

[Component 3 example and interaction]
```

[Explanation of how components interact]

---

## PATTERNS

[Common patterns within this architecture]

### Pattern 1: [Name]
[When and how to use]

### Pattern 2: [Name]
[When and how to use]

---

## ANTI-PATTERNS

[Common mistakes to avoid]

### Anti-Pattern 1: [Name]
[What to avoid and why]

### Anti-Pattern 2: [Name]
[What to avoid and why]

---

## VALIDATION

[How to verify correct implementation]

**Checklist:**
- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]

**Tests:**
- [Test type 1]
- [Test type 2]

---

## RELATED ARCHITECTURES

**Similar:**
- [ARCH-NAME]: [How they relate]

**Combines with:**
- [ARCH-NAME]: [How they work together]

**Contrasts with:**
- [ARCH-NAME]: [Key differences]

---

**Keywords:** [keyword1], [keyword2], [keyword3], [keyword4]

**Related:** [TYPE-ID], [TYPE-ID], [TYPE-ID]

**Version History:**
- v1.0.0 ([DATE]): Initial architecture

---

**END OF FILE**
```

---

## INSTRUCTIONS

1. Copy template
2. Explain core concept clearly
3. Show structure with diagram
4. List benefits and trade-offs
5. Provide implementation guide
6. Include code examples
7. Document patterns and anti-patterns
8. Keep ≤400 lines

---

## GUIDELINES

**Core Concept:**
- What makes this architecture unique
- What problem it solves
- When to use it

**Structure:**
- Component diagram (ASCII)
- Clear responsibilities
- Relationships and dependencies

**Implementation:**
- Step-by-step guide
- File/directory structure
- Code examples

**Validation:**
- How to verify
- What to check
- Testing strategies

---

## RELATED

- SPEC-FILE-STANDARDS.md
- SPEC-STRUCTURE.md

---

**END OF TEMPLATE**