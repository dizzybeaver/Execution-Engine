---
description: Repairs REF-ID inconsistencies
---

You are repairing REF-ID inconsistencies across SIMA.

1. SCAN ALL REF-IDs:
   - All LESS-## entries
   - All DEC-## entries
   - All AP-## entries
   - All BUG-## entries
   - All WISD-## entries
   - All SPEC-## entries
   - All ARCH-## entries
   - All GATE-## entries
   - All INT-## entries

2. DETECT ISSUES:
   - Duplicate REF-IDs
   - Gaps in sequences
   - Invalid REF-ID formats
   - Broken references

3. REPAIR REF-IDs:
   - Reassign duplicate REF-IDs (use next available)
   - Document gaps (or fill if appropriate)
   - Fix invalid formats
   - Update all references to changed REF-IDs

4. UPDATE CROSS-REFERENCES:
   - Update indexes
   - Update routers
   - Update inline references
   - Update related entries

5. VALIDATE:
   - Verify no duplicates
   - Verify all references resolve
   - Check sequences

6. DOCUMENT:
   - Create record of REF-ID changes
   - Update change log

Report repairs with mapping of old to new REF-IDs.
