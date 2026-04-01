/**
 * Content Script
 * Injects into web pages to detect and analyze images/videos
 */

console.log('[Fake Detector] Content script loaded');

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getPageImages') {
        const images = extractPageImages();
        sendResponse({ images: images });
    } else if (request.action === 'scanPage') {
        scanPageMedia();
    }
});

/**
 * Extract all images from the current page
 */
function extractPageImages() {
    const images = [];
    
    // Get img elements
    document.querySelectorAll('img').forEach(img => {
        if (img.src && img.offsetHeight > 50 && img.offsetWidth > 50) {
            images.push({
                src: img.src,
                alt: img.alt || '',
                width: img.width,
                height: img.height,
                type: 'image'
            });
        }
    });

    // Get background images from divs
    document.querySelectorAll('div, section, article').forEach(el => {
        const bg = window.getComputedStyle(el).backgroundImage;
        if (bg && bg !== 'none' && bg.includes('url')) {
            const url = bg.slice(5, -2); // Extract URL from url("...")
            if (!images.find(img => img.src === url)) {
                images.push({
                    src: url,
                    alt: 'Background image',
                    width: el.offsetWidth,
                    height: el.offsetHeight,
                    type: 'background'
                });
            }
        }
    });

    // Get video posters and thumbnails
    document.querySelectorAll('video').forEach(video => {
        if (video.poster) {
            images.push({
                src: video.poster,
                alt: 'Video poster',
                width: video.width,
                height: video.height,
                type: 'video_poster'
            });
        }
    });

    return images;
}

/**
 * Scan page and highlight suspicious content
 */
function scanPageMedia() {
    const images = extractPageImages();
    let suspiciousCount = 0;

    images.forEach(img => {
        // Send to background script for analysis
        chrome.runtime.sendMessage({
            action: 'analyzeImageURL',
            imageUrl: img.src
        }, (response) => {
            if (response && response.is_suspicious) {
                suspiciousCount++;
                highlightSuspiciousImage(img.src);
            }
        });
    });

    // Show notification
    setTimeout(() => {
        if (suspiciousCount > 0) {
            showNotification(`⚠️ Found ${suspiciousCount} suspicious image(s) on this page`);
        }
    }, 1000);
}

/**
 * Highlight a suspicious image on the page
 */
function highlightSuspiciousImage(imageSrc) {
    document.querySelectorAll('img').forEach(img => {
        if (img.src === imageSrc) {
            img.style.border = '3px solid #dc2626';
            img.style.boxShadow = '0 0 10px rgba(220, 38, 38, 0.5)';
            
            // Add warning badge
            const badge = document.createElement('div');
            badge.className = 'fake-detector-warning';
            badge.textContent = '⚠️ SUSPICIOUS';
            badge.style.cssText = `
                position: absolute;
                top: 10px;
                right: 10px;
                background: #dc2626;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                z-index: 10000;
            `;
            
            img.parentElement.style.position = 'relative';
            img.parentElement.appendChild(badge);
        }
    });
}

/**
 * Register context menu for image analysis
 */
function registerContextMenu() {
    chrome.runtime.sendMessage({
        action: 'setupContextMenu'
    });
}

/**
 * Show in-page notification
 */
function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #f59e0b;
        color: white;
        padding: 16px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        z-index: 10001;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize
registerContextMenu();
