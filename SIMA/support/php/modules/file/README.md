# SIMA File Module

**Version:** 1.0.0  
**Date:** 2025-11-27  
**Purpose:** Universal file handling and archiving library for PHP web applications

---

## OVERVIEW

SIMA File Module provides comprehensive file system operations, archiving, extraction, and metadata management for PHP-based web applications. Designed as a universal, reusable library for import/export tools and file management systems.

---

## FEATURES

### File Scanning
- Recursive directory scanning
- Filtered scanning by extension, size, date
- Metadata extraction (version, REF-ID, title)
- Automatic checksum calculation
- Directory statistics and breakdowns

### Archive Operations
- Create ZIP archives from file lists
- Add files to existing archives
- List archive contents
- Configurable compression levels
- Automatic manifest generation
- Archive splitting for size limits

### Extraction Operations
- Extract entire archives
- Extract specific files only
- Preview archive contents without extraction
- Integrity verification (CRC checks)
- Preserve timestamps and permissions
- Overwrite protection

### Metadata Management
- Extract file metadata (size, modified, checksums)
- Content-specific metadata (versions, REF-IDs, titles)
- Generate comprehensive manifests
- Compare file metadata
- Group files by directory or extension

### Validation & Security
- Path validation and sanitization
- Directory traversal prevention
- File integrity verification
- Permission checking
- Dangerous extension filtering
- Archive integrity verification

### File Operations
- Copy files with structure preservation
- Move files with structure preservation
- Delete files with confirmation
- Batch operations
- Automatic directory creation
- Temporary file cleanup

---

## INSTALLATION

### Directory Structure

```
/modules/
└── file/
    ├── file_module.php          # Public API wrapper
    ├── file-config.php          # Configuration
    ├── file-scanner.php         # Scanning operations
    ├── file-archiver.php        # Archive creation
    ├── file-extractor.php       # Archive extraction
    ├── file-validator.php       # Validation
    ├── file-metadata.php        # Metadata extraction
    ├── file-utils.php           # Utility functions
    └── file-README.md           # This file
```

### Requirements

- PHP 7.4 or higher
- ZipArchive extension enabled
- File system write permissions

---

## CONFIGURATION

### Basic Configuration

```php
<?php
require_once '/path/to/modules/file/file_module.php';

// Override default configuration
FileConfig::setConfig([
    'base_directory' => '/var/www/sima',
    'export_directory' => '/var/www/sima/exports',
    'compression_level' => 6,
    'calculate_checksums' => true
]);

// Create module instance
$fileModule = new SIMAFileModule();
```

### Configuration Options

**Base Paths:**
- `base_directory` - Root directory for operations
- `export_directory` - Export/temporary directory
- `upload_directory` - Upload directory
- `archive_directory` - Archive storage directory

**Scanning:**
- `include_extensions` - File extensions to include
- `exclude_extensions` - File extensions to exclude
- `exclude_directories` - Directories to skip
- `max_scan_depth` - Maximum recursion depth (0 = unlimited)
- `follow_symlinks` - Follow symbolic links (true/false)

**Archives:**
- `compression_level` - ZIP compression (0-9)
- `archive_format` - Format: 'zip', 'tar', 'tar.gz'
- `timestamp_archives` - Add timestamp to names (true/false)
- `max_archive_size` - Maximum size in bytes (0 = unlimited)
- `split_archives` - Split large archives (true/false)

**Extraction:**
- `overwrite_on_extract` - Overwrite existing files (true/false)
- `preserve_permissions` - Preserve file permissions (true/false)
- `preserve_timestamps` - Preserve timestamps (true/false)
- `verify_after_extract` - Verify checksums (true/false)

**Metadata:**
- `extract_versions` - Extract version strings (true/false)
- `extract_ref_ids` - Extract REF-IDs (true/false)
- `checksum_algorithm` - Hash algorithm ('sha256', 'md5', etc.)
- `store_file_sizes` - Include file sizes (true/false)

**Security:**
- `validate_paths` - Validate against base directory (true/false)
- `prevent_traversal` - Block directory traversal (true/false)
- `sanitize_filenames` - Clean filenames (true/false)
- `dangerous_extensions` - Blacklisted extensions

---

## USAGE EXAMPLES

### Scanning Directory

```php
$fileModule = new SIMAFileModule();

// Basic scan
$result = $fileModule->scanDirectory('/var/www/sima/generic');

// Filtered scan
$result = $fileModule->scanWithFilter('/var/www/sima', [
    'extensions' => ['md', 'php'],
    'min_size' => 1024,
    'modified_after' => strtotime('-7 days')
]);

// Get statistics
$stats = $fileModule->getDirectoryStats('/var/www/sima');
```

