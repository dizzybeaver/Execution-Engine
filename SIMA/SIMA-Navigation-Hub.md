# SIMA-Navigation-Hub.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Primary navigation guide for SIMA system  
**Type:** Navigation Hub

---

## 🧭 WHAT IS THIS?

This is your **central navigation point** for the entire SIMA system. Use this file to quickly find what you need.

---

## 🚀 GETTING STARTED

### New to SIMA?
1. Read [README.md](/sima/README.md)
2. Review [SIMA-Quick-Reference-Card.md](/sima/SIMA-Quick-Reference-Card.md)
3. Check [docs/user/](/sima/docs/user/)

### Ready to Work?
1. Upload [File-Server-URLs.md](/sima/File-Server-URLs.md)
2. Activate appropriate mode
3. Start working

---

## 🎯 NAVIGATION BY TASK

### Task: Learn About SIMA
**What to Read:**
- [README.md](/sima/README.md) - System overview
- [docs/user/SIMAv4.2.2-User-Guide.md](/sima/docs/user/SIMAv4.2.2-User-Guide.md) - Complete user guide
- [docs/user/SIMAv4.2.2-Quick-Start-Guide.md](/sima/docs/user/SIMAv4.2.2-Quick-Start-Guide.md) - Quick start

**Activation:**
```
"Please load context"
```

---

### Task: Create Knowledge Entries
**What to Use:**
- [templates/](/sima/templates/) - Entry templates
- [support/workflows/](/sima/support/workflows/) - Creation workflows

**Activation:**
```
"Start SIMA Learning Mode"
```

---

### Task: Find Existing Knowledge
**What to Check:**
- [Master-Index-of-Indexes.md](/sima/Master-Index-of-Indexes.md) - All indexes
- [generic/](/sima/generic/) - Universal knowledge
- [languages/](/sima/languages/) - Language patterns
- [platforms/](/sima/platforms/) - Platform knowledge
- [projects/](/sima/projects/) - Project implementations

**Tools:**
- [support/tools/TOOL-01-REF-ID-Directory.md](/sima/support/tools/TOOL-01-REF-ID-Directory.md)
- [support/tools/TOOL-02-Quick-Answer-Index.md](/sima/support/tools/TOOL-02-Quick-Answer-Index.md)

---

### Task: Maintain Knowledge Base
**What to Use:**
- [support/checklists/](/sima/support/checklists/) - Maintenance checklists
- [support/tools/](/sima/support/tools/) - Maintenance tools
- [support/workflows/](/sima/support/workflows/) - Maintenance workflows

**Activation:**
```
"Start SIMA Maintenance Mode"
```

---

### Task: Build Features
**What to Use:**
- [projects/{PROJECT}/](/sima/projects/) - Project files
- [context/projects/](/sima/context/projects/) - Project mode contexts

**Activation:**
```
"Start Project Mode for {PROJECT}"
```

---

### Task: Debug Issues
**What to Use:**
- [context/debug/](/sima/context/debug/) - Debug mode contexts
- [projects/{PROJECT}/](/sima/projects/) - Project debug info

**Activation:**
```
"Start Debug Mode for {PROJECT}"
```

---

### Task: Create New Project
**What to Use:**
- [templates/project_config_template.md](/sima/templates/project_config_template.md)
- [templates/project_readme_template.md](/sima/templates/project_readme_template.md)

**Activation:**
```
"Start New Project Mode: {PROJECT_NAME}"
```

---

## 📂 NAVIGATION BY DOMAIN

### Context System
**Path:** [/sima/context/](/sima/context/)  
**Purpose:** Mode activation and system configuration  
**Index:** [context-Master-Index-of-Indexes.md](/sima/context/context-Master-Index-of-Indexes.md)

**Key Files:**
- MODE-SELECTOR.md - Mode routing
- shared/ - Shared standards
- general/ - General mode
- sima/ - SIMA-specific modes
- debug/ - Debug mode
- projects/ - Project mode

---

### Documentation
**Path:** [/sima/docs/](/sima/docs/)  
**Purpose:** Guides and documentation  
**Index:** [docs-Master-Index-of-Indexes.md](/sima/docs/docs-Master-Index-of-Indexes.md)

**Categories:**
- user/ - User guides
- developer/ - Developer guides
- install/ - Installation guides
- deployment/ - Deployment guides
- migration/ - Migration guides

---

### Generic Knowledge
**Path:** [/sima/generic/](/sima/generic/)  
**Purpose:** Universal patterns and principles  
**Index:** [generic-Master-Index-of-Indexes.md](/sima/generic/generic-Master-Index-of-Indexes.md)  
**Router:** [generic-Router.md](/sima/generic/generic-Router.md)

**Categories:**
- lessons/ - Universal lessons
- decisions/ - Generic decisions
- anti-patterns/ - What not to do
- core/ - Core architecture
- specifications/ - System specs

**Status:** Empty (ready for import)

---

### Languages
**Path:** [/sima/languages/](/sima/languages/)  
**Purpose:** Language-specific patterns  
**Index:** [languages-Master-Index-of-Indexes.md](/sima/languages/languages-Master-Index-of-Indexes.md)  
**Router:** [languages-Router.md](/sima/languages/languages-Router.md)

**Examples:**
- Python patterns
- JavaScript patterns
- TypeScript patterns

**Status:** Empty (ready for import)

---

### Platforms
**Path:** [/sima/platforms/](/sima/platforms/)  
**Purpose:** Platform-specific knowledge  
**Index:** [platforms-Master-Index-of-Indexes.md](/sima/platforms/platforms-Master-Index-of-Indexes.md)  
**Router:** [platforms-Router.md](/sima/platforms/platforms-Router.md)

