# SIMA Tree Module

**Version:** 1.0.0  
**Date:** 2025-11-27

Universal tree scanning, formatting, and rendering module for web applications.

---

## DIRECTORY STRUCTURE

```
modules/tree/
├── tree_module.php          # Public API
├── tree_config.php          # Configuration
├── README.md                # This file
│
├── internal/                # Private components
│   ├── tree_scanner.php     # Filesystem scanning
│   ├── tree_formatter.php   # Tree formatting
│   └── tree_version.php     # Version detection
│
├── js/                      # JavaScript
│   ├── tree_render.js       # Rendering
│   └── tree_interact.js     # AJAX interaction
│
└── css/                     # Styling
    └── tree.css             # Tree styles
```

---

## QUICK START

### 1. Basic Usage

```php
<?php
require_once 'modules/tree/tree_module.php';

$tree = new TreeModule();
$result = $tree->scanWithVersion('/path/to/sima');

// Returns:
// [
//     'tree' => [...],
//     'version' => '4.2',
//     'stats' => [...],
//     'base_path' => '/path/to/sima'
// ]
```

### 2. Custom Configuration

```php
<?php
$config = [
    'scan' => [
        'max_depth' => 10,
        'file_extensions' => ['.md', '.txt']
    ],
    'ui' => [
        'show_checkboxes' => false
    ]
];

$tree = new TreeModule($config);
```

### 3. AJAX Handler

```php
<?php
// handler.php
require_once 'modules/tree/tree_module.php';

$tree = new TreeModule();

if ($_SERVER['REQUEST_METHOD'] === 'POST' && $_POST['action'] === 'scan') {
    $tree->handleScanRequest();
}
```

### 4. Frontend Integration

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="modules/tree/css/tree.css">
</head>
<body>
    <div id="tree-container"></div>
    
    <script src="modules/tree/js/tree_render.js"></script>
    <script src="modules/tree/js/tree_interact.js"></script>
    <script>
        TreeRender.init('tree-container');
        TreeInteract.init({
            endpoint: 'handler.php',
            onScanComplete: (data) => {
                TreeRender.render(data.tree);
            }
        });
        
        TreeInteract.scanDirectory('/path/to/sima');
    </script>
</body>
</html>
```

---

## API REFERENCE

### TreeModule Class

**Constructor**
```php
new TreeModule($config = null)
```

**Scanning Methods**
- `scan($basePath, $options = [])` - Scan directory, return raw tree
- `scanForUI($basePath, $options = [])` - Scan and format for UI
- `scanWithVersion($basePath, $version = null)` - Scan with version detection

**Formatting Methods**
- `formatForUI($rawTree)` - Format raw tree for UI
- `getFlatFileList($rawTree)` - Get flat array of files
- `groupByCategory($rawTree)` - Group files by category
- `generateStats($rawTree)` - Generate statistics
- `filterTree($rawTree, $criteria)` - Filter tree by criteria

**Version Methods**
- `detectVersion($basePath)` - Detect version
- `getVersionInfo($basePath)` - Get version information

**Utility Methods**
- `getAssetPaths($scriptPath = null)` - Get CSS/JS paths
- `getCSSIncludes()` - Generate CSS link tags
- `getJSIncludes()` - Generate JS script tags
- `sendJSON($success, $data, $error)` - Send JSON response
- `handleScanRequest()` - Handle AJAX scan request
- `getConfig($key, $default)` - Get config value
- `setConfig($key, $value)` - Set config value

---

## CONFIGURATION

**tree_config.php** contains all configurable options:

```php
[
    'scan_base_path' => '/path/to/sima',
    'scan' => [
        'include_hidden' => false,
        'max_depth' => 20,
        'file_extensions' => ['.md'],
        'exclude_dirs' => ['.git', 'node_modules']
    ],
    'ui' => [
        'show_checkboxes' => true,
        'collapsible' => true,
        'default_collapsed' => false
    ]
]
```

---

## JAVASCRIPT API

### TreeRender

**Initialization**
```javascript
TreeRender.init('container-id', {
    indentPixels: 20,
    showCheckboxes: true,
    collapsible: true,
    onSelectionChange: (paths) => { /* ... */ }
});
```

**Methods**
- `render(tree)` - Render tree structure
- `selectAll(checked)` - Select/deselect all
- `expandAll()` - Expand all directories
- `collapseAll()` - Collapse all directories
- `getSelectedPaths()` - Get selected file paths

### TreeInteract

**Initialization**
```javascript
TreeInteract.init({
    endpoint: 'handler.php',
    scanAction: 'scan',
    onScanStart: () => { /* ... */ },
    onScanComplete: (data) => { /* ... */ },
    onScanError: (error) => { /* ... */ }
});
```

**Methods**
- `scanDirectory(path)` - Scan directory via AJAX
- `getTree()` - Get current tree
- `getBasePath()` - Get base path

---

## EXAMPLES

### Example 1: Simple Scan

```php
<?php
require_once 'modules/tree/tree_module.php';

$tree = new TreeModule();
$rawTree = $tree->scan('/path/to/sima');
$stats = $tree->generateStats($rawTree);

echo "Total files: " . $stats['total_files'];
```

### Example 2: Filtered Scan

```php
<?php
$tree = new TreeModule();
$rawTree = $tree->scan('/path/to/sima');

$filtered = $tree->filterTree($rawTree, [
    'category' => 'lessons',
    'has_ref_id' => true
]);

$files = $tree->getFlatFileList($filtered);
```

### Example 3: Complete Integration

```php
<?php
// page.php
require_once 'modules/tree/tree_module.php';

$tree = new TreeModule();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $tree->handleScanRequest();
    exit;
}
?>
<!DOCTYPE html>
<html>
<head>
    <?= $tree->getCSSIncludes() ?>
</head>
<body>
    <input type="text" id="path" value="/path/to/sima">
    <button onclick="scan()">Scan</button>
    <div id="tree"></div>
    
    <?= $tree->getJSIncludes() ?>
    <script>
        TreeRender.init('tree');
        TreeInteract.init({
            endpoint: 'page.php',
            onScanComplete: (data) => TreeRender.render(data.tree)
        });
        
        function scan() {
            const path = document.getElementById('path').value;
            TreeInteract.scanDirectory(path);
        }
    </script>
</body>
</html>
```

---

## FEATURES

### Current Features
- ✅ Recursive directory scanning
- ✅ File metadata extraction
- ✅ Version detection (v3.0, v4.1, v4.2)
- ✅ UI-ready tree formatting
- ✅ Flat file list generation
- ✅ Category grouping
- ✅ Statistics generation
- ✅ Tree filtering
- ✅ Interactive rendering
- ✅ Checkbox selection
- ✅ Expand/collapse
- ✅ AJAX support
- ✅ Configurable options

### Future Enhancements
- Search/filter UI
- Drag and drop
- Context menus
- Keyboard navigation
- Virtual scrolling for large trees
- Export to various formats
- Caching support

---

## FILE LIMITS

**All files kept under 350 lines** to ensure:
- Full accessibility via project_knowledge_search
- No truncation by Anthropic
- Easy maintenance and updates

---

## NOTES

- Internal files in `internal/` are private - use TreeModule API only
- JavaScript files are standalone and can be used independently
- CSS is optional - tree works without styling
- Configuration file can be customized per project
- All paths are relative to module directory

---

**Version:** 1.0.0  
**Lines:** 349
