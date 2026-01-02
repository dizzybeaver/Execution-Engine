<?php
/**
 * file-validator.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-27
 * Purpose: File and path validation operations
 * Project: SIMA File Module
 * 
 * ADDED: Complete validation functionality
 */

class FileValidator {
    
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    /**
     * Validate file path
     * 
     * @param string $path Path to validate
     * @return bool Valid or not
     */
    public function isValidPath($path) {
        if (!$this->config['validate_paths']) {
            return true;
        }
        
        // Check path length
        if (strlen($path) > $this->config['max_path_length']) {
            return false;
        }
        
        // Check for null bytes
        if (strpos($path, "\0") !== false) {
            return false;
        }
        
        // Prevent directory traversal
        if ($this->config['prevent_traversal']) {
            if (strpos($path, '..') !== false) {
                return false;
            }
        }
        
        // Validate against base directory
        $realPath = realpath($path);
        if ($realPath === false && !$this->config['verify_existence']) {
            // Path doesn't exist but we don't require it to
            $realPath = $path;
        }
        
        if ($realPath !== false) {
            $basePath = realpath($this->config['base_directory']);
            if ($basePath !== false && strpos($realPath, $basePath) !== 0) {
                return false;
            }
        }
        
        // Check allowed characters
        if (!preg_match($this->config['allowed_path_chars'], $path)) {
            return false;
        }
        
        return true;
    }
    
    /**
     * Validate file exists and is accessible
     * 
     * @param string $filePath File path
     * @return bool Valid or not
     */
    public function isValidFile($filePath) {
        if (!$this->isValidPath($filePath)) {
            return false;
        }
        
        if ($this->config['verify_existence'] && !file_exists($filePath)) {
            return false;
        }
        
        if (file_exists($filePath) && !is_file($filePath)) {
            return false;
        }
        
        if ($this->config['check_permissions'] && !is_readable($filePath)) {
            return false;
        }
        
        // Check dangerous extensions
        $ext = '.' . pathinfo($filePath, PATHINFO_EXTENSION);
        if (in_array($ext, $this->config['dangerous_extensions'])) {
            return false;
        }
        
        return true;
    }
    
    /**
     * Validate archive file
     * 
     * @param string $archivePath Archive path
     * @return bool Valid or not
     */
    public function isValidArchive($archivePath) {
        if (!$this->isValidFile($archivePath)) {
            return false;
        }
        
        $ext = pathinfo($archivePath, PATHINFO_EXTENSION);
        
        if (!in_array($ext, ['zip', 'tar', 'gz'])) {
            return false;
        }
        
        return true;
    }
    
