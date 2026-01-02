# generic-anti-patterns-Index.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Index of generic anti-pattern entries  
**Directory:** /sima/generic/anti-patterns/  
**Type:** Empty Index (Ready for Content)

---

## OVERVIEW

This directory contains universal anti-patterns applicable across all platforms, languages, and projects. Anti-patterns document what NOT to do and why.

**Status:** Active - 1 entry (stable and documented)
**Entry Format:** `AP-GEN-##-[description].md`
**Next ID:** AP-GEN-02

---

## CATEGORIES

When entries are added, they will be organized by:
- Critical mistakes
- Documentation errors
- Error handling mistakes
- Implementation issues
- Performance issues
- Process failures
- Quality issues
- Security vulnerabilities

---

## ENTRIES

### Current Entries

| REF-ID | Title | Difficulty | Lines | Description |
|--------|-------|-----------|-------|-------------|
| [AP-GEN-01](AP-GEN-01-if-elif-chains-in-interfaces.md) | If/Elif Chains in Interfaces | Critical | 60 | Don't use if-elif chains for routing; use DISPATCH instead. Performance impact: O(n) vs O(1) lookup. Applies to UG, REST APIs, command routers, etc. |

### Status
- Total Entries: 1/1 (100% populated)
- Average Lines: 60 (within 350 limit)
- Difficulty: Critical (performance and maintainability impact)
- Coverage: Anti-pattern applicable across all platforms and routing systems

1. Activate SIMA Learning Mode
2. Extract anti-pattern from experience
3. Genericize (remove project/platform specifics)
4. Create as `AP-GEN-##-[description].md`
5. Update this index

---

## RELATED

- **Template:** `/sima/templates/anti_pattern_template.md`
- **Specifications:** `/sima/generic/specifications/`
- **Standards:** `/sima/context/shared/File-Standards.md`

---

**END OF INDEX**

**Version:** 1.1.0
**Lines:** 65
**Status:** Active - 1 entry documented and stable