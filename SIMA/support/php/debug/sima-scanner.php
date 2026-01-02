<?php
/**
 * sima-scanner.php
 * 
 * Comprehensive SIMA Directory Scanner
 * Version: 4.0.0
 * Date: 2025-11-22
 * Location: /sima/support/php/
 * 
 * COMPLETE REWRITE: Full recursive scanning
 * - Scans ALL directories (not just spec-defined)
 * - Finds ALL .md files recursively
 * - Includes context/, docs/, support/, templates/
 * - Maintains version detection for conversion
 * - No spec-based filtering
 * 
 * CRITICAL: Stays under 350 lines
 */

class SIMAScanner {
    
    /**
     * Comprehensive recursive scan
     * Returns complete directory tree with ALL .md files
     * 
     * @param string $basePath Root SIMA directory
     * @param array $options Scan options
     * @return array Complete directory tree
     */
    public static function scanComplete($basePath, $options = []) {
        $defaults = [
            'include_hidden' => false,
            'max_depth' => 20,
            'file_extensions' => ['.md'],
            'exclude_dirs' => ['.git', 'node_modules', '.idea', '__pycache__'],
            'include_metadata' => true
        ];
        
        $options = array_merge($defaults, $options);
        
        if (!is_dir($basePath) || !is_readable($basePath)) {
            throw new Exception("Base path not readable: {$basePath}");
        }
        
        $tree = [
            'base_path' => realpath($basePath),
            'total_files' => 0,
            'total_directories' => 0,
            'directories' => [],
            'scan_timestamp' => date('Y-m-d H:i:s')
        ];
        
        // Scan root level first
        $rootFiles = self::scanDirectory($basePath, '', $options, 0);
        if (!empty($rootFiles['files'])) {
            $tree['directories']['root'] = $rootFiles;
            $tree['total_files'] += count($rootFiles['files']);
            $tree['total_directories']++;
        }
        
        // Scan all subdirectories
        $subdirs = self::getSubdirectories($basePath, $options);
        
        foreach ($subdirs as $subdir) {
            $dirTree = self::scanDirectoryRecursive(
                $basePath,
                $subdir,
                $options,
                0
            );
            
            if (!empty($dirTree)) {
                $tree['directories'][$subdir] = $dirTree;
                $tree['total_files'] += self::countFiles($dirTree);
                $tree['total_directories'] += self::countDirectories($dirTree);
            }
        }
        
        return $tree;
    }
    
    /**
     * Recursively scan directory and subdirectories
     */
    private static function scanDirectoryRecursive($basePath, $relativePath, $options, $depth) {
        if ($depth >= $options['max_depth']) {
            return null;
        }
        
        $fullPath = $basePath . '/' . $relativePath;
        
        if (!is_dir($fullPath) || !is_readable($fullPath)) {
            return null;
        }
        
        $result = [
            'path' => $relativePath,
            'files' => [],
            'subdirectories' => []
        ];
        
        // Scan current directory for files
        $dirScan = self::scanDirectory($basePath, $relativePath, $options, $depth);
        $result['files'] = $dirScan['files'];
        
        // Get subdirectories
        $subdirs = self::getSubdirectories($fullPath, $options);
        
        // Recursively scan subdirectories
        foreach ($subdirs as $subdir) {
            $subPath = $relativePath . '/' . $subdir;
            $subTree = self::scanDirectoryRecursive($basePath, $subPath, $options, $depth + 1);
            
            if ($subTree !== null && (!empty($subTree['files']) || !empty($subTree['subdirectories']))) {
                $result['subdirectories'][$subdir] = $subTree;
            }
        }
        
        return $result;
    }
    
