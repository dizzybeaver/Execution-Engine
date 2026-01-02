# SIMA Version Module

**Version:** 1.0.0  
**Date:** 2025-11-27

Universal version detection, conversion, and compatibility module for SIMA.

---

## DIRECTORY STRUCTURE

```
modules/version/
├── version_module.php           # Public API
├── version_config.php           # Configuration
├── README.md                    # This file
│
└── internal/                    # Private components
    ├── version_detector.php         # Version detection
    ├── version_converter.php        # Version conversion
    └── version_compatibility.php    # Compatibility checking
```

---

## QUICK START

### 1. Detect Version

```php
<?php
require_once 'modules/version/version_module.php';

$version = new VersionModule();

// Detect from directory
$result = $version->detect('/path/to/sima');

echo "Version: " . $result['version'];
echo "Confidence: " . ($result['confidence'] * 100) . "%";
```

### 2. Convert Between Versions

```php
<?php
// Convert content
$converted = $version->convert($content, '4.2', '4.3');

// Convert file
$result = $version->convertFile('/path/to/file.md', '4.3');

if ($result['success']) {
    file_put_contents('/path/to/file.md', $result['content']);
}
```

### 3. Check Compatibility

```php
<?php
// Check if conversion possible
if ($version->canConvert('4.2', '4.3')) {
    echo "Conversion supported";
}

// Check compatibility
$compat = $version->checkCompatibility('4.2', '4.3');
echo "Type: " . $compat['type'];
```

---

## API REFERENCE

### VersionModule Class

**Constructor**
```php
new VersionModule($config = null)
```

**Detection Methods**
- `detect($basePath)` - Detect version from directory
- `detectFromFile($filePath)` - Detect version from file
- `getVersionInfo($version)` - Get version details
- `extractVersion($content)` - Extract version from content

**Conversion Methods**
- `convert($content, $fromVersion, $toVersion)` - Convert content
- `convertFile($filePath, $toVersion)` - Convert file
- `batchConvert($files, $toVersion)` - Batch convert files
- `addVersionTags($content, $version, $metadata)` - Add version tags
- `removeVersionTags($content)` - Remove version tags

**Compatibility Methods**
- `canConvert($fromVersion, $toVersion)` - Check if convertible
- `checkCompatibility($version1, $version2)` - Check compatibility
- `compare($version1, $version2)` - Compare versions
- `isValidVersion($version)` - Validate version string
- `getConversionPath($fromVersion, $toVersion)` - Get conversion steps

**Utility Methods**
- `getSupportedVersions()` - Get supported versions
- `getLatestVersion()` - Get latest version
- `registerConverter($from, $to, $callback)` - Register custom converter

---

## CONFIGURATION

**version_config.php** contains all options:

```php
[
    'supported_versions' => ['3.0', '4.1', '4.2', '4.3'],
    'detection' => [
        'methods' => ['structure', 'file_header', 'metadata'],
        'confidence_threshold' => 0.7
    ],
    'conversion' => [
        'enabled' => true,
        'validate_after' => true
    ]
]
```

---

## SUPPORTED VERSIONS

### Version 3.0
- **Status:** Deprecated
- **Features:** Basic structure, Single domain
- **Converts to:** 4.1, 4.2, 4.3

### Version 4.1
- **Status:** Legacy
- **Features:** Multi-domain, REF-IDs
- **Converts to:** 4.2, 4.3

### Version 4.2
- **Status:** Stable
- **Features:** Language support, Enhanced navigation
- **Converts to:** 4.3

### Version 4.3
- **Status:** Current
- **Features:** Documentation integration, Enhanced indexes
- **Backward compatible:** 4.2, 4.1

---

## EXAMPLES

### Example 1: Auto-Detect and Convert

```php
<?php
$version = new VersionModule();

// Detect current version
$detection = $version->detect('/path/to/sima');
$currentVersion = $detection['version'];

echo "Current version: {$currentVersion}";

// Get latest version
$latestVersion = $version->getLatestVersion();

// Convert if needed
if ($currentVersion !== $latestVersion) {
    if ($version->canConvert($currentVersion, $latestVersion)) {
        echo "Converting to {$latestVersion}...";
        
        // Get all files
        $files = glob('/path/to/sima/**/*.md');
        
        // Batch convert
        $results = $version->batchConvert($files, $latestVersion);
        
        echo "Success: " . count($results['success']);
        echo "Failed: " . count($results['failed']);
    }
}
```

### Example 2: Single File Conversion

