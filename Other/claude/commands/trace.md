---
description: Traces violations, regressions, or rule failures
arguments:
  - name: path
    description: The file, directory, or issue to trace
    required: true
---

You are tracing the issue at: {{path}}

Perform systematic trace:

1. IDENTIFY ISSUE:
   - What violation/regression/failure occurred
   - When it was introduced
   - Current status

2. TRACE EXECUTION PATH:
   - For UG routing: trace route → domain gateway → interface → factory
   - For violations: trace origin → propagation → impact
   - For bugs: trace symptom → root cause → fix history

3. ANALYZE ROOT CAUSE:
   - Why the issue occurred
   - What rules were violated
   - Contributing factors

4. TRACE DEPENDENCIES:
   - What depends on {{path}}
   - What {{path}} depends on
   - Cascade effects

5. REVIEW HISTORY:
   - Related BUG-## entries
   - Related DEC-## entries
   - Previous fixes
   - Regression history

6. GENERATE REPORT:
   - Complete trace with timeline
   - Root cause analysis
   - Impact assessment
   - Recommended actions

Create or update relevant BUG-## or LESS-## entries.
