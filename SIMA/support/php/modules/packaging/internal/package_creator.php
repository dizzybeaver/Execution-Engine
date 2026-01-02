<?php
/**
 * package_creator.php
 * 
 * Package Creation Component
 * Version: 1.0.0
 * Date: 2025-11-27
 * 
 * Internal component - use PackagingModule API
 */

class PackageCreator {
    private $config;
    
    public function __construct($config) {
        $this->config = $config;
    }
    
    public function updateConfig($config) {
        $this->config = $config;
    }
    
    /**
     * Create package
     */
    public function create($files, $packageName, $options = []) {
        // Merge options with defaults
        $options = array_merge($this->getDefaultOptions(), $options);
        
        // Create temp directory
        $tempDir = $this->createTempDirectory($packageName);
        
        // Organize files
        require_once __DIR__ . '/package_organizer.php';
        $organizer = new PackageOrganizer($this->config);
        $organized = $organizer->organize($files, $options['structure']);
        
        // Copy files to temp directory
        foreach ($organized as $targetPath => $sourceFile) {
            $this->copyFileToPackage($sourceFile, $tempDir . '/' . $targetPath);
        }
        
        // Add manifest if requested
        if ($options['include_manifest']) {
            $this->addManifest($tempDir, $options['manifest_content'] ?? null);
        }
        
        // Add instructions if requested
        if ($options['include_instructions']) {
            $this->addInstructions($tempDir, $options['instructions_content'] ?? null);
        }
        
        // Add documentation
        if ($options['include_readme']) {
            $this->addReadme($tempDir, $options);
        }
        
        // Finalize package
        return $this->finalize($tempDir);
    }
    
    /**
     * Get default options
     */
    private function getDefaultOptions() {
        return [
            'structure' => $this->config['default_structure'],
            'include_manifest' => $this->config['manifest']['include_by_default'],
            'include_instructions' => $this->config['instructions']['include_by_default'],
            'include_readme' => $this->config['documentation']['include_readme'],
            'type' => 'export'
        ];
    }
    
    /**
     * Create temp directory
     */
    private function createTempDirectory($packageName) {
        $tempBase = $this->config['temp_directory'];
        
        if (!is_dir($tempBase)) {
            mkdir($tempBase, 0755, true);
        }
        
        $tempDir = $tempBase . '/' . $packageName . '_' . uniqid();
        mkdir($tempDir, 0755, true);
        
        return $tempDir;
    }
    
    /**
     * Copy file to package
     */
    private function copyFileToPackage($sourceFile, $targetPath) {
        $sourcePath = is_array($sourceFile) ? ($sourceFile['path'] ?? '') : $sourceFile;
        
        if (!file_exists($sourcePath)) {
            return false;
        }
        
        // Create target directory
        $targetDir = dirname($targetPath);
        if (!is_dir($targetDir)) {
            mkdir($targetDir, 0755, true);
        }
        
        // Copy file
        if (isset($sourceFile['content'])) {
            file_put_contents($targetPath, $sourceFile['content']);
        } else {
            copy($sourcePath, $targetPath);
        }
        
        // Preserve timestamps if configured
        if ($this->config['format']['preserve_timestamps']) {
            touch($targetPath, filemtime($sourcePath));
        }
        
        return true;
    }
    
    /**
     * Create with manifest
     */
    public function createWithManifest($files, $packageName, $manifestContent, $options = []) {
        $options['manifest_content'] = $manifestContent;
        $options['include_manifest'] = true;
        
        return $this->create($files, $packageName, $options);
    }
    
    /**
     * Create with documentation
     */
    public function createWithDocumentation($files, $packageName, $documentation, $options = []) {
        $options['documentation'] = $documentation;
        
        return $this->create($files, $packageName, $options);
    }
    
    /**
     * Create complete package
     */
    public function createComplete($files, $packageName, $manifestContent, $instructionsContent, $options = []) {
        $options['manifest_content'] = $manifestContent;
        $options['instructions_content'] = $instructionsContent;
        $options['include_manifest'] = true;
        $options['include_instructions'] = true;
        
        return $this->create($files, $packageName, $options);
    }
    
    /**
     * Add manifest
     */
    public function addManifest($packagePath, $manifestContent = null) {
        $filename = $this->config['manifest']['filename'];
        $location = $this->config['manifest']['location'];
        
        $targetPath = $this->getDocumentPath($packagePath, $location, $filename);
        
        if ($manifestContent) {
            file_put_contents($targetPath, $manifestContent);
        } elseif ($this->config['manifest']['auto_generate']) {
            // Generate basic manifest
            $manifest = $this->generateBasicManifest($packagePath);
            file_put_contents($targetPath, $manifest);
        }
        
        return ['success' => true, 'path' => $targetPath];
    }
    
    /**
     * Add instructions
     */
    public function addInstructions($packagePath, $instructionsContent = null) {
        $filename = $this->config['instructions']['filename'];
        $location = $this->config['instructions']['location'];
        
        $targetPath = $this->getDocumentPath($packagePath, $location, $filename);
        
        if ($instructionsContent) {
            file_put_contents($targetPath, $instructionsContent);
        } elseif ($this->config['instructions']['auto_generate']) {
            // Generate basic instructions
            $instructions = $this->generateBasicInstructions($packagePath);
            file_put_contents($targetPath, $instructions);
        }
        
        return ['success' => true, 'path' => $targetPath];
    }
    
    /**
     * Add README
     */
    private function addReadme($packagePath, $options) {
        $filename = $this->config['documentation']['readme_filename'];
        $readme = "# " . basename($packagePath) . "\n\n";
        $readme .= "Package created: " . date('Y-m-d H:i:s') . "\n\n";
        
        if (isset($options['description'])) {
            $readme .= "## Description\n\n" . $options['description'] . "\n\n";
        }
        
        file_put_contents($packagePath . '/' . $filename, $readme);
    }
    
