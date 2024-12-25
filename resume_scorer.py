import os
import sys
import logging
import pandas as pd
from typing import Optional
from roles import RoleRegistry
import logging_config

logger = logging.getLogger(__name__)

def calculate_dimension_score(value: str, dimension: str) -> float:
    """
    Calculate score for a dimension based on its value.
    
    Args:
        value: The assessment value (e.g., "High", "Medium", "Low", "Proficient", etc.)
        dimension: The dimension being scored (for context-specific scoring)
    
    Returns:
        Score between 0 and 1
    """
    # Standardize value for comparison
    value = value.lower().strip()
    
    # Handle different scoring scales
    if value in ['high', 'proficient']:
        return 1.0
    elif value in ['medium', 'ok']:
        return 0.6
    elif value in ['low', 'no signal']:
        return 0.2
    else:
        logger.warning(f"Unknown value '{value}' for dimension '{dimension}', defaulting to 0")
        return 0.0

def calculate_risk_penalty(risks: Optional[str]) -> float:
    """Calculate penalty factor (0-0.2) based on number and severity of risks."""
    if not risks or pd.isna(risks):
        return 0.0
    
    # Count risk factors (simple implementation - could be made more sophisticated)
    risk_count = len([r for r in risks.split('.') if len(r.strip()) > 0])
    return min(0.2, risk_count * 0.05)  # 5% penalty per risk, max 20%

def calculate_highlight_bonus(highlights: Optional[str]) -> float:
    """Calculate bonus factor (0-0.1) based on number and quality of highlights."""
    if not highlights or pd.isna(highlights):
        return 0.0
    
    # Count highlight factors (simple implementation - could be made more sophisticated)
    highlight_count = len([h for h in highlights.split('.') if len(h.strip()) > 0])
    return min(0.1, highlight_count * 0.025)  # 2.5% bonus per highlight, max 10%

def score_resumes(input_file: str, output_file: Optional[str] = None) -> pd.DataFrame:
    """
    Score and rank resumes based on their analysis results.
    
    Args:
        input_file: Path to the input CSV file with analysis results
        output_file: Optional path to save ranked results (if None, only returns DataFrame)
    
    Returns:
        DataFrame with scored and ranked results
    """
    try:
        # Read analysis results
        df = pd.read_csv(input_file)
        
        # Detect role from the columns present
        role_detected = False
        for role_name in RoleRegistry.available_roles():
            role = RoleRegistry.get_role(role_name)
            role_fields = set(role.get_ordered_fields())
            if role_fields.issubset(set(df.columns)):
                logger.info(f"Detected role: {role.role_name}")
                role_detected = True
                break
        
        if not role_detected:
            raise ValueError("Could not detect role from CSV columns")
        
        # Calculate dimension scores
        dimension_scores = {}
        for dimension, weight in role.dimension_weights.items():
            if dimension in df.columns:
                dimension_scores[f"{dimension}_score"] = (
                    df[dimension].apply(lambda x: calculate_dimension_score(x, dimension)) * 
                    (weight / 100)
                )
        
        # Add dimension scores to DataFrame
        for col, scores in dimension_scores.items():
            df[col] = scores
        
        # Calculate risk penalties and highlight bonuses
        df['risk_penalty'] = df['risks'].apply(calculate_risk_penalty)
        df['highlight_bonus'] = df['highlights'].apply(calculate_highlight_bonus)
        
        # Calculate total score with adjustments
        base_score = sum(dimension_scores.values())
        df['total_score'] = (
            base_score * 
            (1 - df['risk_penalty']) * 
            (1 + df['highlight_bonus'])
        )
        
        # Rank candidates
        df['rank'] = df['total_score'].rank(ascending=False, method='min')
        df = df.sort_values('rank')
        
        # Save results if output file specified
        if output_file:
            # Reorder columns for better readability
            score_cols = [c for c in df.columns if c.endswith('_score')]
            other_cols = [c for c in df.columns if not c.endswith('_score') 
                         and c not in ['rank', 'total_score']]
            col_order = ['rank', 'total_score'] + score_cols + other_cols
            df = df[col_order]
            
            df.to_csv(output_file, index=False)
            logger.info(f"Ranked results saved to: {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error scoring resumes: {str(e)}", exc_info=True)
        raise

def main():
    """Command-line interface for resume scoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Score and rank analyzed resumes")
    parser.add_argument("input_file", help="Path to the input CSV file with analysis results")
    parser.add_argument("--output", "-o", help="Path to save ranked results (optional)")
    
    args = parser.parse_args()
    
    try:
        df = score_resumes(args.input_file, args.output)
        
        # Print summary of top candidates
        print("\nTop 5 Candidates:")
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
                    score = float(row[col])
                    print(f"- {col.replace('_score', '').replace('_', ' ').title()}: {score:.2f}")
    
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Set up logging
    logging_config.set_log_level(logging.INFO)
    main() 