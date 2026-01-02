# PROJECT-IMPLEMENTATION.md

**Version:** 1.0.0  
**Date:** 2025-11-29  
**Project:** SIMA-File-Operations  
**Purpose:** Export/Import tools for transferring SIMA knowledge between versions  
**Type:** Project Implementation Guide

---

## PROJECT OVERVIEW

**Goal:** Build tools to export knowledge from SIMAv4.1 and import into SIMAv4.2

**Current Status:** Export tool being modularized to use SIMA module system

**Critical Context:** SIMA is currently BLANK - we're building the tools to populate it

---

## ARCHITECTURE

### Module System

**9 Modules Used:**
1. **validation** - Path/security validation
2. **ajax** - JSON request/response handling  
3. **tree** - Directory scanning and tree generation
4. **file** - File operations and archiving
5. **version** - SIMA version detection and conversion
6. **manifest** - Export manifest generation
7. **instructions** - Import instruction generation
8. **packaging** - Complete package creation
9. **ui** - HTML interface generation

**Module Location:** `/support/php/modules/`

---

## FILE STRUCTURE

```
/support/php/
├── sima-export-tool.php          # Main entry point
├── modules/
│   ├── validation/
│   │   ├── validation_module.php
│   │   ├── validation_config.php
│   │   └── internal/
│   ├── tree/
│   │   ├── tree_module.php
│   │   ├── tree_config.php
│   │   └── internal/
│   ├── file/
│   │   ├── file_module.php
│   │   ├── file_config.php
│   │   └── (internal files)
│   ├── version/
│   │   ├── version_module.php
│   │   └── internal/
│   ├── packaging/
│   │   ├── packaging_module.php
│   │   └── internal/
│   ├── manifest/
│   │   ├── manifest_module.php
│   │   └── internal/
│   ├── instructions/
│   │   ├── instructions_module.php
│   │   └── internal/
│   ├── ajax/
│   │   ├── ajax_module.php
│   │   └── internal/
│   └── ui/
│       ├── ui_module.php
│       ├── ui_config.php
│       └── internal/
├── css/
│   └── sima-styles.css
└── js/
    ├── sima-export-scan.js
    ├── sima-export-render.js
    ├── sima-export-selection.js
    └── sima-export-export.js
```

---

## MODULE CONFIGURATIONS

### 1. Validation Module

**Config File:** `modules/validation/validation_config.php`

**CRITICAL SETTING:**
```php
'path' => [
    'allow_absolute' => false  // DEFAULT - MUST CHANGE FOR EXPORT TOOL
]
```

**Required Configuration:**
```php
// In sima-export-tool.php after loading modules:
if (class_exists('ValidationModule')) {
    $validation = new ValidationModule();
    $validation->setConfig('path.allow_absolute', true);
}
```

**Why:** Export tool receives absolute paths like `/home/joe/web/claude.dizzybeaver.com/public_html`

**Initialization:**
```php
$validation = new ValidationModule();
```

**Key Methods:**
- `validatePath($path, $baseDir)` - Returns `['valid' => bool, 'errors' => array]`
- `sanitizePath($path)` - Returns sanitized string
- `preventTraversal($path, $baseDir)` - Returns bool

---

### 2. Tree Module

**Config File:** `modules/tree/tree_config.php`

**Initialization:**
```php
$tree = new TreeModule();
```

**Key Methods:**
- `scanWithVersion($basePath, $version = null)` - Returns array with tree, version, stats
- `scan($basePath, $options = [])` - Returns raw tree structure
- `formatForUI($rawTree)` - Returns UI-ready tree

**Return Structure from scanWithVersion:**
```php
[
    'tree' => [...],           // UI-formatted tree
    'version' => '4.2',        // Detected version
    'version_info' => [...],   // Version details
    'stats' => [...],          // File statistics
    'base_path' => '/full/path'
]
```

**Dependencies:** Uses version module internally

---

### 3. File Module

**Config File:** `modules/file/file_config.php`

**CRITICAL SETTING:**
```php
'export_directory' => '/tmp/sima-exports'  // DEFAULT
```

**Access Config:**
```php
$exportDir = FileConfig::getConfig('export_directory');
```

