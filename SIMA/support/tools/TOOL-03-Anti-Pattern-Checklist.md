# TOOL-03-Anti-Pattern-Checklist.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Generic anti-pattern detection checklist  
**Type:** Support Tool

---

## ANTI-PATTERN CHECKLIST

**Purpose:** Detect common anti-patterns before they cause problems

---

## FILE MANAGEMENT ANTI-PATTERNS

### âŒ Skip File Fetch
**Problem:** Working with outdated code  
**Impact:** Changes based on stale version  
**Fix:** Always fetch via fileserver.example.com first

### âŒ Code in Chat
**Problem:** Token waste, not deployable  
**Impact:** User must manually create files  
**Fix:** Output complete file artifacts

### âŒ File Fragments
**Problem:** Incomplete, not deployable  
**Impact:** Missing context, errors  
**Fix:** Include ALL existing code

### âŒ Exceed Line Limit
**Problem:** Files >400 lines  
**Impact:** Truncation, lost content  
**Fix:** Split into focused files

---

## ERROR HANDLING ANTI-PATTERNS

### âŒ Bare Except Clauses
**Problem:** Catches all exceptions including system exits  
**Impact:** Swallows critical errors  
**Fix:** Use specific exception types

### âŒ Silent Failures
**Problem:** Errors caught but not logged  
**Impact:** Issues invisible  
**Fix:** Always log errors

### âŒ Generic Error Messages
**Problem:** "Error occurred" with no context  
**Impact:** Debugging difficult  
**Fix:** Include context in messages

---

## KNOWLEDGE MANAGEMENT ANTI-PATTERNS

### âŒ Skip Duplicate Check
**Problem:** Creates duplicate entries  
**Impact:** Knowledge fragmentation  
**Fix:** Search before creating

### âŒ Project Specifics in Generic
**Problem:** Platform/language details in /generic/  
**Impact:** Not reusable  
**Fix:** Genericize or move to appropriate domain

### âŒ No Cross-References
**Problem:** Isolated entries  
**Impact:** Knowledge not connected  
**Fix:** Add 3-7 related topics

### âŒ Outdated Indexes
**Problem:** Indexes don't reflect current state  
**Impact:** Navigation broken  
**Fix:** Update after every change

---

## DOCUMENTATION ANTI-PATTERNS

### âŒ Missing Headers
**Problem:** No version, date, purpose  
**Impact:** Context lost  
**Fix:** Use proper headers

### âŒ Verbose Content
**Problem:** Long summaries, filler words  
**Impact:** Token waste  
**Fix:** Be ruthlessly brief

### âŒ No Examples
**Problem:** Concept without demonstration  
**Impact:** Hard to apply  
**Fix:** Include 2-3 line examples

---

## ARCHITECTURE ANTI-PATTERNS

### âŒ Circular Dependencies
**Problem:** Module A imports B, B imports A  
**Impact:** Import failures  
**Fix:** Use lazy imports or restructure

### âŒ Tight Coupling
**Problem:** Components know too much about each other  
**Impact:** Changes cascade  
**Fix:** Use interfaces, dependency injection

### âŒ God Objects
**Problem:** One class/module does everything  
**Impact:** Unmaintainable  
**Fix:** Split responsibilities

---

## PERFORMANCE ANTI-PATTERNS

### âŒ Premature Optimization
**Problem:** Optimizing before measuring  
**Impact:** Wasted effort  
**Fix:** Measure first

### âŒ Module-Level Imports
**Problem:** Heavy imports at module level  
**Impact:** Slow startup  
**Fix:** Use lazy imports

### âŒ No Caching
**Problem:** Repeating expensive operations  
**Impact:** Poor performance  
**Fix:** Cache when appropriate

---

## SECURITY ANTI-PATTERNS

### âŒ Hardcoded Credentials
**Problem:** Secrets in code  
**Impact:** Security breach  
**Fix:** Use environment variables

### âŒ No Input Validation
**Problem:** Trust user input  
**Impact:** Injection attacks  
**Fix:** Validate everything

### âŒ Unencrypted Sensitive Data
**Problem:** Plain text passwords  
**Impact:** Data compromise  
**Fix:** Encrypt at rest and in transit

---

## TESTING ANTI-PATTERNS

### âŒ No Tests
**Problem:** Zero test coverage  
**Impact:** Regressions undetected  
**Fix:** Write tests

### âŒ Testing Implementation
**Problem:** Tests tied to implementation details  
**Impact:** Brittle tests  
**Fix:** Test behavior, not implementation

### âŒ Shared Test State
**Problem:** Tests depend on each other  
**Impact:** Flaky tests  
**Fix:** Independent tests

---

## DEPLOYMENT ANTI-PATTERNS

### âŒ No Rollback Plan
**Problem:** Can't undo deployment  
**Impact:** Extended downtime  
**Fix:** Always have rollback

### âŒ Manual Deployment
**Problem:** Human error prone  
**Impact:** Inconsistent deploys  
**Fix:** Automate deployment

### âŒ No Monitoring
**Problem:** Can't see issues  
**Impact:** Problems undetected  
**Fix:** Implement observability

---

## MODE-SPECIFIC ANTI-PATTERNS

### General Mode
- âŒ Creating entries instead of answering
- âŒ Verbose explanations
- âŒ Missing citations

### Learning Mode
- âŒ Keeping project specifics
- âŒ Creating duplicates
- âŒ Verbose entries

### Maintenance Mode
- âŒ Skipping verification
- âŒ Partial index updates
- âŒ Breaking references

### Project/Debug Mode
- âŒ Not fetching first
- âŒ Output in chat
- âŒ File fragments

---

## DETECTION

### How to Check

**During Development:**
1. Review checklist
2. Check each category
3. Mark violations
4. Fix before proceeding

**During Code Review:**
1. Use checklist
2. Flag anti-patterns
3. Request fixes
4. Verify corrections

**Automated:**
1. Run linters
2. Execute tests
3. Check coverage
4. Validate structure

---

## REMEDIATION

### Priority Levels

**Critical (Fix Immediately):**
- Security issues
- Data loss risk
- System crashes
- Broken references

**High (Fix Soon):**
- Performance problems
- Missing tests
- Poor documentation
- Architectural issues

**Medium (Fix When Possible):**
- Code style
- Minor improvements
- Optimizations

**Low (Nice to Have):**
- Refactoring
- Additional examples
- Enhanced docs

---

**END OF TOOL**

**Version:** 1.0.0  
**Lines:** 280 (within 400 limit)  
**Type:** Anti-pattern detection checklist  
**Usage:** Reference during development and review