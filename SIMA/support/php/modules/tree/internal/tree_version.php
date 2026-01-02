<?php
/**
 * tree_version.php
 * 
 * Internal: Version detection functionality
 * Version: 1.0.0
 * Date: 2025-11-27
 */

class TreeVersion {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    /**
     * Detect version from directory structure
     */
    public function detectVersion($basePath) {
        if (!is_dir($basePath) || !is_readable($basePath)) {
            return 'unknown';
        }
        
        // v4.2+ (generic/ and platforms/ directories)
        if (is_dir($basePath . '/generic') && is_dir($basePath . '/platforms')) {
            return '4.2';
        }
        
        // v4.1 (entries/ and integration/ directories)
        if (is_dir($basePath . '/entries') && is_dir($basePath . '/integration')) {
            return '4.1';
        }
        
        // v3.0 (NM## directories)
        if (is_dir($basePath . '/NM00') && is_dir($basePath . '/NM01')) {
            return '3.0';
        }
        
        return 'unknown';
    }
    
    /**
     * Get version information
     */
    public function getVersionInfo($basePath) {
        $version = $this->detectVersion($basePath);
        
        $info = [
            'version' => $version,
            'detected' => $version !== 'unknown',
            'base_path' => realpath($basePath)
        ];
        
        if ($version === '4.2' || $version === '4.3') {
            $info['domains'] = ['generic', 'platforms', 'languages', 'projects'];
            $info['support_dirs'] = ['context', 'docs', 'support', 'templates'];
        } elseif ($version === '4.1') {
            $info['domains'] = ['entries', 'integration'];
        } elseif ($version === '3.0') {
            $info['domains'] = $this->getNM00Directories($basePath);
        }
        
        return $info;
    }
    
    /**
     * Get NM directories for v3.0
     */
    private function getNM00Directories($basePath) {
        $dirs = [];
        $entries = scandir($basePath);
        
        foreach ($entries as $entry) {
            if (preg_match('/^NM\d{2}$/', $entry)) {
                $dirs[] = $entry;
            }
        }
        
        sort($dirs);
        return $dirs;
    }
}
