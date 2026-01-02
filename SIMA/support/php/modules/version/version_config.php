<?php
/**
 * version_config.php
 * 
 * Configuration for SIMA Version Module
 * Version: 1.0.0
 * Date: 2025-11-27
 */

return [
    // Base paths
    'version_base_path' => __DIR__,
    
    // Supported versions
    'supported_versions' => ['3.0', '4.1', '4.2', '4.3'],
    
    // Default version
    'default_version' => '4.3',
    
    // Version detection
    'detection' => [
        'methods' => ['structure', 'file_header', 'metadata'],
        'priority' => ['file_header', 'structure', 'metadata'],
        'max_files_to_check' => 10,
        'confidence_threshold' => 0.7
    ],
    
    // Version patterns in files
    'file_patterns' => [
        'version_marker' => '/\*\*Version:\*\*\s*([0-9.]+)/',
        'sima_version' => '/\*\*SIMA Version:\*\*\s*([0-9.]+)/',
        'exported_version' => '/\*\*Exported:\*\*\s*.+\(v([0-9.]+)\)/',
        'package_version' => '/\*\*Package Version:\*\*\s*([0-9.]+)/'
    ],
    
    // Version structure signatures
    'structure_signatures' => [
        '3.0' => [
            'directories' => ['knowledge', 'context'],
            'required_files' => ['Master-Index.md'],
            'optional_files' => []
        ],
        '4.1' => [
            'directories' => ['generic', 'platforms', 'projects', 'context'],
            'required_files' => ['Master-Index-of-Indexes.md'],
            'optional_files' => []
        ],
        '4.2' => [
            'directories' => ['generic', 'platforms', 'languages', 'projects', 'context'],
            'required_files' => ['Master-Index-of-Indexes.md', 'SIMA-Navigation-Hub.md'],
            'optional_files' => ['File-Server-URLs.md']
        ],
        '4.3' => [
            'directories' => ['generic', 'platforms', 'languages', 'projects', 'context', 'docs'],
            'required_files' => ['Master-Index-of-Indexes.md', 'SIMA-Quick-Reference-Card.md'],
            'optional_files' => ['File-Server-URLs.md']
        ]
    ],
    
    // Conversion rules
    'conversion' => [
        'enabled' => true,
        'auto_backup' => true,
        'validate_after' => true,
        'preserve_original_version_tag' => true
    ],
    
    // Version-specific metadata fields
    'metadata_fields' => [
        '3.0' => ['Version', 'Date', 'Category'],
        '4.1' => ['Version', 'Date', 'Purpose', 'Category'],
        '4.2' => ['Version', 'Date', 'Purpose', 'Type', 'REF-ID'],
        '4.3' => ['Version', 'Date', 'Purpose', 'Type', 'REF-ID', 'Keywords']
    ],
    
    // Version-specific header formats
    'header_formats' => [
        '3.0' => "# %s\n\n**Version:** %s\n**Date:** %s\n**Category:** %s\n",
        '4.1' => "# %s\n\n**Version:** %s\n**Date:** %s\n**Purpose:** %s\n**Category:** %s\n",
        '4.2' => "# %s\n\n**Version:** %s\n**Date:** %s\n**Purpose:** %s\n**Type:** %s\n**REF-ID:** %s\n",
        '4.3' => "# %s\n\n**Version:** %s\n**Date:** %s\n**Purpose:** %s\n**Type:** %s\n**REF-ID:** %s\n**Keywords:** %s\n"
    ],
    
    // Conversion paths (from => to)
    'conversion_paths' => [
        '3.0' => ['4.1', '4.2', '4.3'],
        '4.1' => ['4.2', '4.3'],
        '4.2' => ['4.3'],
        '4.3' => []
    ],
    
    // Backward compatibility
    'backward_compatible' => [
        '4.3' => ['4.2', '4.1'],
        '4.2' => ['4.1'],
        '4.1' => []
    ],
    
    // Tag injection
    'tag_injection' => [
        'enabled' => true,
        'position' => 'after_header', // after_header, before_footer
        'format' => "\n**SIMA Version:** %s\n**Exported:** %s\n**Export Package:** %s\n",
        'separator' => '---'
    ],
    
    // Version information
    'version_info' => [
        '3.0' => [
            'name' => 'SIMA v3.0',
            'release_date' => '2024-01-01',
            'status' => 'deprecated',
            'features' => ['Basic structure', 'Single domain']
        ],
        '4.1' => [
            'name' => 'SIMA v4.1',
            'release_date' => '2024-06-01',
            'status' => 'legacy',
            'features' => ['Multi-domain', 'REF-IDs']
        ],
        '4.2' => [
            'name' => 'SIMA v4.2',
            'release_date' => '2024-09-01',
            'status' => 'stable',
            'features' => ['Language support', 'Enhanced navigation']
        ],
        '4.3' => [
            'name' => 'SIMA v4.3',
            'release_date' => '2024-11-01',
            'status' => 'current',
            'features' => ['Documentation integration', 'Enhanced indexes']
        ]
    ],
    
    // Compatibility matrix
    'compatibility_matrix' => [
        '3.0-4.1' => 'convertible',
        '3.0-4.2' => 'convertible',
        '3.0-4.3' => 'convertible',
        '4.1-4.2' => 'convertible',
        '4.1-4.3' => 'convertible',
        '4.2-4.3' => 'convertible',
        '4.3-4.2' => 'backward_compatible',
        '4.2-4.1' => 'backward_compatible',
        '4.1-3.0' => 'incompatible'
    ],
    
    // Validation rules
    'validation' => [
        'require_version_in_header' => true,
        'require_valid_version' => true,
        'check_structure_match' => true,
        'check_metadata_fields' => true
    ],
    
    // Conversion options
    'conversion_options' => [
        'update_header' => true,
        'add_missing_fields' => true,
        'preserve_content' => true,
        'update_cross_references' => true,
        'convert_paths' => true
    ],
    
    // Path conversion rules (version-specific)
    'path_conversions' => [
        '3.0-4.1' => [
            'knowledge/' => 'generic/',
            'context/' => 'context/'
        ],
        '4.1-4.2' => [
            'platforms/aws/' => 'platforms/aws/',
            'projects/' => 'projects/'
        ],
        '4.2-4.3' => [
            'generic/' => 'generic/',
            'context/' => 'context/'
        ]
    ],
    
    // Field mapping for conversions
    'field_mappings' => [
        '3.0-4.1' => [
            'Category' => 'Purpose'
        ],
        '4.1-4.2' => [
            'Purpose' => 'Purpose',
            'Category' => 'Type'
        ],
        '4.2-4.3' => [
            'add' => ['Keywords']
        ]
    ]
];
?>
