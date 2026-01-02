<?php
/**
 * file-archiver.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-27
 * Purpose: Archive creation and management operations
 * Project: SIMA File Module
 * 
 * ADDED: Complete archiving functionality
 */

class FileArchiver {
    
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    /**
     * Create archive from files
     * 
     * @param array $files File paths to archive
     * @param string $archiveName Archive filename
     * @param array $options Archive options
     * @return array Result
     */
    public function create($files, $archiveName, $options = []) {
        $options = array_merge([
            'base_path' => $this->config['base_directory'],
            'preserve_structure' => $this->config['preserve_structure'],
            'compression_level' => $this->config['compression_level'],
            'include_manifest' => $this->config['auto_generate_manifest']
        ], $options);
        
        // Add timestamp if configured
        if ($this->config['timestamp_archives']) {
            $timestamp = date('Ymd_His');
            $archiveName = pathinfo($archiveName, PATHINFO_FILENAME) . '_' . $timestamp . '.zip';
        }
        
        $archivePath = $this->config['archive_directory'] . DIRECTORY_SEPARATOR . $archiveName;
        
        // Create archive based on format
        if ($this->config['archive_format'] === 'zip') {
            return $this->createZip($files, $archivePath, $options);
        }
        
        return ['error' => 'Unsupported archive format: ' . $this->config['archive_format']];
    }
    
    /**
     * Create ZIP archive
     * 
     * @param array $files Files to include
     * @param string $archivePath Archive destination
     * @param array $options Archive options
     * @return array Result
     */
    private function createZip($files, $archivePath, $options) {
        $zip = new ZipArchive();
        
        $result = $zip->open($archivePath, ZipArchive::CREATE | ZipArchive::OVERWRITE);
        if ($result !== true) {
            return ['error' => 'Failed to create ZIP archive: ' . $result];
        }
        
        // Set compression level
        $zip->setCompressionIndex(0, ZipArchive::CM_DEFLATE, $options['compression_level']);
        
        $added = [];
        $failed = [];
        $totalSize = 0;
        
        foreach ($files as $file) {
            if (!file_exists($file)) {
                $failed[] = ['file' => $file, 'reason' => 'File not found'];
                continue;
            }
            
            // Determine archive path
            $archiveName = $this->getArchiveName($file, $options['base_path'], $options['preserve_structure']);
            
            // Add file to archive
            if ($zip->addFile($file, $archiveName)) {
                $added[] = $archiveName;
                $totalSize += filesize($file);
                
                // Check size limit
                if ($this->config['max_archive_size'] > 0 && $totalSize > $this->config['max_archive_size']) {
                    if (!$this->config['split_archives']) {
                        $zip->close();
                        @unlink($archivePath);
                        return ['error' => 'Archive size limit exceeded'];
                    }
                    // TODO: Implement archive splitting
                }
            } else {
                $failed[] = ['file' => $file, 'reason' => 'Failed to add to archive'];
            }
        }
        
        // Add manifest if requested
        if ($options['include_manifest']) {
            $manifest = $this->generateManifestContent($files, $added);
            $zip->addFromString($this->config['manifest_filename'], $manifest);
        }
        
        $zip->close();
        
        return [
            'success' => true,
            'archive_path' => $archivePath,
            'archive_size' => filesize($archivePath),
            'files_added' => count($added),
            'files_failed' => count($failed),
            'added' => $added,
            'failed' => $failed
        ];
    }
    
    /**
     * Add files to existing archive
     * 
     * @param string $archivePath Existing archive
     * @param array $files Files to add
     * @return array Result
     */
    public function addFiles($archivePath, $files) {
        if (!file_exists($archivePath)) {
            return ['error' => 'Archive not found: ' . $archivePath];
        }
        
        $zip = new ZipArchive();
        
        if ($zip->open($archivePath) !== true) {
            return ['error' => 'Failed to open archive'];
        }
        
        $added = [];
        $failed = [];
        
        foreach ($files as $file) {
            if (!file_exists($file)) {
                $failed[] = ['file' => $file, 'reason' => 'File not found'];
                continue;
            }
            
            $archiveName = basename($file);
            
            if ($zip->addFile($file, $archiveName)) {
                $added[] = $archiveName;
            } else {
                $failed[] = ['file' => $file, 'reason' => 'Failed to add'];
            }
        }
        
        $zip->close();
        
        return [
            'success' => true,
            'files_added' => count($added),
            'files_failed' => count($failed),
            'added' => $added,
            'failed' => $failed
        ];
    }
    
    /**
     * List archive contents
     * 
     * @param string $archivePath Archive path
     * @return array Contents
     */
    public function listContents($archivePath) {
        if (!file_exists($archivePath)) {
            return ['error' => 'Archive not found'];
        }
        
        $zip = new ZipArchive();
        
        if ($zip->open($archivePath) !== true) {
            return ['error' => 'Failed to open archive'];
        }
        
        $contents = [];
        
        for ($i = 0; $i < $zip->numFiles; $i++) {
            $stat = $zip->statIndex($i);
            $contents[] = [
                'name' => $stat['name'],
                'size' => $stat['size'],
                'compressed_size' => $stat['comp_size'],
                'modified' => $stat['mtime'],
                'crc' => $stat['crc']
            ];
        }
        
        $zip->close();
        
        return [
            'success' => true,
            'total_files' => count($contents),
            'archive_size' => filesize($archivePath),
            'files' => $contents
        ];
    }
    
    /**
     * Get archive name for file
     * 
     * @param string $filePath Full file path
     * @param string $basePath Base path to remove
     * @param bool $preserveStructure Preserve directory structure
     * @return string Archive name
     */
    private function getArchiveName($filePath, $basePath, $preserveStructure) {
        if (!$preserveStructure) {
            return basename($filePath);
        }
        
        // Remove base path to preserve relative structure
        $relativePath = str_replace($basePath . DIRECTORY_SEPARATOR, '', $filePath);
        
        // Normalize path separators
        return str_replace(DIRECTORY_SEPARATOR, '/', $relativePath);
    }
    
    /**
     * Generate manifest content
     * 
     * @param array $sourceFiles Source file paths
     * @param array $addedFiles Files added to archive
     * @return string Manifest YAML content
     */
    private function generateManifestContent($sourceFiles, $addedFiles) {
        $manifest = [
            'archive' => [
                'created' => date('Y-m-d H:i:s'),
                'version' => '1.0.0',
                'format' => 'zip'
            ],
            'files' => [
                'total' => count($addedFiles),
                'list' => []
            ],
            'stats' => [
                'total_size' => 0
            ]
        ];
        
        foreach ($sourceFiles as $file) {
            if (file_exists($file)) {
                $size = filesize($file);
                $manifest['files']['list'][] = [
                    'path' => basename($file),
                    'size' => $size,
                    'checksum' => hash_file($this->config['checksum_algorithm'], $file)
                ];
                $manifest['stats']['total_size'] += $size;
            }
        }
        
        return $this->arrayToYaml($manifest);
    }
    
    /**
     * Convert array to YAML
     * 
     * @param array $data Data array
     * @param int $indent Current indent level
     * @return string YAML string
     */
    private function arrayToYaml($data, $indent = 0) {
        $yaml = '';
        $spaces = str_repeat('  ', $indent);
        
        foreach ($data as $key => $value) {
            if (is_array($value)) {
                $yaml .= $spaces . $key . ":\n";
                $yaml .= $this->arrayToYaml($value, $indent + 1);
            } else {
                $yaml .= $spaces . $key . ': ' . $value . "\n";
            }
        }
        
        return $yaml;
    }
}
