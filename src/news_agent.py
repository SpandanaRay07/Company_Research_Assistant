import requests
from typing import List, Dict
import os


class NewsAgent:
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    def search_company_news(self, company_name: str, max_results: int = 3) -> List[Dict[str, str]]:
        if not self.is_available():
            return []
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": company_name,
                "sortBy": "relevancy",
                "pageSize": max_results,
                "apiKey": self.api_key,
                "language": "en"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get("articles", [])[:max_results]:
                articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", "")[:500] if article.get("content") else "",
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "publishedAt": article.get("publishedAt", "")
                })
            
            return articles
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

