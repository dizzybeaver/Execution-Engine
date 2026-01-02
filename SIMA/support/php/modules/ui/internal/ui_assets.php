<?php
/**
 * ui_assets.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-28
 * Purpose: SIMA-ui Module - Asset management (CSS/JS includes, paths)
 * Module: SIMA-ui
 * Location: internal/
 * 
 * INTERNAL USE ONLY - Do not call these functions directly
 * Use the public API in ui_module.php instead
 * 
 * MODIFIED: Moved to internal/ directory, added proper header
 */

/**
 * Build CSS include tags
 * 
 * @internal
 */
function _ui_buildCssIncludes($css_files, $options) {
    $defaults = [
        'base_path' => null,
        'version' => UI_USE_CACHE_BUSTING ? UI_ASSET_VERSION : null
    ];
    $options = array_merge($defaults, $options);
    
    // Normalize to array
    if (!is_array($css_files)) {
        $css_files = [$css_files];
    }
    
    // Determine base path
    if ($options['base_path'] === null) {
        $options['base_path'] = _ui_determineAssetBasePath();
    }
    
    $html = '';
    
    foreach ($css_files as $css_file) {
        $url = rtrim($options['base_path'], '/') . '/' . UI_DEFAULT_CSS_PATH . ltrim($css_file, '/');
        
        // Add version for cache busting
        if ($options['version']) {
            $url .= '?v=' . $options['version'];
        }
        
        $html .= "<link rel=\"stylesheet\" href=\"" . ui_escape($url) . "\">\n";
    }
    
    return $html;
}

/**
 * Build JavaScript include tags
 * 
 * @internal
 */
function _ui_buildJsIncludes($js_files, $options) {
    $defaults = [
        'base_path' => null,
        'version' => UI_USE_CACHE_BUSTING ? UI_ASSET_VERSION : null,
        'defer' => false,
        'async' => false
    ];
    $options = array_merge($defaults, $options);
    
    // Normalize to array
    if (!is_array($js_files)) {
        $js_files = [$js_files];
    }
    
    // Determine base path
    if ($options['base_path'] === null) {
        $options['base_path'] = _ui_determineAssetBasePath();
    }
    
    $html = '';
    
    foreach ($js_files as $js_file) {
        $url = rtrim($options['base_path'], '/') . '/' . UI_DEFAULT_JS_PATH . ltrim($js_file, '/');
        
        // Add version for cache busting
        if ($options['version']) {
            $url .= '?v=' . $options['version'];
        }
        
        $html .= "<script src=\"" . ui_escape($url) . "\"";
        
        if ($options['defer']) {
            $html .= " defer";
        }
        
        if ($options['async']) {
            $html .= " async";
        }
        
        $html .= "></script>\n";
    }
    
    return $html;
}

/**
 * Determine asset base path
 * 
 * @internal
 */
function _ui_determineAssetBasePath($script_path = null) {
    if ($script_path === null) {
        // Use the calling script's directory
        $script_path = $_SERVER['SCRIPT_FILENAME'] ?? __FILE__;
    }
    
    // Get directory of the script
    $script_dir = dirname($script_path);
    
    // Get the web-accessible path
    $document_root = $_SERVER['DOCUMENT_ROOT'] ?? '';
    
    if (!empty($document_root) && strpos($script_dir, $document_root) === 0) {
        // Calculate relative path from document root
        $relative_path = substr($script_dir, strlen($document_root));
        $base_path = rtrim($relative_path, '/');
    } else {
        // Fallback to current directory
        $base_path = dirname($_SERVER['SCRIPT_NAME'] ?? '');
    }
    
    return $base_path ?: '/';
}

/**
 * Get full URL for asset
 * 
 * @internal
 */
