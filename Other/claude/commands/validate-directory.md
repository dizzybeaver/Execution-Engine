---
description: Validates a specific directory
arguments:
  - name: path
    description: The directory path to validate (e.g., authentication/services)
    required: true
---

You are performing strict validation of directory: {{path}}

Validate the directory:

1. FILE STANDARDS:
   - All files ≤350 lines
   - Complete headers
   - UTF-8 with LF encoding
   - Proper naming

2. STRUCTURE:
   - Proper directory organization
   - Files in correct locations
   - No misplaced files

3. CROSS-REFERENCES:
   - All references resolve
   - No broken links
   - Proper imports

4. RED FLAGS:
   - Check for all red flag conditions

Return PASS or FAIL with detailed findings.
