<?php
/**
 * request_validator.php
 * 
 * Request Validation Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use AjaxModule API
 */

class RequestValidator {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Validate action
     */
    public function validateAction($action, $allowedActions) {
        // Check if action provided
        if (empty($action)) {
            return [
                'valid' => false,
                'error' => 'Action is required'
            ];
        }
        
        // Check length
        $maxLength = $this->config['validation']['max_action_length'];
        if (strlen($action) > $maxLength) {
            return [
                'valid' => false,
                'error' => "Action exceeds maximum length ({$maxLength})"
            ];
        }
        
        // Check format
        if ($this->config['validation']['validate_action_format']) {
            $pattern = $this->config['validation']['action_pattern'];
            if (!preg_match($pattern, $action)) {
                return [
                    'valid' => false,
                    'error' => 'Invalid action format'
                ];
            }
        }
        
        // Check if allowed
        if (!in_array($action, $allowedActions)) {
            return [
                'valid' => false,
                'error' => 'Action not allowed'
            ];
        }
        
        return ['valid' => true];
    }
    
    /**
     * Validate data against rules
     */
    public function validateData($data, $rules) {
        $errors = [];
        
        foreach ($rules as $field => $ruleSet) {
            $value = $data[$field] ?? null;
            $fieldRules = is_array($ruleSet) ? $ruleSet : explode('|', $ruleSet);
            
            foreach ($fieldRules as $rule) {
                $error = $this->validateRule($field, $value, $rule);
                if ($error) {
                    $errors[$field][] = $error;
                }
            }
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors
        ];
    }
    
    /**
     * Validate single rule
     */
    private function validateRule($field, $value, $rule) {
        // Parse rule (format: rule:param1,param2)
        $parts = explode(':', $rule);
        $ruleName = $parts[0];
        $params = isset($parts[1]) ? explode(',', $parts[1]) : [];
        
        switch ($ruleName) {
            case 'required':
                if (empty($value)) {
                    return $this->getErrorMessage('required', $field);
                }
                break;
                
            case 'email':
                if ($value && !filter_var($value, FILTER_VALIDATE_EMAIL)) {
                    return $this->getErrorMessage('email', $field);
                }
                break;
                
            case 'url':
                if ($value && !filter_var($value, FILTER_VALIDATE_URL)) {
                    return $this->getErrorMessage('url', $field);
                }
                break;
                
            case 'numeric':
                if ($value && !is_numeric($value)) {
                    return $this->getErrorMessage('numeric', $field);
                }
                break;
                
            case 'alpha':
                if ($value && !preg_match('/^[a-zA-Z]+$/', $value)) {
                    return $this->getErrorMessage('alpha', $field);
                }
                break;
                
            case 'alphanumeric':
                if ($value && !preg_match('/^[a-zA-Z0-9]+$/', $value)) {
                    return $this->getErrorMessage('alphanumeric', $field);
                }
                break;
                
            case 'min':
                if (isset($params[0]) && strlen($value) < $params[0]) {
                    return "{$field} must be at least {$params[0]} characters";
                }
                break;
                
            case 'max':
                if (isset($params[0]) && strlen($value) > $params[0]) {
                    return "{$field} must not exceed {$params[0]} characters";
                }
                break;
                
            case 'in':
                if ($value && !in_array($value, $params)) {
                    return "{$field} must be one of: " . implode(', ', $params);
                }
                break;
        }
        
        return null;
    }
    
    /**
     * Get error message
     */
    private function getErrorMessage($rule, $field) {
        $message = $this->config['validation_rules'][$rule] ?? 'Validation failed';
        return str_replace('{field}', $field, $message);
    }
    
    /**
     * Validate CSRF token
     */
    public function validateCsrfToken($token) {
        if (!$this->config['security']['csrf_protection']) {
            return ['valid' => true];
        }
        
        session_start();
        $sessionToken = $_SESSION[$this->config['security']['csrf_token_name']] ?? null;
        
        if (!$sessionToken || $token !== $sessionToken) {
            return [
                'valid' => false,
                'error' => 'Invalid CSRF token'
            ];
        }
        
        return ['valid' => true];
    }
    
    /**
     * Validate origin
     */
    public function validateOrigin() {
        if (!$this->config['security']['verify_origin']) {
            return ['valid' => true];
        }
        
        $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
        $allowed = $this->config['security']['allowed_origins'];
        
        if (!in_array($origin, $allowed) && !in_array('*', $allowed)) {
            return [
                'valid' => false,
                'error' => 'Origin not allowed'
            ];
        }
        
        return ['valid' => true];
    }
}
?>
