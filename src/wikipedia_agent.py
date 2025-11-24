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
        print("<=====Initializing Wikipedia Agent=====>")
        print("Setting up Wikipedia API client")
        print()
        print("Wikipedia Agent initialized successfully")
        print()

    def query(self, query: str) -> List[Dict[str, Any]]:
        print("<=====Querying Wikipedia API=====>")
        print(f"Searching Wikipedia for query: {query}")
        print()
        import wikipedia
        try:
            page_titles = wikipedia.search(query, results=5)
            print(f"Found {len(page_titles)} Wikipedia page titles")
            print()
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
                except Exception as e:
                    print(f"Error fetching page '{title}': {e}")
                    continue
            print(f"Retrieved {len(raw_results)} Wikipedia pages")
            print()
        except Exception as e:
            print(f"Error querying Wikipedia: {e}")
            print()
            raw_results = []
        return self.parse_results(raw_results)

    def parse_results(self, raw_results: Any) -> List[Dict[str, Any]]:
        print("<=====Parsing Wikipedia Results=====>")
        results = []
        for page in raw_results:
            results.append({
                "title": getattr(page, "title", None),
                "url": getattr(page, "url", None),
                "summary": getattr(page, "summary", None)
            })
        print(f"Parsed {len(results)} Wikipedia results")
        print()
        return results 
    
    def get_multiple_sources(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.query(query)
            return results[:limit]
        except Exception as e:
            print(f"Error in get_multiple_sources: {e}")
            return []
