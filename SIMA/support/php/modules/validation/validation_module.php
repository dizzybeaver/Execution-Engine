<?php
/**
 * validation_module.php
 * 
 * SIMA Validation Module - Public API
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Public interface for validation and security checking
 */

class ValidationModule {
    private $config;
    private $pathValidator;
    private $securityValidator;
    private $integrityValidator;
    private $contentValidator;
    
    /**
     * Initialize validation module
     * 
     * @param array|string $config Config array or path to config file
     */
    public function __construct($config = null) {
        // Load configuration
        if (is_string($config) && file_exists($config)) {
            $this->config = require $config;
        } elseif (is_array($config)) {
            $this->config = $config;
        } else {
            $this->config = require __DIR__ . '/validation_config.php';
        }
        
        // Load internal components
        require_once __DIR__ . '/internal/path_validator.php';
        require_once __DIR__ . '/internal/security_validator.php';
        require_once __DIR__ . '/internal/integrity_validator.php';
        require_once __DIR__ . '/internal/content_validator.php';
        
        $this->pathValidator = new PathValidator($this->config);
        $this->securityValidator = new SecurityValidator($this->config);
        $this->integrityValidator = new IntegrityValidator($this->config);
        $this->contentValidator = new ContentValidator($this->config);
    }
    
    /**
     * Validate path
     * 
     * @param string $path Path to validate
     * @param string $baseDir Base directory for validation
     * @return array Validation result
     */
    public function validatePath($path, $baseDir = null) {
        return $this->pathValidator->validate($path, $baseDir);
    }
    
    /**
     * Sanitize path
     * 
     * @param string $path Path to sanitize
     * @return string Sanitized path
     */
    public function sanitizePath($path) {
        return $this->pathValidator->sanitize($path);
    }
    
    /**
     * Prevent directory traversal
     * 
     * @param string $path Path to check
     * @param string $baseDir Base directory
     * @return bool True if safe
     */
    public function preventTraversal($path, $baseDir) {
        return $this->securityValidator->preventTraversal($path, $baseDir);
    }
    
    /**
     * Check for dangerous patterns
     * 
     * @param string $path Path to check
     * @return array Check result
     */
    public function checkDangerousPatterns($path) {
        return $this->securityValidator->checkDangerousPatterns($path);
    }
    
    /**
     * Validate file extension
     * 
     * @param string $filename Filename to check
     * @param array $allowedExtensions Allowed extensions
     * @return bool True if allowed
     */
    public function validateExtension($filename, $allowedExtensions = null) {
        return $this->securityValidator->validateExtension($filename, $allowedExtensions);
    }
    
    /**
     * Validate REF-ID format
     * 
     * @param string $refId REF-ID to validate
     * @return array Validation result
     */
    public function validateRefId($refId) {
        return $this->contentValidator->validateRefId($refId);
    }
    
    /**
     * Validate file integrity
     * 
     * @param string $filePath File path
     * @param string $expectedChecksum Expected checksum
     * @param string $algorithm Checksum algorithm
     * @return array Validation result
     */
    public function validateIntegrity($filePath, $expectedChecksum, $algorithm = 'md5') {
        return $this->integrityValidator->validate($filePath, $expectedChecksum, $algorithm);
    }
    
    /**
     * Calculate checksum
     * 
     * @param string $filePath File path
     * @param string $algorithm Algorithm (md5, sha256)
     * @return string Checksum
     */
    public function calculateChecksum($filePath, $algorithm = 'md5') {
        return $this->integrityValidator->calculateChecksum($filePath, $algorithm);
    }
    
    /**
     * Validate file structure
     * 
     * @param string $filePath File path
     * @return array Validation result
     */
    public function validateFileStructure($filePath) {
        return $this->contentValidator->validateStructure($filePath);
    }
    
    /**
     * Validate cross-references
     * 
     * @param array $files File list
     * @return array Validation result
     */
    public function validateCrossReferences($files) {
        return $this->contentValidator->validateCrossReferences($files);
    }
    
    /**
     * Find duplicates
     * 
     * @param array $files File list
     * @param string $criteria Criteria (filename, refid, checksum)
     * @return array Duplicate groups
     */
    public function findDuplicates($files, $criteria = 'filename') {
        return $this->contentValidator->findDuplicates($files, $criteria);
    }
    