**Initialization:**
```php
$fileModule = new SIMAFileModule();
```

**Key Methods:**
- `scanDirectory($directory, $options = [])` - Scan files
- `createArchive($files, $archiveName, $options = [])` - Create ZIP

---

### 4. Version Module

**Initialization:**
```php
$version = new VersionModule();
```

**Key Methods:**
- `detect($basePath)` - Returns `['version' => string, ...]`
- `getVersionInfo($basePath)` - Returns detailed version info
- `convert($content, $fromVersion, $toVersion)` - Convert file content

---

### 5. Packaging Module

**Initialization:**
```php
$packaging = new PackagingModule();
```

**Key Method:**
```php
createExportPackage($files, $exportName, $metadata)
```

**Parameters:**
- `$files` - Array of file objects with path, size, checksum
- `$exportName` - String archive name
- `$metadata` - Array with description, source_version, target_version

**Returns:**
```php
[
    'archive_name' => 'filename.zip',
    'file_count' => 123,
    'converted_count' => 5
]
```

**Dependencies:** Uses manifest and instructions modules

---

### 6. AJAX Module

**Initialization:**
```php
$ajax = new AjaxModule();
```

**Key Methods:**
- `sendSuccess($data)` - Send JSON success response
- `sendError($message)` - Send JSON error response

**Response Format:**
```php
{
    "success": true,
    "...data..."
}
```

---

### 7. UI Module

**Functions (not class):**
```php
ui_generatePageHeader($title, $options)
ui_generatePageFooter($options)
ui_generateForm($fields, $options)
ui_generateContainer($content, $options)
ui_generateButton($text, $options)
ui_generateStatusContainer($id)
ui_generateLoadingIndicator($options)
ui_generateCssIncludes($cssFiles, $options)
ui_generateJsIncludes($jsFiles, $options)
```

**All return HTML strings**

---

## CRITICAL CONSTRAINTS

### 1. File Size Limit
**350 lines maximum per file**
- Reason: project_knowledge_search truncates beyond this
- Never exceed this limit
- Split files if needed

### 2. Export Directory
**Must use `/tmp/sima-exports`**
- Reason: open_basedir restrictions
- Configured in file_config.php
- Access via: `FileConfig::getConfig('export_directory')`

### 3. Path Handling
**Absolute paths required**
- Users provide: `/home/joe/web/claude.dizzybeaver.com/public_html`
- Validation must allow absolute paths
- Use realpath() for validation
- Check is_dir() and is_readable()

---

## COMMON ERRORS AND FIXES

### Error: "Absolute paths not allowed"
**Cause:** validation_config.php has `allow_absolute => false`  
**Fix:** Configure validation after loading:
```php
$validation->setConfig('path.allow_absolute', true);
```

### Error: "Call to undefined function validation_validatePath()"
**Cause:** Trying to call function instead of method  
**Fix:** Use object method:
```php
$validation = new ValidationModule();
$result = $validation->validatePath($path, $baseDir);
```

### Error: "Directory not within allowed path"
**Cause:** open_basedir restrictions  
**Fix:** Use /tmp/sima-exports, not relative paths like ../../exports

### Error: Module function not found
**Cause:** Assuming function names without checking actual module code  
**Fix:** Reference this document for correct function signatures

---

## WORKFLOW

### Export Process

**1. User provides directory path**
```php
$directory = $_POST['directory']; // e.g., "/home/joe/sima"
```

**2. Validate path (simple)**
```php
$validatedPath = realpath($directory);
if (!$validatedPath || !is_dir($validatedPath) || !is_readable($validatedPath)) {
    throw new Exception("Invalid directory");
}
```

**3. Scan with version detection**
```php
$tree = new TreeModule();
$result = $tree->scanWithVersion($validatedPath);
// Returns: ['tree' => ..., 'version' => ..., 'stats' => ...]
```

**4. User selects files in UI**
```javascript
// JS collects selected files
const selectedFiles = getSelectedFiles(); // Returns array of file objects
```

**5. Create export package**
```php
$packaging = new PackagingModule();
$result = $packaging->createExportPackage($selectedFiles, $archiveName, [
    'description' => $description,
    'source_version' => $sourceVersion,
    'target_version' => $targetVersion
]);
// Returns: ['archive_name' => ..., 'file_count' => ..., 'converted_count' => ...]
```

