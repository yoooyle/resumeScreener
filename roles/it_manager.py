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
        Focus on leadership abilities, technical breadth, and operational excellence.
        
        For each dimension, provide an assessment level (High/Medium/Low/No Signal) and specific evidence from the resume that supports your assessment.
        
        Assessment Levels:
        - High: Strong evidence of excellence in this dimension
        - Medium: Moderate evidence or mixed signals
        - Low: Limited or weak evidence
        - No Signal: No clear evidence found
        
        Be objective and thorough in your analysis."""
    
    @property
    def analysis_model_fields(self) -> Dict[str, tuple]:
        return {
            'english_proficiency': (str, Field(description="English proficiency level (High/Medium/Low/No Signal). High: clear signals of using English as working language (English resume, worked in English speaking firms, study abroad). Medium: signals of working with English docs and tools. Low: basic English exposure. No Signal: no English exposure evidence.")),
            'english_evidence': (str, Field(description="Evidence from resume supporting English proficiency assessment")),
            
            'communication_skill': (str, Field(description="Communication skill level (High/Medium/Low/No Signal). High: clear evidence of effective stakeholder communication and complex explanations. Medium: standard communication tasks. Low: limited communication scope. No Signal: no clear communication evidence.")),
            'communication_evidence': (str, Field(description="Evidence from resume supporting communication skill assessment")),
            
            'us_saas_familiarity': (str, Field(description="Familiarity with US SaaS (High/Medium/Low/No Signal). High: extensive experience with US SaaS like Slack, MSFT Team, Google Workspace, Jira. Medium: some exposure to US tools. Low: mainly local tools. No Signal: no clear indication.")),
            'us_saas_evidence': (str, Field(description="Evidence from resume supporting US SaaS familiarity assessment")),
            
            'technical_breadth': (str, Field(description="Technical domain breadth (High/Medium/Low/No Signal). High: expertise across Endpoint Management, IAM & SSO, VPN & Network, and more IT domains. Medium: proficiency in some domains. Low: limited domain knowledge. No Signal: no clear technical breadth.")),
            'technical_breadth_evidence': (str, Field(description="Evidence from resume supporting technical breadth assessment")),
            
            'architecture_capability': (str, Field(description="Architecture capability level (High/Medium/Low/No Signal). High: led system architecture design and implementation. Medium: contributed to architecture decisions. Low: mainly followed existing designs. No Signal: no architecture experience.")),
            'architecture_evidence': (str, Field(description="Evidence from resume supporting architecture capability assessment")),
            
            'it_operation': (str, Field(description="IT operation capability (High/Medium/Low/No Signal). High: led help desk, built knowledge base, implemented automation. Medium: handled standard operations. Low: basic operational tasks. No Signal: no operations experience.")),
            'it_operation_evidence': (str, Field(description="Evidence from resume supporting IT operation assessment")),
            
            'project_leadership': (str, Field(description="Project leadership level (High/Medium/Low/No Signal). High: led complex cross-team projects. Medium: managed small team projects. Low: participated in projects. No Signal: no leadership evidence.")),
            'leadership_evidence': (str, Field(description="Evidence from resume supporting project leadership assessment")),
            
            'attention_to_detail': (str, Field(description="Attention to detail level (High/Medium/Low/No Signal). High: demonstrated meticulous planning and execution. Medium: standard attention to procedures. Low: some oversight evidence. No Signal: no clear indication.")),
            'attention_evidence': (str, Field(description="Evidence from resume supporting attention to detail assessment")),
            
            'hungry_for_excellence': (str, Field(description="Drive for excellence (High/Medium/Low/No Signal). High: clear pattern of improvement initiatives and growth. Medium: standard professional development. Low: minimal growth evidence. No Signal: no clear drive shown.")),
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