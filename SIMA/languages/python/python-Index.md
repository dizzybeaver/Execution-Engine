# Python Language Knowledge Base Index

**Version:** 1.0.0  
**Date:** 2025-12-31  
**Purpose:** Master index of all Python knowledge items in SIMA

## By Category

### Patterns
| REF-ID | Title | Description |
|--------|-------|-------------|
| PAT-PY-01 | EAFP | Easier to Ask for Forgiveness than Permission pattern |
| PAT-PY-02 | DRY | Don't Repeat Yourself principle implementation |
| PAT-PY-03 | Comprehensions | List, dict, and set comprehensions best practices |
| PAT-PY-04 | Decorators | Decorator patterns for code enhancement |
| PAT-PY-05 | Context Managers | Resource management with context managers |
| PAT-PY-06 | Duck Typing | Pythonic interface implementation |
| PAT-PY-07 | Magic Methods | Special methods for custom behavior |
| GATE-PY-UG-01 | UG Gateway Pattern | Universal Gateway implementation pattern in Python |
| GATE-PY-UG-02 | UG Route Dispatch | Route-based execution pattern for UGS in Python |

### Anti-patterns
| REF-ID | Title | Description |
|--------|-------|-------------|
| AP-PY-01 | Global Mutation | Avoiding global state mutation |
| AP-PY-02 | Deep Inheritance | Deep inheritance hierarchies problems |
| AP-PY-03 | Nested Functions | Overly nested function structures |
| AP-PY-04 | String Concatenation | Inefficient string building |
| AP-PY-05 | Import Star | Wildcard import dangers |
| AP-PY-06 | Bare Excepts | Catching all exceptions properly |
| AP-PY-07 | Mutable Default Args | Mutable default argument pitfalls |

### Decisions
| REF-ID | Title | Description |
|--------|-------|-------------|
| DEC-PY-01 | Async vs Threading | Framework for choosing async vs threading |
| DEC-PY-02 | Framework Choice | Web framework selection criteria |
| DEC-PY-03 | Type Hints | Type annotation strategy and level |
| DEC-PY-04 | Testing Strategy | Testing framework and approach decisions |
| DEC-PY-05 | Dependency Management | Package management and dependency decisions |
| DEC-PY-06 | Virtual Environments | Environment isolation strategy |
| DEC-PY-UG-01 | UG Execution Pattern | Universal Gateway execution integration for Python |
| DEC-PY-UG-02 | UG Interface Implementation | Interface isolation patterns for UGS in Python |

### Lessons
| REF-ID | Title | Description |
|--------|-------|-------------|
| LESS-PY-01 | Metaclass Gotchas | Complex metaclass behaviors and alternatives |
| LESS-PY-02 | GIL Implications | Global Interpreter Lock performance impact |
| LESS-PY-03 | Memory Management | Python memory usage patterns and leaks |
| LESS-PY-04 | C Extensions | When and how to use C extensions |
| LESS-PY-05 | Unicode Handling | Unicode/bytes challenges in Python 3 |
| LESS-PY-UG-01 | UG Factory Pattern | Implementing factory pattern with Universal Gateway integration |

### Core
| REF-ID | Title | Description |
|--------|-------|-------------|
| CR-PY-01 | Decorators | Core decorator concepts and implementation |
| CR-PY-02 | Context Managers | Understanding `with` statements |
| CR-PY-03 | Generators | Iterator patterns and generator expressions |
| CR-PY-04 | Metaclasses | Class creation and metaclass programming |
| CR-PY-05 | Descriptors | Attribute access protocols |

### Workflows
| REF-ID | Title | Description |
|--------|-------|-------------|
| WF-PY-01 | Testing Unit | Unit testing workflow and best practices |
| WF-PY-02 | Integration | Integration testing approach |
| WF-PY-03 | Deployment | Python application deployment workflow |
| WF-PY-04 | Code Quality | Code review and quality assurance process |
| WF-PY-05 | Performance | Performance optimization workflow |

## By Complexity Level

### Beginner (1-50)
- CR-PY-01, CR-PY-02, CR-PY-03
- PAT-PY-01, PAT-PY-03
- AP-PY-04, AP-PY-07
- DEC-PY-06

### Intermediate (51-150)
- PAT-PY-02, PAT-PY-04, PAT-PY-05, PAT-PY-06, PAT-PY-07
- AP-PY-01, AP-PY-02, AP-PY-03, AP-PY-05, AP-PY-06
- DEC-PY-01, DEC-PY-02, DEC-PY-03
- LESS-PY-01, LESS-PY-05
- WF-PY-01, WF-PY-05

### Advanced (151+)
- CR-PY-04, CR-PY-05
- DEC-PY-04, DEC-PY-05
- LESS-PY-02, LESS-PY-03, LESS-PY-04
- WF-PY-02, WF-PY-03, WF-PY-04

## By Python Version

### Python 3.6+
- All patterns and anti-patterns
- DEC-PY-03 (Type Hints)
- CR-PY-01, CR-PY-02, CR-PY-03

### Python 3.8+
- PAT-PY-06 (Walrus operator patterns)
- DEC-PY-01 (Async improvements)

### Python 3.10+
- Pattern matching (future PAT-PY-08)
- Structural pattern matching (future PAT-PY-09)

## Search Index

### By Topic
- **Async/Concurrent**: DEC-PY-01, DEC-PY-UG-01, WF-PY-05
- **Testing**: WF-PY-01, WF-PY-02
- **Performance**: LESS-PY-02, LESS-PY-03, WF-PY-05
- **Web Development**: DEC-PY-02, WF-PY-03
- **Data Science**: PAT-PY-03, CR-PY-03
- **OOP**: CR-PY-04, CR-PY-05, PAT-PY-06
- **API Design**: PAT-PY-01, AP-PY-01
- **Universal Gateway**: DEC-PY-UG-01, DEC-PY-UG-02, GATE-PY-UG-01, GATE-PY-UG-02, LESS-PY-UG-01
- **Architecture**: DEC-PY-UG-01, DEC-PY-UG-02, GATE-PY-UG-01, GATE-PY-UG-01

### By Problem Type
- **Code Quality**: PAT-PY-02, AP-PY-01-07, WF-PY-04
- **Performance**: LESS-PY-02-03, WF-PY-05
- **Maintainability**: DEC-PY-03, DEC-PY-06
- **Debugging**: LESS-PY-01, LESS-PY-04
- **Deployment**: WF-PY-03

## Statistics

- Total Knowledge Items: 36
- Patterns: 9 (25%)
- Anti-patterns: 7 (19%)
- Decisions: 8 (22%)
- Lessons: 6 (17%)
- Core: 5 (14%)
- Workflows: 5 (14%)

## Last Updated

- Categories: 6/6 completed
- REF-IDs: 36/100 allocated
- Coverage: Beginner to Advanced levels
- Python versions: 3.6+ to 3.10+