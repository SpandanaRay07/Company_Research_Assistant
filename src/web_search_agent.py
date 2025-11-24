import requests
from typing import List, Dict
from bs4 import BeautifulSoup
import urllib.parse


class WebSearchAgent:
    
    def __init__(self):
        pass
    
    def search_company(self, company_name: str, max_results: int = 5) -> List[Dict[str, str]]:
        try:
            query = f"{company_name} company"
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                result_links = soup.find_all('a', class_='result__a', limit=max_results)
                
                for link in result_links:
                    title = link.text.strip()
                    url = link.get('href', '')
                    
                    snippet = ""
                    result_div = link.find_parent('div', class_='result')
                    if result_div:
                        snippet_elem = result_div.find('a', class_='result__snippet')
                        if snippet_elem:
                            snippet = snippet_elem.text.strip()
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "description": snippet[:300] if snippet else "",
                            "url": url,
                            "source": "Web Search"
                        })
                
                return results
        except Exception as e:
            pass
        
        return []
    
    def search_with_query(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []
                
                result_links = soup.find_all('a', class_='result__a', limit=max_results)
                
                for link in result_links:
                    title = link.text.strip()
                    url = link.get('href', '')
                    
                    snippet = ""
                    result_div = link.find_parent('div', class_='result')
                    if result_div:
                        snippet_elem = result_div.find('a', class_='result__snippet')
                        if snippet_elem:
                            snippet = snippet_elem.text.strip()
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "description": snippet[:300] if snippet else "",
                            "url": url,
                            "source": "Web Search"
                        })
                
                return results
        except Exception as e:
            pass
        
        return []

