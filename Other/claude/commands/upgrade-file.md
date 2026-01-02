---
description: Upgrades a single file
arguments:
  - name: path
    description: The file path to upgrade
    required: true
---

You are upgrading file {{path}} to EE 2.1 standards.

Apply EE 2.1 upgrade:
1. Fetch current file
2. Apply modern patterns
3. Remove legacy code
4. Update header if needed
5. Validate result
6. Return PASS/FAIL

Report upgrade status for {{path}}.
