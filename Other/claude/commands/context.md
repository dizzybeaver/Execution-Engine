---
description: Provides SIMA context for a file or directory
arguments:
  - name: path
    description: The file or directory path
    required: true
---

You are providing SIMA context for: {{path}}

Load and present:

1. STRUCTURAL CONTEXT:
   - Location in EE/SIMA hierarchy
   - Related files and directories
   - Domain context

2. KNOWLEDGE CONTEXT:
   - Relevant SIMA entries
   - Related LESS/DEC/BUG entries
   - Applicable specifications

3. ARCHITECTURAL CONTEXT:
   - How {{path}} fits in UG architecture
   - Interfaces and factories involved
   - Routing patterns

4. STANDARDS CONTEXT:
   - Applicable SIMA standards
   - File standards
   - Naming conventions
   - REF-ID requirements

5. CROSS-REFERENCES:
   - What references {{path}}
   - What {{path}} references
   - Related documentation

Provide context with REF-IDs and links.
