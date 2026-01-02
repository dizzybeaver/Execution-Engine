# interface_catalog_template.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Template for documenting interface catalogs  
**Category:** Template

---

## TEMPLATE

```markdown
# INT-[NUMBER]-[Name]-Interface.md

**Version:** 1.0.0  
**Date:** [YYYY-MM-DD]  
**Purpose:** [Brief description of interface]  
**Category:** Interfaces

---

## [INTERFACE NAME]

[Brief description of what this interface provides]

---

## PURPOSE

[Explain what problem this interface solves]

[What capabilities does it provide?]

[Who uses this interface?]

---

## FUNCTIONS

### function_1
**Purpose:** [What it does]  
**Params:**
- param1 (type): [Description]
- param2 (type): [Description]

**Returns:** [Return type and description]  
**Example:**
```[language]
result = function_1(value1, value2)
```

### function_2
**Purpose:** [What it does]  
**Params:**
- param1 (type): [Description]

**Returns:** [Return type and description]  
**Example:**
```[language]
result = function_2(value1)
```

[Additional functions...]

---

## USAGE PATTERNS

### Pattern 1: [Name]
[When and how to use]

```[language]
[Example code]
```

### Pattern 2: [Name]
[When and how to use]

```[language]
[Example code]
```

---

## IMPLEMENTATION

**Location:** [File path]  
**Pattern:** [Implementation pattern used]

```[language]
# Core structure
[Skeleton showing implementation approach]
```

---

## RELATED INTERFACES

- [INT-ID]: [How they relate]
- [INT-ID]: [How they interact]

---

**Keywords:** [keyword1], [keyword2], [keyword3]

**Related:** [TYPE-ID], [TYPE-ID]

**Version History:**
- v1.0.0 ([DATE]): Initial interface

---

**END OF FILE**
```

---

## RELATED

- SPEC-FILE-STANDARDS.md
- SPEC-FUNCTION-DOCS.md

---

**END OF TEMPLATE**