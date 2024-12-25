import os
import sys
from dotenv import load_dotenv
import pandas as pd
import glob
import logging
from resume_analysis_core import ResumeAnalyzer
from roles import RoleRegistry
import logging_config

# Load environment variables
load_dotenv()

# Create logger for this module
logger = logging.getLogger(__name__)

class ResumeProcessor:
    def __init__(self, role: str = 'it_manager'):
        """
        Initialize the resume processor for a specific role.
        
        Args:
            role: Name of the role to analyze for (default: 'it_manager')
        """
        self.role = RoleRegistry.get_role(role)
        self.analyzer = ResumeAnalyzer(self.role)

    def analysis_to_dict(self, analysis, resume_file: str) -> dict:
        """Convert analysis result to a dictionary for CSV output."""
        result = {'resume_file': resume_file}
        result.update(analysis)
        return result

    def process_directory(self, directory_path: str, output_file: str = "resume_analysis.csv"):
        """Process all PDF resumes in a directory and save results to CSV."""
        all_results = []
        pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in directory: {directory_path}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing {pdf_file}...")
                analysis = self.analyzer.analyze_resume_file(pdf_file)
                result = self.analysis_to_dict(analysis.dict(), os.path.basename(pdf_file))
                all_results.append(result)
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {str(e)}")
        
        if all_results:
            df = pd.DataFrame(all_results)
            # Order columns according to role configuration
            ordered_columns = ['resume_file'] + self.role.get_ordered_fields()
            df = df[ordered_columns]
            df.to_csv(output_file, index=False)
            logger.info(f"Analysis complete. Results saved to {output_file}")
        else:
            logger.warning("No results were generated. No output file created.")

def main():
    """Command-line interface for batch resume processing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process a directory of resumes for a specific role")
    parser.add_argument("directory_path", help="Path to directory containing PDF resumes")
    parser.add_argument("--role", "-r", default="it_manager",
                       help=f"Role to analyze for. Available roles: {', '.join(RoleRegistry.available_roles())}")
    parser.add_argument("--output", "-o", default="resume_analysis.csv",
                       help="Output CSV file path (default: resume_analysis.csv)")
    
    args = parser.parse_args()
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is not set")
        sys.exit(1)

    if not os.path.exists(args.directory_path):
        logger.error(f"Directory does not exist: {args.directory_path}")
        sys.exit(1)

    if not os.path.isdir(args.directory_path):
        logger.error(f"Path is not a directory: {args.directory_path}")
        sys.exit(1)
    
    processor = ResumeProcessor(args.role)
    processor.process_directory(args.directory_path, args.output)

if __name__ == "__main__":
    # Set up logging
    logging_config.set_log_level(logging.INFO)
    main() 