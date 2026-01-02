<?php
/**
 * tree_formatter.php
 * 
 * Internal: Tree formatting and transformation
 * Version: 1.0.0
 * Date: 2025-11-27
 */

class TreeFormatter {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    /**
     * Format tree for UI
     */
    public function formatForUI($scanTree) {
        if (empty($scanTree) || empty($scanTree['directories'])) {
            return [];
        }
        
        $uiTree = [];
        $domainDirs = $this->config['format']['domain_dirs'];
        $supportDirs = $this->config['format']['support_dirs'];
        
        foreach ($scanTree['directories'] as $dirName => $dirData) {
            if ($dirName === 'root') {
                foreach ($dirData['files'] as $file) {
                    $uiTree[] = $this->formatFile($file, 'root');
                }
                continue;
            }
            
            $isTopLevel = in_array($dirName, $domainDirs) || 
                         in_array($dirName, $supportDirs) ||
                         !$this->isSubdirectoryOfAny($dirName, array_merge($domainDirs, $supportDirs), $scanTree['directories']);
            
            if ($isTopLevel) {
                $dirNode = $this->formatDirectory($dirName, $dirData);
                $uiTree[] = $dirNode;
            }
        }
        
        return $uiTree;
    }
    
    /**
     * Check if directory is subdirectory of any parent
     */
    private function isSubdirectoryOfAny($dirName, $parentDirs, $allDirectories) {
        foreach ($parentDirs as $parentDir) {
            if (isset($allDirectories[$parentDir])) {
                $parentData = $allDirectories[$parentDir];
                if ($this->hasSubdirectory($parentData, $dirName)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    /**
     * Check if directory has subdirectory
     */
    private function hasSubdirectory($dirData, $subdirName) {
        if (!empty($dirData['subdirectories'])) {
            foreach ($dirData['subdirectories'] as $existingSubdirName => $subdirData) {
                if ($existingSubdirName === $subdirName) {
                    return true;
                }
                if ($this->hasSubdirectory($subdirData, $subdirName)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    /**
     * Format directory node
     */
    private function formatDirectory($name, $data) {
        $fileCount = count($data['files'] ?? []);
        $totalFiles = $this->countAllFiles($data);
        
        $node = [
            'type' => 'directory',
            'name' => $name,
            'path' => $data['path'],
            'file_count' => $fileCount,
            'total_files' => $totalFiles,
            'children' => []
        ];
        
        foreach ($data['files'] ?? [] as $file) {
            $node['children'][] = $this->formatFile($file, $data['path']);
        }
        
        foreach ($data['subdirectories'] ?? [] as $subdirName => $subdirData) {
            $node['children'][] = $this->formatDirectory($subdirName, $subdirData);
        }
        
        return $node;
    }
    
    /**
     * Format file node
     */
    private function formatFile($file, $parentPath) {
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
     * Count all files
     */
    private function countAllFiles($data) {
        $count = count($data['files'] ?? []);
        
        foreach ($data['subdirectories'] ?? [] as $subdir) {
            $count += $this->countAllFiles($subdir);
        }
        
        return $count;
    }
    
    /**
     * Get flat file list
     */
    public function getFlatFileList($scanTree) {
        $files = [];
        
        if (empty($scanTree) || empty($scanTree['directories'])) {
            return $files;
        }
        
        foreach ($scanTree['directories'] as $dirName => $dirData) {
            $this->collectFiles($dirData, $files);
        }
        
        return $files;
    }
    
    /**
     * Collect files recursively
     */
    private function collectFiles($data, &$files) {
        foreach ($data['files'] ?? [] as $file) {
            $files[] = $file;
        }
        
        foreach ($data['subdirectories'] ?? [] as $subdirData) {
            $this->collectFiles($subdirData, $files);
        }
    }
    
    /**
     * Group by category
     */
    public function groupByCategory($scanTree) {
        $grouped = [];
        $flatFiles = $this->getFlatFileList($scanTree);
        
        foreach ($flatFiles as $file) {
            $category = $this->determineCategoryFromPath($file['relative_path']);
            
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
     * Determine category from path
     */
    private function determineCategoryFromPath($path) {
        $parts = explode('/', $path);
        
        if (count($parts) >= 2) {
            $firstDir = $parts[0];
            
            if (in_array($firstDir, $this->config['format']['domain_dirs'])) {
                if (count($parts) >= 3) {
                    return $firstDir . '/' . $parts[1];
                }
                return $firstDir;
            }
            
            return $firstDir;
        }
        
        return 'root';
    }
    
    /**
     * Generate statistics
     */
    public function generateStats($scanTree) {
        $stats = [
            'total_files' => $scanTree['total_files'] ?? 0,
            'total_directories' => $scanTree['total_directories'] ?? 0,
            'by_domain' => [],
            'by_category' => [],
            'by_extension' => [],
            'with_ref_id' => 0,
            'with_version' => 0
        ];
        
        $flatFiles = $this->getFlatFileList($scanTree);
        
        foreach ($flatFiles as $file) {
            $parts = explode('/', $file['relative_path']);
            $domain = $parts[0] ?? 'root';
            
            if (!isset($stats['by_domain'][$domain])) {
                $stats['by_domain'][$domain] = 0;
            }
            $stats['by_domain'][$domain]++;
            
            if (!empty($file['category'])) {
                if (!isset($stats['by_category'][$file['category']])) {
                    $stats['by_category'][$file['category']] = 0;
                }
                $stats['by_category'][$file['category']]++;
            }
            
            $ext = pathinfo($file['filename'], PATHINFO_EXTENSION);
            if (!isset($stats['by_extension'][$ext])) {
                $stats['by_extension'][$ext] = 0;
            }
            $stats['by_extension'][$ext]++;
            
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
     * Filter tree
     */
    public function filterTree($scanTree, $criteria) {
        $filtered = [
            'base_path' => $scanTree['base_path'],
            'total_files' => 0,
            'total_directories' => 0,
            'directories' => [],
            'scan_timestamp' => $scanTree['scan_timestamp']
        ];
        
        foreach ($scanTree['directories'] as $dirName => $dirData) {
            $filteredDir = $this->filterDirectory($dirData, $criteria);
            
            if ($filteredDir !== null) {
                $filtered['directories'][$dirName] = $filteredDir;
                $filtered['total_files'] += $this->countAllFiles($filteredDir);
                $filtered['total_directories']++;
            }
        }
        
        return $filtered;
    }
    
    /**
     * Filter directory
     */
    private function filterDirectory($data, $criteria) {
        $result = [
            'path' => $data['path'],
            'files' => [],
            'subdirectories' => []
        ];
        
        foreach ($data['files'] ?? [] as $file) {
            if ($this->matchesCriteria($file, $criteria)) {
                $result['files'][] = $file;
            }
        }
        
        foreach ($data['subdirectories'] ?? [] as $subdirName => $subdirData) {
            $filteredSubdir = $this->filterDirectory($subdirData, $criteria);
            
            if ($filteredSubdir !== null && 
                (!empty($filteredSubdir['files']) || !empty($filteredSubdir['subdirectories']))) {
                $result['subdirectories'][$subdirName] = $filteredSubdir;
            }
        }
        
        if (empty($result['files']) && empty($result['subdirectories'])) {
            return null;
        }
        
        return $result;
    }
    
    /**
     * Check if file matches criteria
     */
    private function matchesCriteria($file, $criteria) {
        if (!empty($criteria['category'])) {
            if (empty($file['category']) || $file['category'] !== $criteria['category']) {
                return false;
            }
        }
        
        if (!empty($criteria['domain'])) {
            $parts = explode('/', $file['relative_path']);
            if (empty($parts[0]) || $parts[0] !== $criteria['domain']) {
                return false;
            }
        }
        
        if (isset($criteria['has_ref_id']) && $criteria['has_ref_id']) {
            if (empty($file['ref_id'])) {
                return false;
            }
        }
        
        if (isset($criteria['has_version']) && $criteria['has_version']) {
            if (empty($file['version'])) {
                return false;
            }
        }
        
        if (!empty($criteria['filename_pattern'])) {
            if (!preg_match($criteria['filename_pattern'], $file['filename'])) {
                return false;
            }
        }
        
        return true;
    }
}
