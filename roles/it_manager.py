from typing import Dict
from pydantic import Field
from .base_role import BaseRole

class ITManagerRole(BaseRole):
    @property
    def role_name(self) -> str:
        return "IT Manager"
    
    @property
    def prompt_template(self) -> str:
        return """You are an expert resume analyzer for IT Manager positions. 
        Analyze the resume text and extract key information about the candidate's qualifications.
        
        For each dimension, provide specific evidence from the resume that supports your assessment.
        Be objective and thorough in your analysis."""
    
    @property
    def analysis_model_fields(self) -> Dict[str, tuple]:
        return {
            'english_proficiency': (str, Field(description="English proficiency level (Proficient/OK/No signal). Proficient: clear signals of using English as working language (English resume, worked in English speaking firms, study abroad in English speaking countries, English certifications like TOEFL/IELTS). OK: signals of working with English docs, compliance frameworks, and tools. No signal: no English exposure evidence.")),
            'english_evidence': (str, Field(description="Evidence from resume supporting English proficiency assessment")),
            
            'communication_skill': (str, Field(description="Assessment of ability to work with diverse non-technical stakeholders and translate business languages into technical solutions")),
            'communication_evidence': (str, Field(description="Evidence from resume supporting communication skill assessment")),
            
            'us_saas_familiarity': (str, Field(description="Familiarity with US SaaS (High/Low/No signal). High: worked in companies using US SaaS like Slack, MSFT Team, Google Workspace, Jira. Low: only worked with China (dealbreaker). No signal: no clear indication.")),
            'us_saas_evidence': (str, Field(description="Evidence from resume supporting US SaaS familiarity assessment")),
            
            'technical_breadth': (str, Field(description="Technical domain breadth (High/Medium/Low). High: has Endpoint Management, IAM & SSO, VPN & Network, and more IT domains. Medium: some of these domains. Low: none of these domains.")),
            'technical_breadth_evidence': (str, Field(description="Evidence from resume supporting technical breadth assessment")),
            
            'architecture_capability': (str, Field(description="Assessment of ability to think and design on system/architecture level vs only implementing others' designs")),
            'architecture_evidence': (str, Field(description="Evidence from resume supporting architecture capability assessment")),
            
            'it_operation': (str, Field(description="Efficient IT operation capability (High/Medium/Low). High: experience running help desk, building knowledge base, automating with Python/AI/low-code tools. Medium: some of these. Low: none of these.")),
            'it_operation_evidence': (str, Field(description="Evidence from resume supporting IT operation assessment")),
            
            'project_leadership': (str, Field(description="Assessment of experience leading complex or long running projects across team boundaries")),
            'leadership_evidence': (str, Field(description="Evidence from resume supporting project leadership assessment")),
            
            'attention_to_detail': (str, Field(description="Assessment of candidate's attention to detail based on resume evidence")),
            'attention_evidence': (str, Field(description="Evidence from resume supporting attention to detail assessment")),
            
            'hungry_for_excellence': (str, Field(description="Assessment of candidate's drive for excellence and hunger for success based on resume evidence")),
            'excellence_evidence': (str, Field(description="Evidence from resume supporting excellence assessment"))
        }
    
    @property
    def dimension_weights(self) -> Dict[str, float]:
        return {
            'english_proficiency': 15.0,
            'us_saas_familiarity': 15.0,
            'technical_breadth': 15.0,
            'it_operation': 12.0,
            'architecture_capability': 10.0,
            'project_leadership': 10.0,
            'communication_skill': 8.0,
            'hungry_for_excellence': 8.0,
            'attention_to_detail': 7.0
        } 