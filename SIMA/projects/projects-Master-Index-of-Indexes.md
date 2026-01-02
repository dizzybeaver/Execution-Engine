# projects-Master-Index-of-Indexes.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Master index for projects domain  
**Domain:** Projects (Project Implementations)  
**Status:** Empty (ready for creation)

---

## 📊 OVERVIEW

This domain contains **project-specific implementations** and knowledge for concrete software projects.

**Current Status:** Empty - ready for project creation

---

## 🏗️ PROJECT STRUCTURE

### Standard Project Layout
```
/sima/projects/
├── {project-name}/
│   ├── config/
│   │   └── knowledge-config.yaml
│   ├── modes/
│   │   ├── PROJECT-MODE-{PROJECT}.md
│   │   ├── DEBUG-MODE-{PROJECT}.md
│   │   └── Custom-Instructions-{PROJECT}.md
│   ├── architecture/
│   ├── decisions/
│   ├── lessons/
│   ├── interfaces/ (optional)
│   ├── function-references/ (optional)
│   ├── indexes/
│   │   └── {project}-index-main.md
│   └── README.md
```

**Status:** No projects created yet

---

## 📂 EXPECTED PROJECTS

### Example Project Types

**Serverless Projects:**
- Lambda-based APIs
- Event-driven architectures
- Scheduled tasks

**Web Applications:**
- Frontend applications
- Backend services
- Full-stack apps

**Integration Projects:**
- Service connectors
- API integrations
- Data pipelines

**Status:** No projects defined yet

---

## 🎯 CONTENT RULES

### What Belongs Here
✅ Project-specific code patterns  
✅ Project architecture  
✅ Project decisions  
✅ Project lessons learned  
✅ Project configuration  
✅ Project integrations  

### What Does NOT Belong
❌ Generic patterns (→ generic/)  
❌ Language-agnostic patterns (→ generic/)  
❌ Platform-agnostic patterns (→ generic/)  
❌ Language syntax (→ languages/)  
❌ Platform features (→ platforms/)  

---

## 🏗️ CREATING NEW PROJECT

### Using New Project Mode

**Activation:**
```
"Start New Project Mode: {PROJECT_NAME}"
```

**Claude will create:**
- Project directory structure
- knowledge-config.yaml
- Mode extension files
- Index files
- README.md
- Integration guide

---

### Manual Creation Steps

1. **Create directory:** `/sima/projects/{project-name}/`
2. **Add config:** `knowledge-config.yaml`
3. **Create modes:** PROJECT-MODE and DEBUG-MODE extensions
4. **Add README:** Project overview
5. **Initialize indexes:** Create main index
6. **Document architecture:** Architecture overview

---

## 🔍 NAVIGATION

### By Project
Browse project-specific index for each project

### By Category (within project)
- Architecture
- Decisions
- Lessons
- Interfaces
- Function references

### By Router
Use [projects-Router.md](/sima/projects/projects-Router.md) for project discovery

---

## 📈 STATISTICS

**Total Projects:** 0  
**Active Projects:** 0  
**Archived Projects:** 0  

**By Type:**
- Serverless: 0
- Web Apps: 0
- Integrations: 0
- Other: 0

---

## ✅ QUALITY STANDARDS

All project entries must:
- Be project-specific (not generic)
- Follow file standards (≤400 lines, UTF-8, LF)
- Include proper headers
- Use REF-IDs with project prefix ({PROJECT}-LESS-##)
- Reference generic/language/platform knowledge
- Document dependencies
- Have 4-8 keywords
- Link 3-7 related topics

---

## 🔧 PROJECT CONFIGURATION

### knowledge-config.yaml

**Required Fields:**
```yaml
project:
  name: "ProjectName"
  description: "Brief description"
  version: "1.0.0"
  created: "YYYY-MM-DD"

knowledge:
  generic:
    enabled: true
  
  platforms:
    {platform}:
      enabled: true
  
  languages:
    {language}:
      enabled: true
```

**See:** `/templates/project_config_template.md`

---

## 🎨 PROJECT MODES

### Project Mode
**Purpose:** Active development for specific project  
**File:** `modes/PROJECT-MODE-{PROJECT}.md`  
**Activation:** `"Start Project Mode for {PROJECT}"`

**Contains:**
- Project constraints
- Architecture patterns
- Red flags
- Examples

---

### Debug Mode
**Purpose:** Troubleshooting for specific project  
**File:** `modes/DEBUG-MODE-{PROJECT}.md`  
**Activation:** `"Start Debug Mode for {PROJECT}"`

**Contains:**
- Known bugs
- Error patterns
- Debug tools
- Common fixes

---

### Custom Instructions
**Purpose:** Project overview and quick reference  
**File:** `modes/Custom-Instructions-{PROJECT}.md`

**Contains:**
- Project summary
- Critical constraints
- Activation phrases
- References

---

## 🔗 RELATED FILES

- **Router:** [projects-Router.md](/sima/projects/projects-Router.md)
- **Generic Knowledge:** [generic-Master-Index-of-Indexes.md](/sima/generic/generic-Master-Index-of-Indexes.md)
- **Languages:** [languages-Master-Index-of-Indexes.md](/sima/languages/languages-Master-Index-of-Indexes.md)
- **Platforms:** [platforms-Master-Index-of-Indexes.md](/sima/platforms/platforms-Master-Index-of-Indexes.md)
- **Navigation:** [SIMA-Navigation-Hub.md](/sima/SIMA-Navigation-Hub.md)

---

## 🚀 GETTING STARTED

### First Project

**Quick Start:**
```
1. "Start New Project Mode: MyProject"
2. Answer Claude's questions
3. Review scaffolded structure
4. Begin development
```

**Manual Start:**
```
1. Create project directory
2. Copy config template
3. Create mode extensions
4. Initialize indexes
5. Document architecture
```

---

**END OF PROJECTS MASTER INDEX**

**Domain:** Projects (Implementations)  
**Status:** Empty (ready for creation)  
**Projects:** 0 (awaiting creation)  
**Next Step:** Create first project using New Project Mode