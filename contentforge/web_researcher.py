"""
Web Researcher for ContentForge AI
Uses DuckDuckGo for web searching and content analysis
"""

import logging
import re
from typing import Dict, List, Optional
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


class WebResearcher:
    """Performs web research using DuckDuckGo search."""
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search the web using DuckDuckGo."""
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            logger.info(f"Found {len(results)} results for: {query}")
            return results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def search_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for recent news articles."""
        try:
            results = list(self.ddgs.news(query, max_results=max_results))
            return results
        except Exception as e:
            logger.error(f"News search error: {e}")
            return []
    
    def search_social(self, platform: str, query: str, max_results: int = 10) -> List[Dict]:
        """Search for social media content."""
        platform_queries = {
            "facebook": f"site:facebook.com {query}",
            "twitter": f"site:twitter.com OR site:x.com {query}",
            "linkedin": f"site:linkedin.com {query}",
            "instagram": f"site:instagram.com {query}",
            "youtube": f"site:youtube.com {query}",
        }
        
        search_query = platform_queries.get(platform, f"{platform} {query}")
        return self.search(search_query, max_results)
    
    def research_facebook_group(self, group_name: str, group_url: str) -> Dict:
        """
        Research content related to a Facebook group topic.
        
        NOTE: DuckDuckGo cannot access private Facebook group posts directly.
        This method searches for PUBLIC content related to the group's topic.
        
        Args:
            group_name: Name/topic of the group
            group_url: URL of the Facebook group
            
        Returns:
            Dict with research results and related posts
        """
        # Clean up the group name for better search
        clean_name = re.sub(r'[^\w\s]', '', group_name).strip()
        
        # Multiple search strategies for best results
        search_queries = [
            # Public Facebook posts on the topic
            f"site:facebook.com {clean_name} posts",
            # Related forum discussions
            f"{clean_name} tutorial mejores posts",
            # Reddit discussions on same topic
            f"site:reddit.com {clean_name}",
            # YouTube content
            f"site:youtube.com {clean_name} tutorial",
            # Forums and communities
            f"{clean_name} comunidad foro discusion",
        ]
        
        all_results = []
        for query in search_queries[:3]:  # Limit to 3 queries
            results = self.search(query, max_results=5)
            all_results.extend(results)
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_results = []
        for r in all_results:
            url = r.get('href', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)
        
        return {
            "group_name": group_name,
            "group_url": group_url,
            "topic": clean_name,
            "related_posts": unique_results[:10],
            "note": "⚠️ Los posts de grupos privados de Facebook no son accesibles públicamente. Estos resultados son contenido público relacionado al tema del grupo."
        }
    
    def find_trending_content(self, topic: str, language: str = "es") -> List[Dict]:
        """Find trending content on a topic in Spanish."""
        queries = [
            f"{topic} viral 2025",
            f"{topic} tendencia",
            f"{topic} popular post",
            f"{topic} mejores tips",
        ]
        
        all_results = []
        for query in queries[:2]:
            results = self.search(query, max_results=5)
            all_results.extend(results)
        
        return all_results[:8]
    
    def find_engagement_patterns(self, query: str) -> Dict:
        """Find posts with high engagement."""
        engagement_keywords = [
            f"{query} viral post facebook",
            f"{query} trending discussion",
            f"{query} comentarios populares",
        ]
        
        results = []
        for kw in engagement_keywords:
            results.extend(self.search(kw, max_results=5))
        
        return {
            "query": query,
            "high_engagement_content": results[:10],
            "total_found": len(results)
        }
    
    def get_topic_ideas(self, niche: str) -> List[Dict]:
        """Get content ideas for a niche."""
        queries = [
            f"{niche} ideas de contenido",
            f"{niche} que publicar",
            f"{niche} posts virales ejemplos",
        ]
        
        results = []
        for q in queries:
            results.extend(self.search(q, max_results=3))
        
        return results[:8]


def get_web_researcher() -> WebResearcher:
    """Get a WebResearcher instance."""
    return WebResearcher()

