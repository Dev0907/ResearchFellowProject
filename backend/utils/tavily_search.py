"""
Tavily search integration for competitive intelligence and market research
"""
from tavily import TavilyClient
import os
from typing import List, Dict, Optional

class TavilySearch:
    """
    Wrapper for Tavily API to perform web searches and research
    """
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY", "")
        self.client = TavilyClient(api_key=self.api_key)
    
    def search_competitors(self, startup_idea: str, max_results: int = 5) -> List[Dict]:
        """
        Search for competitors based on startup idea
        """
        try:
            query = f"startups similar to {startup_idea} competitors alternatives"
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []
    
    def search_market_trends(self, industry: str, max_results: int = 5) -> List[Dict]:
        """
        Search for market trends and insights
        """
        try:
            query = f"{industry} market trends 2026 growth analysis"
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []
    
    def research_topic(self, topic: str, max_results: int = 3) -> str:
        """
        Deep research on a specific topic
        """
        try:
            response = self.client.search(
                query=topic,
                search_depth="advanced",
                max_results=max_results
            )
            
            # Compile research summary
            results = response.get("results", [])
            summary = f"Research on: {topic}\n\n"
            
            for idx, result in enumerate(results, 1):
                summary += f"{idx}. {result.get('title', 'N/A')}\n"
                summary += f"   {result.get('content', 'N/A')[:200]}...\n"
                summary += f"   Source: {result.get('url', 'N/A')}\n\n"
            
            return summary
        except Exception as e:
            return f"Research error: {str(e)}"
    
    def get_context(self, query: str) -> str:
        """
        Get contextual information for a query
        """
        try:
            response = self.client.get_search_context(query=query)
            return response
        except Exception as e:
            return f"Context retrieval error: {str(e)}"
