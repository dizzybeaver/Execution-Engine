# SIMA Validation Module

**Version:** 1.0.0  
**Date:** 2025-11-27

Universal validation and security module for SIMA operations.

---

## DIRECTORY STRUCTURE

```
modules/validation/
├── validation_module.php        # Public API
├── validation_config.php        # Configuration
├── README.md                    # This file
│
└── internal/                    # Private components
    ├── path_validator.php           # Path validation
    ├── security_validator.php       # Security checks
    ├── integrity_validator.php      # File integrity
    └── content_validator.php        # Content validation
```

---

## QUICK START

### 1. Path Validation

```php
<?php
require_once 'modules/validation/validation_module.php';

$validation = new ValidationModule();

// Validate path
$result = $validation->validatePath('/path/to/file.md', '/base/dir');

if (!$result['valid']) {
    print_r($result['errors']);
}

// Sanitize path
$safe = $validation->sanitizePath($userInput);
```

### 2. Security Checks

```php
<?php
// Prevent directory traversal
if (!$validation->preventTraversal($path, $baseDir)) {
    die('Directory traversal attempt detected');
}

// Check dangerous patterns
$check = $validation->checkDangerousPatterns($filePath);

if (!$check['safe']) {
    print_r($check['issues']);
}
```

### 3. File Integrity

```php
<?php
// Validate checksum
$result = $validation->validateIntegrity(
    '/path/to/file.md',
    'abc123def456',
    'md5'
);

if ($result['valid']) {
    echo "File integrity verified";
}
```

---

## API REFERENCE

### ValidationModule Class

**Constructor**
```php
new ValidationModule($config = null)
```

**Path Validation**
- `validatePath($path, $baseDir)` - Validate path
- `sanitizePath($path)` - Sanitize path
- `preventTraversal($path, $baseDir)` - Check traversal

**Security Validation**
- `checkDangerousPatterns($path)` - Check for dangerous content
- `validateExtension($filename, $allowedExtensions)` - Check extension
- `validateUpload($fileData)` - Validate file upload
- `checkPermission($filePath, $permission)` - Check permissions

**Integrity Validation**
- `validateIntegrity($filePath, $checksum, $algorithm)` - Verify checksum
- `calculateChecksum($filePath, $algorithm)` - Calculate checksum

**Content Validation**
- `validateRefId($refId)` - Validate REF-ID format
- `validateFileStructure($filePath)` - Check file structure
- `validateCrossReferences($files)` - Check cross-references
- `findDuplicates($files, $criteria)` - Find duplicate files

**Batch Operations**
- `validateBatch($files, $options)` - Validate multiple files
- `validateAll($filePath, $options)` - Complete validation

---

## CONFIGURATION

**validation_config.php** contains all options:

```php
[
    'path' => [
        'max_length' => 4096,
        'allow_absolute' => false
    ],
    'security' => [
        'check_dangerous_extensions' => true,
        'max_file_size' => 10485760
    ],
    'dangerous_extensions' => [
        'php', 'exe', 'sh', 'bat'
    ]
]
```

---

## VALIDATION TYPES

### Path Validation
- Length checking
- Character validation
- Absolute/relative path control
- Directory traversal prevention
- Filename sanitization

### Security Validation
- Extension blacklisting
- Pattern detection (XSS, code injection)
- File size limits
- Upload validation
- Permission checking

### Integrity Validation
- Checksum calculation (MD5, SHA256)
- File comparison
- Manifest verification
- Change detection

### Content Validation
- REF-ID format checking
- File structure validation
- Cross-reference validation
- Duplicate detection
- Encoding validation

---

## EXAMPLES

### Example 1: Comprehensive File Validation

```php
<?php
$validation = new ValidationModule();

$result = $validation->validateAll('/path/to/file.md', [
    'base_dir' => '/sima',
    'validate_path' => true,
    'validate_security' => true,
    'validate_structure' => true,
    'expected_checksum' => 'abc123...'
]);

if ($result['valid']) {
    echo "File is valid";
} else {
    echo "Errors:\n";
    print_r($result['errors']);
    
    if (!empty($result['warnings'])) {
        echo "\nWarnings:\n";
        print_r($result['warnings']);
    }
}
```

### Example 2: Batch Validation

```php
<?php
$validation = new ValidationModule();

$files = [
    ['path' => '/sima/generic/LESS-01.md'],
    ['path' => '/sima/generic/LESS-02.md'],
    ['path' => '/sima/generic/LESS-03.md']
];

$results = $validation->validateBatch($files, [
    'validate_structure' => true,
    'validate_security' => true
]);

echo "Valid: " . count($results['valid']);
echo "Invalid: " . count($results['invalid']);
```

