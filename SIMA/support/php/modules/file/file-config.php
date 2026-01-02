<?php
/**
 * file-config.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-27
 * Purpose: Configuration for SIMA file module
 * Project: SIMA File Module
 * 
 * ADDED: Complete configuration system
 */

class FileConfig {
    
    /**
     * Default configuration
     */
    private static $config = [
        
        // ========================================
        // BASE PATHS
        // ========================================
        
        // Root directory for file operations
        'base_directory' => '/var/www/sima',
        
        // Export/temporary directory
        'export_directory' => '/var/www/sima/exports',
        
        // Upload directory
        'upload_directory' => '/var/www/sima/uploads',
        
        // Archive storage directory
        'archive_directory' => '/var/www/sima/archives',
        
        // ========================================
        // FILE SCANNING
        // ========================================
        
        // File extensions to include
        'include_extensions' => ['.md', '.php', '.js', '.css', '.yaml', '.json', '.txt'],
        
        // File extensions to exclude
        'exclude_extensions' => ['.zip', '.tar', '.gz', '.log', '.tmp'],
        
        // Directories to exclude from scanning
        'exclude_directories' => ['.git', '.svn', 'node_modules', 'vendor', 'cache'],
        
        // Files to exclude from scanning
        'exclude_files' => ['.gitignore', '.htaccess', 'fileserver.php'],
        
        // Maximum scan depth (0 = unlimited)
        'max_scan_depth' => 0,
        
        // Follow symbolic links
        'follow_symlinks' => false,
        
        // Include hidden files (starting with .)
        'include_hidden' => false,
        
        // ========================================
        // ARCHIVE SETTINGS
        // ========================================
        
        // Default compression level (0-9)
        'compression_level' => 6,
        
        // Archive format ('zip', 'tar', 'tar.gz')
        'archive_format' => 'zip',
        
        // Preserve directory structure
        'preserve_structure' => true,
        
        // Add timestamp to archive names
        'timestamp_archives' => true,
        
        // Maximum archive size (bytes, 0 = unlimited)
        'max_archive_size' => 0,
        
        // Split archives if exceeding size
        'split_archives' => false,
        
        // Split size (bytes)
        'split_size' => 104857600, // 100MB
        
        // ========================================
        // EXTRACTION SETTINGS
        // ========================================
        
        // Overwrite existing files
        'overwrite_on_extract' => false,
        
        // Create directories if missing
        'create_directories' => true,
        
        // Preserve file permissions
        'preserve_permissions' => true,
        
        // Preserve file timestamps
        'preserve_timestamps' => true,
        
        // Verify checksums after extraction
        'verify_after_extract' => true,
        
        // ========================================
        // METADATA SETTINGS
        // ========================================
        
        // Extract version from files
        'extract_versions' => true,
        
        // Extract REF-IDs from files
        'extract_ref_ids' => true,
        
        // Calculate checksums
        'calculate_checksums' => true,
        
        // Checksum algorithm
        'checksum_algorithm' => 'sha256',
        
        // Store file sizes
        'store_file_sizes' => true,
        
        // Store modification times
        'store_mod_times' => true,
        
        // ========================================
        // VALIDATION SETTINGS
        // ========================================
        
        // Validate paths against base directory
        'validate_paths' => true,
        
        // Maximum path length
        'max_path_length' => 4096,
        
        // Allowed path characters regex
        'allowed_path_chars' => '/^[a-zA-Z0-9\/_\-\.]+$/',
        
        // Check file permissions before operations
        'check_permissions' => true,
        
        // Verify file existence before operations
        'verify_existence' => true,
        
        // ========================================
        // SECURITY SETTINGS
        // ========================================
        
        // Prevent directory traversal attacks
        'prevent_traversal' => true,
        
        // Sanitize filenames
        'sanitize_filenames' => true,
        
        // Maximum filename length
        'max_filename_length' => 255,
        
        // Blacklist dangerous extensions
        'dangerous_extensions' => ['.exe', '.dll', '.so', '.sh', '.bat', '.cmd'],
        
        // Whitelist safe extensions only
        'whitelist_mode' => false,
        
        // ========================================
        // PERFORMANCE SETTINGS
        // ========================================
        
        // Maximum files to process in batch
        'max_batch_size' => 1000,
        
        // Memory limit for operations (bytes)
        'memory_limit' => 134217728, // 128MB
        
        // Timeout for long operations (seconds)
        'operation_timeout' => 300,
        
        // Enable caching
        'enable_cache' => true,
        
        // Cache duration (seconds)
        'cache_duration' => 3600,
        
        // ========================================
        // ERROR HANDLING
        // ========================================
        
        // Continue on errors
        'continue_on_error' => true,
        
        // Log errors
        'log_errors' => true,
        
        // Error log path
        'error_log_path' => '/var/www/sima/logs/file-module.log',
        
        // Throw exceptions on critical errors
        'throw_exceptions' => false,
        
        // ========================================
        // OUTPUT SETTINGS
        // ========================================
        
        // Output format ('json', 'array', 'yaml')
        'output_format' => 'array',
        
        // Pretty print JSON
        'pretty_json' => true,
        
        // Include debug info
        'include_debug' => false,
        
        // Verbose output
        'verbose' => false,
        
        // ========================================
        // MANIFEST SETTINGS
        // ========================================
        
        // Generate manifest on archive creation
        'auto_generate_manifest' => true,
        
        // Manifest filename
        'manifest_filename' => 'manifest.yaml',
        
        // Include file tree in manifest
        'manifest_include_tree' => true,
        
        // Include statistics in manifest
        'manifest_include_stats' => true,
        
        // ========================================
        // CLEANUP SETTINGS
        // ========================================
        
        // Auto-delete temporary files
        'auto_cleanup_temp' => true,
        
        // Temporary file lifetime (seconds)
        'temp_lifetime' => 3600,
        
        // Auto-delete old exports
        'auto_cleanup_exports' => true,
        
        // Export lifetime (seconds)
        'export_lifetime' => 86400, // 24 hours
    ];
    
