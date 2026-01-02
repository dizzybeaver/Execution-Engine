# templates-Master-Index.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Complete index of all SIMA templates  
**Category:** Index

---

## OVERVIEW

This index catalogs all template files for creating SIMA documentation entries.

**Total Templates:** 11

---

## NEURAL MAP ENTRY TEMPLATES

### lesson_learned_template.md
**Purpose:** Template for LESS-## lesson entries  
**Location:** `/sima/templates/`  
**Usage:** Documenting lessons from experience  
**Sections:** Context, Problem, Discovery, Insight, Application, Example

### decision_log_template.md
**Purpose:** Template for DEC-## decision entries  
**Location:** `/sima/templates/`  
**Usage:** Documenting technical and architectural decisions  
**Sections:** Context, Decision, Alternatives, Rationale, Consequences, Outcome

### anti_pattern_template.md
**Purpose:** Template for AP-## anti-pattern entries  
**Location:** `/sima/templates/`  
**Usage:** Documenting patterns to avoid  
**Sections:** Pattern, Why Wrong, Example, Right Way, Detection, Prevention

### bug_report_template.md
**Purpose:** Template for BUG-## bug entries  
**Location:** `/sima/templates/`  
**Usage:** Documenting bugs and fixes  
**Sections:** Symptom, Reproduction, Root Cause, Fix, Prevention

### wisdom_template.md
**Purpose:** Template for WISD-## wisdom entries  
**Location:** `/sima/templates/`  
**Usage:** Documenting profound insights  
**Sections:** Insight, Origin, Significance, Applications

---

## ARCHITECTURE TEMPLATES

### architecture_doc_template.md
**Purpose:** Template for ARCH-## architecture docs  
**Location:** `/sima/templates/`  
**Usage:** Documenting architectural patterns  
**Sections:** Concept, Structure, Principles, Benefits, Implementation

### gateway_pattern_template.md
**Purpose:** Template for GATE-## gateway patterns  
**Location:** `/sima/templates/`  
**Usage:** Documenting gateway patterns  
**Sections:** Purpose, Pattern, Implementation, Usage, Benefits

### interface_catalog_template.md
**Purpose:** Template for INT-## interface docs  
**Location:** `/sima/templates/`  
**Usage:** Documenting interfaces and their functions  
**Sections:** Purpose, Functions, Usage Patterns, Implementation

---

## PROJECT TEMPLATES

### project_config_template.md
**Purpose:** Template for knowledge-config.yaml  
**Location:** `/sima/templates/`  
**Usage:** Project knowledge configuration  
**Format:** YAML configuration file

### project_readme_template.md
**Purpose:** Template for project README files  
**Location:** `/sima/templates/`  
**Usage:** Project overview and documentation  
**Sections:** Overview, Architecture, Features, Setup, Usage

---

## GENERIC TEMPLATE

### nmp_entry-template.md
**Purpose:** Generic neural map entry template  
**Location:** `/sima/templates/`  
**Usage:** Creating any type of neural map entry  
**Sections:** Flexible structure for any entry type

---

## USAGE GUIDE

### Choosing the Right Template

**For lessons learned:**
→ lesson_learned_template.md

**For decisions:**
→ decision_log_template.md

**For anti-patterns:**
→ anti_pattern_template.md

**For bugs:**
→ bug_report_template.md

**For wisdom:**
→ wisdom_template.md

**For architectures:**
→ architecture_doc_template.md

**For gateway patterns:**
→ gateway_pattern_template.md

**For interfaces:**
→ interface_catalog_template.md

**For project config:**
→ project_config_template.md

**For project README:**
→ project_readme_template.md

**For generic entries:**
→ nmp_entry-template.md

---

## TEMPLATE USAGE WORKFLOW

### Step 1: Select Template
Choose appropriate template for entry type

### Step 2: Copy Template
Copy the markdown template section

### Step 3: Fill Placeholders
Replace all `[PLACEHOLDER]` text with actual content

### Step 4: Verify Standards
Check compliance:
- [ ] Header complete
- [ ] All sections filled
- [ ] File ≤400 lines
- [ ] UTF-8 encoding, LF endings
- [ ] Keywords present
- [ ] Cross-references added

### Step 5: Save File
Save with proper naming:
- LESS-##.md
- DEC-##.md
- AP-##.md
- BUG-##.md
- WISD-##.md
- ARCH-##.md
- GATE-##.md
- INT-##.md

---

## TEMPLATE STRUCTURE

### Standard Sections

**All templates include:**
1. Header (filename, version, date, purpose, category)
2. Template usage instructions
3. Template markdown (copy-paste ready)
4. Instructions for filling
5. Guidelines for quality
6. Related specifications

**Template benefits:**
- Consistency across entries
- Complete structure provided
- Reduces creation time
- Ensures standards compliance
- Built-in best practices

---

## CUSTOMIZATION

### When to Customize
- Project-specific needs
- Domain-specific requirements
- Special entry types

### How to Customize
1. Copy base template
2. Add/modify sections
3. Keep core structure
4. Maintain standards compliance
5. Document changes

---

## MAINTENANCE

### Adding New Templates

**When to add:**
- New entry type needed
- Common pattern identified
- Multiple projects need same format

**Process:**
1. Create template file
2. Follow template structure
3. Add to this index
4. Test with sample entry
5. Document usage

### Updating Templates

**Version control:**
- PATCH: Clarifications, typos
- MINOR: New sections, examples
- MAJOR: Structure changes

**Update process:**
1. Modify template
2. Update version and date
3. Add to version history
4. Update this index
5. Notify users

---

## QUALITY STANDARDS

**All templates must:**
- Follow SPEC-FILE-STANDARDS
- Include complete headers
- Provide clear instructions
- Have usage examples
- Document guidelines
- Be ≤400 lines
- Use proper formatting

---

## RELATED

- SPEC-FILE-STANDARDS.md
- SPEC-HEADERS.md
- SPEC-STRUCTURE.md
- generic-specifications-Index.md

---

**END OF FILE**