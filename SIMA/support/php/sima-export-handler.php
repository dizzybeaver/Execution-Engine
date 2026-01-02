<?php
/**
 * sima-export-handler.php
 * 
 * Main request handler for SIMA Export Tool
 * Version: 4.4.2
 * Date: 2025-11-23
 * FIXED: Only scans within allowed base directory, no open_basedir violations
 */

class SIMAExportHandler {
    private $baseSearchDir;
    private $autoDetectedRoot;
    private $assetPaths;

    public function __construct($baseSearchDir = '/home/joe/web/claude.dizzybeaver.com/public_html') {
        $this->baseSearchDir = $baseSearchDir;
        $this->autoDetectedRoot = $this->findSIMARoot();
        $this->assetPaths = $this->getAssetPaths();
    }

    /**
     * Auto-detect SIMA root within base search directory ONLY
     */
    private function findSIMARoot() {
        // Only check directories within the allowed base directory
        $possibleDirs = [
            $this->baseSearchDir . '/sima',
            $this->baseSearchDir . '/simav4',
            $this->baseSearchDir . '/simav4.2',
            $this->baseSearchDir . '/simav4.1',
            $this->baseSearchDir . '/simav3',
            $this->baseSearchDir // The base directory itself
        ];

        foreach ($possibleDirs as $dir) {
            // Only check if directory exists within our allowed path
            if (is_dir($dir)) {
                // Check for SIMA v4.2+ structure
                if (is_dir($dir . '/generic') && is_dir($dir . '/platforms')) {
                    return $dir;
                }
                // Check for SIMA v4.1 structure
                if (is_dir($dir . '/entries') && is_dir($dir . '/integration')) {
                    return $dir;
                }
                // Check for SIMA v3 structure
                if (is_dir($dir . '/NM00') && is_dir($dir . '/NM01')) {
                    return $dir;
                }
                // Check if this is already a SIMA knowledge directory
                if ($this->isSIMAKnowledgeDir($dir)) {
                    return $dir;
                }
            }
        }

        return null;
    }

    /**
     * Check if directory contains SIMA knowledge files
     */
    private function isSIMAKnowledgeDir($dir) {
        // Look for common SIMA file patterns
        $simaPatterns = [
            '/*.md',
            '/generic/*.md',
            '/platforms/*.md',
            '/entries/*.md',
            '/integration/*.md',
            '/NM00/*.md',
            '/NM01/*.md'
        ];
        
        foreach ($simaPatterns as $pattern) {
            $files = glob($dir . $pattern);
            if (!empty($files)) {
                return true;
            }
        }
        
        return false;
    }

    /**
     * Get asset paths for CSS and JS
     */
    private function getAssetPaths() {
        $scriptDir = dirname($_SERVER['SCRIPT_NAME']);
        
        if (strpos($scriptDir, '/support/php') !== false) {
            return [
                'css' => $scriptDir . '/css/',
                'js' => $scriptDir . '/js/'
            ];
        }
        
        return [
            'css' => '/css/',
            'js' => '/js/'
        ];
    }

    /**
     * Handle AJAX requests
     */
    public function handleRequest() {
        // Ensure clean output for JSON
        while (ob_get_level()) ob_end_clean();
        
        header('Content-Type: application/json');
        header('Cache-Control: no-cache, no-store, must-revalidate');
        
        try {
            $action = $_POST['action'] ?? '';
            
            if ($action === 'scan') {
                $this->handleScanAction();
            } elseif ($action === 'export') {
                $this->handleExportAction();
            } else {
                $this->sendJsonResponse(false, [], "Unknown action: {$action}");
            }
            
        } catch (Exception $e) {
            $this->sendJsonResponse(false, [], $e->getMessage());
        }
    }

