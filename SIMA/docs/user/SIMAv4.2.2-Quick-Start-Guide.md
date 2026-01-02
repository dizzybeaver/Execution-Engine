# SIMAv4.2.2-Quick-Start-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Fast SIMA setup and usage  
**Type:** Quick Reference

---

## 5-MINUTE SETUP

### Step 1: Upload File Server URLs (10 seconds)
```
File: File-Server-URLs.md
Contains: https://fileserver.example.com/fileserver.php?v=0070
Action: Upload to Claude
```

### Step 2: Activate Mode (5 seconds)
```
For Q&A: "Please load context"
For building: "Start Project Mode for [PROJECT]"
For fixing: "Start Debug Mode for [PROJECT]"
For documenting: "Start SIMA Learning Mode"
```

### Step 3: Work (varies)
Mode loads → Perform task → Get output

---

## COMMON WORKFLOWS

### Workflow 1: Ask Question
```
1. Upload File-Server-URLs.md
2. Say: "Please load context"
3. Ask question
4. Get answer with REF-IDs
```

### Workflow 2: Build Feature
```
1. Upload File-Server-URLs.md
2. Say: "Start Project Mode for [PROJECT]"
3. Describe feature
4. Get complete code artifact
```

### Workflow 3: Fix Bug
```
1. Upload File-Server-URLs.md
2. Say: "Start Debug Mode for [PROJECT]"
3. Describe error
4. Get analysis + fix artifact
```

### Workflow 4: Document Lesson
```
1. Upload File-Server-URLs.md
2. Say: "Start SIMA Learning Mode"
3. Provide source material
4. Get neural map entries as artifacts
```

---

## MODE QUICK REFERENCE

| Mode | Phrase | Use For | Output |
|------|--------|---------|--------|
| General | "Please load context" | Q&A | Answers |
| Project | "Start Project Mode for [PROJECT]" | Building | Code |
| Debug | "Start Debug Mode for [PROJECT]" | Fixing | Fixes |
| Learning | "Start SIMA Learning Mode" | Documenting | Entries |
| Maintenance | "Start SIMA Maintenance Mode" | Cleaning | Updates |
| New Project | "Start New Project Mode: [NAME]" | Setup | Structure |

---

## FILE STANDARDS

**Every file must have:**
- Header (version, date, purpose)
- ≤400 lines
- UTF-8 encoding
- LF line endings

**Knowledge entries need:**
- Keywords (4-8)
- Related topics (3-7)
- REF-ID format (TYPE-##)

---

## NAVIGATION

**Start here:** `/sima/Master-Index-of-Indexes.md`  
**Quick access:** `/sima/SIMA-Quick-Reference-Card.md`  
**Hub:** `/sima/SIMA-Navigation-Hub.md`

**Domain indexes:**
- Generic: `/sima/generic/generic-Master-Index-of-Indexes.md`
- Languages: `/sima/languages/languages-Master-Index-of-Indexes.md`
- Platforms: `/sima/platforms/platforms-Master-Index-of-Indexes.md`
- Projects: `/sima/projects/projects-Master-Index-of-Indexes.md`

---

## CRITICAL RULES

### Rule 1: Always Upload File-Server-URLs.md
Every session. First action. No exceptions.

### Rule 2: Use Exact Activation Phrases
Mode won't activate without exact phrase.

### Rule 3: One Mode Per Task
Don't mix modes. Switch explicitly if needed.

### Rule 4: Check Indexes First
Before creating, check if it already exists.

### Rule 5: ≤400 Lines Always
Split files if they exceed limit.

---

## TROUBLESHOOTING

**Stale content?** Upload File-Server-URLs.md  
**Wrong mode?** Use exact activation phrase  
**Files too large?** Split into multiple files  
**Broken links?** Run Maintenance Mode  
**Duplicates?** Check before creating

---

## NEXT STEPS

**For more details:**
- [Full User Guide](SIMAv4.2.2-User-Guide.md)
- [Mode Comparison](SIMAv4.2.2-Mode-Comparison-Guide.md)
- [Installation Guide](../install/SIMAv4.2.2-Installation-Guide.md)

**To start using:**
1. Upload File-Server-URLs.md
2. Choose mode
3. Start working

---

**END OF QUICK START**

**Version:** 1.0.0 (Initial release)  
**Lines:** 130 (within 400 limit)  
**Purpose:** Fast setup and reference  
**Time to read:** 5 minutes