<?php
/**
 * packaging_config.php
 * 
 * Configuration for SIMA Packaging Module
 * Version: 1.0.0
 * Date: 2025-11-27
 */

return [
    // Base paths
    'packaging_base_path' => __DIR__,
    'output_directory' => '/tmp/sima-packages',
    'temp_directory' => '/tmp/sima-temp',
    
    // Package format
    'format' => [
        'type' => 'zip', // zip, tar, tar.gz
        'compression_level' => 6, // 0-9
        'preserve_permissions' => false,
        'preserve_timestamps' => true
    ],
    
    // Package structure types
    'structures' => [
        'flat' => [
            'enabled' => true,
            'description' => 'All files in root directory'
        ],
        'categorized' => [
            'enabled' => true,
            'description' => 'Files grouped by category',
            'directories' => [
                'lessons' => 'lessons/',
                'decisions' => 'decisions/',
                'anti-patterns' => 'anti-patterns/',
                'specifications' => 'specifications/',
                'workflows' => 'workflows/',
                'other' => 'other/'
            ]
        ],
        'hierarchical' => [
            'enabled' => true,
            'description' => 'Original directory structure preserved',
            'preserve_full_path' => true
        ],
        'domain-based' => [
            'enabled' => true,
            'description' => 'Organized by domain',
            'directories' => [
                'generic' => 'generic/',
                'platforms' => 'platforms/',
                'languages' => 'languages/',
                'projects' => 'projects/'
            ]
        ]
    ],
    
    // Default structure
    'default_structure' => 'categorized',
    
    // File organization
    'organization' => [
        'group_by_default' => 'category', // category, domain, extension
        'create_subdirectories' => true,
        'preserve_structure' => false,
        'flatten_hierarchy' => false
    ],
    
    // Manifest options
    'manifest' => [
        'include_by_default' => true,
        'filename' => 'manifest.yaml',
        'location' => 'root', // root, meta, docs
        'auto_generate' => true
    ],
    
    // Instructions options
    'instructions' => [
        'include_by_default' => true,
        'filename' => 'import-instructions.md',
        'location' => 'root',
        'auto_generate' => true
    ],
    
    // Documentation
    'documentation' => [
        'include_readme' => true,
        'readme_filename' => 'README.md',
        'include_changelog' => false,
        'changelog_filename' => 'CHANGELOG.md',
        'include_license' => false,
        'license_filename' => 'LICENSE'
    ],
    
    // Metadata
    'metadata' => [
        'include_package_info' => true,
        'package_info_filename' => 'package-info.json',
        'include_checksums' => true,
        'checksum_filename' => 'checksums.txt',
        'checksum_algorithm' => 'md5'
    ],
    
    // Package types
    'package_types' => [
        'export' => [
            'structure' => 'categorized',
            'include_manifest' => true,
            'include_instructions' => true,
            'include_readme' => true
        ],
        'backup' => [
            'structure' => 'hierarchical',
            'include_manifest' => true,
            'include_readme' => false,
            'preserve_structure' => true
        ],
        'migration' => [
            'structure' => 'categorized',
            'include_manifest' => true,
            'include_instructions' => true,
            'include_changelog' => true
        ],
        'distribution' => [
            'structure' => 'domain-based',
            'include_manifest' => true,
            'include_readme' => true,
            'include_license' => true
        ]
    ],
    
    // Naming conventions
    'naming' => [
        'prefix' => 'sima',
        'separator' => '-',
        'include_date' => true,
        'date_format' => 'Ymd',
        'include_version' => false,
        'lowercase' => true,
        'template' => '{prefix}{separator}{name}{separator}{date}.{ext}'
    ],
    
    // Size limits
    'limits' => [
        'max_package_size' => 104857600, // 100MB
        'max_files' => 10000,
        'split_large_packages' => true,
        'split_size' => 52428800 // 50MB per split
    ],
    
    // Validation
    'validation' => [
        'validate_before_package' => true,
        'check_file_existence' => true,
        'verify_checksums' => true,
        'validate_structure' => true
    ],
    
    // Temporary files
    'temp' => [
        'cleanup_on_success' => true,
        'cleanup_on_error' => false,
        'max_age_hours' => 24
    ],
    
    // Archive options
    'archive' => [
        'store_empty_directories' => false,
        'follow_symlinks' => false,
        'exclude_patterns' => ['.git', '.svn', '.DS_Store', 'Thumbs.db'],
        'include_hidden' => false
    ],
    
    // Output options
    'output' => [
        'create_directory' => true,
        'overwrite_existing' => false,
        'generate_url' => true,
        'url_base' => '/packages/',
        'return_relative_path' => true
    ]
];
?>
