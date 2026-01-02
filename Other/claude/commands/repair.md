---
description: Runs the full strict repair cycle across the entire repository
---

You are running the full strict repair cycle for the entire EE/SIMA repository.

Follow the strict repair cycle process:
1. ENFORCE SCAN: Enforcer agent scans entire repository for violations
2. CODER REPAIR: Coder agent fixes all identified violations
3. ENFORCE VALIDATE: Enforcer agent validates all repairs
4. CONVERGENCE LOOP: Repeat steps 2-3 until PASS is achieved

Repair scope:
- All EE domains (gateway, authentication, authorization, etc.)
- All SIMA knowledge entries
- All configuration files
- All test files

Red flag checks:
- File sizes ≤350 lines (never ≥400)
- All file headers complete (version/date/purpose/type)
- UTF-8 encoding with LF line endings
- No bare except or incomplete error handling
- All cross-references resolve
- All REF-IDs sequential and unique

Continue the convergence loop until:
- Enforcer returns PASS for entire repository
- All red flags cleared
- All SIMA standards met
- All EE architecture rules satisfied

Report final status with convergence count.
