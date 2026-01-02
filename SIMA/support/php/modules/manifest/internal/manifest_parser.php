<?php
/**
 * manifest_parser.php
 * 
 * Manifest Parsing Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use ManifestModule API
 */

class ManifestParser {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Parse manifest file
     */
    public function parseFile($manifestPath) {
        if (!file_exists($manifestPath)) {
            return ['error' => 'File does not exist: ' . $manifestPath];
        }
        
        $content = file_get_contents($manifestPath);
        return $this->parseContent($content);
    }
    
    /**
     * Parse manifest content
     */
    public function parseContent($manifestContent) {
        $data = $this->parseYaml($manifestContent);
        
        if ($data === null) {
            return ['error' => 'Invalid YAML format'];
        }
        
        // Validate if configured
        if ($this->config['parsing']['validate_on_parse']) {
            require_once __DIR__ . '/manifest_validator.php';
            $validator = new ManifestValidator($this->config);
            $validation = $validator->validateContent($manifestContent);
            
            if (!$validation['valid']) {
                return [
                    'error' => 'Invalid manifest',
                    'validation_errors' => $validation['errors']
                ];
            }
        }
        
        // Process parsed data
        if ($this->config['parsing']['convert_dates']) {
            $data = $this->convertDates($data);
        }
        
        if ($this->config['parsing']['normalize_paths']) {
            $data = $this->normalizePaths($data);
        }
        
        return $data;
    }
    
    /**
     * Parse YAML content
     */
    private function parseYaml($content) {
        $lines = explode("\n", $content);
        $data = [];
        $current = &$data;
        $stack = [];
        $lastIndent = 0;
        $inArray = false;
        
        foreach ($lines as $lineNum => $line) {
            // Skip comments and empty lines
            if (preg_match('/^\s*#/', $line) || trim($line) === '') {
                continue;
            }
            
            // Get indentation
            preg_match('/^(\s*)/', $line, $matches);
            $indent = strlen($matches[1]);
            $trimmedLine = trim($line);
            
            // Handle indent changes
            if ($indent < $lastIndent) {
                $levelsUp = ($lastIndent - $indent) / $this->config['format']['yaml_indent'];
                for ($i = 0; $i < $levelsUp; $i++) {
                    if (count($stack) > 0) {
                        array_pop($stack);
                    }
                }
                $current = &$this->getStackReference($data, $stack);
                $inArray = false;
            }
            
            // Parse line
            if (preg_match('/^-\s+(.+)$/', $trimmedLine, $matches)) {
                // Array item
                $value = $matches[1];
                
                // Check if it's a key:value pair in array
                if (strpos($value, ':') !== false) {
                    list($key, $val) = array_map('trim', explode(':', $value, 2));
                    $val = trim($val, '"\'');
                    
                    if (!$inArray || !is_array($current) || empty($current)) {
                        $current[] = [$key => $this->parseValue($val)];
                    } else {
                        $lastIndex = count($current) - 1;
                        $current[$lastIndex][$key] = $this->parseValue($val);
                    }
                } else {
                    $current[] = $this->parseValue($value);
                }
                
                $inArray = true;
            } elseif (strpos($trimmedLine, ':') !== false) {
                // Key-value pair
                list($key, $value) = array_map('trim', explode(':', $trimmedLine, 2));
                $value = trim($value, '"\'');
                
                if ($value === '' || $value === '[]') {
                    // Nested structure or empty array
                    if ($value === '[]') {
                        $current[$key] = [];
                    } else {
                        $current[$key] = [];
                        $stack[] = $key;
                        $current = &$current[$key];
                    }
                    $inArray = false;
                } else {
                    $current[$key] = $this->parseValue($value);
                }
            }
            
            $lastIndent = $indent;
        }
        
        return $data;
    }
    
    /**
     * Parse YAML value
     */
    private function parseValue($value) {
        // Remove quotes
        $value = trim($value, '"\'');
        
        // Empty string
        if ($value === '') {
            return '';
        }
        
        // Check for numbers
        if (is_numeric($value)) {
            return strpos($value, '.') !== false ? (float)$value : (int)$value;
        }
        
        // Check for booleans
        $lower = strtolower($value);
        if (in_array($lower, ['true', 'yes', 'on'])) {
            return true;
        }
        if (in_array($lower, ['false', 'no', 'off'])) {
            return false;
        }
        
        // Check for null
        if (in_array($lower, ['null', '~', 'nil'])) {
            return null;
        }
        
        return $value;
    }
    
