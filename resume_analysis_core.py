import os
import sys
import logging
from typing import Optional, List, Union, Dict, Any
from pydantic import BaseModel, Field
from openai import OpenAI
from pypdf import PdfReader
from pathlib import Path
from dotenv import load_dotenv
import logging_config

# Load environment variables at module level
load_dotenv()

# Create logger for this module
logger = logging.getLogger(__name__)

# Verify API key is available
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")

class ResumeAnalysisResult(BaseModel):
    chinese_name: Optional[str] = Field(None, description="Chinese name from the resume")
    expected_salary: Optional[str] = Field(None, description="Expected salary if mentioned in the resume")
    years_of_experience: Optional[str] = Field(None, description="Years of experience in relevant IT roles")
    english_proficiency: str = Field(description="English proficiency level (Proficient/OK/No signal). Proficient: clear signals of using English as working language (English resume, worked in English speaking firms, study abroad in English speaking countries, English certifications like TOEFL/IELTS). OK: signals of working with English docs, compliance frameworks, and tools. No signal: no English exposure evidence.")
    english_evidence: str = Field(description="Evidence from resume supporting English proficiency assessment")
    communication_skill: str = Field(description="Assessment of ability to work with diverse non-technical stakeholders and translate business languages into technical solutions")
    communication_evidence: str = Field(description="Evidence from resume supporting communication skill assessment")
    us_saas_familiarity: str = Field(description="Familiarity with US SaaS (High/Low/No signal). High: worked in companies using US SaaS like Slack, MSFT Team, Google Workspace, Jira. Low: only worked with China (dealbreaker). No signal: no clear indication.")
    us_saas_evidence: str = Field(description="Evidence from resume supporting US SaaS familiarity assessment")
    technical_breadth: str = Field(description="Technical domain breadth (High/Medium/Low). High: has Endpoint Management, IAM & SSO, VPN & Network, and more IT domains. Medium: some of these domains. Low: none of these domains.")
    technical_breadth_evidence: str = Field(description="Evidence from resume supporting technical breadth assessment")
    architecture_capability: str = Field(description="Assessment of ability to think and design on system/architecture level vs only implementing others' designs")
    architecture_evidence: str = Field(description="Evidence from resume supporting architecture capability assessment")
    it_operation: str = Field(description="Efficient IT operation capability (High/Medium/Low). High: experience running help desk, building knowledge base, automating with Python/AI/low-code tools. Medium: some of these. Low: none of these.")
    it_operation_evidence: str = Field(description="Evidence from resume supporting IT operation assessment")
    project_leadership: str = Field(description="Assessment of experience leading complex or long running projects across team boundaries")
    leadership_evidence: str = Field(description="Evidence from resume supporting project leadership assessment")
    attention_to_detail: str = Field(description="Assessment of candidate's attention to detail based on resume evidence")
    attention_evidence: str = Field(description="Evidence from resume supporting attention to detail assessment")
    hungry_for_excellence: str = Field(description="Assessment of candidate's drive for excellence and hunger for success based on resume evidence")
    excellence_evidence: str = Field(description="Evidence from resume supporting excellence assessment")
    risks: Optional[str] = Field(None, description="Potential risks and lowlights where the candidate may not qualify")
    highlights: Optional[str] = Field(None, description="Notable highlights and strengths that help the candidate stand out")

    def format_output(self) -> Dict[str, Any]:
        """Format the analysis result for readable output."""
        field_pairs = {
            'chinese_name': None,
            'expected_salary': None,
            'years_of_experience': None,
            'english_proficiency': 'english_evidence',
            'communication_skill': 'communication_evidence',
            'us_saas_familiarity': 'us_saas_evidence',
            'technical_breadth': 'technical_breadth_evidence',
            'architecture_capability': 'architecture_evidence',
            'it_operation': 'it_operation_evidence',
            'project_leadership': 'leadership_evidence',
            'attention_to_detail': 'attention_evidence',
            'hungry_for_excellence': 'excellence_evidence',
            'risks': None,
            'highlights': None
        }
        
        formatted_result = {}
        data = self.model_dump()
        for field, evidence_field in field_pairs.items():
            value = data.get(field)
            if value is not None:
                field_result = {
                    'assessment': value
                }
                if evidence_field:
                    field_result['evidence'] = data.get(evidence_field, '')
                formatted_result[field] = field_result
        
        return formatted_result

class ResumeAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        with open('resume-extractor-prompt.txt', 'r') as file:
            self.system_prompt = file.read()
        logger.debug("ResumeAnalyzer initialized")

    def extract_text_from_pdf(self, pdf_path: Union[str, Path]) -> str:
        """Extract text content from a PDF file."""
        logger.debug(f"Extracting text from PDF: {pdf_path}")
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        logger.debug(f"Extracted {len(text)} characters from PDF")
        return text

    def analyze_resume_text(self, resume_text: str) -> ResumeAnalysisResult:
        """Analyze a single resume text and return structured results."""
        logger.debug("Starting resume text analysis")
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Here is the resume text to analyze:\n\n{resume_text}"}
            ],
            response_format=ResumeAnalysisResult
        )
        
        logger.debug("Resume analysis completed")
        return completion.choices[0].message.parsed

    def analyze_resume_file(self, file_path: Union[str, Path]) -> ResumeAnalysisResult:
        """Analyze a resume file (PDF) and return structured results."""
        logger.info(f"Analyzing resume file: {file_path}")
        text = self.extract_text_from_pdf(file_path)
        logger.debug("Extracted text from PDF, proceeding with analysis")
        return self.analyze_resume_text(text)

def process_resume(file_path: str) -> Dict[str, Any]:
    """Process a resume file and return structured analysis results."""
    try:
        logger.info(f"Starting resume analysis for: {file_path}")
        analyzer = ResumeAnalyzer()
        
        if file_path.lower().endswith('.pdf'):
            result = analyzer.analyze_resume_file(file_path)
        else:
            with open(file_path, 'r') as file:
                resume_text = file.read()
            result = analyzer.analyze_resume_text(resume_text)
        
        formatted_result = result.format_output()
        logger.info("Resume analysis completed successfully")
        return formatted_result
        
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}", exc_info=True)
        raise

def main():
    """Command-line interface for resume analysis."""
    # Set debug level for CLI usage
    logging_config.set_log_level(logging.DEBUG)
    
    if len(sys.argv) != 2:
        logger.error("Invalid number of arguments")
        print("Usage: python resume_analysis_core.py <resume_file>")
        sys.exit(1)
    
    try:
        result = process_resume(sys.argv[1])
        print("\nResume Analysis Results:")
        print("=" * 50)
        
        for field, data in result.items():
            print(f"\n{field.replace('_', ' ').title()}")
            print(f"Assessment: {data['assessment']}")
            if 'evidence' in data:
                print(f"Evidence: {data['evidence']}")
                
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 