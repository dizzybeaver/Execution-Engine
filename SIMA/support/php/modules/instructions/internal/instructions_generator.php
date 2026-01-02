<?php
/**
 * instructions_generator.php
 * 
 * Instructions Generation Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use InstructionsModule API
 */

class InstructionsGenerator {
    private $config;
    private $formatter;
    
    public function __construct($config) {
        $this->config = $config;
        require_once __DIR__ . '/instructions_formatter.php';
        $this->formatter = new InstructionsFormatter($config);
    }
    
    public function updateConfig($config) {
        $this->config = $config;
        if ($this->formatter) {
            $this->formatter->updateConfig($config);
        }
    }
    
    /**
     * Generate instructions for operation
     */
    public function generate($operation, $files, $options = []) {
        $method = 'generate' . ucfirst($operation) . 'Instructions';
        
        if (method_exists($this, $method)) {
            return $this->$method($files, $options);
        }
        
        return $this->generateCustom(
            ucfirst($operation) . ' Instructions',
            ['Overview' => 'Instructions for ' . $operation],
            $options
        );
    }
    
    /**
     * Generate import instructions
     */
    public function generateImportInstructions($files, $options = []) {
        $archiveName = $options['archive_name'] ?? 'archive';
        $sourceVersion = $options['source_version'] ?? 'unknown';
        $targetVersion = $options['target_version'] ?? 'unknown';
        
        $md = $this->generateHeader(
            'Import Instructions',
            '1.0.0',
            'import',
            count($files)
        );
        
        // Overview
        $md .= "## OVERVIEW\n\n";
        $md .= "Import package: **{$archiveName}**  \n";
        $md .= "Source version: **{$sourceVersion}**  \n";
        $md .= "Target version: **{$targetVersion}**  \n";
        $md .= "Total files: **" . count($files) . "**\n\n";
        
        if ($sourceVersion !== $targetVersion) {
            $md .= $this->formatter->formatWarning(
                "Version conversion required from {$sourceVersion} to {$targetVersion}"
            );
        }
        
        $md .= "---\n\n";
        
        // Prerequisites
        $md .= "## PREREQUISITES\n\n";
        $md .= $this->formatter->formatChecklist([
            'Backup current SIMA instance',
            'Verify SIMA version compatibility',
            'Ensure file write permissions',
            'Review manifest.yaml for conflicts'
        ]);
        $md .= "\n";
        
        // File inventory
        $md .= "## FILE INVENTORY\n\n";
        $md .= $this->formatter->formatFileList($files, 'directory');
        $md .= "\n";
        
        // Installation steps
        $md .= "## INSTALLATION STEPS\n\n";
        $steps = [
            'Extract archive to temporary location',
            'Review file list and check for conflicts',
            'Copy files to target directories',
            'Update indexes as needed',
            'Verify file integrity'
        ];
        
        foreach ($steps as $i => $step) {
            $md .= sprintf($this->config['steps']['format'], $i + 1, $step) . "\n";
        }
        $md .= "\n";
        
        // Verification
        $md .= "## VERIFICATION\n\n";
        $md .= $this->formatter->formatChecklist([
            'All files copied successfully',
            'No missing dependencies',
            'Indexes updated correctly',
            'Cross-references valid',
            'File permissions correct'
        ]);
        $md .= "\n";
        
        // Troubleshooting
        $md .= "## TROUBLESHOOTING\n\n";
        $md .= "**REF-ID Conflicts:** Files with same REF-ID will be auto-renumbered\n\n";
        $md .= "**Missing Dependencies:** Install dependencies before importing\n\n";
        $md .= "**Permission Errors:** Ensure write permissions on target directories\n\n";
        
        $md .= $this->generateFooter();
        
        return $md;
    }
    
    /**
     * Generate export instructions
     */
    public function generateExportInstructions($files, $options = []) {
        $archiveName = $options['archive_name'] ?? 'export';
        
        $md = $this->generateHeader(
            'Export Package Instructions',
            '1.0.0',
            'export',
            count($files)
        );
        
        // Overview
        $md .= "## OVERVIEW\n\n";
        $md .= "This package contains **" . count($files) . "** SIMA knowledge files.\n\n";
        $md .= "Package: **{$archiveName}**\n\n";
        $md .= "---\n\n";
        
        // Package contents
        $md .= "## PACKAGE CONTENTS\n\n";
        $md .= "```\n";
        $md .= "{$archiveName}/\n";
        $md .= "├── manifest.yaml\n";
        $md .= "├── import-instructions.md (this file)\n";
        $md .= "└── files/\n";
        $md .= "    └── [" . count($files) . " files]\n";
        $md .= "```\n\n";
        
        // File breakdown
        $md .= "## FILE BREAKDOWN\n\n";
        $md .= $this->formatter->formatFileList($files, 'category');
        $md .= "\n";
        
        // Import instructions
        $md .= "## HOW TO IMPORT\n\n";
        $md .= "1. Extract archive\n";
        $md .= "2. Review manifest.yaml\n";
        $md .= "3. Check for conflicts with existing files\n";
        $md .= "4. Copy files to target SIMA instance\n";
        $md .= "5. Update indexes\n\n";
        
        $md .= $this->generateFooter();
        
        return $md;
    }
    
