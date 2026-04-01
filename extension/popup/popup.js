/**
 * Popup UI Handler
 * Manages user interactions and displays analysis results
 */

class PopupUI {
    constructor() {
        this.apiEndpoint = 'http://localhost:5000';
        this.analysisHistory = [];
        this.currentResults = null;
        this.init();
    }

    async init() {
        // Load settings from storage
        await this.loadSettings();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load analysis history
        await this.loadHistory();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Analysis buttons
        document.getElementById('analyze-url-btn').addEventListener('click', () => this.analyzeURL());
        document.getElementById('analyze-file-btn').addEventListener('click', () => this.analyzeFile());
        document.getElementById('scan-page-btn').addEventListener('click', () => this.scanPageImages());

        // Results buttons
        document.getElementById('save-result-btn')?.addEventListener('click', () => this.saveResult());
        document.getElementById('share-result-btn')?.addEventListener('click', () => this.shareResult());
        document.getElementById('view-report-btn')?.addEventListener('click', () => this.viewFullReport());
        document.getElementById('new-analysis-btn')?.addEventListener('click', () => this.resetAnalysis());

        // Settings
        document.getElementById('settings-btn').addEventListener('click', () => this.toggleSettings());
        document.getElementById('save-settings-btn').addEventListener('click', () => this.saveSettings());
        document.getElementById('close-settings-btn').addEventListener('click', () => this.toggleSettings());

        // History
        document.getElementById('clear-history-btn')?.addEventListener('click', () => this.clearHistory());
    }

    async analyzeURL() {
        const url = document.getElementById('media-url').value;
        
        if (!url.trim()) {
            this.showError('Please enter a URL');
            return;
        }

        if (!this.isValidURL(url)) {
            this.showError('Please enter a valid URL');
            return;
        }

        await this.performAnalysis('url', url);
    }

    async analyzeFile() {
        const fileInput = document.getElementById('media-file');
        const file = fileInput.files[0];

        if (!file) {
            this.showError('Please select a file');
            return;
        }

        await this.performAnalysis('file', file);
    }

