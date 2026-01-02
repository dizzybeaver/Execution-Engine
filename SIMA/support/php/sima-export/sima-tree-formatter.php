<?php
/**
 * sima-tree-formatter.php
 * 
 * Convert Scanner Output to UI Tree Format
 * Version: 1.0.2
 * Date: 2025-11-23
 * Location: /sima/support/php/
 * 
 * FIXED: Proper handling of root-level directories - context no longer shows under generic
 * Converts SIMAScanner output into format expected by sima-tree.js
 * Maintains compatibility with existing UI components
 * 
 * CRITICAL: Stays under 350 lines
 */

class SIMATreeFormatter {
    
    /**
     * Convert scanner tree to UI format
     * FIXED: Proper handling of root-level directories
     * 
     * @param array $scanTree Output from SIMAScanner::scanComplete()
     * @return array UI-compatible tree structure
     */
    public static function formatForUI($scanTree) {
        if (empty($scanTree) || empty($scanTree['directories'])) {
            return [];
        }
        
        $uiTree = [];
        
        // Define domain directories and support directories
        $domainDirs = ['generic', 'platforms', 'languages', 'projects'];
        $supportDirs = ['context', 'docs', 'support', 'templates'];
        
        // Process each top-level directory
        foreach ($scanTree['directories'] as $dirName => $dirData) {
            if ($dirName === 'root') {
                // Root files go directly in tree
                foreach ($dirData['files'] as $file) {
                    $uiTree[] = self::formatFile($file, 'root');
                }
                continue;
            }
            
            // Check if this directory should be a top-level node
            $isTopLevelDir = in_array($dirName, $domainDirs) || 
                            in_array($dirName, $supportDirs) ||
                            !self::isSubdirectoryOfAny($dirName, array_merge($domainDirs, $supportDirs), $scanTree['directories']);
            
            if ($isTopLevelDir) {
                // Format as top-level directory
                $dirNode = self::formatDirectory($dirName, $dirData);
                $uiTree[] = $dirNode;
            }
        }
        
        return $uiTree;
    }
    