    /**
     * Generate update instructions
     */
    public function generateUpdateInstructions($files, $options = []) {
        $md = $this->generateHeader(
            'Update Instructions',
            '1.0.0',
            'update',
            count($files)
        );
        
        // Overview
        $md .= "## OVERVIEW\n\n";
        $md .= "This update affects **" . count($files) . "** files.\n\n";
        $md .= "---\n\n";
        
        // Backup
        $md .= "## BACKUP FIRST\n\n";
        $md .= $this->formatter->formatWarning('Always backup before updating');
        $md .= "\n";
        $md .= $this->formatter->formatChecklist([
            'Backup current files',
            'Export current state',
            'Document current version'
        ]);
        $md .= "\n";
        
        // Affected files
        $md .= "## AFFECTED FILES\n\n";
        $md .= $this->formatter->formatFileList($files, 'directory');
        $md .= "\n";
        
        // Update steps
        $md .= "## UPDATE STEPS\n\n";
        $md .= "1. Create backup\n";
        $md .= "2. Review changes\n";
        $md .= "3. Apply updates\n";
        $md .= "4. Verify functionality\n";
        $md .= "5. Update indexes\n\n";
        
        // Rollback
        $md .= "## ROLLBACK PROCEDURE\n\n";
        $md .= "If issues occur:\n\n";
        $md .= "1. Stop using updated files\n";
        $md .= "2. Restore from backup\n";
        $md .= "3. Verify restoration\n";
        $md .= "4. Document issues\n\n";
        
        $md .= $this->generateFooter();
        
        return $md;
    }
    
    /**
     * Generate restore instructions
     */
    public function generateRestoreInstructions($files, $options = []) {
        $md = $this->generateHeader(
            'Restore Instructions',
            '1.0.0',
            'restore',
            count($files)
        );
        
        // Overview
        $md .= "## OVERVIEW\n\n";
        $md .= "Restore **" . count($files) . "** files from backup.\n\n";
        $md .= "---\n\n";
        
        // Backup info
        $md .= "## BACKUP INFORMATION\n\n";
        $md .= $this->formatter->formatFileList($files, 'directory');
        $md .= "\n";
        
        // Restore steps
        $md .= "## RESTORE STEPS\n\n";
        $md .= "1. Verify backup integrity\n";
        $md .= "2. Clear target location\n";
        $md .= "3. Copy backup files\n";
        $md .= "4. Verify restoration\n";
        $md .= "5. Update indexes\n\n";
        
        // Verification
        $md .= "## VERIFICATION\n\n";
        $md .= $this->formatter->formatChecklist([
            'All files restored',
            'File integrity verified',
            'Indexes updated',
            'System functional'
        ]);
        $md .= "\n";
        
        $md .= $this->generateFooter();
        
        return $md;
    }
    
    /**
     * Generate migration instructions
     */
    public function generateMigrationInstructions($files, $options = []) {
        $fromVersion = $options['from_version'] ?? 'unknown';
        $toVersion = $options['to_version'] ?? 'unknown';
        
        $md = $this->generateHeader(
            'Migration Instructions',
            '1.0.0',
            'migrate',
            count($files)
        );
        
        // Overview
        $md .= "## OVERVIEW\n\n";
        $md .= "Migrate from version **{$fromVersion}** to **{$toVersion}**\n\n";
        $md .= "Files to migrate: **" . count($files) . "**\n\n";
        $md .= "---\n\n";
        
        // Version changes
        $md .= "## VERSION CHANGES\n\n";
        $md .= "- Source: {$fromVersion}\n";
        $md .= "- Target: {$toVersion}\n\n";
        
        // Affected files
        $md .= "## AFFECTED FILES\n\n";
        $md .= $this->formatter->formatFileList($files, 'directory');
        $md .= "\n";
        
        // Migration steps
        $md .= "## MIGRATION STEPS\n\n";
        $md .= "1. Backup current version\n";
        $md .= "2. Review compatibility\n";
        $md .= "3. Convert file formats\n";
        $md .= "4. Update metadata\n";
        $md .= "5. Verify migration\n\n";
        
        $md .= $this->generateFooter();
        
        return $md;
    }
    
    /**
     * Generate custom instructions
     */
    public function generateCustom($title, $sections, $options = []) {
        $md = $this->generateHeader($title, '1.0.0', 'custom', 0);
        
        foreach ($sections as $sectionTitle => $content) {
            $md .= $this->formatter->formatSection($sectionTitle, $content);
        }
        
        $md .= $this->generateFooter();
        
        return $md;
    }
    
    /**
     * Generate document header
     */
    private function generateHeader($title, $version, $operation, $fileCount) {
        if (!$this->config['format']['include_header']) {
            return '';
        }
        
        return sprintf(
            $this->config['header']['template'],
            $title,
            $version,
            date($this->config['format']['date_format']),
            ucfirst($operation),
            $fileCount
        );
    }
    
    /**
     * Generate document footer
     */
    private function generateFooter() {
        if (!$this->config['footer']['enabled']) {
            return '';
        }
        
        return $this->config['footer']['template'];
    }
}
?>
