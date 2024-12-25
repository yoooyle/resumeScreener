import os
import sys
import logging
from typing import Optional, Union, Type
from openai import OpenAI
from pypdf import PdfReader
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from roles import BaseRole, RoleRegistry

# Load environment variables at module level
load_dotenv()

# Verify API key is available
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")

# Create logger for this module
logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    def __init__(self, role: Union[str, BaseRole], api_key: Optional[str] = None):
        """
        Initialize the resume analyzer for a specific role.
        
        Args:
            role: Either a role name string or a BaseRole instance
            api_key: Optional OpenAI API key (defaults to environment variable)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        # Get role configuration
        if isinstance(role, str):
            self.role = RoleRegistry.get_role(role)
        elif isinstance(role, BaseRole):
            self.role = role
        else:
            raise TypeError("role must be either a string or BaseRole instance")
        
        # Create the analysis model for this role
        self.AnalysisModel = self.role.create_analysis_model()
        
        logger.debug(f"ResumeAnalyzer initialized for role: {self.role.role_name}")

    def extract_text_from_pdf(self, pdf_path: Union[str, Path]) -> str:
        """Extract text content from a PDF file."""
        logger.debug(f"Extracting text from PDF: {pdf_path}")
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        logger.debug(f"Extracted {len(text)} characters from PDF")
        return text

    def analyze_resume_text(self, resume_text: str) -> BaseModel:
        """Analyze a single resume text and return structured results."""
        logger.debug("Starting resume text analysis")
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.role.prompt_template},
                {"role": "user", "content": f"Here is the resume text to analyze:\n\n{resume_text}"}
            ],
            response_format=self.AnalysisModel
        )
        logger.debug("Resume analysis completed")
        return completion.choices[0].message.parsed

    def analyze_resume_file(self, file_path: Union[str, Path]) -> BaseModel:
        """Analyze a resume file (PDF) and return structured results."""
        logger.info(f"Analyzing resume file: {file_path}")
        text = self.extract_text_from_pdf(file_path)
        logger.debug("Extracted text from PDF, proceeding with analysis")
        return self.analyze_resume_text(text)

def process_resume(file_path: str, role: Union[str, BaseRole] = 'it_manager') -> dict:
    """
    Process a single resume file and return analysis results.
    
    Args:
        file_path: Path to the resume PDF file
        role: Role to analyze for (default: 'it_manager')
    
    Returns:
        Dictionary containing the analysis results
    """
    analyzer = ResumeAnalyzer(role)
    result = analyzer.analyze_resume_file(file_path)
    return result.dict()

def main():
    """Command-line interface for resume analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze a resume for a specific role")
    parser.add_argument("resume_file", help="Path to the resume PDF file")
    parser.add_argument("--role", "-r", default="it_manager",
                       help=f"Role to analyze for. Available roles: {', '.join(RoleRegistry.available_roles())}")
    
    args = parser.parse_args()
    
    try:
        result = process_resume(args.resume_file, args.role)
        
        # Print results in a readable format
        print("\nResume Analysis Results:")
        print("=" * 50)
        for field, value in result.items():
            if not field.endswith('_evidence'):
                print(f"\n{field.replace('_', ' ').title()}:")
                print(f"Assessment: {value}")
                evidence_field = field + '_evidence'
                evidence = result.get(evidence_field)
                if evidence:
                    print(f"Evidence: {evidence}")
    
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 