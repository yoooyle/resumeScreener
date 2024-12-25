import os
import sys
from dotenv import load_dotenv
import pandas as pd
import glob
import logging
from resume_analysis_core import ResumeAnalyzer, ResumeAnalysisResult
import logging_config
from field_config import FIELD_PAIRS, ASSESSMENT_FIELDS, EVIDENCE_FIELDS

# Load environment variables
load_dotenv()

# Create logger for this module
logger = logging.getLogger(__name__)

class ResumeProcessor:
    def __init__(self):
        self.analyzer = ResumeAnalyzer()

    def analysis_to_dict(self, analysis: ResumeAnalysisResult, resume_file: str) -> dict:
        """Convert analysis result to a dictionary for CSV output.
        
        Returns a flat dictionary with:
        - One column per dimension (assessment)
        - One column per evidence field (at the end)
        """
        # Start with the resume file name
        result = {'resume_file': resume_file}
        data = analysis.model_dump()
        
        # Add all assessment fields first
        for field in ASSESSMENT_FIELDS:
            result[field] = data.get(field)
        
        # Add all evidence fields at the end
        for evidence_field in EVIDENCE_FIELDS:
            result[evidence_field] = data.get(evidence_field, '')
        
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
                result = self.analysis_to_dict(analysis, os.path.basename(pdf_file))
                all_results.append(result)
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {str(e)}")
        
        if all_results:
            df = pd.DataFrame(all_results)
            
            # Reorder columns to put evidence at the end
            cols = ['resume_file'] + ASSESSMENT_FIELDS + EVIDENCE_FIELDS
            df = df[cols]
            
            df.to_csv(output_file, index=False)
            logger.info(f"Analysis complete. Results saved to {output_file}")
            logger.debug(f"CSV columns: {', '.join(df.columns)}")
        else:
            logger.warning("No results were generated. No output file created.")

def main():
    """Command-line interface for batch resume processing."""
    # Set debug level for CLI usage
    logging_config.set_log_level(logging.INFO)
    
    if len(sys.argv) != 2:
        logger.error("Invalid number of arguments")
        print("Usage: python resume_analyzer.py <directory_path>")
        sys.exit(1)

    directory_path = sys.argv[1]
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is not set")
        sys.exit(1)

    if not os.path.exists(directory_path):
        logger.error(f"Directory does not exist: {directory_path}")
        sys.exit(1)

    if not os.path.isdir(directory_path):
        logger.error(f"Path is not a directory: {directory_path}")
        sys.exit(1)
    
    processor = ResumeProcessor()
    processor.process_directory(directory_path)

if __name__ == "__main__":
    main() 