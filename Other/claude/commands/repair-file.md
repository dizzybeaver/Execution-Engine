---
description: Repairs a single file
arguments:
  - name: path
    description: The file path to repair (e.g., EE/src/authentication/interfaces/user-auth.ts)
    required: true
---

You are running a targeted repair on a single file: {{path}}

Repair process:
1. FETCH: Coder agent fetches the current file
2. ANALYZE: Identify violations and issues
3. REPAIR: Apply targeted fixes
4. VALIDATE: Enforcer agent validates the repair

Check for:
- File size ≤350 lines (split if ≥350, never ≥400)
- Complete file header (version/date/purpose/type)
- UTF-8 encoding with LF line endings
- SIMA naming conventions
- Cross-references resolve
- REF-IDs if applicable
- EE architecture compliance

Apply change markers:
- # ADDED: for new code
- # MODIFIED: for changed code
- # FIXED: for bug fixes
- # REMOVED: for deleted code (with explanation)

Validate the repaired file:
- All violations resolved
- No new violations introduced
- File standards met
- Tests pass if applicable

Report repair status for {{path}} with changes summary.
