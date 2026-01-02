# Python Language Router

**Version:** 1.0.0  
**Date:** 2025-12-31  
**Purpose:** Navigation router for Python language knowledge base

## Directory Structure

```
/sima/languages/python/
├── README.md                  # Language overview and navigation guide
├── python-Index.md            # Main index of all Python knowledge items
├── python-Router.md           # This navigation file
├── patterns/                  # Python design patterns
│   ├── patterns-Index.md      # Index of all patterns
│   ├── EAFP.md               # Easier to Ask for Forgiveness than Permission
│   ├── DRY.md                # Don't Repeat Yourself principle
│   └── ...
├── anti-patterns/            # Python anti-patterns
│   ├── anti-patterns-Index.md # Index of all anti-patterns
│   ├── global-mutation.md     # Avoiding global state mutation
│   ├── deep-inheritance.md   # Deep inheritance hierarchies
│   └── ...
├── decisions/                # Python-related decisions
│   ├── decisions-Index.md     # Index of all decisions
│   ├── async-vs-threading.md  # Async vs threading decision framework
│   ├── framework-choice.md    # Web framework selection
│   └── ...
├── lessons/                  # Python lessons learned
│   ├── lessons-Index.md       # Index of all lessons
│   ├── metaclass-gotchas.md  # Metaclass complexities
│   ├── gil-implications.md   # GIL performance implications
│   └── ...
├── core/                     # Core Python concepts
│   ├── core-Index.md          # Index of core concepts
│   ├── decorators.md          # Decorator patterns
│   ├── context-managers.md   # Context managers
│   └── ...
└── workflows/                # Python workflows
    ├── workflows-Index.md    # Index of all workflows
    ├── testing.md            # Testing workflow
    ├── deployment.md         # Deployment workflow
    └── ...
```

## Navigation Guide

### For Beginners
1. Start with [core/](core/) to understand Python fundamentals
2. Review [lessons/](lessons/) to avoid common pitfalls
3. Learn basic [patterns/](patterns/) for clean code

### For Intermediate Developers
1. Study [patterns/](patterns/) for advanced Pythonic practices
2. Understand [decisions/](decisions/) for technical choices
3. Explore [workflows/](workflows/) for development processes

### For Senior Developers
1. Review [anti-patterns/](anti-patterns/) for code quality
2. Update [decisions/](decisions/) based on new practices
3. Document new lessons in [lessons/](lessons/)

## Search Keywords

Use these keywords to find relevant content:
- `pattern` - Design patterns and best practices
- `anti-pattern` - Common mistakes and how to avoid them
- `decision` - Technical decision frameworks
- `lesson` - Real-world experience summaries
- `core` - Fundamental concepts
- `workflow` - Development processes

## REF-ID Format

- Patterns: `PAT-PY-01`, `PAT-PY-02`, etc.
- Anti-patterns: `AP-PY-01`, `AP-PY-02`, etc.
- Decisions: `DEC-PY-01`, `DEC-PY-02`, etc.
- Lessons: `LESS-PY-01`, `LESS-PY-02`, etc.
- Core: `CR-PY-01`, `CR-PY-02`, etc.
- Workflows: `WF-PY-01`, `WF-PY-02`, etc.

## Adding New Content

1. Choose appropriate category directory
2. Create index file if it doesn't exist
3. Add new item with proper REF-ID
4. Update corresponding index file
5. Ensure file meets 350-line limit
6. Include version, date, and purpose headers