```php
<?php
$version = new VersionModule();

// Convert single file
$result = $version->convertFile(
    '/path/to/LESS-01.md',
    '4.3'
);

if ($result['success']) {
    file_put_contents(
        '/path/to/LESS-01.md',
        $result['content']
    );
    
    echo "Converted from {$result['from_version']} to {$result['to_version']}";
}
```

### Example 3: Check Compatibility

```php
<?php
$version = new VersionModule();

// Check if versions compatible
$compat = $version->checkCompatibility('4.2', '4.3');

if ($compat['compatible']) {
    echo "Type: {$compat['type']}";
    
    // Get conversion path
    $path = $version->getConversionPath('4.2', '4.3');
    echo "Steps: " . implode(' → ', $path['steps']);
}
```

### Example 4: Add Version Tags

```php
<?php
$version = new VersionModule();

// Add export tags
$content = file_get_contents('LESS-01.md');

$tagged = $version->addVersionTags($content, '4.3', [
    'package_name' => 'lessons-export',
    'export_date' => '2025-11-27'
]);

file_put_contents('LESS-01.md', $tagged);
```

### Example 5: Custom Converter

```php
<?php
$version = new VersionModule();

// Register custom converter
$version->registerConverter('4.2', '4.3', function($content) {
    // Custom conversion logic
    $content = str_replace('old_pattern', 'new_pattern', $content);
    return $content;
});

// Use custom converter
$converted = $version->convert($content, '4.2', '4.3');
```

---

## DETECTION METHODS

### Structure Detection
Checks directory structure and files:
- Required directories (generic, platforms, etc.)
- Required files (Master-Index-of-Indexes.md, etc.)
- Optional files

### File Header Detection
Examines file headers for version markers:
- `**Version:** X.Y`
- `**SIMA Version:** X.Y`
- `**Exported:** ... (vX.Y)`

### Metadata Detection
Analyzes metadata fields present:
- v3.0: Version, Date, Category
- v4.1: Version, Date, Purpose, Category
- v4.2: Version, Date, Purpose, Type, REF-ID
- v4.3: Version, Date, Purpose, Type, REF-ID, Keywords

---

## CONVERSION PROCESS

### Header Conversion
```
v4.2 → v4.3

FROM:
# LESS-01.md
**Version:** 1.0.0
**Date:** 2025-11-27
**Purpose:** Lesson learned
**Type:** Lessons
**REF-ID:** LESS-01

TO:
# LESS-01.md
**Version:** 1.0.0
**Date:** 2025-11-27
**Purpose:** Lesson learned
**Type:** Lessons
**REF-ID:** LESS-01
**Keywords:** 
```

### Path Conversion
Updates internal path references:
- `knowledge/` → `generic/` (v3.0 to v4.1)
- Maintains consistency across versions

### Metadata Updates
Adds missing fields for target version while preserving existing data.

---

## FEATURES

### Current Features
- ✅ Auto version detection (3 methods)
- ✅ Multi-version support (3.0, 4.1, 4.2, 4.3)
- ✅ Content conversion
- ✅ File conversion
- ✅ Batch conversion
- ✅ Compatibility checking
- ✅ Version comparison
- ✅ Conversion path finding
- ✅ Version tagging
- ✅ Custom converters
- ✅ Upgrade recommendations

---

## INTEGRATION

### With SIMA-manifest Module

```php
<?php
require_once 'modules/version/version_module.php';
require_once 'modules/manifest/manifest_module.php';

$version = new VersionModule();
$manifest = new ManifestModule();

// Detect version
$versionInfo = $version->detect('/sima');

// Generate manifest with version
$yaml = $manifest->generate('export', $files, [
    'source_version' => $versionInfo['version'],
    'target_version' => $version->getLatestVersion()
]);
```

### With Export Tool

```php
<?php
// Export tool uses version module for all conversions
require_once 'modules/version/version_module.php';

$version = new VersionModule();

// Detect source version
$sourceVersion = $version->detect($basePath)['version'];

// Convert files if needed
if ($version->canConvert($sourceVersion, $targetVersion)) {
    $results = $version->batchConvert($files, $targetVersion);
}
```

---

## FILE LIMITS

**All files kept under 350 lines** to ensure:
- Full accessibility via project_knowledge_search
- No truncation by Anthropic
- Easy maintenance

---

## NOTES

- Internal files in `internal/` are private - use VersionModule API only
- Detection uses multiple methods for accuracy
- Conversion preserves all content
- Custom converters override built-in conversion
- Version tags can be added/removed as needed

---

**Version:** 1.0.0  
**Lines:** 347