### Example 3: Security Check

```php
<?php
$validation = new ValidationModule();

// Check uploaded file
if (isset($_FILES['upload'])) {
    $uploadResult = $validation->validateUpload($_FILES['upload']);
    
    if (!$uploadResult['valid']) {
        die('Upload failed: ' . implode(', ', $uploadResult['errors']));
    }
    
    // Additional security checks
    $path = $_FILES['upload']['tmp_name'];
    $dangerCheck = $validation->checkDangerousPatterns($path);
    
    if (!$dangerCheck['safe']) {
        die('Security issues: ' . implode(', ', $dangerCheck['issues']));
    }
    
    // Safe to process
    move_uploaded_file($path, '/safe/location/file.md');
}
```

### Example 4: Cross-Reference Validation

```php
<?php
$validation = new ValidationModule();

$files = [
    ['path' => '/sima/generic/LESS-01.md', 'ref_id' => 'LESS-01'],
    ['path' => '/sima/generic/LESS-02.md', 'ref_id' => 'LESS-02']
];

$result = $validation->validateCrossReferences($files);

if (!$result['valid']) {
    foreach ($result['errors'] as $error) {
        echo "Broken reference in {$error['file']}: {$error['broken_ref']}\n";
    }
}
```

### Example 5: Duplicate Detection

```php
<?php
$validation = new ValidationModule();

// Find duplicate filenames
$byFilename = $validation->findDuplicates($files, 'filename');

if ($byFilename['has_duplicates']) {
    foreach ($byFilename['duplicates'] as $name => $group) {
        echo "Duplicate filename: {$name}\n";
        foreach ($group as $file) {
            echo "  - {$file['path']}\n";
        }
    }
}

// Find duplicate REF-IDs
$byRefId = $validation->findDuplicates($files, 'refid');

// Find duplicate content (by checksum)
$byChecksum = $validation->findDuplicates($files, 'checksum');
```

---

## SECURITY FEATURES

### Directory Traversal Prevention
```php
// Blocks: ../, ..\, %2e%2e/, etc.
$safe = $validation->preventTraversal($userPath, $baseDir);
```

### Dangerous Extension Blocking
```php
// Blocks: .php, .exe, .sh, .bat, etc.
$allowed = $validation->validateExtension($filename);
```

### Code Injection Detection
```php
// Detects: <?php, <script>, eval(), etc.
$check = $validation->checkDangerousPatterns($path);
```

### Upload Validation
```php
// Validates: size, extension, MIME type, errors
$valid = $validation->validateUpload($_FILES['upload']);
```

---

## FEATURES

### Current Features
- ✅ Path validation and sanitization
- ✅ Directory traversal prevention
- ✅ Extension whitelist/blacklist
- ✅ Dangerous pattern detection
- ✅ File size limits
- ✅ Upload validation
- ✅ Checksum calculation (MD5, SHA256)
- ✅ Integrity verification
- ✅ REF-ID validation
- ✅ File structure checking
- ✅ Cross-reference validation
- ✅ Duplicate detection
- ✅ Batch validation
- ✅ Permission checking

---

## INTEGRATION

### With SIMA-file Module

```php
<?php
require_once 'modules/validation/validation_module.php';
require_once 'modules/file/file_module.php';

$validation = new ValidationModule();
$fileModule = new SIMAFileModule();

// Validate before archiving
$files = $fileModule->scanDirectory('/sima/generic');

$validated = $validation->validateBatch($files['files'], [
    'validate_structure' => true,
    'validate_security' => true
]);

$validFiles = $validated['valid'];
$fileModule->createArchive($validFiles, 'export.zip');
```

### With Export Tool

```php
<?php
// Export tool uses validation for security
require_once 'modules/validation/validation_module.php';

$validation = new ValidationModule();

// Validate base directory
$pathCheck = $validation->validatePath($basePath);

if (!$pathCheck['valid']) {
    die('Invalid base path');
}

// Prevent traversal
foreach ($selectedFiles as $file) {
    if (!$validation->preventTraversal($file, $basePath)) {
        die('Security violation detected');
    }
}

// Validate checksums
$integrity = $validation->validateBatch($selectedFiles, [
    'expected_checksum' => true
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

- Internal files in `internal/` are private - use ValidationModule API only
- Security checks are comprehensive but configurable
- Path validation prevents common attack vectors
- Integrity checking ensures file authenticity
- Batch operations handle large file sets efficiently

---

**Version:** 1.0.0  
**Lines:** 343