### Creating Archives

```php
$files = [
    '/var/www/sima/generic/LESS-01.md',
    '/var/www/sima/generic/LESS-02.md',
    '/var/www/sima/generic/DEC-01.md'
];

$result = $fileModule->createArchive(
    $files,
    'knowledge_export.zip',
    ['include_manifest' => true]
);

if ($result['success']) {
    echo "Archive created: " . $result['archive_path'];
    echo "Files added: " . $result['files_added'];
}
```

### Extracting Archives

```php
// Extract entire archive
$result = $fileModule->extractArchive(
    '/var/www/sima/exports/knowledge_export.zip',
    '/var/www/sima/imports',
    ['overwrite' => false]
);

// Extract specific files
$result = $fileModule->extractFiles(
    '/var/www/sima/exports/knowledge_export.zip',
    ['LESS-01.md', 'LESS-02.md'],
    '/var/www/sima/imports'
);

// Preview without extracting
$preview = $fileModule->previewArchive(
    '/var/www/sima/exports/knowledge_export.zip'
);
```

### Metadata Operations

```php
// Get file metadata
$metadata = $fileModule->getFileMetadata('/var/www/sima/generic/LESS-01.md');

// Generate checksums
$checksums = $fileModule->getChecksums($files, 'sha256');

// Create manifest
$manifest = $fileModule->generateManifest($files, [
    'include_checksums' => true,
    'group_by_directory' => true
]);
```

### File Operations

```php
// Copy files
$result = $fileModule->copyFiles($files, '/destination', [
    'preserve_structure' => true,
    'overwrite' => false
]);

// Move files
$result = $fileModule->moveFiles($files, '/destination');

// Delete files (requires confirmation)
$result = $fileModule->deleteFiles($files, ['confirm' => true]);
```

### Validation

```php
// Validate file integrity
$valid = $fileModule->validateIntegrity(
    '/path/to/file.md',
    'expected_checksum_here'
);

// Verify archive
$result = $fileModule->verifyArchive('/path/to/archive.zip');

if ($result['valid']) {
    echo "Archive is valid";
} else {
    print_r($result['errors']);
}
```

---

## WEB APPLICATION INTEGRATION

### Example: Export Tool

```php
<?php
require_once 'modules/file/file_module.php';

// Configure
FileConfig::setConfig([
    'base_directory' => '/var/www/sima',
    'export_directory' => '/var/www/sima/exports'
]);

$fileModule = new SIMAFileModule();

// Handle AJAX request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    
    if ($action === 'scan') {
        $directory = $_POST['directory'] ?? '';
        $result = $fileModule->scanDirectory($directory);
        header('Content-Type: application/json');
        echo json_encode($result);
        exit;
    }
    
    if ($action === 'export') {
        $files = json_decode($_POST['files'] ?? '[]', true);
        $archiveName = $_POST['archive_name'] ?? 'export.zip';
        
        $result = $fileModule->createArchive($files, $archiveName);
        header('Content-Type: application/json');
        echo json_encode($result);
        exit;
    }
}
?>
```

### Example: Import Tool

```php
<?php
require_once 'modules/file/file_module.php';

$fileModule = new SIMAFileModule();

// Handle upload
if ($_FILES['archive']['error'] === UPLOAD_ERR_OK) {
    $uploadPath = '/var/www/sima/uploads/' . basename($_FILES['archive']['name']);
    move_uploaded_file($_FILES['archive']['tmp_name'], $uploadPath);
    
    // Preview contents
    $preview = $fileModule->previewArchive($uploadPath);
    
    // Extract
    if (isset($_POST['extract'])) {
        $result = $fileModule->extractArchive(
            $uploadPath,
            '/var/www/sima/imports',
            ['verify_integrity' => true]
        );
        
        if ($result['success']) {
            echo "Extracted: " . $result['extracted'] . " files";
        }
    }
}
?>
```

---

## ERROR HANDLING

All methods return arrays with consistent structure:

**Success Response:**
```php
[
    'success' => true,
    'data' => [...],
    // Additional result data
]
```

**Error Response:**
```php
[
    'error' => 'Error message here'
]
```

**Check for Errors:**
```php
$result = $fileModule->scanDirectory('/path');

if (isset($result['error'])) {
    echo "Error: " . $result['error'];
} else {
    // Process result
}
```

---

## PERFORMANCE CONSIDERATIONS

### Large File Operations

- Use `max_batch_size` to limit concurrent operations
- Enable `split_archives` for large exports
- Disable `calculate_checksums` if not needed
- Use filtered scanning instead of full scans

