from abc import ABC, abstractmethod
from typing import List, Dict, Any

class WikipediaAgentInterface(ABC):

    @abstractmethod
    def query(self, query: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def parse_results(self, raw_results: Any) -> List[Dict[str, Any]]:
        pass

class WikipediaAgent(WikipediaAgentInterface):
    def __init__(self):
        pass

    def query(self, query: str) -> List[Dict[str, Any]]:
        import wikipedia
        try:
            page_titles = wikipedia.search(query, results=5)
            raw_results = []
            for title in page_titles:
                try:
                    page = wikipedia.page(title)
                    raw_results.append(page)
                except wikipedia.exceptions.DisambiguationError as e:
                    try:
                        page = wikipedia.page(e.options[0])
                        raw_results.append(page)
                    except:
                        continue
                except Exception:
                    continue
        except Exception:
            raw_results = []
        return self.parse_results(raw_results)

    def parse_results(self, raw_results: Any) -> List[Dict[str, Any]]:
        results = []
        for page in raw_results:
            results.append({
                "title": getattr(page, "title", None),
                "url": getattr(page, "url", None),
                "summary": getattr(page, "summary", None)
            })
        return results 
    
    def get_multiple_sources(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.query(query)
            return results[:limit]
        except Exception:
            return []
