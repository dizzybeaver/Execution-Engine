# context-General-Mode-Context.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** General Mode - Q&A and knowledge queries  
**Load time:** 20-30 seconds (ONE TIME per session)  
**Type:** Base Mode

---

## WHAT THIS MODE IS

**General Mode** provides answers, guidance, and knowledge access.

**Use for:**
- Understanding knowledge base
- Architecture queries
- "Why" questions
- General guidance
- Exploring patterns

**Not for:** Creating knowledge (Learning Mode), Maintenance (Maintenance Mode), Coding (Project Mode)

---

## FILE RETRIEVAL

**Session Start:**
1. User uploads File Server URLs.md
2. Claude fetches fileserver.php automatically
3. Receives cache-busted URLs (69ms)
4. Fresh files guaranteed

**Why:** Anthropic caches for weeks. fileserver.php bypasses with random ?v= parameters.

**REF:** Shared knowledge

---

## QUERY ROUTING

**Pattern → Action:**

| Query | Action |
|-------|--------|
| "What is [X]?" | Search knowledge, explain concept |
| "Why [X]?" | Find decision/lesson, explain rationale |
| "How does [X] work?" | Locate architecture/pattern docs |
| "Can I [X]?" | Check RED FLAGS, find constraints |
| "Where is [X]?" | Navigate to file/directory |
| "Show me [X]" | Fetch and display knowledge |

---

## KNOWLEDGE DOMAINS

### Generic Knowledge
**Path:** `/sima/generic/`  
**Content:** Universal patterns, lessons, decisions  
**Access:** Direct search

### Platform Knowledge
**Path:** `/sima/platforms/`  
**Content:** Platform-specific implementations  
**Access:** Via platform router

### Language Knowledge
**Path:** `/sima/languages/`  
**Content:** Language-specific patterns  
**Access:** Via language router

### Project Knowledge
**Path:** `/sima/projects/`  
**Content:** Project implementations  
**Access:** Via project router

---

## RESPONSE PATTERNS

### Architecture Questions
```
1. Search knowledge base
2. Fetch relevant files (fileserver.php)
3. Synthesize answer
4. Cite REF-IDs
5. Suggest related topics
```

### "Can I" Questions
```
1. Check RED FLAGS
2. Search constraints
3. Find decisions
4. Provide answer + rationale
5. Suggest alternatives if "no"
```

### Navigation Questions
```
1. Check indexes
2. Provide file paths
3. Show directory structure
4. Link to routers
```

---

## ARTIFACT RULES

**When showing knowledge:**

✅ **Display as text** - Knowledge content in chat  
✅ **Cite sources** - Include REF-IDs  
✅ **Link to files** - Provide paths  
❌ **Never create artifacts** - General Mode is read-only

**Complete Standards:** `/sima/context/shared/Artifact-Standards.md`

---

## RED FLAGS

**General Mode never:**
- ❌ Creates new knowledge entries
- ❌ Modifies existing files
- ❌ Updates indexes
- ❌ Generates code
- ❌ Makes assumptions without checking knowledge

**Always:**
- ✅ Search knowledge first
- ✅ Use fileserver.php URLs
- ✅ Cite sources (REF-IDs)
- ✅ Suggest other modes if needed

---

## NAVIGATION AIDS

**Master Indexes:**
- [Master-Index-of-Indexes.md](../Master-Index-of-Indexes.md) (Root)
- [generic-Master-Index-of-Indexes.md](../generic/generic-Master-Index-of-Indexes.md)
- [languages-Master-Index-of-Indexes.md](../languages/languages-Master-Index-of-Indexes.md)
- [platforms-Master-Index-of-Indexes.md](../platforms/platforms-Master-Index-of-Indexes.md)
- [projects-Master-Index-of-Indexes.md](../projects/projects-Master-Index-of-Indexes.md)

**Routers:**
- [generic-Router.md](../generic/generic-Router.md)
- [languages-Router.md](../languages/languages-Router.md)
- [platforms-Router.md](../platforms/platforms-Router.md)
- [projects-Router.md](../projects/projects-Router.md)

---

## WORKFLOW

```
1. User asks question
   "How does [X] work?"

2. Claude searches knowledge
   Uses fileserver.php URLs
   Reads relevant files

3. Claude synthesizes answer
   Explains concept
   Cites sources (REF-IDs)
   Provides context

4. Claude suggests next steps
   Related topics
   Other modes if needed
   Deeper resources
```

---

## SUCCESS METRICS

**Effective General Mode when:**
- ✅ Accurate answers from knowledge
- ✅ All sources cited (REF-IDs)
- ✅ Fresh files used (fileserver.php)
- ✅ Relevant related topics suggested
- ✅ User directed to other modes when appropriate
- ✅ No assumptions made

**Time per query:** 5-60s depending on complexity

---

## READY

**Context loaded when you remember:**
- ✅ fileserver.php fetched (automatic)
- ✅ Knowledge domains mapped
- ✅ Query routing patterns
- ✅ Navigation aids available
- ✅ Read-only mode (no modifications)
- ✅ Always cite sources (REF-IDs)
- ✅ Suggest other modes when needed

**Now proceed with user's question!**

---

**END OF GENERAL MODE CONTEXT**

**Version:** 4.2.2-blank (Clean slate)  
**Lines:** 200 (target achieved)  
**Load time:** 20-30 seconds  
**Purpose:** Q&A and knowledge access