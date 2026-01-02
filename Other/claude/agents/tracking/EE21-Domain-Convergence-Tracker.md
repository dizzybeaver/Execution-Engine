# EE 2.1 Domain-by-Domain Convergence Tracker

This tracker defines how the system MUST measure, record, and enforce
convergence for each of the 15 EE domains during the EE 2.1 upgrade.

The goal is to ensure:
- No domain is skipped
- No domain is partially upgraded
- No domain is marked complete without full validation
- No hybrid legacy/new code remains
- All domains converge to EE 2.1 architecture

---

# 1. Domain List

The system MUST track convergence for all 15 EE domains:

1. foundation  
2. observability  
3. security  
4. operations  
5. networking  
6. scanner  
7. test  
8. infrastructure  
9. cli  
10. doc  
11. sdk  
12. web  
13. dashboard  
14. ha  
15. isp  

---

# 2. Convergence States

Each domain MUST be in exactly one of these states:

- `D0_UNTOUCHED`  
- `D1_SCANNED`  
- `D2_VIOLATIONS_FOUND`  
- `D3_REPAIR_IN_PROGRESS`  
- `D4_REPAIRED_PENDING_REVALIDATION`  
- `D5_FULLY_VALIDATED`  
- `D6_CONVERGED`  

---

# 3. State Definitions

## D0_UNTOUCHED
- Domain has not yet been scanned.
- No assumptions may be made about compliance.

Transition:
- `D0_UNTOUCHED → D1_SCANNED`

---

## D1_SCANNED
- Enforcer has scanned the domain.
- Violations may or may not exist.

Transitions:
- If violations exist: `D1_SCANNED → D2_VIOLATIONS_FOUND`
- If no violations: `D1_SCANNED → D5_FULLY_VALIDATED`

---

## D2_VIOLATIONS_FOUND
- Enforcer has reported violations.
- Domain is non-compliant.

Transition:
- `D2_VIOLATIONS_FOUND → D3_REPAIR_IN_PROGRESS`

---

## D3_REPAIR_IN_PROGRESS
- Coder Agent is repairing violations.
- Repairs MUST be global, not local.

Transition:
- `D3_REPAIR_IN_PROGRESS → D4_REPAIRED_PENDING_REVALIDATION`

---

## D4_REPAIRED_PENDING_REVALIDATION
- Repairs applied.
- Domain MUST be re-scanned.

Transition:
- If violations remain: `D4_REPAIRED_PENDING_REVALIDATION → D2_VIOLATIONS_FOUND`
- If clean: `D4_REPAIRED_PENDING_REVALIDATION → D5_FULLY_VALIDATED`

---

## D5_FULLY_VALIDATED
- Domain has passed Enforcer checks.
- No violations remain.

Transition:
- `D5_FULLY_VALIDATED → D6_CONVERGED`

---

## D6_CONVERGED
- Domain is fully EE 2.1 compliant.
- No hybrid code.
- No regressions.
- No AP-28 violations.
- No UG-ISP violations.

This is the final state.

---

# 4. Convergence Rules

The system MUST enforce:

### 4.1 No skipping
A domain MUST NOT jump directly to:
- validated
- converged
- repaired

### 4.2 No partial upgrades
A domain MUST NOT be marked validated if:
- related files remain unscanned
- hybrid patterns exist
- AP-28 violations exist
- SIMA mismatches exist

### 4.3 No regression
If a domain regresses:
- It MUST return to `D2_VIOLATIONS_FOUND`

### 4.4 No early convergence
A domain MUST NOT reach `D6_CONVERGED` until:
- All directories referencing it are clean
- All cross-domain imports are validated
- All factories, interfaces, gateways are correct
- SIMA knowledge is aligned

---

