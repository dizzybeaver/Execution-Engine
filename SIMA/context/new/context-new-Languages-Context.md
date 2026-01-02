# context-new-Languages-Context.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Create new language structure  
**Activation:** "Create New Language with {NAME}"  
**Type:** New Mode

---

## EXTENDS

[context-new-Context.md](context-new-Context.md) (Base scaffolding)

---

## WHAT THIS MODE IS

**New Language Mode** creates complete language structure in `/sima/languages/{name}/`.

**Purpose:** Scaffold new language knowledge domain.

**Outputs:** Language directory, indexes, docs.

---

## LANGUAGE STRUCTURE

```
/sima/languages/{name}/
├── anti-patterns/
├── core/
├── decisions/
├── lessons/
├── wisdom/
├── workflows/
├── frameworks/ (for architecture patterns)
├── {name}-Router.md
├── {name}-Index.md
└── README.md
```

---

## SCAFFOLDING WORKFLOW

### Step 1: Gather Information
```
Language name: {NAME}
Description: {BRIEF_DESCRIPTION}
Type: (Compiled, Interpreted, etc.)
```

### Step 2: Create Structure
```
mkdir -p /sima/languages/{name}/{anti-patterns,core,decisions,lessons,wisdom,workflows,frameworks}
```

### Step 3: Generate Files
```
1. {name}-Router.md - Navigation router
2. {name}-Index.md - Main index
3. README.md - Language README
4. Category indexes (7 files)
```

### Step 4: Output All Artifacts
```
[Create 10 artifacts]
Brief chat: "{NAME} language scaffolded."
```

---

## SUCCESS CRITERIA

**Language scaffolding complete when:**
- ✅ All directories created
- ✅ Router functional
- ✅ Indexes initialized
- ✅ README informative
- ✅ Ready for knowledge

---

**END OF NEW LANGUAGE MODE CONTEXT**

**Version:** 4.2.2-blank  
**Lines:** 100 (compact)  
**Purpose:** Scaffold new languages