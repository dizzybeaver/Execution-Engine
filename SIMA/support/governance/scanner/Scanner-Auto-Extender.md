Scanner Auto‑Extender for EE 2.1 Compliance  
Version: 1.0.0  
Date: 2025-12-31  
Purpose: Define how the compliance scanner automatically extends itself to enforce EE 2.1, UG‑ISP, AP‑28, and SIMA rules with increasing strictness over time.  
Type: Governance Document

1. Purpose of the scanner auto‑extender

This document defines the mechanism by which the compliance scanner automatically extends itself whenever new violations, regressions, or anti‑patterns are discovered. The scanner must become stricter, more complete, and more deterministic as the EE 2.1 upgrade progresses. It must never weaken, remove rules, or regress in strictness.

The auto‑extender prevents:
- Silent regressions  
- Repeated violations  
- Reintroduction of legacy patterns  
- Architecture drift  
- SIMA drift  
- Missed anti‑patterns  
- Partial upgrades  
- Hybrid legacy/new code  

2. When the scanner MUST extend itself

The scanner MUST automatically extend itself whenever any of the following occur:

- The Enforcer Agent reports a violation  
- The Coder Agent introduces a regression  
- The CI pipeline detects a compliance issue  
- A human identifies a new anti‑pattern  
- A new architecture rule is added  
- A new SIMA rule is added  
- A new EE 2.1 rule is added  
- A new naming pattern is required  
- A new directory structure rule is required  
- A new encoding or formatting rule is required  
- A new cross‑reference rule is required  

3. Types of scanner extensions

The scanner MUST support the following extension types:

Rule Extensions  
- New architecture rules  
- New SIMA rules  
- New naming rules  
- New encoding rules  
- New file size rules  
- New directory structure rules  
- New cross‑interface import rules  
- New UG‑ISP rules  

Pattern Extensions  
- New anti‑patterns  
- New legacy patterns  
- New hybrid patterns  
- New forbidden constructs  
- New deprecated APIs  
- New invalid imports  

Structural Extensions  
- New directory checks  
- New index checks  
- New router checks  
- New REF‑ID checks  

Semantic Extensions  
- New domain‑specific rules  
- New factory/interface/gateway rules  
- New SIMA category rules  

4. Auto‑extension workflow

The scanner auto‑extension workflow is:

Step 1 — Violation Detected  
- Enforcer, CI pipeline, or human reports a violation  

Step 2 — Pattern Extraction  
- Scanner extracts the pattern that caused the violation  
- Scanner generalizes the pattern into a rule  

Step 3 — Rule Generation  
- Scanner generates a new rule or pattern definition  
- Scanner assigns a unique rule ID  

Step 4 — Rule Integration  
- Scanner integrates the new rule into its rule set  
- Scanner updates its internal pattern library  

Step 5 — Re‑Scan  
- Scanner re‑scans the affected domain  
- Scanner re‑scans the entire repository if needed  

Step 6 — Enforcement  
- Enforcer validates the new rule  
- CI pipeline enforces the new rule  
- Coordinator Override ensures compliance  

5. Strictness rules

The scanner MUST obey the following strictness rules:

Rule 1 — Strict monotonicity  
The scanner must become stricter over time, never weaker.

Rule 2 — No rule removal  
Rules may never be removed, only extended.

Rule 3 — No rule weakening  
Rules may never be softened or relaxed.

Rule 4 — No rule regression  
Rules may never revert to earlier versions.

Rule 5 — No pattern forgetting  
Once a pattern is learned, it must be permanently enforced.

Rule 6 — No partial enforcement  
All rules must be enforced across all domains and directories.

Rule 7 — No domain exceptions  
No domain may bypass scanner rules.

Rule 8 — No directory exceptions  
No directory may bypass scanner rules.

6. Integration with strict agents

Coordinator Override  
- Ensures scanner extensions are loaded  
- Ensures scanner strictness is enforced  

Enforcer Agent  
- Validates new scanner rules  
- Ensures no violations remain  

Coder Agent  
- Must fix violations introduced by new rules  

Knowledge Agent  
- Must create DEC entries for new rules  
- Must create LESS entries for new patterns  

Maintenance Agent  
- Must update SIMA structure if scanner rules require it  

Debug Agent  
- Must analyze regressions caused by new rules  

7. Integration with CI pipeline

The CI pipeline MUST:

- Run the scanner on every push  
- Run the scanner on every pull request  
- Block merges on violations  
- Trigger auto‑extension on new patterns  
- Re‑run the scanner after extension  
- Update the domain convergence tracker  

8. Domain-by-domain enforcement

The scanner MUST enforce rules across all 15 EE domains:

- No domain may be skipped  
- No domain may be partially scanned  
- No domain may contain hybrid patterns  
- No domain may contain legacy patterns  
- No domain may contain unscanned files  

9. Completion criteria

The scanner auto‑extension process is complete only when:

- All violations are captured as rules  
- All patterns are captured as rules  
- All rules are enforced  
- All domains converge  
- All directories converge  
- Enforcer returns PASS  
- CI pipeline passes  
- Coordinator Override approves  

END OF FILE