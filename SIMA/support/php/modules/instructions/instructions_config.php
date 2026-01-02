<?php
/**
 * instructions_config.php
 * 
 * Configuration for SIMA Instructions Module
 * Version: 1.0.0
 * Date: 2025-11-27
 */

return [
    // Base paths
    'instructions_base_path' => __DIR__,
    
    // Document format
    'format' => [
        'heading_style' => '#', // # or =
        'line_length' => 80,
        'include_header' => true,
        'include_footer' => true,
        'include_toc' => false,
        'date_format' => 'Y-m-d',
        'separator' => '---'
    ],
    
    // Header options
    'header' => [
        'include_title' => true,
        'include_version' => true,
        'include_date' => true,
        'include_operation' => true,
        'include_file_count' => true,
        'template' => "# %s\n\n**Version:** %s  \n**Date:** %s  \n**Operation:** %s  \n**Files:** %d\n\n---\n\n"
    ],
    
    // Footer options
    'footer' => [
        'enabled' => true,
        'template' => "\n---\n\n**END OF INSTRUCTIONS**\n"
    ],
    
    // Table of contents
    'toc' => [
        'enabled' => false,
        'title' => 'Table of Contents',
        'max_depth' => 3,
        'include_numbers' => false
    ],
    
    // File list formatting
    'file_list' => [
        'group_by_default' => 'directory', // directory, category, domain, extension
        'show_paths' => true,
        'show_ref_ids' => true,
        'show_sizes' => false,
        'show_checksums' => false,
        'indent_grouped' => true,
        'indent_size' => 2
    ],
    
    // Checklist formatting
    'checklist' => [
        'unchecked_marker' => '[ ]',
        'checked_marker' => '[x]',
        'indent_nested' => true,
        'add_spacing' => true
    ],
    
    // Tree formatting
    'tree' => [
        'directory_icon' => '📁',
        'file_icon' => '📄',
        'branch_chars' => ['├──', '└──', '│  ', '   '],
        'show_file_count' => true
    ],
    
    // Table formatting
    'table' => [
        'alignment' => 'left', // left, center, right
        'min_column_width' => 10,
        'padding' => 1,
        'border_style' => 'simple' // simple, grid
    ],
    
    // Operation-specific templates
    'templates' => [
        'import' => [
            'sections' => [
                'overview',
                'prerequisites',
                'file_inventory',
                'installation_steps',
                'verification',
                'troubleshooting'
            ]
        ],
        'export' => [
            'sections' => [
                'overview',
                'package_contents',
                'usage',
                'import_instructions'
            ]
        ],
        'update' => [
            'sections' => [
                'overview',
                'changes',
                'affected_files',
                'backup_instructions',
                'update_steps',
                'rollback'
            ]
        ],
        'restore' => [
            'sections' => [
                'overview',
                'backup_info',
                'restore_steps',
                'verification'
            ]
        ],
        'migrate' => [
            'sections' => [
                'overview',
                'version_changes',
                'compatibility',
                'migration_steps',
                'validation'
            ]
        ]
    ],
    
    // Section templates
    'section_templates' => [
        'overview' => "## OVERVIEW\n\n%s\n",
        'prerequisites' => "## PREREQUISITES\n\n%s\n",
        'file_inventory' => "## FILE INVENTORY\n\n%s\n",
        'installation_steps' => "## INSTALLATION STEPS\n\n%s\n",
        'verification' => "## VERIFICATION\n\n%s\n",
        'troubleshooting' => "## TROUBLESHOOTING\n\n%s\n"
    ],
    
    // Content generation
    'content' => [
        'verbose' => true,
        'include_examples' => true,
        'include_warnings' => true,
        'include_notes' => true,
        'auto_number_steps' => true
    ],
    
    // Import-specific
    'import' => [
        'show_file_tree' => true,
        'show_conflicts' => true,
        'show_dependencies' => true,
        'include_verification_checklist' => true
    ],
    
    // Export-specific
    'export' => [
        'show_package_structure' => true,
        'include_usage_examples' => true,
        'show_file_breakdown' => true
    ],
    
    // Update-specific
    'update' => [
        'show_changelog' => true,
        'show_affected_files' => true,
        'include_backup_steps' => true,
        'include_rollback_steps' => true
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
    
    // Warnings and notes
    'warnings' => [
        'enabled' => true,
        'marker' => '⚠️',
        'format' => "**%s WARNING:** %s\n"
    ],
    
    'notes' => [
        'enabled' => true,
        'marker' => '📝',
        'format' => "**%s NOTE:** %s\n"
    ],
    
    // Step numbering
    'steps' => [
        'auto_number' => true,
        'format' => '%d. %s',
        'sub_step_format' => '   %s. %s',
        'include_descriptions' => true
    ],
    
    // Code blocks
    'code_blocks' => [
        'default_language' => 'bash',
        'include_language' => true,
        'show_line_numbers' => false
    ],
    
    // Links and references
    'links' => [
        'format' => '[%s](%s)',
        'include_ref_ids' => true,
        'auto_link_files' => false
    ]
];
?>
