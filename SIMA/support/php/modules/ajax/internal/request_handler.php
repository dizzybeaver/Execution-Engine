<?php
/**
 * request_handler.php
 * 
 * Request Handling Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use AjaxModule API
 */

class RequestHandler {
    private $config;
    private $rateLimitData = [];
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Handle AJAX request
     */
    public function handle($allowedActions, $callback) {
        // Check if AJAX if required
        if ($this->config['request']['require_ajax_header'] && !$this->isAjaxRequest()) {
            $this->sendError('AJAX request required', 403);
        }
        
        // Parse request
        $data = $this->parseRequest();
        
        // Get action
        $action = $data[$this->config['validation']['action_key']] ?? null;
        
        if (!$action) {
            $this->sendError('Action not specified', 400);
        }
        
        // Validate action
        require_once __DIR__ . '/request_validator.php';
        $validator = new RequestValidator($this->config);
        $validation = $validator->validateAction($action, $allowedActions);
        
        if (!$validation['valid']) {
            $this->sendError($validation['error'], 400);
        }
        
        // Check rate limit
        if ($this->config['rate_limit']['enabled']) {
            $identifier = $this->getRateLimitIdentifier();
            if (!$this->checkRateLimit($identifier)) {
                $this->sendError('Rate limit exceeded', 429);
            }
        }
        
        // Log request
        if ($this->config['logging']['log_requests']) {
            $this->logRequest($action, $data);
        }
        
        // Execute callback
        try {
            $result = call_user_func($callback, $action, $data);
            
            require_once __DIR__ . '/response_builder.php';
            $responder = new ResponseBuilder($this->config);
            $responder->sendSuccess($result);
        } catch (Exception $e) {
            $this->sendError($e->getMessage(), 500);
        }
    }
    
    /**
     * Parse request data
     */
    public function parseRequest() {
        $method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
        $data = [];
        
        if ($method === 'POST') {
            // Parse POST data
            $data = $_POST;
            
            // Parse JSON body if configured
            if ($this->config['request']['parse_json_body']) {
                $input = file_get_contents('php://input');
                if ($input) {
                    $json = json_decode($input, true);
                    if (json_last_error() === JSON_ERROR_NONE) {
                        $data = array_merge($data, $json);
                    }
                }
            }
        } elseif ($method === 'GET') {
            $data = $_GET;
        }
        
        // Sanitize if configured
        if ($this->config['security']['sanitize_input']) {
            $data = $this->sanitizeData($data);
        }
        
        return $data;
    }
    
    /**
     * Check if AJAX request
     */
    public function isAjaxRequest() {
        $header = $this->config['request']['ajax_header'];
        $value = $this->config['request']['ajax_value'];
        
        return isset($_SERVER[$header]) && 
               strtolower($_SERVER[$header]) === strtolower($value);
    }
    
    /**
     * Route request
     */
    public function route($routes) {
        $data = $this->parseRequest();
        $action = $data[$this->config['validation']['action_key']] ?? null;
        
        if (!$action) {
            $this->sendError('Action not specified', 400);
        }
        
        // Case sensitivity
        if (!$this->config['routing']['case_sensitive']) {
            $action = strtolower($action);
            $routes = array_change_key_case($routes, CASE_LOWER);
        }
        
        // Find route
        if (!isset($routes[$action])) {
            $this->sendError('Invalid action', 400);
        }
        
        // Execute route
        try {
            $result = call_user_func($routes[$action], $data);
            
            require_once __DIR__ . '/response_builder.php';
            $responder = new ResponseBuilder($this->config);
            $responder->sendSuccess($result);
        } catch (Exception $e) {
            $this->sendError($e->getMessage(), 500);
        }
    }
    
    /**
     * Sanitize data
     */
    private function sanitizeData($data) {
        if (is_array($data)) {
            foreach ($data as $key => $value) {
                $data[$key] = $this->sanitizeData($value);
            }
        } else {
            $data = htmlspecialchars($data, ENT_QUOTES, 'UTF-8');
        }
        
        return $data;
    }
    
    /**
     * Check rate limit
     */
    public function checkRateLimit($identifier, $maxRequests = null, $timeWindow = null) {
        $maxRequests = $maxRequests ?? $this->config['rate_limit']['max_requests'];
        $timeWindow = $timeWindow ?? $this->config['rate_limit']['time_window'];
        
        $now = time();
        
        if (!isset($this->rateLimitData[$identifier])) {
            $this->rateLimitData[$identifier] = [
                'requests' => [],
                'blocked_until' => 0
            ];
        }
        
        $data = &$this->rateLimitData[$identifier];
        
        // Check if blocked
        if ($data['blocked_until'] > $now) {
            return false;
        }
        
        // Remove old requests
        $data['requests'] = array_filter($data['requests'], function($timestamp) use ($now, $timeWindow) {
            return $timestamp > ($now - $timeWindow);
        });
        
        // Check limit
        if (count($data['requests']) >= $maxRequests) {
            $data['blocked_until'] = $now + $timeWindow;
            return false;
        }
        
        // Add request
        $data['requests'][] = $now;
        
        return true;
    }
    
    /**
     * Get rate limit identifier
     */
    private function getRateLimitIdentifier() {
        $type = $this->config['rate_limit']['identifier'];
        
        switch ($type) {
            case 'ip':
                return $_SERVER['REMOTE_ADDR'] ?? 'unknown';
                
            case 'session':
                $this->startSession();
                return session_id();
                
            default:
                return 'default';
        }
    }
    
    /**
     * Start session
     */
    public function startSession() {
        if (session_status() === PHP_SESSION_NONE) {
            $cfg = $this->config['session'];
            
            session_name($cfg['name']);
            session_set_cookie_params(
                $cfg['lifetime'],
                $cfg['path'],
                $cfg['domain'],
                $cfg['secure'],
                $cfg['httponly']
            );
            
            session_start();
        }
    }
    
    /**
     * Get session value
     */
    public function getSession($key, $default = null) {
        $this->startSession();
        return $_SESSION[$key] ?? $default;
    }
    
    /**
     * Set session value
     */
    public function setSession($key, $value) {
        $this->startSession();
        $_SESSION[$key] = $value;
    }
    
    /**
     * Log request
     */
    public function logRequest($action, $data = []) {
        if (!$this->config['logging']['enabled']) {
            return;
        }
        
        $logPath = $this->config['logging']['log_path'];
        $format = $this->config['logging']['log_format'];
        
        $logEntry = str_replace(
            ['{timestamp}', '{action}', '{method}', '{status}'],
            [date('Y-m-d H:i:s'), $action, $_SERVER['REQUEST_METHOD'] ?? 'UNKNOWN', '200'],
            $format
        );
        
        file_put_contents($logPath, $logEntry . "\n", FILE_APPEND);
    }
    
    /**
     * Send error (helper)
     */
    private function sendError($message, $code) {
        require_once __DIR__ . '/response_builder.php';
        $responder = new ResponseBuilder($this->config);
        $responder->sendError($message, $code);
    }
}
?>
