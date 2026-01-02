# SIMA-Quick-Reference-Card.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** One-page quick reference for SIMA  
**Type:** Quick Reference

---

## ⚡ INSTANT START

```
1. Upload File-Server-URLs.md
2. Say: "Please load context"
3. Start working
```

---

## 🎯 MODE ACTIVATION

| Mode | Phrase | Purpose |
|------|--------|---------|
| **General** | `"Please load context"` | Q&A, guidance |
| **Learning** | `"Start SIMA Learning Mode"` | Create entries |
| **Maintenance** | `"Start SIMA Maintenance Mode"` | Clean, update |
| **Project** | `"Start Project Mode for {NAME}"` | Build code |
| **Debug** | `"Start Debug Mode for {NAME}"` | Fix issues |
| **New Project** | `"Start New Project Mode: {NAME}"` | Scaffold |

---

## 📂 KEY DIRECTORIES

```
/context/    → Mode files
/docs/       → Documentation
/generic/    → Universal knowledge ⚠️ EMPTY
/languages/  → Language patterns ⚠️ EMPTY
/platforms/  → Platform knowledge ⚠️ EMPTY
/projects/   → Implementations ⚠️ EMPTY
/support/    → Tools, workflows
/templates/  → Entry templates
```

---

## 🔑 REF-ID TYPES

| Prefix | Type | Example |
|--------|------|---------|
| **LESS-##** | Lessons | LESS-01 |
| **DEC-##** | Decisions | DEC-05 |
| **AP-##** | Anti-patterns | AP-14 |
| **BUG-##** | Bugs | BUG-01 |
| **WISD-##** | Wisdom | WISD-06 |

---

## 📋 COMMON TASKS

### Create Entry
```
1. Activate Learning Mode
2. Provide content
3. Review artifact
4. Deploy to repository
```

### Find Entry
```
1. Check domain index
2. Use REF-ID if known
3. Search by keyword
4. Use router for topic
```

### Update Index
```
1. Activate Maintenance Mode
2. Request index update
3. Review artifact
4. Deploy to repository
```

---

## ⚠️ CRITICAL RULES

### File Standards
✅ ≤400 lines per file  
✅ UTF-8 encoding  
✅ LF line endings  
✅ Headers required  
❌ No trailing whitespace  

### Artifact Rules
✅ Code >20 lines → Artifact  
✅ Complete files only  
✅ Mark all changes  
❌ Never fragments  
❌ Never code in chat  

### Domain Rules
✅ Generic = No specifics  
✅ Language = One language  
✅ Platform = One platform  
✅ Project = Specific implementation  

---

## 🔍 QUICK SEARCHES

### By REF-ID
```
Use: /support/tools/TOOL-01-REF-ID-Directory.md
Format: LESS-##, DEC-##, AP-##, etc.
```

### By Keyword
```
Use: /support/tools/TOOL-02-Quick-Answer-Index.md
Search: "Can I...", "How do I...", "Why..."
```

### By Topic
```
Use: Domain routers
- /generic/generic-Router.md
- /languages/languages-Router.md
- /platforms/platforms-Router.md
- /projects/projects-Router.md
```

---

## 📚 ESSENTIAL DOCS

| Document | Path | Purpose |
|----------|------|---------|
| **README** | /README.md | System overview |
| **Navigation** | /SIMA-Navigation-Hub.md | Central nav |
| **Master Index** | /Master-Index-of-Indexes.md | All indexes |
| **User Guide** | /docs/user/ | Complete guide |
| **Templates** | /templates/ | Entry templates |

---

## 🎨 TEMPLATES

```
/templates/lesson_learned_template.md
/templates/decision_log_template.md
/templates/anti_pattern_template.md
/templates/bug_report_template.md
/templates/wisdom_template.md
/templates/nmp_entry-template.md
```

---

## 🔧 TOOLS

```
TOOL-01: REF-ID Directory
TOOL-02: Quick Answer Index
TOOL-03: Anti-Pattern Checklist
TOOL-04: Verification Protocol
```

Path: `/support/tools/`

---

## ✅ CHECKLISTS

```
Checklist-01: Code Review
Checklist-02: Deployment Readiness
Checklist-03: Documentation Quality
```

Path: `/support/checklists/`

---

## 📈 STATUS

**Version:** 4.2.2-blank  
**Type:** Clean Slate  
**Core System:** ✅ Complete  
**Knowledge:** ❌ Empty

**Ready For:**
- Knowledge import
- Entry creation
- Project scaffolding

---

## 🚨 RED FLAGS

| Issue | What | Fix |
|-------|------|-----|
| **>400 lines** | File too large | Split file |
| **No header** | Missing metadata | Add header |
| **CRLF** | Wrong line endings | Convert to LF |
| **Not UTF-8** | Wrong encoding | Convert to UTF-8 |
| **Fragments** | Incomplete code | Complete file |
| **Specifics in generic** | Wrong domain | Move file |

---

## 🎯 QUICK WINS

### First Entry
```
1. "Start SIMA Learning Mode"
2. Share: "Here's what I learned..."
3. Claude creates LESS-01
4. Done!
```

### First Project
```
1. "Start New Project Mode: MyProject"
2. Answer questions
3. Claude scaffolds structure
4. Done!
```

### Find Knowledge
```
1. Check Master-Index-of-Indexes.md
2. Navigate to domain
3. Use domain router
4. Find entry
```

---

## 💡 TIPS

- Upload File-Server-URLs.md EVERY session
- Use exact mode activation phrases
- One mode at a time
- Complete files always
- Mark changes clearly
- Update indexes after changes

---

## 🔗 QUICK LINKS

- [Full Navigation](/sima/SIMA-Navigation-Hub.md)
- [Master Index](/sima/Master-Index-of-Indexes.md)
- [User Guide](/sima/docs/user/SIMAv4.2.2-User-Guide.md)
- [Templates](/sima/templates/templates-Master-Index.md)

---

**END OF QUICK REFERENCE**

**Print This:** Keep handy during sessions  
**Update:** After system changes  
**Share:** With new SIMA users