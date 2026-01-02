# SIMA Manifest Module

**Version:** 1.0.0  
**Date:** 2025-11-27

Universal manifest generation, validation, and parsing module for SIMA operations.

---

## DIRECTORY STRUCTURE

```
modules/manifest/
├── manifest_module.php      # Public API
├── manifest_config.php      # Configuration
├── README.md                # This file
│
└── internal/                # Private components
    ├── manifest_generator.php   # Generation
    ├── manifest_validator.php   # Validation
    └── manifest_parser.php      # Parsing
```

---

## QUICK START

### 1. Basic Usage

```php
<?php
require_once 'modules/manifest/manifest_module.php';

$manifest = new ManifestModule();

// Generate manifest
$yaml = $manifest->generate('export', $files, [
    'archive_name' => 'knowledge-export',
    'description' => 'Generic lessons export',
    'source_version' => '4.2',
    'target_version' => '4.3'
]);

echo $yaml;
```

### 2. Save to File

```php
<?php
$result = $manifest->generateToFile(
    'export',
    $files,
    '/path/to/manifest.yaml',
    ['archive_name' => 'export-2025']
);

if ($result['success']) {
    echo "Manifest saved: " . $result['path'];
}
```

### 3. Validate Manifest

```php
<?php
$validation = $manifest->validate('/path/to/manifest.yaml');

if ($validation['valid']) {
    echo "Manifest is valid";
} else {
    print_r($validation['errors']);
}
```

### 4. Parse Manifest

```php
<?php
$data = $manifest->parse('/path/to/manifest.yaml');

if (!isset($data['error'])) {
    echo "Operation: " . $data['operation'];
    echo "Files: " . count($data['files']);
}
```

---

## API REFERENCE

### ManifestModule Class

**Constructor**
```php
new ManifestModule($config = null)
```

**Generation Methods**
- `generate($operation, $files, $metadata)` - Generate YAML manifest
- `generateToFile($operation, $files, $outputPath, $metadata)` - Generate and save
- `merge($manifest1, $manifest2)` - Merge two manifests
- `compare($manifestPath1, $manifestPath2)` - Compare manifests

**Validation Methods**
- `validate($manifestPath)` - Validate file
- `validateContent($manifestContent)` - Validate YAML content

**Parsing Methods**
- `parse($manifestPath)` - Parse file
- `parseContent($manifestContent)` - Parse YAML content
- `getFileInventory($manifestPath)` - Get file list
- `getStatistics($manifestPath)` - Get statistics

**File Management**
- `addFiles($manifestPath, $newFiles)` - Add files to manifest
- `removeFiles($manifestPath, $filesToRemove)` - Remove files

---

## CONFIGURATION

**manifest_config.php** contains all options:

```php
[
    'format' => [
        'yaml_indent' => 2,
        'include_checksums' => true,
        'checksum_algorithm' => 'md5'
    ],
    'validation' => [
        'require_operation' => true,
        'validate_ref_ids' => true
    ],
    'statistics' => [
        'enabled' => true,
        'count_by_domain' => true
    ]
]
```

---

## MANIFEST FORMAT

### Example Output

```yaml
operation: export
archive:
  name: knowledge-export
  created: 2025-11-27 10:30:00
  description: Generic lessons export
  total_files: 25
  source_version: 4.2
  target_version: 4.3
files:
  - filename: LESS-01.md
    path: generic/lessons/LESS-01.md
    ref_id: LESS-01
    category: lessons
    size: 2048
    checksum: a1b2c3d4e5f6...
  - filename: LESS-02.md
    path: generic/lessons/LESS-02.md
    ref_id: LESS-02
    category: lessons
    size: 1536
    checksum: f6e5d4c3b2a1...
statistics:
  by_domain:
    generic: 25
  by_category:
    lessons: 25
  by_extension:
    .md: 25
  total_size: 51200
  ref_ids:
    - LESS-01
    - LESS-02
```

---

## EXAMPLES

### Example 1: Export Manifest

```php
<?php
$files = [
    [
        'filename' => 'LESS-01.md',
        'path' => '/sima/generic/lessons/LESS-01.md',
        'relative_path' => 'generic/lessons/LESS-01.md',
        'ref_id' => 'LESS-01',
        'category' => 'lessons',
        'size' => 2048,
        'checksum' => 'a1b2c3...'
    ]
];

$manifest = new ManifestModule();
$yaml = $manifest->generate('export', $files, [
    'archive_name' => 'lessons-export',
    'description' => 'Lessons learned export'
]);
```

