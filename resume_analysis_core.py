import os
import sys
import logging
from typing import Optional, Union, Type
from openai import OpenAI
from pypdf import PdfReader
import fitz  # PyMuPDF
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from roles import BaseRole, RoleRegistry
import logging_config

# Load environment variables at module level
load_dotenv()

# Verify API key is available
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")

# Create logger for this module
logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    def __init__(self, role: Union[str, BaseRole], api_key: Optional[str] = None, use_optimized_pdf: bool = True):
        """
        Initialize the resume analyzer for a specific role.
        
        Args:
            role: Either a role name string or a BaseRole instance
            api_key: Optional OpenAI API key (defaults to environment variable)
            use_optimized_pdf: Whether to use PyMuPDF for optimized PDF extraction (default: True)
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.use_optimized_pdf = use_optimized_pdf
        
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

    def extract_text_from_pdf_pypdf(self, pdf_path: Union[str, Path]) -> str:
        """Extract text content from a PDF file using PyPDF."""
        logger.debug(f"Extracting text from PDF using PyPDF: {pdf_path}")
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        logger.debug(f"Extracted {len(text)} characters from PDF using PyPDF")
        return text

    def extract_text_from_pdf_mupdf(self, pdf_path: Union[str, Path]) -> str:
        """Extract text content from a PDF file using PyMuPDF (optimized)."""
        logger.debug(f"Extracting text from PDF using PyMuPDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        text = ""
        try:
            for page in doc:
                # Get plain text with preserved formatting
                text += page.get_text("text", sort=True) + "\n"
                
                # If text extraction yields little content, try extracting with different flags
                if len(text.strip()) < 50:  # Arbitrary threshold
                    logger.debug("Low text content detected, trying alternative extraction")
                    text = ""
                    for page in doc:
                        # Try with blocks mode which might handle complex layouts better
                        text += page.get_text("blocks") + "\n"
                        
                        # If still low content, try raw mode as last resort
                        if len(text.strip()) < 50:
                            text = ""
                            for page in doc:
                                text += page.get_text("raw") + "\n"
        finally:
            doc.close()
        
        logger.debug(f"Extracted {len(text)} characters from PDF using PyMuPDF")
        return text

    def extract_text_from_pdf(self, pdf_path: Union[str, Path]) -> str:
        """Extract text content from a PDF file using the selected method."""
        if self.use_optimized_pdf:
            return self.extract_text_from_pdf_mupdf(pdf_path)
        return self.extract_text_from_pdf_pypdf(pdf_path)

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

def process_resume(file_path: str, role: Union[str, BaseRole] = 'it_manager', use_optimized_pdf: bool = True) -> dict:
    """
    Process a single resume file and return analysis results.
    
    Args:
        file_path: Path to the resume PDF file
        role: Role to analyze for (default: 'it_manager')
        use_optimized_pdf: Whether to use PyMuPDF for optimized PDF extraction (default: True)
    
    Returns:
        Dictionary containing the analysis results
    """
    analyzer = ResumeAnalyzer(role, use_optimized_pdf=use_optimized_pdf)
    result = analyzer.analyze_resume_file(file_path)
    return result.dict()

def main():
    """Command-line interface for resume analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze a resume for a specific role")
    parser.add_argument("resume_file", help="Path to the resume PDF file")
    parser.add_argument("--role", "-r", default="it_manager",
                       help=f"Role to analyze for. Available roles: {', '.join(RoleRegistry.available_roles())}")
    parser.add_argument("--legacy-pdf", action="store_true",
                       help="Use legacy PDF extraction (PyPDF) instead of optimized PyMuPDF")
    parser.add_argument("--log-level", "-l", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                       help="Set the logging level (default: INFO)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Shortcut for --log-level DEBUG")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Shortcut for --log-level ERROR")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        log_level = "DEBUG"
    elif args.quiet:
        log_level = "ERROR"
    else:
        log_level = args.log_level
    
    logging_config.set_log_level(getattr(logging, log_level))
    
    try:
        result = process_resume(
            args.resume_file,
            args.role,
            use_optimized_pdf=not args.legacy_pdf
        )
        
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