    /**
     * Handle scan action - validates directory is within allowed path
     */
    private function handleScanAction() {
        $directory = $_POST['directory'] ?? '';
        
        if (empty($directory)) {
            throw new Exception("Please enter a SIMA directory path");
        }
        
        $directory = rtrim($directory, '/');
        
        // SECURITY: Ensure directory is within our allowed base path
        if (!$this->isPathWithinBase($directory)) {
            throw new Exception("Directory must be within: {$this->baseSearchDir}");
        }
        
        if (!is_dir($directory)) {
            throw new Exception("Directory not found: {$directory}");
        }
        if (!is_readable($directory)) {
            throw new Exception("Directory not readable: {$directory}");
        }
        
        $validatedDir = realpath($directory);
        
        // Double-check security
        if (!$this->isPathWithinBase($validatedDir)) {
            throw new Exception("Security violation: Directory outside allowed path");
        }
        
        // Load required files
        $this->loadRequiredFiles($validatedDir);
        
        // Get version info and scan
        $versionInfo = SIMAVersionUtils::getVersionInfo($validatedDir);
        $tree = SIMAVersionUtils::scanWithVersion($validatedDir, $versionInfo['version']);
        $stats = SIMAVersionUtils::getStats($validatedDir, $versionInfo['version']);
        
        $this->sendJsonResponse(true, [
            'tree' => $tree,
            'base_path' => $validatedDir,
            'version_info' => $versionInfo,
            'stats' => $stats
        ]);
    }

    /**
     * Handle export action - validates directory is within allowed path
     */
    private function handleExportAction() {
        $baseDir = $_POST['base_directory'] ?? '';
        
        if (empty($baseDir)) {
            throw new Exception("Invalid base directory");
        }
        
        // SECURITY: Ensure directory is within our allowed base path
        if (!$this->isPathWithinBase($baseDir)) {
            throw new Exception("Security violation: Directory outside allowed path");
        }
        
        $validatedBase = realpath($baseDir);
        
        // Double-check security
        if (!$this->isPathWithinBase($validatedBase)) {
            throw new Exception("Security violation: Directory outside allowed path");
        }
        
        // Load required files
        $this->loadRequiredFiles($validatedBase);
        
        $archiveName = $_POST['archive_name'] ?? 'SIMA-Export';
        $description = $_POST['description'] ?? '';
        $selectedPaths = json_decode($_POST['selected_files'] ?? '[]', true);
        
        $sourceVersion = $_POST['source_version'] ?? 'auto';
        $targetVersion = $_POST['target_version'] ?? 'auto';
        
        // Auto-detect versions if needed
        if ($sourceVersion === 'auto') {
            $versionInfo = SIMAVersionUtils::getVersionInfo($validatedBase);
            $sourceVersion = $versionInfo['version'];
        }
        
        if ($targetVersion === 'auto') {
            $targetVersion = $sourceVersion;
        }
        
        if (empty($selectedPaths)) {
            throw new Exception("No files selected for export");
        }
        
        // Create export
        $result = createExportArchive($validatedBase, $archiveName, $description, $selectedPaths, $sourceVersion, $targetVersion);
        
        $this->sendJsonResponse(true, [
            'archive_name' => $result['archive_name'],
            'file_count' => $result['file_count'],
            'converted_count' => $result['converted_count'],
            'download_url' => $result['download_url']
        ]);
    }

    /**
     * Security: Check if path is within our allowed base directory
     */
    private function isPathWithinBase($path) {
        $base = realpath($this->baseSearchDir);
        $checkPath = realpath($path);
        
        if ($base === false || $checkPath === false) {
            return false;
        }
        
        // Check if the path starts with our base directory
        return strpos($checkPath, $base) === 0;
    }

    /**
     * Load required PHP files
     */
    private function loadRequiredFiles($simaRoot = null) {
        $required = [
            'sima-common.php',
            'sima-scanner.php',
            'sima-tree-formatter.php',
            'sima-version-utils.php',
            'sima-export-helpers.php'
        ];
        
        $phpDir = __DIR__;
        $missing = [];
        
        foreach ($required as $file) {
            $filepath = $phpDir . '/' . $file;
            if (!file_exists($filepath)) {
                $missing[] = $file;
                error_log("SIMA Export: Missing file: $filepath");
            } else {
                require_once $filepath;
            }
        }
        
        if (!empty($missing)) {
            throw new Exception("Missing required files: " . implode(', ', $missing));
        }
        
        return true;
    }