    /**
     * Get reference from stack path
     */
    private function &getStackReference(&$data, $stack) {
        $current = &$data;
        foreach ($stack as $key) {
            if (!isset($current[$key])) {
                $current[$key] = [];
            }
            $current = &$current[$key];
        }
        return $current;
    }
    
    /**
     * Convert date strings to timestamps
     */
    private function convertDates($data) {
        if (isset($data['archive']['created'])) {
            $timestamp = strtotime($data['archive']['created']);
            if ($timestamp !== false) {
                $data['archive']['created_timestamp'] = $timestamp;
            }
        }
        
        return $data;
    }
    
    /**
     * Normalize file paths
     */
    private function normalizePaths($data) {
        if (isset($data['files']) && is_array($data['files'])) {
            foreach ($data['files'] as &$file) {
                if (isset($file['path'])) {
                    $file['path'] = $this->normalizePath($file['path']);
                }
            }
        }
        
        return $data;
    }
    
    /**
     * Normalize single path
     */
    private function normalizePath($path) {
        // Convert backslashes to forward slashes
        $path = str_replace('\\', '/', $path);
        
        // Remove duplicate slashes
        $path = preg_replace('#/+#', '/', $path);
        
        // Remove leading ./
        $path = preg_replace('#^\./#', '', $path);
        
        return $path;
    }
    
    /**
     * Extract specific section
     */
    public function extractSection($manifestPath, $section) {
        $data = $this->parseFile($manifestPath);
        
        if (isset($data['error'])) {
            return $data;
        }
        
        if (!isset($data[$section])) {
            return ['error' => "Section not found: {$section}"];
        }
        
        return [
            'success' => true,
            'section' => $section,
            'data' => $data[$section]
        ];
    }
    
    /**
     * Get file list from manifest
     */
    public function getFileList($manifestPath) {
        $data = $this->parseFile($manifestPath);
        
        if (isset($data['error'])) {
            return $data;
        }
        
        return [
            'success' => true,
            'files' => $data['files'] ?? [],
            'total' => count($data['files'] ?? [])
        ];
    }
    
    /**
     * Get files by category
     */
    public function getFilesByCategory($manifestPath, $category) {
        $data = $this->parseFile($manifestPath);
        
        if (isset($data['error'])) {
            return $data;
        }
        
        $files = [];
        foreach ($data['files'] ?? [] as $file) {
            if (($file['category'] ?? '') === $category) {
                $files[] = $file;
            }
        }
        
        return [
            'success' => true,
            'category' => $category,
            'files' => $files,
            'total' => count($files)
        ];
    }
    
    /**
     * Get files by REF-ID
     */
    public function getFilesByRefId($manifestPath, $refId) {
        $data = $this->parseFile($manifestPath);
        
        if (isset($data['error'])) {
            return $data;
        }
        
        $files = [];
        foreach ($data['files'] ?? [] as $file) {
            if (($file['ref_id'] ?? '') === $refId) {
                $files[] = $file;
            }
        }
        
        return [
            'success' => true,
            'ref_id' => $refId,
            'files' => $files,
            'total' => count($files)
        ];
    }
    
    /**
     * Search files by criteria
     */
    public function searchFiles($manifestPath, $criteria) {
        $data = $this->parseFile($manifestPath);
        
        if (isset($data['error'])) {
            return $data;
        }
        
        $files = [];
        foreach ($data['files'] ?? [] as $file) {
            $match = true;
            
            foreach ($criteria as $key => $value) {
                if (!isset($file[$key]) || $file[$key] !== $value) {
                    $match = false;
                    break;
                }
            }
            
            if ($match) {
                $files[] = $file;
            }
        }
        
        return [
            'success' => true,
            'criteria' => $criteria,
            'files' => $files,
            'total' => count($files)
        ];
    }
}
?>
