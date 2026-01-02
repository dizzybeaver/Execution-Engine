<?php
/**
 * sima-export-archive.php
 * 
 * Archive Creation Functions
 * Version: 1.2.0
 * Date: 2025-11-27
 * UPDATED: Uses export-specific functions
 */

/**
 * Create complete export archive
 */
function _createExportArchive($validatedBase, $archiveName, $description, $selectedPaths, $sourceVersion, $targetVersion) {
    $selectedFiles = _buildSelectedFiles($validatedBase, $selectedPaths, $sourceVersion, $targetVersion);
    
    if (empty($selectedFiles)) {
        throw new Exception("No valid files to export");
    }
    
    $exportId = uniqid();
    $exportPath = EXPORT_DIR . '/' . $exportId;
    
    if (!is_dir($exportPath)) {
        mkdir($exportPath, 0755, true);
    }
    
    // Generate documentation
    _generateExportDocumentation($exportPath, $archiveName, $description, $selectedFiles, $sourceVersion, $targetVersion);
    
    // Create archives
    $finalZipPath = _createArchives($exportPath, $archiveName, $selectedFiles);
    
    // Generate download URL
    $downloadUrl = _generateDownloadUrl($exportId, $archiveName);
    
    return [
        'archive_path' => $finalZipPath,
        'archive_name' => $archiveName . '.zip',
        'file_count' => count($selectedFiles),
        'converted_count' => count(array_filter($selectedFiles, fn($f) => $f['converted'])),
        'source_version' => $sourceVersion,
        'target_version' => $targetVersion,
        'download_url' => $downloadUrl,
        'export_id' => $exportId
    ];
}

/**
 * Build selected files array with conversion
 */
function _buildSelectedFiles($validatedBase, $selectedPaths, $sourceVersion, $targetVersion) {
    $selectedFiles = [];
    
    foreach ($selectedPaths as $path) {
        $fileData = _processFileForExport($validatedBase, $path, $sourceVersion, $targetVersion);
        if ($fileData) {
            $selectedFiles[] = $fileData;
        }
    }
    
    return $selectedFiles;
}

/**
 * Process individual file for export
 */
function _processFileForExport($validatedBase, $path, $sourceVersion, $targetVersion) {
    $fullPath = $validatedBase . '/' . $path;
    
    if (!file_exists($fullPath)) {
        error_log("Warning: File not found: {$fullPath}");
        return null;
    }
    
    $content = file_get_contents($fullPath);
    $metadata = extractFileMetadata($fullPath);
    
    // Apply version conversion if needed
    return _applyVersionConversion($content, $path, $metadata, $sourceVersion, $targetVersion, $fullPath);
}

/**
 * Apply version conversion to file
 */
function _applyVersionConversion($content, $path, $metadata, $sourceVersion, $targetVersion, $fullPath) {
    $convertedPath = $path;
    $convertedFilename = basename($path);
    $wasConverted = false;
    
    if ($sourceVersion !== $targetVersion && SIMAVersionUtils::canConvert($sourceVersion, $targetVersion)) {
        $content = SIMAVersionUtils::convertMetadata($content, $sourceVersion, $targetVersion);
        $convertedPath = SIMAVersionUtils::convertPath($path, $sourceVersion, $targetVersion);
        $convertedFilename = SIMAVersionUtils::convertFilename(basename($path), $sourceVersion, $targetVersion);
        $wasConverted = true;
    }
    
    return [
        'path' => $fullPath,
        'relative_path' => $convertedPath,
        'original_path' => $path,
        'filename' => $convertedFilename,
        'ref_id' => $metadata['ref_id'],
        'category' => $metadata['category'] ?? basename(dirname($path)),
        'size' => strlen($content),
        'checksum' => md5($content),
        'content' => $content,
        'converted' => $wasConverted,
        'sima_version' => $targetVersion
    ];
}

/**
 * Generate export documentation
 */
function _generateExportDocumentation($exportPath, $archiveName, $description, $selectedFiles, $sourceVersion, $targetVersion) {
    // Use export-specific manifest function
    $manifestContent = generateExportManifest($archiveName, $description, $selectedFiles, $sourceVersion, $targetVersion);
    file_put_contents($exportPath . '/manifest.yaml', $manifestContent);
    
    // Use export-specific instructions function
    $instructionsContent = generateExportInstructions($archiveName, $selectedFiles, $sourceVersion, $targetVersion);
    file_put_contents($exportPath . '/import-instructions.md', $instructionsContent);
}

/**
 * Create ZIP archives
 */
function _createArchives($exportPath, $archiveName, $selectedFiles) {
    // Create knowledge base ZIP
    $zipPath = $exportPath . '/knowledge-base.zip';
    $zip = new ZipArchive();
    
    if ($zip->open($zipPath, ZipArchive::CREATE) !== true) {
        throw new Exception("Could not create ZIP file");
    }
    
    foreach ($selectedFiles as $file) {
        $zip->addFromString($file['relative_path'], $file['content']);
    }
    
    $zip->close();
    
    // Create final archive
    $finalZipPath = $exportPath . '/' . $archiveName . '.zip';
    $finalZip = new ZipArchive();
    
    if ($finalZip->open($finalZipPath, ZipArchive::CREATE) !== true) {
        throw new Exception("Could not create final archive");
    }
    
    $finalZip->addFile($exportPath . '/manifest.yaml', 'manifest.yaml');
    $finalZip->addFile($exportPath . '/import-instructions.md', 'import-instructions.md');
    $finalZip->addFile($zipPath, 'knowledge-base.zip');
    $finalZip->close();
    
    return $finalZipPath;
}

/**
 * Generate download URL
 */
function _generateDownloadUrl($exportId, $archiveName) {
    $scriptUrl = $_SERVER['REQUEST_SCHEME'] . '://' . $_SERVER['HTTP_HOST'] . dirname($_SERVER['REQUEST_URI']);
    return $scriptUrl . '/../../exports/' . $exportId . '/' . $archiveName . '.zip';
}
?>
