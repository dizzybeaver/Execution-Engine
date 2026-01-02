<?php
/**
 * security_validator.php
 * 
 * Security Validation Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use ValidationModule API
 */

class SecurityValidator {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Prevent directory traversal
     */
    public function preventTraversal($path, $baseDir) {
        if (!$this->config['traversal']['enabled']) {
            return true;
        }
        
        // Normalize paths
        $path = str_replace('\\', '/', $path);
        $baseDir = str_replace('\\', '/', $baseDir);
        
        // Remove trailing slashes
        $baseDir = rtrim($baseDir, '/');
        
        // Check for blocked patterns
        foreach ($this->config['traversal']['blocked_patterns'] as $pattern) {
            if (stripos($path, $pattern) !== false) {
                return false;
            }
        }
        
        // Resolve real path
        if (file_exists($path)) {
            $realPath = realpath($path);
            $realBase = realpath($baseDir);
            
            if ($realPath === false || $realBase === false) {
                return false;
            }
            
            // Check if real path is within base
            if (strpos($realPath, $realBase) !== 0) {
                return false;
            }
        } else {
            // For non-existent paths, check normalized version
            $normalized = $this->normalizePath($baseDir . '/' . $path);
            $normalizedBase = $this->normalizePath($baseDir);
            
            if (strpos($normalized, $normalizedBase) !== 0) {
                return false;
            }
        }
        
        // Check symlinks if not allowed
        if (!$this->config['traversal']['allow_symlinks'] && file_exists($path)) {
            if (is_link($path)) {
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Normalize path for comparison
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
        
        return '/' . implode('/', $normalized);
    }
    
    /**
     * Check for dangerous patterns
     */
    public function checkDangerousPatterns($path) {
        $issues = [];
        
        if (!$this->config['security']['check_dangerous_patterns']) {
            return ['safe' => true, 'issues' => []];
        }
        
        $filename = basename($path);
        
        // Check extension
        $ext = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
        
        if (in_array($ext, $this->config['dangerous_extensions'])) {
            $issues[] = "Dangerous file extension: {$ext}";
        }
        
        // Check content if file exists
        if (file_exists($path) && is_readable($path)) {
            $content = file_get_contents($path);
            
            foreach ($this->config['dangerous_patterns'] as $pattern) {
                if (preg_match($pattern, $content)) {
                    $issues[] = "Dangerous pattern found: {$pattern}";
                }
            }
        }
        
        return [
            'safe' => empty($issues),
            'issues' => $issues
        ];
    }
    
    /**
     * Validate file extension
     */
    public function validateExtension($filename, $allowedExtensions = null) {
        if (!$this->config['security']['check_dangerous_extensions']) {
            return true;
        }
        
        $ext = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
        
        // Use provided list or config list
        $allowed = $allowedExtensions ?? $this->config['allowed_extensions'];
        
        return in_array($ext, $allowed);
    }
    
    /**
     * Check file size
     */
    public function checkFileSize($filePath) {
        if (!$this->config['security']['check_file_size']) {
            return ['valid' => true];
        }
        
        if (!file_exists($filePath)) {
            return [
                'valid' => false,
                'error' => 'File does not exist'
            ];
        }
        
        $size = filesize($filePath);
        $maxSize = $this->config['security']['max_file_size'];
        
        if ($size > $maxSize) {
            return [
                'valid' => false,
                'error' => "File size ({$size} bytes) exceeds maximum ({$maxSize} bytes)"
            ];
        }
        
        return ['valid' => true, 'size' => $size];
    }
    
    /**
     * Check file permissions
     */
    public function checkPermission($filePath, $requiredPermission = 'read') {
        if (!file_exists($filePath)) {
            return false;
        }
        
        switch ($requiredPermission) {
            case 'read':
                return is_readable($filePath);
                
            case 'write':
                return is_writable($filePath);
                
            case 'execute':
                return is_executable($filePath);
                
            default:
                return false;
        }
    }
    
    /**
     * Validate upload
     */
    public function validateUpload($fileData) {
        $errors = [];
        $cfg = $this->config['upload'];
        
        if (!$cfg['enabled']) {
            return ['valid' => true];
        }
        
        // Check upload errors
        if (isset($fileData['error']) && $fileData['error'] !== UPLOAD_ERR_OK) {
            $errors[] = $this->getUploadErrorMessage($fileData['error']);
        }
        
        // Check file size
        if (isset($fileData['size']) && $fileData['size'] > $cfg['max_size']) {
            $errors[] = "File size exceeds maximum ({$cfg['max_size']} bytes)";
        }
        
        // Check extension
        if (isset($fileData['name'])) {
            $ext = strtolower(pathinfo($fileData['name'], PATHINFO_EXTENSION));
            
            if (!in_array($ext, $cfg['allowed_extensions'])) {
                $errors[] = "File extension not allowed: {$ext}";
            }
        }
        
        // Check MIME type
        if ($cfg['check_mime_type'] && isset($fileData['type'])) {
            if (!in_array($fileData['type'], $cfg['allowed_mime_types'])) {
                $errors[] = "MIME type not allowed: {$fileData['type']}";
            }
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors
        ];
    }
    
    /**
     * Get upload error message
     */
    private function getUploadErrorMessage($errorCode) {
        $messages = [
            UPLOAD_ERR_INI_SIZE => 'File exceeds upload_max_filesize',
            UPLOAD_ERR_FORM_SIZE => 'File exceeds MAX_FILE_SIZE',
            UPLOAD_ERR_PARTIAL => 'File was only partially uploaded',
            UPLOAD_ERR_NO_FILE => 'No file was uploaded',
            UPLOAD_ERR_NO_TMP_DIR => 'Missing temporary folder',
            UPLOAD_ERR_CANT_WRITE => 'Failed to write file to disk',
            UPLOAD_ERR_EXTENSION => 'Upload stopped by extension'
        ];
        
        return $messages[$errorCode] ?? 'Unknown upload error';
    }
    
    /**
     * Sanitize filename for security
     */
    public function sanitizeFilename($filename) {
        // Remove directory separators
        $filename = str_replace(['/', '\\'], '', $filename);
        
        // Remove null bytes
        $filename = str_replace("\0", '', $filename);
        
        // Remove dangerous characters
        $filename = preg_replace('/[<>:"|?*]/', '', $filename);
        
        // Limit length
        if (strlen($filename) > 255) {
            $ext = pathinfo($filename, PATHINFO_EXTENSION);
            $name = pathinfo($filename, PATHINFO_FILENAME);
            $name = substr($name, 0, 255 - strlen($ext) - 1);
            $filename = $name . '.' . $ext;
        }
        
        return $filename;
    }
}
?>
