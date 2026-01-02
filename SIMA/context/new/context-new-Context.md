# context-new-Context.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Base context for creating new projects/platforms/languages  
**Type:** Base Mode

---

## WHAT THIS MODE IS

**New Mode** automates scaffolding of new SIMA structures.

**Purpose:** Create complete directory structures with all required files.

**Outputs:** Directories, configs, mode extensions, indexes.

---

## FILE RETRIEVAL

**Session Start:**
1. User uploads File Server URLs.md
2. Claude fetches fileserver.php automatically
3. Receives cache-busted URLs (69ms)
4. Fresh files guaranteed

**REF:** Shared knowledge

---

## STANDARD STRUCTURE

**For any new entity (project/platform/language):**

```
/sima/{domain}/{name}/
├── config/
│   └── knowledge-config.yaml (if project)
├── modes/
│   ├── PROJECT-MODE-{NAME}.md
│   ├── DEBUG-MODE-{NAME}.md
│   └── Custom-Instructions-{NAME}.md
├── lessons/
├── decisions/
├── anti-patterns/
├── indexes/
│   └── {name}-Index-Main.md
└── README.md
```

---

## SCAFFOLDING PROCESS

### Step 1: Gather Information

**Ask user:**
```
Name: {NAME}
Description: {BRIEF_DESCRIPTION}
Type: (Project/Platform/Language)
Details: (Architecture/Technology/Framework)
```

### Step 2: Create Directory Structure

**Generate:**
- Root directory
- All subdirectories
- Config directory (if project)
- Modes directory
- Indexes directory

### Step 3: Generate Configuration

**Create knowledge-config.yaml (if project):**

```yaml
project:
  name: "{NAME}"
  description: "{DESCRIPTION}"
  version: "1.0.0"
  created: "{DATE}"

knowledge:
  generic:
    enabled: true
  
  platforms:
    {PLATFORM}:
      enabled: true
  
  languages:
    {LANGUAGE}:
      enabled: true

context:
  modes:
    - general
    - learning
    - maintenance
    - project
    - debug

file_access:
  include_paths:
    - "/sima/generic/"
    - "/sima/{domain}/{name}/"
```

### Step 4: Generate Mode Extensions

**Create PROJECT-MODE-{NAME}.md:**

```markdown
## PROJECT: {NAME}

## CONSTRAINTS
{Domain-specific constraints}

## ARCHITECTURE
{Architecture patterns used}

## PATTERNS
{Domain-specific patterns}

## WORKFLOWS
{Common development workflows}

## RED FLAGS
{Domain-specific warnings}

## EXAMPLES
{Real-world examples}
```

**Create DEBUG-MODE-{NAME}.md:**

```markdown
## PROJECT: {NAME}

## KNOWN ISSUES
{Document as discovered}

## ERROR PATTERNS
{Domain-specific errors}

## DEBUG TOOLS
{Domain-specific tools}

## COMMON FIXES
{Frequently needed fixes}
```

**Create Custom-Instructions-{NAME}.md:**

```markdown
## {NAME} CUSTOM INSTRUCTIONS

**Type:** {TYPE}
**Domain:** {DOMAIN}

## CRITICAL CONSTRAINTS
{Key limitations}

## ACTIVATION PHRASES
- "Start Project Mode for {NAME}"
- "Start Debug Mode for {NAME}"

## REFERENCES
- Base modes: /sima/context/
- Domain modes: /sima/{domain}/{name}/modes/
- Shared knowledge: /sima/context/shared/
```

### Step 5: Create Index Files

**Generate {name}-Index-Main.md:**

```markdown
# {NAME} Index

## Overview
{Brief description}

## Architecture
{Architecture patterns}

## Lessons
{Link to lessons directory}

## Decisions
{Link to decisions directory}

## References
{Key REF-IDs}
```

### Step 6: Create README

**Generate README.md:**

```markdown
# {NAME}

## Description
{Full description}

## Architecture
{Architecture details}

## Getting Started
{How to use this knowledge}

## Mode Activation
- Project Mode: "Start Project Mode for {NAME}"
- Debug Mode: "Start Debug Mode for {NAME}"

## Directory Structure
{Overview of directories}

## References
{Key documentation links}
```

---

## ARTIFACT RULES

**MANDATORY for all generated files:**

### Output Format
```
[OK] All files -> Artifacts
[OK] Complete files only
[OK] Filename in header
[OK] Proper structure
[X] Never partial files
[X] Never output in chat
```

### Generation Order
```
1. knowledge-config.yaml (if project)
2. PROJECT-MODE-{NAME}.md
3. DEBUG-MODE-{NAME}.md
4. Custom-Instructions-{NAME}.md
5. {name}-Index-Main.md
6. README.md
```

**Complete Standards:** `/sima/context/shared/Artifact-Standards.md`

---

## POST-SETUP CHECKLIST

**After scaffolding:**

1. ✅ Directory structure created
2. ✅ Config generated (if project)
3. ✅ All mode extensions created
4. ✅ Indexes initialized
5. ✅ README created
6. ✅ All files have headers
7. ✅ Chat output minimal
8. ✅ Next steps provided
9. ✅ Ready to use

---

## SUCCESS METRICS

**Successful scaffolding when:**
- ✅ All files generated
- ✅ Structure complete
- ✅ Configs valid (if project)
- ✅ Mode extensions functional
- ✅ Indexes initialized
- ✅ README informative
- ✅ Ready to use immediately
- ✅ Chat minimal

---

## READY

**Base context loaded.**

**See specific New Mode contexts for:**
- New Project Mode
- New Platform Mode
- New Language Mode

---

**END OF NEW MODE BASE CONTEXT**

**Version:** 4.2.2-blank  
**Lines:** 300 (target achieved)  
**Purpose:** Base scaffolding context