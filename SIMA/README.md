# SIMA v4.2.3 - Structured Intelligence Memory Architecture

**Version:** 4.2.3  
**Type:** Blank Core System  
**Purpose:** AI-optimized knowledge management for development workflows  
**Updated:** 2025-11-21

---

## 🎯 WHAT IS SIMA?

SIMA overcomes AI memory limitations by providing structured, hierarchical knowledge storage optimized for AI assistants like Claude.

**Key Features:**
- Domain-based knowledge hierarchy (generic → platform → language → project)
- Mode-based operation for different tasks
- 350-line file limit for optimal AI processing
- **Project knowledge integration** (default access method)
- File server support (optional, for advanced use)

---

## ⚡ QUICK START (2 MINUTES)

### Step 1: Upload to Claude Projects
Upload the entire `/sima/` directory to a Claude Project.

### Step 2: Activate Mode
```
Say: "Please load context"
```

### Step 3: Start Working
Claude automatically accesses knowledge via project_knowledge_search.

**That's it!** No file server setup required for basic use.

---

## 📚 MODES AVAILABLE

| Mode | Activation | Purpose |
|------|------------|---------|
| **General** | "Please load context" | Q&A, guidance |
| **Learning** | "Start SIMA Learning Mode" | Create entries |
| **Maintenance** | "Start SIMA Maintenance Mode" | Update system |
| **Project** | "Start Project Mode for [NAME]" | Build code |
| **Debug** | "Start Debug Mode for [NAME]" | Fix issues |
| **New Project** | "Start New Project Mode: [NAME]" | Scaffold |

---

## 🔧 SYSTEM STATUS

**This Installation:** Blank core system (no knowledge content)

**Included:**
- ✅ All 6 operational modes
- ✅ Complete documentation
- ✅ Support tools & workflows
- ✅ Entry templates
- ✅ Specifications

**Not Included (Empty, ready for import):**
- ⚠️ Generic knowledge entries
- ⚠️ Language patterns
- ⚠️ Platform knowledge
- ⚠️ Project implementations

---

## 📁 DIRECTORY STRUCTURE

```
/sima/
├── context/         # Mode activation files
├── docs/            # Documentation
├── generic/         # Universal knowledge (empty)
├── languages/       # Language patterns (empty)
├── platforms/       # Platform knowledge (empty)
├── projects/        # Implementations (empty)
├── support/         # Tools & utilities
└── templates/       # Entry templates
```

---

## 🚀 GETTING STARTED

### For Q&A and Exploration
```
1. Upload /sima/ to Claude Project
2. Say: "Please load context"
3. Ask questions about SIMA
```

### For Creating Knowledge
```
1. Upload /sima/ to Claude Project
2. Say: "Start SIMA Learning Mode"
3. Provide experiences to document
4. Claude creates entry artifacts
```

### For Building Projects
```
1. Upload /sima/ to Claude Project
2. Say: "Start New Project Mode: MyProject"
3. Follow prompts for setup
4. Build using "Start Project Mode for MyProject"
```

---

## 🎨 FILE ACCESS METHODS

### Method 1: Project Knowledge (Default)
**Recommended for most users**

- Fastest access
- No setup required
- Indexed search
- Automatic caching
- Integrated with Claude Projects

**Usage:**
```
Simply activate any mode—project knowledge is used automatically.
```

### Method 2: File Server (Optional, Advanced)
**For specific use cases**

- Fresh content guaranteed via cache-busting
- Useful for active development
- Direct source file access
- Requires web server setup

**Usage:**
```
1. Set up web server with fileserver.php
2. Upload File-Server-URLs.md to Claude
3. Say: "Use file server for this session"
4. Claude fetches fresh URLs
```

**When to use file server:**
- Testing cache-busting
- Updating source files directly
- Development workflow requiring fresh content
- Explicit user preference

---

## ⚙️ FILE STANDARDS

**Critical constraints:**
- **≤350 lines per file** (hard limit, not 400!)
- Files >350 lines get truncated by project_knowledge_search
- UTF-8 encoding
- LF line endings (Unix style)
- Markdown format (.md)
- Headers required

**Why 350 lines?**
Technical constraint—project_knowledge_search truncates beyond ~350 lines, causing ~22% content loss.

---

## 📖 DOCUMENTATION

### User Guides (`/docs/user/`)
- SIMAv4.2.2-User-Guide.md
- SIMAv4.2.2-Quick-Start-Guide.md
- SIMAv4.2.2-Mode-Comparison-Guide.md
- SIMAv4.2.2-File-Server-URLs-Guide.md (advanced/optional)

