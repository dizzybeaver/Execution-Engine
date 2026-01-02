<?php
/**
 * sima-export-helpers.php
 * 
 * Wrapper for Export Helper Functions
 * Version: 2.0.0
 * Date: 2025-11-27
 * 
 * REFACTORED: Split into modular files
 * FIXED: No duplicate function conflicts
 */

// Load modular components
require_once __DIR__ . '/sima-export-archive.php';
require_once __DIR__ . '/sima-export-manifest.php';
require_once __DIR__ . '/sima-export-instructions.php';

/**
 * Create complete export archive (main entry point)
 */
function createExportArchive($validatedBase, $archiveName, $description, $selectedPaths, $sourceVersion, $targetVersion) {
    return _createExportArchive($validatedBase, $archiveName, $description, $selectedPaths, $sourceVersion, $targetVersion);
}
?>
