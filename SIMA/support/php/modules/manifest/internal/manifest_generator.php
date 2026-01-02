<?php
/**
 * manifest_generator.php
 * 
 * Manifest Generation Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use ManifestModule API
 */

class ManifestGenerator {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Generate manifest
     */
    public function generate($operation, $files, $metadata = []) {
        $manifest = [
            'operation' => $operation,
            'archive' => $this->generateArchiveMetadata($metadata, $files),
            'files' => $this->generateFileMetadata($files)
        ];
        
        if ($this->config['statistics']['enabled']) {
            $manifest['statistics'] = $this->generateStatistics($files);
        }
        
        return $this->arrayToYaml($manifest);
    }
    
    /**
     * Generate archive metadata section
     */
    private function generateArchiveMetadata($metadata, $files) {
        $archive = [
            'name' => $metadata['archive_name'] ?? 'archive',
            'created' => date($this->config['format']['date_format']),
            'description' => $metadata['description'] ?? '',
            'total_files' => count($files)
        ];
        
        if ($this->config['archive']['include_source_version'] && isset($metadata['source_version'])) {
            $archive['source_version'] = $metadata['source_version'];
        }
        
        if ($this->config['archive']['include_target_version'] && isset($metadata['target_version'])) {
            $archive['target_version'] = $metadata['target_version'];
        }
        
        if ($this->config['archive']['include_converted_count']) {
            $converted = 0;
            foreach ($files as $file) {
                if (isset($file['converted']) && $file['converted']) {
                    $converted++;
                }
            }
            if ($converted > 0) {
                $archive['converted_files'] = $converted;
            }
        }
        
        return $archive;
    }
    
    /**
     * Generate file metadata entries
     */
    private function generateFileMetadata($files) {
        $fileList = [];
        $cfg = $this->config['file_metadata'];
        
        foreach ($files as $file) {
            $entry = [];
            
            if ($cfg['include_filename']) {
                $entry['filename'] = $file['filename'] ?? basename($file['path'] ?? '');
            }
            
            if ($cfg['include_path']) {
                $entry['path'] = $file['relative_path'] ?? $file['path'] ?? '';
            }
            
            if ($cfg['include_ref_id']) {
                $entry['ref_id'] = $file['ref_id'] ?? '';
            }
            
            if ($cfg['include_category']) {
                $entry['category'] = $file['category'] ?? 'unknown';
            }
            
            if ($cfg['include_size']) {
                $entry['size'] = $file['size'] ?? 0;
            }
            
            if ($cfg['include_checksum'] && $this->config['format']['include_checksums']) {
                $entry['checksum'] = $file['checksum'] ?? '';
            }
            
            if ($cfg['include_version'] && isset($file['version'])) {
                $entry['version'] = $file['version'];
            }
            
            if ($cfg['include_modified'] && isset($file['modified'])) {
                $entry['modified'] = $file['modified'];
            }
            
            $fileList[] = $entry;
        }
        
        return $fileList;
    }
    
    /**
     * Generate statistics section
     */
    public function generateStatistics($files) {
        $stats = [];
        $cfg = $this->config['statistics'];
        
        if ($cfg['count_by_domain']) {
            $stats['by_domain'] = $this->countByDomain($files);
        }
        
        if ($cfg['count_by_category']) {
            $stats['by_category'] = $this->countByCategory($files);
        }
        
        if ($cfg['count_by_extension']) {
            $stats['by_extension'] = $this->countByExtension($files);
        }
        
        if ($cfg['calculate_total_size']) {
            $totalSize = 0;
            foreach ($files as $file) {
                $totalSize += $file['size'] ?? 0;
            }
            $stats['total_size'] = $totalSize;
        }
        
        if ($cfg['list_ref_ids']) {
            $refIds = [];
            foreach ($files as $file) {
                if (!empty($file['ref_id'])) {
                    $refIds[] = $file['ref_id'];
                }
            }
            $stats['ref_ids'] = $refIds;
        }
        
        return $stats;
    }
    
    /**
     * Count files by domain
     */
    private function countByDomain($files) {
        $counts = [];
        
        foreach ($files as $file) {
            $path = $file['path'] ?? $file['relative_path'] ?? '';
            $domain = $this->extractDomain($path);
            
            if (!isset($counts[$domain])) {
                $counts[$domain] = 0;
            }
            $counts[$domain]++;
        }
        
        return $counts;
    }
    
    /**
     * Count files by category
     */
    private function countByCategory($files) {
        $counts = [];
        
        foreach ($files as $file) {
            $category = $file['category'] ?? 'unknown';
            
            if (!isset($counts[$category])) {
                $counts[$category] = 0;
            }
            $counts[$category]++;
        }
        
        return $counts;
    }
    
