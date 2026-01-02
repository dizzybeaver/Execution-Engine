<?php
/**
 * file-utils.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-27
 * Purpose: File operation utilities
 * Project: SIMA File Module
 * 
 * ADDED: Complete file utilities
 */

class FileUtils {
    
    /**
     * Copy files to destination
     * 
     * @param array $files Source files
     * @param string $destination Destination directory
     * @param array $options Copy options
     * @return array Result
     */
    public static function copyFiles($files, $destination, $options = []) {
        $options = array_merge([
            'overwrite' => false,
            'preserve_structure' => false,
            'base_path' => null
        ], $options);
        
        if (!is_dir($destination)) {
            mkdir($destination, 0755, true);
        }
        
        $copied = [];
        $skipped = [];
        $failed = [];
        
        foreach ($files as $file) {
            if (!file_exists($file)) {
                $failed[] = ['file' => $file, 'reason' => 'Source not found'];
                continue;
            }
            
            $targetPath = self::getTargetPath($file, $destination, $options);
            
            // Check if exists
            if (file_exists($targetPath) && !$options['overwrite']) {
                $skipped[] = $file;
                continue;
            }
            
            // Create parent directory
            $parentDir = dirname($targetPath);
            if (!is_dir($parentDir)) {
                mkdir($parentDir, 0755, true);
            }
            
            // Copy file
            if (copy($file, $targetPath)) {
                $copied[] = $file;
            } else {
                $failed[] = ['file' => $file, 'reason' => 'Copy failed'];
            }
        }
        
        return [
            'success' => true,
            'copied' => count($copied),
            'skipped' => count($skipped),
            'failed' => count($failed),
            'files' => $copied,
            'skipped_files' => $skipped,
            'failed_files' => $failed
        ];
    }
    
    /**
     * Move files to destination
     * 
     * @param array $files Source files
     * @param string $destination Destination directory
     * @param array $options Move options
     * @return array Result
     */
    public static function moveFiles($files, $destination, $options = []) {
        $options = array_merge([
            'overwrite' => false,
            'preserve_structure' => false,
            'base_path' => null
        ], $options);
        
        if (!is_dir($destination)) {
            mkdir($destination, 0755, true);
        }
        
        $moved = [];
        $skipped = [];
        $failed = [];
        
        foreach ($files as $file) {
            if (!file_exists($file)) {
                $failed[] = ['file' => $file, 'reason' => 'Source not found'];
                continue;
            }
            
            $targetPath = self::getTargetPath($file, $destination, $options);
            
            // Check if exists
            if (file_exists($targetPath) && !$options['overwrite']) {
                $skipped[] = $file;
                continue;
            }
            
            // Create parent directory
            $parentDir = dirname($targetPath);
            if (!is_dir($parentDir)) {
                mkdir($parentDir, 0755, true);
            }
            
            // Move file
            if (rename($file, $targetPath)) {
                $moved[] = $file;
            } else {
                $failed[] = ['file' => $file, 'reason' => 'Move failed'];
            }
        }
        
        return [
            'success' => true,
            'moved' => count($moved),
            'skipped' => count($skipped),
            'failed' => count($failed),
            'files' => $moved,
            'skipped_files' => $skipped,
            'failed_files' => $failed
        ];
    }
    
    /**
     * Delete files
     * 
     * @param array $files Files to delete
     * @param array $options Delete options
     * @return array Result
     */
    public static function deleteFiles($files, $options = []) {
        $options = array_merge([
            'confirm' => true
        ], $options);
        
        if ($options['confirm'] === false) {
            return ['error' => 'Delete operation requires confirmation'];
        }
        
        $deleted = [];
        $failed = [];
        
        foreach ($files as $file) {
            if (!file_exists($file)) {
                $failed[] = ['file' => $file, 'reason' => 'File not found'];
                continue;
            }
            
            if (unlink($file)) {
                $deleted[] = $file;
            } else {
                $failed[] = ['file' => $file, 'reason' => 'Delete failed'];
            }
        }
        
        return [
            'success' => true,
            'deleted' => count($deleted),
            'failed' => count($failed),
            'files' => $deleted,
            'failed_files' => $failed
        ];
    }
    
