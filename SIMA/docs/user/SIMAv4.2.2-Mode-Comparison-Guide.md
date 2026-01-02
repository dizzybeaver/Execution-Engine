# SIMAv4.2.2-Mode-Comparison-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Detailed mode comparison and selection  
**Type:** User Documentation

---

## MODE OVERVIEW

SIMA has 6 operational modes, each optimized for specific tasks:

1. **General Mode** - Q&A and learning
2. **Project Mode** - Building and development
3. **Debug Mode** - Troubleshooting and fixes
4. **Learning Mode** - Knowledge extraction
5. **Maintenance Mode** - System maintenance
6. **New Project Mode** - Project scaffolding

---

## COMPARISON TABLE

| Feature | General | Project | Debug | Learning | Maintenance | New Project |
|---------|---------|---------|-------|----------|-------------|-------------|
| **Purpose** | Understand | Build | Fix | Document | Clean | Setup |
| **Activation** | "Please load context" | "Start Project Mode for [PROJECT]" | "Start Debug Mode for [PROJECT]" | "Start SIMA Learning Mode" | "Start SIMA Maintenance Mode" | "Start New Project Mode: [NAME]" |
| **Load Time** | 20-30s | 30-45s | 30-45s | 30-45s | 30-45s | 30-45s |
| **Outputs** | Answers | Code | Fixes | Entries | Updates | Structure |
| **Artifacts** | Minimal | Always | Always | Always | Always | Always |
| **Chat** | Conversational | Minimal | Minimal | Minimal | Minimal | Minimal |
| **Scope** | All knowledge | Project-specific | Project-specific | Generic extraction | All SIMA | New structures |

---

## GENERAL MODE

### Purpose
Ask questions, learn about system, understand architecture, explore knowledge base.

### When to Use
- "How does X work?"
- "Can I use Y?"
- "Why is Z designed this way?"
- "Explain [CONCEPT]"
- General exploration

### Capabilities
- Searches all knowledge domains
- Provides answers with REF-ID citations
- Explains patterns and decisions
- Guides architectural understanding
- References specifications and standards

### Limitations
- Doesn't write code (use Project Mode)
- Doesn't fix bugs (use Debug Mode)
- Doesn't create entries (use Learning Mode)
- Read-only knowledge access

### Output Style
**Chat:** Conversational explanations  
**Citations:** Always includes REF-IDs  
**Artifacts:** Only for code examples >20 lines

### Example Session
```
User: "How does the gateway pattern work?"

Claude: "The gateway pattern provides a single entry point for all 
operations. [explains with GATE-01, ARCH-01 citations]"

User: "Can I import core directly?"

Claude: "No. RULE-01 requires all cross-interface access via gateway. 
Direct core imports violate architecture (AP-01)."
```

---

## PROJECT MODE

### Purpose
Active development: building features, writing code, implementing functionality.

### When to Use
- "Add feature X"
- "Implement Y"
- "Create new Z"
- "Modify file to support W"
- Any code generation task

### Capabilities
- Writes complete code files
- Follows project architecture
- Applies project-specific patterns
- Marks changes clearly
- Verifies against standards
- Uses project constraints

### Limitations
- Requires project name
- Needs project extension file
- Not for debugging (use Debug Mode)
- Not for Q&A (use General Mode)

### Output Style
**Chat:** Minimal status updates  
**Artifacts:** Complete code files always  
**Marking:** # ADDED:, # MODIFIED: comments

### Example Session
```
User: "Start Project Mode for SIMA"
User: "Add new mode context file"

Claude: "Creating mode context file..."
[Outputs complete file as artifact with proper headers]
"File ready. 250 lines. All standards met."
```

---

## DEBUG MODE

### Purpose
Troubleshooting: finding root causes, analyzing errors, providing fixes.

### When to Use
- "Error X occurring"
- "Bug in Y"
- "Performance issue with Z"
- "Why is W failing?"
- Any debugging task

### Capabilities
- Root cause analysis
- Error pattern recognition
- Fetches fresh code via fileserver.php
- Creates complete fix artifacts
- Verifies fixes address root cause
- Uses project-specific debug knowledge

### Limitations
- Requires project name
- Needs project extension file
- Not for feature addition (use Project Mode)
- Not for Q&A (use General Mode)

### Output Style
**Chat:** Analysis and findings  
**Artifacts:** Complete fixed files  
**Marking:** # FIXED: comments

### Example Session
```
User: "Start Debug Mode for SIMA"
User: "Mode won't activate with phrase"

Claude: "Analyzing activation system...
Root cause: Case sensitivity in phrase matcher.
Creating fix artifact..."
[Outputs complete fixed file]
"Fix verified. Test with failing case."
```

---

## LEARNING MODE

### Purpose
Knowledge extraction: creating neural map entries from experiences, patterns, decisions.

