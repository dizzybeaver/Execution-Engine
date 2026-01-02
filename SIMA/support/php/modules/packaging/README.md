# SIMA Packaging Module

**Version:** 1.0.0  
**Date:** 2025-11-27

Universal packaging module for creating organized file packages with manifests and documentation.

---

## DIRECTORY STRUCTURE

```
modules/packaging/
├── packaging_module.php         # Public API
├── packaging_config.php         # Configuration
├── README.md                    # This file
│
└── internal/                    # Private components
    ├── package_creator.php          # Package creation
    └── package_organizer.php        # File organization
```

---

## QUICK START

### 1. Basic Package

```php
<?php
require_once 'modules/packaging/packaging_module.php';

$packaging = new PackagingModule();

// Create package
$result = $packaging->create($files, 'knowledge-export', [
    'structure' => 'categorized',
    'include_manifest' => true,
    'include_instructions' => true
]);

echo "Package created: " . $result['archive_path'];
```

### 2. Export Package

```php
<?php
// Create export package (includes manifest + instructions)
$result = $packaging->createExportPackage($files, 'lessons-export', [
    'description' => 'Generic lessons export',
    'source_version' => '4.2',
    'target_version' => '4.3'
]);
```

### 3. With Custom Documentation

```php
<?php
// Create with custom docs
$result = $packaging->createComplete(
    $files,
    'export-package',
    $manifestContent,
    $instructionsContent
);
```

---

## API REFERENCE

### PackagingModule Class

**Constructor**
```php
new PackagingModule($config = null)
```

**Creation Methods**
- `create($files, $packageName, $options)` - Create package
- `createWithManifest($files, $packageName, $manifest, $options)` - With manifest
- `createWithDocumentation($files, $packageName, $docs, $options)` - With docs
- `createComplete($files, $packageName, $manifest, $instructions, $options)` - Complete

**Specialized Methods**
- `createExportPackage($files, $exportName, $metadata)` - Export package
- `createBackupPackage($files, $backupName, $metadata)` - Backup package
- `createMigrationPackage($files, $name, $from, $to)` - Migration package

**Organization Methods**
- `organize($files, $structure)` - Organize files
- `setStructure($structure)` - Set custom structure

**File Management**
- `addFiles($packagePath, $files)` - Add files to package
- `addManifest($packagePath, $manifest)` - Add manifest
- `addInstructions($packagePath, $instructions)` - Add instructions
- `finalize($packagePath)` - Create final archive

**Utility Methods**
- `getPackageInfo($packagePath)` - Get package info
- `validatePackage($packagePath)` - Validate package

---

## CONFIGURATION

**packaging_config.php** contains all options:

```php
[
    'format' => [
        'type' => 'zip',
        'compression_level' => 6
    ],
    'structures' => [
        'flat' => [...],
        'categorized' => [...],
        'hierarchical' => [...],
        'domain-based' => [...]
    ],
    'default_structure' => 'categorized'
]
```

---

## PACKAGE STRUCTURES

### Flat Structure
All files in root directory:
```
package/
├── manifest.yaml
├── import-instructions.md
├── LESS-01.md
├── LESS-02.md
└── DEC-01.md
```

### Categorized Structure
Files grouped by category:
```
package/
├── manifest.yaml
├── import-instructions.md
├── lessons/
│   ├── LESS-01.md
│   └── LESS-02.md
└── decisions/
    └── DEC-01.md
```

### Hierarchical Structure
Original paths preserved:
```
package/
├── manifest.yaml
├── import-instructions.md
└── generic/
    ├── lessons/
    │   └── LESS-01.md
    └── decisions/
        └── DEC-01.md
```

### Domain-Based Structure
Organized by domain:
```
package/
├── manifest.yaml
├── import-instructions.md
├── generic/
│   └── LESS-01.md
└── platforms/
    └── PLAT-01.md
```

---

## EXAMPLES

### Example 1: Simple Export

