<?php
/**
 * ajax_module.php
 * 
 * SIMA AJAX Module - Public API
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Public interface for AJAX request handling and JSON responses
 */

class AjaxModule {
    private $config;
    private $handler;
    private $validator;
    private $responder;
    
    /**
     * Initialize AJAX module
     * 
     * @param array|string $config Config array or path to config file
     */
    public function __construct($config = null) {
        // Load configuration
        if (is_string($config) && file_exists($config)) {
            $this->config = require $config;
        } elseif (is_array($config)) {
            $this->config = $config;
        } else {
            $this->config = require __DIR__ . '/ajax_config.php';
        }
        
        // Load internal components
        require_once __DIR__ . '/internal/request_handler.php';
        require_once __DIR__ . '/internal/request_validator.php';
        require_once __DIR__ . '/internal/response_builder.php';
        
        $this->handler = new RequestHandler($this->config);
        $this->validator = new RequestValidator($this->config);
        $this->responder = new ResponseBuilder($this->config);
    }
    
    /**
     * Handle AJAX request
     * 
     * @param array $allowedActions Allowed action names
     * @param callable $callback Action callback function($action, $data)
     * @return void Sends JSON response and exits
     */
    public function handleRequest($allowedActions, $callback) {
        $this->handler->handle($allowedActions, $callback);
    }
    
    /**
     * Send success response
     * 
     * @param array $data Response data
     * @param string $message Optional message
     * @return void Sends JSON and exits
     */
    public function sendSuccess($data = [], $message = null) {
        $this->responder->sendSuccess($data, $message);
    }
    
    /**
     * Send error response
     * 
     * @param string $message Error message
     * @param int $code Error code
     * @param array $details Additional error details
     * @return void Sends JSON and exits
     */
    public function sendError($message, $code = 400, $details = []) {
        $this->responder->sendError($message, $code, $details);
    }
    
    /**
     * Validate action
     * 
     * @param string $action Action name
     * @param array $allowedActions Allowed actions
     * @return array Validation result
     */
    public function validateAction($action, $allowedActions) {
        return $this->validator->validateAction($action, $allowedActions);
    }
    
    /**
     * Parse request data
     * 
     * @return array Parsed request data
     */
    public function parseRequest() {
        return $this->handler->parseRequest();
    }
    
    /**
     * Get request method
     * 
     * @return string Request method (GET, POST, etc.)
     */
    public function getRequestMethod() {
        return $_SERVER['REQUEST_METHOD'] ?? 'GET';
    }
    
    /**
     * Check if request is AJAX
     * 
     * @return bool True if AJAX request
     */
    public function isAjaxRequest() {
        return $this->handler->isAjaxRequest();
    }
    
    /**
     * Validate request data
     * 
     * @param array $data Request data
     * @param array $rules Validation rules
     * @return array Validation result
     */
    public function validateData($data, $rules) {
        return $this->validator->validateData($data, $rules);
    }
    
    /**
     * Require AJAX request
     * 
     * @return void Sends error if not AJAX
     */
    public function requireAjax() {
        if (!$this->isAjaxRequest()) {
            $this->sendError('AJAX request required', 403);
        }
    }
    
    /**
     * Require POST method
     * 
     * @return void Sends error if not POST
     */
    public function requirePost() {
        if ($this->getRequestMethod() !== 'POST') {
            $this->sendError('POST method required', 405);
        }
    }
    
    /**
     * Route request to action
     * 
     * @param array $routes Action routes ['action' => callback]
     * @return void Executes route and sends response
     */
    public function route($routes) {
        $this->handler->route($routes);
    }
    
    /**
     * Build response
     * 
     * @param bool $success Success status
     * @param array $data Response data
     * @param string $message Optional message
     * @param string $error Optional error
     * @return array Response array
     */
    public function buildResponse($success, $data = [], $message = null, $error = null) {
        return $this->responder->build($success, $data, $message, $error);
    }
    
    /**
     * Send JSON response
     * 
     * @param array $response Response array
     * @return void Sends JSON and exits
     */
    public function sendJson($response) {
        $this->responder->send($response);
    }
    
    /**
     * Set CORS headers
     * 
     * @param array $options CORS options
     * @return void Sets headers
     */
    public function setCorsHeaders($options = []) {
        $this->responder->setCorsHeaders($options);
    }
    
    /**
     * Start session if needed
     * 
     * @return void Starts session
     */
    public function startSession() {
        $this->handler->startSession();
    }
    
    /**
     * Get session value
     * 
     * @param string $key Session key
     * @param mixed $default Default value
     * @return mixed Session value
     */
    public function getSession($key, $default = null) {
        return $this->handler->getSession($key, $default);
    }
    
    /**
     * Set session value
     * 
     * @param string $key Session key
     * @param mixed $value Session value
     * @return void
     */
    public function setSession($key, $value) {
        $this->handler->setSession($key, $value);
    }
    
    /**
     * Rate limit check
     * 
     * @param string $identifier Rate limit identifier (IP, user ID, etc.)
     * @param int $maxRequests Max requests
     * @param int $timeWindow Time window in seconds
     * @return bool True if allowed
     */
    public function checkRateLimit($identifier, $maxRequests = null, $timeWindow = null) {
        return $this->handler->checkRateLimit($identifier, $maxRequests, $timeWindow);
    }
    
    /**
     * Log request
     * 
     * @param string $action Action name
     * @param array $data Request data
     * @return void Logs request
     */
    public function logRequest($action, $data = []) {
        $this->handler->logRequest($action, $data);
    }
    
    /**
     * Get configuration value
     * 
     * @param string $key Config key (dot notation supported)
     * @param mixed $default Default value
     * @return mixed Config value
     */
    public function getConfig($key, $default = null) {
        $keys = explode('.', $key);
        $value = $this->config;
        
        foreach ($keys as $k) {
            if (!isset($value[$k])) {
                return $default;
            }
            $value = $value[$k];
        }
        
        return $value;
    }
    
    /**
     * Set configuration value
     * 
     * @param string $key Config key
     * @param mixed $value Config value
     */
    public function setConfig($key, $value) {
        $this->config[$key] = $value;
        
        // Update component configs
        if ($this->handler) {
            $this->handler->updateConfig($this->config);
        }
        if ($this->validator) {
            $this->validator->updateConfig($this->config);
        }
        if ($this->responder) {
            $this->responder->updateConfig($this->config);
        }
    }
}
?>
