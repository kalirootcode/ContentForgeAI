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
 * TikTok Extraction - Enhanced with multiple fallback selectors
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

    // Try to get author from multiple sources
    const authorSelectors = [
        '[data-e2e="browse-username"]',
        '[data-e2e="user-title"]',
        'h3[data-e2e="user-title"]',
        'a[href*="/@"] span',
        '[class*="SpanAuthorNickname"]',
        '[class*="DivAuthorContainer"] span',
        'span[data-e2e="browse-username"]'
    ];

    for (const sel of authorSelectors) {
        const el = document.querySelector(sel);
        if (el && el.innerText && el.innerText.length > 1) {
            result.author = el.innerText.trim();
            result.itemCount++;
            break;
        }
    }

    // Video description - try multiple selectors
    const descSelectors = [
        '[data-e2e="browse-video-desc"]',
        '[data-e2e="video-desc"]',
        '[class*="DivBrowserModeContainer"] [class*="SpanText"]',
        '[class*="DivDescriptionContainer"]',
        'div[class*="VideoDetail"] span[class*="SpanText"]',
        'h1[data-e2e="browse-video-desc"]',
        'div[class*="ContentDesc"]',
        // Fallback: look for any large text block near the video
        'main span[dir="auto"]'
    ];

    for (const sel of descSelectors) {
        const el = document.querySelector(sel);
        if (el && el.innerText && el.innerText.length > 10 && !el.innerText.includes('Buscar')) {
            result.description = el.innerText.trim();
            result.title = result.description.split('\n')[0].substring(0, 100);
            result.itemCount++;
            break;
        }
    }

    // If no description found, try to get from meta tags
    if (!result.description) {
        const metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc && metaDesc.content) {
            result.description = metaDesc.content;
            result.title = result.description.substring(0, 100);
            result.itemCount++;
        }
    }

    // If still no description, try document title
    if (!result.description && document.title) {
        const titleMatch = document.title.match(/(.+?) \| TikTok/);
        if (titleMatch) {
            result.description = titleMatch[1];
            result.title = titleMatch[1];
            result.itemCount++;
        }
    }

    // Hashtags - multiple methods
    if (options.includeHashtags) {
        // Method 1: Links to /tag/
        const hashtagLinks = document.querySelectorAll('a[href*="/tag/"]');
        if (hashtagLinks.length > 0) {
            result.hashtags = Array.from(hashtagLinks)
                .map(el => el.innerText.trim())
                .filter(h => h.startsWith('#') || h.length > 0)
                .map(h => h.startsWith('#') ? h : '#' + h);
        }

        // Method 2: Extract from description
        if (result.hashtags.length === 0 && result.description) {
            const hashMatches = result.description.match(/#[\w\u00C0-\u024F]+/g);
            if (hashMatches) {
                result.hashtags = hashMatches;
            }
        }

        // Method 3: Look for hashtag elements
        if (result.hashtags.length === 0) {
            const hashEls = document.querySelectorAll('[class*="HashTag"], [class*="hashtag"]');
            result.hashtags = Array.from(hashEls).map(el => el.innerText.trim()).filter(h => h);
        }

        if (result.hashtags.length > 0) result.itemCount += result.hashtags.length;
    }

    // Stats - enhanced selectors
    if (options.includeStats) {
        const statsSelectors = {
            likes: ['[data-e2e="like-count"]', '[data-e2e="browse-like-count"]', 'strong[data-e2e="like-count"]'],
            comments: ['[data-e2e="comment-count"]', '[data-e2e="browse-comment-count"]'],
            shares: ['[data-e2e="share-count"]', '[data-e2e="undefined-count"]'],
            views: ['[data-e2e="video-views"]', 'strong[data-e2e="video-views"]']
        };

        for (const [stat, selectors] of Object.entries(statsSelectors)) {
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el && el.innerText) {
                    result.stats[stat] = parseStatNumber(el.innerText);
                    break;
                }
            }
        }
        result.itemCount++;
    }

    // Comments
    if (options.includeComments) {
        const commentSelectors = [
            '[data-e2e="comment-item"]',
            '[class*="DivCommentItemContainer"]',
            '[class*="CommentItem"]'
        ];

        for (const sel of commentSelectors) {
            const commentEls = document.querySelectorAll(sel);
            if (commentEls.length > 0) {
                result.comments = Array.from(commentEls).slice(0, 20).map(el => {
                    const userEl = el.querySelector('[data-e2e="comment-username"]') ||
                        el.querySelector('a[href*="/@"]') ||
                        el.querySelector('span[class*="UserName"]');
                    const textEl = el.querySelector('[data-e2e="comment-text"]') ||
                        el.querySelector('p') ||
                        el.querySelector('span[class*="SpanComment"]');
                    return {
                        user: userEl?.innerText.trim() || 'Usuario',
                        text: textEl?.innerText.trim() || ''
                    };
                }).filter(c => c.text);
                result.itemCount += result.comments.length;
                break;
            }
        }
    }

    // Log for debugging
    console.log('TikTok Extraction Result:', result);

    return result;
}

