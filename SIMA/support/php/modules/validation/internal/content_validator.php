<?php
/**
 * content_validator.php
 * 
 * Content Validation Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use ValidationModule API
 */

class ContentValidator {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Validate REF-ID format
     */
    public function validateRefId($refId) {
        $cfg = $this->config['ref_id'];
        
        if (!$cfg['enabled']) {
            return ['valid' => true];
        }
        
        if (empty($refId)) {
            return ['valid' => false, 'error' => 'REF-ID is empty'];
        }
        
        // Check against known patterns
        foreach ($cfg['patterns'] as $prefix => $pattern) {
            if (preg_match($pattern, $refId)) {
                return [
                    'valid' => true,
                    'type' => $prefix
                ];
            }
        }
        
        // Allow custom if configured
        if ($cfg['allow_custom']) {
            return [
                'valid' => true,
                'type' => 'custom'
            ];
        }
        
        return [
            'valid' => false,
            'error' => 'REF-ID does not match any known pattern'
        ];
    }
    
    /**
     * Validate file structure
     */
    public function validateStructure($filePath) {
        $errors = [];
        $warnings = [];
        $cfg = $this->config['structure'];
        
        if (!file_exists($filePath)) {
            return [
                'valid' => false,
                'errors' => ['File does not exist']
            ];
        }
        
        $content = file_get_contents($filePath);
        $lines = explode("\n", $content);
        
        // Check title (first line)
        if ($cfg['require_title'] && (empty($lines[0]) || substr($lines[0], 0, 1) !== '#')) {
            $errors[] = 'Missing title (first line should start with #)';
        }
        
        // Extract header
        $headerEnd = $this->findHeaderEnd($lines);
        
        if ($headerEnd === false) {
            if ($cfg['require_separator']) {
                $errors[] = 'Missing header separator (---)';
            }
            $headerEnd = min($cfg['max_header_lines'], count($lines));
        }
        
        $headerLines = array_slice($lines, 0, $headerEnd);
        $metadata = $this->extractMetadata($headerLines);
        
        // Check required fields
        foreach ($this->config['required_fields'] as $field) {
            if (!isset($metadata[$field])) {
                $errors[] = "Missing required field: {$field}";
            }
        }
        
        // Warn about missing optional fields
        if ($this->config['warnings']['warn_on_missing_optional_fields']) {
            foreach ($this->config['optional_fields'] as $field) {
                if (!isset($metadata[$field])) {
                    $warnings[] = "Missing optional field: {$field}";
                }
            }
        }
        
        // Check encoding
        if ($this->config['content']['check_encoding']) {
            if (!mb_check_encoding($content, $this->config['content']['required_encoding'])) {
                $errors[] = 'Invalid encoding (must be UTF-8)';
            }
        }
        
        // Check line count
        if ($this->config['content']['max_file_lines'] > 0) {
            if (count($lines) > $this->config['content']['max_file_lines']) {
                $errors[] = "File exceeds maximum lines ({$this->config['content']['max_file_lines']})";
            }
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors,
            'warnings' => $warnings,
            'metadata' => $metadata
        ];
    }
    
    /**
     * Find header end (separator line)
     */
    private function findHeaderEnd($lines) {
        $pattern = $this->config['structure']['separator_pattern'];
        
        foreach ($lines as $i => $line) {
            if (preg_match($pattern, trim($line))) {
                return $i;
            }
        }
        
        return false;
    }
    
    /**
     * Extract metadata from header
     */
    private function extractMetadata($lines) {
        $metadata = [];
        
        foreach ($lines as $line) {
            if (preg_match('/\*\*(.+?):\*\*\s*(.+)/', $line, $matches)) {
                $field = trim($matches[1]);
                $value = trim($matches[2]);
                $metadata[$field] = $value;
            }
        }
        
        return $metadata;
    }
    
    /**
     * Validate cross-references
     */
    public function validateCrossReferences($files) {
        $errors = [];
        $refIds = [];
        
        // Build REF-ID map
        foreach ($files as $file) {
            $path = $file['path'] ?? $file;
            
            if (!file_exists($path)) {
                continue;
            }
            
            $content = file_get_contents($path);
            $lines = explode("\n", $content);
            $metadata = $this->extractMetadata($lines);
            
            if (isset($metadata['REF-ID'])) {
                $refIds[$metadata['REF-ID']] = $path;
            }
        }
        
        // Check cross-references
        $pattern = $this->config['cross_references']['ref_pattern'];
        
        foreach ($files as $file) {
            $path = $file['path'] ?? $file;
            
            if (!file_exists($path)) {
                continue;
            }
            
            $content = file_get_contents($path);
            
            // Find all REF-ID references
            if (preg_match_all($pattern, $content, $matches)) {
                foreach ($matches[1] as $refList) {
                    $refs = array_map('trim', explode(',', $refList));
                    
                    foreach ($refs as $ref) {
                        if (!isset($refIds[$ref])) {
                            $errors[] = [
                                'file' => $path,
                                'broken_ref' => $ref,
                                'error' => 'Referenced REF-ID not found'
                            ];
                        }
                    }
                }
            }
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors,
            'total_refs' => count($refIds)
        ];
    }
    
    /**
     * Find duplicates
     */
    public function findDuplicates($files, $criteria = 'filename') {
        $groups = [];
        $cfg = $this->config['duplicates'];
        
        foreach ($files as $file) {
            $key = null;
            
            switch ($criteria) {
                case 'filename':
                    if (!$cfg['check_by_filename']) continue 2;
                    $path = $file['path'] ?? $file;
                    $key = basename($path);
                    break;
                    
                case 'refid':
                    if (!$cfg['check_by_refid']) continue 2;
                    $key = $file['ref_id'] ?? null;
                    break;
                    
                case 'checksum':
                    if (!$cfg['check_by_checksum']) continue 2;
                    $key = $file['checksum'] ?? null;
                    break;
            }
            
            if ($key === null) {
                continue;
            }
            
            if (!isset($groups[$key])) {
                $groups[$key] = [];
            }
            
            $groups[$key][] = $file;
        }
        
        // Filter to only duplicates
        $duplicates = [];
        foreach ($groups as $key => $group) {
            if (count($group) > 1) {
                $duplicates[$key] = $group;
            }
        }
        
        return [
            'has_duplicates' => !empty($duplicates),
            'duplicates' => $duplicates,
            'count' => count($duplicates)
        ];
    }
    
    /**
     * Validate line endings
     */
    public function validateLineEndings($content) {
        if (!$this->config['content']['check_line_endings']) {
            return ['valid' => true];
        }
        
        $required = $this->config['content']['required_line_ending'];
        
        // Check for CRLF
        if ($required === "\n" && strpos($content, "\r\n") !== false) {
            return [
                'valid' => false,
                'error' => 'File contains CRLF line endings (should be LF)'
            ];
        }
        
        // Check for CR
        if ($required === "\n" && strpos($content, "\r") !== false) {
            return [
                'valid' => false,
                'error' => 'File contains CR line endings (should be LF)'
            ];
        }
        
        return ['valid' => true];
    }
    
    /**
     * Extract all REF-IDs from file
     */
    public function extractRefIds($filePath) {
        if (!file_exists($filePath)) {
            return [];
        }
        
        $content = file_get_contents($filePath);
        $refIds = [];
        $pattern = $this->config['cross_references']['ref_pattern'];
        
        if (preg_match_all($pattern, $content, $matches)) {
            foreach ($matches[1] as $refList) {
                $refs = array_map('trim', explode(',', $refList));
                $refIds = array_merge($refIds, $refs);
            }
        }
        
        return array_unique($refIds);
    }
}
?>
