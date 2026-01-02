<?php
/**
 * file-extractor.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-27
 * Purpose: Archive extraction operations
 * Project: SIMA File Module
 * 
 * ADDED: Complete extraction functionality
 */

class FileExtractor {
    
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    /**
     * Extract archive to destination
     * 
     * @param string $archivePath Archive to extract
     * @param string $destination Destination directory
     * @param array $options Extraction options
     * @return array Result
     */
    public function extract($archivePath, $destination, $options = []) {
        $options = array_merge([
            'overwrite' => $this->config['overwrite_on_extract'],
            'create_dirs' => $this->config['create_directories'],
            'preserve_permissions' => $this->config['preserve_permissions'],
            'preserve_timestamps' => $this->config['preserve_timestamps'],
            'verify_integrity' => $this->config['verify_after_extract']
        ], $options);
        
        if (!file_exists($archivePath)) {
            return ['error' => 'Archive not found: ' . $archivePath];
        }
        
        // Create destination if needed
        if (!is_dir($destination)) {
            if ($options['create_dirs']) {
                if (!mkdir($destination, 0755, true)) {
                    return ['error' => 'Failed to create destination directory'];
                }
            } else {
                return ['error' => 'Destination directory does not exist'];
            }
        }
        
        // Extract based on format
        $extension = pathinfo($archivePath, PATHINFO_EXTENSION);
        
        if ($extension === 'zip') {
            return $this->extractZip($archivePath, $destination, $options);
        }
        
        return ['error' => 'Unsupported archive format: ' . $extension];
    }
    
    /**
     * Extract ZIP archive
     * 
     * @param string $archivePath Archive path
     * @param string $destination Destination directory
     * @param array $options Extraction options
     * @return array Result
     */
    private function extractZip($archivePath, $destination, $options) {
        $zip = new ZipArchive();
        
        if ($zip->open($archivePath) !== true) {
            return ['error' => 'Failed to open ZIP archive'];
        }
        
        $extracted = [];
        $skipped = [];
        $failed = [];
        
        for ($i = 0; $i < $zip->numFiles; $i++) {
            $filename = $zip->getNameIndex($i);
            $targetPath = $destination . DIRECTORY_SEPARATOR . $filename;
            
            // Skip directories
            if (substr($filename, -1) === '/') {
                if ($options['create_dirs'] && !is_dir($targetPath)) {
                    mkdir($targetPath, 0755, true);
                }
                continue;
            }
            
            // Check if file exists
            if (file_exists($targetPath) && !$options['overwrite']) {
                $skipped[] = $filename;
                continue;
            }
            
            // Create parent directory if needed
            $parentDir = dirname($targetPath);
            if (!is_dir($parentDir) && $options['create_dirs']) {
                mkdir($parentDir, 0755, true);
            }
            
            // Extract file
            $content = $zip->getFromIndex($i);
            if ($content === false) {
                $failed[] = ['file' => $filename, 'reason' => 'Failed to read from archive'];
                continue;
            }
            
            if (file_put_contents($targetPath, $content) === false) {
                $failed[] = ['file' => $filename, 'reason' => 'Failed to write file'];
                continue;
            }
            
            // Preserve timestamps
            if ($options['preserve_timestamps']) {
                $stat = $zip->statIndex($i);
                touch($targetPath, $stat['mtime']);
            }
            
            $extracted[] = $filename;
        }
        
        $zip->close();
        
        // Verify integrity if requested
        $verification = null;
        if ($options['verify_integrity']) {
            $verification = $this->verifyExtraction($archivePath, $destination, $extracted);
        }
        
        return [
            'success' => true,
            'extracted' => count($extracted),
            'skipped' => count($skipped),
            'failed' => count($failed),
            'files' => $extracted,
            'skipped_files' => $skipped,
            'failed_files' => $failed,
            'verification' => $verification
        ];
    }
    
