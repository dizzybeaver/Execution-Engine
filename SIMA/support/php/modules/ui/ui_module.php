<?php
/**
 * ui_module.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-28
 * Purpose: SIMA-ui Module - Public API for UI component generation
 * Module: SIMA-ui
 * 
 * PUBLIC API - All public-facing functions
 * Use this file for all external calls to the module
 * 
 * MODIFIED: Added proper header with version and date
 */

// Prevent direct access
if (!defined('SIMA_MODULE_UI')) {
    define('SIMA_MODULE_UI', true);
}

// Load configuration
require_once __DIR__ . '/ui_config.php';

// Load internal components
require_once __DIR__ . '/internal/ui_components.php';
require_once __DIR__ . '/internal/ui_assets.php';
require_once __DIR__ . '/internal/ui_layouts.php';
require_once __DIR__ . '/internal/ui_forms.php';

/**
 * Generate page header HTML
 * 
 * @param string $title Page title
 * @param array $options Optional settings
 *   - 'description' => string Page description
 *   - 'version' => string Version to display
 *   - 'include_assets' => bool Auto-include CSS/JS (default: true)
 * @return string HTML header
 */
function ui_generatePageHeader($title, $options = []) {
    $defaults = [
        'description' => '',
        'version' => '',
        'include_assets' => true
    ];
    $options = array_merge($defaults, $options);
    
    return _ui_buildPageHeader($title, $options);
}

/**
 * Generate page footer HTML
 * 
 * @param array $options Optional settings
 *   - 'footer_text' => string Custom footer text
 *   - 'show_timestamp' => bool Show generated timestamp
 * @return string HTML footer
 */
function ui_generatePageFooter($options = []) {
    $defaults = [
        'footer_text' => '',
        'show_timestamp' => false
    ];
    $options = array_merge($defaults, $options);
    
    return _ui_buildPageFooter($options);
}

/**
 * Generate complete page layout
 * 
 * @param string $title Page title
 * @param string $content Page content HTML
 * @param array $options Optional settings
 * @return string Complete HTML page
 */
function ui_generatePage($title, $content, $options = []) {
    return _ui_buildCompletePage($title, $content, $options);
}

/**
 * Generate form input field
 * 
 * @param string $type Input type (text, number, checkbox, etc.)
 * @param string $name Field name
 * @param array $options Optional settings
 *   - 'id' => string Field ID
 *   - 'value' => string Default value
 *   - 'label' => string Field label
 *   - 'placeholder' => string Placeholder text
 *   - 'required' => bool Required field
 *   - 'attributes' => array Additional HTML attributes
 * @return string HTML input field
 */
function ui_generateInput($type, $name, $options = []) {
    return _ui_buildInput($type, $name, $options);
}

/**
 * Generate form textarea
 * 
 * @param string $name Field name
 * @param array $options Optional settings
 * @return string HTML textarea
 */
function ui_generateTextarea($name, $options = []) {
    return _ui_buildTextarea($name, $options);
}

/**
 * Generate form select dropdown
 * 
 * @param string $name Field name
 * @param array $options_list Key-value pairs for options
 * @param array $options Optional settings
 * @return string HTML select
 */
function ui_generateSelect($name, $options_list, $options = []) {
    return _ui_buildSelect($name, $options_list, $options);
}

/**
 * Generate button
 * 
 * @param string $text Button text
 * @param array $options Optional settings
 *   - 'type' => string Button type (button, submit, reset)
 *   - 'id' => string Button ID
 *   - 'class' => string Additional CSS classes
 *   - 'onclick' => string JavaScript onclick handler
 *   - 'disabled' => bool Disabled state
 *   - 'style' => string Button style (primary, secondary, danger)
 * @return string HTML button
 */
function ui_generateButton($text, $options = []) {
    return _ui_buildButton($text, $options);
}

/**
 * Generate form group (label + input wrapper)
 * 
 * @param string $label Label text
 * @param string $input_html Input field HTML
 * @param array $options Optional settings
 *   - 'help_text' => string Help text below input
 *   - 'error' => string Error message
 *   - 'required' => bool Show required indicator
 * @return string HTML form group
 */
function ui_generateFormGroup($label, $input_html, $options = []) {
    return _ui_buildFormGroup($label, $input_html, $options);
}

/**
 * Generate complete form
 * 
 * @param array $fields Array of field definitions
 * @param array $options Optional settings
 *   - 'id' => string Form ID
 *   - 'method' => string Form method (get, post)
 *   - 'action' => string Form action URL
 *   - 'submit_text' => string Submit button text
 * @return string HTML form
 */
