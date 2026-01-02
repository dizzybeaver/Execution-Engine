# SIMAv4.2.2-User-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Complete SIMA user guide  
**Type:** User Documentation

---

## INTRODUCTION

SIMA (Structured Intelligence Memory Architecture) is a knowledge management system designed for AI-assisted development workflows.

### What SIMA Does

- **Organizes Knowledge** - Domain-based hierarchy (generic → platform → language → project)
- **Enables AI Context** - Mode-based system for different tasks
- **Prevents Token Waste** - ≤400 line files for optimal AI processing
- **Ensures Freshness** - fileserver.php cache-busting system

### Key Concepts

**Domain Separation:**
```
Generic (universal patterns)
  ↓
Platform (AWS, Azure, GCP)
  ↓
Language (Python, JavaScript)
  ↓
Project (specific implementations)
```

**File Standards:**
- Markdown format (.md)
- ≤400 lines per file
- UTF-8 encoding
- Headers required
- REF-ID cross-references

---

## GETTING STARTED

### 1. Upload File Server URLs

**File:** `File-Server-URLs.md`  
**Contains:** URL to fileserver.php  
**Action:** Upload at start of every session

```
https://fileserver.example.com/fileserver.php?v=0070
```

### 2. Activate a Mode

**Choose based on task:**

| Task | Mode | Phrase |
|------|------|--------|
| Learn/Ask | General | "Please load context" |
| Build | Project | "Start Project Mode for [PROJECT]" |
| Fix | Debug | "Start Debug Mode for [PROJECT]" |
| Document | Learning | "Start SIMA Learning Mode" |
| Clean | Maintenance | "Start SIMA Maintenance Mode" |
| Setup | New Project | "Start New Project Mode: [NAME]" |

### 3. Work in That Mode

Each mode provides specific capabilities and workflows.

---

## MODE DETAILS

### General Mode
**Purpose:** Q&A, learning, understanding  
**Activation:** "Please load context"  
**Output:** Answers with REF-ID citations  
**Use for:** Architecture questions, explanations, guidance

### Project Mode
**Purpose:** Building features, writing code  
**Activation:** "Start Project Mode for [PROJECT]"  
**Output:** Complete code artifacts  
**Use for:** Development, implementation, feature addition

### Debug Mode
**Purpose:** Troubleshooting, root cause analysis  
**Activation:** "Start Debug Mode for [PROJECT]"  
**Output:** Analysis + complete fix artifacts  
**Use for:** Errors, bugs, performance issues

### Learning Mode
**Purpose:** Extracting knowledge from experiences  
**Activation:** "Start SIMA Learning Mode"  
**Output:** LESS/BUG/DEC/WISD entries as artifacts  
**Use for:** Documenting lessons, patterns, decisions

### Maintenance Mode
**Purpose:** Keeping knowledge base healthy  
**Activation:** "Start SIMA Maintenance Mode"  
**Output:** Updated indexes, cleanup reports  
**Use for:** Updating indexes, verifying references, removing outdated entries

### New Project Mode
**Purpose:** Creating new project structure  
**Activation:** "Start New Project Mode: [NAME]"  
**Output:** Complete project structure with configs  
**Use for:** Setting up new projects, platforms, languages

---

## FILE ORGANIZATION

### Generic Knowledge
**Location:** `/sima/generic/`  
**Contains:** Universal patterns, not specific to any platform/language

**Categories:**
- anti-patterns/ - What NOT to do
- core/ - Core practices
- decisions/ - Generic decisions
- lessons/ - Lessons learned
- workflows/ - Generic workflows
- specifications/ - Standards (SPEC-*)

### Language Knowledge
**Location:** `/sima/languages/[LANGUAGE]/`  
**Contains:** Language-specific patterns and frameworks

**Structure:**
```
/languages/
└── [language]/
    ├── anti-patterns/
    ├── decisions/
    ├── lessons/
    ├── wisdom/
    ├── workflows/
    └── frameworks/
          └── [framework]/
```

### Platform Knowledge
**Location:** `/sima/platforms/[PLATFORM]/`  
**Contains:** Platform-specific implementations

**Structure:**
```
/platforms/
└── [platform]/
    ├── anti-patterns/
    ├── core/
    ├── decisions/
    ├── lessons/
    └── workflows/
```

