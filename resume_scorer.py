import pandas as pd
import logging
from typing import Dict, List
import logging_config

logger = logging.getLogger(__name__)

# Scoring weights for each dimension (total = 100)
DIMENSION_WEIGHTS = {
    'english_proficiency': 15,  # Critical for global team communication
    'us_saas_familiarity': 15,  # Critical for tool adoption
    'technical_breadth': 15,    # Important for IT role coverage
    'it_operation': 12,         # Core job requirement
    'architecture_capability': 10,  # Important for system design
    'project_leadership': 10,    # Important for team impact
    'communication_skill': 8,    # Important for stakeholder management
    'hungry_for_excellence': 8,  # Important for growth
    'attention_to_detail': 7,    # Good to have
}

# Scoring rubric for categorical assessments
CATEGORICAL_SCORES = {
    'english_proficiency': {
        'Proficient': 1.0,
        'OK': 0.6,
        'No signal': 0.0
    },
    'us_saas_familiarity': {
        'High': 1.0,
        'Low': 0.0,  # Dealbreaker
        'No signal': 0.3
    },
    'technical_breadth': {
        'High': 1.0,
        'Medium': 0.7,
        'Low': 0.3
    },
    'it_operation': {
        'High': 1.0,
        'Medium': 0.7,
        'Low': 0.3
    }
}

def score_dimension(value: str, dimension: str) -> float:
    """Score a single dimension based on its assessment value."""
    # For dimensions with specific scoring rubrics
    if dimension in CATEGORICAL_SCORES:
        return CATEGORICAL_SCORES[dimension].get(value, 0.5)
    
    # For other dimensions, use text analysis for scoring
    value = value.lower() if value else ""
    
    # Strong positive indicators
    if any(word in value for word in ['excellent', 'strong', 'extensive', 'significant', 'proven']):
        return 1.0
    # Positive indicators
    elif any(word in value for word in ['good', 'demonstrated', 'solid', 'capable']):
        return 0.8
    # Neutral or moderate indicators
    elif any(word in value for word in ['some', 'basic', 'moderate', 'average']):
        return 0.6
    # Weak or negative indicators
    elif any(word in value for word in ['limited', 'weak', 'minimal', 'no']):
        return 0.3
    # Default score for unclear assessments
    else:
        return 0.5

def calculate_resume_score(row: pd.Series) -> Dict[str, float]:
    """Calculate the overall score and dimension scores for a single resume."""
    dimension_scores = {}
    total_score = 0
    total_weight = sum(DIMENSION_WEIGHTS.values())
    
    for dimension, weight in DIMENSION_WEIGHTS.items():
        value = row[dimension]
        score = score_dimension(value, dimension)
        weighted_score = (score * weight) / total_weight
        
        dimension_scores[f"{dimension}_score"] = score
        total_score += weighted_score
    
    # Add risk penalty (up to 20% reduction)
    if pd.notna(row['risks']):
        risk_penalty = len(row['risks'].split('.')) * 0.05  # 5% per risk point
        risk_penalty = min(risk_penalty, 0.2)  # Cap at 20%
        total_score *= (1 - risk_penalty)
    
    # Add highlight bonus (up to 10% increase)
    if pd.notna(row['highlights']):
        highlight_bonus = len(row['highlights'].split('.')) * 0.025  # 2.5% per highlight
        highlight_bonus = min(highlight_bonus, 0.1)  # Cap at 10%
        total_score *= (1 + highlight_bonus)
    
    # Ensure final score is between 0 and 1
    total_score = max(0, min(1, total_score))
    
    return {
        'total_score': total_score,
        **dimension_scores
    }

def score_resumes(input_file: str, output_file: str = None) -> pd.DataFrame:
    """Score and rank resumes from a CSV file."""
    logger.info(f"Reading resume analysis from {input_file}")
    df = pd.read_csv(input_file)
    
    # Calculate scores for each resume
    logger.info("Calculating scores for each resume")
    scores = []
    for _, row in df.iterrows():
        scores.append(calculate_resume_score(row))
    
    # Add scores to the dataframe
    score_df = pd.DataFrame(scores)
    df = pd.concat([df, score_df], axis=1)
    
    # Sort by total score in descending order
    df = df.sort_values('total_score', ascending=False)
    
    # Add rank column
    df['rank'] = range(1, len(df) + 1)
    
    # Reorder columns to put rank and scores first
    score_cols = ['rank', 'total_score'] + [col for col in df.columns if col.endswith('_score')]
    other_cols = [col for col in df.columns if col not in score_cols]
    df = df[score_cols + other_cols]
    
    if output_file:
        logger.info(f"Saving ranked results to {output_file}")
        df.to_csv(output_file, index=False)
    
    return df

def main():
    """Command-line interface for resume scoring."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python resume_scorer.py <input_csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = input_file.replace('.csv', '_ranked.csv')
    
    try:
        df = score_resumes(input_file, output_file)
        print("\nTop 5 Candidates:")
        print("=" * 50)
        
        # Convert to dictionary format for easier access
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
            for dimension in DIMENSION_WEIGHTS.keys():
                score = float(row[f"{dimension}_score"])
                print(f"- {dimension.replace('_', ' ').title()}: {score:.2f}")
    
    except Exception as e:
        logger.error(f"Error processing resumes: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    logging_config.set_log_level(logging.INFO)
    main() 