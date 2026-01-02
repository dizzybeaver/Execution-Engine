<?php
/**
 * version_detector.php
 * 
 * Version Detection Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use VersionModule API
 */

class VersionDetector {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Detect version from directory
     */
    public function detect($basePath) {
        if (!is_dir($basePath)) {
            return ['error' => 'Directory does not exist'];
        }
        
        $methods = $this->config['detection']['methods'];
        $results = [];
        
        // Try each detection method
        foreach ($methods as $method) {
            switch ($method) {
                case 'structure':
                    $results['structure'] = $this->detectByStructure($basePath);
                    break;
                    
                case 'file_header':
                    $results['file_header'] = $this->detectByFileHeaders($basePath);
                    break;
                    
                case 'metadata':
                    $results['metadata'] = $this->detectByMetadata($basePath);
                    break;
            }
        }
        
        // Determine most likely version
        return $this->determineVersion($results);
    }
    
    /**
     * Detect version by directory structure
     */
    private function detectByStructure($basePath) {
        $scores = [];
        
        foreach ($this->config['structure_signatures'] as $version => $signature) {
            $score = 0;
            $total = 0;
            
            // Check directories
            foreach ($signature['directories'] as $dir) {
                $total++;
                if (is_dir($basePath . '/' . $dir)) {
                    $score++;
                }
            }
            
            // Check required files
            foreach ($signature['required_files'] as $file) {
                $total += 2; // Required files weighted higher
                if (file_exists($basePath . '/' . $file)) {
                    $score += 2;
                }
            }
            
            // Check optional files
            foreach ($signature['optional_files'] as $file) {
                $total++;
                if (file_exists($basePath . '/' . $file)) {
                    $score++;
                }
            }
            
            $scores[$version] = $total > 0 ? $score / $total : 0;
        }
        
        arsort($scores);
        $topVersion = key($scores);
        $confidence = $scores[$topVersion];
        
        return [
            'version' => $topVersion,
            'confidence' => $confidence,
            'scores' => $scores
        ];
    }
    
    /**
     * Detect version by checking file headers
     */
    private function detectByFileHeaders($basePath) {
        $maxFiles = $this->config['detection']['max_files_to_check'];
        $versions = [];
        
        // Get markdown files
        $files = $this->getMDFiles($basePath, $maxFiles);
        
        foreach ($files as $file) {
            $version = $this->extractVersionFromFile($file);
            if ($version) {
                if (!isset($versions[$version])) {
                    $versions[$version] = 0;
                }
                $versions[$version]++;
            }
        }
        
        if (empty($versions)) {
            return [
                'version' => null,
                'confidence' => 0,
                'versions' => []
            ];
        }
        
        arsort($versions);
        $topVersion = key($versions);
        $confidence = $versions[$topVersion] / count($files);
        
        return [
            'version' => $topVersion,
            'confidence' => $confidence,
            'versions' => $versions
        ];
    }
    
    /**
     * Detect version by metadata fields
     */
    private function detectByMetadata($basePath) {
        $maxFiles = $this->config['detection']['max_files_to_check'];
        $files = $this->getMDFiles($basePath, $maxFiles);
        $scores = [];
        
        foreach ($this->config['metadata_fields'] as $version => $fields) {
            $score = 0;
            $total = 0;
            
            foreach ($files as $file) {
                $content = file_get_contents($file);
                $lines = explode("\n", $content);
                $headerLines = array_slice($lines, 0, 20);
                $header = implode("\n", $headerLines);
                
                foreach ($fields as $field) {
                    $total++;
                    if (preg_match('/\*\*' . preg_quote($field) . ':\*\*/', $header)) {
                        $score++;
                    }
                }
            }
            
            $scores[$version] = $total > 0 ? $score / $total : 0;
        }
        
        arsort($scores);
        $topVersion = key($scores);
        $confidence = $scores[$topVersion];
        
        return [
            'version' => $topVersion,
            'confidence' => $confidence,
            'scores' => $scores
        ];
    }
    
    /**
     * Determine final version from results
     */
    private function determineVersion($results) {
        $priority = $this->config['detection']['priority'];
        $threshold = $this->config['detection']['confidence_threshold'];
        
        // Check methods in priority order
        foreach ($priority as $method) {
            if (!isset($results[$method])) {
                continue;
            }
            
            $result = $results[$method];
            
            if ($result['confidence'] >= $threshold) {
                return [
                    'version' => $result['version'],
                    'confidence' => $result['confidence'],
                    'method' => $method,
                    'all_results' => $results
                ];
            }
        }
        
        // If no method meets threshold, return best guess
        $bestMethod = null;
        $bestConfidence = 0;
        $bestVersion = null;
        
        foreach ($results as $method => $result) {
            if ($result['confidence'] > $bestConfidence) {
                $bestConfidence = $result['confidence'];
                $bestVersion = $result['version'];
                $bestMethod = $method;
            }
        }
        
        return [
            'version' => $bestVersion,
            'confidence' => $bestConfidence,
            'method' => $bestMethod,
            'warning' => 'Low confidence detection',
            'all_results' => $results
        ];
    }
    
    /**
     * Get markdown files from directory
     */
    private function getMDFiles($basePath, $maxFiles) {
        $files = [];
        $iterator = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($basePath),
            RecursiveIteratorIterator::SELF_FIRST
        );
        
        foreach ($iterator as $file) {
            if ($file->isFile() && $file->getExtension() === 'md') {
                $files[] = $file->getPathname();
                
                if (count($files) >= $maxFiles) {
                    break;
                }
            }
        }
        
        return $files;
    }
    
    /**
     * Extract version from file
     */
    private function extractVersionFromFile($filePath) {
        $content = file_get_contents($filePath);
        return $this->extractVersionFromContent($content);
    }
    
    /**
     * Extract version from content
     */
    public function extractVersionFromContent($content) {
        $patterns = $this->config['file_patterns'];
        
        foreach ($patterns as $pattern) {
            if (preg_match($pattern, $content, $matches)) {
                $version = $matches[1];
                
                // Validate version
                if (in_array($version, $this->config['supported_versions'])) {
                    return $version;
                }
            }
        }
        
        return null;
    }
    
    /**
     * Detect version from file
     */
    public function detectFromFile($filePath) {
        if (!file_exists($filePath)) {
            return ['error' => 'File does not exist'];
        }
        
        $version = $this->extractVersionFromFile($filePath);
        
        if ($version) {
            return [
                'version' => $version,
                'confidence' => 1.0,
                'method' => 'file_header'
            ];
        }
        
        return [
            'version' => $this->config['default_version'],
            'confidence' => 0.0,
            'method' => 'default',
            'warning' => 'Version not found, using default'
        ];
    }
    
    /**
     * Get version information
     */
    public function getVersionInfo($version) {
        if (!isset($this->config['version_info'][$version])) {
            return [
                'error' => 'Unknown version: ' . $version
            ];
        }
        
        $info = $this->config['version_info'][$version];
        $info['version'] = $version;
        $info['supported'] = in_array($version, $this->config['supported_versions']);
        
        return $info;
    }
}
?>
