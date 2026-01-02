Claude Code Agent Orchestration

Version: 1.0.0  
Date: 2025-12-31  
Purpose: Define agents, skills, commands, and SIMA/EE integration rules for this project.  
Type: Agent Orchestration Configuration

1. Project context

Project root:  
d:\Code\Project\

Key directories:
- EE/  
  Execution Engine with Universal Gateway (UG)  
  EE/src/gateway/ — Universal Gateway implementation  
  EE/src/[domains]/ — Domain-specific implementations  
- SIMA/  
  SIMA Knowledge Storage Architecture root  
  SIMA/context/ — Context mode files  
  SIMA/docs/ — Documentation  
  SIMA/generic/ — Universal knowledge  
  SIMA/languages/ — Language-specific patterns  
  SIMA/platforms/ — Platform-specific knowledge  
  SIMA/projects/EE/ — EE project knowledge base  
  SIMA/support/ — Tools, workflows, templates, checklists  
  SIMA/templates/ — Entry templates  
- Plugins/ — Plugin directory (kept as-is)  
- Text/plan/ — Implementation plans  
- reports/ — Generated reports (date-structured)  
- CLAUDE.md — This file

EE Universal Gateway rules:
- UG is the only entry point for cross-component execution.  
- Interfaces must not import outside their package.  
- Factories are the concrete execution units.  
- Execution flow:  
  External Code → UG.execute_operation(route, payload) → Domain Gateway → Interface → Factory

2. SIMA integration rules

All agents MUST treat SIMA as the primary knowledge source.

SIMA start points:
- /SIMA/Master-Index-of-Indexes.md  
- /SIMA/SIMA-Quick-Reference-Card.md  
- /SIMA/SIMA-Navigation-Hub.md  
- /SIMA/context/context-MODE-SELECTOR.md  
- /SIMA/context/shared/Artifact-Standards.md  
- /SIMA/context/shared/File-Standards.md  
- /SIMA/context/shared/Encoding-Standards.md  
- /SIMA/context/shared/RED-FLAGS.md  
- /SIMA/context/shared/Common-Patterns.md  
- /SIMA/generic/specifications/SPEC-NAMING.md

EE project in SIMA:
- /SIMA/projects/EE/ — primary knowledge base for the Execution Engine

Global SIMA rules (all agents):
- Always load relevant SIMA context before major tasks.  
- Always respect REF-ID system (LESS/DEC/AP/BUG/WISD/SPEC/ARCH/GATE/INT).  
- Always use SIMA templates when creating new entries.  
- Always update indexes/routers when adding knowledge.  
- Always follow Artifact-Standards, File-Standards, Encoding-Standards, SPEC-NAMING, RED-FLAGS.

3. Agents (high-level roles)

The system uses six core agents. The Coordinator selects and orchestrates them.

3.1 Coordinator agent

Purpose:  
Top-level orchestrator. Interprets user intent, loads SIMA context, selects agents, and enforces convergence.

Responsibilities:
- Interpret user requests and map them to modes: General / Learning / Maintenance / Project / Debug / SIMA Project / Export / Import  
- Load SIMA context (indexes, specs, red flags, EE project docs)  
- Select appropriate agent: Coder, Debug, Knowledge, Maintenance  
- Route tasks with relevant context  
- Enforce strict convergence loop with Enforcer PASS required before completion

Key skills:
- load_sima_context  
- summarize_relevant_knowledge  
- select_agent  
- route_task  
- enforce_convergence_loop

3.2 Enforcer agent

Purpose:  
SIMA and EE compliance officer. Nothing is “done” until this agent passes the work.

Responsibilities:
- Validate artifacts against SIMA standards: Artifact-Standards, File-Standards, Encoding-Standards, SPEC-NAMING, RED-FLAGS  
- Validate file headers (version/date/purpose/type)  
- Validate file size (≤350 lines, never ≥400)  
- Validate encoding (UTF-8, LF)  
- Validate naming conventions  
- Validate cross-references and REF-IDs  
- Validate index/router completeness  
- Validate EE architecture rules (UG-only, interface isolation, factories as execution units)

Key skills:
- validate_artifact_against_sima  
- validate_file_headers  
- validate_file_size  
- validate_encoding  
- validate_naming  
- validate_cross_references  
- validate_ug_architecture  
- validate_index_completeness

