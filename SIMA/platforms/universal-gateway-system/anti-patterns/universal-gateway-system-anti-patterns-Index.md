# universal-gateway-system-anti-patterns-Index.md

**Version:** 1.0.0  
**Date:** 2025-12-31  
**Purpose:** Anti-patterns index for Universal Gateway System  
**Type:** Anti-Patterns Index

---

## OVERVIEW

**Category:** Anti-Patterns  
**Platform:** Universal Gateway System  
**Purpose:** Patterns to avoid in UGS implementations

---

## ANTI-PATTERNS

**Status:** Active (2 entries)

**REF-ID Prefix:** `AP-UGS-##`

### Current Entries

1. **[AP-UGS-01: Cross-Interface Imports](AP-UGS-01-cross-interface-imports.md)**
   - Importing from one interface into another
   - Creates tight coupling and breaks isolation
   - Use dependency injection instead

2. **[AP-UGS-02: Import Isolation Violation](AP-UGS-02-import-isolation-violation.md)**
   - Importing domain gateways, UG, or shared utilities
   - Breaks architecture boundaries
   - Generic description, no code examples

### Planned Topics

- Direct domain access
- Bypassing gateway
- Missing interface isolation
- Circular dependencies

---

## NAVIGATION

**Parent Index:** [universal-gateway-system-Index.md](../universal-gateway-system-Index.md)  
**Platform Root:** `/sima/platforms/universal-gateway-system/`

---

## MAINTENANCE

**Last Updated:** 2025-12-31  
**Update After:** Adding new anti-pattern entries

---

**END OF ANTI-PATTERNS INDEX**
