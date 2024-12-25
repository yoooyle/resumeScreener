import os
import sys
import logging
from pathlib import Path
from typing import Optional
from ai_resume_extractor import AIResumeExtractor
import pandas as pd

logger = logging.getLogger(__name__)

class ResumesExtractor:
    """
    Batch processor for extracting dimensions from multiple resumes.
    This class handles the directory traversal and batch processing of resume PDFs.
    """
    
    def __init__(self, role: str = "it_manager", use_optimized_pdf: bool = True):
        """
        Initialize the resumes extractor.
        
        Args:
            role: Role to analyze for (default: "it_manager")
            use_optimized_pdf: Whether to use PyMuPDF for optimized PDF extraction (default: True)
        """
        self.role = role
        self.use_optimized_pdf = use_optimized_pdf
        self.extractor = AIResumeExtractor(role=role, use_optimized_pdf=use_optimized_pdf)
    
    def extract_from_directory(self, directory_path: str, output_file: str = "extracted_dimensions.csv") -> Optional[pd.DataFrame]:
        """
        Extract dimensions from all PDF resumes in a directory and save results to CSV.
        
        Args:
            directory_path: Path to directory containing PDF resumes
            output_file: Path to output CSV file (default: extracted_dimensions.csv)
        
        Returns:
            DataFrame with extracted dimensions if successful, None if error occurs
        """
        try:
            # Get list of PDF files
            pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
            if not pdf_files:
                logger.warning(f"No PDF files found in directory: {directory_path}")
                return None
            
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            # Process each resume
            results = []
            for pdf_file in pdf_files:
                pdf_path = os.path.join(directory_path, pdf_file)
                try:
                    logger.info(f"Processing {pdf_file}...")
                    result = self.extractor.extract_from_pdf(pdf_path)
                    result_dict = result.dict()
                    result_dict['resume_file'] = pdf_file
                    results.append(result_dict)
                except Exception as e:
                    logger.error(f"Error processing {pdf_file}: {str(e)}")
                    continue
            
            if not results:
                logger.error("No results were generated")
                return None
            
            # Convert to DataFrame and save
            df = pd.DataFrame(results)
            
            # Ensure resume_file is the first column
            cols = ['resume_file'] + [col for col in df.columns if col != 'resume_file']
            df = df[cols]
            
            df.to_csv(output_file, index=False)
            logger.info(f"Extraction complete. Results saved to {output_file}")
            return df
            
        except Exception as e:
            logger.error(f"Error processing directory: {str(e)}", exc_info=True)
            return None

def main():
    """Command-line interface for batch resume dimension extraction."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract dimensions from multiple resumes in a directory")
    parser.add_argument("directory_path", help="Path to directory containing PDF resumes")
    parser.add_argument("--role", "-r", default="it_manager",
                       help="Role to analyze for (default: it_manager)")
    parser.add_argument("--output", "-o", default="extracted_dimensions.csv",
                       help="Output CSV file path (default: extracted_dimensions.csv)")
    parser.add_argument("--legacy-pdf", action="store_true",
                       help="Use legacy PDF extraction (PyPDF) instead of optimized PyMuPDF")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory_path):
        logger.error(f"Directory does not exist: {args.directory_path}")
        sys.exit(1)
    
    if not os.path.isdir(args.directory_path):
        logger.error(f"Path is not a directory: {args.directory_path}")
        sys.exit(1)
    
    extractor = ResumesExtractor(role=args.role, use_optimized_pdf=not args.legacy_pdf)
    result = extractor.extract_from_directory(args.directory_path, args.output)
    
    if result is None:
        sys.exit(1)

if __name__ == "__main__":
    main() 