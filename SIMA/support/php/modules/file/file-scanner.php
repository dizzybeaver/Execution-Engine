<?php
/**
 * file-scanner.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-27
 * Purpose: File system scanning operations
 * Project: SIMA File Module
 * 
 * ADDED: Complete scanning functionality
 */

class FileScanner {
    
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    /**
     * Scan directory recursively
     * 
     * @param string $directory Directory path
     * @param array $options Scan options
     * @return array Scan results
     */
    public function scan($directory, $options = []) {
        $options = array_merge([
            'recursive' => true,
            'include_metadata' => true,
            'calculate_checksums' => $this->config['calculate_checksums'],
            'max_depth' => $this->config['max_scan_depth'],
            'current_depth' => 0
        ], $options);
        
        $results = [
            'files' => [],
            'directories' => [],
            'stats' => [
                'total_files' => 0,
                'total_size' => 0,
                'total_directories' => 0
            ]
        ];
        
        if (!is_dir($directory)) {
            return ['error' => 'Directory not found: ' . $directory];
        }
        
        $this->scanRecursive($directory, $results, $options);
        
        return $results;
    }
    
    /**
     * Recursive scanning implementation
     * 
     * @param string $directory Current directory
     * @param array &$results Results array
     * @param array $options Scan options
     */
    private function scanRecursive($directory, &$results, $options) {
        // Check depth limit
        if ($options['max_depth'] > 0 && $options['current_depth'] >= $options['max_depth']) {
            return;
        }
        
        $items = scandir($directory);
        if ($items === false) {
            return;
        }
        
        foreach ($items as $item) {
            if ($item === '.' || $item === '..') {
                continue;
            }
            
            $path = $directory . DIRECTORY_SEPARATOR . $item;
            
            // Skip excluded items
            if ($this->shouldExclude($path, $item)) {
                continue;
            }
            
            if (is_dir($path)) {
                $results['directories'][] = $path;
                $results['stats']['total_directories']++;
                
                if ($options['recursive']) {
                    $newOptions = $options;
                    $newOptions['current_depth']++;
                    $this->scanRecursive($path, $results, $newOptions);
                }
            } elseif (is_file($path)) {
                $fileInfo = [
                    'path' => $path,
                    'filename' => $item,
                    'size' => filesize($path)
                ];
                
                if ($options['include_metadata']) {
                    $fileInfo = array_merge($fileInfo, $this->extractMetadata($path));
                }
                
                if ($options['calculate_checksums']) {
                    $fileInfo['checksum'] = $this->calculateChecksum($path);
                }
                
                $results['files'][] = $fileInfo;
                $results['stats']['total_files']++;
                $results['stats']['total_size'] += $fileInfo['size'];
            }
        }
    }
    
    /**
     * Scan with filters
     * 
     * @param string $directory Directory path
     * @param array $filters Filter criteria
     * @return array Filtered results
     */
    public function scanFiltered($directory, $filters = []) {
        $results = $this->scan($directory);
        
        if (isset($results['error'])) {
            return $results;
        }
        
        // Apply filters
        if (!empty($filters)) {
            $results['files'] = array_filter($results['files'], function($file) use ($filters) {
                return $this->matchesFilters($file, $filters);
            });
            
            // Recalculate stats
            $results['stats']['total_files'] = count($results['files']);
            $results['stats']['total_size'] = array_sum(array_column($results['files'], 'size'));
        }
        
        return $results;
    }
    
    /**
     * Get directory statistics
     * 
     * @param string $directory Directory path
     * @return array Statistics
     */
    public function getStats($directory) {
        $results = $this->scan($directory, ['include_metadata' => false, 'calculate_checksums' => false]);
        
        if (isset($results['error'])) {
            return $results;
        }
        
        $stats = $results['stats'];
        
        // Add extension breakdown
        $stats['by_extension'] = [];
        foreach ($results['files'] as $file) {
            $ext = pathinfo($file['filename'], PATHINFO_EXTENSION);
            if (!isset($stats['by_extension'][$ext])) {
                $stats['by_extension'][$ext] = ['count' => 0, 'size' => 0];
            }
            $stats['by_extension'][$ext]['count']++;
            $stats['by_extension'][$ext]['size'] += $file['size'];
        }
        
        return $stats;
    }
    
    /**
     * Extract metadata from file
     * 
     * @param string $filePath File path
     * @return array Metadata
     */
    private function extractMetadata($filePath) {
        $metadata = [
            'modified' => filemtime($filePath),
            'extension' => pathinfo($filePath, PATHINFO_EXTENSION)
        ];
        
        // Extract version if enabled
        if ($this->config['extract_versions']) {
            $version = $this->extractVersion($filePath);
            if ($version) {
                $metadata['version'] = $version;
            }
        }
        
        // Extract REF-ID if enabled
        if ($this->config['extract_ref_ids']) {
            $refId = $this->extractRefId($filePath);
            if ($refId) {
                $metadata['ref_id'] = $refId;
            }
        }
        
        return $metadata;
    }
    
