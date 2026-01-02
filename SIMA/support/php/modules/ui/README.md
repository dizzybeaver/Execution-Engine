# README.md

**Version:** 1.0.0  
**Date:** 2025-11-28  
**Module:** SIMA-ui  
**Purpose:** UI component generation and asset management  
**Type:** Generic/Reusable Module

---

## OVERVIEW

SIMA-ui provides comprehensive UI component generation for PHP applications, including forms, layouts, status messages, and asset management.

**Key Features:**
- Complete HTML page generation
- Form component builders (inputs, textareas, selects, buttons)
- Layout systems (grid, flex, sidebar, columns)
- Status message and loading indicators
- CSS/JS asset management with cache-busting
- Breadcrumbs, tables, tabs
- Security-focused HTML escaping

---

## QUICK START

```php
// Include the module
require_once 'modules/ui/ui_module.php';

// Generate a simple page
$content = ui_generateContainer(
    ui_generateForm([
        ['type' => 'text', 'name' => 'username', 'label' => 'Username', 'required' => true],
        ['type' => 'email', 'name' => 'email', 'label' => 'Email', 'required' => true]
    ], ['submit_text' => 'Register'])
);

echo ui_generatePage('Registration', $content);
```

---

## FILE STRUCTURE

```
modules/ui/
├── ui_module.php          # Public API (all external calls)
├── ui_config.php          # Configuration constants
├── internal/
│   ├── ui_components.php  # Core UI components
│   ├── ui_forms.php       # Form builders
│   ├── ui_assets.php      # Asset management
│   └── ui_layouts.php     # Layout components
└── README.md              # This file
```

---

## PUBLIC API

### Page Generation

**ui_generatePageHeader($title, $options)**
- Generates page header with optional description and version
- Options: description, version, include_assets

**ui_generatePageFooter($options)**
- Generates page footer
- Options: footer_text, show_timestamp

**ui_generatePage($title, $content, $options)**
- Generates complete HTML page
- Combines header, content, footer

### Form Components

**ui_generateInput($type, $name, $options)**
- Generate form input (text, number, email, password, checkbox, file)
- Options: id, value, label, placeholder, required, attributes

**ui_generateTextarea($name, $options)**
- Generate textarea element
- Options: id, value, rows, cols, placeholder, required

**ui_generateSelect($name, $options_list, $options)**
- Generate select dropdown
- Options: id, selected, required

**ui_generateButton($text, $options)**
- Generate button element
- Options: type, id, class, onclick, disabled, style (primary/secondary/danger/etc.)

**ui_generateFormGroup($label, $input_html, $options)**
- Wrapper for label + input with help text and errors
- Options: help_text, error, required

**ui_generateForm($fields, $options)**
- Generate complete form from field definitions
- Options: id, method, action, submit_text

### Status & Feedback

**ui_generateStatusMessage($type, $message, $options)**
- Generate status message (info/success/warning/error)
- Options: id, dismissible, icon

**ui_generateStatusContainer($id)**
- Empty container for dynamic status messages

**ui_generateLoadingIndicator($options)**
- Generate loading spinner/indicator
- Options: text, id, hidden

### Containers & Layout

**ui_generateContainer($content, $options)**
- Generate container/card element
- Options: id, class, title

**ui_generateBreadcrumb($items, $options)**
- Generate breadcrumb navigation
- Items: [{text, url}, ...]

**ui_generateTable($headers, $rows, $options)**
- Generate data table
- Options: id, class, striped, hover, bordered

**ui_generateTabs($tabs, $options)**
- Generate tabbed interface
- Tabs: [{id, label, content}, ...]
- Options: active (index)

### Asset Management

**ui_generateCssIncludes($css_files, $options)**
- Generate CSS link tags
- Options: base_path, version

**ui_generateJsIncludes($js_files, $options)**
- Generate JavaScript script tags
- Options: base_path, version, defer, async

**ui_getAssetBasePath($script_path)**
- Get base path for assets

### Utilities

**ui_escape($text)**
- Escape HTML for safe output

**ui_getVersion()**
- Get module version

**ui_getConfig()**
- Get module configuration

---

## USAGE EXAMPLES

### Complete Page with Form

```php
require_once 'modules/ui/ui_module.php';

$form_html = ui_generateForm([
    [
        'type' => 'text',
        'name' => 'directory',
        'label' => 'Directory Path',
        'placeholder' => '/path/to/directory',
        'required' => true
    ],
    [
        'type' => 'select',
        'name' => 'action',
        'label' => 'Action',
        'options' => [
            'scan' => 'Scan Directory',
            'export' => 'Export Files'
        ]
    ]
], [
    'id' => 'mainForm',
    'submit_text' => 'Execute'
]);

$content = ui_generateContainer($form_html, ['title' => 'File Manager']);
$content .= ui_generateStatusContainer('status');
$content .= ui_generateLoadingIndicator(['hidden' => true]);

echo ui_generatePage('File Manager Tool', $content, [
    'description' => 'Manage your files easily',
    'version' => '1.0.0'
]);
```