    /**
     * Get document path
     */
    private function getDocumentPath($packagePath, $location, $filename) {
        switch ($location) {
            case 'meta':
                $dir = $packagePath . '/meta';
                break;
            case 'docs':
                $dir = $packagePath . '/docs';
                break;
            default:
                $dir = $packagePath;
        }
        
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        
        return $dir . '/' . $filename;
    }
    
    /**
     * Generate basic manifest
     */
    private function generateBasicManifest($packagePath) {
        $files = $this->scanPackageFiles($packagePath);
        
        $manifest = "operation: package\n";
        $manifest .= "archive:\n";
        $manifest .= "  name: " . basename($packagePath) . "\n";
        $manifest .= "  created: " . date('Y-m-d H:i:s') . "\n";
        $manifest .= "  total_files: " . count($files) . "\n";
        $manifest .= "files:\n";
        
        foreach ($files as $file) {
            $manifest .= "  - filename: " . basename($file) . "\n";
            $manifest .= "    path: " . $file . "\n";
        }
        
        return $manifest;
    }
    
    /**
     * Generate basic instructions
     */
    private function generateBasicInstructions($packagePath) {
        $instructions = "# Import Instructions\n\n";
        $instructions .= "## Overview\n\n";
        $instructions .= "Package: " . basename($packagePath) . "\n\n";
        $instructions .= "## Installation\n\n";
        $instructions .= "1. Extract archive\n";
        $instructions .= "2. Review contents\n";
        $instructions .= "3. Copy files to target location\n";
        
        return $instructions;
    }
    
    /**
     * Scan package files
     */
    private function scanPackageFiles($packagePath) {
        $files = [];
        $iterator = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($packagePath)
        );
        
        foreach ($iterator as $file) {
            if ($file->isFile()) {
                $files[] = str_replace($packagePath . '/', '', $file->getPathname());
            }
        }
        
        return $files;
    }
    
    /**
     * Finalize package
     */
    public function finalize($packagePath) {
        $packageName = basename($packagePath);
        $outputDir = $this->config['output_directory'];
        
        if (!is_dir($outputDir)) {
            mkdir($outputDir, 0755, true);
        }
        
        // Generate final name
        $finalName = $this->generatePackageName($packageName);
        $archivePath = $outputDir . '/' . $finalName;
        
        // Create archive
        $this->createArchive($packagePath, $archivePath);
        
        // Cleanup temp directory if configured
        if ($this->config['temp']['cleanup_on_success']) {
            $this->removeDirectory($packagePath);
        }
        
        return [
            'success' => true,
            'archive_path' => $archivePath,
            'archive_name' => $finalName,
            'size' => filesize($archivePath)
        ];
    }
    
    /**
     * Generate package name
     */
    private function generatePackageName($baseName) {
        $cfg = $this->config['naming'];
        $ext = $this->config['format']['type'];
        
        $parts = [
            'prefix' => $cfg['prefix'],
            'name' => $baseName,
            'date' => $cfg['include_date'] ? date($cfg['date_format']) : null,
            'ext' => $ext
        ];
        
        $parts = array_filter($parts);
        
        $name = implode($cfg['separator'], array_slice($parts, 0, -1)) . '.' . $parts['ext'];
        
        return $cfg['lowercase'] ? strtolower($name) : $name;
    }
    
    /**
     * Create archive
     */
    private function createArchive($sourceDir, $archivePath) {
        $zip = new ZipArchive();
        
        if ($zip->open($archivePath, ZipArchive::CREATE | ZipArchive::OVERWRITE) !== true) {
            throw new Exception("Cannot create archive: {$archivePath}");
        }
        
        $files = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($sourceDir),
            RecursiveIteratorIterator::LEAVES_ONLY
        );
        
        foreach ($files as $file) {
            if (!$file->isDir()) {
                $filePath = $file->getRealPath();
                $relativePath = substr($filePath, strlen($sourceDir) + 1);
                
                $zip->addFile($filePath, $relativePath);
            }
        }
        
        $zip->close();
    }
    
    /**
     * Remove directory recursively
     */
    private function removeDirectory($dir) {
        if (!is_dir($dir)) {
            return;
        }
        
        $files = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($dir, RecursiveDirectoryIterator::SKIP_DOTS),
            RecursiveIteratorIterator::CHILD_FIRST
        );
        
        foreach ($files as $file) {
            if ($file->isDir()) {
                rmdir($file->getRealPath());
            } else {
                unlink($file->getRealPath());
            }
        }
        
        rmdir($dir);
    }
    
    /**
     * Add files to existing package
     */
    public function addFiles($packagePath, $files) {
        foreach ($files as $file) {
            $sourcePath = is_array($file) ? ($file['path'] ?? '') : $file;
            $targetPath = $packagePath . '/' . basename($sourcePath);
            
            $this->copyFileToPackage($file, $targetPath);
        }
        
        return ['success' => true];
    }
    
    /**
     * Get package info
     */
    public function getPackageInfo($packagePath) {
        if (!file_exists($packagePath)) {
            return ['error' => 'Package does not exist'];
        }
        
        return [
            'name' => basename($packagePath),
            'size' => filesize($packagePath),
            'created' => filectime($packagePath),
            'modified' => filemtime($packagePath)
        ];
    }
    
    /**
     * Validate package
     */
    public function validatePackage($packagePath) {
        $errors = [];
        
        if (!file_exists($packagePath)) {
            $errors[] = 'Package does not exist';
        }
        
        return [
            'valid' => empty($errors),
            'errors' => $errors
        ];
    }
}
?>
