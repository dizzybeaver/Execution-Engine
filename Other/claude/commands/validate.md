---
description: Performs full strict validation across the entire repository
---

You are performing full strict validation of the entire EE/SIMA repository.

Run comprehensive validation across all domains and components:

1. FILE STANDARDS VALIDATION:
   - File sizes ≤350 lines (check for files ≥400)
   - Complete headers (version/date/purpose/type)
   - UTF-8 encoding with LF line endings
   - Proper file naming conventions

2. SIMA STRUCTURE VALIDATION:
   - Index completeness and consistency
   - Router accuracy
   - REF-ID sequencing (no gaps, no duplicates)
   - Cross-reference resolution
   - Template compliance

3. EE ARCHITECTURE VALIDATION:
   - UG (Universal Gateway) as only entry point
   - Interface isolation (no imports outside package)
   - Factories as execution units
   - Proper routing: UG → Domain Gateway → Interface → Factory

4. RED FLAG DETECTION:
   - Code in chat (should be in artifacts)
   - File fragments (should be complete files)
   - Files >350 lines
   - Missing headers
   - Broken encoding
   - Bare except clauses
   - Incomplete error handling
   - Condensed topics
   - Wrong output formats

5. CONVERGENCE VALIDATION:
   - All domains pass validation
   - No unresolved violations
   - All tests pass

Return PASS or FAIL with:
- Detailed list of all violations found
- File locations and line numbers
- Severity levels (critical/warning/info)
- Recommended remediation steps