    /**
     * Send JSON response
     */
    private function sendJsonResponse($success, $data = [], $error = null) {
        // Final cleanup before JSON output
        while (ob_get_level()) ob_end_clean();
        
        $response = ['success' => $success];
        if ($success) {
            $response = array_merge($response, $data);
        } else {
            $response['error'] = $error;
        }
        
        echo json_encode($response);
        exit;
    }

    /**
     * Show HTML interface
     */
    public function showInterface() {
        // Clean output buffer for HTML
        while (ob_get_level()) ob_end_clean();
        
        $defaultPath = $this->autoDetectedRoot ?? $this->baseSearchDir;
        $autoDetectMsg = $this->autoDetectedRoot 
            ? "✓ Auto-detected: {$this->autoDetectedRoot}" 
            : "⚠ Could not auto-detect SIMA location - using base directory";
        $autoDetectClass = $this->autoDetectedRoot ? 'success-msg' : 'warning-msg';
        ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIMA Export Tool</title>
    <link rel="stylesheet" href="<?= $this->assetPaths['css'] ?>sima-export-tool.css">
</head>
<body>
    <div class="container">
        <h1>🔍 SIMA Knowledge Export Tool</h1>
        
        <div class="<?= $autoDetectClass ?>">
            <?= htmlspecialchars($autoDetectMsg) ?>
        </div>
        
        <div class="info-msg">
            <strong>Base Directory:</strong> <?= htmlspecialchars($this->baseSearchDir) ?>
        </div>
        
        <div id="error" class="error">
            <strong>Error:</strong> <span id="error-text"></span>
        </div>
        
        <div id="loading">⏳ Processing...</div>
        
        <div class="section">
            <h2>1. SIMA Directory</h2>
            <div class="form-group">
                <label for="simaDirectory">SIMA Root Path:</label>
                <input type="text" id="simaDirectory" value="<?= htmlspecialchars($defaultPath) ?>" placeholder="<?= htmlspecialchars($this->baseSearchDir) ?>">
                <small>Enter path within: <?= htmlspecialchars($this->baseSearchDir) ?></small>
            </div>
            <div class="form-group">
                <label for="sourceVersion">Source Version:</label>
                <select id="sourceVersion">
                    <option value="auto">Auto-Detect</option>
                    <option value="4.2">SIMA v4.2</option>
                    <option value="4.1">SIMA v4.1</option>
                    <option value="3.0">SIMA v3.0</option>
                </select>
            </div>
            <button id="scan-btn" onclick="scanDirectory()">🔍 Scan Directory</button>
            <div id="detectedVersion" style="display:none; margin-top:10px;" class="success-msg"></div>
        </div>
        
        <div class="section hidden" id="tree-section">
            <h2>2. Select Files to Export</h2>
            <div class="tree-controls">
                <button onclick="expandAll()">➕ Expand All</button>
                <button onclick="collapseAll()">➖ Collapse All</button>
                <button onclick="selectAll()">☑️ Select All</button>
                <button onclick="clearSelection()">⬜ Clear All</button>
            </div>
            <div class="tree-container" id="tree"></div>
            <div class="selection-summary" id="summary">Selection: 0 files selected</div>
        </div>
        
        <div class="section hidden" id="export-section">
            <h2>3. Export Settings</h2>
            <div class="form-group">
                <label for="archiveName">Archive Name:</label>
                <input type="text" id="archiveName" value="SIMA-Export" placeholder="MyExport">
            </div>
            <div class="form-group">
                <label for="description">Description:</label>
                <textarea id="description" rows="3" placeholder="Optional description..."></textarea>
            </div>
            <div class="form-group">
                <label for="targetVersion">Target Version:</label>
                <select id="targetVersion">
                    <option value="auto">Same as Source</option>
                    <option value="4.2">SIMA v4.2</option>
                    <option value="4.1">SIMA v4.1</option>
                </select>
                <small>Convert files to different version during export</small>
            </div>
            <button onclick="exportFiles()">📦 Create Export</button>
        </div>
        
        <div id="result-section" class="section hidden">
            <h2>4. Download Export</h2>
            <div id="result-content"></div>
        </div>
    </div>
    
    <!-- JavaScript Files -->
    <script>
    // Global state
    let knowledgeTree = {};
    let selectedFiles = new Set();
    let currentBasePath = '';

    /**
     * Scan directory for SIMA knowledge
     */
    function scanDirectory() {
        const directory = document.getElementById('simaDirectory').value.trim();
        if (!directory) {
            alert('Please enter a SIMA directory path');
            return;
        }
        
        document.getElementById('loading').style.display = 'block';
        document.getElementById('error').classList.remove('active');
        document.getElementById('scan-btn').disabled = true;
        
        const formData = new FormData();
        formData.append('action', 'scan');
        formData.append('directory', directory);
        
        fetch('', { 
            method: 'POST', 
            body: formData 
        })
        .then(r => {
            if (!r.ok) {
                throw new Error(`HTTP error! status: ${r.status}`);
            }
            return r.json();
        })
        .then(data => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('scan-btn').disabled = false;
            
            if (data.success) {
                knowledgeTree = data.tree;
                currentBasePath = data.base_path;
                
                if (data.version_info && data.version_info.version !== 'unknown') {
                    document.getElementById('detectedVersion').textContent = 
                        `✓ Detected: SIMA v${data.version_info.version} - ${data.stats.total_files} files found`;
                    document.getElementById('detectedVersion').style.display = 'block';
                    document.getElementById('sourceVersion').value = data.version_info.version;
                }
                
                renderTree();
                document.getElementById('tree-section').classList.remove('hidden');
                document.getElementById('export-section').classList.remove('hidden');
                updateSummary();
            } else {
                document.getElementById('error-text').textContent = data.error;
                document.getElementById('error').classList.add('active');
            }
        })
        .catch(err => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('scan-btn').disabled = false;
            document.getElementById('error-text').textContent = 'Error: ' + err.message;
            document.getElementById('error').classList.add('active');
            console.error('Scan error:', err);
        });
    }

    /**
     * Render knowledge tree
     */
    function renderTree() {
        const container = document.getElementById('tree');
        container.innerHTML = '';
        
        if (!knowledgeTree || knowledgeTree.length === 0) {
            container.innerHTML = '<p>No files found</p>';
            return;
        }
        
        knowledgeTree.forEach(node => {
            container.appendChild(renderNode(node, 0));
        });
    }

    /**
     * Render individual tree node
     */
    function renderNode(node, depth) {
        const div = document.createElement('div');
        div.style.marginLeft = (depth * 20) + 'px';
        div.style.padding = '5px';
        
        if (node.type === 'directory') {
            const label = document.createElement('div');
            label.style.cursor = 'pointer';
            label.style.fontWeight = 'bold';
            label.style.padding = '5px';
            label.style.background = '#f0f0f0';
            label.style.marginBottom = '5px';
            label.style.borderRadius = '3px';
            
            const toggle = document.createElement('span');
            toggle.textContent = '▼ ';
            label.appendChild(toggle);
            
            const name = document.createElement('span');
            name.textContent = `📁 ${node.name} (${node.total_files} files)`;
            label.appendChild(name);
            div.appendChild(label);
            
            const childrenDiv = document.createElement('div');
            if (node.children) {
                node.children.forEach(child => {
                    childrenDiv.appendChild(renderNode(child, depth + 1));
                });
            }
            div.appendChild(childrenDiv);
            
            // Toggle expand/collapse
            label.onclick = () => {
                const isHidden = childrenDiv.style.display === 'none';
                childrenDiv.style.display = isHidden ? 'block' : 'none';
                toggle.textContent = isHidden ? '▼ ' : '▶ ';
            };
        } else {
            // File node
            const label = document.createElement('label');
            label.style.display = 'block';
            label.style.padding = '3px';
            label.style.cursor = 'pointer';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = node.path;
            checkbox.checked = selectedFiles.has(node.path);
            checkbox.onchange = () => {
                if (checkbox.checked) {
                    selectedFiles.add(node.path);
                } else {
                    selectedFiles.delete(node.path);
                }
                updateSummary();
            };
            
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(` 📄 ${node.name}`));
            
            if (node.ref_id) {
                const refId = document.createElement('span');
                refId.textContent = ` [${node.ref_id}]`;
                refId.style.color = '#666';
                refId.style.fontSize = '0.9em';
                label.appendChild(refId);
            }
            
            div.appendChild(label);
        }
        
        return div;
    }

    /**
     * Update selection summary
     */
    function updateSummary() {
        const count = selectedFiles.size;
        document.getElementById('summary').textContent = 
            `Selection: ${count} file${count !== 1 ? 's' : ''} selected`;
    }

    /**
     * Expand all tree nodes
     */
    function expandAll() {
        document.querySelectorAll('.tree-container > div').forEach(d => {
            setExpanded(d, true);
        });
    }

    /**
     * Collapse all tree nodes
     */
    function collapseAll() {
        document.querySelectorAll('.tree-container > div').forEach(d => {
            setExpanded(d, false);
        });
    }

    /**
     * Set expanded state for a node
     */
    function setExpanded(div, expanded) {
        const childDiv = div.querySelector('div > div');
        const toggle = div.querySelector('span');
        
        if (childDiv && toggle) {
            childDiv.style.display = expanded ? 'block' : 'none';
            toggle.textContent = expanded ? '▼ ' : '▶ ';
        }
    }

    /**
     * Select all files
     */
    function selectAll() {
        document.querySelectorAll('#tree input[type="checkbox"]').forEach(cb => {
            cb.checked = true;
            selectedFiles.add(cb.value);
        });
        updateSummary();
    }

    /**
     * Clear all selections
     */
    function clearSelection() {
        document.querySelectorAll('#tree input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });
        selectedFiles.clear();
        updateSummary();
    }

    /**
     * Export selected files
     */
    function exportFiles() {
        if (selectedFiles.size === 0) {
            alert('Please select at least one file');
            return;
        }
        
        document.getElementById('loading').style.display = 'block';
        document.getElementById('error').classList.remove('active');
        
        const formData = new FormData();
        formData.append('action', 'export');
        formData.append('base_directory', currentBasePath);
        formData.append('archive_name', document.getElementById('archiveName').value.trim() || 'SIMA-Export');
        formData.append('description', document.getElementById('description').value.trim());
        formData.append('source_version', document.getElementById('sourceVersion').value);
        formData.append('target_version', document.getElementById('targetVersion').value);
        formData.append('selected_files', JSON.stringify(Array.from(selectedFiles)));
        
        fetch('', { 
            method: 'POST', 
            body: formData 
        })
        .then(r => {
            if (!r.ok) {
                throw new Error(`HTTP error! status: ${r.status}`);
            }
            return r.json();
        })
        .then(data => {
            document.getElementById('loading').style.display = 'none';
            
            if (data.success) {
                document.getElementById('result-content').innerHTML = `
                    <div class="success">
                        <h3>✓ Export Created Successfully!</h3>
                        <p><strong>Archive:</strong> ${data.archive_name}</p>
                        <p><strong>Files:</strong> ${data.file_count}</p>
                        <p><strong>Converted:</strong> ${data.converted_count}</p>
                        <p><a href="${data.download_url}" download>
                            <button>📥 Download Export</button>
                        </a></p>
                    </div>`;
                document.getElementById('result-section').classList.remove('hidden');
                document.getElementById('result-section').scrollIntoView({ behavior: 'smooth' });
            } else {
                document.getElementById('error-text').textContent = data.error;
                document.getElementById('error').classList.add('active');
            }
        })
        .catch(err => {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('error-text').textContent = 'Error: ' + err.message;
            document.getElementById('error').classList.add('active');
            console.error('Export error:', err);
        });
    }
    </script>
</body>
</html>
        <?php
    }
}
?>
