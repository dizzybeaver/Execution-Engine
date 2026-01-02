---
description: Runs the full CI pipeline in strict mode
---

You are running the full CI pipeline in strict mode.

Execute CI pipeline in sequence:

1. STATIC ANALYSIS:
   - Run all linters and type checkers
   - Check file standards
   - Verify encoding
   - Scan for security issues

2. REPAIR CYCLE:
   - Run full repair cycle on all violations found
   - Convergence loop until PASS
   - Track repairs made

3. VALIDATION:
   - Full repository validation
   - SIMA structure validation
   - Architecture validation
   - Return PASS/FAIL

4. CONVERGENCE CHECK:
   - Domain-by-domain validation
   - Ensure all domains PASS
   - Check for regressions

5. REPORT:
   - CI status (PASS/FAIL)
   - Violations found and fixed
   - Convergence count
   - Remaining issues
   - Execution time

CI must PASS before allowing merge or deployment.