/**
 * Facebook Extraction - Enhanced with multiple fallback selectors
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

    // Post content - try multiple selectors
    const postSelectors = [
        '[data-ad-preview="message"]',
        '[data-testid="post_message"]',
        'div[dir="auto"][data-ad-comet-preview="message"]',
        'div.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1vvkbs span[dir="auto"]',
        'span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x6prxxf.xvq8zen.xo1l8bm.xzsf02u',
        '[class*="userContent"]',
        'div[data-ad-preview="message"]',
        // Generic: any text block in a post
        'div[role="article"] div[dir="auto"]'
    ];

    for (const sel of postSelectors) {
        try {
            const elements = document.querySelectorAll(sel);
            for (const el of elements) {
                const text = el.innerText?.trim();
                if (text && text.length > 20 && !text.includes('Me gusta') && !text.includes('Comentar')) {
                    result.description = text;
                    result.title = text.substring(0, 100);
                    result.itemCount++;
                    break;
                }
            }
            if (result.description) break;
        } catch (e) { }
    }

    // If no description, try meta
    if (!result.description) {
        const metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc?.content) {
            result.description = metaDesc.content;
            result.title = result.description.substring(0, 100);
            result.itemCount++;
        }
    }

    // Author - try multiple selectors
    const authorSelectors = [
        'h2 a[role="link"]',
        'strong a[role="link"]',
        'a.x1i10hfl.xjbqb8w.x6umber.x1ejq31n strong',
        'span.xt0psk2 a',
        'a[aria-label][role="link"] span',
        'h3 a[role="link"]',
        'div[role="article"] h2 a'
    ];

    for (const sel of authorSelectors) {
        try {
            const el = document.querySelector(sel);
            if (el && el.innerText && el.innerText.length > 1) {
                result.author = el.innerText.trim();
                result.itemCount++;
                break;
            }
        } catch (e) { }
    }

    // Hashtags - extract from description
    if (options.includeHashtags && result.description) {
        const hashtagMatches = result.description.match(/#[\w\u00C0-\u024F]+/g) || [];
        result.hashtags = hashtagMatches;
        if (result.hashtags.length > 0) result.itemCount += result.hashtags.length;
    }

    // Stats - reactions, comments, shares
    if (options.includeStats) {
        // Reactions/Likes
        const reactionSelectors = [
            '[aria-label*="reaccion"]',
            '[aria-label*="reaction"]',
            '[aria-label*="Me gusta"]',
            '[aria-label*="Like"]',
            'span.x1rg5ohu span'
        ];

        for (const sel of reactionSelectors) {
            const el = document.querySelector(sel);
            if (el) {
                const label = el.getAttribute('aria-label') || el.innerText;
                if (label) {
                    result.stats.likes = parseStatNumber(label);
                    break;
                }
            }
        }

        // Comments count
        const commentCountEls = document.querySelectorAll('span[dir="auto"]');
        for (const el of commentCountEls) {
            const text = el.innerText;
            if (text && (text.includes('comentario') || text.includes('comment'))) {
                result.stats.comments = parseStatNumber(text);
                break;
            }
        }

        // Shares count
        for (const el of commentCountEls) {
            const text = el.innerText;
            if (text && (text.includes('veces compartido') || text.includes('share'))) {
                result.stats.shares = parseStatNumber(text);
                break;
            }
        }

        result.itemCount++;
    }

    // Comments
    if (options.includeComments) {
        const commentContainers = [
            'div[aria-label*="Comentario"]',
            'div[aria-label*="Comment"]',
            'ul li[class*="Comment"]',
            'div[role="article"] div[role="article"]'
        ];

        for (const sel of commentContainers) {
            const commentEls = document.querySelectorAll(sel);
            if (commentEls.length > 0) {
                result.comments = Array.from(commentEls).slice(0, 15).map(el => {
                    const userEl = el.querySelector('a[role="link"]') || el.querySelector('a');
                    const textEl = el.querySelector('div[dir="auto"]') || el.querySelector('span[dir="auto"]');
                    return {
                        user: userEl?.innerText?.trim() || 'Usuario',
                        text: textEl?.innerText?.trim() || ''
                    };
                }).filter(c => c.text && c.text.length > 2);
                result.itemCount += result.comments.length;
                break;
            }
        }
    }

    // Log for debugging
    console.log('Facebook Extraction Result:', result);

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
