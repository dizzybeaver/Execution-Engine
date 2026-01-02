<?php
/**
 * file-metadata.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-27
 * Purpose: Metadata extraction and manifest generation
 * Project: SIMA File Module
 * 
 * ADDED: Complete metadata functionality
 */

class FileMetadata {
    
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    /**
     * Extract metadata from file
     * 
     * @param string $filePath File path
     * @return array Metadata
     */
    public function extract($filePath) {
        if (!file_exists($filePath)) {
            return ['error' => 'File not found'];
        }
        
        $metadata = [
            'path' => $filePath,
            'filename' => basename($filePath),
            'extension' => pathinfo($filePath, PATHINFO_EXTENSION),
            'size' => filesize($filePath),
            'modified' => filemtime($filePath),
            'modified_date' => date('Y-m-d H:i:s', filemtime($filePath))
        ];
        
        if ($this->config['store_file_sizes']) {
            $metadata['size_human'] = $this->formatSize($metadata['size']);
        }
        
        if ($this->config['calculate_checksums']) {
            $metadata['checksum'] = hash_file($this->config['checksum_algorithm'], $filePath);
        }
        
        // Extract content-specific metadata
        $contentMeta = $this->extractContentMetadata($filePath);
        if (!empty($contentMeta)) {
            $metadata = array_merge($metadata, $contentMeta);
        }
        
        return $metadata;
    }
    
    /**
     * Extract content-specific metadata
     * 
     * @param string $filePath File path
     * @return array Content metadata
     */
    private function extractContentMetadata($filePath) {
        $metadata = [];
        $ext = pathinfo($filePath, PATHINFO_EXTENSION);
        
        // Handle markdown and text files
        if (in_array($ext, ['md', 'txt'])) {
            $content = @file_get_contents($filePath, false, null, 0, 4096);
            if ($content !== false) {
                if ($this->config['extract_versions']) {
                    $version = $this->extractVersion($content);
                    if ($version) {
                        $metadata['version'] = $version;
                    }
                }
                
                if ($this->config['extract_ref_ids']) {
                    $refId = $this->extractRefId($content);
                    if ($refId) {
                        $metadata['ref_id'] = $refId;
                    }
                }
                
                // Extract title
                $title = $this->extractTitle($content);
                if ($title) {
                    $metadata['title'] = $title;
                }
            }
        }
        
        // Handle PHP files
        if ($ext === 'php') {
            $content = @file_get_contents($filePath, false, null, 0, 4096);
            if ($content !== false) {
                if ($this->config['extract_versions']) {
                    $version = $this->extractVersion($content);
                    if ($version) {
                        $metadata['version'] = $version;
                    }
                }
                
                // Extract purpose from docblock
                $purpose = $this->extractPurpose($content);
                if ($purpose) {
                    $metadata['purpose'] = $purpose;
                }
            }
        }
        
        return $metadata;
    }
    
