<?php
/**
 * sima-export-instructions.php
 * 
 * Export-Specific Instructions Generation
 * Version: 1.0.0
 * Date: 2025-11-27
 */

/**
 * Generate export-specific import instructions
 */
function generateExportInstructions($archiveName, $selectedFiles, $sourceVersion, $targetVersion) {
    return generateImportInstructions(
        'export',
        $archiveName, 
        $selectedFiles, 
        $sourceVersion, 
        $targetVersion
    );
}

/**
 * Group files by directory (export-specific helper)
 */
function _groupFilesByDirectory($selectedFiles) {
    $grouped = [];
    foreach ($selectedFiles as $file) {
        $dir = dirname($file['relative_path']);
        if (!isset($grouped[$dir])) {
            $grouped[$dir] = [];
        }
        $grouped[$dir][] = $file;
    }
    return $grouped;
}
?>
