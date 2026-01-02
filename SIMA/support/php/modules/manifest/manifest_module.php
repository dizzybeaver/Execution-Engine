<?php
/**
 * manifest_module.php
 * 
 * SIMA Manifest Module - Public API
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Public interface for manifest generation, validation, and parsing
 */

class ManifestModule {
    private $config;
    private $generator;
    private $validator;
    private $parser;
    
    /**
     * Initialize manifest module
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
            $this->config = require __DIR__ . '/manifest_config.php';
        }
        
        // Load internal components
        require_once __DIR__ . '/internal/manifest_generator.php';
        require_once __DIR__ . '/internal/manifest_validator.php';
        require_once __DIR__ . '/internal/manifest_parser.php';
        
        $this->generator = new ManifestGenerator($this->config);
        $this->validator = new ManifestValidator($this->config);
        $this->parser = new ManifestParser($this->config);
    }
    
    /**
     * Generate manifest for operation
     * 
     * @param string $operation Operation type (export/import/update)
     * @param array $files File list with metadata
     * @param array $metadata Additional metadata
     * @return string YAML manifest content
     */
    public function generate($operation, $files, $metadata = []) {
        return $this->generator->generate($operation, $files, $metadata);
    }
    
    /**
     * Generate and save manifest to file
     * 
     * @param string $operation Operation type
     * @param array $files File list
     * @param string $outputPath Path to save manifest
     * @param array $metadata Additional metadata
     * @return array Result with success and path
     */
    public function generateToFile($operation, $files, $outputPath, $metadata = []) {
        $content = $this->generate($operation, $files, $metadata);
        
        $dir = dirname($outputPath);
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        
        if (file_put_contents($outputPath, $content) === false) {
            return ['error' => 'Failed to write manifest file'];
        }
        
        return [
            'success' => true,
            'path' => $outputPath,
            'size' => strlen($content)
        ];
    }
    
    /**
     * Validate manifest file
     * 
     * @param string $manifestPath Path to manifest file
     * @return array Validation result
     */
    public function validate($manifestPath) {
        return $this->validator->validateFile($manifestPath);
    }
    
    /**
     * Validate manifest content
     * 
     * @param string $manifestContent YAML content
     * @return array Validation result
     */
    public function validateContent($manifestContent) {
        return $this->validator->validateContent($manifestContent);
    }
    
    /**
     * Parse manifest file
     * 
     * @param string $manifestPath Path to manifest file
     * @return array Parsed manifest data or error
     */
    public function parse($manifestPath) {
        return $this->parser->parseFile($manifestPath);
    }
    
    /**
     * Parse manifest content
     * 
     * @param string $manifestContent YAML content
     * @return array Parsed manifest data or error
     */
    public function parseContent($manifestContent) {
        return $this->parser->parseContent($manifestContent);
    }
    
    /**
     * Merge two manifests
     * 
     * @param array $manifest1 First manifest (parsed)
     * @param array $manifest2 Second manifest (parsed)
     * @return array Merged manifest
     */
    public function merge($manifest1, $manifest2) {
        return $this->generator->merge($manifest1, $manifest2);
    }
    
    /**
     * Get file inventory from manifest
     * 
     * @param string $manifestPath Path to manifest file
     * @return array File list or error
     */
    public function getFileInventory($manifestPath) {
        $parsed = $this->parse($manifestPath);
        
        if (isset($parsed['error'])) {
            return $parsed;
        }
        
        return [
            'success' => true,
            'files' => $parsed['files'] ?? [],
            'total' => count($parsed['files'] ?? [])
        ];
    }
    
    /**
     * Get statistics from manifest
     * 
     * @param string $manifestPath Path to manifest file
     * @return array Statistics or error
     */
    public function getStatistics($manifestPath) {
        $parsed = $this->parse($manifestPath);
        
        if (isset($parsed['error'])) {
            return $parsed;
        }
        
        return $this->generator->generateStatistics($parsed['files'] ?? []);
    }
    
    /**
     * Add files to existing manifest
     * 
     * @param string $manifestPath Path to existing manifest
     * @param array $newFiles Files to add
     * @return array Result
     */
    public function addFiles($manifestPath, $newFiles) {
        $parsed = $this->parse($manifestPath);
        
        if (isset($parsed['error'])) {
            return $parsed;
        }
        
        $parsed['files'] = array_merge($parsed['files'] ?? [], $newFiles);
        $parsed['archive']['total_files'] = count($parsed['files']);
        
        $content = $this->generator->arrayToYaml($parsed);
        
        if (file_put_contents($manifestPath, $content) === false) {
            return ['error' => 'Failed to update manifest'];
        }
        
        return [
            'success' => true,
            'total_files' => count($parsed['files'])
        ];
    }
    
    /**
     * Remove files from manifest
     * 
     * @param string $manifestPath Path to manifest
     * @param array $filesToRemove Array of filenames to remove
     * @return array Result
     */
    public function removeFiles($manifestPath, $filesToRemove) {
        $parsed = $this->parse($manifestPath);
        
        if (isset($parsed['error'])) {
            return $parsed;
        }
        
        $parsed['files'] = array_filter($parsed['files'] ?? [], function($file) use ($filesToRemove) {
            return !in_array($file['filename'] ?? '', $filesToRemove);
        });
        
        $parsed['archive']['total_files'] = count($parsed['files']);
        
        $content = $this->generator->arrayToYaml($parsed);
        
        if (file_put_contents($manifestPath, $content) === false) {
            return ['error' => 'Failed to update manifest'];
        }
        
        return [
            'success' => true,
            'total_files' => count($parsed['files'])
        ];
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
        if ($this->validator) {
            $this->validator->updateConfig($this->config);
        }
        if ($this->parser) {
            $this->parser->updateConfig($this->config);
        }
    }
    
    /**
     * Compare two manifests
     * 
     * @param string $manifestPath1 First manifest
     * @param string $manifestPath2 Second manifest
     * @return array Comparison result
     */
    public function compare($manifestPath1, $manifestPath2) {
        $m1 = $this->parse($manifestPath1);
        $m2 = $this->parse($manifestPath2);
        
        if (isset($m1['error'])) {
            return $m1;
        }
        if (isset($m2['error'])) {
            return $m2;
        }
        
        return $this->generator->compare($m1, $m2);
    }
}
?>
