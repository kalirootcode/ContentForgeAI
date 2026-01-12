/**
 * ContentForge AI Chrome Extension - Popup Script
 * Handles UI interactions and communication with content script and API
 */

const API_URL = 'http://localhost:5678';
let extractedContent = null;

// DOM Elements
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const previewTitle = document.getElementById('previewTitle');
const previewUrl = document.getElementById('previewUrl');
const previewText = document.getElementById('previewText');
const extractBtn = document.getElementById('extractBtn');
const sendBtn = document.getElementById('sendBtn');
const result = document.getElementById('result');

// Check API connection on load
document.addEventListener('DOMContentLoaded', async () => {
    await checkConnection();
    await loadCurrentPageInfo();
});

// Check if API server is running
async function checkConnection() {
    try {
        const response = await fetch(`${API_URL}/status`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            statusDot.classList.add('connected');
            statusDot.classList.remove('disconnected');
            statusText.textContent = 'Conectado a ContentForge AI';
        } else {
            throw new Error('Not connected');
        }
    } catch (error) {
        statusDot.classList.add('disconnected');
        statusDot.classList.remove('connected');
        statusText.textContent = 'ContentForge no está ejecutándose';
    }
}

// Load current page info
async function loadCurrentPageInfo() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        previewTitle.textContent = tab.title || 'Sin título';
        previewUrl.textContent = tab.url || '';
        previewText.textContent = 'Haz clic en "Extraer Contenido" para obtener el texto de la página.';
    } catch (error) {
        console.error('Error loading page info:', error);
    }
}

// Extract content from current page
extractBtn.addEventListener('click', async () => {
    extractBtn.disabled = true;
    extractBtn.textContent = '⏳ Extrayendo...';

    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // Send message to content script
        const response = await chrome.tabs.sendMessage(tab.id, { action: 'extractContent' });

        if (response && response.success) {
            extractedContent = {
                url: tab.url,
                title: response.title,
                text: response.text,
                meta: response.meta,
                timestamp: new Date().toISOString()
            };

            // Update preview
            previewTitle.textContent = response.title;
            previewText.textContent = response.text.substring(0, 300) + (response.text.length > 300 ? '...' : '');

            sendBtn.disabled = false;
            showResult('✅ Contenido extraído correctamente', false);
        } else {
            throw new Error('No se pudo extraer el contenido');
        }
    } catch (error) {
        console.error('Extraction error:', error);
        showResult('❌ Error al extraer: ' + error.message, true);
    } finally {
        extractBtn.disabled = false;
        extractBtn.textContent = '📥 Extraer Contenido';
    }
});

// Send content to ContentForge API
sendBtn.addEventListener('click', async () => {
    if (!extractedContent) return;

    sendBtn.disabled = true;
    sendBtn.textContent = '⏳ Enviando...';

    try {
        const response = await fetch(`${API_URL}/extract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(extractedContent)
        });

        if (response.ok) {
            const data = await response.json();
            showResult('🚀 ¡Enviado a ContentForge AI!', false);

            // Reset after success
            setTimeout(() => {
                extractedContent = null;
                sendBtn.disabled = true;
            }, 2000);
        } else {
            throw new Error('Error del servidor');
        }
    } catch (error) {
        console.error('Send error:', error);
        showResult('❌ Error: ContentForge no responde', true);
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = '🚀 Enviar a ContentForge';
    }
});

// Show result message
function showResult(message, isError) {
    result.style.display = 'flex';
    result.className = isError ? 'result error' : 'result';
    result.querySelector('.result-text').textContent = message;
    result.querySelector('.result-icon').textContent = isError ? '❌' : '✅';

    setTimeout(() => {
        result.style.display = 'none';
    }, 3000);
}
