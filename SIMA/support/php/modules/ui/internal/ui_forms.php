<?php
/**
 * ui_forms.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-28
 * Purpose: SIMA-ui Module - Form component builders
 * Module: SIMA-ui
 * Location: internal/
 * 
 * INTERNAL USE ONLY - Do not call these functions directly
 * Use the public API in ui_module.php instead
 * 
 * MODIFIED: Moved to internal/ directory, added proper header
 */

/**
 * Build input field
 * 
 * @internal
 */
function _ui_buildInput($type, $name, $options) {
    $defaults = [
        'id' => $name,
        'value' => '',
        'label' => '',
        'placeholder' => '',
        'required' => false,
        'attributes' => []
    ];
    $options = array_merge($defaults, $options);
    
    $html = '';
    
    // Generate input element
    if ($type === 'checkbox') {
        $html .= _ui_buildCheckbox($name, $options);
    } else {
        $html .= "<input";
        $html .= " type=\"" . ui_escape($type) . "\"";
        $html .= " name=\"" . ui_escape($name) . "\"";
        $html .= " id=\"" . ui_escape($options['id']) . "\"";
        
        if ($type !== 'file') {
            $html .= " class=\"" . UI_INPUT_CLASS . "\"";
        }
        
        if (!empty($options['value'])) {
            $html .= " value=\"" . ui_escape($options['value']) . "\"";
        }
        
        if (!empty($options['placeholder'])) {
            $html .= " placeholder=\"" . ui_escape($options['placeholder']) . "\"";
        }
        
        if ($options['required']) {
            $html .= " required";
        }
        
        // Additional attributes
        foreach ($options['attributes'] as $attr => $value) {
            $html .= " " . ui_escape($attr) . "=\"" . ui_escape($value) . "\"";
        }
        
        $html .= ">\n";
    }
    
    return $html;
}

/**
 * Build checkbox input
 * 
 * @internal
 */
function _ui_buildCheckbox($name, $options) {
    $html = "<label class=\"" . UI_CHECKBOX_CLASS . "-label\">\n";
    $html .= "    <input type=\"checkbox\"";
    $html .= " name=\"" . ui_escape($name) . "\"";
    $html .= " id=\"" . ui_escape($options['id']) . "\"";
    $html .= " class=\"" . UI_CHECKBOX_CLASS . "\"";
    
    if (!empty($options['value'])) {
        $html .= " value=\"" . ui_escape($options['value']) . "\"";
    }
    
    if (!empty($options['checked'])) {
        $html .= " checked";
    }
    
    if ($options['required']) {
        $html .= " required";
    }
    
    foreach ($options['attributes'] as $attr => $value) {
        $html .= " " . ui_escape($attr) . "=\"" . ui_escape($value) . "\"";
    }
    
    $html .= ">\n";
    
    if (!empty($options['label'])) {
        $html .= "    <span>" . ui_escape($options['label']) . "</span>\n";
    }
    
    $html .= "</label>\n";
    
    return $html;
}

/**
 * Build textarea
 * 
 * @internal
 */
