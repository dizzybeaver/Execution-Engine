<?php
/**
 * integrity_validator.php
 * 
 * File Integrity Validation Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use ValidationModule API
 */

class IntegrityValidator {
    private $config;
    private $checksumCache = [];
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Validate file integrity
     */
    public function validate($filePath, $expectedChecksum, $algorithm = 'md5') {
        if (!$this->config['integrity']['enabled']) {
            return ['valid' => true];
        }
        
        if (!file_exists($filePath)) {
            return [
                'valid' => false,
                'error' => 'File does not exist'
            ];
        }
        
        // Validate algorithm
        if (!in_array($algorithm, $this->config['integrity']['algorithms'])) {
            return [
                'valid' => false,
                'error' => "Unsupported algorithm: {$algorithm}"
            ];
        }
        
        // Calculate checksum
        $actualChecksum = $this->calculateChecksum($filePath, $algorithm);
        
        // Compare
        $match = hash_equals(
            strtolower($expectedChecksum),
            strtolower($actualChecksum)
        );
        
        return [
            'valid' => $match,
            'expected' => $expectedChecksum,
            'actual' => $actualChecksum,
            'algorithm' => $algorithm
        ];
    }
    
    /**
     * Calculate checksum
     */
    public function calculateChecksum($filePath, $algorithm = null) {
        if ($algorithm === null) {
            $algorithm = $this->config['integrity']['default_algorithm'];
        }
        
        // Check cache
        if ($this->config['integrity']['cache_checksums']) {
            $cacheKey = $filePath . ':' . $algorithm;
            
            if (isset($this->checksumCache[$cacheKey])) {
                return $this->checksumCache[$cacheKey];
            }
        }
        
        // Calculate checksum
        $checksum = hash_file($algorithm, $filePath);
        
        // Cache if enabled
        if ($this->config['integrity']['cache_checksums']) {
            $this->checksumCache[$cacheKey] = $checksum;
        }
        
        return $checksum;
    }
    
    /**
     * Verify multiple files
     */
    public function verifyBatch($files, $algorithm = 'md5') {
        $results = [
            'valid' => [],
            'invalid' => [],
            'errors' => []
        ];
        
        foreach ($files as $file) {
            $path = $file['path'] ?? '';
            $expectedChecksum = $file['checksum'] ?? '';
            
            if (!$path || !$expectedChecksum) {
                $results['errors'][] = [
                    'path' => $path,
                    'error' => 'Missing path or checksum'
                ];
                continue;
            }
            
            $result = $this->validate($path, $expectedChecksum, $algorithm);
            
            if ($result['valid']) {
                $results['valid'][] = $path;
            } else {
                $results['invalid'][] = [
                    'path' => $path,
                    'expected' => $result['expected'] ?? '',
                    'actual' => $result['actual'] ?? '',
                    'error' => $result['error'] ?? 'Checksum mismatch'
                ];
            }
        }
        
        return $results;
    }
    
    /**
     * Generate checksum manifest
     */
    public function generateManifest($files, $algorithm = 'md5') {
        $manifest = [];
        
        foreach ($files as $file) {
            $path = is_array($file) ? ($file['path'] ?? '') : $file;
            
            if (!$path || !file_exists($path)) {
                continue;
            }
            
            $checksum = $this->calculateChecksum($path, $algorithm);
            
            $manifest[] = [
                'path' => $path,
                'checksum' => $checksum,
                'algorithm' => $algorithm,
                'size' => filesize($path),
                'modified' => filemtime($path)
            ];
        }
        
        return $manifest;
    }
    
    /**
     * Compare file against manifest
     */
    public function verifyAgainstManifest($filePath, $manifest) {
        foreach ($manifest as $entry) {
            if ($entry['path'] === $filePath) {
                return $this->validate(
                    $filePath,
                    $entry['checksum'],
                    $entry['algorithm'] ?? 'md5'
                );
            }
        }
        
        return [
            'valid' => false,
            'error' => 'File not found in manifest'
        ];
    }
    
    /**
     * Clear checksum cache
     */
    public function clearCache() {
        $this->checksumCache = [];
    }
    
    /**
     * Get cached checksums
     */
    public function getCachedChecksums() {
        return $this->checksumCache;
    }
    
    /**
     * Compare two files
     */
    public function compareFiles($file1, $file2, $algorithm = 'md5') {
        if (!file_exists($file1) || !file_exists($file2)) {
            return [
                'identical' => false,
                'error' => 'One or both files do not exist'
            ];
        }
        
        $checksum1 = $this->calculateChecksum($file1, $algorithm);
        $checksum2 = $this->calculateChecksum($file2, $algorithm);
        
        return [
            'identical' => $checksum1 === $checksum2,
            'checksum1' => $checksum1,
            'checksum2' => $checksum2,
            'algorithm' => $algorithm
        ];
    }
    
    /**
     * Verify file hasn't changed
     */
    public function verifyUnchanged($filePath, $previousChecksum, $algorithm = 'md5') {
        return $this->validate($filePath, $previousChecksum, $algorithm);
    }
}
?>
