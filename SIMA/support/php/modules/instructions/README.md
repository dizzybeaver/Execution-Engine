# SIMA Instructions Module

**Version:** 1.0.0  
**Date:** 2025-11-27

Universal instructions generation module for SIMA operations.

---

## DIRECTORY STRUCTURE

```
modules/instructions/
├── instructions_module.php      # Public API
├── instructions_config.php      # Configuration
├── README.md                    # This file
│
└── internal/                    # Private components
    ├── instructions_generator.php   # Generation
    └── instructions_formatter.php   # Formatting
```

---

## QUICK START

### 1. Basic Usage

```php
<?php
require_once 'modules/instructions/instructions_module.php';

$instructions = new InstructionsModule();

// Generate import instructions
$markdown = $instructions->generate('import', $files, [
    'archive_name' => 'knowledge-import',
    'source_version' => '4.2',
    'target_version' => '4.3'
]);

echo $markdown;
```

### 2. Save to File

```php
<?php
$result = $instructions->generateToFile(
    'import',
    $files,
    '/path/to/import-instructions.md',
    ['archive_name' => 'import-2025']
);

if ($result['success']) {
    echo "Instructions saved: " . $result['path'];
}
```

### 3. Custom Sections

```php
<?php
// Add custom section
$section = $instructions->addSection(
    'Prerequisites',
    'Ensure you have backup before proceeding.'
);

// Format file list
$fileList = $instructions->formatFileList($files, 'category');

// Format checklist
$checklist = $instructions->formatChecklist([
    'Backup files',
    'Review changes',
    'Run tests'
]);
```

---

## API REFERENCE

### InstructionsModule Class

**Constructor**
```php
new InstructionsModule($config = null)
```

**Generation Methods**
- `generate($operation, $files, $options)` - Generate instructions
- `generateToFile($operation, $files, $outputPath, $options)` - Generate and save
- `generateImportInstructions($files, $options)` - Import-specific
- `generateExportInstructions($files, $options)` - Export-specific
- `generateUpdateInstructions($files, $options)` - Update-specific
- `generateRestoreInstructions($files, $options)` - Restore-specific
- `generateMigrationInstructions($files, $options)` - Migration-specific
- `generateCustom($title, $sections, $options)` - Custom document

**Formatting Methods**
- `addSection($title, $content)` - Add section
- `formatFileList($files, $groupBy)` - Format file list
- `formatChecklist($items, $checked)` - Format checklist
- `formatFileTree($files)` - Format tree structure
- `formatTable($headers, $rows)` - Format table

**File Management**
- `appendSection($filePath, $title, $content)` - Append to existing

---

## CONFIGURATION

**instructions_config.php** contains all options:

```php
[
    'format' => [
        'heading_style' => '#',
        'include_header' => true,
        'include_footer' => true
    ],
    'file_list' => [
        'group_by_default' => 'directory',
        'show_ref_ids' => true
    ],
    'checklist' => [
        'unchecked_marker' => '[ ]',
        'checked_marker' => '[x]'
    ]
]
```

---

## OUTPUT EXAMPLES

### Import Instructions

```markdown
# Import Instructions

**Version:** 1.0.0  
**Date:** 2025-11-27  
**Operation:** Import  
**Files:** 25

---

## OVERVIEW

Import package: **knowledge-import**  
Source version: **4.2**  
Target version: **4.3**  
Total files: **25**

---

## PREREQUISITES

- [ ] Backup current SIMA instance
- [ ] Verify SIMA version compatibility
- [ ] Ensure file write permissions
- [ ] Review manifest.yaml for conflicts

## FILE INVENTORY

**generic/lessons** (10 files)
  - LESS-01.md (`LESS-01`)
  - LESS-02.md (`LESS-02`)

**generic/decisions** (15 files)
  - DEC-01.md (`DEC-01`)
  - DEC-02.md (`DEC-02`)
```

---

## EXAMPLES

### Example 1: Import Instructions

```php
<?php
$instructions = new InstructionsModule();

$files = [
    [
        'filename' => 'LESS-01.md',
        'path' => 'generic/lessons/LESS-01.md',
        'ref_id' => 'LESS-01',
        'category' => 'lessons',
        'size' => 2048
    ]
];

$md = $instructions->generateImportInstructions($files, [
    'archive_name' => 'lessons-import',
    'source_version' => '4.2',
    'target_version' => '4.3'
]);

file_put_contents('import-instructions.md', $md);
```

### Example 2: Export Package

```php
<?php
$instructions = new InstructionsModule();

$md = $instructions->generateExportInstructions($files, [
    'archive_name' => 'lessons-export'
]);

file_put_contents('export-instructions.md', $md);
```

### Example 3: Custom Instructions

```php
<?php
$instructions = new InstructionsModule();

$sections = [
    'Overview' => 'This is a custom operation',
    'Steps' => "1. First step\n2. Second step",
    'Notes' => 'Important considerations'
];

$md = $instructions->generateCustom(
    'Custom Operation Instructions',
    $sections
);
```

### Example 4: File List Formatting

```php
<?php
// Group by directory
$byDir = $instructions->formatFileList($files, 'directory');

// Group by category
$byCat = $instructions->formatFileList($files, 'category');

// Group by domain
$byDomain = $instructions->formatFileList($files, 'domain');
```

### Example 5: Checklist

```php
<?php
$checklist = $instructions->formatChecklist([
    'Simple item',
    ['text' => 'With children', 'children' => [
        'Sub-item 1',
        'Sub-item 2'
    ]],
    'Another item'
]);

echo $checklist;
```

---

## FEATURES

### Current Features
- ✅ Import instructions generation
- ✅ Export instructions generation
- ✅ Update instructions generation
- ✅ Restore instructions generation
- ✅ Migration instructions generation
- ✅ Custom document generation
- ✅ File list formatting (multiple groupings)
- ✅ Checklist formatting
- ✅ File tree rendering
- ✅ Table formatting
- ✅ Warning/note formatting
- ✅ Code block formatting
- ✅ Configurable templates

### Supported Operations
- import - Import package instructions
- export - Export package documentation
- update - Update procedure documentation
- restore - Restore from backup instructions
- migrate - Version migration guide

---

## INTEGRATION

### With SIMA-manifest Module

```php
<?php
require_once 'modules/manifest/manifest_module.php';
require_once 'modules/instructions/instructions_module.php';

$manifest = new ManifestModule();
$instructions = new InstructionsModule();

// Generate manifest
$yaml = $manifest->generate('export', $files, [
    'archive_name' => 'export'
]);

// Generate instructions
$md = $instructions->generateExportInstructions($files, [
    'archive_name' => 'export'
]);

// Save both
file_put_contents('manifest.yaml', $yaml);
file_put_contents('export-instructions.md', $md);
```

### With Export Tool

```php
<?php
// Export tool uses this for all instruction generation
require_once 'modules/instructions/instructions_module.php';

$instructions = new InstructionsModule();

$md = $instructions->generateImportInstructions($files, [
    'archive_name' => $archiveName,
    'source_version' => $sourceVersion,
    'target_version' => $targetVersion
]);

file_put_contents($exportDir . '/import-instructions.md', $md);
```

---

## FILE LIMITS

**All files kept under 350 lines** to ensure:
- Full accessibility via project_knowledge_search
- No truncation by Anthropic
- Easy maintenance

---

## NOTES

- Internal files in `internal/` are private - use InstructionsModule API only
- Markdown format is compatible with all viewers
- Templates are customizable per operation type
- Supports nested checklists and grouped file lists
- Configurable for different documentation styles

---

**Version:** 1.0.0  
**Lines:** 339