function _ui_buildTextarea($name, $options) {
    $defaults = [
        'id' => $name,
        'value' => '',
        'rows' => 4,
        'cols' => 50,
        'placeholder' => '',
        'required' => false,
        'attributes' => []
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<textarea";
    $html .= " name=\"" . ui_escape($name) . "\"";
    $html .= " id=\"" . ui_escape($options['id']) . "\"";
    $html .= " class=\"" . UI_TEXTAREA_CLASS . "\"";
    $html .= " rows=\"" . intval($options['rows']) . "\"";
    $html .= " cols=\"" . intval($options['cols']) . "\"";
    
    if (!empty($options['placeholder'])) {
        $html .= " placeholder=\"" . ui_escape($options['placeholder']) . "\"";
    }
    
    if ($options['required']) {
        $html .= " required";
    }
    
    foreach ($options['attributes'] as $attr => $value) {
        $html .= " " . ui_escape($attr) . "=\"" . ui_escape($value) . "\"";
    }
    
    $html .= ">";
    $html .= ui_escape($options['value']);
    $html .= "</textarea>\n";
    
    return $html;
}

/**
 * Build select dropdown
 * 
 * @internal
 */
function _ui_buildSelect($name, $options_list, $options) {
    $defaults = [
        'id' => $name,
        'selected' => '',
        'required' => false,
        'attributes' => []
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<select";
    $html .= " name=\"" . ui_escape($name) . "\"";
    $html .= " id=\"" . ui_escape($options['id']) . "\"";
    $html .= " class=\"" . UI_SELECT_CLASS . "\"";
    
    if ($options['required']) {
        $html .= " required";
    }
    
    foreach ($options['attributes'] as $attr => $value) {
        $html .= " " . ui_escape($attr) . "=\"" . ui_escape($value) . "\"";
    }
    
    $html .= ">\n";
    
    foreach ($options_list as $value => $label) {
        $html .= "    <option value=\"" . ui_escape($value) . "\"";
        
        if ($value == $options['selected']) {
            $html .= " selected";
        }
        
        $html .= ">" . ui_escape($label) . "</option>\n";
    }
    
    $html .= "</select>\n";
    
    return $html;
}

/**
 * Build button
 * 
 * @internal
 */
function _ui_buildButton($text, $options) {
    $defaults = [
        'type' => 'button',
        'id' => '',
        'class' => '',
        'onclick' => '',
        'disabled' => false,
        'style' => UI_DEFAULT_BUTTON_STYLE
    ];
    $options = array_merge($defaults, $options);
    
    // Get button style class
    $style_class = UI_BUTTON_STYLES[$options['style']] ?? UI_BUTTON_STYLES['primary'];
    
    $html = "<button";
    $html .= " type=\"" . ui_escape($options['type']) . "\"";
    $html .= " class=\"" . UI_BUTTON_CLASS . " " . $style_class;
    
    if (!empty($options['class'])) {
        $html .= " " . ui_escape($options['class']);
    }
    
    $html .= "\"";
    
    if (!empty($options['id'])) {
        $html .= " id=\"" . ui_escape($options['id']) . "\"";
    }
    
    if (!empty($options['onclick'])) {
        $html .= " onclick=\"" . ui_escape($options['onclick']) . "\"";
    }
    
    if ($options['disabled']) {
        $html .= " disabled";
    }
    
    $html .= ">";
    $html .= ui_escape($text);
    $html .= "</button>\n";
    
    return $html;
}

/**
 * Build form group
 * 
 * @internal
 */
function _ui_buildFormGroup($label, $input_html, $options) {
    $defaults = [
        'help_text' => '',
        'error' => '',
        'required' => false
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<div class=\"" . UI_FORM_GROUP_CLASS . "\">\n";
    
    if (!empty($label)) {
        $html .= "    <label>" . ui_escape($label);
        
        if ($options['required']) {
            $html .= " <span class=\"required\">*</span>";
        }
        
        $html .= "</label>\n";
    }
    
    $html .= "    " . $input_html;
    
    if (!empty($options['help_text'])) {
        $html .= "    <small class=\"help-text\">" . 
                 ui_escape($options['help_text']) . "</small>\n";
    }
    
    if (!empty($options['error'])) {
        $html .= "    <span class=\"error-text\">" . 
                 ui_escape($options['error']) . "</span>\n";
    }
    
    $html .= "</div>\n";
    
    return $html;
}

/**
 * Build complete form
 * 
 * @internal
 */
function _ui_buildForm($fields, $options) {
    $defaults = [
        'id' => '',
        'method' => UI_DEFAULT_FORM_METHOD,
        'action' => '',
        'submit_text' => 'Submit'
    ];
    $options = array_merge($defaults, $options);
    
    $html = "<form";
    
    if (!empty($options['id'])) {
        $html .= " id=\"" . ui_escape($options['id']) . "\"";
    }
    
    $html .= " method=\"" . ui_escape($options['method']) . "\"";
    
    if (!empty($options['action'])) {
        $html .= " action=\"" . ui_escape($options['action']) . "\"";
    }
    
    $html .= ">\n";
    
    // Build fields
    foreach ($fields as $field) {
        $field_html = '';
        
        switch ($field['type']) {
            case 'text':
            case 'number':
            case 'email':
            case 'password':
            case 'file':
                $field_html = _ui_buildInput($field['type'], $field['name'], $field);
                break;
                
            case 'textarea':
                $field_html = _ui_buildTextarea($field['name'], $field);
                break;
                
            case 'select':
                $field_html = _ui_buildSelect($field['name'], $field['options'] ?? [], $field);
                break;
                
            case 'checkbox':
                $field_html = _ui_buildInput('checkbox', $field['name'], $field);
                break;
        }
        
        // Wrap in form group if label provided
        if (!empty($field['label']) && $field['type'] !== 'checkbox') {
            $html .= _ui_buildFormGroup($field['label'], $field_html, $field);
        } else {
            $html .= "    " . $field_html;
        }
    }
    
    // Submit button
    $html .= "    " . _ui_buildButton($options['submit_text'], [
        'type' => 'submit',
        'style' => 'primary'
    ]);
    
    $html .= "</form>\n";
    
    return $html;
}
