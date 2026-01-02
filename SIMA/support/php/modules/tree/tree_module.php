<?php
/**
 * tree_module.php
 * 
 * SIMA Tree Module - Public API
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Public interface for tree scanning, formatting, and rendering
 */

class TreeModule {
    private $config;
    private $scanner;
    private $formatter;
    private $version;
    
    /**
     * Initialize tree module
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
            $this->config = require __DIR__ . '/tree_config.php';
        }
        
        // Load internal components
        require_once __DIR__ . '/internal/tree_scanner.php';
        require_once __DIR__ . '/internal/tree_formatter.php';
        require_once __DIR__ . '/internal/tree_version.php';
        
        $this->scanner = new TreeScanner($this->config);
        $this->formatter = new TreeFormatter($this->config);
        $this->version = new TreeVersion($this->config);
    }
    
    /**
     * Scan directory and return raw tree structure
     * 
     * @param string $basePath Directory to scan
     * @param array $options Override config options
     * @return array Raw tree structure
     */
    public function scan($basePath, $options = []) {
        $scanOptions = array_merge($this->config['scan'], $options);
        return $this->scanner->scanComplete($basePath, $scanOptions);
    }
    
    /**
     * Scan and format for UI in one call
     * 
     * @param string $basePath Directory to scan
     * @param array $options Override config options
     * @return array UI-ready tree structure
     */
    public function scanForUI($basePath, $options = []) {
        $rawTree = $this->scan($basePath, $options);
        return $this->formatter->formatForUI($rawTree);
    }
    
    /**
     * Format raw tree for UI display
     * 
     * @param array $rawTree Raw tree from scan()
     * @return array UI-ready tree structure
     */
    public function formatForUI($rawTree) {
        return $this->formatter->formatForUI($rawTree);
    }
    
    /**
     * Get flat list of all files
     * 
     * @param array $rawTree Raw tree from scan()
     * @return array Flat array of files
     */
    public function getFlatFileList($rawTree) {
        return $this->formatter->getFlatFileList($rawTree);
    }
    
    /**
     * Group files by category
     * 
     * @param array $rawTree Raw tree from scan()
     * @return array Files grouped by category
     */
    public function groupByCategory($rawTree) {
        return $this->formatter->groupByCategory($rawTree);
    }
    
    /**
     * Generate statistics
     * 
     * @param array $rawTree Raw tree from scan()
     * @return array Statistics
     */
    public function generateStats($rawTree) {
        return $this->formatter->generateStats($rawTree);
    }
    
    /**
     * Filter tree by criteria
     * 
     * @param array $rawTree Raw tree from scan()
     * @param array $criteria Filter criteria
     * @return array Filtered tree
     */
    public function filterTree($rawTree, $criteria) {
        return $this->formatter->filterTree($rawTree, $criteria);
    }
    
    /**
     * Detect version of scanned directory
     * 
     * @param string $basePath Directory to check
     * @return string Version string or 'unknown'
     */
    public function detectVersion($basePath) {
        return $this->version->detectVersion($basePath);
    }
    
    /**
     * Get version information
     * 
     * @param string $basePath Directory to check
     * @return array Version information
     */
    public function getVersionInfo($basePath) {
        return $this->version->getVersionInfo($basePath);
    }
    
    /**
     * Scan with version detection
     * 
     * @param string $basePath Directory to scan
     * @param string $version Optional version override
     * @return array UI-ready tree with version info
     */
    public function scanWithVersion($basePath, $version = null) {
        if ($version === null) {
            $version = $this->version->detectVersion($basePath);
        }
        
        $rawTree = $this->scan($basePath);
        $uiTree = $this->formatForUI($rawTree);
        
        return [
            'tree' => $uiTree,
            'version' => $version,
            'version_info' => $this->version->getVersionInfo($basePath),
            'stats' => $this->generateStats($rawTree),
            'base_path' => realpath($basePath)
        ];
    }
    
    /**
     * Get asset paths for CSS and JS
     * 
     * @param string $scriptPath Path to calling script
     * @return array Paths to CSS and JS directories
     */
    public function getAssetPaths($scriptPath = null) {
        if ($scriptPath === null) {
            $scriptPath = $_SERVER['SCRIPT_NAME'];
        }
        
        $scriptDir = dirname($scriptPath);
        $treeModulePath = '/modules/tree';
        
        return [
            'css' => $scriptDir . $treeModulePath . '/' . $this->config['assets']['css_path'],
            'js' => $scriptDir . $treeModulePath . '/' . $this->config['assets']['js_path']
        ];
    }
    
    /**
     * Generate HTML for CSS includes
     * 
     * @return string HTML link tags
     */
    public function getCSSIncludes() {
        $paths = $this->getAssetPaths();
        $html = '';
        
        if (file_exists(__DIR__ . '/css/tree.css')) {
            $html .= '<link rel="stylesheet" href="' . $paths['css'] . '/tree.css">' . "\n";
        }
        
        return $html;
    }
    
    /**
     * Generate HTML for JS includes
     * 
     * @return string HTML script tags
     */
    public function getJSIncludes() {
        $paths = $this->getAssetPaths();
        $html = '';
        
        $jsFiles = ['tree_render.js', 'tree_interact.js'];
        
        foreach ($jsFiles as $file) {
            if (file_exists(__DIR__ . '/js/' . $file)) {
                $html .= '<script src="' . $paths['js'] . '/' . $file . '"></script>' . "\n";
            }
        }
        
        return $html;
    }
    
    /**
     * Send JSON response
     * 
     * @param bool $success Success flag
     * @param array $data Data to return
     * @param string $error Error message if failed
     */
    public function sendJSON($success, $data = [], $error = null) {
        while (ob_get_level()) ob_end_clean();
        
        header('Content-Type: application/json');
        header('Cache-Control: no-cache, no-store, must-revalidate');
        
        $response = ['success' => $success];
        
        if ($success) {
            $response = array_merge($response, $data);
        } else {
            $response['error'] = $error;
        }
        
        echo json_encode($response);
        exit;
    }
    
    /**
     * Handle AJAX scan request
     * Expects POST with 'directory' parameter
     */
    public function handleScanRequest() {
        try {
            $directory = $_POST['directory'] ?? '';
            
            if (empty($directory)) {
                throw new Exception("Directory path required");
            }
            
            $directory = rtrim($directory, '/');
            
            if (!is_dir($directory)) {
                throw new Exception("Directory not found: {$directory}");
            }
            
            if (!is_readable($directory)) {
                throw new Exception("Directory not readable: {$directory}");
            }
            
            $result = $this->scanWithVersion($directory);
            
            $this->sendJSON(true, $result);
            
        } catch (Exception $e) {
            $this->sendJSON(false, [], $e->getMessage());
        }
    }
    
    /**
     * Get configuration value
     * 
     * @param string $key Dot-notation key (e.g., 'scan.max_depth')
     * @param mixed $default Default value if not found
     * @return mixed Configuration value
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
     * @param string $key Dot-notation key
     * @param mixed $value Value to set
     */
    public function setConfig($key, $value) {
        $keys = explode('.', $key);
        $config = &$this->config;
        
        foreach ($keys as $k) {
            if (!isset($config[$k])) {
                $config[$k] = [];
            }
            $config = &$config[$k];
        }
        
        $config = $value;
    }
}
