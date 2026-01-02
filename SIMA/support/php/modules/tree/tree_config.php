<?php
/**
 * tree_config.php
 * 
 * Configuration for SIMA Tree Module
 * Version: 1.0.0
 * Date: 2025-11-27
 */

return [
    // Base paths
    'tree_base_path' => __DIR__,
    'scan_base_path' => '/path/to/sima',
    
    // Scanning options
    'scan' => [
        'include_hidden' => false,
        'max_depth' => 20,
        'file_extensions' => ['.md'],
        'exclude_dirs' => ['.git', 'node_modules', '.idea', '__pycache__', 'vendor'],
        'include_metadata' => true
    ],
    
    // Metadata extraction
    'metadata' => [
        'max_lines_to_scan' => 20,
        'fields' => [
            'version' => '/\*\*Version:\*\*\s*(.+)$/',
            'ref_id' => '/\*\*REF-ID:\*\*\s*(.+)$/',
            'category' => '/\*\*Category:\*\*\s*(.+)$/',
            'purpose' => '/\*\*Purpose:\*\*\s*(.+)$/'
        ],
        'header_end_marker' => '---'
    ],
    
    // Tree formatting
    'format' => [
        'domain_dirs' => ['generic', 'platforms', 'languages', 'projects'],
        'support_dirs' => ['context', 'docs', 'support', 'templates'],
        'show_file_counts' => true,
        'show_sizes' => true,
        'show_modified_dates' => true
    ],
    
    // UI rendering
    'ui' => [
        'indent_pixels' => 20,
        'show_checkboxes' => true,
        'collapsible' => true,
        'default_collapsed' => false,
        'show_icons' => true,
        'icons' => [
            'directory' => '📁',
            'file' => '📄',
            'expand' => '▼',
            'collapse' => '▶'
        ]
    ],
    
    // Statistics
    'stats' => [
        'enabled' => true,
        'count_by_domain' => true,
        'count_by_category' => true,
        'count_by_extension' => true,
        'count_metadata_presence' => true
    ],
    
    // Filtering
    'filter' => [
        'enabled' => true,
        'allow_category_filter' => true,
        'allow_domain_filter' => true,
        'allow_ref_id_filter' => true,
        'allow_version_filter' => true,
        'allow_pattern_filter' => true
    ],
    
    // Performance
    'performance' => [
        'cache_enabled' => false,
        'cache_ttl' => 300,
        'cache_dir' => __DIR__ . '/cache'
    ],
    
    // Version detection
    'version' => [
        'auto_detect' => true,
        'supported_versions' => ['3.0', '4.1', '4.2', '4.3'],
        'spec_files_dir' => __DIR__ . '/specs'
    ],
    
    // Asset paths (relative to tree module)
    'assets' => [
        'css_path' => 'css',
        'js_path' => 'js'
    ]
];
