# SIMA AJAX Module

**Version:** 1.0.0  
**Date:** 2025-11-27

Universal AJAX request handling and JSON response module for web applications.

---

## DIRECTORY STRUCTURE

```
modules/ajax/
├── ajax_module.php              # Public API
├── ajax_config.php              # Configuration
├── README.md                    # This file
│
└── internal/                    # Private components
    ├── request_handler.php          # Request handling
    ├── request_validator.php        # Request validation
    └── response_builder.php         # Response building
```

---

## QUICK START

### 1. Basic Handler

```php
<?php
require_once 'modules/ajax/ajax_module.php';

$ajax = new AjaxModule();

// Handle request
$ajax->handleRequest(['scan', 'export'], function($action, $data) {
    if ($action === 'scan') {
        return ['files' => scanFiles($data['path'])];
    } elseif ($action === 'export') {
        return ['archive' => exportFiles($data['files'])];
    }
});
```

### 2. Route-Based

```php
<?php
$ajax = new AjaxModule();

$ajax->route([
    'scan' => function($data) {
        return ['files' => scanFiles($data['path'])];
    },
    'export' => function($data) {
        return ['archive' => exportFiles($data['files'])];
    }
]);
```

### 3. Manual Response

```php
<?php
$ajax = new AjaxModule();

$data = $ajax->parseRequest();

if ($data['action'] === 'scan') {
    $result = scanFiles($data['path']);
    $ajax->sendSuccess($result);
} else {
    $ajax->sendError('Invalid action', 400);
}
```

---

## API REFERENCE

### AjaxModule Class

**Constructor**
```php
new AjaxModule($config = null)
```

**Request Handling**
- `handleRequest($allowedActions, $callback)` - Handle AJAX request
- `route($routes)` - Route to action callbacks
- `parseRequest()` - Parse request data
- `isAjaxRequest()` - Check if AJAX
- `getRequestMethod()` - Get HTTP method

**Response Methods**
- `sendSuccess($data, $message)` - Send success JSON
- `sendError($message, $code, $details)` - Send error JSON
- `sendJson($response)` - Send custom JSON
- `buildResponse($success, $data, $message, $error)` - Build response array

**Validation**
- `validateAction($action, $allowedActions)` - Validate action
- `validateData($data, $rules)` - Validate data
- `requireAjax()` - Require AJAX or error
- `requirePost()` - Require POST or error

**Security**
- `setCorsHeaders($options)` - Set CORS headers
- `checkRateLimit($identifier, $max, $window)` - Rate limiting

**Session**
- `startSession()` - Start session
- `getSession($key, $default)` - Get session value
- `setSession($key, $value)` - Set session value

**Logging**
- `logRequest($action, $data)` - Log request

---

## CONFIGURATION

**ajax_config.php** contains all options:

```php
[
    'request' => [
        'require_ajax_header' => true,
        'allowed_methods' => ['POST', 'GET']
    ],
    'response' => [
        'format' => 'json',
        'pretty_print' => false
    ],
    'security' => [
        'csrf_protection' => true,
        'sanitize_input' => true
    ]
]
```

---

## RESPONSE FORMAT

### Success Response
```json
{
  "success": true,
  "data": {
    "files": [...],
    "total": 25
  },
  "message": null,
  "timestamp": "2025-11-27 10:30:00"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Action not allowed",
  "code": 400,
  "details": [],
  "timestamp": "2025-11-27 10:30:00"
}
```

---

## EXAMPLES

### Example 1: File Scanner

```php
<?php
require_once 'modules/ajax/ajax_module.php';

$ajax = new AjaxModule();

$ajax->handleRequest(['scan'], function($action, $data) {
    $path = $data['path'] ?? '';
    
    if (empty($path)) {
        throw new Exception('Path is required');
    }
    
    $files = glob($path . '/*.md');
    
    return [
        'files' => $files,
        'total' => count($files)
    ];
});
```

### Example 2: With Validation

```php
<?php
$ajax = new AjaxModule();

$data = $ajax->parseRequest();

// Validate
$validation = $ajax->validateData($data, [
    'path' => 'required',
    'format' => 'required|in:json,xml,yaml'
]);

if (!$validation['valid']) {
    $ajax->sendError('Validation failed', 400, $validation['errors']);
}

// Process
$result = processData($data);
$ajax->sendSuccess($result);
```

### Example 3: Rate Limited

```php
<?php
$ajax = new AjaxModule();

// Check rate limit (60 requests per minute)
if (!$ajax->checkRateLimit('user_123', 60, 60)) {
    $ajax->sendError('Rate limit exceeded', 429);
}

// Handle request
$ajax->handleRequest(['action1', 'action2'], function($action, $data) {
    return ['result' => 'success'];
});
```

### Example 4: With CORS

```php
<?php
$ajax = new AjaxModule();

// Set CORS headers
$ajax->setCorsHeaders([
    'allow_origin' => 'https://example.com',
    'allow_methods' => ['POST'],
    'allow_credentials' => true
]);

$ajax->handleRequest(['getData'], function($action, $data) {
    return ['data' => getData()];
});
```

### Example 5: Session-Based

```php
<?php
$ajax = new AjaxModule();

$ajax->startSession();

$ajax->route([
    'login' => function($data) use ($ajax) {
        if (authenticate($data['username'], $data['password'])) {
            $ajax->setSession('user_id', $data['username']);
            return ['message' => 'Logged in'];
        }
        throw new Exception('Invalid credentials');
    },
    'logout' => function($data) use ($ajax) {
        $ajax->setSession('user_id', null);
        return ['message' => 'Logged out'];
    }
]);
```

---

## VALIDATION RULES

### Available Rules
- `required` - Field is required
- `email` - Valid email format
- `url` - Valid URL format
- `numeric` - Must be numeric
- `alpha` - Letters only
- `alphanumeric` - Letters and numbers only
- `min:n` - Minimum length n
- `max:n` - Maximum length n
- `in:a,b,c` - Must be one of values

### Usage
```php
$rules = [
    'email' => 'required|email',
    'age' => 'required|numeric|min:1|max:3',
    'role' => 'required|in:admin,user,guest'
];

$validation = $ajax->validateData($data, $rules);
```

---

## FEATURES

### Current Features
- ✅ AJAX request handling
- ✅ Action routing
- ✅ JSON responses
- ✅ Data validation
- ✅ Input sanitization
- ✅ CSRF protection
- ✅ Rate limiting
- ✅ CORS support
- ✅ Session management
- ✅ Request logging
- ✅ Error handling
- ✅ Custom headers

---

## INTEGRATION

### With Export Tool

```php
<?php
require_once 'modules/ajax/ajax_module.php';

$ajax = new AjaxModule();

$ajax->route([
    'scan' => function($data) {
        // Use tree module to scan
        $tree = new TreeModule();
        return $tree->scan($data['path']);
    },
    'export' => function($data) {
        // Use packaging module to export
        $packaging = new PackagingModule();
        return $packaging->create($data['files'], $data['name']);
    }
]);
```

---

## FILE LIMITS

**All files kept under 350 lines** to ensure:
- Full accessibility via project_knowledge_search
- No truncation by Anthropic
- Easy maintenance

---

## NOTES

- Internal files in `internal/` are private - use AjaxModule API only
- Automatic JSON response formatting
- Built-in security features
- Configurable validation rules
- Rate limiting with multiple strategies
- CORS support for cross-origin requests

---

**Version:** 1.0.0  
**Lines:** 345
