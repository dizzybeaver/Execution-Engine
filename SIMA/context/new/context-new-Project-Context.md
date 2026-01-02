# context-new-Project-Context.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Create new project structure  
**Activation:** "Create New Project with {NAME}"  
**Type:** New Mode

---

## EXTENDS

[context-new-Context.md](context-new-Context.md) (Base scaffolding)

---

## WHAT THIS MODE IS

**New Project Mode** creates complete project structure in `/sima/projects/{name}/`.

**Purpose:** Scaffold new project with all required files.

**Outputs:** Project directory, configs, modes, indexes.

---

## PROJECT STRUCTURE

```
/sima/projects/{name}/
├── config/
│   ├── knowledge-config.yaml
│   └── project_config.md
├── modes/
│   ├── PROJECT-MODE-{NAME}.md
│   ├── DEBUG-MODE-{NAME}.md
│   └── Custom-Instructions-{NAME}.md
├── lessons/
├── decisions/
├── anti-patterns/
├── architecture/
├── indexes/
│   └── {name}-Index-Main.md
├── {NAME}-Architecture-Overview.md
└── README.md
```

---

## SCAFFOLDING WORKFLOW

### Step 1: Gather Information
```
Project name: {NAME}
Description: {BRIEF_DESCRIPTION}
Platform: (AWS, Generic, etc.)
Language: (Python, JavaScript, etc.)
Architectures: (SUGA, Other patterns)
```

### Step 2: Create Structure
```
mkdir -p /sima/projects/{name}/{config,modes,lessons,decisions,anti-patterns,architecture,indexes}
```

### Step 3: Generate Files
```
1. knowledge-config.yaml - Complete project config
2. project_config.md - Project overview
3. PROJECT-MODE-{NAME}.md - Project mode extension
4. DEBUG-MODE-{NAME}.md - Debug mode extension
5. Custom-Instructions-{NAME}.md - Custom instructions
6. {name}-Index-Main.md - Main index
7. {NAME}-Architecture-Overview.md - Architecture doc
8. README.md - Project README
```

### Step 4: Output All Artifacts
```
[Create 8 artifacts]
Brief chat: "{NAME} project scaffolded. 8 files created."
```

---

## CONFIGURATION TEMPLATE

**knowledge-config.yaml:**

```yaml
project:
  name: "{NAME}"
  description: "{DESCRIPTION}"
  version: "1.0.0"
  created: "2025-11-10"
  type: "{TYPE}"

knowledge:
  generic:
    enabled: true
    categories:
      - lessons
      - decisions
      - anti-patterns
      - specifications
  
  platforms:
    {platform}:
      enabled: true
  
  languages:
    {language}:
      enabled: true
      architectures:
        {architecture}: true

context:
  modes:
    - general
    - learning
    - maintenance
    - project
    - debug
  
  custom_instructions: true

file_access:
  include_paths:
    - "/sima/generic/"
    - "/sima/platforms/{platform}/"
    - "/sima/languages/{language}/"
    - "/sima/projects/{name}/"
```

---

## SUCCESS CRITERIA

**Project scaffolding complete when:**
- ✅ All 8 files created
- ✅ Directory structure complete
- ✅ Configs valid
- ✅ Mode extensions functional
- ✅ Indexes initialized
- ✅ Architecture documented
- ✅ README informative
- ✅ Ready for development

---

## NEXT STEPS FOR USER

**After scaffolding:**

```
Your project is ready!

1. Review generated files
2. Customize mode extensions
3. Add project-specific knowledge
4. Activate modes:
   - "Start Project Mode for {NAME}"
   - "Start Debug Mode for {NAME}"

Files created: 8 artifacts
Location: /sima/projects/{name}/
```

---

## READY

**Context loaded for new project scaffolding.**

---

**END OF NEW PROJECT MODE CONTEXT**

**Version:** 4.2.2-blank  
**Lines:** 150 (target achieved)  
**Purpose:** Scaffold new projects