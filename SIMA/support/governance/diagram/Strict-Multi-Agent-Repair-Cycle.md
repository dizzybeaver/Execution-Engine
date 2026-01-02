Strict Multi-Agent Repair Cycle Diagram  
Version: 1.0.0  
Date: 2025-12-31  
Purpose: Define the deterministic repair cycle used by the strict multi-agent system during the EE 2.1 upgrade.  
Type: Governance Diagram (Textual Specification)

1. Purpose of this repair cycle

This document defines the strict, deterministic, non-negotiable repair cycle that governs all multi-agent interactions during the EE 2.1 upgrade. It ensures that no violations remain, no partial fixes are accepted, and no hybrid legacy/new code survives. The cycle is enforced by the Coordinator Override, Enforcer Agent, and Coder Agent.

The repair cycle prevents:
- Early “done”  
- Skipped validation  
- Skipped repairs  
- Partial fixes  
- Silent regressions  
- Architecture drift  
- SIMA drift  
- Domain-level drift  
- Directory-level drift  

2. Core repair cycle

The strict repair cycle is:

Enforcer → Coder → Enforcer → Coder → (repeat until PASS) → Knowledge → Coordinator

This cycle MUST continue until:
- All violations are fixed  
- All architecture rules are satisfied  
- All SIMA rules are satisfied  
- All EE 2.1 rules are satisfied  
- All domains converge  
- All directories converge  
- Enforcer returns PASS  

3. Detailed cycle phases

Phase 1 — Enforcer Validation  
- Enforcer scans the artifact  
- Enforcer identifies violations  
- Enforcer returns FAIL with explicit reasons  
- Coordinator routes to Coder  

Phase 2 — Coder Repair  
- Coder fetches the file  
- Coder applies minimal, targeted fixes  
- Coder outputs complete file artifacts  
- Coder applies SIMA change markers  
- Coder returns artifact to Enforcer  

Phase 3 — Enforcer Re-Validation  
- Enforcer re-checks the artifact  
- If violations remain → FAIL  
- If new violations appear → FAIL  
- If all violations are fixed → PASS  

Phase 4 — Knowledge Update  
After PASS:
- Knowledge Agent creates LESS entries  
- Knowledge Agent creates DEC entries  
- Knowledge Agent updates indexes  
- Knowledge Agent updates routers  

Phase 5 — Coordinator Confirmation  
Coordinator confirms:
- All agents passed  
- All governance rules satisfied  
- All SIMA updates complete  
- All EE 2.1 rules satisfied  

4. Rules of the repair cycle

The repair cycle MUST obey the following rules:

Rule 1 — No skipping  
No agent may skip its turn in the cycle.

Rule 2 — No early PASS  
Enforcer must not return PASS unless all violations are fixed.

Rule 3 — No partial fixes  
Coder must fix all violations identified in the cycle.

Rule 4 — No multi-change debugging  
Coder must apply minimal, targeted fixes.

Rule 5 — No hybrid code  
Legacy and new patterns must not coexist.

Rule 6 — No architecture drift  
UG-only execution must be preserved.

Rule 7 — No SIMA drift  
Indexes, routers, and REF-IDs must remain correct.

Rule 8 — No domain drift  
All domains must converge fully.

Rule 9 — No directory drift  
All directories must converge fully.

Rule 10 — No silent regressions  
Any new violation must restart the cycle.

5. Enforcement by Coordinator Override

The Coordinator Override MUST enforce:

- The cycle cannot be bypassed  
- The cycle cannot be shortened  
- The cycle cannot be exited early  
- The cycle cannot be overridden by user commands  
- The cycle cannot be skipped for any domain or directory  

6. Integration with CI pipeline

The CI pipeline MUST run the repair cycle automatically when:

- A violation is detected  
- A regression is detected  
- A new anti-pattern is discovered  
- A build fails  
- A merge request is opened  
- A push occurs  

7. Completion criteria

The repair cycle is complete only when:

- Enforcer returns PASS  
- Knowledge Agent updates SIMA  
- Coordinator Override approves  
- CI pipeline passes  
- Governance state machine allows transition  
- Domain convergence tracker marks domain as converged  

END OF FILE