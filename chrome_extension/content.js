/**
 * ContentForge AI Chrome Extension - Content Script
 * Extracts page content intelligently
 */

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractContent') {
        try {
            const content = extractPageContent();
            sendResponse({ success: true, ...content });
        } catch (error) {
            sendResponse({ success: false, error: error.message });
        }
    }
    return true; // Required for async response
});

/**
 * Extract main content from the page
 */
function extractPageContent() {
    // Get page title
    const title = document.title || '';

    // Get meta description
    const metaDesc = document.querySelector('meta[name="description"]');
    const metaOG = document.querySelector('meta[property="og:description"]');
    const description = metaDesc?.content || metaOG?.content || '';

    // Get meta keywords
    const metaKeywords = document.querySelector('meta[name="keywords"]');
    const keywords = metaKeywords?.content || '';

    // Get main text content
    const text = extractMainText();

    // Get social media specific content
    const socialContent = extractSocialContent();

    return {
        title,
        text: socialContent || text,
        meta: {
            description,
            keywords,
            url: window.location.href,
            domain: window.location.hostname
        }
    };
}

/**
 * Extract main text, avoiding navigation and ads
 */
function extractMainText() {
    // Priority selectors for main content
    const contentSelectors = [
        'article',
        '[role="main"]',
        'main',
        '.post-content',
        '.article-content',
        '.entry-content',
        '.content',
        '#content',
        '.post-body',
        '.story-body'
    ];

    // Try each selector
    for (const selector of contentSelectors) {
        const element = document.querySelector(selector);
        if (element && element.innerText.length > 100) {
            return cleanText(element.innerText);
        }
    }

    // Fallback: get body text, excluding common non-content elements
    const excludeSelectors = [
        'nav', 'header', 'footer', 'aside',
        '.sidebar', '.menu', '.navigation',
        '.advertisement', '.ads', '.social-share',
        'script', 'style', 'noscript'
    ];

    const body = document.body.cloneNode(true);
    excludeSelectors.forEach(sel => {
        body.querySelectorAll(sel).forEach(el => el.remove());
    });

    return cleanText(body.innerText);
}

/**
 * Extract content from social media pages
 */
function extractSocialContent() {
    const domain = window.location.hostname;

    // Facebook
    if (domain.includes('facebook.com')) {
        return extractFacebookContent();
    }

    // Twitter/X
    if (domain.includes('twitter.com') || domain.includes('x.com')) {
        return extractTwitterContent();
    }

    // LinkedIn
    if (domain.includes('linkedin.com')) {
        return extractLinkedInContent();
    }

    // Reddit
    if (domain.includes('reddit.com')) {
        return extractRedditContent();
    }

    return null;
}

/**
 * Extract Facebook post content
 */
function extractFacebookContent() {
    // Try different Facebook post selectors
    const selectors = [
        '[data-ad-preview="message"]',
        '[data-testid="post_message"]',
        '.userContent',
        '[dir="auto"]'
    ];

    for (const sel of selectors) {
        const elements = document.querySelectorAll(sel);
        if (elements.length > 0) {
            const texts = Array.from(elements)
                .map(el => el.innerText)
                .filter(t => t.length > 20);

            if (texts.length > 0) {
                return texts.slice(0, 5).join('\n\n---\n\n');
            }
        }
    }

    return null;
}

/**
 * Extract Twitter/X post content
 */
function extractTwitterContent() {
    const tweets = document.querySelectorAll('[data-testid="tweetText"]');
    if (tweets.length > 0) {
        return Array.from(tweets)
            .slice(0, 10)
            .map(t => t.innerText)
            .join('\n\n---\n\n');
    }
    return null;
}

/**
 * Extract LinkedIn post content
 */
function extractLinkedInContent() {
    const posts = document.querySelectorAll('.feed-shared-update-v2__description');
    if (posts.length > 0) {
        return Array.from(posts)
            .slice(0, 5)
            .map(p => p.innerText)
            .join('\n\n---\n\n');
    }
    return null;
}

/**
 * Extract Reddit post content
 */
function extractRedditContent() {
    const posts = document.querySelectorAll('[data-testid="post-container"]');
    if (posts.length > 0) {
        return Array.from(posts)
            .slice(0, 5)
            .map(p => {
                const title = p.querySelector('h3')?.innerText || '';
                const body = p.querySelector('[data-click-id="text"]')?.innerText || '';
                return `${title}\n${body}`;
            })
            .join('\n\n---\n\n');
    }
    return null;
}

/**
 * Clean extracted text
 */
function cleanText(text) {
    return text
        .replace(/\s+/g, ' ')
        .replace(/\n\s*\n/g, '\n\n')
        .trim()
        .substring(0, 5000); // Limit to 5000 chars
}