    /**
     * Get target path for file operation
     * 
     * @param string $sourcePath Source file path
     * @param string $destination Destination directory
     * @param array $options Options
     * @return string Target path
     */
    private static function getTargetPath($sourcePath, $destination, $options) {
        if (!$options['preserve_structure']) {
            return $destination . DIRECTORY_SEPARATOR . basename($sourcePath);
        }
        
        // Preserve directory structure
        if ($options['base_path']) {
            $relativePath = str_replace($options['base_path'] . DIRECTORY_SEPARATOR, '', $sourcePath);
            return $destination . DIRECTORY_SEPARATOR . $relativePath;
        }
        
        return $destination . DIRECTORY_SEPARATOR . basename($sourcePath);
    }
    
    /**
     * Create directory if not exists
     * 
     * @param string $directory Directory path
     * @param int $permissions Directory permissions
     * @return bool Success
     */
    public static function ensureDirectory($directory, $permissions = 0755) {
        if (is_dir($directory)) {
            return true;
        }
        
        return mkdir($directory, $permissions, true);
    }
    
    /**
     * Remove directory recursively
     * 
     * @param string $directory Directory path
     * @return bool Success
     */
    public static function removeDirectory($directory) {
        if (!is_dir($directory)) {
            return false;
        }
        
        $items = scandir($directory);
        
        foreach ($items as $item) {
            if ($item === '.' || $item === '..') {
                continue;
            }
            
            $path = $directory . DIRECTORY_SEPARATOR . $item;
            
            if (is_dir($path)) {
                self::removeDirectory($path);
            } else {
                unlink($path);
            }
        }
        
        return rmdir($directory);
    }
    
    /**
     * Get file MIME type
     * 
     * @param string $filePath File path
     * @return string MIME type
     */
    public static function getMimeType($filePath) {
        if (!file_exists($filePath)) {
            return 'application/octet-stream';
        }
        
        if (function_exists('finfo_open')) {
            $finfo = finfo_open(FILEINFO_MIME_TYPE);
            $mime = finfo_file($finfo, $filePath);
            finfo_close($finfo);
            return $mime;
        }
        
        if (function_exists('mime_content_type')) {
            return mime_content_type($filePath);
        }
        
        // Fallback to extension-based detection
        $ext = pathinfo($filePath, PATHINFO_EXTENSION);
        $mimeTypes = [
            'md' => 'text/markdown',
            'txt' => 'text/plain',
            'php' => 'text/x-php',
            'js' => 'application/javascript',
            'css' => 'text/css',
            'json' => 'application/json',
            'yaml' => 'text/yaml',
            'yml' => 'text/yaml',
            'zip' => 'application/zip'
        ];
        
        return isset($mimeTypes[$ext]) ? $mimeTypes[$ext] : 'application/octet-stream';
    }
    
    /**
     * Send JSON response
     * 
     * @param array $data Response data
     * @param int $statusCode HTTP status code
     */
    public static function sendJsonResponse($data, $statusCode = 200) {
        http_response_code($statusCode);
        header('Content-Type: application/json');
        echo json_encode($data, JSON_PRETTY_PRINT);
        exit;
    }
    
    /**
     * Convert array to YAML
     * 
     * @param array $data Data array
     * @param int $indent Indent level
     * @return string YAML string
     */
    public static function arrayToYaml($data, $indent = 0) {
        $yaml = '';
        $spaces = str_repeat('  ', $indent);
        
        foreach ($data as $key => $value) {
            if (is_array($value)) {
                $yaml .= $spaces . $key . ":\n";
                $yaml .= self::arrayToYaml($value, $indent + 1);
            } else {
                $yaml .= $spaces . $key . ': ' . $value . "\n";
            }
        }
        
        return $yaml;
    }
    
    /**
     * Clean temporary files
     * 
     * @param string $directory Directory to clean
     * @param int $maxAge Maximum age in seconds
     * @return array Result
     */
    public static function cleanTempFiles($directory, $maxAge = 3600) {
        if (!is_dir($directory)) {
            return ['error' => 'Directory not found'];
        }
        
        $now = time();
        $deleted = [];
        $failed = [];
        
        $items = scandir($directory);
        
        foreach ($items as $item) {
            if ($item === '.' || $item === '..') {
                continue;
            }
            
            $path = $directory . DIRECTORY_SEPARATOR . $item;
            
            if (is_file($path)) {
                $age = $now - filemtime($path);
                
                if ($age > $maxAge) {
                    if (unlink($path)) {
                        $deleted[] = $item;
                    } else {
                        $failed[] = $item;
                    }
                }
            }
        }
        
        return [
            'deleted' => count($deleted),
            'failed' => count($failed),
            'files' => $deleted
        ];
    }
}
