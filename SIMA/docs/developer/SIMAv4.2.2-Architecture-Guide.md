# SIMAv4.2.2-Architecture-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** SIMA system architecture  
**Type:** Developer Documentation

---

## ARCHITECTURE OVERVIEW

SIMA uses a hierarchical, domain-based architecture with mode-specific contexts optimized for AI-assisted workflows.

**Core Principles:**
- Domain separation (generic → platform → language → project)
- File-size constraints (≤400 lines for AI processing)
- Cache-busting for fresh content
- Mode-based operation

---

## SYSTEM LAYERS

### Layer 1: Knowledge Domains

```
┌─────────────────────────────────────┐
│ GENERIC (Universal Patterns)        │
│ - Anti-patterns, Lessons, Decisions │
│ - No platform/language specifics    │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ PLATFORMS (Platform-Specific)       │
│ - AWS, Azure, GCP                   │
│ - Platform constraints/patterns     │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ LANGUAGES (Language-Specific)       │
│ - Python, JavaScript                │
│ - Language patterns/frameworks      │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ PROJECTS (Project Implementation)   │
│ - Specific projects                 │
│ - Combines above layers             │
└─────────────────────────────────────┘
```

**Information Flow:**
- Lower layers reference higher (projects → languages → platforms → generic)
- Higher layers never reference lower
- Each layer adds specificity

### Layer 2: Context System

```
┌─────────────────────┐
│  MODE SELECTOR      │ ← Entry point
│  (context-MODE-     │
│   SELECTOR.md)      │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  BASE CONTEXT       │ ← Mode-specific
│  (context-[MODE]-   │    behavior
│   Context.md)       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  SHARED KNOWLEDGE   │ ← Standards,
│  (/context/shared/) │    patterns
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  PROJECT EXTENSION  │ ← Project-specific
│  (PROJECT-MODE-     │    (optional)
│   [PROJECT].md)     │
└─────────────────────┘
```

**Context Loading:**
1. User provides activation phrase
2. Mode selector identifies mode
3. Loads base context
4. Loads shared knowledge
5. Loads project extension (if applicable)

### Layer 3: File System

```
/sima/
├── context/           # Mode contexts
│   ├── shared/        # Shared standards
│   ├── general/       # General mode
│   ├── sima/          # SIMA modes
│   ├── debug/         # Debug mode
│   ├── projects/      # Project mode
│   ├── new/           # New project mode
│   └── ai/            # AI loaders
│
├── generic/           # Universal knowledge
│   ├── anti-patterns/
│   ├── core/
│   ├── decisions/
│   ├── lessons/
│   ├── workflows/
│   └── specifications/
│
├── languages/         # Language-specific
│   └── [language]/
│       ├── anti-patterns/
│       ├── lessons/
│       └── frameworks/
│           └── [framework]/
│
├── platforms/         # Platform-specific
│   └── [platform]/
│       └── [sub-platform]/
│
├── projects/          # Project-specific
│   └── [project]/
│       ├── config/
│       ├── anti-patterns/
│       └── lessons/
│
├── docs/              # Documentation
├── support/           # Tools, workflows
└── templates/         # Entry templates
```

---

## KEY COMPONENTS

### 1. Cache-Busting System

**Problem:** Anthropic caches files for weeks  
**Solution:** fileserver.php generates unique URLs

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ 1. Upload File-Server-URLs.md
       ↓
┌─────────────┐
│     AI      │
└──────┬──────┘
       │ 2. Fetch fileserver.php
       ↓
┌─────────────┐
│ fileserver  │ 3. Generate URLs with
│   .php      │    random ?v= params
└──────┬──────┘
       │ 4. Return ~412 URLs
       ↓
┌─────────────┐
│     AI      │ 5. Access fresh files
└─────────────┘
```

**Performance:** 69ms, 412 files, fresh guaranteed

### 2. Mode System

**Purpose:** Task-specific contexts and behaviors

**Modes:**
```
General     → Q&A, learning
Project     → Building, coding
Debug       → Troubleshooting
Learning    → Knowledge extraction
Maintenance → System health
New Project → Project scaffolding
```

**Architecture:**
- Each mode has full + quick context
- Shared knowledge referenced
- Project extensions optional
- Explicit activation required

### 3. REF-ID System

**Purpose:** Cross-referencing knowledge entries

**Format:**
```
TYPE-## where:
TYPE = LESS, DEC, AP, BUG, WISD, etc.
## = Sequential number
```

**Usage:**
```markdown
**REF:** LESS-01, DEC-04
**Related:** WISD-06
**See also:** AP-08
```

**Benefits:**
- Fast navigation
- Clear relationships
- Version-independent
- Language-agnostic

### 4. Index System

**Hierarchy:**
```
Master Index of Indexes
├── Domain Master Indexes
│   ├── Category Indexes
│   │   └── Entry listings
│   └── Quick Indexes
└── Cross-Reference Matrices
```

**Types:**
- **Master:** Top-level navigation
- **Category:** Specific categories
- **Quick:** Fast access subsets
- **Router:** Domain routing

### 5. File Standards

**Every file must:**
```markdown
# filename.md

