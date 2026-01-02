<?php
/**
 * ui_components.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-28
 * Purpose: SIMA-ui Module - Core UI component builders
 * Module: SIMA-ui
 * Location: internal/
 * 
 * INTERNAL USE ONLY - Do not call these functions directly
 * Use the public API in ui_module.php instead
 * 
 * MODIFIED: Moved to internal/ directory, added proper header
 */

/**
 * Build page header HTML
 * 
 * @internal
 */
function _ui_buildPageHeader($title, $options) {
    $html = '';
    
    // Include assets if requested
    if ($options['include_assets']) {
        $html .= "<!DOCTYPE html>\n";
        $html .= "<html lang=\"" . UI_HTML_LANG . "\">\n";
        $html .= "<head>\n";
        $html .= "    <meta charset=\"" . UI_CHARSET . "\">\n";
        $html .= "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n";
        $html .= "    <title>" . ui_escape($title) . "</title>\n";
        
        if (!empty($options['description'])) {
            $html .= "    <meta name=\"description\" content=\"" . 
                     ui_escape($options['description']) . "\">\n";
        }
        
        $html .= "</head>\n";
        $html .= "<body>\n";
    }
    
    // Header section
    $html .= "<header class=\"" . UI_HEADER_CLASS . "\">\n";
    $html .= "    <h1>" . ui_escape($title) . "</h1>\n";
    
    if (!empty($options['description'])) {
        $html .= "    <p class=\"description\">" . 
                 ui_escape($options['description']) . "</p>\n";
    }
    
    if (!empty($options['version'])) {
        $html .= "    <span class=\"version\">v" . 
                 ui_escape($options['version']) . "</span>\n";
    }
    
    $html .= "</header>\n";
    
    return $html;
}

/**
 * Build page footer HTML
 * 
 * @internal
 */
function _ui_buildPageFooter($options) {
    $html = "<footer class=\"" . UI_FOOTER_CLASS . "\">\n";
    
    if (!empty($options['footer_text'])) {
        $html .= "    <p>" . ui_escape($options['footer_text']) . "</p>\n";
    } else {
        $html .= "    <p>" . UI_DEFAULT_FOOTER_TEXT . "</p>\n";
    }
    
    if ($options['show_timestamp']) {
        $html .= "    <p class=\"timestamp\">Generated: " . 
                 date('Y-m-d H:i:s') . "</p>\n";
    }
    
    $html .= "</footer>\n";
    $html .= "</body>\n</html>";
    
    return $html;
}

/**
 * Build complete page
 * 
 * @internal
 */
function _ui_buildCompletePage($title, $content, $options) {
    $header = _ui_buildPageHeader($title, array_merge(['include_assets' => true], $options));
    $footer = _ui_buildPageFooter($options);
    
    return $header . $content . $footer;
}

/**
 * Build status message
 * 
 * @internal
 */
function _ui_buildStatusMessage($type, $message, $options) {
    $defaults = [
        'id' => '',
        'dismissible' => false,
        'icon' => null
    ];
    $options = array_merge($defaults, $options);
    
    // Get status type config
    $type_config = UI_STATUS_TYPES[$type] ?? UI_STATUS_TYPES['info'];
    $icon = $options['icon'] ?? $type_config['icon'];
    
    $html = "<div class=\"" . UI_STATUS_CLASS . " " . $type_config['class'] . "\"";
    
    if (!empty($options['id'])) {
        $html .= " id=\"" . ui_escape($options['id']) . "\"";
    }
    
    $html .= ">\n";
    $html .= "    <span class=\"status-icon\">" . $icon . "</span>\n";
    $html .= "    <span class=\"status-message\">" . ui_escape($message) . "</span>\n";
    
    if ($options['dismissible']) {
        $html .= "    <button class=\"status-close\" onclick=\"this.parentElement.style.display='none'\">" . 
                 UI_ICONS['close'] . "</button>\n";
    }
    
    $html .= "</div>\n";
    
    return $html;
}

/**
 * Build status container
 * 
 * @internal
 */
function _ui_buildStatusContainer($id) {
    return "<div id=\"" . ui_escape($id) . "\" class=\"" . 
           UI_STATUS_CLASS . "-container\"></div>\n";
}

/**
 * Build loading indicator
 * 
 * @internal
 */