function _ui_getAssetUrl($asset_path, $type = 'css', $options = []) {
    $defaults = [
        'base_path' => null,
        'version' => UI_USE_CACHE_BUSTING ? UI_ASSET_VERSION : null
    ];
    $options = array_merge($defaults, $options);
    
    if ($options['base_path'] === null) {
        $options['base_path'] = _ui_determineAssetBasePath();
    }
    
    $type_path = ($type === 'css') ? UI_DEFAULT_CSS_PATH : UI_DEFAULT_JS_PATH;
    $url = rtrim($options['base_path'], '/') . '/' . $type_path . ltrim($asset_path, '/');
    
    if ($options['version']) {
        $url .= '?v=' . $options['version'];
    }
    
    return $url;
}

/**
 * Generate inline CSS
 * 
 * @internal
 */
function _ui_generateInlineCss($css_content) {
    return "<style>\n" . $css_content . "\n</style>\n";
}

/**
 * Generate inline JavaScript
 * 
 * @internal
 */
function _ui_generateInlineJs($js_content) {
    return "<script>\n" . $js_content . "\n</script>\n";
}

/**
 * Build complete asset includes (CSS + JS)
 * 
 * @internal
 */
function _ui_buildAssetIncludes($css_files, $js_files, $options = []) {
    $html = '';
    
    // CSS includes
    if (!empty($css_files)) {
        $html .= _ui_buildCssIncludes($css_files, $options);
    }
    
    // JS includes
    if (!empty($js_files)) {
        $html .= _ui_buildJsIncludes($js_files, $options);
    }
    
    return $html;
}

/**
 * Validate asset path for security
 * 
 * @internal
 */
function _ui_validateAssetPath($path) {
    // Check for directory traversal attempts
    if (strpos($path, '..') !== false) {
        return false;
    }
    
    // Check for absolute paths
    if (strpos($path, '/') === 0 || preg_match('/^[a-z]:\\\\/i', $path)) {
        return false;
    }
    
    // Check for protocol handlers
    if (preg_match('/^[a-z]+:/i', $path)) {
        return false;
    }
    
    return true;
}

/**
 * Get asset file extension
 * 
 * @internal
 */
function _ui_getAssetExtension($filename) {
    $parts = explode('.', $filename);
    return strtolower(end($parts));
}

/**
 * Check if asset is CSS
 * 
 * @internal
 */
function _ui_isCssAsset($filename) {
    return _ui_getAssetExtension($filename) === 'css';
}

/**
 * Check if asset is JavaScript
 * 
 * @internal
 */
function _ui_isJsAsset($filename) {
    $ext = _ui_getAssetExtension($filename);
    return in_array($ext, ['js', 'mjs']);
}

/**
 * Generate cache-busting parameter
 * 
 * @internal
 */
function _ui_generateCacheBuster($file_path = null) {
    if ($file_path && file_exists($file_path)) {
        // Use file modification time
        return filemtime($file_path);
    }
    
    // Fallback to current time
    return time();
}

/**
 * Build preload hints for assets
 * 
 * @internal
 */
function _ui_buildPreloadHints($css_files, $js_files, $options = []) {
    $html = '';
    
    $base_path = $options['base_path'] ?? _ui_determineAssetBasePath();
    
    // CSS preloads
    if (!empty($css_files)) {
        $files = is_array($css_files) ? $css_files : [$css_files];
        foreach ($files as $file) {
            $url = rtrim($base_path, '/') . '/' . UI_DEFAULT_CSS_PATH . ltrim($file, '/');
            $html .= "<link rel=\"preload\" href=\"" . ui_escape($url) . 
                     "\" as=\"style\">\n";
        }
    }
    
    // JS preloads
    if (!empty($js_files)) {
        $files = is_array($js_files) ? $js_files : [$js_files];
        foreach ($files as $file) {
            $url = rtrim($base_path, '/') . '/' . UI_DEFAULT_JS_PATH . ltrim($file, '/');
            $html .= "<link rel=\"preload\" href=\"" . ui_escape($url) . 
                     "\" as=\"script\">\n";
        }
    }
    
    return $html;
}
