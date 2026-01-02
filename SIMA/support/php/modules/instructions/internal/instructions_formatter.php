<?php
/**
 * instructions_formatter.php
 * 
 * Instructions Formatting Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use InstructionsModule API
 */

class InstructionsFormatter {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Format section
     */
    public function formatSection($title, $content) {
        $heading = $this->config['format']['heading_style'];
        return "{$heading}{$heading} " . strtoupper($title) . "\n\n{$content}\n\n";
    }
    
    /**
     * Format file list
     */
    public function formatFileList($files, $groupBy = 'directory') {
        $cfg = $this->config['file_list'];
        
        // Group files
        $grouped = $this->groupFiles($files, $groupBy);
        
        $md = '';
        
        foreach ($grouped as $group => $groupFiles) {
            $md .= "**{$group}** (" . count($groupFiles) . " files)\n";
            
            foreach ($groupFiles as $file) {
                $indent = $cfg['indent_grouped'] ? str_repeat(' ', $cfg['indent_size']) : '';
                
                $line = $indent . '- ';
                
                $filename = $file['filename'] ?? basename($file['path'] ?? '');
                $line .= $filename;
                
                if ($cfg['show_ref_ids'] && !empty($file['ref_id'])) {
                    $line .= ' (`' . $file['ref_id'] . '`)';
                }
                
                if ($cfg['show_sizes'] && isset($file['size'])) {
                    $line .= ' - ' . $this->formatSize($file['size']);
                }
                
                if ($cfg['show_paths'] && isset($file['path'])) {
                    $line .= "\n{$indent}  Path: `" . $file['path'] . '`';
                }
                
                $md .= $line . "\n";
            }
            
            $md .= "\n";
        }
        
        return $md;
    }
    
    /**
     * Group files by criteria
     */
    private function groupFiles($files, $groupBy) {
        $grouped = [];
        
        foreach ($files as $file) {
            $key = $this->getGroupKey($file, $groupBy);
            
            if (!isset($grouped[$key])) {
                $grouped[$key] = [];
            }
            
            $grouped[$key][] = $file;
        }
        
        ksort($grouped);
        
        return $grouped;
    }
    
    /**
     * Get group key for file
     */
    private function getGroupKey($file, $groupBy) {
        switch ($groupBy) {
            case 'directory':
                $path = $file['path'] ?? $file['relative_path'] ?? '';
                return dirname($path);
                
            case 'category':
                return $file['category'] ?? 'unknown';
                
            case 'domain':
                $path = $file['path'] ?? $file['relative_path'] ?? '';
                $parts = explode('/', trim($path, '/'));
                if (count($parts) > 0 && isset($this->config['domains'][$parts[0]])) {
                    return $this->config['domains'][$parts[0]];
                }
                return 'Unknown';
                
            case 'extension':
                $filename = $file['filename'] ?? basename($file['path'] ?? '');
                $ext = pathinfo($filename, PATHINFO_EXTENSION);
                return $ext ? '.' . $ext : 'no extension';
                
            default:
                return 'ungrouped';
        }
    }
    
    /**
     * Format checklist
     */
    public function formatChecklist($items, $checked = false) {
        $cfg = $this->config['checklist'];
        $marker = $checked ? $cfg['checked_marker'] : $cfg['unchecked_marker'];
        
        $md = '';
        
        foreach ($items as $item) {
            if (is_array($item)) {
                // Nested checklist
                $md .= "- {$marker} " . $item['text'] . "\n";
                
                if (isset($item['children'])) {
                    foreach ($item['children'] as $child) {
                        $indent = str_repeat(' ', 2);
                        $md .= "{$indent}- {$marker} {$child}\n";
                    }
                }
            } else {
                $md .= "- {$marker} {$item}\n";
            }
            
            if ($cfg['add_spacing']) {
                $md .= "\n";
            }
        }
        
        return rtrim($md) . "\n";
    }
    
    /**
     * Format file tree
     */
    public function formatFileTree($files) {
        $tree = $this->buildTree($files);
        return $this->renderTree($tree);
    }
    
    /**
     * Build tree structure
     */
    private function buildTree($files) {
        $tree = [];
        
        foreach ($files as $file) {
            $path = $file['path'] ?? $file['relative_path'] ?? '';
            $parts = explode('/', trim($path, '/'));
            
            $current = &$tree;
            
            foreach ($parts as $i => $part) {
                if (!isset($current[$part])) {
                    $current[$part] = [];
                }
                
                if ($i === count($parts) - 1) {
                    $current[$part]['_file'] = $file;
                }
                
                $current = &$current[$part];
            }
        }
        
        return $tree;
    }
    
