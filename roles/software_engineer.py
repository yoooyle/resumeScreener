from typing import Dict
from pydantic import Field
from .base_role import BaseRole

class SoftwareEngineerRole(BaseRole):
    @property
    def role_name(self) -> str:
        return "Software Engineer"
    
    @property
    def prompt_template(self) -> str:
        return """You are an expert resume analyzer for Software Engineer positions. 
        Analyze the resume text and extract key information about the candidate's qualifications.
        Focus on technical skills, coding proficiency, and engineering practices.
        
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
            'coding_proficiency': (str, Field(description="Coding skill level (High/Medium/Low/No Signal). High: multiple languages/frameworks in production, complex problem solving. Medium: basic production experience. Low: mainly learning projects. No Signal: no coding evidence.")),
            'coding_evidence': (str, Field(description="Evidence from resume supporting coding proficiency assessment")),
            
            'system_design': (str, Field(description="System design capability (High/Medium/Low/No Signal). High: designed scalable systems, clear architecture decisions. Medium: some design experience. Low: mainly implementation work. No Signal: no design experience.")),
            'system_design_evidence': (str, Field(description="Evidence from resume supporting system design assessment")),
            
            'engineering_practices': (str, Field(description="Software engineering practices (High/Medium/Low/No Signal). High: strong CI/CD, testing, code review practices. Medium: follows some best practices. Low: limited engineering rigor. No Signal: no evidence of practices.")),
            'engineering_evidence': (str, Field(description="Evidence from resume supporting engineering practices assessment")),
            
            'problem_solving': (str, Field(description="Problem-solving ability (High/Medium/Low/No Signal). High: solved complex technical challenges, optimization work. Medium: standard problem-solving. Low: straightforward tasks. No Signal: no problem-solving evidence.")),
            'problem_solving_evidence': (str, Field(description="Evidence from resume supporting problem-solving assessment")),
            
            'tech_stack_breadth': (str, Field(description="Technical stack breadth (High/Medium/Low/No Signal). High: diverse languages, frameworks, and tools. Medium: moderate variety. Low: limited to few technologies. No Signal: no clear tech exposure.")),
            'tech_stack_evidence': (str, Field(description="Evidence from resume supporting tech stack assessment")),
            
            'backend_skills': (str, Field(description="Backend development skills (High/Medium/Low/No Signal). High: databases, APIs, services, scalability. Medium: basic backend work. Low: limited backend exposure. No Signal: no backend experience.")),
            'backend_evidence': (str, Field(description="Evidence from resume supporting backend skills assessment")),
            
            'devops_knowledge': (str, Field(description="DevOps and infrastructure knowledge (High/Medium/Low/No Signal). High: cloud platforms, deployment, monitoring. Medium: basic DevOps. Low: limited ops experience. No Signal: no DevOps exposure.")),
            'devops_evidence': (str, Field(description="Evidence from resume supporting DevOps knowledge assessment")),
            
            'english_proficiency': (str, Field(description="English proficiency level (High/Medium/Low/No Signal). High: clear signals of using English as working language. Medium: signals of working with English docs and tools. Low: basic English exposure. No Signal: no English exposure evidence.")),
            'english_evidence': (str, Field(description="Evidence from resume supporting English proficiency assessment")),
            
            'team_collaboration': (str, Field(description="Team collaboration level (High/Medium/Low/No Signal). High: effective team work, mentoring, knowledge sharing. Medium: standard collaboration. Low: mainly individual work. No Signal: no collaboration evidence.")),
            'collaboration_evidence': (str, Field(description="Evidence from resume supporting team collaboration assessment")),
            
            'learning_ability': (str, Field(description="Learning and adaptability (High/Medium/Low/No Signal). High: quick learner, adapts to new tech. Medium: standard learning pace. Low: limited growth evidence. No Signal: no learning indicators.")),
            'learning_evidence': (str, Field(description="Evidence from resume supporting learning ability assessment"))
        }
    
    @property
    def dimension_weights(self) -> Dict[str, float]:
        return {
            'coding_proficiency': 20.0,
            'system_design': 15.0,
            'engineering_practices': 12.0,
            'problem_solving': 10.0,
            'tech_stack_breadth': 10.0,
            'backend_skills': 8.0,
            'devops_knowledge': 7.0,
            'english_proficiency': 7.0,
            'team_collaboration': 6.0,
            'learning_ability': 5.0
        } 