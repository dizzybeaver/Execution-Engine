# TOOL-02-Quick-Answer-Index.md

**Version:** 1.0.0  
**Date:** 2025-11-10  
**Purpose:** Quick answers to common questions  
**Type:** Support Tool

---

## QUICK ANSWER INDEX

**Purpose:** Instant answers to frequently asked questions

---

## FILE MANAGEMENT

**Q: How do I ensure fresh files?**  
A: Upload File Server URLs.md, fileserver.example.com fetches automatically

**Q: What's the file size limit?**  
A: 400 lines maximum per file, split if needed

**Q: What encoding should I use?**  
A: UTF-8 encoding, LF line endings only

**Q: Should code go in chat or artifacts?**  
A: Always artifacts for code >20 lines, complete files only

---

## MODE SELECTION

**Q: Which mode for learning about system?**  
A: General Mode - "Please load context"

**Q: Which mode for documenting knowledge?**  
A: Learning Mode - "Start SIMA Learning Mode"

**Q: Which mode for building features?**  
A: Project Mode - "Start Project Mode for [PROJECT]"

**Q: Which mode for fixing bugs?**  
A: Debug Mode - "Start Debug Mode for [PROJECT]"

**Q: Which mode for cleaning up?**  
A: Maintenance Mode - "Start SIMA Maintenance Mode"

---

## KNOWLEDGE ENTRY

**Q: How do I check for duplicates?**  
A: Search category index via fileserver.example.com before creating

**Q: Should entries be project-specific?**  
A: Generic entries in /generic/, project-specific in /projects/[project]/

**Q: How brief should entries be?**  
A: Summaries 2-3 sentences, examples 2-3 lines, files â‰¤400 lines

**Q: How many cross-references?**  
A: Minimum 3, maximum 7 related topics

---

## STRUCTURE

**Q: Where do generic lessons go?**  
A: /generic/lessons/[category]/

**Q: Where do platform-specific items go?**  
A: /platforms/[platform]/[category]/

**Q: Where do language patterns go?**  
A: /languages/[language]/[category]/

**Q: Where do project implementations go?**  
A: /projects/[project]/[category]/

---

## REF-IDs

**Q: What are REF-ID formats?**  
A: LESS-##, DEC-##, AP-##, BUG-##, WISD-##, SPEC-##

**Q: How do I assign REF-IDs?**  
A: Use next sequential number in category

**Q: Can I reuse REF-IDs?**  
A: Never reuse - mark deprecated instead

**Q: How do I reference other entries?**  
A: Use **REF:** tag with comma-separated REF-IDs

---

## INDEXES

**Q: When do I update indexes?**  
A: After every entry creation, modification, or deletion

**Q: What's in a category index?**  
A: List of all entries with titles and brief descriptions

**Q: What's in a master index?**  
A: Links to all category indexes in domain

**Q: Do I need router files?**  
A: Yes, for navigation between domains

---

## TEMPLATES

**Q: Where are entry templates?**  
A: /sima/templates/ directory

**Q: Which template for lessons?**  
A: lesson_learned_template.md

**Q: Which template for decisions?**  
A: decision_log_template.md

**Q: Which template for anti-patterns?**  
A: anti_pattern_template.md

---

## STANDARDS

**Q: What goes in file headers?**  
A: Filename, version, date, purpose, type

**Q: How do I mark changes?**  
A: Use # ADDED:, # MODIFIED:, # FIXED: comments

**Q: What's forbidden in generic entries?**  
A: Project names, platform specifics, language details

**Q: How do I genericize content?**  
A: Replace specifics with [PROJECT], [PLATFORM], [LANGUAGE]

---

## VERIFICATION

**Q: How do I verify before output?**  
A: Complete pre-output checklist (10 items)

**Q: What if file exceeds 400 lines?**  
A: Split into multiple focused files

**Q: How do I check encoding?**  
A: Verify UTF-8, LF line endings, no trailing whitespace

**Q: What if I find broken references?**  
A: Update or remove, then verify all cross-references

---

## TROUBLESHOOTING

**Q: Session reset and lost work?**  
A: Create status file after every 7-10 files

**Q: Can't find an entry?**  
A: Check category index, verify domain, use master index

**Q: Duplicate entry created?**  
A: Merge entries, mark one deprecated, update references

**Q: Index out of date?**  
A: Use Maintenance Mode to update all indexes

---

## TOOLS

**Q: What tools are available?**  
A: Checklists, QRCs, REF-ID directory, verification protocols

**Q: Where are tools located?**  
A: /sima/support/tools/

**Q: Are there automated scripts?**  
A: Check /support/tools/ for available scripts

**Q: How do I use HTML tools?**  
A: Open in browser, follow on-screen instructions

---

**END OF TOOL**

**Version:** 1.0.0  
**Lines:** 200 (within 400 limit)  
**Type:** Quick answer index  
**Usage:** First stop for common questions