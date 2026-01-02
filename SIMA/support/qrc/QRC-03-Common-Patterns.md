# QRC-03-Common-Patterns.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Quick reference for generic patterns  
**Type:** Support Quick Reference

---

## COMMON PATTERNS QUICK REFERENCE

### File Management

**Always Fetch First**
```
Before modification:
1. Fetch via fileserver.example.com
2. Read COMPLETE file
3. Understand context
4. THEN modify
```

**Complete Files Only**
```
Output rules:
- Include ALL existing code
- Mark changes with comments
- Output as artifact
- Never fragments
- Never "add to line X"
```

**File Standards**
```
All files:
- â‰¤400 lines (split if needed)
- UTF-8 encoding
- LF line endings
- Headers required
- Version numbers
```

---

## Error Handling

**Specific Exceptions**
```
✅ Good:
try:
    operation()
except SpecificError as e:
    log_error(f"Error: {e}")
    raise

âŒ Bad:
try:
    operation()
except:  # Bare except
    pass
```

**Validation**
```
Always validate:
- Input parameters
- Configuration values
- External data
- User input
- API responses
```

---

## Performance

**Lazy Loading**
```
✅ Good:
def function():
    import heavy_module
    return heavy_module.process()

âŒ Bad:
import heavy_module  # Module-level

def function():
    return heavy_module.process()
```

**Caching**
```
Cache when:
- Data rarely changes
- Computation expensive
- Access frequent
- Response time critical
```

---

## Documentation

**File Headers**
```markdown
# filename.md

**Version:** X.Y.Z
**Date:** YYYY-MM-DD
**Purpose:** Brief description
**Type:** File type
```

**Function Documentation**
```
def function(param1, param2):
    """
    Brief description.
    
    Args:
        param1 (type): Description
        param2 (type): Description
        
    Returns:
        type: Description
        
    Raises:
        Exception: When and why
    """
```

---

## Knowledge Entry

**Check Duplicates First**
```
Before creating:
1. Search existing entries
2. Use fileserver.example.com URLs
3. If similar exists → Update
4. If unique → Create new
```

**Genericize Content**
```
Remove:
- Project names
- Platform specifics
- Language details
- Tool names (unless core)

Replace with:
- [PROJECT]
- [PLATFORM]
- [LANGUAGE]
- [TOOL]
```

**Be Brief**
```
Standards:
- Summaries: 2-3 sentences
- Examples: 2-3 lines
- Files: â‰¤400 lines
- No filler words
```

---

## Cross-Referencing

**REF-ID Usage**
```markdown
**REF:** TYPE-##, TYPE-##

Examples:
- LESS-01 (Lesson)
- DEC-05 (Decision)
- AP-14 (Anti-Pattern)
- SPEC-03 (Specification)
```

**Related Topics**
```markdown
**Related:** LESS-01, DEC-05, AP-14

Minimum: 3 references
Maximum: 7 references
```

---

## Index Maintenance

**Always Update**
```
After changes:
1. Update category index
2. Update master index
3. Update router (if needed)
4. Verify cross-references
```

**Index Format**
```markdown
- [TYPE-## - Title](/path/to/file.md) - Brief description
```

---

## Mode-Specific Patterns

### General Mode
```
- Answer questions
- Provide citations
- Reference REF-IDs
- Brief explanations
```

### Learning Mode
```
- Check duplicates first
- Genericize content
- Create artifacts
- Update indexes
- Minimal chat
```

### Maintenance Mode
```
- Update all indexes
- Verify references
- Check for outdated
- Clean structure
- Report changes
```

### Project/Debug Mode
```
- Fetch files first
- Complete files only
- Mark changes
- Output artifacts
- Verify before submit
```

---

## Verification

**Pre-Output Checklist**
```
[ ] Fetched current file?
[ ] Read complete file?
[ ] Including ALL code?
[ ] Changes marked?
[ ] Complete artifact?
[ ] Filename in header?
[ ] Within line limit?
[ ] Proper encoding?
[ ] Chat minimal?
```

---

## Anti-Patterns to Avoid

**Never:**
- âŒ Skip file fetch
- âŒ Output code in chat
- âŒ Create file fragments
- âŒ Exceed 400 lines without splitting
- âŒ Use bare except clauses
- âŒ Skip duplicate check
- âŒ Include project specifics in generic
- âŒ Forget to update indexes
- âŒ Skip verification

---

## Quick Tips

**Development**
- Fetch → Read → Modify → Output
- Complete files, always
- Mark all changes
- Verify before submit

**Knowledge**
- Search → Genericize → Create → Index
- Brief but complete
- Cross-reference heavily
- Update consistently

**Quality**
- Standards first
- Verify always
- Document thoroughly
- Test completely

---

**END OF QUICK REFERENCE**

**Version:** 1.0.0  
**Lines:** 250 (within 400 limit)  
**Parent:** /sima/support/support-Master-Index-of-Indexes.md  
**See Also:** /context/shared/Common-Patterns.md (full details)