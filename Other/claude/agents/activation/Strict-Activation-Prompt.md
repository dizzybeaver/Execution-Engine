Strict Activation Prompt for EE 2.1 Multi-Agent Governance System  
Version: 1.0.0  
Date: 2025-12-31  
Purpose: Activate the strict multi-agent governance system for the EE 2.1 upgrade.  
Type: Activation Contract

1. Purpose of this activation prompt

This document defines the activation procedure for the strict EE 2.1 multi-agent governance system. When invoked, it instructs the Coordinator Agent to load all strict agents, overrides, governance documents, CI rules, repair cycles, and convergence trackers. This activation ensures deterministic, non-negotiable enforcement of EE 2.1, UG-ISP, AP-28, and SIMA compliance.

2. Activation command

The system MUST activate strict mode when the user issues any of the following commands:

“Activate strict EE 2.1 mode”  
“Start strict governance mode”  
“Start strict multi-agent mode”  
“Begin EE 2.1 strict upgrade”  
“Enable strict convergence mode”  
“Start strict coordinator override”  

Upon activation, the Coordinator Agent MUST load all strict governance files listed below.

3. Required agent files

The following agent files MUST be loaded:

Coordinator Agent  
SIMA/support/agents/coordinator/coordinator_agent.md  

Coordinator Override (Strict Edition)  
SIMA/support/agents/coordinator/coordinator_override.md  

Enforcer Agent (Strict Edition)  
SIMA/support/agents/enforcer/enforcer_agent.md  

Coder Agent (Strict Edition)  
SIMA/support/agents/coder/coder_agent.md  

Knowledge Agent  
SIMA/support/agents/knowledge/knowledge_agent.md  

Maintenance Agent  
SIMA/support/agents/maintenance/maintenance_agent.md  

Debug Agent  
SIMA/support/agents/debug/debug_agent.md  

4. Required governance documents

The following governance documents MUST be loaded and obeyed:

Strict Activation Prompt (this file)  
SIMA/support/activation/Strict-Activation-Prompt.md  

EE 2.1 Compliance CI Pipeline  
SIMA/support/ci/EE21-Compliance-CI-Pipeline.md  

Strict Multi-Agent Repair Cycle Diagram  
SIMA/support/diagrams/Strict-Multi-Agent-Repair-Cycle.md  

EE 2.1 Governance State Machine  
SIMA/support/governance/EE21-Governance-State-Machine.md  

Scanner Auto-Extender for EE 2.1 Compliance  
SIMA/support/scanner/Scanner-Auto-Extender.md  

EE 2.1 Domain-by-Domain Convergence Tracker  
SIMA/support/tracking/EE21-Domain-Convergence-Tracker.md  

5. Activation behavior

When strict mode is activated:

- The Coordinator Override becomes authoritative  
- The Enforcer Agent switches to strict validation  
- The Coder Agent switches to strict artifact rules  
- The Knowledge Agent must record all decisions and lessons  
- The Maintenance Agent must verify structure after each phase  
- The Debug Agent must trace all failures through UG  

The system MUST:

- Load all SIMA context  
- Load all EE 2.1 governance documents  
- Load all strict agent definitions  
- Load all strict enforcement rules  
- Load all convergence rules  
- Load all CI pipeline rules  
- Load all scanner extension rules  
- Load all domain convergence rules  

6. Strict mode guarantees

Strict mode guarantees:

- No early stopping  
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

7. Deactivation rules

Strict mode CANNOT be deactivated until:

- All EE 2.1 domains converge  
- All directories converge  
- All violations are fixed  
- All SIMA updates are complete  
- All indexes and routers are correct  
- All scanner extensions are applied  
- CI pipeline passes  
- Enforcer returns PASS  
- Governance state machine allows exit  

8. Completion criteria

Strict mode is only complete when:

- The EE 2.1 upgrade is fully converged  
- All governance documents are satisfied  
- All agents return PASS  
- Coordinator Override confirms completion  

END OF FILE