    /**
     * Scan single directory (non-recursive)
     */
    private static function scanDirectory($basePath, $relativePath, $options, $depth) {
        $fullPath = $relativePath ? $basePath . '/' . $relativePath : $basePath;
        
        $result = [
            'path' => $relativePath ?: 'root',
            'files' => []
        ];
        
        if (!is_dir($fullPath) || !is_readable($fullPath)) {
            return $result;
        }
        
        $entries = scandir($fullPath);
        
        foreach ($entries as $entry) {
            // Skip special entries
            if ($entry === '.' || $entry === '..') {
                continue;
            }
            
            // Skip hidden files unless allowed
            if (!$options['include_hidden'] && $entry[0] === '.') {
                continue;
            }
            
            $entryPath = $fullPath . '/' . $entry;
            
            // Only process files (directories handled separately)
            if (!is_file($entryPath)) {
                continue;
            }
            
            // Check file extension
            $hasValidExtension = false;
            foreach ($options['file_extensions'] as $ext) {
                if (substr($entry, -strlen($ext)) === $ext) {
                    $hasValidExtension = true;
                    break;
                }
            }
            
            if (!$hasValidExtension) {
                continue;
            }
            
            // Build file info
            $fileRelativePath = $relativePath ? $relativePath . '/' . $entry : $entry;
            
            $fileInfo = [
                'filename' => $entry,
                'relative_path' => $fileRelativePath,
                'size' => filesize($entryPath),
                'modified' => filemtime($entryPath)
            ];
            
            // Add metadata if requested
            if ($options['include_metadata']) {
                $metadata = self::extractQuickMetadata($entryPath);
                $fileInfo = array_merge($fileInfo, $metadata);
            }
            
            $result['files'][] = $fileInfo;
        }
        
        return $result;
    }
    
    /**
     * Get subdirectories of a directory
     */
    private static function getSubdirectories($path, $options) {
        $subdirs = [];
        
        if (!is_dir($path) || !is_readable($path)) {
            return $subdirs;
        }
        
        $entries = scandir($path);
        
        foreach ($entries as $entry) {
            if ($entry === '.' || $entry === '..') {
                continue;
            }
            
            // Skip hidden unless allowed
            if (!$options['include_hidden'] && $entry[0] === '.') {
                continue;
            }
            
            // Skip excluded directories
            if (in_array($entry, $options['exclude_dirs'])) {
                continue;
            }
            
            $entryPath = $path . '/' . $entry;
            
            if (is_dir($entryPath) && is_readable($entryPath)) {
                $subdirs[] = $entry;
            }
        }
        
        sort($subdirs);
        return $subdirs;
    }
    
    /**
     * Extract quick metadata from file (first few lines only)
     */
    private static function extractQuickMetadata($filepath) {
        $metadata = [
            'version' => null,
            'ref_id' => null,
            'category' => null,
            'purpose' => null
        ];
        
        if (!is_readable($filepath)) {
            return $metadata;
        }
        
        // Read first 20 lines only (performance)
        $handle = fopen($filepath, 'r');
        $lineCount = 0;
        $maxLines = 20;
        
        while (!feof($handle) && $lineCount < $maxLines) {
            $line = trim(fgets($handle));
            $lineCount++;
            
            // Extract version
            if (preg_match('/\*\*Version:\*\*\s*(.+)$/', $line, $matches)) {
                $metadata['version'] = trim($matches[1]);
            }
            
            // Extract REF-ID
            if (preg_match('/\*\*REF-ID:\*\*\s*(.+)$/', $line, $matches)) {
                $metadata['ref_id'] = trim($matches[1]);
            }
            
            // Extract category
            if (preg_match('/\*\*Category:\*\*\s*(.+)$/', $line, $matches)) {
                $metadata['category'] = trim($matches[1]);
            }
            
            // Extract purpose
            if (preg_match('/\*\*Purpose:\*\*\s*(.+)$/', $line, $matches)) {
                $metadata['purpose'] = trim($matches[1]);
            }
            
            // Stop after header section
            if ($line === '---' && $lineCount > 3) {
                break;
            }
        }
        
        fclose($handle);
        return $metadata;
    }
    
    /**
     * Count total files in tree
     */
    private static function countFiles($tree) {
        $count = count($tree['files'] ?? []);
        
        if (!empty($tree['subdirectories'])) {
            foreach ($tree['subdirectories'] as $subdir) {
                $count += self::countFiles($subdir);
            }
        }
        
        return $count;
    }
    
    /**
     * Count total directories in tree
     */
    private static function countDirectories($tree) {
        $count = 1; // Current directory
        
        if (!empty($tree['subdirectories'])) {
            foreach ($tree['subdirectories'] as $subdir) {
                $count += self::countDirectories($subdir);
            }
        }
        
        return $count;
    }
}
