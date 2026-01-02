<?php
/**
 * manifest_config.php
 * 
 * Configuration for SIMA Manifest Module
 * Version: 1.0.0
 * Date: 2025-11-27
 */

return [
    // Base paths
    'manifest_base_path' => __DIR__,
    
    // Manifest format options
    'format' => [
        'yaml_indent' => 2,
        'include_comments' => true,
        'date_format' => 'Y-m-d H:i:s',
        'include_checksums' => true,
        'checksum_algorithm' => 'md5' // md5, sha256
    ],
    
    // Operation types
    'operations' => [
        'allowed' => ['export', 'import', 'update', 'backup', 'restore', 'migrate'],
        'default' => 'export'
    ],
    
    // Archive metadata
    'archive' => [
        'include_source_version' => true,
        'include_target_version' => true,
        'include_timestamp' => true,
        'include_description' => true,
        'include_file_count' => true,
        'include_converted_count' => true
    ],
    
    // File metadata
    'file_metadata' => [
        'include_filename' => true,
        'include_path' => true,
        'include_ref_id' => true,
        'include_category' => true,
        'include_size' => true,
        'include_checksum' => true,
        'include_version' => false,
        'include_modified' => false
    ],
    
    // Statistics generation
    'statistics' => [
        'enabled' => true,
        'count_by_domain' => true,
        'count_by_category' => true,
        'count_by_extension' => true,
        'calculate_total_size' => true,
        'list_ref_ids' => true
    ],
    
    // Validation rules
    'validation' => [
        'require_operation' => true,
        'require_archive_name' => true,
        'require_files_array' => true,
        'require_file_paths' => true,
        'validate_ref_ids' => true,
        'validate_checksums' => false,
        'check_file_existence' => false
    ],
    
    // Parsing options
    'parsing' => [
        'strict_mode' => false,
        'validate_on_parse' => true,
        'convert_dates' => true,
        'normalize_paths' => true
    ],
    
    // Merging behavior
    'merging' => [
        'allow_duplicates' => false,
        'merge_strategy' => 'append', // append, replace, skip
        'combine_statistics' => true,
        'preserve_order' => true
    ],
    
    // Comparison options
    'comparison' => [
        'compare_checksums' => true,
        'compare_sizes' => true,
        'compare_ref_ids' => true,
        'report_missing' => true,
        'report_modified' => true
    ],
    
    // Domain categorization
    'domains' => [
        'generic' => 'Generic',
        'platforms' => 'Platform-Specific',
        'languages' => 'Language-Specific',
        'projects' => 'Project-Specific'
    ],
    
    // Category types
    'categories' => [
        'lessons' => 'Lessons Learned',
        'decisions' => 'Architectural Decisions',
        'anti-patterns' => 'Anti-Patterns',
        'specifications' => 'Specifications',
        'workflows' => 'Workflows',
        'context' => 'Context Files',
        'docs' => 'Documentation',
        'support' => 'Support Files',
        'templates' => 'Templates'
    ],
    
    // REF-ID patterns
    'ref_id_patterns' => [
        'LESS' => 'Lessons',
        'DEC' => 'Decisions',
        'AP' => 'Anti-Patterns',
        'SPEC' => 'Specifications',
        'WORK' => 'Workflows',
        'BUG' => 'Bugs',
        'WISD' => 'Wisdom'
    ],
    
    // Output options
    'output' => [
        'pretty_print' => true,
        'add_header_comment' => true,
        'add_footer_comment' => false,
        'header_template' => "# SIMA Manifest\n# Generated: %s\n# Operation: %s\n",
        'section_separators' => true
    ],
    
    // Error handling
    'errors' => [
        'throw_on_error' => false,
        'log_errors' => true,
        'verbose_errors' => true
    ]
];
?>
