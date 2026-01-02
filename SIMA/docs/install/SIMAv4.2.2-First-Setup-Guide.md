# SIMAv4.2.2-First-Setup-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** First-time SIMA setup  
**Type:** Setup Documentation

---

## FIRST-TIME SETUP

### Step 1: Verify Installation
```bash
cd sima/
ls -R | head -20
# Should see context/, docs/, generic/, etc.
```

### Step 2: Configure File Server URLs
```bash
# Edit File-Server-URLs.md
nano File-Server-URLs.md

# Update with your domain:
https://your-domain.com/fileserver.php?v=0070
```

### Step 3: Test File Server
```bash
curl https://your-domain.com/fileserver.php?v=test
# Should return list of URLs
```

### Step 4: First Session with AI
```
1. Upload File-Server-URLs.md to Claude
2. Say: "Please load context"
3. Wait ~20-30s for context load
4. Ask: "What is SIMA?"
5. Verify response with REF-IDs
```

### Step 5: Test Each Mode
```
"Please load context" - General Mode
"Start SIMA Learning Mode" - Learning Mode
"Start SIMA Maintenance Mode" - Maintenance Mode
```

---

## INITIAL CONFIGURATION

### Create Your First Project
```
Say: "Start New Project Mode: MyProject"

AI will create:
- Directory structure
- Config files
- Mode extensions
- Indexes
```

### Add Your First Knowledge
```
Say: "Start SIMA Learning Mode"

Provide: Some experience or pattern

AI will:
- Extract knowledge
- Create entries
- Update indexes
```

---

## VALIDATION

**Check installation:**
```bash
# File counts
find . -type f -name "*.md" | wc -l
# ~150 files

# File sizes
find . -name "*.md" -exec wc -l {} \; | awk '$1 > 400'
# Should be empty

# Encoding
file -b --mime-encoding */**.md | grep -v utf-8
# Should be empty
```

---

## NEXT STEPS

1. Read User Guide
2. Explore directory structure
3. Test all modes
4. Create first project
5. Add knowledge entries

---

**END OF FIRST SETUP**

**Version:** 1.0.0  
**Lines:** 80 (within 400 limit)