    /**
     * Extract specific files from archive
     * 
     * @param string $archivePath Archive path
     * @param array $files Files to extract
     * @param string $destination Destination directory
     * @return array Result
     */
    public function extractSelected($archivePath, $files, $destination) {
        if (!file_exists($archivePath)) {
            return ['error' => 'Archive not found'];
        }
        
        $zip = new ZipArchive();
        
        if ($zip->open($archivePath) !== true) {
            return ['error' => 'Failed to open archive'];
        }
        
        $extracted = [];
        $failed = [];
        
        foreach ($files as $file) {
            $targetPath = $destination . DIRECTORY_SEPARATOR . basename($file);
            
            // Create parent directory if needed
            $parentDir = dirname($targetPath);
            if (!is_dir($parentDir)) {
                mkdir($parentDir, 0755, true);
            }
            
            // Extract file
            $content = $zip->getFromName($file);
            if ($content === false) {
                $failed[] = ['file' => $file, 'reason' => 'Not found in archive'];
                continue;
            }
            
            if (file_put_contents($targetPath, $content) === false) {
                $failed[] = ['file' => $file, 'reason' => 'Failed to write'];
                continue;
            }
            
            $extracted[] = $file;
        }
        
        $zip->close();
        
        return [
            'success' => true,
            'extracted' => count($extracted),
            'failed' => count($failed),
            'files' => $extracted,
            'failed_files' => $failed
        ];
    }
    
    /**
     * Preview archive contents without extracting
     * 
     * @param string $archivePath Archive path
     * @return array Archive structure
     */
    public function preview($archivePath) {
        if (!file_exists($archivePath)) {
            return ['error' => 'Archive not found'];
        }
        
        $zip = new ZipArchive();
        
        if ($zip->open($archivePath) !== true) {
            return ['error' => 'Failed to open archive'];
        }
        
        $structure = [
            'directories' => [],
            'files' => [],
            'total_size' => 0,
            'compressed_size' => 0
        ];
        
        for ($i = 0; $i < $zip->numFiles; $i++) {
            $stat = $zip->statIndex($i);
            $name = $stat['name'];
            
            if (substr($name, -1) === '/') {
                $structure['directories'][] = $name;
            } else {
                $structure['files'][] = [
                    'name' => $name,
                    'size' => $stat['size'],
                    'compressed_size' => $stat['comp_size'],
                    'modified' => date('Y-m-d H:i:s', $stat['mtime']),
                    'compression_ratio' => $stat['size'] > 0 ? 
                        round((1 - $stat['comp_size'] / $stat['size']) * 100, 2) : 0
                ];
                $structure['total_size'] += $stat['size'];
                $structure['compressed_size'] += $stat['comp_size'];
            }
        }
        
        $zip->close();
        
        $structure['file_count'] = count($structure['files']);
        $structure['directory_count'] = count($structure['directories']);
        $structure['total_compression_ratio'] = $structure['total_size'] > 0 ?
            round((1 - $structure['compressed_size'] / $structure['total_size']) * 100, 2) : 0;
        
        return [
            'success' => true,
            'structure' => $structure
        ];
    }
    
    /**
     * Verify extraction integrity
     * 
     * @param string $archivePath Original archive
     * @param string $destination Extraction destination
     * @param array $extractedFiles List of extracted files
     * @return array Verification results
     */
    private function verifyExtraction($archivePath, $destination, $extractedFiles) {
        $zip = new ZipArchive();
        
        if ($zip->open($archivePath) !== true) {
            return ['error' => 'Failed to reopen archive for verification'];
        }
        
        $verified = [];
        $corrupted = [];
        
        foreach ($extractedFiles as $file) {
            $targetPath = $destination . DIRECTORY_SEPARATOR . $file;
            
            if (!file_exists($targetPath)) {
                $corrupted[] = ['file' => $file, 'reason' => 'File not found after extraction'];
                continue;
            }
            
            // Get CRC from archive
            $index = $zip->locateName($file);
            if ($index === false) {
                $corrupted[] = ['file' => $file, 'reason' => 'Cannot locate in archive'];
                continue;
            }
            
            $stat = $zip->statIndex($index);
            $archiveCrc = $stat['crc'];
            
            // Calculate CRC of extracted file
            $extractedCrc = hash_file('crc32b', $targetPath);
            
            if (strtolower(dechex($archiveCrc)) === strtolower($extractedCrc)) {
                $verified[] = $file;
            } else {
                $corrupted[] = ['file' => $file, 'reason' => 'CRC mismatch'];
            }
        }
        
        $zip->close();
        
        return [
            'verified' => count($verified),
            'corrupted' => count($corrupted),
            'verified_files' => $verified,
            'corrupted_files' => $corrupted
        ];
    }
}