### Project Knowledge
**Location:** `/sima/projects/[PROJECT]/`  
**Contains:** Project-specific knowledge and configs

**Structure:**
```
/projects/
└── [project]/
    ├── config/
    ├── anti-patterns/
    ├── core/
    ├── decisions/
    ├── lessons/
    └── workflows/
```

---

## NAVIGATION

### Indexes

**Master Indexes:**
- `/sima/Master-Index-of-Indexes.md` - Root navigation
- `/sima/context/context-Master-Index-of-Indexes.md` - Context indexes
- `/sima/generic/generic-Master-Index-of-Indexes.md` - Generic indexes
- `/sima/languages/languages-Master-Index-of-Indexes.md` - Language indexes
- `/sima/platforms/platforms-Master-Index-of-Indexes.md` - Platform indexes
- `/sima/projects/projects-Master-Index-of-Indexes.md` - Project indexes

**Quick Indexes:**
Each master index has a corresponding Quick Index for fast access.

### Routers

**Purpose:** Load appropriate context based on task  
**Location:** Each domain has a Router file  
**Example:** `generic-Router.md`, `languages-Router.md`

---

## WORKING WITH KNOWLEDGE

### Reading Knowledge

1. Navigate via indexes
2. Use REF-IDs for cross-referencing
3. Follow related topics

**Example:**
```
LESS-01 references DEC-04
DEC-04 references AP-08
AP-08 shows what NOT to do
```

### Adding Knowledge

**Via Learning Mode:**
1. Activate Learning Mode
2. Provide source material
3. AI extracts patterns
4. Creates entries as artifacts
5. Updates indexes

**Manually:**
1. Use templates from `/sima/templates/`
2. Follow naming conventions
3. Add to appropriate domain
4. Update indexes
5. Add cross-references

### Maintaining Knowledge

**Via Maintenance Mode:**
1. Activate Maintenance Mode
2. Specify task (update indexes, check references, etc.)
3. AI performs maintenance
4. Outputs updated files

---

## BEST PRACTICES

### Session Management

**Every Session:**
1. Upload File-Server-URLs.md
2. Activate appropriate mode
3. Work until task complete or low tokens
4. Create transition file if needed

### Knowledge Quality

**Standards:**
- Generic (no unnecessary project specifics)
- Unique (not duplicate)
- Brief (≤400 lines)
- Complete (all key info)
- Actionable (can be applied)
- Verifiable (testable)

### File Standards

**Always:**
- Headers with version, date, purpose
- UTF-8 encoding
- LF line endings
- ≤400 lines
- REF-IDs for cross-reference
- Keywords (4-8)
- Related topics (3-7)

---

## TROUBLESHOOTING

### Issue: Stale Content

**Symptom:** AI working with old code  
**Solution:** Ensure File-Server-URLs.md uploaded  
**Prevention:** Upload at every session start

### Issue: Mode Won't Activate

**Symptom:** Wrong behavior for task  
**Solution:** Use exact activation phrase  
**Example:** "Start Project Mode for SIMA" (not "Start SIMA project mode")

### Issue: Files Too Large

**Symptom:** Context truncated  
**Solution:** Split file into multiple ≤400 line files  
**Tool:** Maintenance Mode can identify oversized files

### Issue: Broken References

**Symptom:** REF-ID points to non-existent entry  
**Solution:** Use Maintenance Mode to verify references  
**Prevention:** Update references when moving/deleting entries

---

## SUPPORT

**Documentation:** `/sima/docs/`  
**Templates:** `/sima/templates/`  
**Tools:** `/sima/support/tools/`  
**Workflows:** `/sima/support/workflows/`

**Quick References:**
- [Quick Start Guide](SIMAv4.2.2-Quick-Start-Guide.md)
- [Mode Comparison](SIMAv4.2.2-Mode-Comparison-Guide.md)
- [File Server Guide](SIMAv4.2.2-File-Server-URLs-Guide.md)

---

**END OF USER GUIDE**

**Version:** 1.0.0 (Initial blank SIMA release)  
**Lines:** 290 (within 400 limit)  
**Type:** User Documentation  
**Audience:** End users