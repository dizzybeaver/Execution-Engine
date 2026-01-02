<?php
/**
 * version_compatibility.php
 * 
 * Version Compatibility Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use VersionModule API
 */

class VersionCompatibility {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Check if conversion is possible
     */
    public function canConvert($fromVersion, $toVersion) {
        if ($fromVersion === $toVersion) {
            return true;
        }
        
        // Check conversion paths
        if (isset($this->config['conversion_paths'][$fromVersion])) {
            if (in_array($toVersion, $this->config['conversion_paths'][$fromVersion])) {
                return true;
            }
        }
        
        // Check backward compatibility
        if (isset($this->config['backward_compatible'][$toVersion])) {
            if (in_array($fromVersion, $this->config['backward_compatible'][$toVersion])) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Check version compatibility
     */
    public function checkCompatibility($version1, $version2) {
        $key1 = "{$version1}-{$version2}";
        $key2 = "{$version2}-{$version1}";
        
        $status1 = $this->config['compatibility_matrix'][$key1] ?? null;
        $status2 = $this->config['compatibility_matrix'][$key2] ?? null;
        
        if ($status1) {
            return [
                'compatible' => true,
                'type' => $status1,
                'from' => $version1,
                'to' => $version2
            ];
        }
        
        if ($status2) {
            return [
                'compatible' => true,
                'type' => $status2,
                'from' => $version2,
                'to' => $version1
            ];
        }
        
        return [
            'compatible' => false,
            'type' => 'incompatible',
            'from' => $version1,
            'to' => $version2
        ];
    }
    
    /**
     * Compare versions
     */
    public function compare($version1, $version2) {
        $v1Parts = explode('.', $version1);
        $v2Parts = explode('.', $version2);
        
        $maxLength = max(count($v1Parts), count($v2Parts));
        
        for ($i = 0; $i < $maxLength; $i++) {
            $v1 = isset($v1Parts[$i]) ? (int)$v1Parts[$i] : 0;
            $v2 = isset($v2Parts[$i]) ? (int)$v2Parts[$i] : 0;
            
            if ($v1 < $v2) {
                return -1;
            } elseif ($v1 > $v2) {
                return 1;
            }
        }
        
        return 0;
    }
    
    /**
     * Validate version string
     */
    public function isValidVersion($version) {
        // Check if in supported versions
        if (in_array($version, $this->config['supported_versions'])) {
            return true;
        }
        
        // Check format (X.Y or X.Y.Z)
        if (preg_match('/^\d+\.\d+(\.\d+)?$/', $version)) {
            return true;
        }
        
        return false;
    }
    
    /**
     * Get conversion path
     */
    public function getConversionPath($fromVersion, $toVersion) {
        if ($fromVersion === $toVersion) {
            return [
                'steps' => [],
                'direct' => true
            ];
        }
        
        // Check for direct conversion
        if ($this->canConvert($fromVersion, $toVersion)) {
            return [
                'steps' => [$fromVersion, $toVersion],
                'direct' => true
            ];
        }
        
        // Find indirect path
        $path = $this->findConversionPath($fromVersion, $toVersion);
        
        if ($path) {
            return [
                'steps' => $path,
                'direct' => false
            ];
        }
        
        return [
            'steps' => [],
            'direct' => false,
            'error' => 'No conversion path found'
        ];
    }
    
    /**
     * Find conversion path (BFS)
     */
    private function findConversionPath($fromVersion, $toVersion) {
        $queue = [[$fromVersion]];
        $visited = [$fromVersion => true];
        
        while (!empty($queue)) {
            $path = array_shift($queue);
            $current = end($path);
            
            if ($current === $toVersion) {
                return $path;
            }
            
            // Get possible next versions
            $nextVersions = $this->config['conversion_paths'][$current] ?? [];
            
            foreach ($nextVersions as $next) {
                if (!isset($visited[$next])) {
                    $visited[$next] = true;
                    $newPath = $path;
                    $newPath[] = $next;
                    $queue[] = $newPath;
                }
            }
        }
        
        return null;
    }
    
    /**
     * Get compatible versions
     */
    public function getCompatibleVersions($version) {
        $compatible = [];
        
        // Forward compatible (can convert to)
        if (isset($this->config['conversion_paths'][$version])) {
            $compatible['forward'] = $this->config['conversion_paths'][$version];
        } else {
            $compatible['forward'] = [];
        }
        
        // Backward compatible (can read from)
        if (isset($this->config['backward_compatible'][$version])) {
            $compatible['backward'] = $this->config['backward_compatible'][$version];
        } else {
            $compatible['backward'] = [];
        }
        
        return $compatible;
    }
    
    /**
     * Check if version is current
     */
    public function isCurrent($version) {
        $info = $this->config['version_info'][$version] ?? null;
        
        if (!$info) {
            return false;
        }
        
        return ($info['status'] ?? '') === 'current';
    }
    
    /**
     * Check if version is deprecated
     */
    public function isDeprecated($version) {
        $info = $this->config['version_info'][$version] ?? null;
        
        if (!$info) {
            return false;
        }
        
        return ($info['status'] ?? '') === 'deprecated';
    }
    
    /**
     * Get upgrade recommendations
     */
    public function getUpgradeRecommendations($currentVersion) {
        $recommendations = [];
        
        // Get all versions
        $versions = $this->config['supported_versions'];
        
        foreach ($versions as $version) {
            if ($this->compare($version, $currentVersion) > 0) {
                $info = $this->config['version_info'][$version] ?? null;
                
                if ($info) {
                    $canConvert = $this->canConvert($currentVersion, $version);
                    $path = $this->getConversionPath($currentVersion, $version);
                    
                    $recommendations[] = [
                        'version' => $version,
                        'name' => $info['name'],
                        'status' => $info['status'],
                        'features' => $info['features'],
                        'can_convert' => $canConvert,
                        'conversion_path' => $path,
                        'recommended' => $info['status'] === 'current'
                    ];
                }
            }
        }
        
        return $recommendations;
    }
    
    /**
     * Check breaking changes
     */
    public function hasBreakingChanges($fromVersion, $toVersion) {
        // Breaking changes occur when major version changes
        $fromParts = explode('.', $fromVersion);
        $toParts = explode('.', $toVersion);
        
        $fromMajor = (int)($fromParts[0] ?? 0);
        $toMajor = (int)($toParts[0] ?? 0);
        
        return $toMajor > $fromMajor;
    }
    
    /**
     * Get version features
     */
    public function getFeatures($version) {
        $info = $this->config['version_info'][$version] ?? null;
        
        if (!$info) {
            return [];
        }
        
        return $info['features'] ?? [];
    }
    
    /**
     * Compare features between versions
     */
    public function compareFeatures($version1, $version2) {
        $features1 = $this->getFeatures($version1);
        $features2 = $this->getFeatures($version2);
        
        return [
            'added' => array_diff($features2, $features1),
            'removed' => array_diff($features1, $features2),
            'common' => array_intersect($features1, $features2)
        ];
    }
}
?>
