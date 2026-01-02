# SIMA Export Tool - Extractable Generic Modules

**Version:** 1.0.0  
**Date:** 2025-11-27  
**Purpose:** Identify reusable functionality for extraction

---

## EXTRACTED MODULES (Completed)

### 1. SIMA-tree Module ✅
**Files:** tree_module.php, tree_scanner.php, tree_formatter.php, tree_version.php  
**Purpose:** Directory scanning, tree formatting, version detection  
**Reusable for:** Import, Update, File Management tools

### 2. SIMA-file Module ✅
**Files:** file_module.php, file-scanner.php, file-archiver.php, file-extractor.php  
**Purpose:** File operations, archiving, extraction, validation  
**Reusable for:** Import, Update, Backup, Migration tools

---

## EXTRACTABLE MODULES (New)

### 3. SIMA-manifest Module
**Current Files:**
- sima-export-manifest.php
- sima-common.php (generateManifest function)

**Generic Functionality:**
- Generate operation manifests (export/import/update)
- File inventory tracking
- Domain/category counting
- Checksum recording
- YAML generation from arrays
- Metadata compilation

**Reusable for:**
- Import tool manifests
- Update tool change tracking
- Backup system metadata
- Migration documentation
- Audit trail generation

**Interface:**
```php
ManifestModule::generate($operation, $files, $metadata)
ManifestModule::validate($manifestPath)
ManifestModule::parse($manifestPath)
ManifestModule::merge($manifest1, $manifest2)
```

---

### 4. SIMA-instructions Module
**Current Files:**
- sima-export-instructions.php

**Generic Functionality:**
- Generate operation instructions (import/update/restore)
- File grouping by directory/category
- Installation state documentation
- Process guide generation
- Markdown formatting for guides

**Reusable for:**
- Import process documentation
- Update instructions
- Migration guides
- Installation documentation
- Recovery procedures

**Interface:**
```php
InstructionsModule::generate($operation, $files, $options)
InstructionsModule::addSection($title, $content)
InstructionsModule::formatFileList($files, $groupBy)
InstructionsModule::formatChecklist($items)
```

---

### 5. SIMA-version Module
**Current Files:**
- sima-version-utils.php
- Parts of sima-common.php (version tagging)

**Generic Functionality:**
- Version detection from file structure
- Version conversion/migration
- Version compatibility checking
- Version tag injection
- Multi-version support (v4.1, v4.2, v4.3)

**Reusable for:**
- Import version validation
- Update compatibility checking
- Migration version tracking
- Backward compatibility
- Version-specific processing

**Interface:**
```php
VersionModule::detect($basePath)
VersionModule::convert($content, $fromVersion, $toVersion)
VersionModule::canConvert($fromVersion, $toVersion)
VersionModule::addVersionTags($content, $version)
VersionModule::getVersionInfo($version)
```

---

### 6. SIMA-validation Module
**Current Files:**
- Scattered validation in sima-export-handler.php
- Path validation logic
- Security checks

**Generic Functionality:**
- Path validation and sanitization
- Security checks (directory traversal prevention)
- File integrity verification
- REF-ID validation
- Cross-reference validation
- Duplicate detection

**Reusable for:**
- Import validation
- Update validation
- File upload security
- Data integrity checking
- Structure validation

**Interface:**
```php
ValidationModule::validatePath($path, $baseDir)
ValidationModule::sanitizePath($path)
ValidationModule::preventTraversal($path)
ValidationModule::validateRefId($refId)
ValidationModule::checkIntegrity($files)
ValidationModule::findDuplicates($files)
```

---

### 7. SIMA-packaging Module
**Current Files:**
- Parts of sima-export-archive.php
- Archive creation logic

**Generic Functionality:**
- Multi-file packaging
- Directory structure preservation
- Manifest/documentation inclusion
- Package naming conventions
- Archive metadata embedding

**Reusable for:**
- Import package creation
- Backup packaging
- Migration bundles
- Distribution packages
- Update packages

**Interface:**
```php
PackagingModule::create($files, $packageName)
PackagingModule::addManifest($manifest)
PackagingModule::addInstructions($instructions)
PackagingModule::setStructure($structure)
PackagingModule::finalize()
```

