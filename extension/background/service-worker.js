/**
 * Service Worker / Background Script
 * Handles background tasks, context menus, and API communication
 */

console.log('[Fake Detector] Background script loaded');

let apiEndpoint = 'http://localhost:5000';

// Load settings on startup
chrome.storage.sync.get(['apiEndpoint'], (result) => {
    if (result.apiEndpoint) {
        apiEndpoint = result.apiEndpoint;
    }
});

// Listen for settings changes
chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName === 'sync' && changes.apiEndpoint) {
        apiEndpoint = changes.apiEndpoint.newValue;
    }
});

// Setup context menu
function setupContextMenu() {
    chrome.contextMenus.removeAll(() => {
        // Analyze image context menu
        chrome.contextMenus.create({
            id: 'analyze-image',
            title: '🔍 Analyze Image (Fake Detector)',
            contexts: ['image'],
            icons: {
                '16': 'images/icon-16.png'
            }
        });

        // Analyze link context menu
        chrome.contextMenus.create({
            id: 'analyze-link',
            title: '🔍 Analyze Link (Fake Detector)',
            contexts: ['link']
        });
    });
}

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'analyze-image') {
        analyzeContextImage(info.srcUrl, tab);
    } else if (info.menuItemId === 'analyze-link') {
        analyzeContextLink(info.linkUrl, tab);
    }
});

/**
 * Analyze image from context menu
 */
async function analyzeContextImage(imageUrl, tab) {
    // Open popup with the image URL
    chrome.action.setPopup({ popup: 'popup/popup.html' });
    
    // Send message to popup with the URL
    chrome.tabs.sendMessage(tab.id, {
        action: 'setAnalysisURL',
        url: imageUrl
    }).catch(() => {
        // Popup might not be ready, store in temporary storage
        chrome.storage.session.set({ pendingAnalysisURL: imageUrl });
    });
}

/**
 * Analyze link from context menu
 */
async function analyzeContextLink(linkUrl, tab) {
    chrome.storage.session.set({ pendingAnalysisURL: linkUrl });
}

/**
 * Listen for messages from content script and popup
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'setupContextMenu') {
        setupContextMenu();
    } else if (request.action === 'analyzeImageURL') {
        analyzeImage(request.imageUrl, sendResponse);
        return true; // Keep the connection open for async response
    } else if (request.action === 'analyzeVideoURL') {
        analyzeVideo(request.videoUrl, sendResponse);
        return true;
    }
});

/**
 * Analyze image URL
 */
async function analyzeImage(imageUrl, sendResponse) {
    try {
        const response = await fetch(`${apiEndpoint}/api/v1/analyze/image`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: imageUrl })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        const result = await response.json();
        
        sendResponse({
            success: true,
            data: result,
            is_suspicious: result.overall_risk?.level !== 'low'
        });

    } catch (error) {
        console.error('[Fake Detector] Analysis error:', error);
        sendResponse({
            success: false,
            error: error.message,
            is_suspicious: null
        });
    }
}

/**
 * Analyze video URL
 */
async function analyzeVideo(videoUrl, sendResponse) {
    try {
        const response = await fetch(`${apiEndpoint}/api/v1/analyze/video`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: videoUrl, sample_frames: 10 })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        const result = await response.json();
        
        sendResponse({
            success: true,
            data: result,
            is_suspicious: result.overall_risk?.level !== 'low'
        });

    } catch (error) {
        console.error('[Fake Detector] Video analysis error:', error);
        sendResponse({
            success: false,
            error: error.message,
            is_suspicious: null
        });
    }
}

/**
 * Monitor for tab updates to enable/disable extension on certain sites
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete') {
        // Check if extension should be active on this page
        const enabledSites = [
            'twitter.com',
            'facebook.com',
            'instagram.com',
            'tiktok.com',
            'reddit.com',
            'youtube.com',
            'whatsapp.web.com'
        ];

        const isEnabledSite = enabledSites.some(site => tab.url?.includes(site));
        
        // Set extension icon color based on site
        chrome.action.setBadgeBackgroundColor(
            { color: isEnabledSite ? '#2563eb' : '#9ca3af', tabId },
            () => {
                if (isEnabledSite) {
                    chrome.action.setBadgeText({ text: '✓', tabId });
                } else {
                    chrome.action.setBadgeText({ text: '', tabId });
                }
            }
        );
    }
});

/**
 * Handle installation and updates
 */
chrome.runtime.onInstalled.addListener(({ reason }) => {
    if (reason === 'install') {
        // Open welcome/setup page
        chrome.tabs.create({
            url: 'popup/popup.html?welcome=true'
        });
    }
});

// Initialize all components
setupContextMenu();

console.log('[Fake Detector] Background script initialization complete');
