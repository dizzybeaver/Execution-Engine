# SIMA Export Tool - File Dependencies

**Version:** 4.4.1  
**Main File:** sima-export-tool.php  
**Base Directory:** /support/php/

---

## DIRECTORY STRUCTURE

```
/support/php/
├── sima-export-tool.php (main entry point)
├── sima-export-handler.php (request handler)
├── sima-common.php (shared utilities)
├── sima-scanner.php (file scanning)
├── sima-tree-formatter.php (tree rendering)
├── sima-version-utils.php (version detection)
├── sima-export-helpers.php (export wrapper)
├── sima-export-archive.php (archive creation)
├── sima-export-manifest.php (manifest generation)
├── sima-export-instructions.php (instruction generation)
│
├── css/
│   └── sima-styles.css (UI styling)
│
└── js/
    ├── sima-export-scan.js (scan functionality)
    ├── sima-export-render.js (tree rendering)
    ├── sima-export-selection.js (file selection)
    └── sima-export-export.js (export execution)
```

---

## PHP FILE DEPENDENCIES

### 1. sima-export-tool.php (Main Entry)
**Requires:**
- `sima-export-handler.php`

**Functions:**
- Entry point for both HTML interface and AJAX requests
- Configures base search directory
- Manages output buffering
- Routes to SIMAExportHandler class

---

### 2. sima-export-handler.php (Request Handler)
**Requires:**
- `sima-common.php`
- `sima-scanner.php`
- `sima-tree-formatter.php`
- `sima-version-utils.php`
- `sima-export-helpers.php`

**Functions:**
- Handles AJAX requests (scan, export)
- Security validation (path checking)
- Asset path management (CSS/JS)
- HTML interface generation
- JSON response handling

---

### 3. sima-common.php (Shared Utilities)
**Requires:** None (base file)

**Functions:**
- `sendJsonResponse()` - JSON output
- `arrayToYaml()` - YAML conversion
- `calculateChecksum()` - File checksums
- Common utility functions

---

### 4. sima-scanner.php (File Scanning)
**Requires:** None

**Functions:**
- `scanSIMADirectory()` - Recursive directory scan
- `extractRefId()` - Extract REF-ID from files
- `extractVersion()` - Extract version from files
- `shouldIncludeFile()` - File filtering
- File metadata extraction

---

### 5. sima-tree-formatter.php (Tree Rendering)
**Requires:** None

**Functions:**
- `formatAsTree()` - Generate tree structure
- HTML tree generation
- Indentation and icons
- Checkbox rendering for selection

---

### 6. sima-version-utils.php (Version Detection)
**Requires:**
- `sima-scanner.php`

**Functions:**
- `detectVersion()` - Auto-detect SIMA version
- `getVersionInfo()` - Get version details
- `scanWithVersion()` - Version-aware scanning
- `getStats()` - File statistics
- Version-specific handling (v4.1, v4.2, v4.3)

---

### 7. sima-export-helpers.php (Export Wrapper)
**Requires:**
- `sima-export-archive.php`
- `sima-export-manifest.php`
- `sima-export-instructions.php`

**Functions:**
- `createExportArchive()` - Main entry point wrapper
- Loads modular export components

---

### 8. sima-export-archive.php (Archive Creation)
**Requires:**
- `sima-common.php`
- `sima-export-manifest.php`
- `sima-export-instructions.php`

**Functions:**
- `_createExportArchive()` - Create ZIP archive
- File copying and validation
- Version conversion (if needed)
- Export directory management
- Download URL generation

---

### 9. sima-export-manifest.php (Manifest Generation)
**Requires:**
- `sima-common.php`

**Functions:**
- `generateManifest()` - Create manifest.yaml
- File inventory tracking
- Domain/category counting
- Checksum recording
- Metadata compilation

---

### 10. sima-export-instructions.php (Instructions)
**Requires:** None

**Functions:**
- `generateImportInstructions()` - Create import-instructions.md
- File grouping by directory
- Installation state documentation
- Import process guide
- Markdown formatting

---

## CSS DEPENDENCIES

### css/sima-styles.css
**Used by:** HTML interface in sima-export-handler.php

**Provides:**
- Container and layout styles
- Button styling
- Form input styles
- Tree view styles
- Status message styles (error, success, warning, info)
- Loading indicator styles
- File selection styles

---

## JAVASCRIPT DEPENDENCIES

### 1. js/sima-export-scan.js
**Purpose:** Directory scanning functionality

**Functions:**
- `scanDirectory()` - Initiate scan AJAX request
- Error handling for scan
- Status display updates
- Base path validation

---

### 2. js/sima-export-render.js
**Purpose:** Tree rendering and display

**Functions:**
- `renderTree()` - Display file tree
- `renderTreeItem()` - Render individual items
- `selectAll()` - Select/deselect all files
- Checkbox state management
- Version info display
- Statistics display

---

### 3. js/sima-export-selection.js
**Purpose:** File selection management

**Functions:**
- `getSelectedFiles()` - Collect selected paths
- `collectCheckedPaths()` - Recursive checkbox collection
- Path array building
- Selection counting

---

### 4. js/sima-export-export.js
**Purpose:** Export execution

**Functions:**
- `exportFiles()` - Execute export AJAX request
- Export form data collection
- Result display
- Download link generation
- Error handling for export

---

## DATA FLOW

```
1. User loads sima-export-tool.php
   ↓
2. Shows HTML interface (CSS loaded)
   ↓
3. User enters directory, clicks Scan
   ↓
4. sima-export-scan.js → AJAX request
   ↓
5. sima-export-handler.php receives request
   ↓
6. Loads: common, scanner, tree-formatter, version-utils
   ↓
7. sima-version-utils.php detects version, scans files
   ↓
8. sima-tree-formatter.php formats tree HTML
   ↓
9. JSON response → sima-export-render.js
   ↓
10. Tree displayed, user selects files
    ↓
11. User clicks Export
    ↓
12. sima-export-export.js → AJAX request
    ↓
13. sima-export-handler.php receives export request
    ↓
14. sima-export-helpers.php → sima-export-archive.php
    ↓
15. Creates ZIP with manifest and instructions
    ↓
16. Returns download URL
    ↓
17. User downloads export package
```

---

## REQUIRED FILES SUMMARY

### PHP Files (10 total)
1. sima-export-tool.php
2. sima-export-handler.php
3. sima-common.php
4. sima-scanner.php
5. sima-tree-formatter.php
6. sima-version-utils.php
7. sima-export-helpers.php
8. sima-export-archive.php
9. sima-export-manifest.php
10. sima-export-instructions.php

### CSS Files (1 total)
1. css/sima-styles.css

### JS Files (4 total)
1. js/sima-export-scan.js
2. js/sima-export-render.js
3. js/sima-export-selection.js
4. js/sima-export-export.js

### Generated Directories
- exports/ (created automatically for ZIP files)

---

## NOTES

**Location:** All files in `/support/php/` except subdirectories
**CSS Path:** `/support/php/css/`
**JS Path:** `/support/php/js/`
**Export Path:** `/support/php/exports/` (auto-created)

**Asset Loading:** Paths auto-detected based on script location
**Security:** All file access validated against base directory
**Error Handling:** Comprehensive logging and JSON error responses

---

**END OF DEPENDENCY MAP**

**Total Files:** 15 (10 PHP + 1 CSS + 4 JS)  
**Main Entry:** sima-export-tool.php  
**Interface:** HTML with AJAX functionality