---

### 8. SIMA-ajax Module
**Current Files:**
- sima-export-handler.php (request handling)
- Response formatting logic

**Generic Functionality:**
- AJAX request handling
- JSON response formatting
- Error response standardization
- Request validation
- Action routing
- Session management

**Reusable for:**
- Import tool AJAX
- Update tool AJAX
- Any web-based SIMA tool
- API endpoints
- Interactive interfaces

**Interface:**
```php
AjaxModule::handleRequest($allowedActions)
AjaxModule::sendSuccess($data)
AjaxModule::sendError($message, $code)
AjaxModule::validateAction($action, $allowed)
AjaxModule::parseRequest()
```

---

### 9. SIMA-ui Module
**Current Files:**
- HTML generation in sima-export-handler.php
- CSS loading logic
- JS loading logic

**Generic Functionality:**
- Standard UI component generation
- Asset path management
- Form generation
- Status message formatting
- Loading indicator generation
- Common layouts

**Reusable for:**
- Import tool UI
- Update tool UI
- Any SIMA web tool
- Configuration interfaces
- Management dashboards

**Interface:**
```php
UIModule::generateHeader($title)
UIModule::generateForm($fields)
UIModule::generateStatusArea()
UIModule::getAssetIncludes($css, $js)
UIModule::generateButton($label, $action)
```

---

### 10. SIMA-conversion Module
**Current Files:**
- Version conversion logic in sima-version-utils.php
- Content transformation

**Generic Functionality:**
- Content format conversion
- Metadata transformation
- Path conversion between versions
- Filename conversion
- Batch conversion processing

**Reusable for:**
- Import format normalization
- Update migrations
- Legacy data conversion
- Multi-version support
- Format standardization

**Interface:**
```php
ConversionModule::convertContent($content, $from, $to)
ConversionModule::convertMetadata($metadata, $from, $to)
ConversionModule::batchConvert($files, $from, $to)
ConversionModule::registerConverter($from, $to, $callback)
```

---

## PRIORITY EXTRACTION SEQUENCE

### Phase 1: High Priority (Immediate Reuse)
1. **SIMA-manifest** - Needed for Import and Update
2. **SIMA-validation** - Critical for security across all tools
3. **SIMA-version** - Required for Import compatibility

### Phase 2: Medium Priority (Near-term Reuse)
4. **SIMA-instructions** - Useful for Import and Update
5. **SIMA-packaging** - Needed for Import, Backup
6. **SIMA-ajax** - Required for web-based tools

### Phase 3: Lower Priority (Enhancement)
7. **SIMA-conversion** - Useful but less urgent
8. **SIMA-ui** - Nice to have, can use inline initially
9. Extract remaining utilities as patterns emerge

---

## EXTRACTION BENEFITS

### Code Reuse
- Import tool: Use 6-8 modules
- Update tool: Use 5-7 modules
- Backup tool: Use 4-6 modules

### Maintenance
- Fix once, benefits all tools
- Consistent behavior
- Easier testing
- Clear dependencies

### Development Speed
- Build new tools faster
- Known interfaces
- Proven functionality
- Less duplication

---

## MODULE DEPENDENCIES

```
SIMA-manifest
  ↓ uses
SIMA-validation, SIMA-version

SIMA-packaging
  ↓ uses
SIMA-manifest, SIMA-instructions, SIMA-file

SIMA-ajax
  ↓ uses
SIMA-validation

SIMA-version
  ↓ uses
SIMA-conversion, SIMA-validation

SIMA-ui
  ↓ uses
SIMA-ajax (for includes)
```

---

## NOTES

- Each module should be ≤350 lines per file
- All modules follow same pattern as SIMA-tree and SIMA-file
- Include README.md for each module
- Include config file for each module
- Public API wrapper + internal components
- Standalone operation with minimal dependencies

---

**END OF ANALYSIS**

**Extractable Modules:** 8 new (10 total with tree/file)  
**Priority:** 3 phases  
**Estimated Effort:** ~40 hours for all phases
