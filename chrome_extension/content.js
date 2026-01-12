/**
 * ContentForge AI - Enhanced Content Script
 * Smart extraction for TikTok, Facebook, Twitter, and other platforms
 */

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractContent') {
        try {
            const options = request.options || {};
            const content = extractSmartContent(options);
            sendResponse({ success: true, ...content });
        } catch (error) {
            sendResponse({ success: false, error: error.message });
        }
    }
    return true;
});

/**
 * Smart content extraction based on platform
 */
function extractSmartContent(options) {
    const domain = window.location.hostname;
    let result = {
        platform: 'generic',
        title: document.title,
        description: '',
        hashtags: [],
        stats: null,
        comments: [],
        formattedText: '',
        itemCount: 0
    };

    // Platform-specific extraction
    if (domain.includes('tiktok.com')) {
        result = extractTikTok(options);
    } else if (domain.includes('facebook.com')) {
        result = extractFacebook(options);
    } else if (domain.includes('twitter.com') || domain.includes('x.com')) {
        result = extractTwitter(options);
    } else if (domain.includes('instagram.com')) {
        result = extractInstagram(options);
    } else if (domain.includes('youtube.com')) {
        result = extractYouTube(options);
    } else if (domain.includes('linkedin.com')) {
        result = extractLinkedIn(options);
    } else {
        result = extractGeneric(options);
    }

    // Format text for display
    result.formattedText = formatExtractedContent(result, options);

    return result;
}

/**
 * TikTok Extraction
 */
function extractTikTok(options) {
    const result = {
        platform: 'tiktok',
        title: '',
        description: '',
        hashtags: [],
        stats: { likes: 0, comments: 0, shares: 0, views: 0 },
        comments: [],
        author: '',
        itemCount: 0
    };

    // Author name
    const authorEl = document.querySelector('[data-e2e="browse-username"]') ||
        document.querySelector('[class*="AuthorTitle"]') ||
        document.querySelector('h3[data-e2e="user-title"]');
    if (authorEl) {
        result.author = authorEl.innerText.trim();
        result.itemCount++;
    }

    // Video description
    const descEl = document.querySelector('[data-e2e="browse-video-desc"]') ||
        document.querySelector('[class*="ContentContainer"]') ||
        document.querySelector('[data-e2e="video-desc"]');
    if (descEl) {
        result.description = descEl.innerText.trim();
        result.title = result.description.split('\n')[0].substring(0, 100);
        result.itemCount++;
    }

    // Hashtags
    if (options.includeHashtags) {
        const hashtagEls = document.querySelectorAll('[data-e2e="browse-video-desc"] a[href*="/tag/"]') ||
            document.querySelectorAll('a[href*="/tag/"]');
        result.hashtags = Array.from(hashtagEls).map(el => el.innerText.trim()).filter(h => h.startsWith('#'));
        if (result.hashtags.length > 0) result.itemCount += result.hashtags.length;
    }

    // Stats
    if (options.includeStats) {
        // Likes
        const likesEl = document.querySelector('[data-e2e="like-count"]') ||
            document.querySelector('[data-e2e="browse-like-count"]');
        if (likesEl) result.stats.likes = parseStatNumber(likesEl.innerText);

        // Comments count
        const commentsEl = document.querySelector('[data-e2e="comment-count"]') ||
            document.querySelector('[data-e2e="browse-comment-count"]');
        if (commentsEl) result.stats.comments = parseStatNumber(commentsEl.innerText);

        // Shares
        const sharesEl = document.querySelector('[data-e2e="share-count"]');
        if (sharesEl) result.stats.shares = parseStatNumber(sharesEl.innerText);

        // Views
        const viewsEl = document.querySelector('[data-e2e="video-views"]') ||
            document.querySelector('strong[data-e2e="video-views"]');
        if (viewsEl) result.stats.views = parseStatNumber(viewsEl.innerText);

        result.itemCount++;
    }

    // Comments
    if (options.includeComments) {
        const commentEls = document.querySelectorAll('[data-e2e="comment-item"]') ||
            document.querySelectorAll('[class*="CommentItem"]');
        result.comments = Array.from(commentEls).slice(0, 20).map(el => {
            const userEl = el.querySelector('[data-e2e="comment-username"]') || el.querySelector('a[href*="/@"]');
            const textEl = el.querySelector('[data-e2e="comment-text"]') || el.querySelector('p');
            return {
                user: userEl?.innerText.trim() || 'Usuario',
                text: textEl?.innerText.trim() || ''
            };
        }).filter(c => c.text);
        result.itemCount += result.comments.length;
    }

    return result;
}

/**
 * Facebook Extraction
 */
