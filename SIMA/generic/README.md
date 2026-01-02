# SIMA Generic Knowledge Base

Generic best practices and architecture decisions extracted from the EE codebase analysis. These entries are language-agnostic and framework-agnostic, focusing on universal principles.

## Structure

```
sima/generic/
├── lessons/           # Best practices and patterns
│   ├── LESS-GEN-01-dependency-injection.md
│   ├── LESS-GEN-02-factory-pattern.md
│   ├── LESS-GEN-03-descriptive-error-messages.md
│   └── LESS-GEN-04-exception-chaining.md
├── decisions/         # Architecture decisions
│   └── DEC-GEN-01-singleton-registry.md
└── README.md          # This file
```

## Knowledge Entries

### Lessons (Best Practices)

1. **LESS-GEN-01: Dependency Injection Pattern**
   - Inject dependencies rather than importing
   - Benefits: Testability, loose coupling, flexibility
   - 168 lines

2. **LESS-GEN-02: Factory Pattern for Execution Units**
   - Use factories to create and manage execution units
   - Benefits: Resource management, encapsulation, consistency
   - 236 lines

3. **LESS-GEN-03: Descriptive Error Messages**
   - Error messages with context, expected, received, options
   - Benefits: Self-debugging, faster development, better UX
   - 334 lines

4. **LESS-GEN-04: Exception Chaining**
   - Preserve root cause when re-raising exceptions
   - Benefits: Complete stack trace, root cause visibility
   - 325 lines

### Decisions (Architecture Choices)

1. **DEC-GEN-01: Singleton Registry Pattern**
   - Thread-safe singleton with double-check locking
   - Benefits: Single source of truth, thread safety
   - 263 lines

## File Standards

All SIMA files adhere to these standards:
- UTF-8 encoding
- LF line endings
- Maximum 350 lines per file
- Descriptive (no code examples in generic entries)
- Cross-references to related entries
- Language-agnostic principles

## Usage

These entries serve as:
- Generic best practices applicable to any language
- Architecture decision rationale
- Educational material for software design
- Reference for implementing similar patterns

## Cross-References

- **Python/EE Implementation**: EE codebase at `d:/Code/Project/EE/`
- **SIMA Structure**: `d:/Code/Project/sima/`
- **Reports**: `d:/Code/Project/reports/2025/December/31st/`

## Related Documentation

- EE Codebase Analysis Report (source)
- Universal Gateway Architecture Guide
- Project CLAUDE.md configuration

---

**Created**: 2025-12-31  
**Source**: EE Codebase Comprehensive Analysis  
**Status**: Active
