<?php
/**
 * path_validator.php
 * 
 * Path Validation Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use ValidationModule API
 */

class PathValidator {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Validate path
     */
    public function validate($path, $baseDir = null) {
        $errors = [];
        $cfg = $this->config['path'];
        
        // Check length
        if (strlen($path) > $cfg['max_length']) {
            $errors[] = "Path exceeds maximum length ({$cfg['max_length']} characters)";
        }
        
        // Check absolute/relative
        if ($this->isAbsolute($path) && !$cfg['allow_absolute']) {
            $errors[] = 'Absolute paths not allowed';
        }
        
        if (!$this->isAbsolute($path) && !$cfg['allow_relative']) {
            $errors[] = 'Relative paths not allowed';
        }
        
        // Check for null bytes
        if (strpos($path, "\0") !== false) {
            $errors[] = 'Path contains null bytes';
        }
        
        // Check separators
        $validSeparators = $cfg['allowed_separators'];
        $pathSeparators = $this->getSeparators($path);
        
        foreach ($pathSeparators as $sep) {
            if (!in_array($sep, $validSeparators)) {
                $errors[] = "Invalid path separator: {$sep}";
            }
        }
        
        // Validate against base directory if provided
        if ($baseDir && $this->config['traversal']['enabled']) {
            require_once __DIR__ . '/security_validator.php';
            $secValidator = new SecurityValidator($this->config);
            
            if (!$secValidator->preventTraversal($path, $baseDir)) {
                $errors[] = 'Path attempts directory traversal';
            }
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors
        ];
    }
    
    /**
     * Sanitize path
     */
    public function sanitize($path) {
        // Remove null bytes
        $path = str_replace("\0", '', $path);
        
        // Normalize separators to forward slash
        $path = str_replace('\\', '/', $path);
        
        // Remove duplicate slashes
        $path = preg_replace('#/+#', '/', $path);
        
        // Remove leading ./
        $path = preg_replace('#^\./#', '', $path);
        
        // Normalize if configured
        if ($this->config['path']['normalize']) {
            $path = $this->normalizePath($path);
        }
        
        return $path;
    }
    
    /**
     * Normalize path
     */
    private function normalizePath($path) {
        $parts = explode('/', $path);
        $normalized = [];
        
        foreach ($parts as $part) {
            if ($part === '' || $part === '.') {
                continue;
            }
            
            if ($part === '..') {
                if (count($normalized) > 0) {
                    array_pop($normalized);
                }
            } else {
                $normalized[] = $part;
            }
        }
        
        return implode('/', $normalized);
    }
    
    /**
     * Check if path is absolute
     */
    private function isAbsolute($path) {
        // Unix absolute path
        if (substr($path, 0, 1) === '/') {
            return true;
        }
        
        // Windows absolute path
        if (preg_match('/^[A-Z]:/i', $path)) {
            return true;
        }
        
        return false;
    }
    
    /**
     * Get separators used in path
     */
    private function getSeparators($path) {
        $separators = [];
        
        if (strpos($path, '/') !== false) {
            $separators[] = '/';
        }
        
        if (strpos($path, '\\') !== false) {
            $separators[] = '\\';
        }
        
        return $separators;
    }
    
    /**
     * Resolve path relative to base
     */
    public function resolvePath($path, $baseDir) {
        // Sanitize both paths
        $path = $this->sanitize($path);
        $baseDir = $this->sanitize($baseDir);
        
        // If path is absolute, return as-is
        if ($this->isAbsolute($path)) {
            return $path;
        }
        
        // Combine and normalize
        $combined = $baseDir . '/' . $path;
        return $this->normalizePath($combined);
    }
    
    /**
     * Check if path is within base directory
     */
    public function isWithinBase($path, $baseDir) {
        $resolvedPath = $this->resolvePath($path, $baseDir);
        $normalizedBase = $this->normalizePath($baseDir);
        
        // Check if resolved path starts with base directory
        return strpos($resolvedPath, $normalizedBase) === 0;
    }
    
    /**
     * Extract filename from path
     */
    public function getFilename($path) {
        $path = $this->sanitize($path);
        return basename($path);
    }
    
    /**
     * Extract directory from path
     */
    public function getDirectory($path) {
        $path = $this->sanitize($path);
        return dirname($path);
    }
    
    /**
     * Extract extension from path
     */
    public function getExtension($path) {
        $filename = $this->getFilename($path);
        return pathinfo($filename, PATHINFO_EXTENSION);
    }
    
    /**
     * Validate filename
     */
    public function validateFilename($filename) {
        $errors = [];
        
        // Check for dangerous characters
        $dangerousChars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', "\0"];
        
        foreach ($dangerousChars as $char) {
            if (strpos($filename, $char) !== false) {
                $errors[] = "Filename contains dangerous character: {$char}";
            }
        }
        
        // Check length
        if (strlen($filename) > 255) {
            $errors[] = 'Filename exceeds 255 characters';
        }
        
        // Check for reserved names (Windows)
        $reserved = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1'];
        $nameWithoutExt = pathinfo($filename, PATHINFO_FILENAME);
        
        if (in_array(strtoupper($nameWithoutExt), $reserved)) {
            $errors[] = 'Filename uses reserved name';
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors
        ];
    }
}
?>
