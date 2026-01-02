# Directory Tree Generation - File Analysis

**Analysis Date:** 2025-11-27  
**Purpose:** Identify all files directly related to directory tree generation

---

## CORE TREE GENERATION FILES

### 1. sima-scanner.php (PRIMARY - Data Collection)
**Location:** /support/php/  
**Purpose:** Scans filesystem and collects file data

**Key Functions:**
- `scanComplete($basePath, $options)` - Main entry point, scans entire directory tree
- `scanDirectoryRecursive($basePath, $relativePath, $options, $depth)` - Recursive directory scanning
- `scanDirectory($basePath, $relativePath, $options, $depth)` - Scans single directory
- `getSubdirectories($path, $options)` - Gets list of subdirectories
- `extractQuickMetadata($filepath)` - Extracts version, REF-ID, category from files
- `countFiles($tree)` - Counts total files in tree
- `countDirectories($tree)` - Counts total directories

**Output Format:**
```php
[
    'base_path' => '/path/to/sima',
    'total_files' => 150,
    'total_directories' => 25,
    'directories' => [
        'root' => [
            'path' => 'root',
            'files' => [...],
            'subdirectories' => []
        ],
        'generic' => [
            'path' => 'generic',
            'files' => [...],
            'subdirectories' => [
                'lessons' => [...],
                'decisions' => [...]
            ]
        ]
    ],
    'scan_timestamp' => '2025-11-27 10:30:00'
]
```

**Note:** This is the RAW scanner output. It's a nested structure that represents the actual filesystem hierarchy.

---

### 2. sima-tree-formatter.php (PRIMARY - Data Transformation)
**Location:** /support/php/  
**Purpose:** Converts scanner output to UI-compatible tree format

**Key Functions:**
- `formatForUI($scanTree)` - Main conversion function (scanner → UI format)
- `formatDirectory($name, $data)` - Formats directory nodes recursively
- `formatFile($file, $parentPath)` - Formats file nodes
- `isSubdirectoryOfAny($dirName, $parentDirs, $allDirectories)` - Hierarchy validation
- `hasSubdirectory($dirData, $subdirName)` - Checks for subdirectory presence
- `countAllFiles($data)` - Counts files in directory tree

**Additional Utility Functions:**
- `getFlatFileList($scanTree)` - Flattens tree to array of files
- `collectFiles($data, &$files)` - Recursively collects files
- `groupByCategory($scanTree)` - Groups files by category/domain
- `determineCategoryFromPath($path)` - Extracts category from path
- `generateStats($scanTree)` - Generates statistics
- `filterTree($scanTree, $criteria)` - Filters tree by criteria
- `filterDirectory($data, $criteria)` - Filters directory recursively
- `matchesCriteria($file, $criteria)` - Checks if file matches filter

**Output Format:**
```php
[
    [
        'type' => 'directory',
        'name' => 'generic',
        'path' => 'generic',
        'file_count' => 15,
        'total_files' => 45,
        'children' => [
            [
                'type' => 'file',
                'name' => 'LESS-01.md',
                'path' => 'generic/lessons/LESS-01.md',
                'size' => 5432,
                'modified' => 1701234567,
                'version' => '1.0.0',
                'ref_id' => 'LESS-01',
                'category' => 'lessons'
            ],
            [
                'type' => 'directory',
                'name' => 'lessons',
                'path' => 'generic/lessons',
                'file_count' => 10,
                'total_files' => 10,
                'children' => [...]
            ]
        ]
    ]
]
```

**Note:** This is the UI-READY format. It's a flat array of top-level nodes, each containing nested children.

---

### 3. sima-export-render.js (FRONTEND - Display)
**Location:** /support/php/js/  
**Purpose:** Renders the tree in HTML with interactivity

**Key Functions:**
- `renderTree()` - Main render function, iterates through tree nodes
- `renderNode(node, depth)` - Renders individual node (file or directory)
- `selectAll(checked)` - Selects/deselects all files in tree
- `toggleNode(node, toggle)` - Expands/collapses directory nodes

**What It Does:**
- Takes UI-formatted tree from sima-tree-formatter.php
- Generates HTML DOM elements
- Creates checkboxes for selection
- Adds expand/collapse functionality
- Applies indentation based on depth
- Shows file/directory icons
- Displays file counts

**HTML Output Structure:**
```html
<div style="margin-left: 0px; padding: 5px;">
    <div style="cursor: pointer; font-weight: bold;">
        <span>▼ </span>
        <span>📁 generic (45 files)</span>
    </div>
    <div>
        <!-- Children rendered recursively -->
    </div>
</div>
```

---

## SUPPORTING FILES (Used by Tree Generation)

### 4. sima-version-utils.php (SUPPORTING)
**Location:** /support/php/  
**Purpose:** Version detection and scanning coordination

**Functions Used in Tree Generation:**
- `detectVersion($basePath)` - Auto-detects SIMA version
- `scanWithVersion($basePath, $version)` - Calls scanner, formats for UI
- `getFlatFileList($basePath, $version)` - Gets flat file list
- `getStats($basePath, $version)` - Gets statistics

**Role:** Orchestrates scanner and formatter, adds version awareness

**Flow:**
```
detectVersion() 
    ↓
scanWithVersion()
    ↓ calls
SIMAScanner::scanComplete()
    ↓ passes to
SIMATreeFormatter::formatForUI()
    ↓ returns
UI-ready tree
```

---

