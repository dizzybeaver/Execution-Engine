<?php
/**
 * tree_scanner.php
 * 
 * Internal: Filesystem scanning functionality
 * Version: 1.0.0
 * Date: 2025-11-27
 */

class TreeScanner {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    /**
     * Scan directory tree completely
     */
    public function scanComplete($basePath, $options = []) {
        $options = array_merge($this->config['scan'], $options);
        
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
        
        // Scan root level
        $rootFiles = $this->scanDirectory($basePath, '', $options, 0);
        if (!empty($rootFiles['files'])) {
            $tree['directories']['root'] = $rootFiles;
            $tree['total_files'] += count($rootFiles['files']);
            $tree['total_directories']++;
        }
        
        // Scan subdirectories
        $subdirs = $this->getSubdirectories($basePath, $options);
        
        foreach ($subdirs as $subdir) {
            $dirTree = $this->scanDirectoryRecursive($basePath, $subdir, $options, 0);
            
            if (!empty($dirTree)) {
                $tree['directories'][$subdir] = $dirTree;
                $tree['total_files'] += $this->countFiles($dirTree);
                $tree['total_directories'] += $this->countDirectories($dirTree);
            }
        }
        
        return $tree;
    }
    
    /**
     * Scan directory recursively
     */
    private function scanDirectoryRecursive($basePath, $relativePath, $options, $depth) {
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
        
        // Scan current directory
        $dirScan = $this->scanDirectory($basePath, $relativePath, $options, $depth);
        $result['files'] = $dirScan['files'];
        
        // Get subdirectories
        $subdirs = $this->getSubdirectories($fullPath, $options);
        
        // Recurse
        foreach ($subdirs as $subdir) {
            $subPath = $relativePath . '/' . $subdir;
            $subTree = $this->scanDirectoryRecursive($basePath, $subPath, $options, $depth + 1);
            
            if ($subTree !== null && (!empty($subTree['files']) || !empty($subTree['subdirectories']))) {
                $result['subdirectories'][$subdir] = $subTree;
            }
        }
        
        return $result;
    }
    
    /**
     * Scan single directory
     */
    private function scanDirectory($basePath, $relativePath, $options, $depth) {
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
            if ($entry === '.' || $entry === '..') {
                continue;
            }
            
            if (!$options['include_hidden'] && $entry[0] === '.') {
                continue;
            }
            
            $entryPath = $fullPath . '/' . $entry;
            
            if (!is_file($entryPath)) {
                continue;
            }
            
            // Check extension
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
            
            $fileRelativePath = $relativePath ? $relativePath . '/' . $entry : $entry;
            
            $fileInfo = [
                'filename' => $entry,
                'relative_path' => $fileRelativePath,
                'size' => filesize($entryPath),
                'modified' => filemtime($entryPath)
            ];
            
            if ($options['include_metadata']) {
                $metadata = $this->extractMetadata($entryPath);
                $fileInfo = array_merge($fileInfo, $metadata);
            }
            
            $result['files'][] = $fileInfo;
        }
        
        return $result;
    }
    
    /**
     * Get subdirectories
     */
    private function getSubdirectories($path, $options) {
        $subdirs = [];
        
        if (!is_dir($path) || !is_readable($path)) {
            return $subdirs;
        }
        
        $entries = scandir($path);
        
        foreach ($entries as $entry) {
            if ($entry === '.' || $entry === '..') {
                continue;
            }
            
            if (!$options['include_hidden'] && $entry[0] === '.') {
                continue;
            }
            
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
     * Extract metadata from file
     */
    private function extractMetadata($filepath) {
        $metadata = [
            'version' => null,
            'ref_id' => null,
            'category' => null,
            'purpose' => null
        ];
        
        if (!is_readable($filepath)) {
            return $metadata;
        }
        
        $handle = fopen($filepath, 'r');
        $lineCount = 0;
        $maxLines = $this->config['metadata']['max_lines_to_scan'];
        
        while (!feof($handle) && $lineCount < $maxLines) {
            $line = trim(fgets($handle));
            $lineCount++;
            
            foreach ($this->config['metadata']['fields'] as $field => $pattern) {
                if (preg_match($pattern, $line, $matches)) {
                    $metadata[$field] = trim($matches[1]);
                }
            }
            
            if ($line === $this->config['metadata']['header_end_marker'] && $lineCount > 3) {
                break;
            }
        }
        
        fclose($handle);
        return $metadata;
    }
    
    /**
     * Count files in tree
     */
    private function countFiles($tree) {
        $count = count($tree['files'] ?? []);
        
        if (!empty($tree['subdirectories'])) {
            foreach ($tree['subdirectories'] as $subdir) {
                $count += $this->countFiles($subdir);
            }
        }
        
        return $count;
    }
    
    /**
     * Count directories in tree
     */
    private function countDirectories($tree) {
        $count = 1;
        
        if (!empty($tree['subdirectories'])) {
            foreach ($tree['subdirectories'] as $subdir) {
                $count += $this->countDirectories($subdir);
            }
        }
        
        return $count;
    }
}
