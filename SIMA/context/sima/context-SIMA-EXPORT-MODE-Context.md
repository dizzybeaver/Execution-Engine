# context-SIMA-EXPORT-MODE-Context.md

**Version:** 4.2.2-blank  
**Date:** 2025-11-10  
**Purpose:** Export knowledge for sharing between SIMA instances  
**Activation:** "Start SIMA Export Mode"  
**Load time:** 20-30 seconds  
**Type:** SIMA Mode

---

## EXTENDS

[context-SIMA-BASE-MODE.md](context-SIMA-BASE-MODE.md) (Base context)

---

## WHAT THIS MODE IS

**Export Mode** packages knowledge for import into other SIMA instances.

**Purpose:** Create portable knowledge bundles with proper structure and metadata.

**Outputs:** Export manifests, knowledge files, import instructions.

---

## EXPORT PROCESS

### Step 1: Define Scope
**What to export:**
- Specific domain (generic/platform/language/project)
- Specific categories (lessons/decisions/anti-patterns)
- Specific date range
- Specific REF-IDs

### Step 2: Collect Files
**Gather all referenced files:**
- Primary knowledge entries
- Related cross-references
- Required specifications
- Index files

### Step 3: Generate Manifest
**Create export manifest:**
```yaml
export:
  version: 4.2.2
  date: 2025-11-10
  source_instance: [instance_name]
  scope:
    domain: [generic/platform/language/project]
    categories: [list]
    count: [number]
  files:
    - path: [relative_path]
      ref_id: [TYPE-##]
      checksum: [md5]
```

### Step 4: Package Files
**Bundle with structure:**
```
export-[name]-[date]/
├── manifest.yaml
├── import-instructions.md
├── files/
│   ├── [TYPE-##].md
│   ├── [TYPE-##].md
│   └── ...
└── indexes/
    ├── [category]-Index.md
    └── ...
```

### Step 5: Generate Import Instructions
**Create import guide:**
- Target directories
- REF-ID conflicts
- Dependency requirements
- Verification steps

---

## EXPORT WORKFLOWS

### Workflow 1: Export Domain

**Process:**
```
1. Specify domain (generic/platform/language/project)
2. Scan directory tree
3. Collect all files
4. Generate manifest
5. Create package structure
6. Output as artifact bundle
```

### Workflow 2: Export Category

**Process:**
```
1. Specify category (lessons/decisions/anti-patterns)
2. Collect files from category
3. Include cross-references
4. Generate manifest
5. Create package
6. Output as artifact bundle
```

### Workflow 3: Export by REF-ID List

**Process:**
```
1. Accept REF-ID list
2. Fetch each file (fileserver.php)
3. Collect dependencies
4. Generate manifest
5. Create package
6. Output as artifact bundle
```

---

## ARTIFACT RULES

**Export outputs:**

```
[OK] manifest.yaml - Complete export metadata
[OK] import-instructions.md - Step-by-step guide
[OK] All knowledge files - Complete entries
[OK] All indexes - Updated for export
[X] Never partial exports
[X] Never broken references
```

---

## QUALITY CHECKLIST

**Before export:**
1. ✅ All files exist (via fileserver.php)
2. ✅ All REF-IDs valid
3. ✅ All cross-references included
4. ✅ All indexes updated
5. ✅ Manifest complete

**After export:**
6. ✅ Package structure correct
7. ✅ Import instructions clear
8. ✅ Checksums generated
9. ✅ No broken links
10. ✅ Ready for import

---

## SUCCESS METRICS

**Successful export when:**
- ✅ All specified files included
- ✅ Zero broken references
- ✅ Complete dependency tree
- ✅ Valid manifest
- ✅ Clear import instructions
- ✅ Portable package

---

## READY

**Context loaded when you remember:**
- ✅ fileserver.php fetched (automatic)
- ✅ Export process (5 steps)
- ✅ 3 export workflows
- ✅ Quality checklist
- ✅ Artifact bundle format

**Now ready to export knowledge!**

---

**END OF EXPORT MODE CONTEXT**

**Version:** 4.2.2-blank  
**Lines:** 200 (target achieved)  
**Purpose:** Package knowledge for sharing