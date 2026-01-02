<?php
/**
 * instructions_module.php
 * 
 * SIMA Instructions Module - Public API
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Public interface for generating operation instructions
 */

class InstructionsModule {
    private $config;
    private $generator;
    private $formatter;
    
    /**
     * Initialize instructions module
     * 
     * @param array|string $config Config array or path to config file
     */
    public function __construct($config = null) {
        // Load configuration
        if (is_string($config) && file_exists($config)) {
            $this->config = require $config;
        } elseif (is_array($config)) {
            $this->config = $config;
        } else {
            $this->config = require __DIR__ . '/instructions_config.php';
        }
        
        // Load internal components
        require_once __DIR__ . '/internal/instructions_generator.php';
        require_once __DIR__ . '/internal/instructions_formatter.php';
        
        $this->generator = new InstructionsGenerator($this->config);
        $this->formatter = new InstructionsFormatter($this->config);
    }
    
    /**
     * Generate instructions for operation
     * 
     * @param string $operation Operation type (import/export/update/restore)
     * @param array $files File list
     * @param array $options Additional options
     * @return string Markdown instructions
     */
    public function generate($operation, $files, $options = []) {
        return $this->generator->generate($operation, $files, $options);
    }
    
    /**
     * Generate and save instructions to file
     * 
     * @param string $operation Operation type
     * @param array $files File list
     * @param string $outputPath Path to save instructions
     * @param array $options Additional options
     * @return array Result with success and path
     */
    public function generateToFile($operation, $files, $outputPath, $options = []) {
        $content = $this->generate($operation, $files, $options);
        
        $dir = dirname($outputPath);
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        
        if (file_put_contents($outputPath, $content) === false) {
            return ['error' => 'Failed to write instructions file'];
        }
        
        return [
            'success' => true,
            'path' => $outputPath,
            'size' => strlen($content)
        ];
    }
    
    /**
     * Add section to existing instructions
     * 
     * @param string $title Section title
     * @param string $content Section content
     * @return string Section markdown
     */
    public function addSection($title, $content) {
        return $this->formatter->formatSection($title, $content);
    }
    
    /**
     * Format file list
     * 
     * @param array $files File list
     * @param string $groupBy Group by: directory, category, domain, extension
     * @return string Formatted markdown
     */
    public function formatFileList($files, $groupBy = 'directory') {
        return $this->formatter->formatFileList($files, $groupBy);
    }
    
    /**
     * Format checklist
     * 
     * @param array $items Checklist items
     * @param bool $checked Default checked state
     * @return string Formatted markdown checklist
     */
    public function formatChecklist($items, $checked = false) {
        return $this->formatter->formatChecklist($items, $checked);
    }
    
    /**
     * Format file tree
     * 
     * @param array $files File list
     * @return string Tree structure markdown
     */
    public function formatFileTree($files) {
        return $this->formatter->formatFileTree($files);
    }
    
    /**
     * Format table
     * 
     * @param array $headers Table headers
     * @param array $rows Table rows
     * @return string Markdown table
     */
    public function formatTable($headers, $rows) {
        return $this->formatter->formatTable($headers, $rows);
    }
    
    /**
     * Generate import instructions
     * 
     * @param array $files File list
     * @param array $options Options (archive_name, source_version, target_version)
     * @return string Import instructions markdown
     */
    public function generateImportInstructions($files, $options = []) {
        return $this->generator->generateImportInstructions($files, $options);
    }
    
    /**
     * Generate export instructions
     * 
     * @param array $files File list
     * @param array $options Options
     * @return string Export instructions markdown
     */
    public function generateExportInstructions($files, $options = []) {
        return $this->generator->generateExportInstructions($files, $options);
    }
    
    /**
     * Generate update instructions
     * 
     * @param array $files File list
     * @param array $options Options
     * @return string Update instructions markdown
     */
    public function generateUpdateInstructions($files, $options = []) {
        return $this->generator->generateUpdateInstructions($files, $options);
    }
    
    /**
     * Generate restore instructions
     * 
     * @param array $files File list
     * @param array $options Options
     * @return string Restore instructions markdown
     */
    public function generateRestoreInstructions($files, $options = []) {
        return $this->generator->generateRestoreInstructions($files, $options);
    }
    
    /**
     * Generate migration instructions
     * 
     * @param array $files File list
     * @param array $options Options (from_version, to_version)
     * @return string Migration instructions markdown
     */
    public function generateMigrationInstructions($files, $options = []) {
        return $this->generator->generateMigrationInstructions($files, $options);
    }
    
    /**
     * Append section to existing file
     * 
     * @param string $filePath Existing instructions file
     * @param string $title Section title
     * @param string $content Section content
     * @return array Result
     */
    public function appendSection($filePath, $title, $content) {
        if (!file_exists($filePath)) {
            return ['error' => 'File does not exist'];
        }
        
        $existing = file_get_contents($filePath);
        $section = $this->addSection($title, $content);
        $updated = $existing . "\n\n" . $section;
        
        if (file_put_contents($filePath, $updated) === false) {
            return ['error' => 'Failed to update file'];
        }
        
        return [
            'success' => true,
            'path' => $filePath
        ];
    }
    
    /**
     * Generate custom instructions
     * 
     * @param string $title Document title
     * @param array $sections Array of ['title' => 'content'] pairs
     * @param array $options Options (include_header, include_toc)
     * @return string Markdown document
     */
    public function generateCustom($title, $sections, $options = []) {
        return $this->generator->generateCustom($title, $sections, $options);
    }
    
    /**
     * Get configuration value
     * 
     * @param string $key Config key (dot notation supported)
     * @param mixed $default Default value
     * @return mixed Config value
     */
    public function getConfig($key, $default = null) {
        $keys = explode('.', $key);
        $value = $this->config;
        
        foreach ($keys as $k) {
            if (!isset($value[$k])) {
                return $default;
            }
            $value = $value[$k];
        }
        
        return $value;
    }
    
    /**
     * Set configuration value
     * 
     * @param string $key Config key
     * @param mixed $value Config value
     */
    public function setConfig($key, $value) {
        $this->config[$key] = $value;
        
        // Update component configs
        if ($this->generator) {
            $this->generator->updateConfig($this->config);
        }
        if ($this->formatter) {
            $this->formatter->updateConfig($this->config);
        }
    }
    
    /**
     * Validate instructions content
     * 
     * @param string $content Instructions markdown
     * @return array Validation result
     */
    public function validate($content) {
        $errors = [];
        
        if (empty($content)) {
            $errors[] = 'Content is empty';
        }
        
        if (!preg_match('/^#\s+/', $content)) {
            $errors[] = 'Missing main heading';
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors
        ];
    }
}
?>