    /**
     * Extract version from content
     * 
     * @param string $content File content
     * @return string|null Version
     */
    private function extractVersion($content) {
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
     * Extract REF-ID from content
     * 
     * @param string $content File content
     * @return string|null REF-ID
     */
    private function extractRefId($content) {
        if (preg_match('/\*\*REF-ID:\*\*\s*([A-Z]+-\d+)/i', $content, $matches)) {
            return $matches[1];
        }
        if (preg_match('/^#\s+([A-Z]+-\d+)/m', $content, $matches)) {
            return $matches[1];
        }
        return null;
    }
    
    /**
     * Extract title from content
     * 
     * @param string $content File content
     * @return string|null Title
     */
    private function extractTitle($content) {
        if (preg_match('/^#\s+(.+)$/m', $content, $matches)) {
            return trim($matches[1]);
        }
        return null;
    }
    
    /**
     * Extract purpose from content
     * 
     * @param string $content File content
     * @return string|null Purpose
     */
    private function extractPurpose($content) {
        if (preg_match('/\*\s*Purpose:\s*(.+)$/m', $content, $matches)) {
            return trim($matches[1]);
        }
        return null;
    }
    
    /**
     * Calculate checksums for multiple files
     * 
     * @param array $files File paths
     * @param string $algorithm Hash algorithm
     * @return array Checksums
     */
    public function calculateChecksums($files, $algorithm = null) {
        if ($algorithm === null) {
            $algorithm = $this->config['checksum_algorithm'];
        }
        
        $checksums = [];
        
        foreach ($files as $file) {
            if (file_exists($file)) {
                $checksums[$file] = hash_file($algorithm, $file);
            }
        }
        
        return $checksums;
    }
    
    /**
     * Create manifest for files
     * 
     * @param array $files File paths
     * @param array $options Manifest options
     * @return array Manifest data
     */
    public function createManifest($files, $options = []) {
        $options = array_merge([
            'include_checksums' => true,
            'include_metadata' => true,
            'group_by_directory' => false,
            'format' => 'yaml'
        ], $options);
        
        $manifest = [
            'archive' => [
                'created' => date('Y-m-d H:i:s'),
                'created_timestamp' => time(),
                'version' => '1.0.0',
                'generator' => 'SIMA File Module'
            ],
            'files' => [
                'total' => count($files),
                'list' => []
            ],
            'stats' => [
                'total_size' => 0,
                'by_extension' => []
            ]
        ];
        
        foreach ($files as $file) {
            if (!file_exists($file)) {
                continue;
            }
            
            $fileInfo = [
                'path' => $file,
                'size' => filesize($file)
            ];
            
            if ($options['include_checksums']) {
                $fileInfo['checksum'] = hash_file($this->config['checksum_algorithm'], $file);
            }
            
            if ($options['include_metadata']) {
                $metadata = $this->extract($file);
                $fileInfo = array_merge($fileInfo, $metadata);
            }
            
            $manifest['files']['list'][] = $fileInfo;
            $manifest['stats']['total_size'] += $fileInfo['size'];
            
            // Track by extension
            $ext = pathinfo($file, PATHINFO_EXTENSION);
            if (!isset($manifest['stats']['by_extension'][$ext])) {
                $manifest['stats']['by_extension'][$ext] = [
                    'count' => 0,
                    'size' => 0
                ];
            }
            $manifest['stats']['by_extension'][$ext]['count']++;
            $manifest['stats']['by_extension'][$ext]['size'] += $fileInfo['size'];
        }
        
        // Add human-readable size
        $manifest['stats']['total_size_human'] = $this->formatSize($manifest['stats']['total_size']);
        
        // Group by directory if requested
        if ($options['group_by_directory']) {
            $manifest['files']['by_directory'] = $this->groupByDirectory($manifest['files']['list']);
        }
        
        return $manifest;
    }
    
    /**
     * Group files by directory
     * 
     * @param array $files File list
     * @return array Grouped files
     */
    private function groupByDirectory($files) {
        $grouped = [];
        
        foreach ($files as $file) {
            $dir = dirname($file['path']);
            if (!isset($grouped[$dir])) {
                $grouped[$dir] = [];
            }
            $grouped[$dir][] = $file;
        }
        
        return $grouped;
    }
    
    /**
     * Format file size to human-readable
     * 
     * @param int $bytes Bytes
     * @return string Formatted size
     */
    private function formatSize($bytes) {
        $units = ['B', 'KB', 'MB', 'GB', 'TB'];
        $index = 0;
        
        while ($bytes >= 1024 && $index < count($units) - 1) {
            $bytes /= 1024;
            $index++;
        }
        
        return round($bytes, 2) . ' ' . $units[$index];
    }
    
    /**
     * Compare file metadata
     * 
     * @param string $file1 First file
     * @param string $file2 Second file
     * @return array Comparison result
     */
    public function compare($file1, $file2) {
        $meta1 = $this->extract($file1);
        $meta2 = $this->extract($file2);
        
        if (isset($meta1['error']) || isset($meta2['error'])) {
            return ['error' => 'Failed to extract metadata'];
        }
        
        return [
            'identical' => $meta1['checksum'] === $meta2['checksum'],
            'size_difference' => $meta1['size'] - $meta2['size'],
            'newer_file' => $meta1['modified'] > $meta2['modified'] ? $file1 : $file2,
            'metadata' => [
                'file1' => $meta1,
                'file2' => $meta2
            ]
        ];
    }
}
