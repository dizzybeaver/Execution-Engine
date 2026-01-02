---
description: Validates a specific EE domain
arguments:
  - name: domain
    description: The EE domain to validate (e.g., authentication, authorization, gateway)
    required: true
---

You are performing strict validation of the EE domain: {{domain}}

Validate the {{domain}} domain:

1. FILE STANDARDS:
   - All files ≤350 lines
   - Complete headers on all files
   - UTF-8 with LF encoding
   - Proper naming

2. EE ARCHITECTURE:
   - UG compliance for all operations
   - Interface isolation maintained
   - Factories as execution units
   - Proper routing patterns

3. DOMAIN-SPECIFIC:
   - Interfaces defined correctly
   - Factories implement interfaces
   - Domain gateway routes properly
   - Tests cover domain functionality

4. CROSS-REFERENCES:
   - All internal references resolve
   - No circular dependencies
   - Proper imports

5. RED FLAGS:
   - Check for all red flag conditions

Return PASS or FAIL with:
- List of violations in {{domain}}
- File locations
- Remediation steps