    /**
     * Check if a directory is actually a subdirectory of any other directory
     */
    private static function isSubdirectoryOfAny($dirName, $parentDirs, $allDirectories) {
        foreach ($parentDirs as $parentDir) {
            if (isset($allDirectories[$parentDir])) {
                $parentData = $allDirectories[$parentDir];
                if (self::hasSubdirectory($parentData, $dirName)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    /**
     * Check if directory data contains a specific subdirectory
     */
    private static function hasSubdirectory($dirData, $subdirName) {
        if (!empty($dirData['subdirectories'])) {
            foreach ($dirData['subdirectories'] as $existingSubdirName => $subdirData) {
                if ($existingSubdirName === $subdirName) {
                    return true;
                }
                // Check recursively
                if (self::hasSubdirectory($subdirData, $subdirName)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    /**
     * Format directory node recursively
     */
    private static function formatDirectory($name, $data) {
        $fileCount = count($data['files'] ?? []);
        $subdirCount = count($data['subdirectories'] ?? []);
        $totalFiles = self::countAllFiles($data);
        
        $node = [
            'type' => 'directory',
            'name' => $name,
            'path' => $data['path'],
            'file_count' => $fileCount,
            'total_files' => $totalFiles,
            'children' => []
        ];
        
        // Add files
        foreach ($data['files'] ?? [] as $file) {
            $node['children'][] = self::formatFile($file, $data['path']);
        }
        
        // Add subdirectories recursively
        foreach ($data['subdirectories'] ?? [] as $subdirName => $subdirData) {
            $node['children'][] = self::formatDirectory($subdirName, $subdirData);
        }
        
        return $node;
    }
    
    /**
     * Format file node
     */
    private static function formatFile($file, $parentPath) {
        return [
            'type' => 'file',
            'name' => $file['filename'],
            'path' => $file['relative_path'],
            'size' => $file['size'],
            'modified' => $file['modified'],
            'version' => $file['version'] ?? null,
            'ref_id' => $file['ref_id'] ?? null,
            'category' => $file['category'] ?? null,
            'purpose' => $file['purpose'] ?? null
        ];
    }
    
    /**
     * Count all files in directory tree
     */
    private static function countAllFiles($data) {
        $count = count($data['files'] ?? []);
        
        foreach ($data['subdirectories'] ?? [] as $subdir) {
            $count += self::countAllFiles($subdir);
        }
        
        return $count;
    }
    
    /**
     * Generate flat file list from tree
     * Used for export selection
     * 
     * @param array $scanTree Output from SIMAScanner::scanComplete()
     * @return array Flat array of all files
     */
    public static function getFlatFileList($scanTree) {
        $files = [];
        
        if (empty($scanTree) || empty($scanTree['directories'])) {
            return $files;
        }
        
        foreach ($scanTree['directories'] as $dirName => $dirData) {
            self::collectFiles($dirData, $files);
        }
        
        return $files;
    }
    
    /**
     * Recursively collect files
     */
    private static function collectFiles($data, &$files) {
        // Add files from current directory
        foreach ($data['files'] ?? [] as $file) {
            $files[] = $file;
        }
        
        // Recurse into subdirectories
        foreach ($data['subdirectories'] ?? [] as $subdirData) {
            self::collectFiles($subdirData, $files);
        }
    }
    
    /**
     * Group files by category/domain
     * Used for organized display
     * 
     * @param array $scanTree Output from SIMAScanner::scanComplete()
     * @return array Files grouped by category
     */
    public static function groupByCategory($scanTree) {
        $grouped = [];
        
        $flatFiles = self::getFlatFileList($scanTree);
        
        foreach ($flatFiles as $file) {
            // Determine category from path
            $category = self::determineCategoryFromPath($file['relative_path']);
            
            if (!isset($grouped[$category])) {
                $grouped[$category] = [
                    'name' => $category,
                    'files' => []
                ];
            }
            
            $grouped[$category]['files'][] = $file;
        }
        
        return $grouped;
    }
    
    /**
     * Determine category from file path
     */
    private static function determineCategoryFromPath($path) {
        $parts = explode('/', $path);
        
        // Check for domain structure (generic, platforms, languages, projects)
        if (count($parts) >= 2) {
            $firstDir = $parts[0];
            
            if (in_array($firstDir, ['generic', 'platforms', 'languages', 'projects'])) {
                // Use domain as primary category
                if (count($parts) >= 3) {
                    // Include subdomain/platform/language name
                    return $firstDir . '/' . $parts[1];
                }
                return $firstDir;
            }
            
            // Other top-level directories (context, docs, support, templates)
            return $firstDir;
        }
        
        return 'root';
    }
    
    /**
     * Generate statistics from tree
     * 
     * @param array $scanTree Output from SIMAScanner::scanComplete()
     * @return array Statistics
     */
    public static function generateStats($scanTree) {
        $stats = [
            'total_files' => $scanTree['total_files'] ?? 0,
            'total_directories' => $scanTree['total_directories'] ?? 0,
            'by_domain' => [],
            'by_category' => [],
            'by_extension' => [],
            'with_ref_id' => 0,
            'with_version' => 0
        ];
        
        $flatFiles = self::getFlatFileList($scanTree);
        
        foreach ($flatFiles as $file) {
            // Count by domain
            $parts = explode('/', $file['relative_path']);
            $domain = $parts[0] ?? 'root';
            
            if (!isset($stats['by_domain'][$domain])) {
                $stats['by_domain'][$domain] = 0;
            }
            $stats['by_domain'][$domain]++;
            
            // Count by category
            if (!empty($file['category'])) {
                if (!isset($stats['by_category'][$file['category']])) {
                    $stats['by_category'][$file['category']] = 0;
                }
                $stats['by_category'][$file['category']]++;
            }
            
            // Count by extension
            $ext = pathinfo($file['filename'], PATHINFO_EXTENSION);
            if (!isset($stats['by_extension'][$ext])) {
                $stats['by_extension'][$ext] = 0;
            }
            $stats['by_extension'][$ext]++;
            
            // Count metadata presence
            if (!empty($file['ref_id'])) {
                $stats['with_ref_id']++;
            }
            if (!empty($file['version'])) {
                $stats['with_version']++;
            }
        }
        
        return $stats;
    }
    
    /**
     * Filter tree by criteria
     * 
     * @param array $scanTree Output from SIMAScanner::scanComplete()
     * @param array $criteria Filter criteria
     * @return array Filtered tree
     */
    public static function filterTree($scanTree, $criteria) {
        $filtered = [
            'base_path' => $scanTree['base_path'],
            'total_files' => 0,
            'total_directories' => 0,
            'directories' => [],
            'scan_timestamp' => $scanTree['scan_timestamp']
        ];
        
        foreach ($scanTree['directories'] as $dirName => $dirData) {
            $filteredDir = self::filterDirectory($dirData, $criteria);
            
            if ($filteredDir !== null) {
                $filtered['directories'][$dirName] = $filteredDir;
                $filtered['total_files'] += self::countAllFiles($filteredDir);
                $filtered['total_directories']++;
            }
        }
        
        return $filtered;
    }
    
    /**
     * Filter directory recursively
     */
    private static function filterDirectory($data, $criteria) {
        $result = [
            'path' => $data['path'],
            'files' => [],
            'subdirectories' => []
        ];
        
        // Filter files
        foreach ($data['files'] ?? [] as $file) {
            if (self::matchesCriteria($file, $criteria)) {
                $result['files'][] = $file;
            }
        }
        
        // Filter subdirectories
        foreach ($data['subdirectories'] ?? [] as $subdirName => $subdirData) {
            $filteredSubdir = self::filterDirectory($subdirData, $criteria);
            
            if ($filteredSubdir !== null && 
                (!empty($filteredSubdir['files']) || !empty($filteredSubdir['subdirectories']))) {
                $result['subdirectories'][$subdirName] = $filteredSubdir;
            }
        }
        
        // Return null if no files and no subdirectories
        if (empty($result['files']) && empty($result['subdirectories'])) {
            return null;
        }
        
        return $result;
    }
    
    /**
     * Check if file matches filter criteria
     */
    private static function matchesCriteria($file, $criteria) {
        // Category filter
        if (!empty($criteria['category'])) {
            if (empty($file['category']) || $file['category'] !== $criteria['category']) {
                return false;
            }
        }
        
        // Domain filter (from path)
        if (!empty($criteria['domain'])) {
            $parts = explode('/', $file['relative_path']);
            if (empty($parts[0]) || $parts[0] !== $criteria['domain']) {
                return false;
            }
        }
        
        // REF-ID presence filter
        if (isset($criteria['has_ref_id']) && $criteria['has_ref_id']) {
            if (empty($file['ref_id'])) {
                return false;
            }
        }
        
        // Version presence filter
        if (isset($criteria['has_version']) && $criteria['has_version']) {
            if (empty($file['version'])) {
                return false;
            }
        }
        
        // Filename pattern filter
        if (!empty($criteria['filename_pattern'])) {
            if (!preg_match($criteria['filename_pattern'], $file['filename'])) {
                return false;
            }
        }
        
        return true;
    }
}
