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
        Focus on technical skills, coding proficiency, system design capabilities, and engineering practices.
        
        For each dimension, provide specific evidence from the resume that supports your assessment.
        Be objective and thorough in your analysis.
        
        When evaluating coding proficiency, look for:
        - Languages and frameworks used in production
        - Complex technical problems solved
        - Code quality and testing practices
        
        When evaluating system design, look for:
        - Architecture decisions and tradeoffs
        - Scalability considerations
        - Performance optimizations
        
        When evaluating engineering practices, look for:
        - CI/CD experience
        - Testing strategies
        - Code review practices
        - Documentation habits"""
    
    @property
    def analysis_model_fields(self) -> Dict[str, tuple]:
        return {
            'english_proficiency': (str, Field(description="English proficiency level (Proficient/OK/No signal). Proficient: clear signals of using English as working language (English resume, worked in English speaking firms, study abroad in English speaking countries, English certifications). OK: signals of working with English docs and tools. No signal: no English exposure evidence.")),
            'english_evidence': (str, Field(description="Evidence from resume supporting English proficiency assessment")),
            
            'coding_proficiency': (str, Field(description="Coding skill level (High/Medium/Low). High: multiple languages/frameworks in production, complex problem solving, strong CS fundamentals. Medium: basic production experience. Low: mainly academic/learning projects.")),
            'coding_evidence': (str, Field(description="Evidence from resume supporting coding proficiency assessment")),
            
            'system_design': (str, Field(description="System design capability (High/Medium/Low). High: designed scalable systems, clear architecture decisions, performance optimization experience. Medium: some design experience. Low: mainly implementation work.")),
            'system_design_evidence': (str, Field(description="Evidence from resume supporting system design assessment")),
            
            'engineering_practices': (str, Field(description="Software engineering practices (High/Medium/Low). High: strong CI/CD, testing, code review, and documentation practices. Medium: follows some best practices. Low: limited evidence of engineering rigor.")),
            'engineering_evidence': (str, Field(description="Evidence from resume supporting engineering practices assessment")),
            
            'problem_solving': (str, Field(description="Problem-solving ability (High/Medium/Low). High: solved complex technical challenges, algorithmic thinking, optimization work. Medium: standard problem-solving. Low: mainly straightforward tasks.")),
            'problem_solving_evidence': (str, Field(description="Evidence from resume supporting problem-solving assessment")),
            
            'tech_stack_breadth': (str, Field(description="Technical stack breadth (High/Medium/Low). High: diverse languages, frameworks, and tools. Medium: moderate variety. Low: limited to few technologies.")),
            'tech_stack_evidence': (str, Field(description="Evidence from resume supporting tech stack assessment")),
            
            'backend_skills': (str, Field(description="Backend development skills (High/Medium/Low). High: databases, APIs, services, scalability. Medium: basic backend work. Low: limited backend exposure.")),
            'backend_evidence': (str, Field(description="Evidence from resume supporting backend skills assessment")),
            
            'devops_knowledge': (str, Field(description="DevOps and infrastructure knowledge (High/Medium/Low). High: cloud platforms, deployment, monitoring, infrastructure. Medium: basic DevOps. Low: limited ops experience.")),
            'devops_evidence': (str, Field(description="Evidence from resume supporting DevOps knowledge assessment")),
            
            'team_collaboration': (str, Field(description="Team collaboration and communication (High/Medium/Low). High: effective team work, mentoring, knowledge sharing. Medium: standard collaboration. Low: mainly individual work.")),
            'collaboration_evidence': (str, Field(description="Evidence from resume supporting team collaboration assessment")),
            
            'learning_ability': (str, Field(description="Learning and adaptability (High/Medium/Low). High: quick learner, adapts to new tech, self-directed learning. Medium: standard learning pace. Low: limited evidence of growth.")),
            'learning_evidence': (str, Field(description="Evidence from resume supporting learning ability assessment"))
        }
    
    @property
    def dimension_weights(self) -> Dict[str, float]:
        return {
            'coding_proficiency': 20.0,    # Core skill
            'system_design': 15.0,         # Critical for scalable solutions
            'engineering_practices': 12.0,  # Important for code quality
            'problem_solving': 10.0,       # Essential for complex tasks
            'tech_stack_breadth': 10.0,    # Important for adaptability
            'backend_skills': 8.0,         # Specific technical focus
            'devops_knowledge': 7.0,       # Important for modern development
            'english_proficiency': 7.0,    # Communication requirement
            'team_collaboration': 6.0,     # Team work
            'learning_ability': 5.0        # Growth potential
        } 