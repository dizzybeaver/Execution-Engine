<?php
/**
 * packaging_module.php
 * 
 * SIMA Packaging Module - Public API
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Public interface for creating packages with manifests and documentation
 */

class PackagingModule {
    private $config;
    private $creator;
    private $organizer;
    
    /**
     * Initialize packaging module
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
            $this->config = require __DIR__ . '/packaging_config.php';
        }
        
        // Load internal components
        require_once __DIR__ . '/internal/package_creator.php';
        require_once __DIR__ . '/internal/package_organizer.php';
        
        $this->creator = new PackageCreator($this->config);
        $this->organizer = new PackageOrganizer($this->config);
    }
    
    /**
     * Create package from files
     * 
     * @param array $files File list
     * @param string $packageName Package name
     * @param array $options Package options
     * @return array Result with package path
     */
    public function create($files, $packageName, $options = []) {
        return $this->creator->create($files, $packageName, $options);
    }
    
    /**
     * Create package with manifest
     * 
     * @param array $files File list
     * @param string $packageName Package name
     * @param string $manifestContent Manifest YAML content
     * @param array $options Options
     * @return array Result
     */
    public function createWithManifest($files, $packageName, $manifestContent, $options = []) {
        return $this->creator->createWithManifest($files, $packageName, $manifestContent, $options);
    }
    
    /**
     * Create package with documentation
     * 
     * @param array $files File list
     * @param string $packageName Package name
     * @param array $documentation Documentation array (filename => content)
     * @param array $options Options
     * @return array Result
     */
    public function createWithDocumentation($files, $packageName, $documentation, $options = []) {
        return $this->creator->createWithDocumentation($files, $packageName, $documentation, $options);
    }
    
    /**
     * Create complete package (files + manifest + instructions)
     * 
     * @param array $files File list
     * @param string $packageName Package name
     * @param string $manifestContent Manifest content
     * @param string $instructionsContent Instructions content
     * @param array $options Options
     * @return array Result
     */
    public function createComplete($files, $packageName, $manifestContent, $instructionsContent, $options = []) {
        return $this->creator->createComplete($files, $packageName, $manifestContent, $instructionsContent, $options);
    }
    
    /**
     * Set package structure
     * 
     * @param array $structure Structure definition
     */
    public function setStructure($structure) {
        $this->organizer->setStructure($structure);
    }
    
    /**
     * Organize files by structure
     * 
     * @param array $files File list
     * @param string $structure Structure type (flat, categorized, hierarchical)
     * @return array Organized files
     */
    public function organize($files, $structure = 'categorized') {
        return $this->organizer->organize($files, $structure);
    }
    
    /**
     * Add files to existing package
     * 
     * @param string $packagePath Existing package path
     * @param array $files Files to add
     * @return array Result
     */
    public function addFiles($packagePath, $files) {
        return $this->creator->addFiles($packagePath, $files);
    }
    
    /**
     * Add manifest to package
     * 
     * @param string $packagePath Package path
     * @param string $manifestContent Manifest content
     * @return array Result
     */
    public function addManifest($packagePath, $manifestContent) {
        return $this->creator->addManifest($packagePath, $manifestContent);
    }
    
    /**
     * Add instructions to package
     * 
     * @param string $packagePath Package path
     * @param string $instructionsContent Instructions content
     * @return array Result
     */
    public function addInstructions($packagePath, $instructionsContent) {
        return $this->creator->addInstructions($packagePath, $instructionsContent);
    }
    
    /**
     * Finalize package
     * 
     * @param string $packagePath Package directory path
     * @return array Result with final archive path
     */
    public function finalize($packagePath) {
        return $this->creator->finalize($packagePath);
    }
    
    /**
     * Create export package
     * 
     * @param array $files File list
     * @param string $exportName Export name
     * @param array $metadata Export metadata
     * @return array Result
     */
    public function createExportPackage($files, $exportName, $metadata = []) {
        $options = array_merge([
            'type' => 'export',
            'include_manifest' => true,
            'include_instructions' => true,
            'structure' => 'categorized'
        ], $metadata);
        
        return $this->create($files, $exportName, $options);
    }
    
    /**
     * Create backup package
     * 
     * @param array $files File list
     * @param string $backupName Backup name
     * @param array $metadata Backup metadata
     * @return array Result
     */
    public function createBackupPackage($files, $backupName, $metadata = []) {
        $options = array_merge([
            'type' => 'backup',
            'include_manifest' => true,
            'structure' => 'hierarchical',
            'preserve_structure' => true
        ], $metadata);
        
        return $this->create($files, $backupName, $options);
    }
    
    /**
     * Create migration package
     * 
     * @param array $files File list
     * @param string $migrationName Migration name
     * @param string $fromVersion Source version
     * @param string $toVersion Target version
     * @return array Result
     */
    public function createMigrationPackage($files, $migrationName, $fromVersion, $toVersion) {
        $options = [
            'type' => 'migration',
            'from_version' => $fromVersion,
            'to_version' => $toVersion,
            'include_manifest' => true,
            'include_instructions' => true
        ];
        
        return $this->create($files, $migrationName, $options);
    }
    
    /**
     * Get package information
     * 
     * @param string $packagePath Package path
     * @return array Package info
     */
    public function getPackageInfo($packagePath) {
        return $this->creator->getPackageInfo($packagePath);
    }
    
    /**
     * Validate package structure
     * 
     * @param string $packagePath Package path
     * @return array Validation result
     */
    public function validatePackage($packagePath) {
        return $this->creator->validatePackage($packagePath);
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
        if ($this->creator) {
            $this->creator->updateConfig($this->config);
        }
        if ($this->organizer) {
            $this->organizer->updateConfig($this->config);
        }
    }
}
?>
