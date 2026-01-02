<?php
/**
 * file_module.php
 * 
 * Version: 1.0.0
 * Date: 2025-11-27
 * Purpose: Public API wrapper for SIMA file handling and archiving operations
 * Project: SIMA File Module
 * 
 * ADDED: Complete file handling and archiving module
 */

// Load configuration
require_once __DIR__ . '/file-config.php';

// Load core components
require_once __DIR__ . '/file-scanner.php';
require_once __DIR__ . '/file-archiver.php';
require_once __DIR__ . '/file-extractor.php';
require_once __DIR__ . '/file-validator.php';
require_once __DIR__ . '/file-metadata.php';
require_once __DIR__ . '/file-utils.php';

/**
 * SIMA File Module - Public API
 */
class SIMAFileModule {
    
    private $config;
    private $scanner;
    private $archiver;
    private $extractor;
    private $validator;
    private $metadata;
    
    /**
     * Constructor
     * 
     * @param array $config Optional configuration overrides
     */
    public function __construct($config = []) {
        $this->config = array_merge(FileConfig::getConfig(), $config);
        $this->scanner = new FileScanner($this->config);
        $this->archiver = new FileArchiver($this->config);
        $this->extractor = new FileExtractor($this->config);
        $this->validator = new FileValidator($this->config);
        $this->metadata = new FileMetadata($this->config);
    }
    
    // ========================================
    // SCANNING OPERATIONS
    // ========================================
    
    /**
     * Scan directory recursively
     * 
     * @param string $directory Directory path to scan
     * @param array $options Scan options
     * @return array Scan results
     */
    public function scanDirectory($directory, $options = []) {
        if (!$this->validator->isValidPath($directory)) {
            return ['error' => 'Invalid directory path'];
        }
        
        return $this->scanner->scan($directory, $options);
    }
    
    /**
     * Scan with file filtering
     * 
     * @param string $directory Directory path
     * @param array $filters Filter criteria
     * @return array Filtered results
     */
    public function scanWithFilter($directory, $filters = []) {
        if (!$this->validator->isValidPath($directory)) {
            return ['error' => 'Invalid directory path'];
        }
        
        return $this->scanner->scanFiltered($directory, $filters);
    }
    
    /**
     * Get directory statistics
     * 
     * @param string $directory Directory path
     * @return array Statistics
     */
    public function getDirectoryStats($directory) {
        if (!$this->validator->isValidPath($directory)) {
            return ['error' => 'Invalid directory path'];
        }
        
        return $this->scanner->getStats($directory);
    }
    
    // ========================================
    // ARCHIVE OPERATIONS
    // ========================================
    
    /**
     * Create ZIP archive from files
     * 
     * @param array $files Array of file paths
     * @param string $archiveName Archive filename
     * @param array $options Archive options
     * @return array Result with archive path or error
     */
    public function createArchive($files, $archiveName, $options = []) {
        if (!$this->validator->validateFileList($files)) {
            return ['error' => 'Invalid file list'];
        }
        
        return $this->archiver->create($files, $archiveName, $options);
    }
    
    /**
     * Add files to existing archive
     * 
     * @param string $archivePath Existing archive path
     * @param array $files Files to add
     * @return array Result
     */
    public function addToArchive($archivePath, $files) {
        if (!$this->validator->isValidArchive($archivePath)) {
            return ['error' => 'Invalid archive path'];
        }
        
        return $this->archiver->addFiles($archivePath, $files);
    }
    
    /**
     * List archive contents
     * 
     * @param string $archivePath Archive path
     * @return array Archive contents
     */
    public function listArchive($archivePath) {
        if (!$this->validator->isValidArchive($archivePath)) {
            return ['error' => 'Invalid archive path'];
        }
        
        return $this->archiver->listContents($archivePath);
    }
    
    // ========================================
    // EXTRACTION OPERATIONS
    // ========================================
    
    /**
     * Extract archive to directory
     * 
     * @param string $archivePath Archive to extract
     * @param string $destination Destination directory
     * @param array $options Extraction options
     * @return array Result
     */
    public function extractArchive($archivePath, $destination, $options = []) {
        if (!$this->validator->isValidArchive($archivePath)) {
            return ['error' => 'Invalid archive path'];
        }
        
        if (!$this->validator->isValidPath($destination)) {
            return ['error' => 'Invalid destination path'];
        }
        
        return $this->extractor->extract($archivePath, $destination, $options);
    }
    
