/**
 * ContentForge AI Chrome Extension - Enhanced Popup Script
 * Handles extraction options, platform detection, and API communication
 */

const API_URL = 'http://localhost:5678';
let extractedContent = null;

// Platform configurations
const PLATFORMS = {
    'tiktok.com': { name: 'TikTok', icon: '🎵', color: '#00f2ea' },
    'facebook.com': { name: 'Facebook', icon: '📘', color: '#1877f2' },
    'twitter.com': { name: 'Twitter', icon: '🐦', color: '#1da1f2' },
    'x.com': { name: 'X (Twitter)', icon: '✖️', color: '#000000' },
    'instagram.com': { name: 'Instagram', icon: '📷', color: '#e4405f' },
    'linkedin.com': { name: 'LinkedIn', icon: '💼', color: '#0077b5' },
    'youtube.com': { name: 'YouTube', icon: '📺', color: '#ff0000' },
    'reddit.com': { name: 'Reddit', icon: '🔴', color: '#ff4500' }
};

// DOM Elements
const elements = {
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    platformIcon: document.getElementById('platformIcon'),
    platformName: document.getElementById('platformName'),
    previewTitle: document.getElementById('previewTitle'),
    previewUrl: document.getElementById('previewUrl'),
    previewStats: document.getElementById('previewStats'),
    previewText: document.getElementById('previewText'),
    statLikes: document.getElementById('statLikes'),
    statComments: document.getElementById('statComments'),
    statShares: document.getElementById('statShares'),
    statViews: document.getElementById('statViews'),
    extractBtn: document.getElementById('extractBtn'),
    sendBtn: document.getElementById('sendBtn'),
    result: document.getElementById('result'),
    extractedInfo: document.getElementById('extractedInfo'),
    // Options
    optTitle: document.getElementById('optTitle'),
    optHashtags: document.getElementById('optHashtags'),
    optStats: document.getElementById('optStats'),
    optComments: document.getElementById('optComments')
};

// Initialize on load
document.addEventListener('DOMContentLoaded', async () => {
    await checkConnection();
    await detectPlatform();
});

// Check API connection
async function checkConnection() {
    try {
        const response = await fetch(`${API_URL}/status`, { method: 'GET' });
        if (response.ok) {
            elements.statusDot.classList.add('connected');
            elements.statusText.textContent = 'Conectado a ContentForge';
        } else {
            throw new Error('Not connected');
        }
    } catch (error) {
        elements.statusDot.classList.add('disconnected');
        elements.statusText.textContent = 'ContentForge no está activo';
    }
}

// Detect platform from current tab
async function detectPlatform() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const url = new URL(tab.url);
        const domain = url.hostname.replace('www.', '');

        // Find matching platform
        let detected = null;
        for (const [key, value] of Object.entries(PLATFORMS)) {
            if (domain.includes(key)) {
                detected = value;
                break;
            }
        }

        if (detected) {
            elements.platformIcon.textContent = detected.icon;
            elements.platformName.textContent = detected.name;
            elements.platformName.style.color = detected.color;
        } else {
            elements.platformIcon.textContent = '🌐';
            elements.platformName.textContent = 'Página Web';
        }

        elements.previewUrl.textContent = tab.url;
        elements.previewTitle.textContent = tab.title || 'Sin título';

    } catch (error) {
        console.error('Platform detection error:', error);
    }
}

// Get extraction options
function getExtractionOptions() {
    return {
        includeTitle: elements.optTitle.checked,
        includeHashtags: elements.optHashtags.checked,
        includeStats: elements.optStats.checked,
        includeComments: elements.optComments.checked
    };
}

// Extract content
elements.extractBtn.addEventListener('click', async () => {
    elements.extractBtn.disabled = true;
    elements.extractBtn.textContent = '⏳ Extrayendo...';

    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const options = getExtractionOptions();

        // Send message to content script with options
        const response = await chrome.tabs.sendMessage(tab.id, {
            action: 'extractContent',
            options: options
        });

        if (response && response.success) {
            extractedContent = {
                url: tab.url,
                platform: response.platform,
                title: response.title,
                description: response.description,
                hashtags: response.hashtags,
                stats: response.stats,
                comments: response.comments,
                text: response.formattedText,
                timestamp: new Date().toISOString()
            };

            // Update preview
            updatePreview(extractedContent);

            elements.sendBtn.disabled = false;
            elements.extractedInfo.textContent = `✅ Extraído: ${response.itemCount || 0} elementos`;
            showResult('✅ Contenido extraído', false);
        } else {
            throw new Error(response?.error || 'Error de extracción');
        }
    } catch (error) {
        console.error('Extraction error:', error);
        showResult('❌ Error: ' + error.message, true);
    } finally {
        elements.extractBtn.disabled = false;
        elements.extractBtn.textContent = '📥 Extraer Contenido';
    }
});

// Update preview with extracted data
function updatePreview(data) {
    elements.previewTitle.textContent = data.title || 'Sin título';

    // Show stats if available
    if (data.stats) {
        elements.previewStats.style.display = 'flex';
        elements.statLikes.textContent = formatNumber(data.stats.likes || 0);
        elements.statComments.textContent = formatNumber(data.stats.comments || 0);
        elements.statShares.textContent = formatNumber(data.stats.shares || 0);
        elements.statViews.textContent = formatNumber(data.stats.views || 0);
    }

    // Build preview text
    let preview = '';
    if (data.description) {
        preview += data.description.substring(0, 150) + '\n';
    }
    if (data.hashtags && data.hashtags.length > 0) {
        preview += '\n' + data.hashtags.slice(0, 5).join(' ');
    }
    elements.previewText.textContent = preview || 'Contenido extraído correctamente';
}

// Format numbers (1000 -> 1K)
function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

// Send to ContentForge API
elements.sendBtn.addEventListener('click', async () => {
    if (!extractedContent) return;

    elements.sendBtn.disabled = true;
    elements.sendBtn.textContent = '⏳ Enviando...';

    try {
        const response = await fetch(`${API_URL}/extract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(extractedContent)
        });

        if (response.ok) {
            showResult('🚀 ¡Enviado a ContentForge!', false);
            elements.extractedInfo.textContent = '📤 Contenido enviado';
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        showResult('❌ Error de conexión', true);
    } finally {
        elements.sendBtn.disabled = false;
        elements.sendBtn.textContent = '🚀 Enviar a ContentForge';
    }
});

// Show result message
function showResult(message, isError) {
    elements.result.style.display = 'flex';
    elements.result.className = isError ? 'result error' : 'result';
    elements.result.querySelector('.result-text').textContent = message;
    elements.result.querySelector('.result-icon').textContent = isError ? '❌' : '✅';

    setTimeout(() => {
        elements.result.style.display = 'none';
    }, 3000);
}