### When to Use
- "Extract lessons from this conversation"
- "Document this pattern"
- "Create entry for this decision"
- "Capture this wisdom"
- Documenting any new knowledge

### Capabilities
- Recognizes 7 signal types
- Checks for duplicates via fileserver.php
- Genericizes automatically
- Creates LESS/AP/DEC/BUG/WISD entries
- Updates indexes
- Maintains quality standards

### Limitations
- Only creates knowledge entries
- Not for code generation (use Project Mode)
- Not for fixes (use Debug Mode)
- Requires source material

### Output Style
**Chat:** Brief extraction status  
**Artifacts:** Complete neural map entries  
**Count:** 3-5 entries per session typical

### Example Session
```
User: "Start SIMA Learning Mode"
User: [provides conversation log]

Claude: "Extracting knowledge...
Checking duplicates...
Creating 3 artifacts..."
[LESS-## entry]
[DEC-## entry]
[AP-## entry]
"3 entries created. Topics: [list]"
```

---

## MAINTENANCE MODE

### Purpose
System maintenance: updating indexes, verifying references, cleaning structure.

### When to Use
- "Update all indexes"
- "Check for broken references"
- "Remove outdated entries"
- "Verify cross-references"
- Periodic system health

### Capabilities
- Scans all directories
- Updates index files
- Checks REF-ID validity
- Finds broken links
- Identifies duplicates
- Verifies standards compliance

### Limitations
- Doesn't create new knowledge (use Learning Mode)
- Doesn't generate code (use Project Mode)
- Maintenance tasks only

### Output Style
**Chat:** Progress updates  
**Artifacts:** Updated indexes, reports  
**Summary:** Changes made

### Example Session
```
User: "Start SIMA Maintenance Mode"
User: "Update lesson indexes"

Claude: "Scanning directories...
Creating index artifacts..."
[4 index files as artifacts]
"Summary:
- Core: 8 entries
- Operations: 18 entries
- Total: 42 lessons indexed"
```

---

## NEW PROJECT MODE

### Purpose
Project scaffolding: creating complete project structure with all required files.

### When to Use
- "Create new project [NAME]"
- "Set up new platform [NAME]"
- "Initialize new language [NAME]"
- First-time project setup

### Capabilities
- Creates directory structure
- Generates config files
- Creates mode extensions
- Initializes indexes
- Generates README
- Creates integration guides

### Limitations
- One-time setup only
- Can't modify existing projects
- Requires project name
- Generic templates only

### Output Style
**Chat:** Progress through steps  
**Artifacts:** All structure files  
**Count:** 7+ files generated

### Example Session
```
User: "Start New Project Mode: MyProject"

Claude: "Creating project structure...
[config file artifact]
[mode extension artifacts]
[index artifacts]
[README artifact]
"Project ready. 7 files created.
Location: /sima/projects/myproject/
Activate: 'Start Project Mode for MyProject'"
```

---

## MODE SELECTION GUIDE

### By Task Type

**Understanding:**
→ General Mode

**Creating:**
- Code: Project Mode
- Knowledge: Learning Mode
- Project: New Project Mode

**Fixing:**
→ Debug Mode

**Maintaining:**
→ Maintenance Mode

### By Question

**"How does...?"** → General Mode  
**"Can I...?"** → General Mode  
**"Build X"** → Project Mode  
**"Error Y"** → Debug Mode  
**"Document Z"** → Learning Mode  
**"Update indexes"** → Maintenance Mode  
**"Create new W"** → New Project Mode

### By Output Needed

**Explanation** → General Mode  
**Code** → Project Mode  
**Fix** → Debug Mode  
**Entry** → Learning Mode  
**Index** → Maintenance Mode  
**Structure** → New Project Mode

---

## MODE SWITCHING

### Same Session
Can switch modes in same session:
```
"Start Project Mode for X" → work → "Start Debug Mode for X" → fix
```

### Between Projects
Can switch projects:
```
"Start Project Mode for X" → work → "Start Project Mode for Y" → work
```

### Explicit Only
Must explicitly activate each mode. AI won't guess.

---

## BEST PRACTICES

### Mode Selection
1. Identify task type
2. Check table above
3. Use exact activation phrase
4. Confirm mode loaded
5. Begin work

### During Work
- Stay in one mode for coherent work
- Switch modes for different tasks
- Don't mix behaviors
- Use transitions when switching

### Quality
- Each mode has specific standards
- Follow mode-specific guidelines
- Use mode-appropriate outputs
- Verify results

---

**END OF MODE COMPARISON**

**Version:** 1.0.0 (Initial release)  
**Lines:** 400 (at limit)  
**Purpose:** Detailed mode reference  
**Companion:** [Quick Guide](SIMAv4.2.2-Mode-Comparison-Quick-Guide.md)