    async scanPageImages() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        // Request content script to extract images
        chrome.tabs.sendMessage(tab.id, {
            action: 'getPageImages'
        }, (response) => {
            if (chrome.runtime.lastError) {
                this.showError('Could not access page images');
                return;
            }

            if (response && response.images && response.images.length > 0) {
                this.analyzeImages(response.images);
            } else {
                this.showError('No images found on page');
            }
        });
    }

    async performAnalysis(type, data) {
        // Show loading
        const resultsContainer = document.getElementById('results-container');
        const loadingIndicator = document.getElementById('loading-indicator');
        const resultsSection = document.getElementById('results-section');

        resultsContainer.style.display = 'block';
        loadingIndicator.style.display = 'block';
        resultsSection.style.display = 'none';

        try {
            let results;

            if (type === 'url') {
                results = await this.callAPI('analyze/image', { url: data });
            } else if (type === 'file') {
                results = await this.uploadFile(data);
            } else {
                throw new Error('Invalid analysis type');
            }

            // Save to history
            await this.addToHistory({
                type: type,
                timestamp: new Date().toISOString(),
                results: results
            });

            // Display results
            this.displayResults(results);

        } catch (error) {
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            loadingIndicator.style.display = 'none';
        }
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

        try {
            const response = await fetch(`${this.apiEndpoint}/api/v1/analyze/image`, {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }

            return await response.json();
        } finally {
            clearTimeout(timeoutId);
        }
    }

    async callAPI(endpoint, data) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

        try {
            const response = await fetch(`${this.apiEndpoint}/api/v1/${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data),
                signal: controller.signal
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.statusText}`);
            }

            return await response.json();
        } finally {
            clearTimeout(timeoutId);
        }
    }

    displayResults(results) {
        const resultsSection = document.getElementById('results-section');
        this.currentResults = results;

        // Calculate risk level
        const confidence = results.detection_results?.confidence || results.overall_risk?.score || 0;
        const riskLevel = this.calculateRiskLevel(confidence);

        // Update risk badge
        const riskElement = document.getElementById('risk-level');
        riskElement.textContent = riskLevel.level.toUpperCase();
        riskElement.className = `risk-level risk-${riskLevel.level}`;

        const riskTitle = document.getElementById('risk-title');
        const riskDescription = document.getElementById('risk-description');

        switch(riskLevel.level) {
            case 'low':
                riskTitle.textContent = '✓ Likely Authentic';
                riskDescription.textContent = 'No significant signs of manipulation detected';
                break;
            case 'medium':
                riskTitle.textContent = '⚠ Potentially Modified';
                riskDescription.textContent = 'Some anomalies detected, verify with caution';
                break;
            case 'high':
                riskTitle.textContent = '⚠️ Likely Fake';
                riskDescription.textContent = 'Strong indicators of deepfake or manipulation';
                break;
            case 'critical':
                riskTitle.textContent = '🚫 Very Likely Fake';
                riskDescription.textContent = 'Multiple strong indicators of synthetic media';
                break;
        }

        // Update confidence meter
        const confidenceBar = document.getElementById('confidence-bar');
        const confidenceText = document.getElementById('confidence-text');
        confidenceBar.style.width = (confidence * 100) + '%';
        confidenceText.textContent = `${(confidence * 100).toFixed(1)}% Confidence`;

        // Display detection details
        this.displayDetectionDetails(results);

        // Display risk factors
        this.displayRiskFactors(results);

        // Show results section
        resultsSection.style.display = 'block';
        document.getElementById('new-analysis-btn').style.display = 'block';
    }

    displayDetectionDetails(results) {
        const detailsContainer = document.getElementById('detection-details');
        detailsContainer.innerHTML = '';

        const detections = results.detection_results;
        if (detections) {
            // Face count
            if (detections.face_count !== undefined) {
                this.addDetailItem(detailsContainer, 'Faces Detected', detections.face_count);
            }

            // Is Deepfake
            if (detections.is_deepfake !== undefined) {
                this.addDetailItem(detailsContainer, 'Deepfake Detected', 
                    detections.is_deepfake ? '⚠️ Yes' : '✓ No');
            }

            // Specific indicators
            if (detections.detections && detections.detections.length > 0) {
                const face = detections.detections[0];
                if (face.indicators) {
                    if (face.indicators.frequency_score !== undefined) {
                        this.addDetailItem(detailsContainer, 'Frequency Anomaly',
                            this.scoreToStatus(face.indicators.frequency_score));
                    }
                    if (face.indicators.texture_score !== undefined) {
                        this.addDetailItem(detailsContainer, 'Synthetic Texture',
                            this.scoreToStatus(face.indicators.texture_score));
                    }
                    if (face.indicators.blink_score !== undefined) {
                        this.addDetailItem(detailsContainer, 'Eye Consistency',
                            this.scoreToStatus(face.indicators.blink_score));
                    }
                    if (face.indicators.blend_score !== undefined) {
                        this.addDetailItem(detailsContainer, 'Blend Artifacts',
                            this.scoreToStatus(face.indicators.blend_score));
                    }
                }
            }
        }

        // Metadata analysis
        const metadata = results.metadata_results;
        if (metadata) {
            if (metadata.exif_analysis?.exif_present !== undefined) {
                this.addDetailItem(detailsContainer, 'EXIF Data',
                    metadata.exif_analysis.exif_present ? '✓ Present' : '⚠️ Missing');
            }
        }
    }

    displayRiskFactors(results) {
        const riskFactorsSection = document.getElementById('risk-factors-section');
        const riskFactorsList = document.getElementById('risk-factors-list');

        const riskFactors = results.detection_results?.risk_factors || [];
        const metadataRisks = results.metadata_results?.exif_analysis?.suspicious_fields || [];

        const allRisks = [...riskFactors, ...metadataRisks];

        if (allRisks.length > 0) {
            riskFactorsSection.style.display = 'block';
            riskFactorsList.innerHTML = '';
            allRisks.forEach(risk => {
                const li = document.createElement('li');
                li.textContent = risk;
                riskFactorsList.appendChild(li);
            });
        } else {
            riskFactorsSection.style.display = 'none';
        }
    }

    addDetailItem(container, label, value) {
        const div = document.createElement('div');
        div.className = 'detail-item';
        div.innerHTML = `<span class="detail-label">${label}:</span><span class="detail-value">${value}</span>`;
        container.appendChild(div);
    }

    scoreToStatus(score) {
        if (score < 0.33) return '✓ Normal';
        if (score < 0.66) return '⚠️ Anomaly';
        return '🚫 Strong Anomaly';
    }

    calculateRiskLevel(confidence) {
        if (confidence >= 0.8) return { level: 'critical', score: confidence };
        if (confidence >= 0.6) return { level: 'high', score: confidence };
        if (confidence >= 0.4) return { level: 'medium', score: confidence };
        return { level: 'low', score: confidence };
    }

    isValidURL(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show selected tab
        document.getElementById(`${tabName}-tab`).classList.add('active');
        event.target.classList.add('active');
    }

    resetAnalysis() {
        document.getElementById('results-container').style.display = 'none';
        document.getElementById('results-section').style.display = 'none';
        document.getElementById('media-url').value = '';
        document.getElementById('media-file').value = '';
        document.getElementById('new-analysis-btn').style.display = 'none';
        this.currentResults = null;
    }

    async loadHistory() {
        const result = await chrome.storage.local.get(['analysisHistory']);
        this.analysisHistory = result.analysisHistory || [];
        this.displayHistory();
    }

    async addToHistory(entry) {
        this.analysisHistory.unshift(entry);
        // Keep only last 50 entries
        if (this.analysisHistory.length > 50) {
            this.analysisHistory = this.analysisHistory.slice(0, 50);
        }
        await chrome.storage.local.set({ analysisHistory: this.analysisHistory });
        await this.loadHistory();
    }

    displayHistory() {
        const historyList = document.getElementById('history-list');
        const clearBtn = document.getElementById('clear-history-btn');

        if (this.analysisHistory.length === 0) {
            historyList.innerHTML = '<p class="empty-state">No analysis history yet</p>';
            clearBtn.style.display = 'none';
            return;
        }

        clearBtn.style.display = 'block';
        historyList.innerHTML = '';

        this.analysisHistory.forEach((entry, index) => {
            const div = document.createElement('div');
            div.className = 'history-item';

            const timestamp = new Date(entry.timestamp);
            const riskLevel = entry.results.overall_risk?.level || 'unknown';

            div.innerHTML = `
                <div class="history-item-header">
                    <span class="history-time">${timestamp.toLocaleString()}</span>
                    <span class="risk-badge-inline risk-${riskLevel}">${riskLevel.toUpperCase()}</span>
                </div>
                <div class="history-item-details">
                    <p>Confidence: ${((entry.results.overall_risk?.score || 0) * 100).toFixed(1)}%</p>
                </div>
            `;

            div.addEventListener('click', () => this.displayResults(entry.results));
            historyList.appendChild(div);
        });
    }

    async clearHistory() {
        if (confirm('Clear all analysis history?')) {
            this.analysisHistory = [];
            await chrome.storage.local.set({ analysisHistory: [] });
            await this.loadHistory();
        }
    }

    toggleSettings() {
        const panel = document.getElementById('settings-panel');
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }

    async loadSettings() {
        const result = await chrome.storage.sync.get([
            'apiEndpoint',
            'enableNotifications',
            'enableAutoScan',
            'enableContextMenu',
            'detectionSensitivity'
        ]);

        this.apiEndpoint = result.apiEndpoint || 'http://localhost:5000';
        document.getElementById('api-endpoint').value = this.apiEndpoint;
        document.getElementById('enable-notifications').checked = result.enableNotifications !== false;
        document.getElementById('enable-auto-scan').checked = result.enableAutoScan !== false;
        document.getElementById('enable-context-menu').checked = result.enableContextMenu !== false;
        document.getElementById('detection-sensitivity').value = result.detectionSensitivity || 'medium';
    }

    async saveSettings() {
        const settings = {
            apiEndpoint: document.getElementById('api-endpoint').value,
            enableNotifications: document.getElementById('enable-notifications').checked,
            enableAutoScan: document.getElementById('enable-auto-scan').checked,
            enableContextMenu: document.getElementById('enable-context-menu').checked,
            detectionSensitivity: document.getElementById('detection-sensitivity').value
        };

        await chrome.storage.sync.set(settings);
        this.apiEndpoint = settings.apiEndpoint;
        this.showMessage('Settings saved successfully!');
        this.toggleSettings();
    }

    saveResult() {
        if (!this.currentResults) return;

        const dataStr = JSON.stringify(this.currentResults, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `analysis-${Date.now()}.json`;
        link.click();
    }

    shareResult() {
        if (!this.currentResults) return;

        const text = `Fake Content Detection Result:\n` +
            `Risk Level: ${this.currentResults.overall_risk?.level || 'unknown'}\n` +
            `Confidence: ${((this.currentResults.overall_risk?.score || 0) * 100).toFixed(1)}%`;

        if (navigator.share) {
            navigator.share({
                title: 'Fake Content Detection',
                text: text
            }).catch(err => console.log('Share error:', err));
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(text).then(() => {
                this.showMessage('Result copied to clipboard!');
            });
        }
    }

    viewFullReport() {
        // Could open a full report page
        const report = JSON.stringify(this.currentResults, null, 2);
        const blob = new Blob([report], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        chrome.tabs.create({ url: url });
    }

    showError(message) {
        const container = document.getElementById('results-container');
        const loadingIndicator = document.getElementById('loading-indicator');
        const resultsSection = document.getElementById('results-section');

        container.style.display = 'block';
        loadingIndicator.style.display = 'block';
        loadingIndicator.innerHTML = `
            <div class="error-message">
                <p>❌ ${message}</p>
                <button onclick="location.reload()" style="margin-top: 10px;">Try Again</button>
            </div>
        `;
        resultsSection.style.display = 'none';
    }

    showMessage(message) {
        const container = document.getElementById('results-container');
        const loadingIndicator = document.getElementById('loading-indicator');
        container.style.display = 'block';
        loadingIndicator.style.display = 'block';
        loadingIndicator.innerHTML = `<p>✓ ${message}</p>`;
        setTimeout(() => {
            container.style.display = 'none';
        }, 3000);
    }

    async analyzeImages(images) {
        // This would implement batch analysis
        this.showMessage(`Found ${images.length} images. Starting analysis...`);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new PopupUI();
});
