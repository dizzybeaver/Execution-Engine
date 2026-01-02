<?php
/**
 * version_module.php
 * 
 * SIMA Version Module - Public API
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Public interface for version detection, conversion, and compatibility
 */

class VersionModule {
    private $config;
    private $detector;
    private $converter;
    private $compatibility;
    
    /**
     * Initialize version module
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
            $this->config = require __DIR__ . '/version_config.php';
        }
        
        // Load internal components
        require_once __DIR__ . '/internal/version_detector.php';
        require_once __DIR__ . '/internal/version_converter.php';
        require_once __DIR__ . '/internal/version_compatibility.php';
        
        $this->detector = new VersionDetector($this->config);
        $this->converter = new VersionConverter($this->config);
        $this->compatibility = new VersionCompatibility($this->config);
    }
    
    /**
     * Detect version from directory structure
     * 
     * @param string $basePath Base directory path
     * @return array Version info or error
     */
    public function detect($basePath) {
        return $this->detector->detect($basePath);
    }
    
    /**
     * Detect version from file
     * 
     * @param string $filePath File path
     * @return array Version info or error
     */
    public function detectFromFile($filePath) {
        return $this->detector->detectFromFile($filePath);
    }
    
    /**
     * Get version information
     * 
     * @param string $version Version string
     * @return array Version details
     */
    public function getVersionInfo($version) {
        return $this->detector->getVersionInfo($version);
    }
    
    /**
     * Convert content between versions
     * 
     * @param string $content File content
     * @param string $fromVersion Source version
     * @param string $toVersion Target version
     * @return string Converted content
     */
    public function convert($content, $fromVersion, $toVersion) {
        return $this->converter->convert($content, $fromVersion, $toVersion);
    }
    
    /**
     * Convert file between versions
     * 
     * @param string $filePath File path
     * @param string $toVersion Target version
     * @return array Result with success and converted content
     */
    public function convertFile($filePath, $toVersion) {
        if (!file_exists($filePath)) {
            return ['error' => 'File does not exist'];
        }
        
        $content = file_get_contents($filePath);
        $versionInfo = $this->detectFromFile($filePath);
        
        if (isset($versionInfo['error'])) {
            return $versionInfo;
        }
        
        $fromVersion = $versionInfo['version'];
        $converted = $this->convert($content, $fromVersion, $toVersion);
        
        return [
            'success' => true,
            'content' => $converted,
            'from_version' => $fromVersion,
            'to_version' => $toVersion
        ];
    }
    
    /**
     * Batch convert files
     * 
     * @param array $files File list with paths
     * @param string $toVersion Target version
     * @return array Results
     */
    public function batchConvert($files, $toVersion) {
        return $this->converter->batchConvert($files, $toVersion);
    }
    
    /**
     * Check if conversion is possible
     * 
     * @param string $fromVersion Source version
     * @param string $toVersion Target version
     * @return bool True if conversion supported
     */
    public function canConvert($fromVersion, $toVersion) {
        return $this->compatibility->canConvert($fromVersion, $toVersion);
    }
    
    /**
     * Check version compatibility
     * 
     * @param string $version1 First version
     * @param string $version2 Second version
     * @return array Compatibility info
     */
    public function checkCompatibility($version1, $version2) {
        return $this->compatibility->checkCompatibility($version1, $version2);
    }
    
    /**
     * Add version tags to content
     * 
     * @param string $content File content
     * @param string $version Version to tag
     * @param array $metadata Additional metadata
     * @return string Content with version tags
     */
    public function addVersionTags($content, $version, $metadata = []) {
        return $this->converter->addVersionTags($content, $version, $metadata);
    }
    
    /**
     * Remove version tags from content
     * 
     * @param string $content File content
     * @return string Content without version tags
     */
    public function removeVersionTags($content) {
        return $this->converter->removeVersionTags($content);
    }
    
    /**
     * Extract version from content
     * 
     * @param string $content File content
     * @return string|null Version string or null
     */
    public function extractVersion($content) {
        return $this->detector->extractVersionFromContent($content);
    }
    
    /**
     * Compare versions
     * 
     * @param string $version1 First version
     * @param string $version2 Second version
     * @return int -1 if v1 < v2, 0 if equal, 1 if v1 > v2
     */
    public function compare($version1, $version2) {
        return $this->compatibility->compare($version1, $version2);
    }
    
    /**
     * Get supported versions
     * 
     * @return array List of supported versions
     */
    public function getSupportedVersions() {
        return $this->config['supported_versions'];
    }
    
    /**
     * Get latest version
     * 
     * @return string Latest version string
     */
    public function getLatestVersion() {
        $versions = $this->config['supported_versions'];
        usort($versions, [$this->compatibility, 'compare']);
        return end($versions);
    }
    
    /**
     * Validate version string
     * 
     * @param string $version Version string
     * @return bool True if valid
     */
    public function isValidVersion($version) {
        return $this->compatibility->isValidVersion($version);
    }
    
    /**
     * Get conversion path
     * 
     * @param string $fromVersion Source version
     * @param string $toVersion Target version
     * @return array Conversion steps
     */
    public function getConversionPath($fromVersion, $toVersion) {
        return $this->compatibility->getConversionPath($fromVersion, $toVersion);
    }
    
    /**
     * Register custom converter
     * 
     * @param string $fromVersion Source version
     * @param string $toVersion Target version
     * @param callable $callback Conversion function
     */
    public function registerConverter($fromVersion, $toVersion, $callback) {
        $this->converter->registerConverter($fromVersion, $toVersion, $callback);
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
        if ($this->detector) {
            $this->detector->updateConfig($this->config);
        }
        if ($this->converter) {
            $this->converter->updateConfig($this->config);
        }
        if ($this->compatibility) {
            $this->compatibility->updateConfig($this->config);
        }
    }
}
?>
