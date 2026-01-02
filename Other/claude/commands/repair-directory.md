---
description: Repairs a specific directory within a domain
arguments:
  - name: path
    description: The domain/directory path to repair (e.g., authentication/services)
    required: true
---

You are running the strict repair cycle on a specific directory: {{path}}

Follow the strict repair cycle process:
1. ENFORCE SCAN: Enforcer agent scans {{path}} for violations
2. CODER REPAIR: Coder agent fixes all identified violations
3. ENFORCE VALIDATE: Enforcer agent validates all repairs
4. CONVERGENCE LOOP: Repeat steps 2-3 until PASS is achieved

Repair scope for {{path}}:
- All files in the directory
- All subdirectories
- Related tests and documentation

Checks:
- SIMA file standards (≤350 lines, headers, encoding)
- EE architecture rules
- Cross-reference integrity
- REF-ID correctness

Continue the convergence loop until:
- Enforcer returns PASS for {{path}}
- All red flags cleared
- All standards met

Report final status for {{path}}.
