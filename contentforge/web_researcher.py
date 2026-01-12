"""
Web Researcher for ContentForge AI
Uses DuckDuckGo for web searching and content analysis
"""

import logging
from typing import Dict, List, Optional
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


class WebResearcher:
    """Performs web research using DuckDuckGo search."""
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search the web using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results with title, url, body
        """
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
        """
        Search for social media content.
        
        Args:
            platform: 'facebook', 'twitter', 'linkedin', etc.
            query: Search query
            max_results: Maximum results
        """
        platform_queries = {
            "facebook": f"site:facebook.com {query}",
            "twitter": f"site:twitter.com OR site:x.com {query}",
            "linkedin": f"site:linkedin.com {query}",
            "instagram": f"site:instagram.com {query}",
            "youtube": f"site:youtube.com {query}",
        }
        
        search_query = platform_queries.get(platform, f"{platform} {query}")
        return self.search(search_query, max_results)
    
    def analyze_url_content(self, url: str) -> Optional[Dict]:
        """
        Get information about a specific URL via search.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dict with analysis results or None
        """
        try:
            # Search for the specific URL
            results = list(self.ddgs.text(f"site:{url}", max_results=5))
            
            if results:
                return {
                    "url": url,
                    "found_content": results,
                    "total_results": len(results)
                }
            return {"url": url, "found_content": [], "total_results": 0}
        except Exception as e:
            logger.error(f"URL analysis error: {e}")
            return None
    
    def get_trending_topics(self, niche: str = "cybersecurity", region: str = "es-mx") -> List[Dict]:
        """
        Find trending topics in a specific niche.
        
        Args:
            niche: Topic area (e.g., 'cybersecurity', 'hacking', 'tech')
            region: Region code
        """
        queries = [
            f"{niche} trending 2024",
            f"{niche} noticias recientes",
            f"{niche} viral",
        ]
        
        all_results = []
        for query in queries:
            results = self.search(query, max_results=5)
            all_results.extend(results)
        
        return all_results[:10]  # Return top 10
    
    def research_competition(self, topic: str, platforms: List[str] = None) -> Dict:
        """
        Research what competitors are posting about a topic.
        
        Args:
            topic: Topic to research
            platforms: List of platforms to search
        """
        if platforms is None:
            platforms = ["facebook", "twitter", "linkedin"]
        
        results = {}
        for platform in platforms:
            results[platform] = self.search_social(platform, topic, max_results=5)
        
        return results
    
    def find_engagement_patterns(self, query: str) -> Dict:
        """
        Find posts with high engagement patterns.
        
        Args:
            query: Topic to analyze
        """
        engagement_keywords = [
            f"{query} viral post",
            f"{query} trending discussion",
            f"{query} popular thread",
        ]
        
        results = []
        for kw in engagement_keywords:
            results.extend(self.search(kw, max_results=5))
        
        return {
            "query": query,
            "high_engagement_content": results[:10],
            "total_found": len(results)
        }


# Convenience function
def get_web_researcher() -> WebResearcher:
    """Get a WebResearcher instance."""
    return WebResearcher()
