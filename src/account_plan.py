from typing import Dict, List, Optional
from datetime import datetime


class AccountPlan:
    
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at
        self.sections = {
            "company_overview": "",
            "business_model": "",
            "key_products_services": "",
            "market_position": "",
            "financial_highlights": "",
            "opportunities": "",
            "challenges": "",
            "recommendations": "",
            "next_steps": ""
        }
        self.sources = []
    
    def update_section(self, section_name: str, content: str) -> bool:
        if section_name in self.sections:
            self.sections[section_name] = content
            self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
        return False
    
    def get_section(self, section_name: str) -> Optional[str]:
        return self.sections.get(section_name)
    
    def add_source(self, source: Dict[str, str]):
        self.sources.append(source)
    
    def to_markdown(self) -> str:
        md = f"# Account Plan: {self.company_name}\n\n"
        md += f"*Created: {self.created_at}*\n\n"
        
        section_titles = {
            "company_overview": "Company Overview",
            "business_model": "Business Model",
            "key_products_services": "Key Products & Services",
            "market_position": "Market Position",
            "financial_highlights": "Financial Highlights",
            "opportunities": "Opportunities",
            "challenges": "Challenges",
            "recommendations": "Recommendations",
            "next_steps": "Next Steps"
        }
        
        for section_key, section_title in section_titles.items():
            content = self.sections.get(section_key, "")
            if content:
                md += f"## {section_title}\n\n{content}\n\n"
        
        if self.sources:
            md += "## Sources\n\n"
            for i, source in enumerate(self.sources, 1):
                md += f"{i}. {source.get('title', 'Unknown')}\n"
            md += "\n"
        
        return md


class AccountPlanGenerator:
    
    def __init__(self, openai_client):
        self.client = openai_client
    
    def generate_plan(self, company_name: str, research_context: str, 
                     conflicts: List[str] = None) -> AccountPlan:
        plan = AccountPlan(company_name)
        
        system_prompt = """You are creating an account plan. Analyze the research and create sections:
1. Company Overview
2. Business Model
3. Key Products & Services
4. Market Position
5. Financial Highlights
6. Opportunities
7. Challenges
8. Recommendations
9. Next Steps

Be clear and factual. If info is missing, say so."""
        
        user_prompt = f"""Create an account plan for {company_name} based on this research:

{research_context}

Generate all sections based on the available information."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            plan_content = response.choices[0].message.content
            self._parse_plan_content(plan, plan_content)
            return plan
        except Exception as e:
            print(f"Error: {e}")
            return plan
    
    def _parse_plan_content(self, plan: AccountPlan, content: str):
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        section_map = {
            "company overview": "company_overview",
            "business model": "business_model",
            "products": "key_products_services",
            "market position": "market_position",
            "financial": "financial_highlights",
            "opportunities": "opportunities",
            "challenges": "challenges",
            "recommendations": "recommendations",
            "next steps": "next_steps"
        }
        
        for line in lines:
            line_lower = line.lower().strip()
            is_section = False
            
            for key, section_key in section_map.items():
                if key in line_lower and (line.startswith('#') or line_lower.startswith(key)):
                    if current_section and current_content:
                        plan.sections[current_section] = '\n'.join(current_content).strip()
                    current_section = section_key
                    current_content = []
                    is_section = True
                    break
            
            if not is_section and current_section:
                if line.strip():
                    current_content.append(line)
        
        if current_section and current_content:
            plan.sections[current_section] = '\n'.join(current_content).strip()
        
        if not any(plan.sections.values()):
            plan.sections["company_overview"] = content