**6. Send download URL**
```php
$exportDir = FileConfig::getConfig('export_directory');
$downloadUrl = $exportDir . '/' . $result['archive_name'];

$ajax = new AjaxModule();
$ajax->sendSuccess([
    'archive_name' => $result['archive_name'],
    'file_count' => $result['file_count'],
    'download_url' => $downloadUrl
]);
```

---

## INITIALIZATION SEQUENCE

**sima-export-tool.php startup:**

```php
// 1. Load all modules
loadModules(); // Loads validation, ajax, tree, file, etc.

// 2. Configure validation for absolute paths
if (class_exists('ValidationModule')) {
    $validation = new ValidationModule();
    $validation->setConfig('path.allow_absolute', true);
}

// 3. Get export directory from file config
if (class_exists('FileConfig')) {
    $exportDir = FileConfig::getConfig('export_directory');
    define('EXPORT_DIR', $exportDir);
}

// 4. Initialize handler
$handler = new SIMAExportHandler($simaRoot);
$handler->handleRequest();
```

---

## HANDLER CLASS STRUCTURE

```php
class SIMAExportHandler {
    private $baseSearchDir;
    private $tree;
    private $version;
    private $packaging;
    private $ajax;
    
    public function __construct($baseSearchDir) {
        // Initialize module instances
        $this->tree = new TreeModule();
        $this->version = new VersionModule();
        $this->packaging = new PackagingModule();
        $this->ajax = new AjaxModule();
    }
    
    public function handleRequest() {
        $action = $_POST['action'] ?? null;
        
        if ($action === 'scan') {
            $this->handleScan();
        } elseif ($action === 'export') {
            $this->handleExport();
        } else {
            $this->showInterface();
        }
    }
    
    private function handleScan() {
        // 1. Get directory from POST
        // 2. Validate with realpath() + is_dir() + is_readable()
        // 3. Call $this->tree->scanWithVersion($path)
        // 4. Send JSON response via $this->ajax->sendSuccess($result)
    }
    
    private function handleExport() {
        // 1. Get directory, archive name, description, files from POST
        // 2. Validate directory
        // 3. Detect versions if auto
        // 4. Call $this->packaging->createExportPackage()
        // 5. Generate download URL
        // 6. Send JSON response
    }
    
    private function showInterface() {
        // Use ui_generate*() functions to build HTML
    }
}
```

---

## VERIFICATION CHECKLIST

**Before deploying changes:**

- [ ] All files ≤350 lines
- [ ] Validation configured for absolute paths
- [ ] Export directory uses FileConfig value
- [ ] Module methods called correctly (not functions)
- [ ] Error handling in place
- [ ] JSON responses use ajax module
- [ ] No hardcoded paths
- [ ] No removed security features
- [ ] Previous bug fixes preserved
- [ ] Tested scan action
- [ ] Tested export action

---

## ANTI-PATTERNS TO AVOID

**❌ DON'T:**
- Rewrite entire functions when fixing one line
- Remove validation/security when it causes errors
- Assume function names without checking module code
- Hardcode paths instead of using config
- Call module functions - most are classes with methods
- Use relative paths for exports
- Exceed 350 line limit

**✅ DO:**
- Make surgical fixes to specific lines
- Configure modules properly to allow needed behavior
- Reference this document for correct API calls
- Use config files for paths
- Initialize modules as classes, call methods
- Use /tmp/sima-exports from config
- Split files if approaching limit

---

## DEPENDENCIES BETWEEN MODULES

```
sima-export-tool.php
  ├─ uses: ajax (for responses)
  ├─ uses: tree (for scanning)
  │   └─ uses: version (for detection)
  ├─ uses: packaging (for export)
  │   ├─ uses: manifest
  │   ├─ uses: instructions
  │   └─ uses: file (for archiving)
  └─ uses: ui (for interface)
  
Validation can be used but must be configured for absolute paths
```

---

**END OF IMPLEMENTATION GUIDE**

**Remember:** This is the FIRST document to load when working on export tool  
**Purpose:** Prevent bugs from being reintroduced by having verified reference  
**Critical:** Always check this before making changes
