import pandas as pd
import numpy as np
from scipy import stats
import os
import glob
import pingouin as pg

def load_and_process_rankings(filename):
    df = pd.read_csv(filename)
    # Sort by resume_file to ensure consistent ordering
    df = df.sort_values('resume_file')
    return df['resume_file'].values, df['rank'].values

def calculate_top_k_overlap(rankings_data, k_values=[5, 10]):
    """Calculate the overlap between top-K items across different rankings."""
    n_rankings = len(rankings_data)
    results = {}
    
    for k in k_values:
        print(f"\nTop-{k} Overlap Analysis:")
        for i in range(n_rankings):
            for j in range(i+1, n_rankings):
                # Get top K resumes from each ranking
                top_k_i = set(rankings_data[i][0][rankings_data[i][1].argsort()[:k]])
                top_k_j = set(rankings_data[j][0][rankings_data[j][1].argsort()[:k]])
                
                # Calculate overlap
                overlap = len(top_k_i.intersection(top_k_j))
                overlap_percentage = (overlap / k) * 100
                
                print(f"Rankings {i+1} and {j+1}:")
                print(f"- {overlap} out of {k} resumes overlap ({overlap_percentage:.1f}%)")

def calculate_kendall_w(rankings):
    """
    Calculate Kendall's W (coefficient of concordance) for a set of rankings.
    
    Args:
        rankings: List of numpy arrays containing rankings
        
    Returns:
        tuple: (W coefficient, p-value, interpretation string)
    """
    # Convert rankings to DataFrame
    rankings_df = pd.DataFrame(np.array(rankings).T, columns=[f'Ranking_{i+1}' for i in range(len(rankings))])
    
    # Calculate parameters
    n = len(rankings_df)  # number of items being ranked
    m = len(rankings)     # number of judges
    
    # Calculate the mean rank for each item
    rank_sums = rankings_df.sum(axis=1)
    mean_rank = np.mean(rank_sums)
    
    # Calculate S (sum of squared deviations)
    S = np.sum((rank_sums - mean_rank) ** 2)
    
    # Calculate maximum possible S
    max_S = (m**2 * (n**3 - n)) / 12
    
    # Calculate W
    w = S / max_S
    
    # Calculate chi-square statistic
    chi2_stat = m * (n - 1) * w
    
    # Calculate p-value using chi-square distribution
    from scipy.stats import chi2
    p_value = 1 - chi2.cdf(chi2_stat, df=n-1)
    
    # Generate interpretation
    if w > 0.9:
        interpretation = "Very strong agreement between all rankings"
    elif w > 0.7:
        interpretation = "Strong agreement between all rankings"
    elif w > 0.5:
        interpretation = "Moderate agreement between all rankings"
    elif w > 0.3:
        interpretation = "Weak agreement between all rankings"
    else:
        interpretation = "Very weak agreement between all rankings"
    
    return w, p_value, interpretation

def analyze_rankings(folder_path):
    # Get all CSV files in the folder
    ranking_files = glob.glob(os.path.join(folder_path, "resume_ranked*.csv"))
    
    if len(ranking_files) < 2:
        print(f"Error: Found only {len(ranking_files)} ranking files. Need at least 2 files to compare.")
        return
    
    print(f"\nAnalyzing {len(ranking_files)} ranking files:")
    for file in ranking_files:
        print(f"- {os.path.basename(file)}")
    
    # Load all rankings
    rankings_data = []  # Will store tuples of (resume_files, ranks)
    rankings = []       # Will store just the ranks for backwards compatibility
    for file in ranking_files:
        resume_files, ranks = load_and_process_rankings(file)
        rankings_data.append((resume_files, ranks))
        rankings.append(ranks)
    
    # Calculate top-K overlap
    calculate_top_k_overlap(rankings_data)
    
    # Calculate pairwise Kendall's tau for all combinations
    n_files = len(ranking_files)
    print("\nKendall's tau correlation coefficients:")
    for i in range(n_files):
        for j in range(i+1, n_files):
            tau, p_value = stats.kendalltau(rankings[i], rankings[j])
            file1 = os.path.basename(ranking_files[i])
            file2 = os.path.basename(ranking_files[j])
            print(f"\nBetween {file1} and {file2}:")
            print(f"τ = {tau:.3f} (p-value: {p_value:.3f})")
            
            # Print interpretation
            if p_value < 0.05:
                print("- Statistically significant correlation (p < 0.05)")
                if abs(tau) > 0.7:
                    print("- Strong correlation")
                elif abs(tau) > 0.5:
                    print("- Moderate correlation")
                elif abs(tau) > 0.3:
                    print("- Weak correlation")
                else:
                    print("- Very weak correlation")
            else:
                print("- No statistically significant correlation")
    
    # Calculate and print Kendall's W results
    w, p_value, interpretation = calculate_kendall_w(rankings)
    print(f"\nOverall Kendall's W (Coefficient of Concordance): {w:.3f}")
    print(f"p-value: {p_value:.3f}")
    print("\nInterpretation of Kendall's W:")
    print(interpretation)

if __name__ == "__main__":
    # Analyze rankings in the specified folder
    analyze_rankings("zero_temp/ranked") 