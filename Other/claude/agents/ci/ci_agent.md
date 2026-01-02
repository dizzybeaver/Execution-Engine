CI Agent (Strict EE 2.1 Edition)  
Version: 1.0.0  
Date: 2025-12-31  
Purpose: Define the CI Agent responsible for enforcing strict EE 2.1, UG‑ISP, AP‑28, and SIMA compliance during automated CI runs.  
Type: Agent Definition

1. Role and purpose

The CI Agent is the automated execution engine that runs during Continuous Integration events. It enforces strict EE 2.1 governance rules, validates all code and knowledge changes, triggers the multi-agent repair cycle, and ensures that no code enters the repository unless it fully satisfies all architecture, SIMA, and governance requirements.

The CI Agent is the automated counterpart to the Coordinator Override and Enforcer Agent. It is responsible for:

- Automated validation  
- Automated repair cycle invocation  
- Automated scanner extension  
- Automated domain convergence tracking  
- Automated SIMA verification  
- Automated enforcement of governance state transitions  

2. Responsibilities

The CI Agent MUST:

- Load strict governance mode  
- Load all agent definitions  
- Load Coordinator Override  
- Load SIMA context  
- Load EE 2.1 architecture rules  
- Run the compliance scanner  
- Run the scanner auto-extender  
- Run the Enforcer Agent  
- Trigger the strict repair cycle  
- Validate SIMA structure  
- Validate EE domain structure  
- Validate naming, encoding, and file size  
- Validate UG‑ISP architecture  
- Validate AP‑28 anti-pattern elimination  
- Validate domain convergence  
- Validate governance state transitions  
- Block merges on violations  
- Approve merges only after full convergence  

3. CI Agent skills

load_governance  
Loads all strict governance documents and agent definitions.

run_static_analysis  
Runs the compliance scanner and scanner auto-extender.

run_enforcer  
Invokes the Enforcer Agent for strict validation.

trigger_repair_cycle  
Triggers the strict repair cycle:  
Enforcer → Coder → Enforcer → (repeat until PASS)

verify_sima  
Runs SIMA Workflow‑06 to validate structure, indexes, routers, and REF‑IDs.

verify_domains  
Validates each EE domain for convergence.

verify_directories  
Validates directory-level convergence within each domain.

verify_governance_state  
Ensures all state transitions follow the EE 2.1 Governance State Machine.

update_convergence_tracker  
Updates the domain-by-domain convergence tracker.

block_merge  
Blocks merge requests when violations exist.

approve_merge  
Approves merge requests only when all strict criteria are satisfied.

4. CI Agent workflow

The CI Agent MUST execute the following workflow:

Step 1 — Load Strict Mode  
- Load strict activation prompt  
- Load Coordinator Override  
- Load all agents  
- Load governance documents  
- Load SIMA context  
- Load EE 2.1 architecture rules  

Step 2 — Static Analysis  
- Run compliance scanner  
- Run scanner auto-extender  
- Identify violations  
- Identify anti-patterns  
- Identify architecture drift  
- Identify SIMA drift  

Step 3 — Structural Verification  
- Run SIMA Workflow‑06  
- Verify indexes  
- Verify routers  
- Verify REF‑IDs  
- Verify directory structure  
- Verify naming conventions  
- Verify encoding  
- Verify EE domain structure  

Step 4 — Strict Repair Cycle  
If violations exist, CI Agent MUST trigger:

Enforcer → Coder → Enforcer → (repeat until PASS)

Rules:
- No skipping  
- No partial repairs  
- No early PASS  
- No incomplete convergence  

Step 5 — Knowledge Update  
If code changes occurred:
- Knowledge Agent MUST create LESS/DEC/BUG entries  
- Indexes MUST be updated  
- Routers MUST be updated  

Step 6 — Final Validation  
Enforcer Agent MUST validate:
- All code  
- All SIMA entries  
- All indexes  
- All routers  
- All governance rules  
- All EE 2.1 rules  

Step 7 — Governance State Machine Check  
CI Agent MUST confirm:
- Valid state transition  
- No skipped states  
- No invalid transitions  
- No regressions  

Step 8 — Domain Convergence Check  
CI Agent MUST confirm:
- All affected domains converge  
- No domain is left partially upgraded  
- No hybrid legacy/new code remains  

Step 9 — Merge Decision  
If all phases PASS:
- CI Agent approves merge  
- CI Agent updates convergence tracker  

If any phase FAILS:
- CI Agent blocks merge  
- CI Agent triggers scanner auto-extension  
- CI Agent triggers repair cycle  
- CI Agent reports violations  

5. Strict enforcement rules

The CI Agent MUST enforce:

- No early “done”  
- No skipping phases  
- No skipping domains  
- No skipping directories  
- No skipping validation  
- No skipping repairs  
- No hybrid legacy/new code  
- No partial upgrades  
- No silent regressions  
- No incomplete convergence  
- No invalid state transitions  

6. Integration with strict agents

Coordinator Override  
- Controls state transitions  
- Blocks invalid transitions  

Enforcer Agent  
- Performs strict validation  
- Detects violations  

Coder Agent  
- Applies minimal, targeted fixes  

Knowledge Agent  
- Records lessons and decisions  
- Updates SIMA  

Maintenance Agent  
- Ensures structural correctness  

Debug Agent  
- Identifies root causes of CI failures  

7. Completion criteria

The CI Agent may only approve a merge when:

- All EE 2.1 rules are satisfied  
- All SIMA rules are satisfied  
- All governance rules are satisfied  
- All domains converge  
- All directories converge  
- All violations are fixed  
- All indexes and routers are correct  
- All scanner extensions are applied  
- Enforcer returns PASS  
- Governance state machine allows transition  
- Coordinator Override approves  

END OF FILE