    /**
     * Extract version from file content
     * 
     * @param string $filePath File path
     * @return string|null Version string
     */
    private function extractVersion($filePath) {
        $ext = pathinfo($filePath, PATHINFO_EXTENSION);
        if ($ext !== 'md' && $ext !== 'php') {
            return null;
        }
        
        $content = @file_get_contents($filePath, false, null, 0, 2048);
        if ($content === false) {
            return null;
        }
        
        // Match version patterns
        if (preg_match('/\*\*Version:\*\*\s*([\d\.]+)/i', $content, $matches)) {
            return $matches[1];
        }
        if (preg_match('/Version:\s*([\d\.]+)/i', $content, $matches)) {
            return $matches[1];
        }
        if (preg_match('/@version\s+([\d\.]+)/i', $content, $matches)) {
            return $matches[1];
        }
        
        return null;
    }
    
    /**
     * Extract REF-ID from file content
     * 
     * @param string $filePath File path
     * @return string|null REF-ID
     */
    private function extractRefId($filePath) {
        $ext = pathinfo($filePath, PATHINFO_EXTENSION);
        if ($ext !== 'md') {
            return null;
        }
        
        $content = @file_get_contents($filePath, false, null, 0, 2048);
        if ($content === false) {
            return null;
        }
        
        // Match REF-ID patterns
        if (preg_match('/\*\*REF-ID:\*\*\s*([A-Z]+-\d+)/i', $content, $matches)) {
            return $matches[1];
        }
        if (preg_match('/^#\s+([A-Z]+-\d+)/m', $content, $matches)) {
            return $matches[1];
        }
        
        return null;
    }
    
    /**
     * Calculate file checksum
     * 
     * @param string $filePath File path
     * @return string Checksum
     */
    private function calculateChecksum($filePath) {
        $algorithm = $this->config['checksum_algorithm'];
        return hash_file($algorithm, $filePath);
    }
    
    /**
     * Check if item should be excluded
     * 
     * @param string $path Full path
     * @param string $name Item name
     * @return bool Should exclude
     */
    private function shouldExclude($path, $name) {
        // Exclude hidden files if configured
        if (!$this->config['include_hidden'] && strpos($name, '.') === 0) {
            return true;
        }
        
        // Check excluded directories
        if (is_dir($path)) {
            foreach ($this->config['exclude_directories'] as $excluded) {
                if ($name === $excluded) {
                    return true;
                }
            }
        }
        
        // Check excluded files
        if (is_file($path)) {
            foreach ($this->config['exclude_files'] as $excluded) {
                if ($name === $excluded) {
                    return true;
                }
            }
            
            // Check excluded extensions
            $ext = '.' . pathinfo($name, PATHINFO_EXTENSION);
            if (in_array($ext, $this->config['exclude_extensions'])) {
                return true;
            }
            
            // Check whitelist mode
            if ($this->config['whitelist_mode']) {
                if (!in_array($ext, $this->config['include_extensions'])) {
                    return true;
                }
            }
        }
        
        return false;
    }
    
    /**
     * Check if file matches filters
     * 
     * @param array $file File info
     * @param array $filters Filter criteria
     * @return bool Matches
     */
    private function matchesFilters($file, $filters) {
        // Extension filter
        if (isset($filters['extensions'])) {
            if (!in_array($file['extension'], $filters['extensions'])) {
                return false;
            }
        }
        
        // Size filter
        if (isset($filters['min_size']) && $file['size'] < $filters['min_size']) {
            return false;
        }
        if (isset($filters['max_size']) && $file['size'] > $filters['max_size']) {
            return false;
        }
        
        // Date filter
        if (isset($filters['modified_after']) && $file['modified'] < $filters['modified_after']) {
            return false;
        }
        if (isset($filters['modified_before']) && $file['modified'] > $filters['modified_before']) {
            return false;
        }
        
        // Version filter
        if (isset($filters['version']) && isset($file['version'])) {
            if ($file['version'] !== $filters['version']) {
                return false;
            }
        }
        
        // REF-ID filter
        if (isset($filters['ref_id']) && isset($file['ref_id'])) {
            if ($file['ref_id'] !== $filters['ref_id']) {
                return false;
            }
        }
        
        // Pattern filter
        if (isset($filters['pattern'])) {
            if (!preg_match($filters['pattern'], $file['filename'])) {
                return false;
            }
        }
        
        return true;
    }
}
