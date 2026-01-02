# projects-Router.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Navigation router for projects domain  
**Domain:** Projects (Project Implementations)  
**Status:** Empty (ready for creation)

---

## 🧭 WHAT IS THIS?

This router helps you navigate **project-specific implementations** and find project knowledge.

**Current Status:** Empty - awaiting project creation

---

## 🏗️ BROWSE PROJECTS

### No Projects Yet

**Status:** No projects created

**To Create First Project:**
```
"Start New Project Mode: {PROJECT_NAME}"
```

---

## 🔍 SEARCH BY PROJECT TYPE

### Serverless Projects
**Examples:**
- Lambda-based APIs
- Event-driven systems
- Scheduled tasks
- Serverless integrations

**Status:** No projects

---

### Web Applications
**Examples:**
- Frontend apps (React, Vue, etc.)
- Backend services (REST APIs)
- Full-stack applications

**Status:** No projects

---

### Integration Projects
**Examples:**
- Third-party API connectors
- Service integrations
- Data pipelines

**Status:** No projects

---

### Other Project Types
**Examples:**
- CLI tools
- Desktop applications
- Mobile applications
- Libraries/frameworks

**Status:** No projects

---

## 📂 STANDARD PROJECT STRUCTURE

### When Projects Exist

**Project Directory:**
```
/sima/projects/{project-name}/
├── config/              # Configuration
├── modes/               # Mode extensions
├── architecture/        # Architecture docs
├── decisions/           # Project decisions
├── lessons/             # Project lessons
├── interfaces/          # Interface catalogs
├── function-references/ # Function docs
├── indexes/             # Project indexes
└── README.md            # Project overview
```

---

## 🎯 PROJECT MODES

### Project Mode
**Purpose:** Active development  
**Activation:** `"Start Project Mode for {PROJECT}"`

**Use For:**
- Building features
- Writing code
- Creating implementations
- Extending functionality

---

### Debug Mode
**Purpose:** Troubleshooting  
**Activation:** `"Start Debug Mode for {PROJECT}"`

**Use For:**
- Finding root causes
- Analyzing errors
- Fixing bugs
- Performance issues

---

## 🔍 SEARCH BY TOPIC

### Architecture
**Look in:** {project}/architecture/  
**Find:** System design, patterns, diagrams

**Status:** No projects

---

### Decisions
**Look in:** {project}/decisions/  
**Find:** Technical choices, trade-offs, rationale

**Status:** No projects

---

### Lessons
**Look in:** {project}/lessons/  
**Find:** What worked, what failed, insights

**Status:** No projects

---

### Interfaces
**Look in:** {project}/interfaces/  
**Find:** API definitions, interface patterns

**Status:** No projects

---

### Functions
**Look in:** {project}/function-references/  
**Find:** Function catalogs, documentation

**Status:** No projects

---

## 🚀 CREATING A PROJECT

### Using New Project Mode

**Step 1: Activate Mode**
```
"Start New Project Mode: MyProject"
```

**Step 2: Provide Information**
```
Claude will ask:
- Project name
- Description
- Platform (AWS, Azure, GCP, etc.)
- Language (Python, JavaScript, etc.)
- Architectures (SUGA, etc.)
```

**Step 3: Review Structure**
```
Claude generates:
- Directory structure
- Configuration files
- Mode extensions
- Indexes
- README
- Integration guide
```

**Step 4: Begin Development**
```
"Start Project Mode for MyProject"
```

---

### Manual Project Creation

**Step 1: Create Directory**
```
/sima/projects/my-project/
```

**Step 2: Add Configuration**
```
config/knowledge-config.yaml
```

**Step 3: Create Mode Extensions**
```
modes/PROJECT-MODE-MyProject.md
modes/DEBUG-MODE-MyProject.md
modes/Custom-Instructions-MyProject.md
```

**Step 4: Initialize Documentation**
```
README.md
architecture/
decisions/
lessons/
indexes/
```

---

## 💡 PROJECT BEST PRACTICES

### Knowledge Organization
- Keep project-specific content here
- Reference generic patterns from /generic/
- Reference language patterns from /languages/
- Reference platform knowledge from /platforms/

### Naming Conventions
- REF-IDs: {PROJECT}-LESS-##, {PROJECT}-DEC-##
- Files: Use project prefix
- Directories: Clear, descriptive names

### Documentation
- Document architecture early
- Track decisions as made
- Capture lessons immediately
- Maintain indexes continuously

---

## 🔗 NAVIGATION AIDS

### By Purpose
- Creating: Use New Project Mode
- Developing: Use Project Mode
- Debugging: Use Debug Mode
- Understanding: Read project README

### By Knowledge Type
- Generic patterns → /generic/
- Language patterns → /languages/
- Platform knowledge → /platforms/
- Project implementation → /projects/{project}/

---

## ⚠️ REMEMBER

**Project-specific means:**
- ✅ Concrete implementation
- ✅ Project architecture
- ✅ Project decisions
- ✅ Project lessons

**NOT project-specific:**
- ❌ Universal patterns (→ generic/)
- ❌ Language syntax (→ languages/)
- ❌ Platform features (→ platforms/)

---

## 🎯 COMMON WORKFLOWS

### Start New Project
```
1. "Start New Project Mode: ProjectName"
2. Provide project details
3. Review generated structure
4. Begin development
```

### Work on Existing Project
```
1. "Start Project Mode for ProjectName"
2. Build features, write code
3. Document decisions/lessons
4. Update indexes
```

### Debug Project Issues
```
1. "Start Debug Mode for ProjectName"
2. Analyze error, find root cause
3. Apply fix
4. Document as lesson
```

---

## 📚 WHEN PROJECTS EXIST

**This router will show:**
- List of active projects
- Project types
- Quick links to project indexes
- Common tasks per project
- Related knowledge links

---

**END OF PROJECTS ROUTER**

**Domain:** Projects (Implementations)  
**Purpose:** Navigation and discovery  
**Status:** Empty (awaiting creation)  
**Next Step:** Create first project using New Project Mode