Behavior:
- Returns only PASS or FAIL (+ reasons)  
- Must run after Coder, Knowledge, or Maintenance modifications  
- Coordinator must not allow completion unless Enforcer returns PASS

3.3 Coder agent

Purpose:  
Produces complete, deployable file artifacts. Never outputs code in chat.

Responsibilities:
- Fetch current file before any modification  
- Write complete file artifacts (no fragments, include all existing code)  
- Apply change markers: # ADDED:, # MODIFIED:, # FIXED:, # REMOVED:  
- Follow EE Universal Gateway architecture  
- Respect SIMA file standards and size limits  
- Split files as needed (≤350 lines target, never ≥400)  
- Implement new interfaces, factories, and domain gateways as required

Key skills:
- fetch_file  
- create_artifact  
- apply_change_markers  
- split_large_file  
- generate_interface  
- generate_factory  
- refactor_to_ug_pattern

Chat rule:  
Coder agent never outputs code in chat; it only writes artifacts.

3.4 Knowledge agent

Purpose:  
Maintains SIMA knowledge (especially /SIMA/projects/EE/).

Responsibilities:
- Create new entries: LESS / DEC / AP / BUG / WISD / ARCH / GATE / INT / SPEC  
- Use templates from /SIMA/templates/  
- Assign REF-IDs sequentially, no reuse  
- Update domain indexes, master indexes, routers  
- Extract lessons and decisions from code diffs, architecture changes, debug sessions

Key skills:
- create_sima_entry  
- update_sima_index  
- update_sima_router  
- extract_lessons_from_diff  
- extract_decisions_from_architecture

3.5 Maintenance agent

Purpose:  
Keeps SIMA and EE structure clean, consistent, and verifiable.

Responsibilities:
- Run SIMA Workflow-06-Verify-Structure.md  
- Detect and repair broken links, missing entries, index inconsistencies, naming violations, encoding issues, router issues, REF-ID mismatches

Key skills:
- scan_directory  
- verify_structure  
- repair_index  
- repair_router  
- repair_cross_references  
- repair_encoding

When to use:
- After imports  
- After large refactors  
- Before releases or major milestones

3.6 Debug agent

Purpose:  
Performs systematic root-cause analysis using EE’s UG architecture.

Responsibilities:
- Reproduce bugs using actual routes/payloads  
- Trace failing routes through UG → Domain Gateway → Interface → Factory  
- Identify root cause and propose minimal changes  
- Hand off implementation to Coder agent  
- Create BUG-## and DEC-## entries describing symptoms, root cause, fix, impact

Key skills:
- trace_ug_route  
- analyze_stack  
- identify_root_cause  
- propose_fix  
- create_bug_entry

4. Modes and routing

General Mode — “Please load context”  
Coordinator loads SIMA context and answers using existing knowledge with REF-IDs. Read-only.

Learning Mode — “Start SIMA Learning Mode”  
Coordinator → Knowledge agent.

Maintenance Mode — “Start SIMA Maintenance Mode”  
Coordinator → Maintenance agent.

Project Mode (EE) — “Start Project Mode for EE”  
Coordinator → Coder → Enforcer → Knowledge.

Debug Mode (EE) — “Start Debug Mode for EE”  
Coordinator → Debug agent → Coder → Enforcer → Knowledge.

SIMA Project Mode — “Start SIMA Project Mode”  
Coordinator → Knowledge + Maintenance.

Export / Import Modes  
Coordinator → Knowledge + Maintenance.

5. Red flags (hard stops)

1. Code in chat  
2. File fragments  
3. Files >350 lines  
4. Missing headers  
5. Broken encoding  
6. Skip file fetch  
7. Bare except  
8. Skip verification  
9. Guess without data  
10. Multiple changes when debugging  
11. Condensed topics  
12. Wrong output format

If any red flag is triggered, Enforcer returns FAIL and Coordinator must reroute or stop.

6. Convergence loop

User Request  
→ Coordinator  
→ (optional) Debug / Knowledge  
→ Coder (implementation)  
→ Enforcer (validation)  
→ if FAIL → Coder → Enforcer  
→ if PASS → Knowledge (LESS / DEC / BUG / etc.)  
→ Coordinator confirms completion

A task is only complete when:
1. Enforcer returns PASS  
2. SIMA entries and indexes are updated  
3. EE architecture rules remain intact

END OF FILE