    /**
     * Count files by extension
     */
    private function countByExtension($files) {
        $counts = [];
        
        foreach ($files as $file) {
            $filename = $file['filename'] ?? basename($file['path'] ?? '');
            $ext = pathinfo($filename, PATHINFO_EXTENSION);
            $ext = $ext ? '.' . $ext : 'no_extension';
            
            if (!isset($counts[$ext])) {
                $counts[$ext] = 0;
            }
            $counts[$ext]++;
        }
        
        return $counts;
    }
    
    /**
     * Extract domain from path
     */
    private function extractDomain($path) {
        $parts = explode('/', trim($path, '/'));
        
        if (count($parts) > 0 && isset($this->config['domains'][$parts[0]])) {
            return $parts[0];
        }
        
        return 'unknown';
    }
    
    /**
     * Merge two manifests
     */
    public function merge($manifest1, $manifest2) {
        $strategy = $this->config['merging']['merge_strategy'];
        
        $merged = [
            'operation' => $manifest1['operation'] ?? 'merged',
            'archive' => [
                'name' => ($manifest1['archive']['name'] ?? '') . '_merged',
                'created' => date($this->config['format']['date_format']),
                'description' => 'Merged manifest',
                'total_files' => 0
            ],
            'files' => []
        ];
        
        $files1 = $manifest1['files'] ?? [];
        $files2 = $manifest2['files'] ?? [];
        
        if ($strategy === 'append') {
            $merged['files'] = array_merge($files1, $files2);
        } elseif ($strategy === 'replace') {
            $fileMap = [];
            foreach ($files1 as $file) {
                $fileMap[$file['filename']] = $file;
            }
            foreach ($files2 as $file) {
                $fileMap[$file['filename']] = $file;
            }
            $merged['files'] = array_values($fileMap);
        } elseif ($strategy === 'skip') {
            $fileMap = [];
            foreach ($files1 as $file) {
                $fileMap[$file['filename']] = $file;
            }
            foreach ($files2 as $file) {
                if (!isset($fileMap[$file['filename']])) {
                    $fileMap[$file['filename']] = $file;
                }
            }
            $merged['files'] = array_values($fileMap);
        }
        
        $merged['archive']['total_files'] = count($merged['files']);
        
        if ($this->config['merging']['combine_statistics']) {
            $merged['statistics'] = $this->generateStatistics($merged['files']);
        }
        
        return $merged;
    }
    
    /**
     * Compare two manifests
     */
    public function compare($manifest1, $manifest2) {
        $cfg = $this->config['comparison'];
        
        $files1 = $manifest1['files'] ?? [];
        $files2 = $manifest2['files'] ?? [];
        
        $map1 = [];
        $map2 = [];
        
        foreach ($files1 as $file) {
            $map1[$file['filename']] = $file;
        }
        foreach ($files2 as $file) {
            $map2[$file['filename']] = $file;
        }
        
        $comparison = [
            'only_in_first' => [],
            'only_in_second' => [],
            'in_both' => [],
            'modified' => []
        ];
        
        foreach ($map1 as $filename => $file) {
            if (!isset($map2[$filename])) {
                $comparison['only_in_first'][] = $filename;
            } else {
                $comparison['in_both'][] = $filename;
                
                if ($cfg['report_modified'] && $this->filesModified($file, $map2[$filename], $cfg)) {
                    $comparison['modified'][] = $filename;
                }
            }
        }
        
        foreach ($map2 as $filename => $file) {
            if (!isset($map1[$filename])) {
                $comparison['only_in_second'][] = $filename;
            }
        }
        
        return $comparison;
    }
    
    /**
     * Check if files are modified
     */
    private function filesModified($file1, $file2, $cfg) {
        if ($cfg['compare_checksums'] && 
            isset($file1['checksum']) && isset($file2['checksum']) &&
            $file1['checksum'] !== $file2['checksum']) {
            return true;
        }
        
        if ($cfg['compare_sizes'] &&
            isset($file1['size']) && isset($file2['size']) &&
            $file1['size'] !== $file2['size']) {
            return true;
        }
        
        return false;
    }
    
    /**
     * Convert array to YAML
     */
    public function arrayToYaml($data, $indent = 0) {
        $yaml = '';
        $indentStr = str_repeat(' ', $indent * $this->config['format']['yaml_indent']);
        
        foreach ($data as $key => $value) {
            if (is_array($value)) {
                $yaml .= $indentStr . $key . ":\n";
                $yaml .= $this->arrayToYaml($value, $indent + 1);
            } else {
                $yaml .= $indentStr . $key . ': ' . $this->formatValue($value) . "\n";
            }
        }
        
        return $yaml;
    }
    
    /**
     * Format value for YAML
     */
    private function formatValue($value) {
        if (is_string($value) && (strpos($value, ':') !== false || strpos($value, '#') !== false)) {
            return '"' . addslashes($value) . '"';
        }
        return $value;
    }
}
?>
