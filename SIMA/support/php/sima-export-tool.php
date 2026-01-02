<?php
/**
 * sima-export-tool.php
 * 
 * Version: 5.0.0
 * Date: 2025-11-28
 * Purpose: SIMA Knowledge Export Tool - Main entry point
 * 
 * REFACTORED: Now uses modular system with CORRECT API calls
 */

// Start output buffering
ob_start();

// Error handling
ini_set('display_errors', '0');
error_reporting(E_ALL);
ini_set('log_errors', '1');

// Get base directory (where this script is located)
define('TOOL_BASE_DIR', __DIR__);
define('MODULES_DIR', TOOL_BASE_DIR . '/modules');

/**
 * Load all required modules
 */
function loadModules() {
    $modules = [
        'validation/validation_module.php',
        'ajax/ajax_module.php',
        'tree/tree_module.php',
        'file/file_module.php',
        'version/version_module.php',
        'manifest/manifest_module.php',
        'instructions/instructions_module.php',
        'packaging/packaging_module.php',
        'ui/ui_module.php'
    ];
    
    $missing = [];
    foreach ($modules as $module) {
        $path = MODULES_DIR . '/' . $module;
        if (!file_exists($path)) {
            $missing[] = $module;
        }
    }
    
    if (!empty($missing)) {
        throw new Exception("Missing modules: " . implode(', ', $missing));
    }
    
    foreach ($modules as $module) {
        require_once MODULES_DIR . '/' . $module;
    }
    
    // Get export directory from file config
    if (class_exists('FileConfig')) {
        $exportDir = FileConfig::getConfig('export_directory');
        if (!defined('EXPORT_DIR')) {
            define('EXPORT_DIR', $exportDir);
        }
        
        // Ensure export directory exists
        if (!is_dir(EXPORT_DIR)) {
            @mkdir(EXPORT_DIR, 0755, true);
        }
    } else {
        // Fallback if FileConfig not available
        if (!defined('EXPORT_DIR')) {
            define('EXPORT_DIR', '/tmp/sima-exports');
        }
        if (!is_dir(EXPORT_DIR)) {
            @mkdir(EXPORT_DIR, 0755, true);
        }
    }
}

/**
 * Auto-detect SIMA root directory
 */
function findSIMARoot($startPath = null) {
    if ($startPath === null) {
        $startPath = TOOL_BASE_DIR;
    }
    
    // List of allowed base directories from open_basedir
    $allowedBases = [
        '/home/joe/web/claude.dizzybeaver.com/public_html',
        '/tmp'
    ];
    
    // Check if current directory has SIMA structure
    foreach ($allowedBases as $base) {
        if (@is_dir($base . '/generic') && @is_dir($base . '/platforms')) {
            return $base;
        }
    }
    
    // Try subdirectories of allowed bases
    foreach ($allowedBases as $base) {
        if (@is_dir($base)) {
            $subdirs = @glob($base . '/*', GLOB_ONLYDIR);
            if ($subdirs) {
                foreach ($subdirs as $subdir) {
                    if (@is_dir($subdir . '/generic') && @is_dir($subdir . '/platforms')) {
                        return $subdir;
                    }
                }
            }
        }
    }
    
    // Default fallback
    return '/home/joe/web/claude.dizzybeaver.com/public_html';
}

/**
 * Main request handler
 */
class SIMAExportHandler {
    private $baseSearchDir;
    private $validation;
    private $tree;
    private $version;
    private $packaging;
    private $ajax;
    
    public function __construct($baseSearchDir) {
        $this->baseSearchDir = $baseSearchDir;
        
        // Initialize modules
        if (class_exists('ValidationModule')) {
            $this->validation = new ValidationModule();
        }
        if (class_exists('TreeModule')) {
            $this->tree = new TreeModule();
        }
        if (class_exists('VersionModule')) {
            $this->version = new VersionModule();
        }
        if (class_exists('PackagingModule')) {
            $this->packaging = new PackagingModule();
        }
        if (class_exists('AjaxModule')) {
            $this->ajax = new AjaxModule();
        }
    }
    
    public function handleRequest() {
        try {
            $action = $_GET['action'] ?? $_POST['action'] ?? null;
            
            if ($action === 'scan') {
                $this->handleScan();
            } elseif ($action === 'export') {
                $this->handleExport();
            } else {
                $this->showInterface();
            }
        } catch (Exception $e) {
            error_log("SIMA Export Error: " . $e->getMessage());
            
            if ($this->ajax) {
                $this->ajax->sendError($e->getMessage());
            } else {
                http_response_code(500);
                header('Content-Type: application/json');
                echo json_encode([
                    'success' => false,
                    'error' => $e->getMessage()
                ]);
            }
        }
    }
    
    private function handleScan() {
        $directory = $_POST['directory'] ?? '';
        
        if (empty($directory)) {
            throw new Exception("Directory path is required");
        }
        
        // Simple validation like the old code did
        $validatedPath = realpath($directory);
        if (!$validatedPath || !is_dir($validatedPath)) {
            throw new Exception("Directory does not exist or is not accessible");
        }
        
        // Check it's readable
        if (!is_readable($validatedPath)) {
            throw new Exception("Directory is not readable");
        }
        
        // Scan with version detection
        $result = $this->tree->scanWithVersion($validatedPath);
        
        // Send JSON response
        if ($this->ajax) {
            $this->ajax->sendSuccess($result);
        } else {
            header('Content-Type: application/json');
            echo json_encode(array_merge(['success' => true], $result));
        }
    }
    
