<?php
/**
 * ui_config.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-28
 * Purpose: SIMA-ui Module - Configuration constants and defaults
 * Module: SIMA-ui
 */

// Module version
define('UI_MODULE_VERSION', '1.0.0');

// CSS class prefix for all UI components
define('UI_CSS_CLASS_PREFIX', 'sima-');

// Default button styles
define('UI_DEFAULT_BUTTON_STYLE', 'primary');
define('UI_BUTTON_STYLES', [
    'primary' => 'btn-primary',
    'secondary' => 'btn-secondary',
    'danger' => 'btn-danger',
    'success' => 'btn-success',
    'warning' => 'btn-warning',
    'info' => 'btn-info'
]);

// Status message types
define('UI_STATUS_TYPES', [
    'info' => ['class' => 'status-info', 'icon' => 'ℹ'],
    'success' => ['class' => 'status-success', 'icon' => '✓'],
    'warning' => ['class' => 'status-warning', 'icon' => '⚠'],
    'error' => ['class' => 'status-error', 'icon' => '✗']
]);

// Form defaults
define('UI_DEFAULT_FORM_METHOD', 'post');
define('UI_DEFAULT_INPUT_TYPE', 'text');

// Asset paths (relative to module)
define('UI_DEFAULT_CSS_PATH', 'css/');
define('UI_DEFAULT_JS_PATH', 'js/');

// HTML templates
define('UI_DOCTYPE', '<!DOCTYPE html>');
define('UI_HTML_LANG', 'en');
define('UI_CHARSET', 'UTF-8');

// Container classes
define('UI_CONTAINER_CLASS', UI_CSS_CLASS_PREFIX . 'container');
define('UI_FORM_GROUP_CLASS', UI_CSS_CLASS_PREFIX . 'form-group');
define('UI_STATUS_CLASS', UI_CSS_CLASS_PREFIX . 'status');
define('UI_LOADING_CLASS', UI_CSS_CLASS_PREFIX . 'loading');

// Input classes
define('UI_INPUT_CLASS', UI_CSS_CLASS_PREFIX . 'input');
define('UI_TEXTAREA_CLASS', UI_CSS_CLASS_PREFIX . 'textarea');
define('UI_SELECT_CLASS', UI_CSS_CLASS_PREFIX . 'select');
define('UI_BUTTON_CLASS', UI_CSS_CLASS_PREFIX . 'button');
define('UI_CHECKBOX_CLASS', UI_CSS_CLASS_PREFIX . 'checkbox');

// Table classes
define('UI_TABLE_CLASS', UI_CSS_CLASS_PREFIX . 'table');
define('UI_TABLE_STRIPED_CLASS', 'table-striped');
define('UI_TABLE_HOVER_CLASS', 'table-hover');
define('UI_TABLE_BORDERED_CLASS', 'table-bordered');

// Layout classes
define('UI_HEADER_CLASS', UI_CSS_CLASS_PREFIX . 'header');
define('UI_FOOTER_CLASS', UI_CSS_CLASS_PREFIX . 'footer');
define('UI_BREADCRUMB_CLASS', UI_CSS_CLASS_PREFIX . 'breadcrumb');

// Tab classes
define('UI_TAB_CONTAINER_CLASS', UI_CSS_CLASS_PREFIX . 'tabs');
define('UI_TAB_NAV_CLASS', 'tab-nav');
define('UI_TAB_CONTENT_CLASS', 'tab-content');
define('UI_TAB_ACTIVE_CLASS', 'active');

// Icon mappings for common actions
define('UI_ICONS', [
    'info' => 'ℹ',
    'success' => '✓',
    'warning' => '⚠',
    'error' => '✗',
    'loading' => '⟳',
    'folder' => '📁',
    'file' => '📄',
    'download' => '⬇',
    'upload' => '⬆',
    'search' => '🔍',
    'close' => '✕'
]);

// Default page metadata
define('UI_DEFAULT_PAGE_TITLE', 'SIMA Tool');
define('UI_DEFAULT_PAGE_DESCRIPTION', '');
define('UI_DEFAULT_FOOTER_TEXT', 'SIMA Module System');

// Cache busting
define('UI_ASSET_VERSION', time());
define('UI_USE_CACHE_BUSTING', true);
