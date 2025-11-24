import os
from typing import Optional, Dict, List, Callable
from openai import OpenAI
from .wikipedia_agent import WikipediaAgent
from .news_agent import NewsAgent
from .linkedin_agent import LinkedInAgent
from .web_search_agent import WebSearchAgent


class CompanyResearchAgent:
    
    def __init__(self, openai_api_key: Optional[str] = None):
        if openai_api_key:
            self.api_key = openai_api_key
        else:
            self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it in .env file, environment variable, or pass as argument.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.wikipedia_agent = WikipediaAgent()
        self.news_agent = NewsAgent()
        self.linkedin_agent = LinkedInAgent()
        self.web_search_agent = WebSearchAgent()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def format_sources_context(self, wikipedia_sources: List[Dict[str, str]], news_sources: List[Dict[str, str]] = None, linkedin_source: Dict[str, str] = None, web_sources: List[Dict[str, str]] = None) -> str:
        context_parts = []
        
        if wikipedia_sources:
            context_parts.append("=== WIKIPEDIA SOURCES ===")
            for i, source in enumerate(wikipedia_sources, 1):
                title = source.get('title', 'Unknown')
                summary = source.get('summary', 'No summary available')
                url = source.get('url', 'N/A')
                context_parts.append(f"Wikipedia Source {i}: {title}")
                context_parts.append(f"Summary: {summary}")
                context_parts.append(f"URL: {url}")
                context_parts.append("")
        
        if news_sources:
            context_parts.append("=== NEWS SOURCES ===")
            for i, article in enumerate(news_sources, 1):
                context_parts.append(f"News Article {i}: {article.get('title', 'Unknown')}")
                context_parts.append(f"Source: {article.get('source', 'Unknown')}")
                context_parts.append(f"Description: {article.get('description', 'No description')}")
                if article.get('content'):
                    context_parts.append(f"Content: {article.get('content', '')}")
                context_parts.append(f"URL: {article.get('url', 'N/A')}")
                context_parts.append("")
        
        if linkedin_source:
            context_parts.append("=== LINKEDIN SOURCE ===")
            context_parts.append(f"Company: {linkedin_source.get('title', 'Unknown')}")
            context_parts.append(f"Description: {linkedin_source.get('description', 'No description')}")
            context_parts.append(f"URL: {linkedin_source.get('url', 'N/A')}")
            context_parts.append("")
        
        if web_sources:
            context_parts.append("=== WEB SEARCH RESULTS ===")
            for i, result in enumerate(web_sources, 1):
                context_parts.append(f"Web Result {i}: {result.get('title', 'Unknown')}")
                context_parts.append(f"Description: {result.get('description', 'No description')}")
                context_parts.append(f"URL: {result.get('url', 'N/A')}")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def detect_conflicts(self, wikipedia_sources: List[Dict[str, str]], news_sources: List[Dict[str, str]] = None, linkedin_source: Dict[str, str] = None) -> List[str]:
        conflicts = []
        
        if len(wikipedia_sources) > 1:
            titles = [s.get('title', '') for s in wikipedia_sources]
            if len(set(titles)) < len(titles):
                conflicts.append("Multiple Wikipedia pages with similar names found")
        
        all_texts = []
        if wikipedia_sources:
            all_texts.append(('Wikipedia', ' '.join([s.get('summary', '')[:200] for s in wikipedia_sources[:2] if s.get('summary')])))
        if news_sources:
            all_texts.append(('News', ' '.join([a.get('description', '')[:200] for a in news_sources[:2] if a.get('description')])))
        if linkedin_source and linkedin_source.get('description'):
            all_texts.append(('LinkedIn', linkedin_source.get('description', '')[:200]))
        
        if len(all_texts) >= 2:
            try:
                sources_text = '\n'.join([f"{name}: {text}" for name, text in all_texts if text])
                conflict_check = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Check if sources conflict. Reply 'CONFLICT: [what conflicts]' or 'NO_CONFLICT'."},
                        {"role": "user", "content": f"{sources_text}\n\nAny conflicts?"}
                    ],
                    temperature=0.3,
                    max_tokens=150
                )
                result = conflict_check.choices[0].message.content
                if "CONFLICT:" in result:
                    conflict_desc = result.replace("CONFLICT:", "").strip()
                    conflicts.append(conflict_desc)
            except:
                pass
        
        return conflicts
    
    def dig_deeper(self, company_name: str, conflict_topic: str) -> Dict[str, str]:
        print(f"\n🔍 Digging deeper into: {conflict_topic}")
        
        additional_wiki = self.wikipedia_agent.get_multiple_sources(f"{company_name} {conflict_topic}", limit=2)
        additional_news = []
        if self.news_agent.is_available():
            additional_news = self.news_agent.search_company_news(f"{company_name} {conflict_topic}", max_results=2)
        
        context = self.format_sources_context(additional_wiki, additional_news)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You're a friendly research assistant helping clarify conflicting information. Be helpful, clear, and reassuring. Explain the situation in a friendly, easy-to-understand way."},
                    {"role": "user", "content": f"Company: {company_name}\nThere's some conflicting information about: {conflict_topic}\n\nI found additional research:\n{context}\n\nPlease help clarify this in a friendly, helpful way."}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return {
                'success': True,
                'clarification': response.choices[0].message.content,
                'sources': additional_wiki + additional_news
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def research_company(self, query: str, use_multiple_sources: bool = True, ask_user_callback=None, voice_mode: bool = False) -> Dict[str, any]:
        company_name = self._extract_company_name(query)
        
        print("🔍 Let me gather information from multiple sources...")
        if use_multiple_sources:
            wikipedia_sources = self.wikipedia_agent.get_multiple_sources(company_name, limit=3)
        else:
            results = self.wikipedia_agent.get_multiple_sources(company_name, limit=1)
            wikipedia_sources = results if results else []
        
        news_sources = []
        if self.news_agent.is_available():
            news_sources = self.news_agent.search_company_news(company_name, max_results=3)
        
        linkedin_source = None
        try:
            linkedin_info = self.linkedin_agent.get_company_info(company_name)
            if linkedin_info.get('description'):
                linkedin_source = linkedin_info
        except:
            pass
        
        web_sources = self.web_search_agent.search_company(company_name, max_results=5)
        
        if not wikipedia_sources and not news_sources and not linkedin_source and not web_sources:
            return {
                'success': False,
                'error': f"Could not find information about '{company_name}' from any source.",
                'response': None,
                'sources': []
            }
        
        conflicts = self.detect_conflicts(wikipedia_sources, news_sources, linkedin_source)
        
        deeper_research = None
        if conflicts and ask_user_callback:
            print("\nHmm, I noticed some conflicting information while researching:")
            for i, conflict in enumerate(conflicts, 1):
                print(f"   {i}. {conflict}")
            print("\nWould you like me to dig a bit deeper to clarify this? (yes/no)")
            response = ask_user_callback("Your answer: ").strip().lower()
            if response in ['yes', 'y']:
                if len(conflicts) == 1:
                    deeper_research = self.dig_deeper(company_name, conflicts[0])
                else:
                    print("\nWhich one would you like me to look into? (enter the number)")
                    choice = ask_user_callback("Your choice: ").strip()
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(conflicts):
                            deeper_research = self.dig_deeper(company_name, conflicts[idx])
                    except:
                        deeper_research = self.dig_deeper(company_name, conflicts[0])
        
        context = self.format_sources_context(wikipedia_sources, news_sources, linkedin_source, web_sources)
        
        if deeper_research and deeper_research.get('success'):
            context += f"\n\n=== ADDITIONAL RESEARCH (Digging Deeper) ===\n{deeper_research.get('clarification', '')}\n"
            conflicts = []
        
        conflict_note = ""
        if conflicts:
            conflict_note = f"\n\nNote: The following conflicts were detected: {'; '.join(conflicts)}"
        
        if voice_mode:
            system_prompt = """You are a friendly and knowledgeable company research assistant. You help people learn about companies in a conversational, engaging way. When answering:
- Be warm, friendly, and approachable
- Use natural, conversational language (like talking to a friend)
- Keep your response SHORT and CONCISE (2-3 sentences maximum)
- Focus on the most important information only
- This will be read aloud, so keep it brief and clear
- If you find conflicting information, mention it briefly
- Always be helpful and encouraging"""
        else:
            system_prompt = """You are a friendly and knowledgeable company research assistant. You help people learn about companies in a conversational, engaging way. When answering:
- Be warm, friendly, and approachable
- Use natural, conversational language (like talking to a friend)
- Show enthusiasm about interesting facts
- Break down complex information into easy-to-understand points
- Use emojis sparingly when appropriate (but not too many)
- Make the information interesting and engaging
- If you find conflicting information, mention it in a helpful, non-alarming way
- Always be helpful and encouraging"""
        
        if voice_mode:
            user_prompt = f"""User asked: {query}

I've gathered information from multiple sources:
{context}
{conflict_note}

Please provide a SHORT, friendly answer (2-3 sentences max) that:
- Directly addresses what they asked
- Focuses on the most important information only
- This will be read aloud, so keep it brief and clear"""
        else:
            user_prompt = f"""User asked: {query}

I've gathered information from multiple sources:
{context}
{conflict_note}

Please provide a friendly, conversational answer that:
- Directly addresses what they asked
- Includes interesting and relevant details from all sources
- Feels like a natural conversation
- Makes the information easy to understand and engaging"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content
            
            all_sources = wikipedia_sources + news_sources + web_sources
            if linkedin_source:
                all_sources.append(linkedin_source)
            if deeper_research and deeper_research.get('sources'):
                all_sources.extend(deeper_research.get('sources', []))
            
            return {
                'success': True,
                'query': query,
                'company_name': company_name,
                'wikipedia_sources': wikipedia_sources,
                'news_sources': news_sources,
                'linkedin_source': linkedin_source,
                'web_sources': web_sources,
                'sources': all_sources,
                'response': answer,
                'sources_count': len(all_sources),
                'conflicts': conflicts,
                'deeper_research': deeper_research
            }
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
                detailed_error = "OpenAI API quota exceeded. Please check:\n"
            else:
                detailed_error = f"OpenAI API Error: {error_msg}"
            
            return {
                'success': False,
                'error': detailed_error,
                'response': None,
                'sources': []
            }
    
    def _extract_company_name(self, query: str) -> str:
        query_lower = query.lower()
        company_name = query
        
        remove_phrases = [
            "tell me about",
            "what is",
            "who is",
            "information about",
            "details about",
            "research",
            "find information about",
            "tell me",
            "about"
        ]
        
        for phrase in remove_phrases:
            if query_lower.startswith(phrase):
                company_name = query[len(phrase):].strip()
                query_lower = company_name.lower()
                break
        
        company_name = company_name.rstrip("?.,! ")
        if company_name.lower().endswith(" company"):
            company_name = company_name[:-8].strip()
        
        company_name = " ".join(company_name.split())
        
        if not company_name:
            return query
        
        return company_name
