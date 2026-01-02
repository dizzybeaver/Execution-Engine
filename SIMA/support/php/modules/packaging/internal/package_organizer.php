<?php
/**
 * package_organizer.php
 * 
 * Package Organization Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use PackagingModule API
 */

class PackageOrganizer {
    private $config;
    private $customStructure = null;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Set custom structure
     */
    public function setStructure($structure) {
        $this->customStructure = $structure;
    }
    
    /**
     * Organize files
     */
    public function organize($files, $structure = 'categorized') {
        if ($this->customStructure) {
            return $this->organizeByCustomStructure($files);
        }
        
        switch ($structure) {
            case 'flat':
                return $this->organizeFlat($files);
                
            case 'categorized':
                return $this->organizeCategorized($files);
                
            case 'hierarchical':
                return $this->organizeHierarchical($files);
                
            case 'domain-based':
                return $this->organizeDomainBased($files);
                
            default:
                return $this->organizeCategorized($files);
        }
    }
    
    /**
     * Organize flat (all files in root)
     */
    private function organizeFlat($files) {
        $organized = [];
        
        foreach ($files as $file) {
            $filename = $this->getFilename($file);
            $organized[$filename] = $file;
        }
        
        return $organized;
    }
    
    /**
     * Organize by category
     */
    private function organizeCategorized($files) {
        $organized = [];
        $directories = $this->config['structures']['categorized']['directories'];
        
        foreach ($files as $file) {
            $category = $this->getCategory($file);
            $filename = $this->getFilename($file);
            
            // Get target directory
            $targetDir = $directories[$category] ?? $directories['other'];
            $targetPath = $targetDir . $filename;
            
            $organized[$targetPath] = $file;
        }
        
        return $organized;
    }
    
    /**
     * Organize hierarchically (preserve structure)
     */
    private function organizeHierarchical($files) {
        $organized = [];
        
        foreach ($files as $file) {
            $path = is_array($file) ? ($file['relative_path'] ?? $file['path']) : $file;
            $organized[$path] = $file;
        }
        
        return $organized;
    }
    
    /**
     * Organize by domain
     */
    private function organizeDomainBased($files) {
        $organized = [];
        $directories = $this->config['structures']['domain-based']['directories'];
        
        foreach ($files as $file) {
            $domain = $this->getDomain($file);
            $filename = $this->getFilename($file);
            
            // Get target directory
            $targetDir = $directories[$domain] ?? 'other/';
            $targetPath = $targetDir . $filename;
            
            $organized[$targetPath] = $file;
        }
        
        return $organized;
    }
    
    /**
     * Organize by custom structure
     */
    private function organizeByCustomStructure($files) {
        $organized = [];
        
        foreach ($files as $file) {
            $targetPath = $this->resolveCustomPath($file);
            $organized[$targetPath] = $file;
        }
        
        return $organized;
    }
    
    /**
     * Get filename from file
     */
    private function getFilename($file) {
        if (is_array($file)) {
            return $file['filename'] ?? basename($file['path'] ?? '');
        }
        
        return basename($file);
    }
    
    /**
     * Get category from file
     */
    private function getCategory($file) {
        if (is_array($file)) {
            if (isset($file['category'])) {
                return $file['category'];
            }
            
            // Try to determine from path
            $path = $file['path'] ?? '';
            
            if (strpos($path, '/lessons/') !== false) {
                return 'lessons';
            } elseif (strpos($path, '/decisions/') !== false) {
                return 'decisions';
            } elseif (strpos($path, '/anti-patterns/') !== false) {
                return 'anti-patterns';
            } elseif (strpos($path, '/specifications/') !== false) {
                return 'specifications';
            } elseif (strpos($path, '/workflows/') !== false) {
                return 'workflows';
            }
        }
        
        return 'other';
    }
    
    /**
     * Get domain from file
     */
    private function getDomain($file) {
        if (is_array($file)) {
            if (isset($file['domain'])) {
                return $file['domain'];
            }
            
            // Try to determine from path
            $path = $file['path'] ?? '';
            
            if (strpos($path, '/generic/') !== false || strpos($path, 'generic/') === 0) {
                return 'generic';
            } elseif (strpos($path, '/platforms/') !== false || strpos($path, 'platforms/') === 0) {
                return 'platforms';
            } elseif (strpos($path, '/languages/') !== false || strpos($path, 'languages/') === 0) {
                return 'languages';
            } elseif (strpos($path, '/projects/') !== false || strpos($path, 'projects/') === 0) {
                return 'projects';
            }
        }
        
        return 'other';
    }
    
    /**
     * Resolve custom path
     */
    private function resolveCustomPath($file) {
        $filename = $this->getFilename($file);
        
        // Check if custom structure has mapping for this file
        if (isset($this->customStructure['mappings'])) {
            foreach ($this->customStructure['mappings'] as $pattern => $targetDir) {
                if (preg_match($pattern, $filename)) {
                    return $targetDir . $filename;
                }
            }
        }
        
        // Use default directory if specified
        if (isset($this->customStructure['default'])) {
            return $this->customStructure['default'] . $filename;
        }
        
        // Fallback to flat
        return $filename;
    }
    
    /**
     * Group files by criteria
     */
    public function groupBy($files, $criteria) {
        $grouped = [];
        
        foreach ($files as $file) {
            $key = null;
            
            switch ($criteria) {
                case 'category':
                    $key = $this->getCategory($file);
                    break;
                    
                case 'domain':
                    $key = $this->getDomain($file);
                    break;
                    
                case 'extension':
                    $filename = $this->getFilename($file);
                    $key = pathinfo($filename, PATHINFO_EXTENSION);
                    break;
                    
                case 'directory':
                    $path = is_array($file) ? ($file['path'] ?? '') : $file;
                    $key = dirname($path);
                    break;
            }
            
            if ($key === null) {
                $key = 'ungrouped';
            }
            
            if (!isset($grouped[$key])) {
                $grouped[$key] = [];
            }
            
            $grouped[$key][] = $file;
        }
        
        return $grouped;
    }
    
    /**
     * Create directory structure
     */
    public function createStructure($basePath, $structure) {
        switch ($structure) {
            case 'categorized':
                $dirs = $this->config['structures']['categorized']['directories'];
                break;
                
            case 'domain-based':
                $dirs = $this->config['structures']['domain-based']['directories'];
                break;
                
            default:
                return;
        }
        
        foreach ($dirs as $dir) {
            $fullPath = $basePath . '/' . $dir;
            if (!is_dir($fullPath)) {
                mkdir($fullPath, 0755, true);
            }
        }
    }
    
    /**
     * Flatten hierarchy
     */
    public function flatten($files) {
        $flattened = [];
        
        foreach ($files as $file) {
            $filename = $this->getFilename($file);
            
            // Handle duplicates by adding counter
            $targetName = $filename;
            $counter = 1;
            
            while (isset($flattened[$targetName])) {
                $name = pathinfo($filename, PATHINFO_FILENAME);
                $ext = pathinfo($filename, PATHINFO_EXTENSION);
                $targetName = $name . '_' . $counter . '.' . $ext;
                $counter++;
            }
            
            $flattened[$targetName] = $file;
        }
        
        return $flattened;
    }
}
?>