    /**
     * Get configuration
     * 
     * @param string|null $key Configuration key or null for all
     * @return mixed Configuration value or array
     */
    public static function getConfig($key = null) {
        if ($key === null) {
            return self::$config;
        }
        
        return isset(self::$config[$key]) ? self::$config[$key] : null;
    }
    
    /**
     * Set configuration value
     * 
     * @param string|array $key Configuration key or array of key-value pairs
     * @param mixed $value Configuration value (if key is string)
     */
    public static function setConfig($key, $value = null) {
        if (is_array($key)) {
            self::$config = array_merge(self::$config, $key);
        } else {
            self::$config[$key] = $value;
        }
    }
    
    /**
     * Load configuration from file
     * 
     * @param string $filePath Path to configuration file
     * @return bool Success
     */
    public static function loadFromFile($filePath) {
        if (!file_exists($filePath)) {
            return false;
        }
        
        $extension = pathinfo($filePath, PATHINFO_EXTENSION);
        
        if ($extension === 'php') {
            $config = include $filePath;
            if (is_array($config)) {
                self::setConfig($config);
                return true;
            }
        } elseif ($extension === 'json') {
            $json = file_get_contents($filePath);
            $config = json_decode($json, true);
            if (is_array($config)) {
                self::setConfig($config);
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Validate configuration
     * 
     * @return array Validation errors (empty if valid)
     */
    public static function validate() {
        $errors = [];
        
        // Validate required directories exist and are writable
        $dirs = ['base_directory', 'export_directory', 'upload_directory', 'archive_directory'];
        foreach ($dirs as $dir) {
            $path = self::$config[$dir];
            if (!is_dir($path) && !mkdir($path, 0755, true)) {
                $errors[] = "Cannot create directory: {$path}";
            } elseif (!is_writable($path)) {
                $errors[] = "Directory not writable: {$path}";
            }
        }
        
        // Validate numeric settings
        if (self::$config['compression_level'] < 0 || self::$config['compression_level'] > 9) {
            $errors[] = "Invalid compression_level (must be 0-9)";
        }
        
        // Validate array settings
        if (!is_array(self::$config['include_extensions'])) {
            $errors[] = "include_extensions must be array";
        }
        
        return $errors;
    }
}