### Status Messages

```php
// Success message
echo ui_generateStatusMessage('success', 'Operation completed successfully', [
    'dismissible' => true
]);

// Error message
echo ui_generateStatusMessage('error', 'An error occurred', [
    'id' => 'error-msg'
]);

// Warning with custom icon
echo ui_generateStatusMessage('warning', 'Please check your input', [
    'icon' => '⚡'
]);
```

### Data Table

```php
$headers = ['Name', 'Size', 'Modified'];
$rows = [
    ['file1.txt', '2.5 KB', '2025-01-15'],
    ['file2.txt', '1.2 MB', '2025-01-14'],
    ['file3.txt', '456 KB', '2025-01-13']
];

echo ui_generateTable($headers, $rows, [
    'striped' => true,
    'hover' => true,
    'bordered' => true
]);
```

### Asset Includes

```php
// Single CSS file
echo ui_generateCssIncludes('styles.css');

// Multiple JS files with defer
echo ui_generateJsIncludes(['app.js', 'utils.js'], [
    'defer' => true
]);

// Custom base path
echo ui_generateCssIncludes(['main.css', 'theme.css'], [
    'base_path' => '/assets'
]);
```

### Breadcrumb Navigation

```php
echo ui_generateBreadcrumb([
    ['text' => 'Home', 'url' => '/'],
    ['text' => 'Tools', 'url' => '/tools'],
    ['text' => 'Export Tool']
]);
```

### Tabs

```php
$tabs = [
    [
        'id' => 'tab1',
        'label' => 'Configuration',
        'content' => '<p>Configuration content here</p>'
    ],
    [
        'id' => 'tab2',
        'label' => 'Results',
        'content' => '<p>Results content here</p>'
    ]
];

echo ui_generateTabs($tabs, ['active' => 0]);
```

---

## CONFIGURATION

Edit `ui_config.php` to customize:

- **UI_CSS_CLASS_PREFIX** - CSS class prefix (default: 'sima-')
- **UI_DEFAULT_BUTTON_STYLE** - Default button style
- **UI_STATUS_TYPES** - Status message types and icons
- **UI_DEFAULT_CSS_PATH** - CSS directory (default: 'css/')
- **UI_DEFAULT_JS_PATH** - JS directory (default: 'js/')
- **UI_USE_CACHE_BUSTING** - Enable/disable cache busting

---

## SECURITY

All output is HTML-escaped via `ui_escape()` to prevent XSS attacks.

Asset paths are validated to prevent directory traversal.

Forms support CSRF protection when integrated with token systems.

---

## STYLING

The module generates semantic HTML with consistent CSS classes:

- `.sima-container` - Main containers
- `.sima-form-group` - Form groups
- `.sima-status` - Status messages
- `.sima-button` - Buttons
- `.sima-table` - Tables
- `.sima-tabs` - Tab containers

Create `css/sima-styles.css` for custom styling.

---

## INTEGRATION

### With SIMA-ajax Module

```php
// In your handler
require_once 'modules/ajax/ajax_module.php';
require_once 'modules/ui/ui_module.php';

$result = someOperation();

if ($result['success']) {
    $html = ui_generateStatusMessage('success', $result['message']);
    ajax_sendJsonResponse(['html' => $html]);
} else {
    $html = ui_generateStatusMessage('error', $result['error']);
    ajax_sendJsonResponse(['html' => $html], 400);
}
```

### With SIMA-file Module

```php
require_once 'modules/file/file_module.php';
require_once 'modules/ui/ui_module.php';

$files = file_listDirectory('/path/to/files');

$rows = array_map(function($file) {
    return [
        $file['name'],
        file_formatSize($file['size']),
        date('Y-m-d', $file['modified'])
    ];
}, $files);

echo ui_generateTable(['Name', 'Size', 'Modified'], $rows, [
    'striped' => true
]);
```

---

## DEPENDENCIES

**PHP Requirements:**
- PHP 7.0 or higher
- No external libraries required

**Optional:**
- CSS framework for styling
- JavaScript for interactive components

---

## VERSION HISTORY

**1.0.0** (2025-11-28)
- Initial release
- Core components (header, footer, containers)
- Complete form builders
- Status messages and loading indicators
- Asset management with cache-busting
- Layout components
- Tables, breadcrumbs, tabs

---

## LICENSE

Part of SIMA Module System  
Licensed under Apache 2.0

---

**END OF README**