### Memory Management

- Configure `memory_limit` in settings
- Process large archives in chunks
- Use `preview()` before full extraction
- Clean temporary files regularly

### Optimization Tips

```php
// Fast scan without metadata
$result = $fileModule->scanDirectory($dir, [
    'include_metadata' => false,
    'calculate_checksums' => false
]);

// Efficient filtering
$result = $fileModule->scanWithFilter($dir, [
    'extensions' => ['md'],  // Limit scope
    'max_size' => 1048576    // Skip large files
]);
```

---

## SECURITY BEST PRACTICES

1. **Validate Input:**
   ```php
   FileConfig::setConfig(['validate_paths' => true]);
   ```

2. **Prevent Traversal:**
   ```php
   FileConfig::setConfig(['prevent_traversal' => true]);
   ```

3. **Sanitize Names:**
   ```php
   FileConfig::setConfig(['sanitize_filenames' => true]);
   ```

4. **Blacklist Extensions:**
   ```php
   FileConfig::setConfig([
       'dangerous_extensions' => ['.exe', '.sh', '.bat']
   ]);
   ```

5. **Check Permissions:**
   ```php
   FileConfig::setConfig(['check_permissions' => true]);
   ```

---

## ADVANCED FEATURES

### Custom Filters

```php
$result = $fileModule->scanWithFilter($directory, [
    'pattern' => '/^LESS-\d+\.md$/',  // Regex pattern
    'modified_after' => strtotime('-30 days'),
    'min_size' => 1024,
    'max_size' => 1048576,
    'version' => '1.0.0'  // Specific version
]);
```

### Manifest Generation

```php
$manifest = $fileModule->generateManifest($files, [
    'include_checksums' => true,
    'include_metadata' => true,
    'group_by_directory' => true,
    'format' => 'yaml'
]);

// Save manifest
file_put_contents('manifest.yaml', 
    FileUtils::arrayToYaml($manifest));
```

### Integrity Verification

```php
// Verify single file
$valid = $fileModule->validateIntegrity(
    '/path/to/file.md',
    'abc123...'  // Expected checksum
);

// Verify entire archive
$result = $fileModule->verifyArchive('/path/to/archive.zip');

if (!$result['valid']) {
    foreach ($result['errors'] as $error) {
        echo "Corrupted: " . $error['file'] . "\n";
    }
}
```

---

## TROUBLESHOOTING

### Common Issues

**Problem:** "Directory not writable"
```php
// Solution: Check permissions
chmod 0755 /var/www/sima/exports
```

**Problem:** "Archive too large"
```php
// Solution: Enable splitting
FileConfig::setConfig([
    'split_archives' => true,
    'split_size' => 104857600  // 100MB
]);
```

**Problem:** "Memory limit exceeded"
```php
// Solution: Increase PHP memory
ini_set('memory_limit', '256M');

// Or reduce batch size
FileConfig::setConfig(['max_batch_size' => 500]);
```

**Problem:** "Path validation failed"
```php
// Solution: Set correct base directory
FileConfig::setConfig(['base_directory' => '/correct/path']);
```

---

## EXTENDING THE MODULE

### Custom Validation

```php
class CustomValidator extends FileValidator {
    public function customCheck($filePath) {
        // Add custom validation logic
        return true;
    }
}
```

### Custom Metadata Extraction

```php
class CustomMetadata extends FileMetadata {
    protected function extractContentMetadata($filePath) {
        $metadata = parent::extractContentMetadata($filePath);
        
        // Add custom metadata extraction
        $metadata['custom_field'] = $this->extractCustomField($filePath);
        
        return $metadata;
    }
}
```

---

## API REFERENCE

See individual PHP files for complete method documentation:

- `file_module.php` - Main API wrapper
- `file-scanner.php` - Scanning operations
- `file-archiver.php` - Archive creation
- `file-extractor.php` - Extraction operations
- `file-validator.php` - Validation methods
- `file-metadata.php` - Metadata extraction
- `file-utils.php` - Utility functions

---

## VERSION HISTORY

**1.0.0** (2025-11-27)
- Initial release
- Core scanning functionality
- Archive creation and extraction
- Metadata extraction
- Validation and security features
- File operations (copy, move, delete)

---

## LICENSE

Part of SIMA (Structured Intelligence Memory Architecture)  
For project-specific use

---

## SUPPORT

For issues or questions, refer to SIMA project documentation.

---

**END OF README**

**Module:** SIMA File Module  
**Version:** 1.0.0  
**Files:** 7 PHP files + README  
**Lines:** ~2100 total (all files ≤350 lines)
