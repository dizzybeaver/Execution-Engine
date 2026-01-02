<?php
/**
 * response_builder.php
 * 
 * Response Building Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use AjaxModule API
 */

class ResponseBuilder {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Send success response
     */
    public function sendSuccess($data = [], $message = null) {
        $response = $this->build(true, $data, $message, null);
        $this->send($response);
    }
    
    /**
     * Send error response
     */
    public function sendError($message, $code = 400, $details = []) {
        $response = $this->build(false, [], null, $message);
        $response['code'] = $code;
        
        if (!empty($details)) {
            $response['details'] = $details;
        }
        
        http_response_code($code);
        $this->send($response);
    }
    
    /**
     * Build response array
     */
    public function build($success, $data = [], $message = null, $error = null) {
        if ($success) {
            $response = $this->config['success_structure'];
            $response['success'] = true;
            $response['data'] = $data;
            
            if ($message) {
                $response['message'] = $message;
            }
        } else {
            $response = $this->config['error_structure'];
            $response['success'] = false;
            $response['error'] = $error;
        }
        
        // Add timestamp if configured
        if ($this->config['response']['include_timestamp']) {
            $response['timestamp'] = date('Y-m-d H:i:s');
        }
        
        // Add request ID if configured
        if ($this->config['response']['include_request_id']) {
            $response['request_id'] = uniqid('req_', true);
        }
        
        return $response;
    }
    
    /**
     * Send JSON response
     */
    public function send($response) {
        // Clear any output
        if (ob_get_level()) {
            ob_clean();
        }
        
        // Set headers
        $this->setHeaders();
        
        // Set CORS if enabled
        if ($this->config['cors']['enabled']) {
            $this->setCorsHeaders();
        }
        
        // Encode JSON
        $options = JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES;
        
        if ($this->config['response']['pretty_print']) {
            $options |= JSON_PRETTY_PRINT;
        }
        
        $json = json_encode($response, $options);
        
        // Send response
        echo $json;
        exit;
    }
    
    /**
     * Set response headers
     */
    private function setHeaders() {
        $cfg = $this->config['headers'];
        
        // Content type
        header('Content-Type: ' . $cfg['content_type'] . '; charset=' . $this->config['response']['charset']);
        
        // Cache control
        header('Cache-Control: ' . $cfg['cache_control']);
        header('Pragma: ' . $cfg['pragma']);
        header('Expires: ' . $cfg['expires']);
        
        // Custom headers
        foreach ($cfg['custom_headers'] as $name => $value) {
            header("{$name}: {$value}");
        }
    }
    
    /**
     * Set CORS headers
     */
    public function setCorsHeaders($options = []) {
        $cfg = array_merge($this->config['cors'], $options);
        
        header('Access-Control-Allow-Origin: ' . $cfg['allow_origin']);
        header('Access-Control-Allow-Methods: ' . implode(', ', $cfg['allow_methods']));
        header('Access-Control-Allow-Headers: ' . implode(', ', $cfg['allow_headers']));
        
        if ($cfg['allow_credentials']) {
            header('Access-Control-Allow-Credentials: true');
        }
        
        header('Access-Control-Max-Age: ' . $cfg['max_age']);
    }
    
    /**
     * Format error for display
     */
    public function formatError($message, $code, $trace = null) {
        $error = [
            'message' => $message,
            'code' => $code
        ];
        
        if ($trace && $this->config['errors']['include_trace']) {
            $error['trace'] = $trace;
        }
        
        return $error;
    }
    
    /**
     * Send validation error
     */
    public function sendValidationError($errors) {
        $response = $this->build(false, [], null, 'Validation failed');
        $response['validation_errors'] = $errors;
        $response['code'] = 400;
        
        http_response_code(400);
        $this->send($response);
    }
}
?>