function _ui_buildLoadingIndicator($options) {
    $defaults = [
        'text' => 'Loading...',
        'id' => 'loading',
        'hidden' => true
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<div id=\"" . ui_escape($options['id']) . "\" class=\"" . 
            UI_LOADING_CLASS . "\"";
    
    if ($options['hidden']) {
        $html .= " style=\"display:none\"";
    }
    
    $html .= ">\n";
    $html .= "    <span class=\"loading-icon\">" . UI_ICONS['loading'] . "</span>\n";
    $html .= "    <span class=\"loading-text\">" . ui_escape($options['text']) . "</span>\n";
    $html .= "</div>\n";
    
    return $html;
}

/**
 * Build container
 * 
 * @internal
 */
function _ui_buildContainer($content, $options) {
    $defaults = [
        'id' => '',
        'class' => '',
        'title' => ''
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<div class=\"" . UI_CONTAINER_CLASS;
    
    if (!empty($options['class'])) {
        $html .= " " . ui_escape($options['class']);
    }
    
    $html .= "\"";
    
    if (!empty($options['id'])) {
        $html .= " id=\"" . ui_escape($options['id']) . "\"";
    }
    
    $html .= ">\n";
    
    if (!empty($options['title'])) {
        $html .= "    <h2>" . ui_escape($options['title']) . "</h2>\n";
    }
    
    $html .= $content . "\n";
    $html .= "</div>\n";
    
    return $html;
}

/**
 * Build breadcrumb
 * 
 * @internal
 */
function _ui_buildBreadcrumb($items, $options) {
    $html = "<nav class=\"" . UI_BREADCRUMB_CLASS . "\">\n";
    $html .= "    <ol>\n";
    
    $total = count($items);
    foreach ($items as $index => $item) {
        $html .= "        <li";
        if ($index === $total - 1) {
            $html .= " class=\"active\"";
        }
        $html .= ">";
        
        if (isset($item['url']) && $index !== $total - 1) {
            $html .= "<a href=\"" . ui_escape($item['url']) . "\">" . 
                     ui_escape($item['text']) . "</a>";
        } else {
            $html .= ui_escape($item['text']);
        }
        
        $html .= "</li>\n";
    }
    
    $html .= "    </ol>\n";
    $html .= "</nav>\n";
    
    return $html;
}

/**
 * Build table
 * 
 * @internal
 */
function _ui_buildTable($headers, $rows, $options) {
    $defaults = [
        'id' => '',
        'class' => '',
        'striped' => false,
        'hover' => false,
        'bordered' => false
    ];
    $options = array_merge($defaults, $options);
    
    $classes = [UI_TABLE_CLASS];
    if ($options['striped']) $classes[] = UI_TABLE_STRIPED_CLASS;
    if ($options['hover']) $classes[] = UI_TABLE_HOVER_CLASS;
    if ($options['bordered']) $classes[] = UI_TABLE_BORDERED_CLASS;
    if (!empty($options['class'])) $classes[] = $options['class'];
    
    $html = "<table class=\"" . implode(' ', $classes) . "\"";
    
    if (!empty($options['id'])) {
        $html .= " id=\"" . ui_escape($options['id']) . "\"";
    }
    
    $html .= ">\n";
    
    // Headers
    $html .= "    <thead>\n        <tr>\n";
    foreach ($headers as $header) {
        $html .= "            <th>" . ui_escape($header) . "</th>\n";
    }
    $html .= "        </tr>\n    </thead>\n";
    
    // Rows
    $html .= "    <tbody>\n";
    foreach ($rows as $row) {
        $html .= "        <tr>\n";
        foreach ($row as $cell) {
            $html .= "            <td>" . ui_escape($cell) . "</td>\n";
        }
        $html .= "        </tr>\n";
    }
    $html .= "    </tbody>\n";
    $html .= "</table>\n";
    
    return $html;
}

/**
 * Build tabs
 * 
 * @internal
 */
function _ui_buildTabs($tabs, $options) {
    $defaults = ['active' => 0];
    $options = array_merge($defaults, $options);
    
    $html = "<div class=\"" . UI_TAB_CONTAINER_CLASS . "\">\n";
    
    // Tab navigation
    $html .= "    <ul class=\"" . UI_TAB_NAV_CLASS . "\">\n";
    foreach ($tabs as $index => $tab) {
        $active_class = ($index === $options['active']) ? ' ' . UI_TAB_ACTIVE_CLASS : '';
        $html .= "        <li class=\"tab-item{$active_class}\">\n";
        $html .= "            <a href=\"#" . ui_escape($tab['id']) . "\">" . 
                 ui_escape($tab['label']) . "</a>\n";
        $html .= "        </li>\n";
    }
    $html .= "    </ul>\n";
    
    // Tab content
    foreach ($tabs as $index => $tab) {
        $active_class = ($index === $options['active']) ? ' ' . UI_TAB_ACTIVE_CLASS : '';
        $html .= "    <div id=\"" . ui_escape($tab['id']) . 
                 "\" class=\"" . UI_TAB_CONTENT_CLASS . $active_class . "\">\n";
        $html .= $tab['content'] . "\n";
        $html .= "    </div>\n";
    }
    
    $html .= "</div>\n";
    
    return $html;
}
