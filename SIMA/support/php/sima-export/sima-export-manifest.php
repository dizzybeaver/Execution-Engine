<?php
/**
 * sima-export-manifest.php
 * 
 * Export-Specific Manifest Generation
 * Version: 1.0.0
 * Date: 2025-11-27
 */

/**
 * Generate export-specific manifest.yaml
 */
function generateExportManifest($archiveName, $description, $selectedFiles, $sourceVersion, $targetVersion) {
    return generateManifest(
        'export', 
        $archiveName, 
        $description, 
        $selectedFiles, 
        $sourceVersion, 
        $targetVersion
    );
}
?>
