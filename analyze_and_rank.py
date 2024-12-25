import os
import sys
import logging
from resume_analyzer import ResumeProcessor
from resume_scorer import score_resumes
import logging_config
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)

def process_and_rank(
    directory_path: str, 
    output_prefix: str = "resume",
    force_rerun: bool = False
) -> Optional[pd.DataFrame]:
    """
    Process a directory of resumes and produce ranked results.
    Skips steps if output files exist, unless force_rerun is True.
    
    Args:
        directory_path: Path to directory containing PDF resumes
        output_prefix: Prefix for output files (default: "resume")
                      Will produce <prefix>_analysis.csv and <prefix>_ranked.csv
        force_rerun: If True, rerun all steps even if outputs exist
    
    Returns:
        DataFrame with ranked results if successful, None if error occurs
    """
    # Set up output file paths
    analysis_file = f"{output_prefix}_analysis.csv"
    ranked_file = f"{output_prefix}_ranked.csv"
    
    try:
        # Step 1: Analyze resumes
        if force_rerun or not os.path.exists(analysis_file):
            logger.info("Step 1: Analyzing resumes...")
            processor = ResumeProcessor()
            processor.process_directory(directory_path, analysis_file)
        else:
            logger.info(f"Using existing analysis file: {analysis_file}")
            if not os.path.getsize(analysis_file):
                logger.error(f"Existing analysis file is empty: {analysis_file}")
                return None
        
        # Step 2: Score and rank results
        if force_rerun or not os.path.exists(ranked_file):
            logger.info("Step 2: Scoring and ranking candidates...")
            df = score_resumes(analysis_file, ranked_file)
        else:
            logger.info(f"Using existing ranked file: {ranked_file}")
            if not os.path.getsize(ranked_file):
                logger.error(f"Existing ranked file is empty: {ranked_file}")
                return None
            df = pd.read_csv(ranked_file)
        
        logger.info(f"Analysis complete. Results available in:")
        logger.info(f"- Raw analysis: {analysis_file}")
        logger.info(f"- Ranked results: {ranked_file}")
        
        # Print top 5 summary
        print("\nTop 5 Candidates Summary:")
        print("=" * 50)
        top_5 = df.head().to_dict('records')
        
        for row in top_5:
            print(f"\nRank {int(row['rank'])} - Score: {float(row['total_score']):.2f}")
            print(f"File: {row['resume_file']}")
            print(f"Name: {str(row['chinese_name'])}")
            if pd.notna(row['highlights']):
                print(f"Key Strengths: {str(row['highlights'])}")
            if pd.notna(row['risks']):
                print(f"Risks: {str(row['risks'])}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing directory: {str(e)}", exc_info=True)
        return None

def main():
    """Command-line interface for combined analysis and ranking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze and rank resumes from a directory")
    parser.add_argument("directory_path", help="Path to directory containing PDF resumes")
    parser.add_argument("--force", "-f", action="store_true", 
                       help="Force rerun all steps even if outputs exist")
    parser.add_argument("--prefix", "-p", default="resume",
                       help="Prefix for output files (default: 'resume')")
    
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
    
    result = process_and_rank(
        args.directory_path,
        output_prefix=args.prefix,
        force_rerun=args.force
    )
    
    if result is None:
        sys.exit(1)

if __name__ == "__main__":
    # Set up logging
    logging_config.set_log_level(logging.INFO)
    main() 