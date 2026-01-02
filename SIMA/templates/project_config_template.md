# project_config_template.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Template for project knowledge configuration files  
**Category:** Template

---

## TEMPLATE

```yaml
project:
  name: "[project-name]"
  description: "[Brief project description]"
  version: "v2025.11.10.1"

knowledge:
  generic:
    enabled: true  # MUST be true
  
  platforms:
    [platform-name]:
      enabled: [true|false]
      services:
        [service-name]: [true|false]
        [service-name]: [true|false]
  
  languages:
    [language-name]:
      enabled: [true|false]
      architectures:
        [architecture-name]: [true|false]
        [architecture-name]: [true|false]
  
  features:
    [feature-name]:
      enabled: [true|false]
      note: "[Optional explanation]"

context:
  constraints:
    - "[Constraint 1]"
    - "[Constraint 2]"
    - "[Constraint 3]"
  
  capabilities:
    - "[Capability 1]"
    - "[Capability 2]"
    - "[Capability 3]"

file_access:
  include_paths:
    - "/sima/generic/**"
    - "/sima/platforms/[platform]/**"
    - "/sima/languages/[language]/**"
    - "/sima/projects/[project]/**"
  
  exclude_paths:
    - "/sima/platforms/[other-platform]/**"
  
  exclude_ref_ids:
    - "[REF-ID]"  # Not applicable
```

---

## INSTRUCTIONS

### Step 1: Copy Template
Save as `knowledge-config.yaml` in `/sima/projects/[project]/config/`

### Step 2: Fill Project Info
- name: Project identifier (lowercase, hyphens)
- description: One sentence (max 100 chars)
- version: vYYYY.MM.DD.R format

### Step 3: Configure Knowledge
- Generic: MUST be true
- Platforms: Enable only those used
- Languages: Enable only those used
- Architectures: Enable patterns applied

### Step 4: Document Context
- Constraints: List limitations
- Capabilities: List strengths

### Step 5: Set File Access
- Include: Paths to load
- Exclude: Paths to skip
- Exclude REF-IDs: Specific entries to ignore

---

## RELATED

- SPEC-KNOWLEDGE-CONFIG.md

---

**END OF TEMPLATE**