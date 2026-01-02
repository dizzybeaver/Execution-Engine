<?php
/**
 * ui_layouts.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-28
 * Purpose: SIMA-ui Module - Page layout and structure builders
 * Module: SIMA-ui
 * Location: internal/
 * 
 * INTERNAL USE ONLY - Do not call these functions directly
 * Use the public API in ui_module.php instead
 * 
 * MODIFIED: Moved to internal/ directory, added proper header
 */

/**
 * Build two-column layout
 * 
 * @internal
 */
function _ui_buildTwoColumnLayout($left_content, $right_content, $options = []) {
    $defaults = [
        'left_width' => '30%',
        'right_width' => '70%',
        'gap' => '20px'
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<div class=\"" . UI_CSS_CLASS_PREFIX . "two-column\" style=\"display:flex;gap:" . 
            ui_escape($options['gap']) . "\">\n";
    
    $html .= "    <div class=\"column-left\" style=\"width:" . 
             ui_escape($options['left_width']) . "\">\n";
    $html .= $left_content . "\n";
    $html .= "    </div>\n";
    
    $html .= "    <div class=\"column-right\" style=\"width:" . 
             ui_escape($options['right_width']) . "\">\n";
    $html .= $right_content . "\n";
    $html .= "    </div>\n";
    
    $html .= "</div>\n";
    
    return $html;
}

/**
 * Build three-column layout
 * 
 * @internal
 */
function _ui_buildThreeColumnLayout($left, $center, $right, $options = []) {
    $defaults = [
        'left_width' => '25%',
        'center_width' => '50%',
        'right_width' => '25%',
        'gap' => '20px'
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<div class=\"" . UI_CSS_CLASS_PREFIX . "three-column\" style=\"display:flex;gap:" . 
            ui_escape($options['gap']) . "\">\n";
    
    $html .= "    <div class=\"column-left\" style=\"width:" . 
             ui_escape($options['left_width']) . "\">\n";
    $html .= $left . "\n";
    $html .= "    </div>\n";
    
    $html .= "    <div class=\"column-center\" style=\"width:" . 
             ui_escape($options['center_width']) . "\">\n";
    $html .= $center . "\n";
    $html .= "    </div>\n";
    
    $html .= "    <div class=\"column-right\" style=\"width:" . 
             ui_escape($options['right_width']) . "\">\n";
    $html .= $right . "\n";
    $html .= "    </div>\n";
    
    $html .= "</div>\n";
    
    return $html;
}

/**
 * Build grid layout
 * 
 * @internal
 */
function _ui_buildGridLayout($items, $options = []) {
    $defaults = [
        'columns' => 3,
        'gap' => '20px',
        'item_class' => 'grid-item'
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<div class=\"" . UI_CSS_CLASS_PREFIX . "grid\" style=\"display:grid;grid-template-columns:repeat(" . 
            intval($options['columns']) . ",1fr);gap:" . ui_escape($options['gap']) . "\">\n";
    
    foreach ($items as $item) {
        $html .= "    <div class=\"" . ui_escape($options['item_class']) . "\">\n";
        $html .= $item . "\n";
        $html .= "    </div>\n";
    }
    
    $html .= "</div>\n";
    
    return $html;
}

/**
 * Build sidebar layout
 * 
 * @internal
 */
function _ui_buildSidebarLayout($sidebar_content, $main_content, $options = []) {
    $defaults = [
        'sidebar_position' => 'left',
        'sidebar_width' => '250px',
        'gap' => '20px'
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<div class=\"" . UI_CSS_CLASS_PREFIX . "sidebar-layout\" style=\"display:flex;gap:" . 
            ui_escape($options['gap']) . "\">\n";
    
    if ($options['sidebar_position'] === 'left') {
        $html .= _ui_buildSidebarSection($sidebar_content, $options);
        $html .= _ui_buildMainSection($main_content);
    } else {
        $html .= _ui_buildMainSection($main_content);
        $html .= _ui_buildSidebarSection($sidebar_content, $options);
    }
    
    $html .= "</div>\n";
    
    return $html;
}

/**
 * Build sidebar section
 * 
 * @internal
 */
function _ui_buildSidebarSection($content, $options) {
    $html = "    <aside class=\"sidebar\" style=\"width:" . 
            ui_escape($options['sidebar_width']) . ";flex-shrink:0\">\n";
    $html .= $content . "\n";
    $html .= "    </aside>\n";
    
    return $html;
}

/**
 * Build main section
 * 
 * @internal
 */
function _ui_buildMainSection($content) {
    $html = "    <main class=\"main-content\" style=\"flex-grow:1\">\n";
    $html .= $content . "\n";
    $html .= "    </main>\n";
    
    return $html;
}

/**
 * Build card layout
 * 
 * @internal
 */
function _ui_buildCard($content, $options = []) {
    $defaults = [
        'title' => '',
        'footer' => '',
        'class' => ''
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<div class=\"" . UI_CSS_CLASS_PREFIX . "card";
    
    if (!empty($options['class'])) {
        $html .= " " . ui_escape($options['class']);
    }
    
    $html .= "\">\n";
    
    if (!empty($options['title'])) {
        $html .= "    <div class=\"card-header\">\n";
        $html .= "        <h3>" . ui_escape($options['title']) . "</h3>\n";
        $html .= "    </div>\n";
    }
    
    $html .= "    <div class=\"card-body\">\n";
    $html .= $content . "\n";
    $html .= "    </div>\n";
    
    if (!empty($options['footer'])) {
        $html .= "    <div class=\"card-footer\">\n";
        $html .= $options['footer'] . "\n";
        $html .= "    </div>\n";
    }
    
    $html .= "</div>\n";
    
    return $html;
}

/**
 * Build panel/section
 * 
 * @internal
 */
function _ui_buildPanel($content, $options = []) {
    $defaults = [
        'title' => '',
        'collapsible' => false,
        'collapsed' => false,
        'id' => uniqid('panel_')
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<div class=\"" . UI_CSS_CLASS_PREFIX . "panel\" id=\"" . 
            ui_escape($options['id']) . "\">\n";
    
    if (!empty($options['title'])) {
        $html .= "    <div class=\"panel-header\"";
        
        if ($options['collapsible']) {
            $html .= " onclick=\"document.getElementById('" . 
                     ui_escape($options['id']) . "-body').classList.toggle('collapsed')\"";
            $html .= " style=\"cursor:pointer\"";
        }
        
        $html .= ">\n";
        $html .= "        <h4>" . ui_escape($options['title']) . "</h4>\n";
        
        if ($options['collapsible']) {
            $html .= "        <span class=\"toggle-icon\">▼</span>\n";
        }
        
        $html .= "    </div>\n";
    }
    
    $collapsed_class = ($options['collapsed'] && $options['collapsible']) ? ' collapsed' : '';
    
    $html .= "    <div class=\"panel-body" . $collapsed_class . "\" id=\"" . 
             ui_escape($options['id']) . "-body\">\n";
    $html .= $content . "\n";
    $html .= "    </div>\n";
    
    $html .= "</div>\n";
    
    return $html;
}

/**
 * Build hero section
 * 
 * @internal
 */
function _ui_buildHero($title, $content, $options = []) {
    $defaults = [
        'background' => '',
        'height' => '400px',
        'text_align' => 'center'
    ];
    $options = array_merge($defaults, $options);
    
    $style = "height:" . ui_escape($options['height']) . 
             ";text-align:" . ui_escape($options['text_align']);
    
    if (!empty($options['background'])) {
        $style .= ";background:" . ui_escape($options['background']);
    }
    
    $html = "<div class=\"" . UI_CSS_CLASS_PREFIX . "hero\" style=\"" . $style . "\">\n";
    $html .= "    <h1>" . ui_escape($title) . "</h1>\n";
    $html .= "    <div class=\"hero-content\">\n";
    $html .= $content . "\n";
    $html .= "    </div>\n";
    $html .= "</div>\n";
    
    return $html;
}

/**
 * Build flex container
 * 
 * @internal
 */
function _ui_buildFlexContainer($items, $options = []) {
    $defaults = [
        'direction' => 'row',
        'justify' => 'flex-start',
        'align' => 'stretch',
        'wrap' => 'nowrap',
        'gap' => '10px'
    ];
    $options = array_merge($defaults, $options);
    
    $style = "display:flex;" . 
             "flex-direction:" . ui_escape($options['direction']) . ";" .
             "justify-content:" . ui_escape($options['justify']) . ";" .
             "align-items:" . ui_escape($options['align']) . ";" .
             "flex-wrap:" . ui_escape($options['wrap']) . ";" .
             "gap:" . ui_escape($options['gap']);
    
    $html = "<div class=\"" . UI_CSS_CLASS_PREFIX . "flex\" style=\"" . $style . "\">\n";
    
    foreach ($items as $item) {
        $html .= "    <div class=\"flex-item\">\n";
        $html .= $item . "\n";
        $html .= "    </div>\n";
    }
    
    $html .= "</div>\n";
    
    return $html;
}
