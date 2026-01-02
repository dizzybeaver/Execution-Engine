# EE/SIMA Commands

EE/SIMA Command Definitions  
Version: 1.0.0  
Date: 2025-12-31  
Purpose: Define all slash-commands for EE/SIMA multi-agent orchestration, enabling Claude Code to expose commands in the `/` menu.  
Type: Command File

---

## 1. Activation & Governance Commands

### `/activate-strict`
**Description:** Activates strict governance mode, loading all strict agents, rules, and enforcement layers.  
**Agents:** coordinator_override, coordinator_agent  
**Workflow:** load strict activation prompt → load governance → enforce strict mode

### `/load-governance`
**Description:** Loads all governance documents, state machines, repair cycles, and strict rules.  
**Agents:** coordinator_agent  
**Workflow:** load governance → validate governance integrity

### `/reload-agents`
**Description:** Reloads all strict agents and their skills.  
**Agents:** coordinator_agent  
**Workflow:** load agents → validate agent integrity

### `/reload-sima`
**Description:** Reloads SIMA context, indexes, routers, and REF-IDs.  
**Agents:** knowledge_agent, maintenance_agent  
**Workflow:** load SIMA → validate SIMA structure

---

## 2. Repair Cycle Commands

### `/repair`
**Description:** Runs the full strict repair cycle across the entire repository.  
**Agents:** enforcer_agent, coder_agent, coordinator_override  
**Workflow:** Enforcer → Coder → Enforcer (repeat until PASS)

### `/repair-domain <domain>`
**Description:** Repairs a specific EE domain using strict repair cycle rules.  
**Agents:** enforcer_agent, coder_agent  
**Workflow:** scan domain → repair → validate → converge

### `/repair-directory <domain>/<directory>`
**Description:** Repairs a specific directory within a domain.  
**Agents:** enforcer_agent, coder_agent  
**Workflow:** scan directory → repair → validate

### `/repair-file <path>`
**Description:** Repairs a single file.  
**Agents:** coder_agent  
**Workflow:** targeted fix → validate

---

## 3. Validation Commands

### `/validate`
**Description:** Performs full strict validation across the entire repository.  
**Agents:** enforcer_agent  
**Workflow:** scan → validate → return PASS/FAIL

### `/validate-domain <domain>`
**Description:** Validates a specific EE domain.  
**Agents:** enforcer_agent  
**Workflow:** scan domain → validate → return PASS/FAIL

### `/validate-directory <domain>/<directory>`
**Description:** Validates a specific directory.  
**Agents:** enforcer_agent  
**Workflow:** scan directory → validate

### `/validate-file <path>`
**Description:** Validates a single file.  
**Agents:** enforcer_agent  
**Workflow:** scan file → validate

### `/validate-sima`
**Description:** Validates SIMA structure, indexes, routers, and REF-IDs.  
**Agents:** maintenance_agent  
**Workflow:** run SIMA Workflow-06

### `/validate-architecture`
**Description:** Validates EE 2.1, UG-ISP, and AP-28 architecture rules.  
**Agents:** enforcer_agent  
**Workflow:** architecture validation

---

## 4. Upgrade Commands

### `/upgrade-ee21`
**Description:** Applies EE 2.1 upgrade patterns across the entire repository.  
**Agents:** coder_agent  
**Workflow:** apply EE21 → remove legacy → validate

### `/upgrade-domain <domain>`
**Description:** Upgrades a specific domain to EE 2.1.  
**Agents:** coder_agent  
**Workflow:** apply EE21 → validate → converge

### `/upgrade-directory <domain>/<directory>`
**Description:** Upgrades a specific directory.  
**Agents:** coder_agent  
**Workflow:** apply EE21 → validate

### `/upgrade-file <path>`
**Description:** Upgrades a single file.  
**Agents:** coder_agent  
**Workflow:** targeted EE21 upgrade → validate

---

## 5. Knowledge Commands

### `/summarize`
**Description:** Summarizes the current context, changes, or violations.  
**Agents:** knowledge_agent  
**Workflow:** generate summary

### `/explain <topic>`
**Description:** Explains any EE/SIMA concept.  
**Agents:** knowledge_agent  
**Workflow:** generate explanation

### `/context <path>`
**Description:** Provides SIMA context for a file or directory.  
**Agents:** knowledge_agent  
**Workflow:** retrieve context

### `/trace <path>`
**Description:** Traces violations, regressions, or rule failures.  
**Agents:** debug_agent  
**Workflow:** trace failure → generate report

---

## 6. CI / Automation Commands

### `/ci-run`
**Description:** Runs the full CI pipeline in strict mode.  
**Agents:** ci_agent  
**Workflow:** static analysis → repair cycle → validation → convergence

### `/ci-validate`
**Description:** Runs CI validation only.  
**Agents:** ci_agent  
**Workflow:** static analysis → validation

### `/ci-repair`
**Description:** Runs CI repair cycle.  
**Agents:** ci_agent  
**Workflow:** repair cycle

### `/ci-scan`
**Description:** Runs CI scanner and auto-extender.  
**Agents:** ci_agent  
**Workflow:** scan → extend scanner

### `/ci-convergence`
**Description:** Runs domain-by-domain convergence checks.  
**Agents:** ci_agent  
**Workflow:** validate convergence

---

## 7. Navigation Commands

### `/list-domains`
**Description:** Lists all EE domains.  
**Agents:** coordinator_agent  
**Workflow:** enumerate domains

### `/list-directories <domain>`
**Description:** Lists directories within a domain.  
**Agents:** coordinator_agent  
**Workflow:** enumerate directories

### `/list-violations`
**Description:** Lists all current violations.  
**Agents:** enforcer_agent  
**Workflow:** scan → list violations

### `/list-governance`
**Description:** Lists all governance files.  
**Agents:** coordinator_agent  
**Workflow:** enumerate governance

### `/list-agents`
**Description:** Lists all strict agents and their skills.  
**Agents:** coordinator_agent  
**Workflow:** enumerate agents

---

## 8. Maintenance Commands

### `/fix-structure`
**Description:** Repairs directory and SIMA structure.  
**Agents:** maintenance_agent  
**Workflow:** verify structure → repair

### `/fix-sima`
**Description:** Repairs SIMA entries, indexes, routers, and REF-IDs.  
**Agents:** maintenance_agent  
**Workflow:** run SIMA Workflow-06

### `/fix-indexes`
**Description:** Repairs SIMA indexes.  
**Agents:** maintenance_agent  
**Workflow:** index repair

### `/fix-routers`
**Description:** Repairs SIMA routers.  
**Agents:** maintenance_agent  
**Workflow:** router repair

### `/fix-refids`
**Description:** Repairs REF-ID inconsistencies.  
**Agents:** maintenance_agent  
**Workflow:** refid repair