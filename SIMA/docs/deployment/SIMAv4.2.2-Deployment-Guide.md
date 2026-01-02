# SIMAv4.2.2-Deployment-Guide.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Guide for deploying blank SIMAv4 system  
**Audience:** System administrators and project leads

---

## OVERVIEW

This guide covers deploying a blank SIMAv4 installation for your team or organization.

**What you'll deploy:**
- Complete SIMA directory structure
- All mode contexts (General, Learning, Maintenance, Project, Debug, New)
- Empty generic knowledge structure ready for content
- All templates and tools
- Documentation system

**What's NOT included:**
- Language-specific knowledge (add via imports)
- Platform-specific knowledge (add via imports)
- Project implementations (create via New Project Mode)
- Existing knowledge entries (blank slate)

---

## PREREQUISITES

**Server Requirements:**
- Web server (nginx, Apache, or similar)
- PHP 7.4+ (for fileserver.php)
- File system access
- HTTPS recommended

**Client Requirements:**
- Claude.ai account (Sonnet 4 recommended)
- Modern web browser
- Text editor (for File Server URLs)

---

## DEPLOYMENT STEPS

### Step 1: Extract Archive

```bash
# If using tar.gz
tar -xzf blank-sima-v4.2.2.tar.gz -C /var/www/

# If using zip
unzip blank-sima-v4.2.2.zip -d /var/www/
```

### Step 2: Set Permissions

```bash
cd /var/www/sima
chmod -R 755 .
```

### Step 3: Configure Web Server

**nginx example:**
```nginx
server {
    listen 80;
    server_name sima.yourdomain.com;
    root /var/www/sima;
    
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
    }
}
```

**Apache example:**
```apache
<VirtualHost *:80>
    ServerName sima.yourdomain.com
    DocumentRoot /var/www/sima
    
    <Directory /var/www/sima>
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

### Step 4: Test fileserver.php

```bash
curl https://sima.yourdomain.com/fileserver.php
```

Should return JSON list of ~130 files with cache-busting parameters.

### Step 5: Create File Server URLs.md

```markdown
# File Server URLs.md

https://sima.yourdomain.com/fileserver.php?v=0001
```

### Step 6: Test with Claude

1. Upload File Server URLs.md to Claude
2. Say: "Please load context"
3. Verify General Mode loads
4. Ask: "What SIMA modes are available?"

### Step 7: Verify Structure

```bash
# Check all critical directories exist
find /var/www/sima -type d | wc -l  # Should be ~40
find /var/www/sima -name "*.md" | wc -l  # Should be ~147
```

---

## POST-DEPLOYMENT

### Enable Team Access

**Option 1: Single Team Instance**
- Share File Server URLs.md with team
- Everyone uses same SIMA installation
- Shared knowledge grows together

**Option 2: Per-User Instances**
- Each user gets own SIMA copy
- Independent knowledge bases
- Can share exports between instances

### First Knowledge Entry

```
1. Say: "Start SIMA Learning Mode"
2. Provide experience to document
3. Claude extracts and creates generic entries
4. Knowledge base begins to grow
```

### Add Language/Platform Knowledge

```
1. Export from existing SIMA (if available)
2. Say: "Start SIMA Import Mode"
3. Provide export file
4. Claude integrates into blank SIMA
```

---

## MAINTENANCE

### Weekly
- Verify fileserver.php responding
- Check File Server URLs.md current
- Update cache-bust parameter if needed

### Monthly
- Review generic indexes for growth
- Check disk space usage
- Update documentation if needed

### Quarterly
- Full backup of /sima directory
- Review and archive old knowledge
- Update to new SIMA versions

---

## TROUBLESHOOTING

**Problem: fileserver.php returns 500 error**
- Check PHP version (7.4+ required)
- Check file permissions (755)
- Check PHP error logs

**Problem: Claude can't fetch files**
- Verify File Server URLs.md uploaded
- Check HTTPS certificate valid
- Test fileserver.php manually

**Problem: Cache-busting not working**
- Increment ?v= parameter manually
- Clear Claude session and restart
- Check fileserver.php generating random values

**Problem: Missing directories**
- Re-extract archive
- Verify all 40 directories present
- Check file permissions

---

## SECURITY CONSIDERATIONS

### File Access

**Restrict fileserver.php (optional):**
```nginx
location /fileserver.php {
    allow 10.0.0.0/8;
    deny all;
}
```

### HTTPS

**Enable SSL:**
```bash
certbot --nginx -d sima.yourdomain.com
```

### Backups

**Automated backup:**
```bash
#!/bin/bash
# /usr/local/bin/backup-sima.sh
tar -czf /backups/sima-$(date +%Y%m%d).tar.gz /var/www/sima
find /backups -name "sima-*.tar.gz" -mtime +30 -delete
```

**Cron:**
```
0 2 * * * /usr/local/bin/backup-sima.sh
```

---

## MONITORING

### Health Checks

**Monitor fileserver.php:**
```bash
# /usr/local/bin/check-sima-health.sh
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" https://sima.yourdomain.com/fileserver.php)
if [ $response -ne 200 ]; then
    echo "SIMA fileserver.php down: HTTP $response" | mail -s "SIMA Alert" admin@yourdomain.com
fi
```

### Performance

**Monitor response times:**
```bash
curl -w "@curl-format.txt" -o /dev/null -s https://sima.yourdomain.com/fileserver.php
```

**curl-format.txt:**
```
time_total: %{time_total}s
```

---

## SCALING

### Multiple Teams

**Separate instances:**
```
/var/www/sima-team-a/
/var/www/sima-team-b/
```

**Shared knowledge:**
```
/var/www/sima-shared/generic/
/var/www/sima-team-a/projects/
/var/www/sima-team-b/projects/
```

### Load Balancing

**nginx upstream:**
```nginx
upstream sima_backend {
    server sima1.yourdomain.com;
    server sima2.yourdomain.com;
}
```

---

## SUPPORT

**Documentation:**
- User Guide: `/sima/docs/user/SIMAv4.2.2-User-Guide.md`
- Developer Guide: `/sima/docs/developer/SIMAv4.2.2-Developer-Guide.md`
- Quick Start: `/sima/docs/user/SIMAv4.2.2-Quick-Start-Guide.md`

**Related Guides:**
- Installation: `/sima/docs/install/SIMAv4.2.2-Installation-Guide.md`
- First Setup: `/sima/docs/install/SIMAv4.2.2-First-Setup-Guide.md`

---

## APPENDIX: FILE COUNTS

**Expected file counts by directory:**

| Directory | Files | Purpose |
|-----------|-------|---------|
| /context | 48 | Mode contexts |
| /docs | 19 | User documentation |
| /generic | 19 | Generic knowledge structure |
| /languages | 2 | Language routers (empty) |
| /platforms | 2 | Platform routers (empty) |
| /projects | 2 | Project routers (empty) |
| /support | 25 | Tools and workflows |
| /templates | 12 | Entry templates |
| Root | 10 | Navigation and info |
| **Total** | **~147** | **Core system** |

---

**END OF DEPLOYMENT GUIDE**

**Version:** 1.0.0  
**Lines:** 340 (within 400 limit)  
**Purpose:** Production deployment procedures  
**Audience:** System administrators