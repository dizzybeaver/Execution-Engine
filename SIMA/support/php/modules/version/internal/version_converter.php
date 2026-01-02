<?php
/**
 * version_converter.php
 * 
 * Version Conversion Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use VersionModule API
 */

class VersionConverter {
    private $config;
    private $customConverters = [];
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Convert content between versions
     */
    public function convert($content, $fromVersion, $toVersion) {
        if ($fromVersion === $toVersion) {
            return $content;
        }
        
        if (!$this->config['conversion']['enabled']) {
            return $content;
        }
        
        // Check for custom converter
        $key = "{$fromVersion}-{$toVersion}";
        if (isset($this->customConverters[$key])) {
            return call_user_func($this->customConverters[$key], $content);
        }
        
        // Use built-in conversion
        return $this->performConversion($content, $fromVersion, $toVersion);
    }
    
    /**
     * Perform built-in conversion
     */
    private function performConversion($content, $fromVersion, $toVersion) {
        // Update header
        if ($this->config['conversion_options']['update_header']) {
            $content = $this->convertHeader($content, $fromVersion, $toVersion);
        }
        
        // Add missing fields
        if ($this->config['conversion_options']['add_missing_fields']) {
            $content = $this->addMissingFields($content, $fromVersion, $toVersion);
        }
        
        // Update cross-references
        if ($this->config['conversion_options']['update_cross_references']) {
            $content = $this->updateCrossReferences($content, $fromVersion, $toVersion);
        }
        
        return $content;
    }
    
    /**
     * Convert header format
     */
    private function convertHeader($content, $fromVersion, $toVersion) {
        $lines = explode("\n", $content);
        
        // Extract current metadata
        $metadata = $this->extractMetadata($lines);
        
        // Get target format
        $targetFormat = $this->config['header_formats'][$toVersion] ?? null;
        
        if (!$targetFormat) {
            return $content;
        }
        
        // Find header end
        $headerEnd = 0;
        foreach ($lines as $i => $line) {
            if (trim($line) === '---') {
                $headerEnd = $i;
                break;
            }
        }
        
        // Build new header
        $newHeader = $this->buildHeader($metadata, $toVersion);
        
        // Replace header
        $newLines = array_merge(
            explode("\n", $newHeader),
            array_slice($lines, $headerEnd)
        );
        
        return implode("\n", $newLines);
    }
    
    /**
     * Extract metadata from lines
     */
    private function extractMetadata($lines) {
        $metadata = [];
        
        foreach ($lines as $line) {
            if (preg_match('/\*\*(.+?):\*\*\s*(.+)/', $line, $matches)) {
                $field = $matches[1];
                $value = $matches[2];
                $metadata[$field] = $value;
            }
        }
        
        return $metadata;
    }
    
    /**
     * Build header for version
     */
    private function buildHeader($metadata, $version) {
        $format = $this->config['header_formats'][$version];
        $fields = $this->config['metadata_fields'][$version];
        
        // Get filename (first line should be # filename)
        $filename = $metadata['filename'] ?? 'Unnamed';
        
        // Prepare field values
        $values = [$filename];
        
        foreach ($fields as $field) {
            $values[] = $metadata[$field] ?? '';
        }
        
        return vsprintf($format, $values) . "---\n";
    }
    
    /**
     * Add missing fields
     */
    private function addMissingFields($content, $fromVersion, $toVersion) {
        $key = "{$fromVersion}-{$toVersion}";
        
        if (!isset($this->config['field_mappings'][$key])) {
            return $content;
        }
        
        $mapping = $this->config['field_mappings'][$key];
        
        if (isset($mapping['add'])) {
            $lines = explode("\n", $content);
            $headerEnd = 0;
            
            foreach ($lines as $i => $line) {
                if (trim($line) === '---') {
                    $headerEnd = $i;
                    break;
                }
            }
            
            // Add new fields before separator
            $additions = [];
            foreach ($mapping['add'] as $field) {
                $additions[] = "**{$field}:** ";
            }
            
            array_splice($lines, $headerEnd, 0, $additions);
            $content = implode("\n", $lines);
        }
        
        return $content;
    }
    
    /**
     * Update cross-references
     */
    private function updateCrossReferences($content, $fromVersion, $toVersion) {
        // Update path references if needed
        $key = "{$fromVersion}-{$toVersion}";
        
        if (!isset($this->config['path_conversions'][$key])) {
            return $content;
        }
        
        $conversions = $this->config['path_conversions'][$key];
        
        foreach ($conversions as $oldPath => $newPath) {
            $content = str_replace($oldPath, $newPath, $content);
        }
        
        return $content;
    }
    
    /**
     * Add version tags
     */
    public function addVersionTags($content, $version, $metadata = []) {
        if (!$this->config['tag_injection']['enabled']) {
            return $content;
        }
        
        $position = $this->config['tag_injection']['position'];
        $format = $this->config['tag_injection']['format'];
        $separator = $this->config['tag_injection']['separator'];
        
        $packageName = $metadata['package_name'] ?? 'Unknown';
        $exportDate = $metadata['export_date'] ?? date('Y-m-d');
        
        $tags = sprintf($format, $version, $exportDate, $packageName);
        
        $lines = explode("\n", $content);
        
        if ($position === 'after_header') {
            // Find header end
            $insertPos = 0;
            foreach ($lines as $i => $line) {
                if (trim($line) === $separator) {
                    $insertPos = $i + 1;
                    break;
                }
            }
            
            array_splice($lines, $insertPos, 0, explode("\n", $tags));
        } else {
            // Before footer
            $lines[] = $tags;
        }
        
        return implode("\n", $lines);
    }
    
    /**
     * Remove version tags
     */
    public function removeVersionTags($content) {
        $lines = explode("\n", $content);
        $filtered = [];
        
        foreach ($lines as $line) {
            if (preg_match('/\*\*(SIMA Version|Exported|Export Package):\*\*/', $line)) {
                continue;
            }
            $filtered[] = $line;
        }
        
        return implode("\n", $filtered);
    }
    
    /**
     * Batch convert files
     */
    public function batchConvert($files, $toVersion) {
        $results = [
            'success' => [],
            'failed' => [],
            'skipped' => []
        ];
        
        require_once __DIR__ . '/version_detector.php';
        $detector = new VersionDetector($this->config);
        
        foreach ($files as $file) {
            $path = $file['path'] ?? $file;
            
            if (!file_exists($path)) {
                $results['failed'][] = [
                    'path' => $path,
                    'error' => 'File does not exist'
                ];
                continue;
            }
            
            $content = file_get_contents($path);
            $versionInfo = $detector->detectFromFile($path);
            
            if (isset($versionInfo['error'])) {
                $results['failed'][] = [
                    'path' => $path,
                    'error' => $versionInfo['error']
                ];
                continue;
            }
            
            $fromVersion = $versionInfo['version'];
            
            if ($fromVersion === $toVersion) {
                $results['skipped'][] = [
                    'path' => $path,
                    'reason' => 'Already target version'
                ];
                continue;
            }
            
            $converted = $this->convert($content, $fromVersion, $toVersion);
            
            $results['success'][] = [
                'path' => $path,
                'from_version' => $fromVersion,
                'to_version' => $toVersion,
                'content' => $converted
            ];
        }
        
        return $results;
    }
    
    /**
     * Register custom converter
     */
    public function registerConverter($fromVersion, $toVersion, $callback) {
        $key = "{$fromVersion}-{$toVersion}";
        $this->customConverters[$key] = $callback;
    }
}
?>