    private function handleExport() {
        $directory = $_POST['directory'] ?? '';
        $archiveName = $_POST['archive_name'] ?? 'SIMA-Export';
        $description = $_POST['description'] ?? '';
        $selectedFiles = json_decode($_POST['selected_files'] ?? '[]', true);
        $sourceVersion = $_POST['source_version'] ?? 'auto';
        $targetVersion = $_POST['target_version'] ?? 'auto';
        
        if (empty($directory)) {
            throw new Exception("Directory path is required");
        }
        
        // Simple validation like the old code did
        $validatedPath = realpath($directory);
        if (!$validatedPath || !is_dir($validatedPath)) {
            throw new Exception("Directory does not exist or is not accessible");
        }
        
        if (empty($selectedFiles)) {
            throw new Exception("No files selected for export");
        }
        
        // Auto-detect versions if needed
        if ($sourceVersion === 'auto' && $this->version) {
            $versionInfo = $this->version->detect($validatedPath);
            $sourceVersion = $versionInfo['version'] ?? 'unknown';
        }
        
        if ($targetVersion === 'auto') {
            $targetVersion = $sourceVersion;
        }
        
        // Create export package
        $result = $this->packaging->createExportPackage($selectedFiles, $archiveName, [
            'description' => $description,
            'source_version' => $sourceVersion,
            'target_version' => $targetVersion
        ]);
        
        // Generate download URL
        $exportDir = defined('EXPORT_DIR') ? EXPORT_DIR : '/tmp/sima-exports';
        $downloadUrl = $exportDir . '/' . $result['archive_name'];
        
        // Send JSON response
        $responseData = [
            'archive_name' => $result['archive_name'],
            'file_count' => $result['file_count'] ?? count($selectedFiles),
            'converted_count' => $result['converted_count'] ?? 0,
            'download_url' => $downloadUrl
        ];
        
        if ($this->ajax) {
            $this->ajax->sendSuccess($responseData);
        } else {
            header('Content-Type: application/json');
            echo json_encode(array_merge(['success' => true], $responseData));
        }
    }
    
    private function showInterface() {
        // Generate form
        $formHtml = ui_generateForm([
            [
                'type' => 'text',
                'name' => 'directory',
                'label' => 'SIMA Directory Path',
                'placeholder' => '/path/to/sima',
                'required' => true,
                'attributes' => ['id' => 'directory']
            ],
            [
                'type' => 'text',
                'name' => 'archive_name',
                'label' => 'Archive Name',
                'value' => 'SIMA-Export',
                'attributes' => ['id' => 'archiveName']
            ],
            [
                'type' => 'textarea',
                'name' => 'description',
                'label' => 'Description',
                'rows' => 3,
                'attributes' => ['id' => 'description']
            ]
        ], [
            'id' => 'exportForm',
            'submit_text' => 'Scan Directory'
        ]);
        
        // Wrap form in container
        $content = ui_generateContainer($formHtml, [
            'title' => 'Step 1: Scan Directory'
        ]);
        
        // Add status container
        $content .= ui_generateStatusContainer('status');
        
        // Add loading indicator
        $content .= ui_generateLoadingIndicator([
            'id' => 'loading',
            'hidden' => true
        ]);
        
        // Add results container
        $content .= ui_generateContainer('', [
            'id' => 'results',
            'title' => 'Step 2: Select Files',
            'class' => 'hidden'
        ]);
        
        // Add export button container
        $content .= '<div id="exportButtonContainer" class="hidden">';
        $content .= ui_generateButton('Export Selected Files', [
            'id' => 'exportButton',
            'onclick' => 'exportFiles()',
            'style' => 'primary'
        ]);
        $content .= '</div>';
        
        // Generate complete page
        $page = ui_generatePageHeader('SIMA Export Tool', [
            'description' => 'Export SIMA knowledge for sharing or backup',
            'version' => '5.0.0',
            'include_assets' => true
        ]);
        
        // Add CSS
        $page .= ui_generateCssIncludes('sima-styles.css', [
            'base_path' => dirname($_SERVER['SCRIPT_NAME'])
        ]);
        
        $page .= $content;
        
        // Add JavaScript
        $page .= ui_generateJsIncludes([
            'sima-export-scan.js',
            'sima-export-render.js',
            'sima-export-selection.js',
            'sima-export-export.js'
        ], [
            'base_path' => dirname($_SERVER['SCRIPT_NAME']),
            'defer' => true
        ]);
        
        $page .= ui_generatePageFooter([
            'show_timestamp' => true
        ]);
        
        ob_clean();
        echo $page;
    }
}

// Main execution
try {
    // Load all modules (this also sets EXPORT_DIR from FileConfig)
    loadModules();
    
    // Find SIMA root
    $simaRoot = findSIMARoot();
    
    // Create handler and process request
    $handler = new SIMAExportHandler($simaRoot);
    $handler->handleRequest();
    
} catch (Exception $e) {
    ob_clean();
    header('Content-Type: application/json');
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
    exit;
}
