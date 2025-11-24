import requests
from typing import List, Dict
from bs4 import BeautifulSoup
import os


class LinkedInAgent:
    
    def __init__(self):
        pass
    
    def search_company(self, company_name: str) -> List[Dict[str, str]]:
        try:
            url = f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                description = ""
                desc_elem = soup.find('meta', {'property': 'og:description'})
                if desc_elem:
                    description = desc_elem.get('content', '')
                
                title = company_name
                title_elem = soup.find('title')
                if title_elem:
                    title = title_elem.text.strip()
                
                if description or title != company_name:
                    return [{
                        "title": title,
                        "description": description[:500] if description else "Company information from LinkedIn",
                        "url": url,
                        "source": "LinkedIn"
                    }]
            
            return []
        except Exception as e:
            return []
    
    def get_company_info(self, company_name: str) -> Dict[str, str]:
        results = self.search_company(company_name)
        if results:
            return results[0]
        return {
            "title": company_name,
            "description": "",
            "url": f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}",
            "source": "LinkedIn"
        }

