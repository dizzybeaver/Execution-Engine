# SIMA Update Summary - Project Knowledge Priority

**Date:** 2025-11-21  
**Version:** 4.2.3  
**Change:** Prioritize project knowledge over file server access

---

## PRIMARY CHANGES

### 1. Custom-Instructions-for-AI-assistant.md ✅
**Location:** `/sima/context/shared/`  
**Status:** Updated  
**Key Changes:**
- Default to project_knowledge_search
- File server is explicit opt-in only
- 350-line limit enforced (not 400)
- Updated verification checklist

---

## FILES REQUIRING UPDATES

### Context Files

**1. context-General-Mode-Context.md**
- Update file access instructions
- Prioritize project knowledge
- 350-line limit enforcement

**2. context-PROJECT-MODE-Context.md**
- Update file retrieval workflow
- Default to project knowledge
- File server as explicit option

**3. context-DEBUG-MODE-Context.md**
- Update code access pattern
- Project knowledge first
- File server when requested

**4. context-SIMA-PROJECT-MODE.md**
- SIMA-specific project mode
- Project knowledge priority
- Development workflow updates

**5. context-SIMA-LEARNING-MODE-Context.md**
- Duplicate checking via project knowledge
- File server for edge cases only

**6. All MODE-SELECTOR files**
- Reference project knowledge default
- Note file server as option

---

### Documentation Files

**7. README.md**
- Update quick start
- Remove mandatory file server upload
- Add project knowledge explanation

**8. SIMA-Quick-Reference-Card.md**
- Update session start procedure
- Project knowledge as default
- File server as optional

**9. SIMAv4.2.2-User-Guide.md**
- Revise getting started section
- Project knowledge first approach
- File server for advanced use

**10. SIMAv4.2.2-Quick-Start-Guide.md**
- Remove File-Server-URLs.md from required steps
- Add project knowledge explanation
- File server as optional step

**11. SIMAv4.2.2-File-Server-URLs-Guide.md**
- Mark as "Advanced/Optional"
- Explain when needed
- Not required for basic use

---

### Support Files

**12. QRC-03-Common-Patterns.md**
- Update file access patterns
- Project knowledge workflows
- File server optional patterns

**13. All workflow files**
- Update to use project knowledge
- File server as alternative

---

## SPECIFICATION UPDATES

**14. SPEC-FILE-STANDARDS.md**
- Change max lines from 400 to 350
- Emphasize truncation at 350
- Update all examples

**15. SPEC-LINE-LIMITS.md**
- Update limit to 350 lines
- Explain 22% loss if exceeded
- Add project_knowledge_search constraint

---

## BEHAVIORAL CHANGES

### Old Behavior
```
Session start:
1. User uploads File-Server-URLs.md (REQUIRED)
2. AI fetches fileserver.php
3. AI gets cache-busted URLs
4. Mode activation
5. Work begins
```

### New Behavior
```
Session start:
1. User activates mode (e.g., "Please load context")
2. AI uses project_knowledge_search automatically
3. Work begins immediately

Optional (explicit request):
1. User uploads File-Server-URLs.md
2. User says "use file server"
3. AI fetches fileserver.php
4. AI uses file server for session
```

---

## PRIORITY ORDER FOR UPDATES

### Critical (Do First)
1. ✅ Custom-Instructions-for-AI-assistant.md
2. context-General-Mode-Context.md
3. context-PROJECT-MODE-Context.md
4. README.md
5. SPEC-FILE-STANDARDS.md
6. SPEC-LINE-LIMITS.md

### High Priority
7. SIMA-Quick-Reference-Card.md
8. SIMAv4.2.2-Quick-Start-Guide.md
9. context-DEBUG-MODE-Context.md
10. context-SIMA-PROJECT-MODE.md

### Medium Priority
11. All other mode contexts
12. All user documentation
13. Support files

### Low Priority
14. File-Server-URLs-Guide.md (mark as advanced)
15. Migration guides
16. Installation guides

---

## TESTING CHECKLIST

After updates:

- [ ] Activate General Mode without File-Server-URLs.md
- [ ] Verify project_knowledge_search is used
- [ ] Test file access via project knowledge
- [ ] Verify file server still works when explicitly requested
- [ ] Confirm 350-line limit is enforced
- [ ] Test all modes with project knowledge
- [ ] Verify documentation accuracy

---

## COMMUNICATION TO USERS

### Key Messages

1. **File server now optional** - Not required for basic use
2. **Project knowledge is default** - Faster, simpler access
3. **350-line limit** - Critical constraint (was 400)
4. **File server still available** - For advanced use cases

### Migration Note

**For existing users:**
- Your workflows still work
- File server still supported
- Simply don't upload File-Server-URLs.md unless needed
- Project knowledge provides faster access

---

## VERSION CHANGE

**From:** 4.2.2-blank  
**To:** 4.2.3  
**Reason:** Behavioral change (project knowledge priority)

**Semantic versioning:**
- PATCH increment (4.2.2 → 4.2.3)
- Backward compatible
- Behavioral improvement
- No breaking changes

---

**END OF SUMMARY**

**Next Action:** Update remaining context files per priority order