    /**
     * Validate list of files
     * 
     * @param array $files File paths
     * @return bool Valid or not
     */
    public function validateFileList($files) {
        if (!is_array($files) || empty($files)) {
            return false;
        }
        
        foreach ($files as $file) {
            if (!$this->isValidFile($file)) {
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Check file integrity via checksum
     * 
     * @param string $filePath File path
     * @param string $expectedChecksum Expected checksum
     * @param string $algorithm Hash algorithm
     * @return bool Integrity valid
     */
    public function checkIntegrity($filePath, $expectedChecksum, $algorithm = null) {
        if (!$this->isValidFile($filePath)) {
            return false;
        }
        
        if ($algorithm === null) {
            $algorithm = $this->config['checksum_algorithm'];
        }
        
        $actualChecksum = hash_file($algorithm, $filePath);
        
        return hash_equals(strtolower($expectedChecksum), strtolower($actualChecksum));
    }
    
    /**
     * Verify archive integrity
     * 
     * @param string $archivePath Archive path
     * @return array Verification results
     */
    public function verifyArchive($archivePath) {
        if (!$this->isValidArchive($archivePath)) {
            return ['error' => 'Invalid archive'];
        }
        
        $zip = new ZipArchive();
        
        if ($zip->open($archivePath, ZipArchive::CHECKCONS) !== true) {
            return [
                'valid' => false,
                'error' => 'Archive integrity check failed'
            ];
        }
        
        $errors = [];
        
        for ($i = 0; $i < $zip->numFiles; $i++) {
            $stat = $zip->statIndex($i);
            
            // Verify CRC
            $content = $zip->getFromIndex($i);
            if ($content === false) {
                $errors[] = [
                    'file' => $stat['name'],
                    'error' => 'Failed to read file'
                ];
                continue;
            }
            
            $calculatedCrc = crc32($content);
            if ($calculatedCrc !== $stat['crc']) {
                $errors[] = [
                    'file' => $stat['name'],
                    'error' => 'CRC mismatch',
                    'expected' => $stat['crc'],
                    'actual' => $calculatedCrc
                ];
            }
        }
        
        $zip->close();
        
        return [
            'valid' => empty($errors),
            'errors' => $errors,
            'files_checked' => $zip->numFiles
        ];
    }
    
    /**
     * Sanitize filename
     * 
     * @param string $filename Filename to sanitize
     * @return string Sanitized filename
     */
    public function sanitizeFilename($filename) {
        if (!$this->config['sanitize_filenames']) {
            return $filename;
        }
        
        // Remove directory separators
        $filename = str_replace(['/', '\\'], '', $filename);
        
        // Remove null bytes
        $filename = str_replace("\0", '', $filename);
        
        // Remove dangerous characters
        $filename = preg_replace('/[^a-zA-Z0-9\._\-]/', '_', $filename);
        
        // Enforce length limit
        if (strlen($filename) > $this->config['max_filename_length']) {
            $ext = pathinfo($filename, PATHINFO_EXTENSION);
            $name = pathinfo($filename, PATHINFO_FILENAME);
            $maxNameLength = $this->config['max_filename_length'] - strlen($ext) - 1;
            $filename = substr($name, 0, $maxNameLength) . '.' . $ext;
        }
        
        return $filename;
    }
    
    /**
     * Check if operation is permitted
     * 
     * @param string $operation Operation type (read, write, delete)
     * @param string $path Target path
     * @return array Permission result
     */
    public function checkPermission($operation, $path) {
        if (!$this->config['check_permissions']) {
            return ['allowed' => true];
        }
        
        if (!$this->isValidPath($path)) {
            return [
                'allowed' => false,
                'reason' => 'Invalid path'
            ];
        }
        
        $exists = file_exists($path);
        
        switch ($operation) {
            case 'read':
                if (!$exists) {
                    return ['allowed' => false, 'reason' => 'File does not exist'];
                }
                if (!is_readable($path)) {
                    return ['allowed' => false, 'reason' => 'File not readable'];
                }
                break;
                
            case 'write':
                if ($exists && !is_writable($path)) {
                    return ['allowed' => false, 'reason' => 'File not writable'];
                }
                $dir = dirname($path);
                if (!is_writable($dir)) {
                    return ['allowed' => false, 'reason' => 'Directory not writable'];
                }
                break;
                
            case 'delete':
                if (!$exists) {
                    return ['allowed' => false, 'reason' => 'File does not exist'];
                }
                if (!is_writable(dirname($path))) {
                    return ['allowed' => false, 'reason' => 'Cannot delete file'];
                }
                break;
                
            default:
                return ['allowed' => false, 'reason' => 'Unknown operation'];
        }
        
        return ['allowed' => true];
    }
    
    /**
     * Validate directory for operations
     * 
     * @param string $directory Directory path
     * @param bool $mustExist Must exist
     * @param bool $mustBeWritable Must be writable
     * @return array Validation result
     */
    public function validateDirectory($directory, $mustExist = true, $mustBeWritable = false) {
        if (!$this->isValidPath($directory)) {
            return [
                'valid' => false,
                'error' => 'Invalid directory path'
            ];
        }
        
        if ($mustExist && !is_dir($directory)) {
            return [
                'valid' => false,
                'error' => 'Directory does not exist'
            ];
        }
        
        if ($mustBeWritable && !is_writable($directory)) {
            return [
                'valid' => false,
                'error' => 'Directory not writable'
            ];
        }
        
        return ['valid' => true];
    }
}
