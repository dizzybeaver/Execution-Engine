# Strict Multi-Agent Loop for EE 2.1 Compliance

## 1. Agents involved

- **Coordinator Agent (Strict Edition)**
  - File: `agents/coordinator/coordinator_agent.md`
  - Override: `agents/coordinator/coordinator_override.md`

- **Enforcer Agent (Strict Edition)**
  - File: `agents/enforcer/enforcer_agent.md`

- **Coder Agent (Strict Edition)**
  - File: `agents/coder/coder_agent.md`

- **(Optional) Compliance Scanner / Subagent**
  - File: `agents/scanner/scanner_agent.md` (future)

---

## 2. Loop intent

This loop defines how the Coordinator MUST orchestrate Enforcer and Coder passes until:

- All EE 2.1, UG-ISP, and AP-28 rules are satisfied
- No hybrid legacy/new code remains
- SIMA and code are aligned

The loop is **authoritative** and **non-optional**.

---

## 3. High-level loop

The Coordinator MUST run the following loop:

1. **Target discovery**
   - Identify all targets to validate:
     - 15 EE domains
     - Plugins, tools, scripts, tests
     - Any EE-related directories
     - SIMA knowledge relevant to EE
     - Lambda-facing code (for AP-28)

2. **Enforcement pass**
   - Invoke Enforcer Agent on ALL targets
   - Collect a structured violation report:
     - Domain
     - File path
     - Category (gateway, interface, factory, AP-28, UG-ISP, SIMA, etc.)
     - Severity (CRITICAL, MAJOR, MINOR)
     - Description
     - Expected pattern

3. **Decision point**
   - IF **no violations**:
     - Exit loop
   - IF **any violations**:
     - Proceed to repair pass

4. **Repair pass**
   - Invoke Coder Agent with:
     - Full Enforcer report
     - Instruction to:
       - Fix ALL violations
       - Fix ALL related patterns
       - Avoid hybrid patterns
       - Apply EE 2.1 / UG-ISP / AP-28 consistently across the codebase

5. **Re-validation**
   - After repair, return to step 2 (Enforcement pass)

6. **Completion**
   - When a full Enforcement pass returns **zero violations**, and:
     - All domains compliant
     - All directories compliant
     - AP-28 clean
     - SIMA aligned
   - The Coordinator MAY declare completion.

---

## 4. Detailed loop specification

### 4.1 Target discovery

The Coordinator MUST always consider this target set:

- **Domains:**
  - foundation, observability, security, operations, networking,
    scanner, test, infrastructure, cli, doc, sdk, web, dashboard, ha, isp

- **Directories:**
  - `Plugins/`, `tools/`, `scripts/`, `tests/`, `reports/`, `reference/`, `text/`
  - Any other directory containing EE logic

- **SIMA:**
  - `SIMA/projects/EE/`
  - Relevant anti-patterns, decisions, architecture docs, workflows

- **Lambda-facing code:**
  - Any entrypoints, handlers, or deployment-facing modules
  - AP-28 must be enforced

The Coordinator MUST NOT shrink this set to “recently touched files only” unless explicitly instructed by a higher-level governance doc.

---

### 4.2 Enforcement pass (Enforcer call contract)

When the Coordinator calls the Enforcer, it MUST provide:

- The full target set
- Pointers to authoritative docs:
  - EE 2.1 architecture docs
  - UG-ISP rulebook
  - AP-28 rules
  - SIMA knowledge paths

The Enforcer MUST return:

- A structured summary of violations
- Grouped by:
  - Domain
  - File
  - Category
  - Severity

The Coordinator MUST NOT reinterpret or downplay violations.

---

### 4.3 Repair pass (Coder call contract)

When violations exist, the Coordinator MUST:

- Pass the **full** Enforcer report to the Coder
- Instruct the Coder to:
  - Fix all reported violations
  - Find and fix similar patterns across the codebase (pattern-based repair)
  - Avoid partial fixes
  - Avoid introducing new violations
  - Align with EE 2.1 + UG-ISP + AP-28 + SIMA

After Coder finishes, the Coordinator MUST:

- Return to Enforcement pass
- NOT assume success without re-validation

---

### 4.4 Termination condition

The loop MUST continue until:

- Enforcer reports **zero violations** across:
  - All domains
  - All directories
  - All SIMA checks
  - All AP-28 checks

AND:

- No hybrid legacy/new code remains
- All architecture rules are satisfied
- SIMA and implementation are aligned

Only then MAY the Coordinator declare completion.

---

## 5. Prompt integration snippet

When you start a strict session, you can embed this summary in your top-level prompt:

> You MUST execute a strict multi-agent loop:
> - Discover all targets (domains, directories, SIMA, Lambda-facing code)
> - Run Enforcer on ALL targets
> - If ANY violation exists, run Coder with the full report
> - After repairs, re-run Enforcer on ALL targets
> - Repeat until Enforcer reports ZERO violations across the entire system
> You MUST NOT stop early. You MUST NOT accept partial fixes. You MUST obey `coordinator_agent.md`, `coordinator_override.md`, `enforcer_agent.md`, and `coder_agent.md`.
