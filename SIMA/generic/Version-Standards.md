# Version-Standards.md

**Version:** 1.0.0  
**Date:** 2025-12-07  
**Purpose:** Version format standards for code and documentation  
**Category:** Specifications

---

## PURPOSE

Define universal versioning standards for LEE and other projects using date-based versioning for clarity and maintainability.

---

## VERSION FORMAT

### Date-Based Format

**Pattern:** `YYYY-MM-DD_R`

**Components:**
- `YYYY` - Year (4 digits)
- `MM` - Month (2 digits, zero-padded)
- `DD` - Day (2 digits, zero-padded)
- `R` - Daily revision number (1, 2, 3, ...)

**Examples:**
```
2025-12-06_1    # First revision on Dec 6, 2025
2025-12-06_2    # Second revision same day
2025-12-07_1    # First revision next day
2025-12-15_3    # Third revision on Dec 15
```

---

## BENEFITS

### Over Semantic Versioning

**Advantages:**
- Chronological sorting automatic
- Clear deployment timeline
- Multiple revisions per day supported
- No arbitrary version numbers
- No semantic versioning confusion
- Deployment date visible at glance

**When to Use:**
- Application code (production deployments)
- Infrastructure code
- Configuration files
- Deployment manifests

---

## SEMANTIC VERSIONING

### When to Use

**Pattern:** `MAJOR.MINOR.PATCH`

**Use For:**
- Libraries and packages
- APIs with versioned contracts
- Documentation standards
- Specifications
- Reusable components

**Examples:**
```
1.0.0    # Initial release
1.0.1    # Patch/fix
1.1.0    # Minor addition
2.0.0    # Breaking change
```

---

## INCREMENT RULES

### Date-Based Versioning

**Daily Revision (R):**
1. Reset to `1` on new day
2. Increment for each deployment same day
3. No limit on daily revisions

**Example Timeline:**
```
2025-12-06_1 (09:00) - Initial deployment
2025-12-06_2 (14:30) - Bug fix
2025-12-06_3 (16:45) - Feature addition
2025-12-07_1 (10:00) - Next day (reset to 1)
```

### Semantic Versioning

**MAJOR (X.0.0):**
- Breaking changes
- API incompatibilities
- Major restructuring

**MINOR (x.X.0):**
- New features (backward compatible)
- Significant additions
- New capabilities

**PATCH (x.x.X):**
- Bug fixes
- Corrections
- Minor improvements

---

## FILE HEADERS

### Code Files (Date-Based)

**Python:**
```python
"""
filename.py
Version: 2025-12-06_3
Purpose: One-line description
License: Apache 2.0
"""
```

**JavaScript:**
```javascript
/**
 * filename.js
 * Version: 2025-12-06_3
 * Purpose: One-line description
 * License: MIT
 */
```

### Documentation (Semantic)

**Markdown:**
```markdown
# filename.md

**Version:** 1.2.0  
**Date:** 2025-12-06  
**Purpose:** Brief description  
**Category:** Category name
```

---

## CHANGELOG LOCATION

### Code Files

**Do NOT include in code:**
- ❌ Multi-line changelogs in headers
- ❌ Version history comments
- ❌ Change descriptions

**Include in companion .md:**
- ✅ Detailed changelog
- ✅ Version history table
- ✅ Migration notes

**Example:**
```
ha_alexa_core.py       (code only, minimal header)
ha_alexa_core.md       (includes full changelog)
```

### Documentation Files

**Include in file:**
- Small changes: Header comment
- Major changes: Version history section

**Separate CHANGELOG.md:**
- For directory-level changes
- For project-wide changes
- For breaking changes

---

## VERSION COMPARISON

### Date-Based Sorting

**Automatic chronological order:**
```
2025-11-30_1
2025-12-01_1
2025-12-01_2
2025-12-06_1
2025-12-06_2
2025-12-06_3
2025-12-07_1
```

**Benefits:**
- No manual sorting needed
- Clear timeline
- Easy to find recent versions

### Semantic Sorting

**Logical progression:**
```
1.0.0
1.0.1
1.1.0
1.1.1
2.0.0
```

**Benefits:**
- API compatibility clear
- Breaking changes obvious
- Feature additions visible

---

## MIGRATION GUIDE

### From Arbitrary Versions

**Old Format:**
```python
"""
Version: 4.3.0
Date: 2025-12-06
"""
```

**New Format:**
```python
"""
Version: 2025-12-06_1
Purpose: Brief description
License: Apache 2.0
"""
```

**Steps:**
1. Determine deployment date
2. Set R=1 for first conversion
3. Update header format
4. Move changelog to .md file
5. Remove verbose comments

### From Semantic to Date-Based

**When:**
- Deploying to production
- Code (not libraries)
- Application files

**How:**
1. Note last semantic version
2. Use current date
3. Set R=1
4. Document in changelog: "Migrated from v2.3.1 to date-based versioning"

---

## QUALITY STANDARDS

**Checklist:**
- [ ] Version format correct (YYYY-MM-DD_R or X.Y.Z)
- [ ] Date matches actual deployment/update
- [ ] R incremented correctly for same day
- [ ] R reset to 1 on new day
- [ ] Changelog in appropriate location
- [ ] Header minimal (code files)

---

## TOOLS

### Version Validator

**Python:**
```python
import re
from datetime import datetime

def validate_date_version(version_str):
    """Validate YYYY-MM-DD_R format."""
    pattern = r'^(\d{4})-(\d{2})-(\d{2})_(\d+)$'
    match = re.match(pattern, version_str)
    
    if not match:
        return False, "Invalid format"
    
    year, month, day, revision = match.groups()
    
    # Validate date
    try:
        datetime(int(year), int(month), int(day))
    except ValueError:
        return False, "Invalid date"
    
    # Validate revision
    if int(revision) < 1:
        return False, "Revision must be >= 1"
    
    return True, "Valid"
```

### Version Incrementer

**Python:**
```python
from datetime import datetime

def next_version(current_version=None):
    """Generate next version number."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    if not current_version:
        return f"{today}_1"
    
    # Parse current version
    date_part, rev = current_version.rsplit('_', 1)
    
    if date_part == today:
        # Same day, increment revision
        return f"{today}_{int(rev) + 1}"
    else:
        # New day, reset to 1
        return f"{today}_1"
```

---

## EXAMPLES

### Application Code

**Lambda Function:**
```python
"""
lambda_function.py
Version: 2025-12-06_2
Purpose: AWS Lambda entry point for LEE
License: Apache 2.0
"""
```

### Infrastructure

**Terraform:**
```hcl
# main.tf
# Version: 2025-12-06_1
# Purpose: LEE infrastructure definition
```

### Documentation

**Specification:**
```markdown
# Debug-System.md

**Version:** 1.0.0  
**Date:** 2025-12-06  
**Purpose:** Debug infrastructure specification  
**Category:** Specifications
```

---

## RELATED STANDARDS

- **File-Standards.md** - File organization and headers
- **Artifact-Standards.md** - Artifact creation rules
- **SPEC-HEADERS.md** - Header requirements
- **SPEC-FILE-STANDARDS.md** - Universal file standards

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-07 | Initial specification for date-based versioning |

---

**END OF FILE**
