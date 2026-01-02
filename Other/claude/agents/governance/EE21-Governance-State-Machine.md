# EE 2.1 Governance State Machine

This document defines the **governance states** and **allowed transitions** for the EE 2.1 upgrade and compliance workflow, enforced by:

- Coordinator Agent (Strict Edition)
- Coordinator Override
- Enforcer Agent (Strict Edition)
- Coder Agent (Strict Edition)
- (Optional) Compliance Scanner Subagent

The goal is to prevent:
- Early “done”
- Skipping phases
- Skipping domains/directories
- Partial or hybrid upgrades
- Ignored violations
- Silent regressions

---

## 1. State list

The system can be in exactly one of these states at a time:

1. `S0_IDLE`
2. `S1_SIMA_UPGRADE`
3. `S2_DOMAIN_UPGRADE`
4. `S3_DIRECTORY_UPGRADE`
5. `S4_KNOWLEDGE_RECORDING`
6. `S5_ENFORCEMENT_PASS`
7. `S6_REPAIR_PASS`
8. `S7_FULL_REVALIDATION`
9. `S8_COMPLIANT`
10. `S9_FAILED` (governance failure / manual intervention required)

---

## 2. State definitions

### S0_IDLE — Idle / Not upgrading

**Entry conditions:**
- No active upgrade process
- Or previous cycle completed

**Allowed transitions:**
- `S0_IDLE → S1_SIMA_UPGRADE` when a strict EE 2.1 upgrade is initiated.

Coordinator responsibility:
- Initialize context
- Load architecture docs, SIMA, agent specs, override

---

### S1_SIMA_UPGRADE — SIMA-first upgrade

**Purpose:**
- Bring SIMA in line with EE 2.1, UG-ISP, AP-28.

**Coordinator MUST:**
- Rewrite EE-related SIMA docs
- Update anti-patterns, decisions, workflows, lessons, indexes
- Ensure AP-28 exists and is correct
- Remove obsolete architecture references

**Allowed transitions:**
- `S1_SIMA_UPGRADE → S5_ENFORCEMENT_PASS` for validation of SIMA
- `S1_SIMA_UPGRADE → S9_FAILED` only on unrecoverable error

---

### S2_DOMAIN_UPGRADE — Domain-by-domain EE upgrade

**Purpose:**
- Upgrade all 15 EE domains to EE 2.1.

**Domains:**
- foundation, observability, security, operations, networking,
  scanner, test, infrastructure, cli, doc, sdk, web, dashboard, ha, isp

**Coordinator MUST:**
- Work domain by domain, no skipping, no reordering
- For each domain, use enforcement + repair loop

**Allowed transitions:**
- `S2_DOMAIN_UPGRADE → S5_ENFORCEMENT_PASS` (per domain / per cycle)
- `S2_DOMAIN_UPGRADE → S3_DIRECTORY_UPGRADE` only after ALL domains pass
- `S2_DOMAIN_UPGRADE → S9_FAILED` on unrecoverable error

---

### S3_DIRECTORY_UPGRADE — Plugins/tools/scripts/tests/etc.

**Purpose:**
- Upgrade all non-domain EE assets to EE 2.1 + UG-ISP + AP-28.

**Targets:**
- Plugins/, tools/, scripts/, tests/, reports/, reference/, text/
- Any EE-related directory

**Allowed transitions:**
- `S3_DIRECTORY_UPGRADE → S5_ENFORCEMENT_PASS`
- `S3_DIRECTORY_UPGRADE → S4_KNOWLEDGE_RECORDING` only after all directories pass
- `S3_DIRECTORY_UPGRADE → S9_FAILED` on unrecoverable error

---

### S4_KNOWLEDGE_RECORDING — SIMA synchronization

**Purpose:**
- Ensure all new patterns, rules, decisions, and architecture changes are encoded in SIMA.

**Coordinator MUST:**
- Route EE-specific knowledge to SIMA/projects/EE/
- UG-specific to SIMA/platforms/universal-gateway-system/
- Python-specific to SIMA/languages/python/
- Generic patterns to SIMA/generic/

**Allowed transitions:**
- `S4_KNOWLEDGE_RECORDING → S5_ENFORCEMENT_PASS` (to verify SIMA alignment)
- `S4_KNOWLEDGE_RECORDING → S9_FAILED` on unrecoverable error

---

