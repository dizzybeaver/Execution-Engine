# File-Server-URLs.md

**Version:** 2.0.0  
**Date:** 2025-11-10  
**Purpose:** Dynamic URL inventory via fileserver.php  
**System:** fileserver.php cache-busting  
**Installation:** Blank SIMA 4.2.2

---

## 📄 DYNAMIC FILE RETRIEVAL

**Upload this file to Claude at session start.**

Claude will automatically fetch fileserver.php which returns all file URLs with unique cache-busting parameters, ensuring fresh content every session.

---

## ⚠️ CRITICAL: USE EXACT URL

**MANDATORY:** When fetching fileserver.php, use the COMPLETE URL below INCLUDING the ?v= parameter.

❌ WRONG: https://fileserver.example.com/fileserver.php  
✅ CORRECT: https://fileserver.example.com/fileserver.php?v=XXXX

Dropping the parameter defeats the entire cache-busting system!

---

## 🔗 FILE SERVER ENDPOINT

# Set your fileserver endpoint here
```
https://fileserver.example.com/fileserver.php?v=0063
```

*Note: Update the ?v= parameter value periodically if needed*

---

## ⚙️ HOW IT WORKS

**When you upload this file:**
1. Claude sees the fileserver.php URL
2. Claude fetches it automatically at session start
3. fileserver.php returns ~150+ URLs with unique ?v=XXXXXXXXXX parameters
4. Claude can access any file with fresh content (no cached versions)

**Performance:**
- Generation time: ~50-100ms
- Total files: ~150 (core system only)
- Cache-busting: Random 10-digit per file, per session

**Why this approach:**
Anthropic's platform caches files for weeks, ignoring server headers. Query parameters on explicit URLs cause permission errors. Solution: Dynamic generation via fetchable endpoint that returns cache-busted URLs.

---

## 📦 WHAT YOU GET

**Core System:** /sima directory (150+ files)
- Context files (mode activation)
- Documentation (guides)
- Support tools and workflows
- Templates (all entry types)
- Specifications (system specs)
- Empty knowledge domains (ready for import)

**NOT Included in Blank Installation:**
- ❌ Knowledge entries (LESS, DEC, AP, BUG, WISD)
- ❌ Language-specific patterns
- ❌ Platform-specific knowledge
- ❌ Project implementations

---

## 🚀 FIRST TIME SETUP

1. **Upload this file**
   ```
   At start of every Claude session
   ```

2. **Wait for fetch**
   ```
   Claude automatically fetches fileserver.php
   Confirms URL inventory received
   ```

3. **Activate mode**
   ```
   "Please load context"
   or
   "Start SIMA Learning Mode"
   etc.
   ```

4. **Begin work**
   ```
   All files accessible with fresh content
   ```

---

## 🔧 TROUBLESHOOTING

### If fileserver.php times out:
- Server may be under load
- Try again in a moment
- Usually resolves within seconds

### If file fetch fails:
- Verify file exists in repository
- Check file path matches fileserver.php output
- Ensure fileserver.php was fetched first

### If content seems stale:
- Verify using complete URL with ?v= parameter
- Check fileserver.php returned unique values
- Confirm not using cached fileserver.php response

---

## 📊 TECHNICAL NOTES

**Cache-Busting Format:**
```
https://fileserver.example.com/sima/path/to/file.md?v=7382915046
```
- Random 10-digit number per file
- Unique each session
- Bypasses Anthropic's cache
- Server ignores parameter

**File Organization:**
```
/sima/
├── context/         # Mode files
├── docs/            # Documentation  
├── generic/         # Universal knowledge (empty)
├── languages/       # Language patterns (empty)
├── platforms/       # Platform knowledge (empty)
├── projects/        # Implementations (empty)
├── support/         # Tools & utilities
└── templates/       # Entry templates
```

---

## 📚 RELATED DOCUMENTATION

**Cache-Busting System:**
- Specification: /generic/specifications/SPEC-ENCODING.md
- Wisdom: WISD-06 (when imported)
- Implementation: fileserver.php on server

**File Access:**
- All modes automatically use fresh URLs
- No manual cache management needed
- Transparent to user workflow

---

## ✅ QUALITY ASSURANCE

**Verify After Upload:**
- ✅ fileserver.php fetched successfully
- ✅ URL list received (~150 files)
- ✅ Cache-busting parameters present
- ✅ All paths begin with /sima/

**Per-Session Check:**
- ✅ Upload at start of EVERY session
- ✅ Wait for fetch confirmation
- ✅ Verify no error messages

---

## 🎯 QUICK REFERENCE

**Purpose:** Ensure fresh file access  
**Frequency:** Every session start  
**Automatic:** Yes (Claude fetches)  
**Manual Setup:** None required  

**Key Benefit:** No stale content, no manual cache management

---

**END OF FILE**

**Action Required:** Upload this file when starting any Claude session  
**Result:** Fresh files guaranteed via dynamic cache-busting  
**Maintenance:** None (automatic generation)  
**Installation Type:** Blank SIMA 4.2.2 (core system only)