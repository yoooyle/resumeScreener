import os
import sys
import logging
from pathlib import Path
from typing import Optional
from resumes_extractor import ResumesExtractor
from resumes_ranker import score_and_rank_resumes
from roles import RoleRegistry
import logging_config
import pandas as pd

logger = logging.getLogger(__name__)

def extract_and_rank(
    resume_dir: str,
    role: str = "it_manager",
    output_prefix: str = "resume",
    force_rerun: bool = False,
    use_optimized_pdf: bool = True
) -> tuple[str, str, Optional[pd.DataFrame]]:
    """
    Extract dimensions from resumes and generate ranked results.
    
    Args:
        resume_dir: Directory containing resume PDFs
        role: Role to analyze for (default: "it_manager")
        output_prefix: Prefix for output files (default: "resume")
        force_rerun: Whether to force rerun extraction even if output exists
        use_optimized_pdf: Whether to use PyMuPDF for optimized PDF extraction
    
    Returns:
        Tuple of (extracted_csv_path, ranked_csv_path, ranked_df)
        ranked_df will be None if there's an error or no results
    """
    extracted_csv = f"{output_prefix}_extracted.csv"
    ranked_csv = f"{output_prefix}_ranked.csv"
    
    try:
        # Check if we need to run extraction
        if force_rerun or not os.path.exists(extracted_csv):
            logger.info("Running dimension extraction...")
            extractor = ResumesExtractor(role=role, use_optimized_pdf=use_optimized_pdf)
            extractor.extract_from_directory(resume_dir, output_file=extracted_csv)
        else:
            logger.info(f"Using existing extracted dimensions: {extracted_csv}")
            if not os.path.getsize(extracted_csv):
                logger.error(f"Existing extracted file is empty: {extracted_csv}")
                return extracted_csv, ranked_csv, None
        
        # Check if we need to run ranking
        if force_rerun or not os.path.exists(ranked_csv):
            logger.info("Generating ranked results...")
            df = score_and_rank_resumes(extracted_csv, ranked_csv)
        else:
            logger.info(f"Using existing ranked file: {ranked_csv}")
            if not os.path.getsize(ranked_csv):
                logger.error(f"Existing ranked file is empty: {ranked_csv}")
                return extracted_csv, ranked_csv, None
            df = pd.read_csv(ranked_csv)
        
        return extracted_csv, ranked_csv, df
        
    except Exception as e:
        logger.error(f"Error in extraction pipeline: {str(e)}", exc_info=True)
        return extracted_csv, ranked_csv, None

def main():
    """Command-line interface for the complete extraction and ranking pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract dimensions from resumes and rank them for a specific role")
    parser.add_argument("resume_dir", help="Directory containing resume PDFs")
    parser.add_argument("--role", "-r", default="it_manager",
                       help=f"Role to analyze for. Available roles: {', '.join(RoleRegistry.available_roles())}")
    parser.add_argument("--prefix", "-p", default="resume",
                       help="Prefix for output files (default: resume)")
    parser.add_argument("--force", "-f", action="store_true",
                       help="Force rerun all steps even if output files exist")
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
    
    # Validate inputs
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is not set")
        sys.exit(1)

    if not os.path.exists(args.resume_dir):
        logger.error(f"Directory does not exist: {args.resume_dir}")
        sys.exit(1)

    if not os.path.isdir(args.resume_dir):
        logger.error(f"Path is not a directory: {args.resume_dir}")
        sys.exit(1)
    
    # Validate role
    try:
        RoleRegistry.get_role(args.role)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    
    try:
        extracted_csv, ranked_csv, df = extract_and_rank(
            args.resume_dir,
            role=args.role,
            output_prefix=args.prefix,
            force_rerun=args.force,
            use_optimized_pdf=not args.legacy_pdf
        )
        
        print(f"\nExtraction and ranking complete!")
        print(f"Extracted dimensions: {extracted_csv}")
        print(f"Ranked results: {ranked_csv}")
        
        if df is not None and not df.empty:
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
                
                # Print dimension scores
                print("\nDimension Scores:")
                for col in row.keys():
                    if col.endswith('_score') and col != 'total_score':
                        score = float(row[col]) * 100
                        print(f"- {col.replace('_score', '').replace('_', ' ').title()}: {score:.1f}%")
    
    except Exception as e:
        logger.error(f"Error in extraction pipeline: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 