### S5_ENFORCEMENT_PASS — Enforcer run

**Purpose:**
- Run Enforcer Agent on ALL relevant targets for the current phase (or entire system during full revalidation).

**Enforcer MUST:**
- Report ALL violations
- Treat ANY violation as blocking

**Allowed transitions:**
- If violations exist:
  - `S5_ENFORCEMENT_PASS → S6_REPAIR_PASS`
- If no violations AND phase-specific goals are met:
  - Return to previous phase state (S1/S2/S3/S4) or move forward
- If in S7_FULL_REVALIDATION and no violations:
  - `S5_ENFORCEMENT_PASS → S8_COMPLIANT`
- On unrecoverable failure:
  - `S5_ENFORCEMENT_PASS → S9_FAILED`

---

### S6_REPAIR_PASS — Coder run

**Purpose:**
- Apply repairs based on Enforcer report.

**Coder MUST:**
- Fix ALL violations
- Fix related patterns globally
- Avoid hybrid legacy/new code
- Avoid regressions

**Allowed transitions:**
- `S6_REPAIR_PASS → S5_ENFORCEMENT_PASS` (mandatory)
- `S6_REPAIR_PASS → S9_FAILED` on unrecoverable error

There is **no direct transition** from S6 to any “done” state. It MUST go back through Enforcement.

---

### S7_FULL_REVALIDATION — Full-system audit

**Purpose:**
- Verify that the entire system (domains, directories, SIMA, AP-28) is fully compliant.

Entered when:
- SIMA, domains, directories, and knowledge recording phases have all reached local “no known violations” conditions.

**Coordinator MUST:**
- Run Enforcer across the **entire** system, not just recently touched files.

**Allowed transitions:**
- `S7_FULL_REVALIDATION → S5_ENFORCEMENT_PASS`
- After S5:
  - If violations exist: loop S6 → S5 → S7 again
  - If no violations: `S7_FULL_REVALIDATION → S8_COMPLIANT`

---

### S8_COMPLIANT — Fully EE 2.1 compliant

**Purpose:**
- System has converged.

**Entry conditions:**
- Full-system Enforcer pass reports zero violations
- Coordinator’s completion criteria are all satisfied
- No hybrid legacy/new code
- SIMA and implementation aligned

**Allowed transitions:**
- `S8_COMPLIANT → S0_IDLE`
- Or future maintenance cycles can re-enter S2/S3/S7.

---

### S9_FAILED — Governance failure / manual intervention

**Purpose:**
- Represent an unrecoverable or ambiguous state that needs human decision.

Examples:
- Conflicting architectural rules
- Inconsistent SIMA vs. code with no clear resolution
- Broken build system preventing analysis

**Allowed transitions:**
- `S9_FAILED → S0_IDLE` after manual reset/recovery
- Or explicit restart at an earlier phase

---

## 3. Illegal transitions

The following transitions are **explicitly forbidden**:

- `S1_SIMA_UPGRADE → S2_DOMAIN_UPGRADE` without an Enforcement pass
- `S2_DOMAIN_UPGRADE → S4_KNOWLEDGE_RECORDING` directly
- `S2_DOMAIN_UPGRADE → S8_COMPLIANT` directly
- `S3_DIRECTORY_UPGRADE → S8_COMPLIANT` directly
- `S6_REPAIR_PASS → S8_COMPLIANT` directly
- `S6_REPAIR_PASS → S0_IDLE` directly
- Any state → `S8_COMPLIANT` without passing through `S7_FULL_REVALIDATION` + `S5_ENFORCEMENT_PASS` with zero violations

These illegal transitions are exactly the “lazy AI” shortcuts this state machine is designed to forbid.

---

## 4. Prompt integration snippet

When running in strict mode, you can add:

> You MUST treat the EE 2.1 upgrade as a governance state machine with states:
> S0_IDLE, S1_SIMA_UPGRADE, S2_DOMAIN_UPGRADE, S3_DIRECTORY_UPGRADE, S4_KNOWLEDGE_RECORDING, S5_ENFORCEMENT_PASS, S6_REPAIR_PASS, S7_FULL_REVALIDATION, S8_COMPLIANT, S9_FAILED.
> You MUST obey the allowed transitions only, and you MUST forbid any direct transition to COMPLIANT (S8) that bypasses FULL_REVALIDATION (S7) and a zero-violation ENFORCEMENT_PASS (S5).
