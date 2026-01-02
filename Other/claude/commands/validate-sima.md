---
description: Validates SIMA structure, indexes, routers, and REF-IDs
---

You are performing comprehensive SIMA structure validation.

Run SIMA Workflow-06 Verify Structure:

1. INDEX VALIDATION:
   - Master index completeness
   - Domain indexes match actual structure
   - All entries indexed
   - No orphaned entries

2. ROUTER VALIDATION:
   - All routers complete
   - Routing entries accurate
   - No broken routes
   - Routers synchronized with indexes

3. REF-ID VALIDATION:
   - Sequential numbering (no gaps)
   - No duplicate REF-IDs
   - Proper prefixes (LESS/DEC/AP/BUG/WISD/SPEC/ARCH/GATE/INT)
   - All REF-IDs resolve to valid entries

4. CROSS-REFERENCE VALIDATION:
   - All internal links resolve
   - No broken references
   - Bidirectional links consistent

5. STRUCTURE VALIDATION:
   - Directory structure matches SIMA standards
   - Files in correct locations
   - Templates intact
   - Context files complete

6. ENCODING VALIDATION:
   - All files UTF-8
   - All files use LF line endings

Return PASS or FAIL with:
- List of structural issues
- Index/router inconsistencies
- REF-ID problems
- Broken references
- Encoding violations
