# Python Anti-patterns Index

**Version:** 1.0.0  
**Date:** 2025-12-31  
**Purpose:** Index of common Python anti-patterns and their solutions

## Anti-pattern List

| REF-ID | Title | Difficulty | Lines | Description |
|--------|-------|-----------|-------|-------------|
| AP-PY-01 | Global Mutation | Intermediate | 65 | Avoiding global state mutation |
| AP-PY-02 | Deep Inheritance | Advanced | 70 | Deep inheritance hierarchies problems |
| AP-PY-03 | Nested Functions | Intermediate | 55 | Overly nested function structures |
| AP-PY-04 | String Concatenation | Beginner | 45 | Inefficient string building |
| AP-PY-05 | Import Star | Beginner | 40 | Wildcard import dangers |
| AP-PY-06 | Bare Excepts | Beginner | 50 | Catching all exceptions properly |
| AP-PY-07 | Mutable Default Args | Intermediate | 60 | Mutable default argument pitfalls |
| **AP-PY-UG-01** | **Direct UG Instantiation** | **Critical** | **350** | **Never instantiate UniversalGateway in factories** |
| **AP-PY-UG-02** | **Bare Except Clauses** | **High** | **350** | **Never use bare except clauses in Python** |
| **AP-PY-UG-03** | **UG Bypass** | **Critical** | **350** | **Never bypass UniversalGateway for domain access** |

## Anti-pattern Categories

### Code Quality Anti-patterns (3)
- AP-PY-01 (Global Mutation)
- AP-PY-02 (Deep Inheritance)
- AP-PY-03 (Nested Functions)

### Performance Anti-patterns (2)
- AP-PY-04 (String Concatenation)
- AP-PY-07 (Mutable Default Args)

### Best Practice Violations (2)
- AP-PY-05 (Import Star)
- AP-PY-06 (Bare Excepts)

### UG-Specific Anti-patterns (3)
- **AP-PY-UG-01** (Direct UG Instantiation) - Critical architecture violation
- **AP-PY-UG-02** (Bare Except Clauses) - Error handling best practice
- **AP-PY-UG-03** (UG Bypass) - Architecture integrity violation

## Learning Path

### Beginner Anti-patterns (Critical to avoid first)
1. **AP-PY-04 - String Concatenation** (45 lines)
   - Performance impact and alternatives
   - Easy to fall into, easy to fix

2. **AP-PY-05 - Import Star** (40 lines)
   - Namespace pollution issues
   - Simple rule: never use `import *`

3. **AP-PY-06 - Bare Excepts** (50 lines)
   - Exception handling best practices
   - Crucial for debugging

### Intermediate Anti-patterns (More complex issues)
4. **AP-PY-03 - Nested Functions** (55 lines)
   - Readability and maintainability issues
   - Refactoring strategies

5. **AP-PY-07 - Mutable Default Args** (60 lines)
   - Unexpected behavior in functions
   - Common gotcha for Python developers

6. **AP-PY-01 - Global Mutation** (65 lines)
   - State management problems
   - Architectural implications

### Advanced Anti-patterns (System design issues)
7. **AP-PY-02 - Deep Inheritance** (70 lines)
   - Object design problems
   - Refactoring complex hierarchies

## Related Patterns

| Anti-pattern | Solution Pattern |
|-------------|-------------------|
| Global Mutation (AP-PY-01) | Context Managers (PAT-PY-05) |
| String Concatenation (AP-PY-04) | Comprehensions (PAT-PY-03) |
| Bare Excepts (AP-PY-06) | EAFP (PAT-PY-01) |
| Nested Functions (AP-PY-03) | Decorators (PAT-PY-04) |
| Mutable Default Args (AP-PY-07) | DRY (PAT-PY-02) |

## Detection and Prevention

### Automated Detection Tools
- **flake8**: Can detect many code smells
- **pylint**: Comprehensive code analysis
- **mypy**: Type-related anti-patterns
- **vulture**: Dead code detection

### Manual Code Review Checklist
- [ ] Are imports explicit and organized?
- [ ] Are exceptions specific and handled properly?
- [ ] Are default arguments immutable?
- [ ] Is state mutation localized?
- [ ] Are inheritance hierarchies shallow?
- [ ] Is string building efficient?
- [ ] Are functions appropriately nested?

## Implementation Status

- Total Anti-patterns: 10/10 (100%)
- Average Lines: 113 (within 350 limit)
- Difficulty Distribution:
  - Beginner: 3 anti-patterns
  - Intermediate: 3 anti-patterns
  - Advanced: 1 anti-pattern
  - UG-Specific: 3 anti-patterns (Critical)
- Coverage: Major Python anti-patterns covered + comprehensive UG-specific violations

## Severity Levels

### High Impact (Fix immediately)
- **AP-PY-UG-01** (Direct UG Instantiation) - Architecture violation, breaks singleton
- **AP-PY-UG-02** (Bare Except Clauses) - Makes debugging impossible
- AP-PY-05 (Import Star) - Namespace pollution
- AP-PY-06 (Bare Excepts) - Debugging nightmares
- AP-PY-04 (String Concatenation) - Performance issues

### Medium Impact (Fix in next iteration)
- AP-PY-07 (Mutable Default Args) - Logic errors
- AP-PY-01 (Global Mutation) - Maintenance issues

### Low Impact (Fix when refactoring)
- AP-PY-03 (Nested Functions) - Readability
- AP-PY-02 (Deep Inheritance) - Design issues