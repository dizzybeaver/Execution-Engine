# gateway_pattern_template.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Template for documenting gateway patterns  
**Category:** Template

---

## TEMPLATE

```markdown
# GATE-[NUMBER]-[Brief-Title].md

**Version:** 1.0.0  
**Date:** [YYYY-MM-DD]  
**Purpose:** [Brief description of gateway pattern]  
**Category:** Gateway Patterns

---

## [PATTERN NAME]

[Brief description of what this gateway pattern does]

---

## PURPOSE

[Explain the problem this gateway pattern solves]

[What does it enable or prevent?]

[Why is a gateway needed for this?]

---

## THE PATTERN

[Describe the pattern in detail]

**Components:**
- Gateway function: [Purpose]
- Wrapper layer: [Purpose]
- Implementation: [Purpose]

**Flow:**
```
Caller → Gateway → Wrapper → Implementation → Result
```

---

## IMPLEMENTATION

```[language]
# Gateway function
def gateway_function(param1, param2):
    """Gateway entry point."""
    from wrapper_module import wrapper_function
    return wrapper_function(param1, param2)

# Wrapper function
def wrapper_function(param1, param2):
    """Wrapper with lazy import."""
    from implementation_module import implementation
    return implementation.execute(param1, param2)

# Implementation
class Implementation:
    def execute(self, param1, param2):
        """Core implementation."""
        # Business logic here
        return result
```

---

## USAGE

```[language]
# How to use from external code
from gateway import gateway_function

result = gateway_function(value1, value2)
```

**Rules:**
- Always call via gateway
- Never import implementation directly
- Lazy imports at each layer

---

## BENEFITS

- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

---

## ANTI-PATTERNS

### Direct Import
[What not to do and why]

```[language]
# WRONG - bypasses gateway
from implementation_module import implementation
```

---

## RELATED PATTERNS

- [GATE-ID]: [How they relate]
- [GATE-ID]: [How they complement]

---

**Keywords:** [keyword1], [keyword2], [keyword3]

**Related:** [TYPE-ID], [TYPE-ID]

**Version History:**
- v1.0.0 ([DATE]): Initial pattern

---

**END OF FILE**
```

---

## RELATED

- SPEC-FILE-STANDARDS.md

---

**END OF TEMPLATE**