### 5. sima-export-scan.js (SUPPORTING - AJAX)
**Location:** /support/php/js/  
**Purpose:** Initiates scan via AJAX request

**Key Functions:**
- `scanDirectory()` - Sends scan request to server

**What It Does:**
- Gets directory path from input
- Sends POST request to PHP
- Receives JSON response with tree
- Stores tree in `window.knowledgeTree`
- Calls `renderTree()` to display
- Shows version info and stats

**Not directly tree generation, but triggers the process.**

---

### 6. sima-export-selection.js (SUPPORTING - Interaction)
**Location:** /support/php/js/  
**Purpose:** Manages file selection in tree

**Key Functions:**
- `getSelectedFiles()` - Collects selected file paths
- `collectCheckedPaths(element, paths)` - Recursively finds checked items
- `updateSummary()` - Updates selection count display

**Not tree generation, but works with rendered tree.**

---

## EXPORT-TOOL SPECIFIC (Use Tree but Not Core)

### 7. sima-export-handler.php
**Location:** /support/php/  
**Uses Tree Functions:** YES
**Directly Generates Tree:** NO

**What It Does:**
- Receives AJAX requests
- Calls `SIMAVersionUtils::scanWithVersion()` 
- Returns JSON with tree data
- Does NOT generate tree itself

**Role:** Bridge between AJAX and tree generation functions

---

### 8. sima-export-export.js
**Location:** /support/php/js/  
**Uses Tree Functions:** YES  
**Directly Generates Tree:** NO

**What It Does:**
- Collects selected files from rendered tree
- Sends export request
- Displays results

**Role:** Works with tree, doesn't create it

---

## DATA FLOW DIAGRAM

```
User Action (Scan Button)
    ↓
sima-export-scan.js::scanDirectory()
    ↓ AJAX POST
sima-export-handler.php::handleScanAction()
    ↓ calls
SIMAVersionUtils::detectVersion()
    ↓ calls
SIMAVersionUtils::scanWithVersion()
    ↓ calls
SIMAScanner::scanComplete()
    │
    ├─ Scans filesystem
    ├─ Reads .md files
    ├─ Extracts metadata
    └─ Returns nested tree structure
    ↓
SIMATreeFormatter::formatForUI()
    │
    ├─ Converts nested to flat-with-children
    ├─ Adds UI properties
    ├─ Counts files
    └─ Returns UI-ready tree
    ↓
JSON response to browser
    ↓
sima-export-scan.js receives data
    ↓
window.knowledgeTree = data.tree
    ↓
renderTree() called
    ↓
sima-export-render.js::renderTree()
    │
    ├─ Creates HTML elements
    ├─ Adds interactivity
    ├─ Renders recursively
    └─ Displays in DOM
    ↓
User sees tree
```

---

## SUMMARY BY ROLE

### PRIMARY TREE GENERATION (3 files)
1. **sima-scanner.php** - Scans filesystem, collects data
2. **sima-tree-formatter.php** - Transforms data to UI format
3. **sima-export-render.js** - Renders HTML tree

**These 3 files ARE the tree generation system.**

### SUPPORTING (3 files)
4. **sima-version-utils.php** - Orchestrates scanner/formatter
5. **sima-export-scan.js** - Triggers process via AJAX
6. **sima-export-selection.js** - Manages interaction with rendered tree

**These support but don't generate.**

### EXPORT-TOOL SPECIFIC (2 files)
7. **sima-export-handler.php** - AJAX handler, calls tree functions
8. **sima-export-export.js** - Uses tree for export selection

**These USE tree functions for export-specific purposes.**

---

## REUSABILITY ASSESSMENT

### Fully Reusable (Tree Generation Core)
- ✅ sima-scanner.php
- ✅ sima-tree-formatter.php
- ✅ sima-version-utils.php

**Can be used in ANY tool that needs to scan and display SIMA structure.**

### Partially Reusable (Generic Rendering)
- ⚠️ sima-export-render.js - Generic tree rendering, but includes checkboxes (export-specific)

**Could be made more generic by parameterizing checkbox behavior.**

### Tool-Specific (Export Only)
- ❌ sima-export-scan.js - Export tool specific
- ❌ sima-export-selection.js - Export tool specific
- ❌ sima-export-handler.php - Export tool specific
- ❌ sima-export-export.js - Export tool specific

**These would need modification for other tools.**

---

## NOTES FOR NEW TOOL DEVELOPMENT

**If building a new tool that needs directory tree:**

**Reuse These:**
1. sima-scanner.php (as-is)
2. sima-tree-formatter.php (as-is)
3. sima-version-utils.php (as-is)

**Adapt This:**
4. sima-export-render.js (remove/parameterize checkboxes)

**Replace These:**
5. Tool-specific AJAX handler (like sima-export-handler.php)
6. Tool-specific UI JavaScript (like sima-export-scan.js, sima-export-export.js)

**Architecture:**
```
PHP Layer:
- sima-scanner.php (reuse)
- sima-tree-formatter.php (reuse)
- sima-version-utils.php (reuse)
- your-tool-handler.php (new)

JS Layer:
- sima-tree-render.js (adapt from sima-export-render.js)
- your-tool-ui.js (new)
```

---

**END OF ANALYSIS**

**Core Tree Files:** 3 (scanner, formatter, renderer)  
**Supporting Files:** 3 (version-utils, scan trigger, selection)  
**Export-Specific:** 2 (handler, export logic)  
**Total Analyzed:** 8 files