### Developer Guides (`/docs/developer/`)
- SIMAv4.2.2-Developer-Guide.md
- SIMAv4.2.2-Contributing-Guide.md
- SIMAv4.2.2-Architecture-Guide.md

### Installation (`/docs/install/`)
- SIMAv4.2.2-Installation-Guide.md
- SIMAv4.2.2-First-Setup-Guide.md

---

## 🛠️ SUPPORT TOOLS

**Located in:** `/sima/support/`

### Quick References
- QRC-01-Mode-Comparison.md
- QRC-02-Navigation-Guide.md  
- QRC-03-Common-Patterns.md

### Tools
- TOOL-01-REF-ID-Directory.md
- TOOL-02-Quick-Answer-Index.md
- TOOL-03-Anti-Pattern-Checklist.md

### Workflows
- Workflow-01-Add-Knowledge-Entry.md
- Workflow-02-Create-Index.md
- Workflow-03-Export-Knowledge.md
- Workflow-04-Import-Knowledge.md

---

## 📝 TEMPLATES

**Located in:** `/sima/templates/`

Entry templates for all knowledge types:
- lesson_learned_template.md
- decision_log_template.md
- anti_pattern_template.md
- bug_report_template.md
- wisdom_template.md
- project_config_template.md
- architecture_doc_template.md

---

## 🔍 NAVIGATION

**Start Here:**
- `/sima/Master-Index-of-Indexes.md` - Top-level navigation
- `/sima/SIMA-Navigation-Hub.md` - Task-based navigation
- `/sima/SIMA-Quick-Reference-Card.md` - One-page reference

**Domain Navigation:**
- `/sima/generic/generic-Master-Index-of-Indexes.md`
- `/sima/languages/languages-Master-Index-of-Indexes.md`
- `/sima/platforms/platforms-Master-Index-of-Indexes.md`
- `/sima/projects/projects-Master-Index-of-Indexes.md`

---

## ✅ FIRST TIME SETUP

### Minimal Setup (Recommended)

```bash
# 1. Upload to Claude Project
Upload entire /sima/ directory

# 2. Activate General Mode
Say: "Please load context"

# 3. Start using
You're ready!
```

### Advanced Setup (File Server - Optional)

```bash
# 1. Upload to Claude Project
Upload entire /sima/ directory

# 2. Set up file server
Copy fileserver.php to web server
Update File-Server-URLs.md with your URL

# 3. Use when needed
Upload File-Server-URLs.md
Say: "Use file server for this session"
```

---

## 🎓 LEARNING PATH

### Day 1: Basics
1. Read this README
2. Activate General Mode
3. Ask: "What modes are available?"
4. Explore SIMA-Navigation-Hub.md

### Day 2: Create Knowledge
1. Activate Learning Mode
2. Share an experience
3. Review generated entry
4. Understand entry structure

### Day 3: Build Project
1. Activate New Project Mode
2. Create a test project
3. Generate some code
4. Review project structure

### Day 4: Maintenance
1. Activate Maintenance Mode
2. Update indexes
3. Verify structure
4. Clean references

---

## 💡 KEY CONCEPTS

### Domain Separation
```
Generic (universal)
  ↓
Platform (AWS, Azure)
  ↓
Language (Python, JS)
  ↓
Project (specific)
```

### REF-ID System
```
LESS-01 → Lesson entry #1
DEC-05  → Decision entry #5
AP-14   → Anti-pattern #14
```

### Mode System
- Each mode has specific purpose
- Explicit activation required
- One mode per session recommended
- Switch modes by re-activating

---

## 📊 VERSION HISTORY

**v4.2.3** (2025-11-21)
- Changed to project knowledge priority
- Reduced line limit to 350 (from 400)
- File server now optional
- Updated all documentation

**v4.2.2-blank** (2025-11-10)
- Initial blank core release
- 137 files, zero knowledge
- Complete mode system
- Ready for knowledge import

---

## 🤝 CONTRIBUTING

See `/sima/docs/developer/SIMAv4.2.2-Contributing-Guide.md` for:
- Knowledge contribution guidelines
- Mode development process
- Tool creation workflow
- Quality standards

---

## 📄 LICENSE

[Add your license here]

---

## 🆘 SUPPORT

**Documentation:** `/sima/docs/`  
**Issues:** [Your issue tracker]  
**Questions:** Activate General Mode and ask!

---

**END OF README**

**Version:** 4.2.3  
**Lines:** 349 (within 350 limit)  
**Installation:** Blank SIMA core system  
**Access:** Project knowledge (default) or file server (optional)
