EE 2.1 Domain-by-Domain Convergence Tracker  
Version: 1.0.0  
Date: 2025-12-31  
Purpose: Define the domain-by-domain convergence tracking system required for the EE 2.1 upgrade.  
Type: Governance Document

1. Purpose of this tracker

This document defines the authoritative convergence tracking system for the EE 2.1 upgrade. It ensures that each of the 15 EE domains is upgraded, validated, repaired, and converged individually before the system can progress. No domain may be skipped, partially upgraded, or marked complete early.

The tracker prevents:
- Skipped domains  
- Partial upgrades  
- Hybrid legacy/new code  
- Silent regressions  
- Incomplete convergence  
- Architecture drift  
- SIMA drift  
- Directory drift  

2. List of EE domains

The EE 2.1 upgrade MUST track convergence for the following domains:

1. gateway  
2. routing  
3. interfaces  
4. factories  
5. serialization  
6. validation  
7. logging  
8. metrics  
9. configuration  
10. environment  
11. security  
12. storage  
13. transport  
14. orchestration  
15. utilities  

Each domain MUST converge independently.

3. Convergence requirements for each domain

A domain is considered converged only when:

- All legacy patterns are removed  
- All new EE 2.1 patterns are applied  
- All UG-ISP rules are satisfied  
- All AP-28 anti-patterns are eliminated  
- All factories follow execution-unit rules  
- All interfaces follow isolation rules  
- All gateways follow routing rules  
- All imports follow domain isolation rules  
- All files follow SIMA standards  
- All files follow naming conventions  
- All files follow encoding standards  
- All files are ≤350 lines  
- All directories follow structure rules  
- All SIMA entries are created  
- All indexes are updated  
- All routers are updated  
- All REF-IDs are correct  
- All scanner rules pass  
- All CI pipeline checks pass  
- Enforcer returns PASS  
- Coordinator Override approves  

4. Domain convergence workflow

The convergence workflow for each domain is:

Step 1 — Pre-Scan  
- Scanner identifies violations  
- Enforcer validates domain  
- Maintenance verifies structure  

Step 2 — Upgrade  
- Coder applies EE 2.1 patterns  
- Coder removes legacy patterns  
- Coder refactors to UG-ISP  

Step 3 — Validation  
- Enforcer validates  
- Scanner re-scans  
- CI pipeline runs  

Step 4 — Knowledge Update  
- Knowledge Agent creates LESS entries  
- Knowledge Agent creates DEC entries  
- Knowledge Agent updates indexes and routers  

Step 5 — Convergence Check  
- Coordinator Override checks domain  
- Governance state machine validates transition  

Step 6 — Mark Domain Converged  
- Only when all requirements are satisfied  

5. Regression handling

If a regression is detected in a domain:

- Domain MUST revert to “In Progress”  
- Scanner MUST extend itself  
- Repair cycle MUST restart  
- CI pipeline MUST block merges  
- Knowledge Agent MUST record a DEC entry  
- Domain convergence tracker MUST update status  

6. Directory-level convergence

Within each domain, every directory MUST converge:

- No directory may contain hybrid patterns  
- No directory may contain legacy code  
- No directory may contain partial upgrades  
- No directory may be skipped  
- No directory may bypass validation  

7. Domain convergence states

Each domain MUST track the following states:

STATE 0 — Not Started  
STATE 1 — Pre-Validation  
STATE 2 — Upgrade In Progress  
STATE 3 — Validation  
STATE 4 — Convergence Check  
STATE 5 — Converged  
STATE 6 — Regression Detected (returns to STATE 2)  

8. Allowed transitions

0 → 1  
1 → 2  
2 → 3  
3 → 4  
4 → 5  
5 → 6 (if regression)  
6 → 2  

9. Forbidden transitions

Any → 5 (without full convergence)  
Any → 4 (without validation)  
Any → 3 (without upgrade)  
Any → 2 (without pre-validation)  
5 → 0 (no resets allowed)  
5 → 1 (no backward transitions)  

If a forbidden transition is attempted:
- Coordinator Override MUST block it  
- Enforcer MUST be invoked  
- System MUST revert to last valid state  

10. System-wide convergence

The EE 2.1 upgrade may only progress to system convergence when:

- All 15 domains reach STATE 5  
- No domain is in STATE 6  
- No domain contains unresolved violations  
- No domain contains hybrid patterns  
- No domain contains legacy code  
- All directories converge  
- All SIMA updates are complete  
- All scanner extensions are applied  
- CI pipeline passes  
- Enforcer returns PASS  
- Governance state machine allows transition  

11. Completion criteria

The EE 2.1 upgrade is complete only when:

- All domains converge  
- All directories converge  
- All governance rules are satisfied  
- All agents return PASS  
- Coordinator Override approves  
- Governance state machine allows exit  

END OF FILE