    /**
     * Render tree structure
     */
    private function renderTree($tree, $prefix = '', $isLast = true) {
        $md = '';
        $cfg = $this->config['tree'];
        $entries = array_keys($tree);
        $count = count($entries);
        
        foreach ($entries as $i => $name) {
            if ($name === '_file') {
                continue;
            }
            
            $isLastEntry = ($i === $count - 1) || ($i === $count - 2 && isset($entries[$count - 1]) && $entries[$count - 1] === '_file');
            
            $branch = $isLastEntry ? $cfg['branch_chars'][1] : $cfg['branch_chars'][0];
            $icon = isset($tree[$name]['_file']) ? $cfg['file_icon'] : $cfg['directory_icon'];
            
            $md .= $prefix . $branch . ' ' . $icon . ' ' . $name;
            
            if (!isset($tree[$name]['_file']) && $cfg['show_file_count']) {
                $fileCount = $this->countFiles($tree[$name]);
                if ($fileCount > 0) {
                    $md .= " ({$fileCount})";
                }
            }
            
            $md .= "\n";
            
            if (!isset($tree[$name]['_file'])) {
                $newPrefix = $prefix . ($isLastEntry ? $cfg['branch_chars'][3] : $cfg['branch_chars'][2]);
                $md .= $this->renderTree($tree[$name], $newPrefix, $isLastEntry);
            }
        }
        
        return $md;
    }
    
    /**
     * Count files in tree
     */
    private function countFiles($tree) {
        $count = 0;
        
        foreach ($tree as $key => $value) {
            if ($key === '_file') {
                $count++;
            } elseif (is_array($value)) {
                $count += $this->countFiles($value);
            }
        }
        
        return $count;
    }
    
    /**
     * Format table
     */
    public function formatTable($headers, $rows) {
        $cfg = $this->config['table'];
        
        // Calculate column widths
        $widths = [];
        foreach ($headers as $i => $header) {
            $widths[$i] = max(strlen($header), $cfg['min_column_width']);
        }
        
        foreach ($rows as $row) {
            foreach ($row as $i => $cell) {
                if (isset($widths[$i])) {
                    $widths[$i] = max($widths[$i], strlen($cell));
                }
            }
        }
        
        $md = '';
        
        // Header row
        $md .= '| ';
        foreach ($headers as $i => $header) {
            $md .= str_pad($header, $widths[$i]) . ' | ';
        }
        $md .= "\n";
        
        // Separator
        $md .= '|';
        foreach ($widths as $width) {
            $md .= str_repeat('-', $width + 2) . '|';
        }
        $md .= "\n";
        
        // Data rows
        foreach ($rows as $row) {
            $md .= '| ';
            foreach ($row as $i => $cell) {
                $md .= str_pad($cell, $widths[$i]) . ' | ';
            }
            $md .= "\n";
        }
        
        return $md;
    }
    
    /**
     * Format size
     */
    private function formatSize($bytes) {
        $units = ['B', 'KB', 'MB', 'GB'];
        $i = 0;
        
        while ($bytes >= 1024 && $i < count($units) - 1) {
            $bytes /= 1024;
            $i++;
        }
        
        return round($bytes, 2) . ' ' . $units[$i];
    }
    
    /**
     * Format warning
     */
    public function formatWarning($message) {
        if (!$this->config['warnings']['enabled']) {
            return '';
        }
        
        return sprintf(
            $this->config['warnings']['format'],
            $this->config['warnings']['marker'],
            $message
        );
    }
    
    /**
     * Format note
     */
    public function formatNote($message) {
        if (!$this->config['notes']['enabled']) {
            return '';
        }
        
        return sprintf(
            $this->config['notes']['format'],
            $this->config['notes']['marker'],
            $message
        );
    }
    
    /**
     * Format code block
     */
    public function formatCodeBlock($code, $language = null) {
        $lang = $language ?? $this->config['code_blocks']['default_language'];
        
        if ($this->config['code_blocks']['include_language']) {
            return "```{$lang}\n{$code}\n```\n";
        }
        
        return "```\n{$code}\n```\n";
    }
    
    /**
     * Format link
     */
    public function formatLink($text, $url) {
        return sprintf($this->config['links']['format'], $text, $url);
    }
}
?>