### Example 2: Import Validation

```php
<?php
$manifest = new ManifestModule();

// Validate before import
$validation = $manifest->validate('import-manifest.yaml');

if (!$validation['valid']) {
    echo "Invalid manifest:\n";
    foreach ($validation['errors'] as $error) {
        echo "- $error\n";
    }
    exit;
}

// Parse for import
$data = $manifest->parse('import-manifest.yaml');
$filesToImport = $data['files'];
```

### Example 3: Merge Manifests

```php
<?php
$manifest = new ManifestModule();

$m1 = $manifest->parse('export1.yaml');
$m2 = $manifest->parse('export2.yaml');

$merged = $manifest->merge($m1, $m2);

$manifest->generateToFile(
    'export',
    $merged['files'],
    'merged-manifest.yaml',
    ['archive_name' => 'merged-export']
);
```

### Example 4: Compare Manifests

```php
<?php
$manifest = new ManifestModule();

$comparison = $manifest->compare(
    'old-manifest.yaml',
    'new-manifest.yaml'
);

echo "Only in old: " . count($comparison['only_in_first']);
echo "Only in new: " . count($comparison['only_in_second']);
echo "Modified: " . count($comparison['modified']);
```

### Example 5: Update Manifest

```php
<?php
$manifest = new ManifestModule();

// Add new files
$newFiles = [
    [
        'filename' => 'LESS-26.md',
        'path' => 'generic/lessons/LESS-26.md',
        'ref_id' => 'LESS-26',
        'category' => 'lessons',
        'size' => 1024,
        'checksum' => 'xyz123...'
    ]
];

$result = $manifest->addFiles('manifest.yaml', $newFiles);

// Remove files
$result = $manifest->removeFiles('manifest.yaml', ['LESS-01.md']);
```

---

## FEATURES

### Current Features
- ✅ YAML manifest generation
- ✅ Multiple operation types (export/import/update)
- ✅ File inventory tracking
- ✅ Domain/category counting
- ✅ Checksum recording
- ✅ Statistics generation
- ✅ Validation with detailed errors
- ✅ Parsing with error handling
- ✅ Manifest merging
- ✅ Manifest comparison
- ✅ File addition/removal
- ✅ Configurable options

### Supported Operations
- export - Package for export
- import - Prepare for import
- update - Track updates
- backup - Backup metadata
- restore - Restoration info
- migrate - Migration tracking

---

## INTEGRATION

### With SIMA-file Module

```php
<?php
require_once 'modules/file/file_module.php';
require_once 'modules/manifest/manifest_module.php';

$fileModule = new SIMAFileModule();
$manifestModule = new ManifestModule();

// Scan files
$scanResult = $fileModule->scanDirectory('/sima/generic/lessons');
$files = $scanResult['files'];

// Generate manifest
$yaml = $manifestModule->generate('export', $files, [
    'archive_name' => 'lessons-export'
]);

// Create archive with manifest
$fileModule->createArchive($files, 'lessons.zip');
file_put_contents('manifest.yaml', $yaml);
```

### With Export Tool

```php
<?php
// Export tool uses this module for all manifest operations
require_once 'modules/manifest/manifest_module.php';

$manifest = new ManifestModule();

// Generate export manifest
$yaml = $manifest->generate('export', $selectedFiles, [
    'archive_name' => $archiveName,
    'description' => $description,
    'source_version' => $sourceVersion,
    'target_version' => $targetVersion
]);

// Save alongside archive
file_put_contents($exportDir . '/manifest.yaml', $yaml);
```

---

## FILE LIMITS

**All files kept under 350 lines** to ensure:
- Full accessibility via project_knowledge_search
- No truncation by Anthropic
- Easy maintenance

---

## NOTES

- Internal files in `internal/` are private - use ManifestModule API only
- YAML format is simple and human-readable
- Validation catches common errors before processing
- Statistics provide quick overview of manifest contents
- Configurable for different use cases

---

**Version:** 1.0.0  
**Lines:** 344
