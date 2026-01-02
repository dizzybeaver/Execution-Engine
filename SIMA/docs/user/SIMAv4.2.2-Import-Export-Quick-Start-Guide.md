# SIMAv4.2.2-Import-Export-Quick-Start-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-12  
**Purpose:** Quick start guide for SIMA Import/Export  
**Type:** Quick Start Guide

---

## 🚀 QUICK START

SIMA Import/Export enables knowledge sharing between instances. Export creates portable packages, Import integrates them.

**Read time:** 3 minutes

---

## 📤 EXPORT IN 3 STEPS

### Step 1: Activate
```
"Start SIMA Export Mode"
```

### Step 2: Specify What to Export

**Option A - Entire Domain:**
```
"Export the generic domain"
"Export the platforms/aws domain"
```

**Option B - Specific Category:**
```
"Export all lessons from generic"
"Export all decisions from platforms/aws"
```

**Option C - By REF-ID:**
```
"Export LESS-01, LESS-05, DEC-03, and AP-02"
```

### Step 3: Share Package

Claude generates artifacts containing:
- `manifest.yaml` - Package metadata
- `import-instructions.md` - How to use
- `files/` - Knowledge entries
- `indexes/` - Category indexes

**Share these artifacts with recipient**

---

## 📥 IMPORT IN 3 STEPS

### Step 1: Activate
```
"Start SIMA Import Mode"
```

### Step 2: Provide Package

Copy/paste or upload the export package artifacts.

### Step 3: Resolve Any Conflicts

**REF-ID Collision?** (You have LESS-01, import has LESS-01)
- Auto-renumbered (import becomes LESS-25)

**Content Duplicate?** (Different IDs, same content)
- Choose: keep yours, keep import, or merge

**Missing Dependency?** (Import references file you don't have)
- Choose: import anyway, skip entry, or get dependency

**Done!** Claude imports, updates indexes, generates report.

---

## 💡 COMMON SCENARIOS

### Share Generic Patterns with Team

**You (Exporter):**
```
1. "Start SIMA Export Mode"
2. "Export the generic domain"
3. Share package artifacts
```

**Teammate (Importer):**
```
1. "Start SIMA Import Mode"
2. [Paste your package]
3. Review conflicts, approve import
```

---

### Get AWS Knowledge from Colleague

**Colleague (Exporter):**
```
1. "Start SIMA Export Mode"
2. "Export platforms/aws"
3. Sends you package
```

**You (Importer):**
```
1. "Start SIMA Import Mode"
2. [Paste their package]
3. Handle any duplicates
4. AWS knowledge now in your SIMA!
```

---

### Share Specific Lessons

**You (Exporter):**
```
1. "Start SIMA Export Mode"
2. "Export LESS-01, LESS-03, LESS-05"
3. Share focused package
```

**Recipient:**
```
1. "Start SIMA Import Mode"
2. [Receives 3 lessons + dependencies]
3. Imports quickly, minimal conflicts
```

---

## 🎯 BEST PRACTICES

### Exporting

✅ **DO:**
- Update indexes before exporting
- Include related dependencies
- Review manifest before sharing
- Test import in clean instance (optional)

❌ **DON'T:**
- Export sensitive data
- Skip fileserver.php load
- Export outdated content

---

### Importing

✅ **DO:**
- Backup your knowledge first (export it)
- Read manifest before importing
- Review conflicts carefully
- Check import report after

❌ **DON'T:**
- Skip conflict resolution
- Import untrusted sources without review
- Ignore broken link warnings

---

## 📦 PACKAGE STRUCTURE

```
export-aws-lambda-2025-11-12/
├── manifest.yaml              # Metadata + checksums
├── import-instructions.md     # Usage guide
├── files/
│   ├── AWS-LESS-01.md
│   ├── AWS-LESS-02.md
│   └── ...
└── indexes/
    └── AWS-Lessons-Index.md
```

**All generated as Claude artifacts** - easy to copy/share

---

## ⚠️ CONFLICT TYPES

| Conflict | What It Means | Resolution |
|----------|---------------|------------|
| REF-ID Collision | Both have LESS-01 | Auto-renumber import |
| Content Duplicate | Similar content, different IDs | Choose best version |
| Missing Dependency | References non-existent file | Skip or import anyway |

**Claude handles automatically with your approval**

---

## 🔄 WORKFLOW COMPARISON

### Export Workflows

| Workflow | Use When | Command Example |
|----------|----------|-----------------|
| Domain | Share everything in domain | "Export generic domain" |
| Category | Share specific type | "Export all lessons" |
| REF-ID List | Share curated set | "Export LESS-01, DEC-05" |

### Import Workflows

| Workflow | Use When | Approach |
|----------|----------|----------|
| Full | No conflicts expected | Import everything |
| Selective | Want subset only | Choose categories |
| Merge | Many duplicates | Compare & combine |

---

## 🆘 TROUBLESHOOTING

### "Export fails or times out"
- Load fileserver.php first
- Try smaller scope
- New session

### "Too many conflicts on import"
- Use Merge workflow instead
- Review duplicates
- Consider selective import

### "Broken links after import"
- Check import report for skipped dependencies
- Import missing files
- Run Maintenance Mode

### "Don't know what's in package"
- Read `manifest.yaml` first
- Check `import-instructions.md`
- Review file list before importing

---

## 📖 MORE INFO

**Detailed guide:** SIMAv4.2.2-Import-Export-User-Guide.md

**Mode documentation:**
- `/sima/context/sima/context-SIMA-EXPORT-MODE-Context.md`
- `/sima/context/sima/context-SIMA-IMPORT-MODE-Context.md`

**Related modes:**
- Maintenance Mode - Update indexes
- Learning Mode - Create knowledge
- General Mode - Query knowledge

---

## ✅ CHECKLISTS

### Export Checklist
- [ ] fileserver.php loaded
- [ ] Scope decided
- [ ] "Start SIMA Export Mode"
- [ ] Specify what to export
- [ ] Review package
- [ ] Share artifacts

### Import Checklist
- [ ] Package received
- [ ] Backup created (optional but recommended)
- [ ] "Start SIMA Import Mode"
- [ ] Provide package
- [ ] Resolve conflicts
- [ ] Review report
- [ ] Verify cross-references

---

## 🎓 REMEMBER

**Export = Share Knowledge**
- Creates portable packages
- Includes dependencies automatically
- Safe to share (no modifications to your SIMA)

**Import = Receive Knowledge**
- Integrates external knowledge
- Handles conflicts automatically
- Updates indexes automatically
- Can undo with backup

**Both work together for team knowledge sharing!**

---

**END OF QUICK START GUIDE**

**Next steps:** Try exporting a small domain, then import it in a test to see how it works!
