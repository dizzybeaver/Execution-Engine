---
description: Applies EE 2.1 upgrade patterns across the entire repository
---

You are upgrading the entire EE repository to EE 2.1 standards.

Apply EE 2.1 upgrade patterns across all domains:

1. APPLY EE 2.1 PATTERNS:
   - Modern error handling (no bare except, proper exception types)
   - Clean typing and interfaces
   - Proper async/await patterns
   - Modern Python/TypeScript patterns
   - UG-ISP compliance

2. REMOVE LEGACY CODE:
   - Old error handling patterns
   - Deprecated functions
   - Legacy architectural patterns
   - Outdated imports and dependencies

3. ARCHITECTURE ALIGNMENT:
   - Ensure UG is only entry point
   - Interface isolation enforced
   - Factories as execution units
   - Proper routing through domain gateways

4. UPDATE HEADERS:
   - Ensure all files have current version
   - Update date stamps
   - Verify type specifications

5. SPLIT LARGE FILES:
   - Files ≥350 lines must be split
   - Never allow files ≥400 lines
   - Maintain logical cohesion

6. VALIDATE AFTER UPGRADE:
   - Run full validation
   - Check for red flags
   - Verify all tests pass
   - Ensure convergence

Convergence loop:
- If validation FAILS, repair and revalidate
- Continue until PASS achieved

Report upgrade status with convergence count.
