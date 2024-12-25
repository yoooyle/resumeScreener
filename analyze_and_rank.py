import os
import sys
import logging
from resume_analyzer import ResumeProcessor
from resume_scorer import score_resumes
import logging_config

logger = logging.getLogger(__name__)

def process_and_rank(directory_path: str, output_prefix: str = "resume") -> None:
    """
    Process a directory of resumes and produce ranked results.
    
    Args:
        directory_path: Path to directory containing PDF resumes
        output_prefix: Prefix for output files (default: "resume")
                      Will produce <prefix>_analysis.csv and <prefix>_ranked.csv
    """
    # Set up output file paths
    analysis_file = f"{output_prefix}_analysis.csv"
    ranked_file = f"{output_prefix}_ranked.csv"
    
    try:
        # Step 1: Analyze resumes
        logger.info("Step 1: Analyzing resumes...")
        processor = ResumeProcessor()
        processor.process_directory(directory_path, analysis_file)
        
        # Step 2: Score and rank results
        logger.info("Step 2: Scoring and ranking candidates...")
        score_resumes(analysis_file, ranked_file)
        
        logger.info(f"Analysis complete. Results saved to:")
        logger.info(f"- Raw analysis: {analysis_file}")
        logger.info(f"- Ranked results: {ranked_file}")
        
        # Print top 5 summary
        print("\nTop 5 Candidates Summary:")
        print("=" * 50)
        df = score_resumes(analysis_file)  # This returns the DataFrame
        top_5 = df.head().to_dict('records')
        
        for row in top_5:
            print(f"\nRank {int(row['rank'])} - Score: {float(row['total_score']):.2f}")
            print(f"File: {row['resume_file']}")
            print(f"Name: {str(row['chinese_name'])}")
            if pd.notna(row['highlights']):
                print(f"Key Strengths: {str(row['highlights'])}")
            if pd.notna(row['risks']):
                print(f"Risks: {str(row['risks'])}")
        
    except Exception as e:
        logger.error(f"Error processing directory: {str(e)}", exc_info=True)
        sys.exit(1)

def main():
    """Command-line interface for combined analysis and ranking."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_and_rank.py <directory_path>")
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
    
    process_and_rank(directory_path)

if __name__ == "__main__":
    # Set up logging
    logging_config.set_log_level(logging.INFO)
    main() 