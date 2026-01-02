<?php
/**
 * manifest_validator.php
 * 
 * Manifest Validation Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use ManifestModule API
 */

class ManifestValidator {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Validate manifest file
     */
    public function validateFile($manifestPath) {
        if (!file_exists($manifestPath)) {
            return [
                'valid' => false,
                'errors' => ['File does not exist: ' . $manifestPath]
            ];
        }
        
        $content = file_get_contents($manifestPath);
        return $this->validateContent($content);
    }
    
    /**
     * Validate manifest content
     */
    public function validateContent($manifestContent) {
        $errors = [];
        $cfg = $this->config['validation'];
        
        // Parse YAML
        $data = $this->parseYaml($manifestContent);
        
        if ($data === null) {
            return [
                'valid' => false,
                'errors' => ['Invalid YAML format']
            ];
        }
        
        // Validate required fields
        if ($cfg['require_operation']) {
            if (!isset($data['operation'])) {
                $errors[] = 'Missing required field: operation';
            } elseif (!in_array($data['operation'], $this->config['operations']['allowed'])) {
                $errors[] = 'Invalid operation: ' . $data['operation'];
            }
        }
        
        if ($cfg['require_archive_name']) {
            if (!isset($data['archive']['name'])) {
                $errors[] = 'Missing required field: archive.name';
            }
        }
        
        if ($cfg['require_files_array']) {
            if (!isset($data['files'])) {
                $errors[] = 'Missing required field: files';
            } elseif (!is_array($data['files'])) {
                $errors[] = 'Field "files" must be an array';
            }
        }
        
        // Validate files
        if (isset($data['files']) && is_array($data['files'])) {
            $fileErrors = $this->validateFiles($data['files']);
            $errors = array_merge($errors, $fileErrors);
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors
        ];
    }
    
    /**
     * Validate files array
     */
    private function validateFiles($files) {
        $errors = [];
        $cfg = $this->config['validation'];
        
        foreach ($files as $index => $file) {
            if ($cfg['require_file_paths']) {
                if (!isset($file['path']) && !isset($file['filename'])) {
                    $errors[] = "File at index {$index}: Missing path or filename";
                }
            }
            
            if ($cfg['validate_ref_ids']) {
                if (isset($file['ref_id']) && !$this->isValidRefId($file['ref_id'])) {
                    $errors[] = "File at index {$index}: Invalid REF-ID format: " . $file['ref_id'];
                }
            }
            
            if ($cfg['validate_checksums']) {
                if (isset($file['checksum']) && !$this->isValidChecksum($file['checksum'])) {
                    $errors[] = "File at index {$index}: Invalid checksum format";
                }
            }
            
            if ($cfg['check_file_existence']) {
                $path = $file['path'] ?? '';
                if ($path && !file_exists($path)) {
                    $errors[] = "File at index {$index}: File does not exist: {$path}";
                }
            }
        }
        
        return $errors;
    }
    
    /**
     * Validate REF-ID format
     */
    private function isValidRefId($refId) {
        if (empty($refId)) {
            return true; // Empty is allowed
        }
        
        // Check against known patterns
        foreach ($this->config['ref_id_patterns'] as $prefix => $label) {
            if (preg_match('/^' . $prefix . '-\d+$/', $refId)) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Validate checksum format
     */
    private function isValidChecksum($checksum) {
        if (empty($checksum)) {
            return true; // Empty is allowed
        }
        
        $algo = $this->config['format']['checksum_algorithm'];
        
        if ($algo === 'md5') {
            return preg_match('/^[a-f0-9]{32}$/i', $checksum) === 1;
        } elseif ($algo === 'sha256') {
            return preg_match('/^[a-f0-9]{64}$/i', $checksum) === 1;
        }
        
        return false;
    }
    
    /**
     * Parse YAML content
     */
    private function parseYaml($content) {
        // Simple YAML parser for basic structures
        $lines = explode("\n", $content);
        $data = [];
        $current = &$data;
        $stack = [];
        $lastIndent = 0;
        
        foreach ($lines as $line) {
            // Skip comments and empty lines
            if (preg_match('/^\s*#/', $line) || trim($line) === '') {
                continue;
            }
            
            // Get indentation
            preg_match('/^(\s*)/', $line, $matches);
            $indent = strlen($matches[1]);
            $line = trim($line);
            
            // Handle indent changes
            if ($indent < $lastIndent) {
                $levelsUp = ($lastIndent - $indent) / $this->config['format']['yaml_indent'];
                for ($i = 0; $i < $levelsUp; $i++) {
                    if (count($stack) > 0) {
                        array_pop($stack);
                    }
                }
                $current = &$this->getStackReference($data, $stack);
            }
            
            // Parse line
            if (strpos($line, ':') !== false) {
                list($key, $value) = array_map('trim', explode(':', $line, 2));
                
                // Remove quotes from value
                $value = trim($value, '"\'');
                
                if ($value === '') {
                    // This key will have nested values
                    $current[$key] = [];
                    $stack[] = $key;
                    $current = &$current[$key];
                } elseif ($value === '[]') {
                    $current[$key] = [];
                } else {
                    $current[$key] = $this->parseValue($value);
                }
            } elseif (strpos($line, '- ') === 0) {
                // Array item
                $value = substr($line, 2);
                $current[] = $this->parseValue($value);
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
        
        // Check for numbers
        if (is_numeric($value)) {
            return strpos($value, '.') !== false ? (float)$value : (int)$value;
        }
        
        // Check for booleans
        if (in_array(strtolower($value), ['true', 'yes'])) {
            return true;
        }
        if (in_array(strtolower($value), ['false', 'no'])) {
            return false;
        }
        
        // Check for null
        if (in_array(strtolower($value), ['null', '~'])) {
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
            $current = &$current[$key];
        }
        return $current;
    }
    
    /**
     * Validate manifest structure
     */
    public function validateStructure($manifest) {
        $required = ['operation', 'archive', 'files'];
        $missing = [];
        
        foreach ($required as $field) {
            if (!isset($manifest[$field])) {
                $missing[] = $field;
            }
        }
        
        if (!empty($missing)) {
            return [
                'valid' => false,
                'errors' => ['Missing required fields: ' . implode(', ', $missing)]
            ];
        }
        
        return [
            'valid' => true,
            'errors' => []
        ];
    }
    
    /**
     * Check for duplicate files
     */
    public function checkDuplicates($files) {
        $seen = [];
        $duplicates = [];
        
        foreach ($files as $file) {
            $filename = $file['filename'] ?? basename($file['path'] ?? '');
            
            if (isset($seen[$filename])) {
                $duplicates[] = $filename;
            } else {
                $seen[$filename] = true;
            }
        }
        
        return [
            'has_duplicates' => !empty($duplicates),
            'duplicates' => $duplicates
        ];
    }
}
?>