```php
<?php
$packaging = new PackagingModule();

$files = [
    ['path' => '/sima/generic/lessons/LESS-01.md', 'category' => 'lessons'],
    ['path' => '/sima/generic/lessons/LESS-02.md', 'category' => 'lessons']
];

$result = $packaging->create($files, 'lessons-export', [
    'structure' => 'categorized'
]);

if ($result['success']) {
    echo "Created: {$result['archive_name']}";
    echo "Size: {$result['size']} bytes";
}
```

### Example 2: Complete Package

```php
<?php
$packaging = new PackagingModule();

// Create manifest
$manifest = "operation: export\narchive:\n  name: export\n";

// Create instructions
$instructions = "# Import Instructions\n\nExtract and import files.";

// Create package
$result = $packaging->createComplete(
    $files,
    'complete-export',
    $manifest,
    $instructions,
    ['structure' => 'categorized']
);
```

### Example 3: Backup Package

```php
<?php
$packaging = new PackagingModule();

$result = $packaging->createBackupPackage($files, 'daily-backup', [
    'description' => 'Daily SIMA backup',
    'created_by' => 'automated-script'
]);
```

### Example 4: Migration Package

```php
<?php
$packaging = new PackagingModule();

$result = $packaging->createMigrationPackage(
    $files,
    'v4.2-to-v4.3',
    '4.2',
    '4.3'
);
```

### Example 5: Custom Structure

```php
<?php
$packaging = new PackagingModule();

// Define custom structure
$packaging->setStructure([
    'mappings' => [
        '/^LESS-/' => 'lessons/',
        '/^DEC-/' => 'decisions/',
        '/^AP-/' => 'anti-patterns/'
    ],
    'default' => 'other/'
]);

$result = $packaging->create($files, 'custom-export');
```

---

## PACKAGE TYPES

### Export Package
```php
[
    'structure' => 'categorized',
    'include_manifest' => true,
    'include_instructions' => true,
    'include_readme' => true
]
```

### Backup Package
```php
[
    'structure' => 'hierarchical',
    'include_manifest' => true,
    'preserve_structure' => true
]
```

### Migration Package
```php
[
    'structure' => 'categorized',
    'include_manifest' => true,
    'include_instructions' => true,
    'include_changelog' => true
]
```

---

## FEATURES

### Current Features
- ✅ Multiple structure types (flat, categorized, hierarchical, domain-based)
- ✅ Automatic manifest generation
- ✅ Automatic instructions generation
- ✅ README generation
- ✅ ZIP archive creation
- ✅ Timestamp preservation
- ✅ Custom structure support
- ✅ Package validation
- ✅ Specialized package types
- ✅ File organization
- ✅ Temp directory cleanup

---

## INTEGRATION

### With SIMA-manifest Module

```php
<?php
require_once 'modules/manifest/manifest_module.php';
require_once 'modules/packaging/packaging_module.php';

$manifest = new ManifestModule();
$packaging = new PackagingModule();

// Generate manifest
$yaml = $manifest->generate('export', $files);

// Create package with manifest
$result = $packaging->createWithManifest($files, 'export', $yaml);
```

### With SIMA-instructions Module

```php
<?php
require_once 'modules/instructions/instructions_module.php';
require_once 'modules/packaging/packaging_module.php';

$instructions = new InstructionsModule();
$packaging = new PackagingModule();

// Generate instructions
$md = $instructions->generateImportInstructions($files);

// Create complete package
$result = $packaging->createComplete($files, 'export', $yaml, $md);
```

### With Export Tool

```php
<?php
// Export tool uses packaging for final archive creation
require_once 'modules/packaging/packaging_module.php';

$packaging = new PackagingModule();

// Create export package
$result = $packaging->createExportPackage($files, $archiveName, [
    'source_version' => $sourceVersion,
    'target_version' => $targetVersion
]);
```

---

## FILE LIMITS

**All files kept under 350 lines** to ensure:
- Full accessibility via project_knowledge_search
- No truncation by Anthropic
- Easy maintenance

---

## NOTES

- Internal files in `internal/` are private - use PackagingModule API only
- Supports multiple organization structures
- Automatic documentation generation
- ZIP format with configurable compression
- Temp directories cleaned automatically
- Package validation before finalization

---

**Version:** 1.0.0  
**Lines:** 344
