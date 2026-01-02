<?php
/**
 * ajax_config.php
 * 
 * Configuration for SIMA AJAX Module
 * Version: 1.0.0
 * Date: 2025-11-27
 */

return [
    // Base paths
    'ajax_base_path' => __DIR__,
    
    // Request handling
    'request' => [
        'require_ajax_header' => true,
        'ajax_header' => 'HTTP_X_REQUESTED_WITH',
        'ajax_value' => 'XMLHttpRequest',
        'allowed_methods' => ['POST', 'GET'],
        'default_method' => 'POST',
        'max_input_size' => 10485760, // 10MB
        'parse_json_body' => true
    ],
    
    // Response format
    'response' => [
        'format' => 'json',
        'charset' => 'UTF-8',
        'pretty_print' => false,
        'include_timestamp' => true,
        'include_request_id' => false
    ],
    
    // Success response structure
    'success_structure' => [
        'success' => true,
        'data' => [],
        'message' => null,
        'timestamp' => null
    ],
    
    // Error response structure
    'error_structure' => [
        'success' => false,
        'error' => null,
        'code' => null,
        'details' => [],
        'timestamp' => null
    ],
    
    // Validation
    'validation' => [
        'require_action' => true,
        'action_key' => 'action',
        'validate_action_format' => true,
        'action_pattern' => '/^[a-z_]+$/',
        'max_action_length' => 50
    ],
    
    // Security
    'security' => [
        'csrf_protection' => true,
        'csrf_token_name' => 'csrf_token',
        'verify_origin' => false,
        'allowed_origins' => [],
        'sanitize_input' => true,
        'escape_output' => false
    ],
    
    // Rate limiting
    'rate_limit' => [
        'enabled' => false,
        'max_requests' => 60,
        'time_window' => 60, // seconds
        'storage' => 'session', // session, file, memory
        'identifier' => 'ip' // ip, session, custom
    ],
    
    // Session
    'session' => [
        'auto_start' => false,
        'name' => 'SIMA_SESSION',
        'lifetime' => 3600,
        'path' => '/',
        'domain' => '',
        'secure' => false,
        'httponly' => true
    ],
    
    // CORS
    'cors' => [
        'enabled' => false,
        'allow_origin' => '*',
        'allow_methods' => ['GET', 'POST'],
        'allow_headers' => ['Content-Type', 'X-Requested-With'],
        'allow_credentials' => false,
        'max_age' => 86400
    ],
    
    // Error handling
    'errors' => [
        'display_errors' => false,
        'log_errors' => true,
        'error_log_path' => '/tmp/sima-ajax-errors.log',
        'include_trace' => false,
        'default_error_code' => 400
    ],
    
    // Logging
    'logging' => [
        'enabled' => false,
        'log_requests' => true,
        'log_responses' => false,
        'log_path' => '/tmp/sima-ajax.log',
        'log_format' => '[{timestamp}] {action} - {method} - {status}'
    ],
    
    // Caching
    'caching' => [
        'enabled' => false,
        'cache_responses' => false,
        'cache_ttl' => 300,
        'cache_key_prefix' => 'ajax_'
    ],
    
    // Headers
    'headers' => [
        'content_type' => 'application/json',
        'cache_control' => 'no-cache, must-revalidate',
        'pragma' => 'no-cache',
        'expires' => '0',
        'custom_headers' => []
    ],
    
    // Action routing
    'routing' => [
        'case_sensitive' => false,
        'allow_dynamic_actions' => true,
        'action_prefix' => '',
        'action_suffix' => ''
    ],
    
    // Data validation rules
    'validation_rules' => [
        'required' => 'Value is required',
        'email' => 'Invalid email format',
        'url' => 'Invalid URL format',
        'numeric' => 'Must be numeric',
        'alpha' => 'Must contain only letters',
        'alphanumeric' => 'Must contain only letters and numbers'
    ],
    
    // HTTP status codes
    'status_codes' => [
        200 => 'OK',
        400 => 'Bad Request',
        401 => 'Unauthorized',
        403 => 'Forbidden',
        404 => 'Not Found',
        405 => 'Method Not Allowed',
        429 => 'Too Many Requests',
        500 => 'Internal Server Error'
    ]
];
?>