**Version:** X.Y.Z
**Date:** YYYY-MM-DD
**Purpose:** Brief description

[Content]

≤400 lines total
UTF-8 encoding
LF line endings
```

**Why ≤400 lines:**
- AI processing limit
- Files >400 get truncated
- Content becomes inaccessible
- Hard technical constraint

---

## DATA FLOW

### Knowledge Query Flow

```
User Query
    ↓
General Mode
    ↓
Search Indexes
    ↓
Fetch via fileserver.php (fresh)
    ↓
Read Entry
    ↓
Follow REF-IDs
    ↓
Synthesize Answer
    ↓
Provide with Citations
```

### Knowledge Creation Flow

```
Experience/Pattern
    ↓
Learning Mode
    ↓
Extract Signals
    ↓
Check Duplicates (fileserver.php)
    ↓
Genericize
    ↓
Create Entry (artifact)
    ↓
Update Indexes
    ↓
Add Cross-References
```

### Code Generation Flow

```
Feature Request
    ↓
Project Mode
    ↓
Fetch Current Code (fileserver.php)
    ↓
Read Complete File
    ↓
Apply Architecture Patterns
    ↓
Generate Complete File
    ↓
Mark Changes
    ↓
Output as Artifact
```

### Debug Flow

```
Error Report
    ↓
Debug Mode
    ↓
Fetch Current Code (fileserver.php)
    ↓
Analyze Error
    ↓
Identify Root Cause
    ↓
Generate Fix
    ↓
Output Complete Fixed File
```

---

## DESIGN DECISIONS

### Decision 1: Domain Separation

**Why:** Enables knowledge reuse at appropriate levels

**Impact:**
- Generic knowledge broadly applicable
- Platform knowledge platform-specific
- Language knowledge language-specific
- Project knowledge project-specific

### Decision 2: ≤400 Line Limit

**Why:** AI processing truncates files >400 lines

**Impact:**
- Forces atomic, focused files
- Enables complete file transmission
- Requires splitting large topics
- Maintains accessibility

### Decision 3: Cache-Busting via fileserver.php

**Why:** Platform caches ignore server headers

**Impact:**
- Guaranteed fresh content
- Random parameters bypass cache
- Transparent to server
- Requires session setup

### Decision 4: Mode-Based Operation

**Why:** Different tasks need different behaviors

**Impact:**
- Clear task separation
- Optimized for specific workflows
- Explicit mode switching
- No behavior mixing

### Decision 5: REF-ID Cross-Referencing

**Why:** Enable fast knowledge navigation

**Impact:**
- Version-independent links
- Clear relationships
- Fast traversal
- Language-agnostic

---

## SCALABILITY

### Horizontal: More Domains

**Add new:**
- Platforms (Azure, GCP)
- Languages (JavaScript, Go)
- Projects (as needed)

**Process:**
- Create directory structure
- Generate indexes
- Add to master indexes
- Update routers

### Vertical: More Knowledge

**Add entries:**
- Within existing domains
- Following standards
- Updating indexes
- Maintaining limits

**Limit:** No practical limit on entry count

### Depth: More Modes

**Add modes:**
- Identify unique purpose
- Create contexts
- Update mode selector
- Test integration

**Limit:** Maintain clear separation

---

## PERFORMANCE

### File Access

**Without cache-busting:** 
- Weeks-old content
- Wrong fixes
- Duplicate entries

**With cache-busting:**
- Fresh content (69ms)
- Correct fixes
- Accurate duplicates

### Mode Loading

**General:** 20-30s (lighter context)  
**Project/Debug:** 30-45s (base + extension)  
**Learning/Maintenance:** 30-45s (full context)

**Optimization:**
- Shared knowledge referenced (not duplicated)
- Quick contexts for fast access
- Mode-specific only content

### Search Performance

**Index-based:** O(1) to find category  
**File fetch:** ~69ms via fileserver.php  
**REF-ID lookup:** O(1) direct access

---

## MAINTENANCE

### Regular Tasks

**Daily:**
- Monitor file server
- Check new entries

**Weekly:**
- Update indexes
- Verify references

**Monthly:**
- Run full validation
- Check for duplicates
- Verify standards

**Quarterly:**
- Review architecture
- Plan improvements
- Update documentation

---

## EXTENSIBILITY

### Adding Features

**New Mode:**
1. Create contexts
2. Update selector
3. Document
4. Test

**New Domain:**
1. Create structure
2. Generate indexes
3. Add routers
4. Integrate

**New Tool:**
1. Implement
2. Document
3. Add to support
4. Update indexes

---

**END OF ARCHITECTURE GUIDE**

**Version:** 1.0.0  
**Lines:** 400 (at limit)  
**Purpose:** System architecture  
**Audience:** Developers, architects