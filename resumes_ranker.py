import os
import sys
import logging
import pandas as pd
from typing import Optional
from roles import RoleRegistry

logger = logging.getLogger(__name__)

def score_and_rank_resumes(input_file: str, output_file: str = "ranked_resumes.csv") -> Optional[pd.DataFrame]:
    """
    Score and rank resumes based on extracted dimensions.
    
    Args:
        input_file: Path to CSV file containing extracted dimensions
        output_file: Path to output CSV file with rankings (default: ranked_resumes.csv)
    
    Returns:
        DataFrame with scored and ranked results if successful, None if error occurs
    """
    try:
        # Read the input file
        df = pd.read_csv(input_file)
        if df.empty:
            logger.error(f"Input file is empty: {input_file}")
            return None
        
        # Get role from first row's dimensions
        dimension_cols = [col for col in df.columns if not col.endswith('_evidence') 
                        and col not in ['resume_file', 'chinese_name', 'expected_salary', 'years_of_experience', 'risks', 'highlights']]
        
        if not dimension_cols:
            logger.error("No scoreable dimensions found in input file")
            return None
        
        # Detect role from dimensions
        role_detected = False
        for role_name in RoleRegistry.available_roles():
            role = RoleRegistry.get_role(role_name)
            role_dimensions = set(role.dimension_weights.keys())
            if role_dimensions.issubset(set(dimension_cols)):
                logger.info(f"Detected role: {role.role_name}")
                role_detected = True
                break
        
        if not role_detected:
            logger.error("Could not detect role from dimensions")
            return None
        
        # Create score columns and calculate weighted scores
        weighted_scores = pd.Series(0.0, index=df.index)
        for dimension, weight in role.dimension_weights.items():
            # Convert categorical assessments to scores
            score_col = f"{dimension}_score"
            
            # Define valid categories
            score_mapping = {
                'High': 1.0,
                'Medium': 0.6,
                'Low': 0.2,
                'No Signal': 0.0,
                # Legacy mappings for backward compatibility
                'Proficient': 1.0,
                'OK': 0.6,
                'No signal': 0.0
            }
            
            # Check for unexpected categories
            unique_values = df[dimension].unique()
            unexpected = [val for val in unique_values if pd.notna(val) and val not in score_mapping]
            if unexpected:
                logger.error(f"Unexpected assessment categories in {dimension}: {unexpected}")
                logger.error(f"Valid categories are: High, Medium, Low, No Signal")
                return None
            
            # Apply scoring (store as percentages)
            df[score_col] = df[dimension].map(score_mapping).fillna(0.0) * 100
            
            # Add weighted contribution to total score (convert back to 0-1 scale for weighting)
            weighted_scores += (df[score_col] / 100) * (weight / 100)
        
        # Set total score (already on 100-point scale since weights sum to 100)
        df['total_score'] = weighted_scores * 100
        
        # Apply risk penalty (up to 20% reduction)
        risk_count = df['risks'].notna().astype(int)  # Count risks
        df['risk_penalty'] = risk_count * 0.2  # 20% penalty per risk
        df['total_score'] *= (1 - df['risk_penalty'])
        
        # Apply highlight bonus (up to 10% increase)
        highlight_count = df['highlights'].notna().astype(int)  # Count highlights
        df['highlight_bonus'] = highlight_count * 0.1  # 10% bonus per highlight
        df['total_score'] *= (1 + df['highlight_bonus'])
        
        # Rank the results
        df['rank'] = df['total_score'].rank(ascending=False, method='min').astype(int)
        df = df.sort_values('rank')
        
        # Save results
        df.to_csv(output_file, index=False)
        logger.info(f"Ranking complete. Results saved to {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error scoring and ranking resumes: {str(e)}", exc_info=True)
        return None

def main():
    """Command-line interface for resume ranking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Score and rank resumes based on extracted dimensions")
    parser.add_argument("input_file", help="Path to CSV file containing extracted dimensions")
    parser.add_argument("--output", "-o", default="ranked_resumes.csv",
                       help="Output CSV file path (default: ranked_resumes.csv)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        logger.error(f"Input file does not exist: {args.input_file}")
        sys.exit(1)
    
    result = score_and_rank_resumes(args.input_file, args.output)
    
    if result is None:
        sys.exit(1)
    
    # Print summary of top candidates
    print("\nTop Candidates Summary:")
    print("=" * 50)
    top_5 = result.head().to_dict('records')
    
    for row in top_5:
        print(f"\nRank {int(row['rank'])} - Score: {float(row['total_score']):.1f}%")
        print(f"File: {row['resume_file']}")
        print(f"Name: {str(row['chinese_name'])}")
        if pd.notna(row['highlights']):
            print(f"Key Strengths: {str(row['highlights'])}")
        if pd.notna(row['risks']):
            print(f"Risks: {str(row['risks'])}")
        
        # Print dimension scores
        print("\nDimension Scores:")
        for dimension, weight in role.dimension_weights.items():
            score_col = f"{dimension}_score"
            if score_col in row:
                score = float(row[score_col])
                print(f"- {dimension.replace('_', ' ').title()} ({weight}%): {score:.1f}%")

if __name__ == "__main__":
    main() 