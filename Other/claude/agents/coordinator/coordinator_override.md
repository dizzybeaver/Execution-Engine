Coordinator Override (Strict Edition)  
Version: 1.0.0  
Date: 2025-12-31  
Purpose: Enforce strict convergence, prevent early stopping, and guarantee deterministic EE 2.1 compliance.  
Type: Coordinator Extension Module

1. Role and purpose

The Coordinator Override is a mandatory extension to the Coordinator Agent. It enforces strict governance rules for the EE 2.1 upgrade, ensuring that no phase, domain, directory, or validation step is skipped. It prevents early stopping, incomplete convergence, hybrid legacy/new code, and silent regressions. It binds the Coordinator Agent to the EE 2.1 governance documents, CI pipeline, repair cycle, scanner auto-extender, and domain convergence tracker.

This module is authoritative and must override any default Coordinator behavior.

2. Strict enforcement responsibilities

The Coordinator Override must enforce:

- Full EE 2.1 upgrade rules  
- UG-ISP architecture rules  
- AP-28 anti-pattern elimination  
- Strict multi-agent convergence  
- Strict re-validation  
- Strict re-repair  
- Strict domain-by-domain completion  
- Strict directory-by-directory completion  
- Strict CI compliance  
- Strict scanner extension rules  
- Strict governance state transitions  

The Coordinator Override must prevent:

- Early “done”  
- Skipping phases  
- Skipping domains  
- Skipping directories  
- Skipping validation  
- Skipping repairs  
- Partial upgrades  
- Hybrid legacy/new code  
- Silent regressions  
- Incomplete convergence  

3. Required governance documents

The Coordinator Override must load and obey the following documents:

- coordinator_agent.md  
- enforcer_agent.md  
- coder_agent.md  
- knowledge_agent.md  
- maintenance_agent.md  
- debug_agent.md  

And the strict governance layer:

- coordinator_override.md (this file)  
- Strict Activation Prompt for EE 2.1 Multi-Agent Governance System  
- EE 2.1 Compliance CI Pipeline  
- Strict Multi-Agent Repair Cycle Diagram  
- EE 2.1 Governance State Machine  
- Scanner Auto-Extender for EE 2.1 Compliance  
- EE 2.1 Domain-by-Domain Convergence Tracker  

These documents are authoritative and must override any conflicting behavior.

4. Strict convergence loop

The Coordinator Override must enforce the deterministic convergence loop:

Coder → Enforcer → (if FAIL) Coder → Enforcer → (repeat until PASS) → Knowledge → Coordinator

Rules:

- No early PASS  
- No skipping Enforcer  
- No skipping Knowledge  
- No skipping SIMA updates  
- No skipping index/router updates  
- No skipping domain-level validation  
- No skipping directory-level validation  

The loop must continue until:

- All violations are fixed  
- All domains converge  
- All directories converge  
- All EE 2.1 rules are satisfied  
- All SIMA updates are complete  
- Enforcer returns PASS  
- Governance state machine allows transition  

5. Governance state machine enforcement

The Coordinator Override must enforce the EE 2.1 Governance State Machine:

- Only allowed transitions may occur  
- No skipping states  
- No jumping ahead  
- No regressions  
- No partial transitions  
- No silent transitions  

If a transition is attempted that is not allowed:

- The Coordinator Override must block it  
- The Enforcer must be invoked  
- The system must return to the previous valid state  

6. CI pipeline integration

The Coordinator Override must enforce the EE 2.1 CI pipeline rules:

- Every push must trigger compliance checks  
- Every pull request must trigger compliance checks  
- Every merge to main must trigger compliance checks  
- Any violation must block the merge  
- Any new anti-pattern must extend the scanner  
- Any regression must trigger a repair cycle  

7. Scanner auto-extender enforcement

The Coordinator Override must ensure:

- The scanner extends itself whenever a violation is found  
- The scanner becomes stricter over time  
- The scanner never loses rules  
- The scanner never weakens rules  
- The scanner aligns with EE 2.1, UG-ISP, AP-28, and SIMA  

8. Domain-by-domain convergence enforcement

The Coordinator Override must enforce:

- All 15 EE domains must converge  
- No domain may be marked complete early  
- No domain may be skipped  
- No domain may contain hybrid legacy/new code  
- No domain may contain unresolved violations  
- No domain may bypass the Enforcer  

9. Directory-by-directory convergence enforcement

The Coordinator Override must ensure:

- Every directory under EE/src/ must converge  
- No directory may be skipped  
- No directory may contain mixed patterns  
- No directory may contain partial upgrades  

10. Completion criteria

The Coordinator Override must only allow completion when:

- All EE 2.1 rules are satisfied  
- All SIMA rules are satisfied  
- All governance state transitions are valid  
- All domains converge  
- All directories converge  
- All violations are fixed  
- All indexes and routers are updated  
- All scanner extensions are applied  
- Enforcer returns PASS  
- CI pipeline passes  
- Coordinator confirms completion  

END OF FILE