    /**
     * Extract specific files from archive
     * 
     * @param string $archivePath Archive path
     * @param array $files Files to extract
     * @param string $destination Destination directory
     * @return array Result
     */
    public function extractFiles($archivePath, $files, $destination) {
        if (!$this->validator->isValidArchive($archivePath)) {
            return ['error' => 'Invalid archive path'];
        }
        
        return $this->extractor->extractSelected($archivePath, $files, $destination);
    }
    
    /**
     * Preview archive without extracting
     * 
     * @param string $archivePath Archive path
     * @return array Archive structure
     */
    public function previewArchive($archivePath) {
        if (!$this->validator->isValidArchive($archivePath)) {
            return ['error' => 'Invalid archive path'];
        }
        
        return $this->extractor->preview($archivePath);
    }
    
    // ========================================
    // METADATA OPERATIONS
    // ========================================
    
    /**
     * Extract metadata from file
     * 
     * @param string $filePath File path
     * @return array Metadata
     */
    public function getFileMetadata($filePath) {
        if (!$this->validator->isValidFile($filePath)) {
            return ['error' => 'Invalid file path'];
        }
        
        return $this->metadata->extract($filePath);
    }
    
    /**
     * Get checksums for files
     * 
     * @param array $files File paths
     * @param string $algorithm Hash algorithm
     * @return array Checksums
     */
    public function getChecksums($files, $algorithm = 'sha256') {
        if (!$this->validator->validateFileList($files)) {
            return ['error' => 'Invalid file list'];
        }
        
        return $this->metadata->calculateChecksums($files, $algorithm);
    }
    
    /**
     * Generate manifest for files
     * 
     * @param array $files File paths
     * @param array $options Manifest options
     * @return array Manifest data
     */
    public function generateManifest($files, $options = []) {
        if (!$this->validator->validateFileList($files)) {
            return ['error' => 'Invalid file list'];
        }
        
        return $this->metadata->createManifest($files, $options);
    }
    
    // ========================================
    // FILE OPERATIONS
    // ========================================
    
    /**
     * Copy files to destination
     * 
     * @param array $files Source files
     * @param string $destination Destination directory
     * @param array $options Copy options
     * @return array Result
     */
    public function copyFiles($files, $destination, $options = []) {
        if (!$this->validator->validateFileList($files)) {
            return ['error' => 'Invalid file list'];
        }
        
        if (!$this->validator->isValidPath($destination)) {
            return ['error' => 'Invalid destination path'];
        }
        
        return FileUtils::copyFiles($files, $destination, $options);
    }
    
    /**
     * Move files to destination
     * 
     * @param array $files Source files
     * @param string $destination Destination directory
     * @param array $options Move options
     * @return array Result
     */
    public function moveFiles($files, $destination, $options = []) {
        if (!$this->validator->validateFileList($files)) {
            return ['error' => 'Invalid file list'];
        }
        
        if (!$this->validator->isValidPath($destination)) {
            return ['error' => 'Invalid destination path'];
        }
        
        return FileUtils::moveFiles($files, $destination, $options);
    }
    
    /**
     * Delete files
     * 
     * @param array $files Files to delete
     * @param array $options Delete options
     * @return array Result
     */
    public function deleteFiles($files, $options = []) {
        if (!$this->validator->validateFileList($files)) {
            return ['error' => 'Invalid file list'];
        }
        
        return FileUtils::deleteFiles($files, $options);
    }
    
    // ========================================
    // VALIDATION OPERATIONS
    // ========================================
    
    /**
     * Validate file integrity
     * 
     * @param string $filePath File path
     * @param string $expectedChecksum Expected checksum
     * @return bool Valid or not
     */
    public function validateIntegrity($filePath, $expectedChecksum) {
        return $this->validator->checkIntegrity($filePath, $expectedChecksum);
    }
    
    /**
     * Verify archive integrity
     * 
     * @param string $archivePath Archive path
     * @return array Validation result
     */
    public function verifyArchive($archivePath) {
        if (!$this->validator->isValidArchive($archivePath)) {
            return ['error' => 'Invalid archive path'];
        }
        
        return $this->validator->verifyArchive($archivePath);
    }
}
