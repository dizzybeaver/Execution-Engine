<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
/**
 * sima-export-tool.php
 * 
 * SIMA Knowledge Export Tool - Fixed Modular Version
 * Version: 4.4.1
 * Date: 2025-11-23
 * 
 * FIXED: JSON response issues, clean output buffering
 */

// Configuration - Set this to your base search directory
$BASE_SEARCH_DIR = '/home/joe/web/claude.dizzybeaver.com/public_html';

// Start output buffering with error suppression
if (ob_get_level()) ob_end_clean();
ob_start();

// Error handling - suppress display but log
ini_set('display_errors', '0');
error_reporting(E_ALL);
ini_set('log_errors', '1');

// Define export directory within allowed paths
if (!defined('EXPORT_DIR')) {
    define('EXPORT_DIR', __DIR__ . '/exports');
}

// Load the main handler
require_once __DIR__ . '/sima-export-handler.php';

// Handle AJAX requests
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Clear any previous output
    while (ob_get_level()) ob_end_clean();
    
    $handler = new SIMAExportHandler($BASE_SEARCH_DIR);
    $handler->handleRequest();
    exit;
}

// Show HTML interface
$handler = new SIMAExportHandler($BASE_SEARCH_DIR);
$handler->showInterface();
?>
