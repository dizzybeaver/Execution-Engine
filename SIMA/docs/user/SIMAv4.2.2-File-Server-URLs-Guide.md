# SIMAv4.2.2-File-Server-URLs-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** File server system explanation  
**Type:** User Documentation

---

## PROBLEM

Anthropic's platform caches files for weeks, ignoring all server cache-control headers. This causes AI to work with stale code and outdated knowledge, leading to:

- Wrong fixes (code changed since cache)
- False duplicates (new entries not seen)
- Outdated references (moved files not found)
- Wasted tokens (rework on stale state)

**Impact:** Breaks development workflows requiring fresh content.

---

## SOLUTION

**fileserver.php** generates unique cache-busting URLs dynamically:

```
Original: https://example.com/file.md
Cached: Yes (weeks)

Generated: https://example.com/file.md?v=7382915046
Cached: No (random parameter bypasses cache)
```

**How It Works:**
1. User uploads File-Server-URLs.md containing fileserver.php URL
2. AI fetches fileserver.php at session start
3. Receives ~412 URLs with random ?v= parameters
4. Each URL points to fresh file content
5. Random values change every session

**Performance:** 69ms generation, 412 files, fresh content guaranteed.

---

## USAGE

### Every Session

**Step 1: Upload File-Server-URLs.md**
```markdown
Contains: https://fileserver.example.com/fileserver.php?v=0070
```

**Step 2: AI Auto-Fetches**
AI automatically fetches fileserver.php and receives all cache-busted URLs.

**Step 3: Work Normally**
All file fetches use fresh content automatically.

---

## FILE-SERVER-URLS.MD

### Contents

```markdown
# File Server URLs.md

**Version:** 2.0.0  
**Purpose:** Dynamic URL inventory via fileserver.php

## FILE SERVER ENDPOINT

https://fileserver.example.com/fileserver.php?v=0070

## CRITICAL: USE EXACT URL
Always include the ?v= parameter!
```

### Why Upload This File?

**Permission:** Explicit URL in uploaded file grants permission to fetch  
**Automatic:** AI recognizes and fetches automatically  
**Fresh:** Ensures latest URLs every session  
**Simple:** One file upload, automatic handling

### Where To Get It

**Location:** `/sima/File-Server-URLs.md`  
**Update:** Maintained automatically by system  
**Version:** Check file header for current version

---

## FILESERVER.PHP DETAILS

### What It Does

1. Scans `/src` and `/sima` directories
2. Generates list of all .md, .py, .yaml, .html files
3. Adds random 10-digit ?v= parameter to each URL
4. Returns complete list in ~69ms
5. Randomizes on each fetch

### Output Format

```
https://fileserver.example.com/sima/context/MODE-SELECTOR.md?v=6408252197
https://fileserver.example.com/sima/generic/generic-Router.md?v=6268948902
...
```

**Count:** ~412 files  
**Domains:** /src (source code) + /sima (documentation)  
**Time:** ~69ms execution  
**Cache:** Fresh each session

### Technical Details

**Server:** Ignores ?v= parameter (transparent)  
**Platform:** Sees different URL (bypasses cache)  
**Random:** crypto_random_bytes(10 digits)  
**Scope:** All .md, .py, .yaml, .html files  
**Exclusions:** .git/, node_modules/, vendor/

---

## WHY THIS APPROACH

### Previous Attempts

**Server Headers:** ❌ Platform ignores  
**Manual Parameters:** ❌ Permission errors  
**File Listing:** ❌ Gets cached too  

**Dynamic Generation:** ✅ Works!

### Benefits

**No Setup:** Upload one file, done  
**Automatic:** AI handles fetching  
**Fresh:** Never stale content  
**Fast:** 69ms generation  
**Complete:** All files covered  
**Transparent:** Works seamlessly

---

## COMMON SCENARIOS

### Scenario 1: Development Session

```
1. Upload File-Server-URLs.md
2. Say: "Start Project Mode for SIMA"
3. AI fetches fileserver.php automatically
4. Receives 412 fresh URLs
5. Fetches current code files
6. Generates accurate fixes
```

**Result:** Working with latest code

### Scenario 2: Learning Session

```
1. Upload File-Server-URLs.md
2. Say: "Start SIMA Learning Mode"
3. AI fetches fileserver.php automatically
4. Checks existing entries via fresh URLs
5. Detects actual duplicates
6. Creates only unique entries
```

**Result:** Accurate duplicate detection

### Scenario 3: Debug Session

```
1. Upload File-Server-URLs.md
2. Say: "Start Debug Mode for PROJECT"
3. AI fetches fileserver.php automatically
4. Gets current file state
5. Analyzes actual code
6. Provides relevant fix
```

**Result:** Fix addresses real issue

---

## TROUBLESHOOTING

### Issue: AI Working with Old Code

**Symptom:** Suggested fixes don't match current code  
**Cause:** File-Server-URLs.md not uploaded  
**Fix:** Upload file at session start  
**Prevention:** Make it first action every session

### Issue: Duplicate Entries Created

**Symptom:** Knowledge entry exists but new one created  
**Cause:** Cached entry list (File-Server-URLs.md not uploaded)  
**Fix:** Upload file before Learning Mode  
**Prevention:** Always upload first

### Issue: Broken References

**Symptom:** AI can't find recently moved file  
**Cause:** Cached directory structure  
**Fix:** Upload File-Server-URLs.md  
**Prevention:** Upload at session start

### Issue: fileserver.php Timeout

**Symptom:** Fetch takes >1 second or fails  
**Cause:** Server under load  
**Fix:** Wait moment, try again  
**Prevention:** Usually resolves immediately

---

## TECHNICAL NOTES

### Cache-Busting Format

```
URL: https://example.com/file.md
Parameter: ?v=7382915046
Full: https://example.com/file.md?v=7382915046
```

**Random:** 10 digits from crypto_random_bytes  
**Unique:** Different every session  
**Transparent:** Server ignores parameter  
**Effective:** Platform sees unique URL

### Why Random?

**Sequential:** `?v=1`, `?v=2` → Could be cached across sessions  
**Timestamp:** `?v=1699999999` → Predictable  
**Random:** `?v=7382915046` → Unpredictable, always unique

### Server Configuration

**Script:** fileserver.php  
**Language:** PHP  
**Permissions:** Read-only directory scanning  
**Security:** Only lists known directories  
**Performance:** Fast (69ms for 412 files)

---

## RELATED DOCUMENTATION

**Problem:** WISD-06 (Cache-Busting Platform Limitation)  
**Decision:** DEC-24 (Dynamic URL Generation)  
**Implementation:** fileserver.php  
**User Impact:** Seamless, automatic, effective

---

## BEST PRACTICES

### Session Start
1. Upload File-Server-URLs.md (FIRST)
2. Activate mode (SECOND)
3. Begin work (THIRD)

### Development
- Always upload before code generation
- Always upload before debugging
- Always upload before learning

### Maintenance
- Keep File-Server-URLs.md current
- Check version periodically
- Update if system changes

---

**END OF FILE SERVER GUIDE**

**Version:** 1.0.0  
**Lines:** 320 (within 400 limit)  
**Purpose:** Explain cache-busting system  
**Audience:** Users troubleshooting or understanding system