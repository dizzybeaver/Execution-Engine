---
description: Validates a single file
arguments:
  - name: path
    description: The file path to validate
    required: true
---

You are performing strict validation of file: {{path}}

Validate the file:

1. FILE SIZE:
   - Must be ≤350 lines
   - FAIL if ≥400 lines
   - WARNING if >350 lines

2. FILE HEADER:
   - Version present
   - Date present
   - Purpose clear
   - Type specified

3. ENCODING:
   - UTF-8 encoding
   - LF line endings (no CRLF)

4. NAMING:
   - Follows SIMA naming conventions
   - Matches file type standards

5. CONTENT:
   - No red flags (bare except, incomplete error handling, etc.)
   - Proper structure
   - Clear documentation

6. CROSS-REFERENCES:
   - All references resolve
   - REF-IDs correct if used

Return PASS or FAIL with specific issues listed.