**Examples:**
- AWS knowledge
- Azure knowledge
- GCP knowledge

**Status:** Empty (ready for import)

---

### Projects
**Path:** [/sima/projects/](/sima/projects/)  
**Purpose:** Project implementations  
**Index:** [projects-Master-Index-of-Indexes.md](/sima/projects/projects-Master-Index-of-Indexes.md)  
**Router:** [projects-Router.md](/sima/projects/projects-Router.md)

**Structure:**
- {project}/config/
- {project}/modes/
- {project}/lessons/
- {project}/decisions/

**Status:** Empty (ready for creation)

---

### Support
**Path:** [/sima/support/](/sima/support/)  
**Purpose:** Tools, workflows, utilities  
**Index:** [support-Master-Index-of-Indexes.md](/sima/support/support-Master-Index-of-Indexes.md)

**Categories:**

- checklists/ - Quality checklists
- quick-reference/ - Quick guides
- templates/ - Entry templates
- tools/ - Utility tools
- utilities/ - Helper utilities
- workflows/ - Common workflows
- governance/ - Strict governance system (agents, CI, scanner, state machine, repair cycle, activation, tracking, diagrams)
- checklists/ - Quality checklists
- quick-reference/ - Quick guides
- templates/ - Entry templates
- tools/ - Utility tools
- utilities/ - Helper utilities
- workflows/ - Common workflows

---

### Templates
**Path:** [/sima/templates/](/sima/templates/)  
**Purpose:** Entry and project templates  
**Index:** [templates-Master-Index.md](/sima/templates/templates-Master-Index.md)

**Types:**
- Entry templates (LESS, DEC, AP, etc.)
- Project templates
- Configuration templates

---

## 🎨 NAVIGATION BY MODE

### General Mode
**File:** [context/general/context-General-Mode-Context.md](/sima/context/general/context-General-Mode-Context.md)  
**Purpose:** Q&A, understanding, guidance  
**Activation:** `"Please load context"`

---

### Learning Mode
**File:** [context/sima/context-SIMA-LEARNING-MODE-Context.md](/sima/context/sima/context-SIMA-LEARNING-MODE-Context.md)  
**Purpose:** Extract and document knowledge  
**Activation:** `"Start SIMA Learning Mode"`

---

### Maintenance Mode
**File:** [context/sima/context-SIMA-MAINTENANCE-MODE-Context.md](/sima/context/sima/context-SIMA-MAINTENANCE-MODE-Context.md)  
**Purpose:** Update indexes, clean structure  
**Activation:** `"Start SIMA Maintenance Mode"`

---

### Project Mode
**File:** [context/projects/context-PROJECT-MODE-Context.md](/sima/context/projects/context-PROJECT-MODE-Context.md)  
**Purpose:** Active development  
**Activation:** `"Start Project Mode for {PROJECT}"`

---

### Debug Mode
**File:** [context/debug/context-DEBUG-MODE-Context.md](/sima/context/debug/context-DEBUG-MODE-Context.md)  
**Purpose:** Troubleshooting  
**Activation:** `"Start Debug Mode for {PROJECT}"`

---

### New Project Mode
**File:** [context/new/context-new-Context.md](/sima/context/new/context-new-Context.md)  
**Purpose:** Scaffold new projects  
**Activation:** `"Start New Project Mode: {NAME}"`

---

## 🔍 QUICK SEARCHES

### By REF-ID
**Tool:** [support/tools/TOOL-01-REF-ID-Directory.md](/sima/support/tools/TOOL-01-REF-ID-Directory.md)

**Format:**
- LESS-## - Lessons
- DEC-## - Decisions
- AP-## - Anti-patterns
- BUG-## - Bugs
- WISD-## - Wisdom

---

### By Keyword
**Tool:** [support/tools/TOOL-02-Quick-Answer-Index.md](/sima/support/tools/TOOL-02-Quick-Answer-Index.md)

**Common Keywords:**
- "Can I...?" - Check constraints
- "How do I...?" - Find workflows
- "Why...?" - Find decisions
- "What is...?" - Find explanations

---

### By Topic
**Use:** Domain routers
- [generic-Router.md](/sima/generic/generic-Router.md)
- [languages-Router.md](/sima/languages/languages-Router.md)
- [platforms-Router.md](/sima/platforms/platforms-Router.md)
- [projects-Router.md](/sima/projects/projects-Router.md)

---

## 📊 SYSTEM OVERVIEW

**Total Domains:** 8  
**Mode Contexts:** 6  
**Templates:** 12  
**Specifications:** 11  
**Support Tools:** 4

**Content Status:**
- Core system: ✅ Complete
- Knowledge: ❌ Empty (ready for import)

---

## 🔗 ESSENTIAL LINKS

**Root Files:**
- [README.md](/sima/README.md)
- [Master-Index-of-Indexes.md](/sima/Master-Index-of-Indexes.md)
- [SIMA-Quick-Reference-Card.md](/sima/SIMA-Quick-Reference-Card.md)
- [File-Server-URLs.md](/sima/File-Server-URLs.md)

**Documentation:**
- [User Guide](/sima/docs/user/SIMAv4.2.2-User-Guide.md)
- [Quick Start](/sima/docs/user/SIMAv4.2.2-Quick-Start-Guide.md)
- [Developer Guide](/sima/docs/developer/SIMAv4.2.2-Developer-Guide.md)

**Templates:**
- [All Templates](/sima/templates/templates-Master-Index.md)

---

**END OF NAVIGATION HUB**

**Purpose:** Central navigation point  
**Scope:** Entire SIMA system  
**Type:** Master navigation file