# context-new-Platform-Context.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Create new platform structure  
**Activation:** "Create New Platform with {NAME}"  
**Type:** New Mode

---

## EXTENDS

[context-new-Context.md](context-new-Context.md) (Base scaffolding)

---

## WHAT THIS MODE IS

**New Platform Mode** creates complete platform structure in `/sima/platforms/{name}/`.

**Purpose:** Scaffold new platform knowledge domain.

**Outputs:** Platform directory, indexes, docs.

---

## PLATFORM STRUCTURE

```
/sima/platforms/{name}/
├── anti-patterns/
├── core/
├── decisions/
├── lessons/
├── workflows/
├── {name}-Router.md
├── {name}-Index.md
└── README.md
```

---

## SCAFFOLDING WORKFLOW

### Step 1: Gather Information
```
Platform name: {NAME}
Description: {BRIEF_DESCRIPTION}
Type: (Cloud, On-Premise, etc.)
```

### Step 2: Create Structure
```
mkdir -p /sima/platforms/{name}/{anti-patterns,core,decisions,lessons,workflows}
```

### Step 3: Generate Files
```
1. {name}-Router.md - Navigation router
2. {name}-Index.md - Main index
3. README.md - Platform README
4. Category indexes (5 files)
```

### Step 4: Output All Artifacts
```
[Create 8 artifacts]
Brief chat: "{NAME} platform scaffolded."
```

---

## SUCCESS CRITERIA

**Platform scaffolding complete when:**
- ✅ All directories created
- ✅ Router functional
- ✅ Indexes initialized
- ✅ README informative
- ✅ Ready for knowledge

---

**END OF NEW PLATFORM MODE CONTEXT**

**Version:** 4.2.2-blank  
**Lines:** 100 (compact)  
**Purpose:** Scaffold new platforms