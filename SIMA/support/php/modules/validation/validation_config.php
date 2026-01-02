<?php
/**
 * validation_config.php
 * 
 * Configuration for SIMA Validation Module
 * Version: 1.0.0
 * Date: 2025-11-27
 */

return [
    // Base paths
    'validation_base_path' => __DIR__,
    
    // Path validation
    'path' => [
        'max_length' => 4096,
        'allow_absolute' => false,
        'allow_relative' => true,
        'normalize' => true,
        'case_sensitive' => true,
        'allowed_separators' => ['/', '\\']
    ],
    
    // Directory traversal prevention
    'traversal' => [
        'enabled' => true,
        'strict_mode' => true,
        'blocked_patterns' => [
            '../',
            '..\\',
            '%2e%2e/',
            '%2e%2e\\',
            '..%2f',
            '..%5c'
        ],
        'allow_symlinks' => false
    ],
    
    // Security validation
    'security' => [
        'check_dangerous_extensions' => true,
        'check_dangerous_patterns' => true,
        'validate_mime_type' => false,
        'check_file_size' => true,
        'max_file_size' => 10485760 // 10MB
    ],
    
    // Dangerous extensions
    'dangerous_extensions' => [
        'php', 'php3', 'php4', 'php5', 'phtml',
        'exe', 'bat', 'cmd', 'com',
        'sh', 'bash', 'zsh',
        'js', 'vbs', 'jar',
        'dll', 'so', 'dylib',
        'scr', 'msi', 'app'
    ],
    
    // Allowed extensions
    'allowed_extensions' => [
        'md', 'txt', 'yaml', 'yml', 'json',
        'pdf', 'doc', 'docx',
        'png', 'jpg', 'jpeg', 'gif', 'svg',
        'zip', 'tar', 'gz'
    ],
    
    // Dangerous patterns
    'dangerous_patterns' => [
        '/\<\?php/i',
        '/\<\?=/i',
        '/\<script/i',
        '/javascript:/i',
        '/on\w+\s*=/i', // onclick, onload, etc.
        '/eval\s*\(/i',
        '/exec\s*\(/i',
        '/system\s*\(/i'
    ],
    
    // Integrity validation
    'integrity' => [
        'enabled' => true,
        'algorithms' => ['md5', 'sha256', 'sha1'],
        'default_algorithm' => 'md5',
        'verify_on_read' => false,
        'cache_checksums' => false
    ],
    
    // REF-ID validation
    'ref_id' => [
        'enabled' => true,
        'patterns' => [
            'LESS' => '/^LESS-\d+$/',
            'DEC' => '/^DEC-\d+$/',
            'AP' => '/^AP-\d+$/',
            'SPEC' => '/^SPEC-\d+$/',
            'WORK' => '/^WORK-\d+$/',
            'BUG' => '/^BUG-\d+$/',
            'WISD' => '/^WISD-\d+$/'
        ],
        'require_prefix' => true,
        'require_number' => true,
        'allow_custom' => false
    ],
    
    // File structure validation
    'structure' => [
        'require_header' => true,
        'require_title' => true,
        'require_version' => true,
        'require_date' => true,
        'require_separator' => true,
        'max_header_lines' => 20,
        'separator_pattern' => '/^---+$/'
    ],
    
    // Required header fields
    'required_fields' => [
        'Version',
        'Date',
        'Purpose'
    ],
    
    // Optional header fields
    'optional_fields' => [
        'Type',
        'REF-ID',
        'Category',
        'Keywords',
        'Related'
    ],
    
    // Cross-reference validation
    'cross_references' => [
        'enabled' => true,
        'validate_existence' => true,
        'check_broken_links' => true,
        'allow_external' => false,
        'ref_pattern' => '/REF-ID:\s*([A-Z]+-\d+(?:,\s*[A-Z]+-\d+)*)/i'
    ],
    
    // Duplicate detection
    'duplicates' => [
        'check_by_filename' => true,
        'check_by_refid' => true,
        'check_by_checksum' => true,
        'check_by_content' => false,
        'similarity_threshold' => 0.95
    ],
    
    // Content validation
    'content' => [
        'check_encoding' => true,
        'required_encoding' => 'UTF-8',
        'check_line_endings' => true,
        'required_line_ending' => "\n", // LF
        'max_line_length' => 0, // 0 = no limit
        'max_file_lines' => 400,
        'check_trailing_whitespace' => false
    ],
    
    // Upload validation
    'upload' => [
        'enabled' => true,
        'max_size' => 10485760, // 10MB
        'allowed_extensions' => ['md', 'txt', 'yaml', 'zip'],
        'check_mime_type' => true,
        'allowed_mime_types' => [
            'text/plain',
            'text/markdown',
            'application/zip',
            'application/x-yaml'
        ],
        'quarantine_on_fail' => false
    ],
    
    // Permission checking
    'permissions' => [
        'check_read' => true,
        'check_write' => true,
        'check_execute' => false,
        'require_owner' => false
    ],
    
    // Batch validation
    'batch' => [
        'max_files' => 1000,
        'stop_on_error' => false,
        'report_warnings' => true,
        'parallel_processing' => false
    ],
    
    // Error handling
    'errors' => [
        'throw_on_error' => false,
        'log_errors' => true,
        'verbose_errors' => true,
        'include_suggestions' => true
    ],
    
    // Warnings
    'warnings' => [
        'enabled' => true,
        'warn_on_missing_optional_fields' => true,
        'warn_on_large_files' => true,
        'large_file_threshold' => 5242880, // 5MB
        'warn_on_old_dates' => false
    ]
];
?>