function extractFacebook(options) {
    const result = {
        platform: 'facebook',
        title: '',
        description: '',
        hashtags: [],
        stats: { likes: 0, comments: 0, shares: 0 },
        comments: [],
        author: '',
        itemCount: 0
    };

    // Post content
    const postEl = document.querySelector('[data-ad-preview="message"]') ||
        document.querySelector('[data-testid="post_message"]') ||
        document.querySelector('[dir="auto"][style*="webkit-line-clamp"]');
    if (postEl) {
        result.description = postEl.innerText.trim();
        result.title = result.description.substring(0, 100);
        result.itemCount++;
    }

    // Author
    const authorEl = document.querySelector('h2 a[role="link"]') ||
        document.querySelector('strong a');
    if (authorEl) {
        result.author = authorEl.innerText.trim();
        result.itemCount++;
    }

    // Hashtags
    if (options.includeHashtags) {
        const hashtagMatches = result.description.match(/#[\w\u00C0-\u024F]+/g) || [];
        result.hashtags = hashtagMatches;
    }

    // Stats - reactions, comments, shares from the reaction bar
    if (options.includeStats) {
        const statsText = document.querySelector('[aria-label*="reacciones"]') ||
            document.querySelector('[aria-label*="reactions"]');
        if (statsText) {
            result.stats.likes = parseStatNumber(statsText.getAttribute('aria-label') || '0');
        }
    }

    // Comments
    if (options.includeComments) {
        const commentEls = document.querySelectorAll('[data-testid="comment"]') ||
            document.querySelectorAll('[aria-label="Comentario"]');
        result.comments = Array.from(commentEls).slice(0, 15).map(el => ({
            user: el.querySelector('a')?.innerText || 'Usuario',
            text: el.querySelector('[dir="auto"]')?.innerText || ''
        })).filter(c => c.text);
        result.itemCount += result.comments.length;
    }

    return result;
}

/**
 * Twitter/X Extraction
 */
function extractTwitter(options) {
    const result = {
        platform: 'twitter',
        title: '',
        description: '',
        hashtags: [],
        stats: { likes: 0, comments: 0, shares: 0, views: 0 },
        comments: [],
        author: '',
        itemCount: 0
    };

    // Main tweet
    const tweetEl = document.querySelector('[data-testid="tweetText"]');
    if (tweetEl) {
        result.description = tweetEl.innerText.trim();
        result.title = result.description.substring(0, 100);
        result.itemCount++;
    }

    // Author
    const authorEl = document.querySelector('[data-testid="User-Name"]');
    if (authorEl) {
        result.author = authorEl.innerText.split('\n')[0];
        result.itemCount++;
    }

    // Hashtags
    if (options.includeHashtags) {
        const hashtagLinks = document.querySelectorAll('a[href*="/hashtag/"]');
        result.hashtags = Array.from(hashtagLinks).map(el => el.innerText.trim());
    }

    // Stats
    if (options.includeStats) {
        const statsGroup = document.querySelector('[role="group"]');
        if (statsGroup) {
            const buttons = statsGroup.querySelectorAll('button');
            buttons.forEach(btn => {
                const label = btn.getAttribute('aria-label') || '';
                const num = parseStatNumber(label);
                if (label.includes('repl') || label.includes('comment')) result.stats.comments = num;
                if (label.includes('like') || label.includes('Me gusta')) result.stats.likes = num;
                if (label.includes('Retweet') || label.includes('repost')) result.stats.shares = num;
                if (label.includes('view')) result.stats.views = num;
            });
            result.itemCount++;
        }
    }

    // Comments (replies)
    if (options.includeComments) {
        const replyEls = document.querySelectorAll('article[data-testid="tweet"]');
        result.comments = Array.from(replyEls).slice(1, 15).map(el => {
            const userEl = el.querySelector('[data-testid="User-Name"]');
            const textEl = el.querySelector('[data-testid="tweetText"]');
            return {
                user: userEl?.innerText.split('\n')[0] || 'Usuario',
                text: textEl?.innerText || ''
            };
        }).filter(c => c.text);
        result.itemCount += result.comments.length;
    }

    return result;
}

/**
 * Instagram Extraction
 */
function extractInstagram(options) {
    const result = {
        platform: 'instagram',
        title: '',
        description: '',
        hashtags: [],
        stats: { likes: 0, comments: 0 },
        comments: [],
        author: '',
        itemCount: 0
    };

    // Caption
    const captionEl = document.querySelector('h1._ap3a') ||
        document.querySelector('span._ap3a');
    if (captionEl) {
        result.description = captionEl.innerText.trim();
        result.title = result.description.substring(0, 100);
        result.itemCount++;
    }

    // Author
    const authorEl = document.querySelector('header a._ap3a');
    if (authorEl) {
        result.author = authorEl.innerText.trim();
        result.itemCount++;
    }

    // Hashtags
    if (options.includeHashtags) {
        result.hashtags = (result.description.match(/#[\w]+/g) || []);
    }

    return result;
}

/**
 * YouTube Extraction
 */
function extractYouTube(options) {
    const result = {
        platform: 'youtube',
        title: '',
        description: '',
        hashtags: [],
        stats: { views: 0, likes: 0 },
        comments: [],
        author: '',
        itemCount: 0
    };

    // Title
    const titleEl = document.querySelector('h1.ytd-video-primary-info-renderer') ||
        document.querySelector('yt-formatted-string.ytd-video-primary-info-renderer');
    if (titleEl) {
        result.title = titleEl.innerText.trim();
        result.itemCount++;
    }

    // Description
    const descEl = document.querySelector('#description-inline-expander') ||
        document.querySelector('ytd-expander[slot="content"]');
    if (descEl) {
        result.description = descEl.innerText.substring(0, 500);
        result.itemCount++;
    }

    // Author
    const authorEl = document.querySelector('#owner-name a') ||
        document.querySelector('ytd-channel-name a');
    if (authorEl) {
        result.author = authorEl.innerText.trim();
        result.itemCount++;
    }

    // Stats
    if (options.includeStats) {
        const viewsEl = document.querySelector('#info-strings yt-formatted-string') ||
            document.querySelector('[class*="view-count"]');
        if (viewsEl) result.stats.views = parseStatNumber(viewsEl.innerText);

        const likesEl = document.querySelector('#segmented-like-button button');
        if (likesEl) result.stats.likes = parseStatNumber(likesEl.getAttribute('aria-label') || '0');
        result.itemCount++;
    }

    return result;
}

/**
 * LinkedIn Extraction
 */
function extractLinkedIn(options) {
    const result = {
        platform: 'linkedin',
        title: '',
        description: '',
        hashtags: [],
        stats: { likes: 0, comments: 0 },
        comments: [],
        author: '',
        itemCount: 0
    };

    // Post content
    const postEl = document.querySelector('.feed-shared-update-v2__description');
    if (postEl) {
        result.description = postEl.innerText.trim();
        result.title = result.description.substring(0, 100);
        result.itemCount++;
    }

    // Author
    const authorEl = document.querySelector('.feed-shared-actor__name');
    if (authorEl) {
        result.author = authorEl.innerText.trim();
        result.itemCount++;
    }

    // Hashtags
    if (options.includeHashtags) {
        result.hashtags = (result.description.match(/#[\w]+/g) || []);
    }

    return result;
}

/**
 * Generic Web Page Extraction
 */
function extractGeneric(options) {
    const result = {
        platform: 'generic',
        title: document.title,
        description: '',
        hashtags: [],
        stats: null,
        comments: [],
        author: '',
        itemCount: 1
    };

    // Meta description
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) {
        result.description = metaDesc.content;
        result.itemCount++;
    }

    // Article content
    const articleEl = document.querySelector('article') ||
        document.querySelector('[role="main"]') ||
        document.querySelector('main');
    if (articleEl && !result.description) {
        result.description = articleEl.innerText.substring(0, 1000);
        result.itemCount++;
    }

    return result;
}

/**
 * Parse stat numbers (1.2K, 5M, etc.)
 */
function parseStatNumber(str) {
    if (!str) return 0;
    const cleaned = str.replace(/[^0-9.KMB]/gi, '');
    const num = parseFloat(cleaned) || 0;

    if (cleaned.toUpperCase().includes('B')) return num * 1000000000;
    if (cleaned.toUpperCase().includes('M')) return num * 1000000;
    if (cleaned.toUpperCase().includes('K')) return num * 1000;
    return Math.round(num);
}

/**
 * Format extracted content for display
 */
function formatExtractedContent(data, options) {
    let text = `═══════════════════════════════════════════════════\n`;
    text += `📱 PLATAFORMA: ${data.platform.toUpperCase()}\n`;
    text += `═══════════════════════════════════════════════════\n\n`;

    if (data.author) {
        text += `👤 AUTOR: ${data.author}\n\n`;
    }

    if (options.includeTitle && data.title) {
        text += `📝 TÍTULO/POST:\n${data.description || data.title}\n\n`;
    }

    if (options.includeHashtags && data.hashtags.length > 0) {
        text += `#️⃣ HASHTAGS:\n${data.hashtags.join(' ')}\n\n`;
    }

    if (options.includeStats && data.stats) {
        text += `📊 ESTADÍSTICAS:\n`;
        if (data.stats.views) text += `   👁️ Vistas: ${formatNum(data.stats.views)}\n`;
        if (data.stats.likes) text += `   ❤️ Likes: ${formatNum(data.stats.likes)}\n`;
        if (data.stats.comments) text += `   💬 Comentarios: ${formatNum(data.stats.comments)}\n`;
        if (data.stats.shares) text += `   🔄 Compartidos: ${formatNum(data.stats.shares)}\n`;
        text += `\n`;
    }

    if (options.includeComments && data.comments.length > 0) {
        text += `💬 COMENTARIOS (${data.comments.length}):\n`;
        text += `───────────────────────────────────────────────────\n`;
        data.comments.forEach((c, i) => {
            text += `${i + 1}. @${c.user}: ${c.text.substring(0, 100)}\n`;
        });
        text += `\n`;
    }

    text += `═══════════════════════════════════════════════════\n`;

    return text;
}

function formatNum(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n.toString();
}