    /**
     * Validate batch of files
     * 
     * @param array $files File list
     * @param array $options Validation options
     * @return array Validation results
     */
    public function validateBatch($files, $options = []) {
        $results = [
            'valid' => [],
            'invalid' => [],
            'warnings' => []
        ];
        
        foreach ($files as $file) {
            $path = $file['path'] ?? $file;
            $validation = $this->validateAll($path, $options);
            
            if ($validation['valid']) {
                $results['valid'][] = $path;
            } else {
                $results['invalid'][] = [
                    'path' => $path,
                    'errors' => $validation['errors']
                ];
            }
            
            if (!empty($validation['warnings'])) {
                $results['warnings'][] = [
                    'path' => $path,
                    'warnings' => $validation['warnings']
                ];
            }
        }
        
        return $results;
    }
    
    /**
     * Validate all aspects of a file
     * 
     * @param string $filePath File path
     * @param array $options Validation options
     * @return array Comprehensive validation result
     */
    public function validateAll($filePath, $options = []) {
        $errors = [];
        $warnings = [];
        
        // Path validation
        if ($options['validate_path'] ?? true) {
            $pathResult = $this->validatePath($filePath, $options['base_dir'] ?? null);
            if (!$pathResult['valid']) {
                $errors = array_merge($errors, $pathResult['errors']);
            }
        }
        
        // Security validation
        if ($options['validate_security'] ?? true) {
            $securityResult = $this->checkDangerousPatterns($filePath);
            if (!$securityResult['safe']) {
                $errors = array_merge($errors, $securityResult['issues']);
            }
        }
        
        // File existence
        if (!file_exists($filePath)) {
            $errors[] = 'File does not exist';
            
            return [
                'valid' => false,
                'errors' => $errors,
                'warnings' => $warnings
            ];
        }
        
        // Structure validation
        if ($options['validate_structure'] ?? true) {
            $structureResult = $this->validateFileStructure($filePath);
            if (!$structureResult['valid']) {
                $errors = array_merge($errors, $structureResult['errors']);
            }
            if (!empty($structureResult['warnings'])) {
                $warnings = array_merge($warnings, $structureResult['warnings']);
            }
        }
        
        // Integrity validation
        if (isset($options['expected_checksum'])) {
            $integrityResult = $this->validateIntegrity(
                $filePath,
                $options['expected_checksum'],
                $options['checksum_algorithm'] ?? 'md5'
            );
            
            if (!$integrityResult['valid']) {
                $errors[] = 'Checksum mismatch';
            }
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors,
            'warnings' => $warnings
        ];
    }
    
    /**
     * Check file permissions
     * 
     * @param string $filePath File path
     * @param string $requiredPermission Required permission (read, write, execute)
     * @return bool True if has permission
     */
    public function checkPermission($filePath, $requiredPermission = 'read') {
        return $this->securityValidator->checkPermission($filePath, $requiredPermission);
    }
    
    /**
     * Validate upload
     * 
     * @param array $fileData $_FILES array data
     * @return array Validation result
     */
    public function validateUpload($fileData) {
        return $this->securityValidator->validateUpload($fileData);
    }
    
    /**
     * Get configuration value
     * 
     * @param string $key Config key (dot notation supported)
     * @param mixed $default Default value
     * @return mixed Config value
     */
    public function getConfig($key, $default = null) {
        $keys = explode('.', $key);
        $value = $this->config;
        
        foreach ($keys as $k) {
            if (!isset($value[$k])) {
                return $default;
            }
            $value = $value[$k];
        }
        
        return $value;
    }
    
    /**
     * Set configuration value
     * 
     * @param string $key Config key
     * @param mixed $value Config value
     */
    public function setConfig($key, $value) {
        $this->config[$key] = $value;
        
        // Update component configs
        if ($this->pathValidator) {
            $this->pathValidator->updateConfig($this->config);
        }
        if ($this->securityValidator) {
            $this->securityValidator->updateConfig($this->config);
        }
        if ($this->integrityValidator) {
            $this->integrityValidator->updateConfig($this->config);
        }
        if ($this->contentValidator) {
            $this->contentValidator->updateConfig($this->config);
        }
    }
}
?>