function ui_generateForm($fields, $options = []) {
    return _ui_buildForm($fields, $options);
}

/**
 * Generate status message area
 * 
 * @param string $type Message type (info, success, warning, error)
 * @param string $message Message text
 * @param array $options Optional settings
 *   - 'id' => string Container ID
 *   - 'dismissible' => bool Show close button
 *   - 'icon' => string Custom icon
 * @return string HTML status message
 */
function ui_generateStatusMessage($type, $message, $options = []) {
    return _ui_buildStatusMessage($type, $message, $options);
}

/**
 * Generate empty status message container
 * 
 * @param string $id Container ID
 * @return string HTML container
 */
function ui_generateStatusContainer($id = 'status') {
    return _ui_buildStatusContainer($id);
}

/**
 * Generate loading indicator
 * 
 * @param array $options Optional settings
 *   - 'text' => string Loading text
 *   - 'id' => string Container ID
 *   - 'hidden' => bool Initially hidden
 * @return string HTML loading indicator
 */
function ui_generateLoadingIndicator($options = []) {
    return _ui_buildLoadingIndicator($options);
}

/**
 * Generate container/card element
 * 
 * @param string $content Container content
 * @param array $options Optional settings
 *   - 'id' => string Container ID
 *   - 'class' => string Additional CSS classes
 *   - 'title' => string Container title
 * @return string HTML container
 */
function ui_generateContainer($content, $options = []) {
    return _ui_buildContainer($content, $options);
}

/**
 * Generate CSS include tags
 * 
 * @param string|array $css_files CSS file path(s) relative to base
 * @param array $options Optional settings
 *   - 'base_path' => string Base path for CSS files
 *   - 'version' => string Cache-busting version
 * @return string HTML link tags
 */
function ui_generateCssIncludes($css_files, $options = []) {
    return _ui_buildCssIncludes($css_files, $options);
}

/**
 * Generate JavaScript include tags
 * 
 * @param string|array $js_files JS file path(s) relative to base
 * @param array $options Optional settings
 *   - 'base_path' => string Base path for JS files
 *   - 'version' => string Cache-busting version
 *   - 'defer' => bool Add defer attribute
 *   - 'async' => bool Add async attribute
 * @return string HTML script tags
 */
function ui_generateJsIncludes($js_files, $options = []) {
    return _ui_buildJsIncludes($js_files, $options);
}

/**
 * Get asset base path
 * 
 * @param string $script_path Path to current script
 * @return string Base path for assets
 */
function ui_getAssetBasePath($script_path = null) {
    return _ui_determineAssetBasePath($script_path);
}

/**
 * Generate breadcrumb navigation
 * 
 * @param array $items Array of breadcrumb items
 *   Each item: ['text' => string, 'url' => string (optional)]
 * @param array $options Optional settings
 * @return string HTML breadcrumb
 */
function ui_generateBreadcrumb($items, $options = []) {
    return _ui_buildBreadcrumb($items, $options);
}

/**
 * Generate data table
 * 
 * @param array $headers Table header labels
 * @param array $rows Table rows (array of arrays)
 * @param array $options Optional settings
 *   - 'id' => string Table ID
 *   - 'class' => string Additional CSS classes
 *   - 'striped' => bool Striped rows
 *   - 'hover' => bool Hover effect
 *   - 'bordered' => bool Bordered table
 * @return string HTML table
 */
function ui_generateTable($headers, $rows, $options = []) {
    return _ui_buildTable($headers, $rows, $options);
}

/**
 * Generate tabs navigation
 * 
 * @param array $tabs Tab definitions
 *   Each tab: ['id' => string, 'label' => string, 'content' => string]
 * @param array $options Optional settings
 *   - 'active' => int Active tab index (0-based)
 * @return string HTML tabs
 */
function ui_generateTabs($tabs, $options = []) {
    return _ui_buildTabs($tabs, $options);
}

/**
 * Escape HTML for safe output
 * 
 * @param string $text Text to escape
 * @return string Escaped text
 */
function ui_escape($text) {
    return htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
}

/**
 * Get module version
 * 
 * @return string Version number
 */
function ui_getVersion() {
    return UI_MODULE_VERSION;
}

/**
 * Get module configuration
 * 
 * @return array Configuration array
 */
function ui_getConfig() {
    return [
        'version' => UI_MODULE_VERSION,
        'css_class_prefix' => UI_CSS_CLASS_PREFIX,
        'default_button_style' => UI_DEFAULT_BUTTON_STYLE,
        'default_form_method' => UI_DEFAULT_FORM_METHOD
    ];
}
