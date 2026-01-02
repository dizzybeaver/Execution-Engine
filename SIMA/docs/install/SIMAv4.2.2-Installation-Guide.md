# SIMAv4.2.2-Installation-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** SIMA installation procedures  
**Type:** Installation Documentation

---

## INSTALLATION OVERVIEW

SIMA is a documentation-based system that requires no traditional installation. Setup involves organizing files and configuring access.

---

## PREREQUISITES

### System Requirements
- Git (for version control)
- Text editor (VS Code, Sublime, etc.)
- Web server (for fileserver.php)
- Claude.ai account

### File Server Requirements
- PHP 7.4+ 
- Web server (nginx/Apache)
- Directory read permissions
- Public HTTPS access

---

## INSTALLATION METHODS

### Method 1: Extract Archive

**Steps:**
```bash
# 1. Extract archive
tar -xzf blank-sima-v4.2.2.tar.gz

# 2. Navigate to directory
cd sima/

# 3. Verify structure
ls -R

# 4. Check file count
find . -name "*.md" | wc -l
# Should be ~150
```

### Method 2: Clone Repository

**Steps:**
```bash
# 1. Clone
git clone [repository-url] sima

# 2. Navigate
cd sima/

# 3. Checkout version
git checkout v4.2.2-blank

# 4. Verify
./tools/verify-structure.sh
```

---

## FILE SERVER SETUP

### PHP Script Installation

**1. Copy fileserver.php to web root:**
```bash
cp support/fileserver.php /var/www/html/
```

**2. Set permissions:**
```bash
chmod 644 /var/www/html/fileserver.php
```

**3. Test access:**
```bash
curl https://your-domain.com/fileserver.php?v=0001
```

**4. Verify output:**
Should return ~150+ URLs with cache-busting parameters.

### Web Server Configuration

**nginx:**
```nginx
location ~ \.php$ {
    fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
    fastcgi_index fileserver.php;
    include fastcgi_params;
}
```

**Apache:**
```apache
<FilesMatch "\.php$">
    SetHandler application/x-httpd-php
</FilesMatch>
```

### Security

**Restrict access (optional):**
```nginx
location /fileserver.php {
    allow [your-ip];
    deny all;
}
```

---

## FILE-SERVER-URLS.MD CONFIGURATION

**Edit File-Server-URLs.md:**
```markdown
# File Server URLs.md

**Version:** 2.0.0

## FILE SERVER ENDPOINT

https://your-domain.com/fileserver.php?v=0070
```

**Save and test:**
1. Upload to Claude.ai
2. Verify AI can fetch fileserver.php
3. Check returns URLs

---

## DIRECTORY STRUCTURE VERIFICATION

**Run validation:**
```bash
# Check all expected directories exist
./tools/verify-structure.sh

# Check file standards
./tools/verify-standards.sh

# Check encoding
./tools/verify-encoding.sh
```

**Expected output:**
```
✓ All directories present
✓ All indexes exist
✓ All files ≤400 lines
✓ All files UTF-8
✓ All files LF endings
```

---

## FIRST RUN

### Test General Mode

**Steps:**
```
1. Upload File-Server-URLs.md to Claude
2. Say: "Please load context"
3. AI should load general context (~20-30s)
4. Ask: "What is SIMA?"
5. Should receive explanation with REF-IDs
```

### Test Other Modes

**Project Mode:**
```
"Start Project Mode for SIMA"
```

**Learning Mode:**
```
"Start SIMA Learning Mode"
```

**Maintenance Mode:**
```
"Start SIMA Maintenance Mode"
```

---

## POST-INSTALLATION

### Optional: Git Repository

**Initialize:**
```bash
cd sima/
git init
git add .
git commit -m "Initial blank SIMA v4.2.2"
git tag v4.2.2-blank
```

### Optional: Backup

**Create backup:**
```bash
tar -czf sima-backup-$(date +%Y%m%d).tar.gz sima/
```

### Optional: Custom Domain

**Update File-Server-URLs.md with your domain**

---

## TROUBLESHOOTING

### Issue: fileserver.php Not Found

**Check:**
- File copied to web root
- Permissions correct (644)
- PHP enabled
- Web server configuration

**Test:**
```bash
php /var/www/html/fileserver.php
```

### Issue: No URLs Returned

**Check:**
- PHP has read permissions
- /src and /sima directories exist
- Paths correct in fileserver.php

### Issue: Mode Won't Activate

**Check:**
- File-Server-URLs.md uploaded
- Exact activation phrase used
- Context files exist

### Issue: Files Truncated

**Check:**
- All files ≤400 lines
- Run: `find . -name "*.md" -exec wc -l {} \; | awk '$1 > 400'`
- Split oversized files

---

## NEXT STEPS

**After installation:**
1. Read Quick Start Guide
2. Test each mode
3. Review directory structure
4. Create first project
5. Add knowledge entries

**Guides:**
- [First Setup Guide](SIMAv4.2.2-First-Setup-Guide.md)
- [Quick Start](../user/SIMAv4.2.2-Quick-Start-Guide.md)
- [User Guide](../user/SIMAv4.2.2-User-Guide.md)

---

**END OF INSTALLATION GUIDE**

**Version:** 1.0.0  
**Lines:** 250 (within 400 limit)  
**Purpose:** Installation procedures  
**Audience:** System administrators