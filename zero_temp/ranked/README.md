Analyzing 3 ranking files:
- resume_ranked-2.csv
- resume_ranked-3.csv
- resume_ranked-1.csv

Top-5 Overlap Analysis:
Rankings 1 and 2:
- 4 out of 5 resumes overlap (80.0%)
Rankings 1 and 3:
- 4 out of 5 resumes overlap (80.0%)
Rankings 2 and 3:
- 4 out of 5 resumes overlap (80.0%)

Top-10 Overlap Analysis:
Rankings 1 and 2:
- 10 out of 10 resumes overlap (100.0%)
Rankings 1 and 3:
- 10 out of 10 resumes overlap (100.0%)
Rankings 2 and 3:
- 10 out of 10 resumes overlap (100.0%)

Kendall's tau correlation coefficients:

Between resume_ranked-2.csv and resume_ranked-3.csv:
τ = 0.885 (p-value: 0.000)
- Statistically significant correlation (p < 0.05)
- Strong correlation

Between resume_ranked-2.csv and resume_ranked-1.csv:
τ = 0.872 (p-value: 0.000)
- Statistically significant correlation (p < 0.05)
- Strong correlation

Between resume_ranked-3.csv and resume_ranked-1.csv:
τ = 0.853 (p-value: 0.000)
- Statistically significant correlation (p < 0.05)
- Strong correlation

Overall Kendall's W (Coefficient of Concordance): 0.976
p-value: 0.000

Interpretation of Kendall's W:
Very strong agreement between all rankings

# Summary of Results

The analysis reveals high consistency across different ranking runs:

1. **Top-K Overlap**:
   - For top-5: There's an 80% overlap between all pairs of rankings (4 out of 5 resumes are the same)
   - For top-10: There's a perfect 100% overlap between all pairs (all 10 resumes are the same)

2. **Kendall's Tau**:
   - All pairs show very strong correlations (τ > 0.85)
   - All correlations are statistically significant (p < 0.05)

3. **Kendall's W**:
   - Shows very strong agreement (W = 0.976) between all rankings
   - The result is statistically significant (p < 0.05)

This suggests that the ranking system is producing highly consistent results, especially for the top candidates. The perfect overlap in the top-10 candidates across all runs indicates particularly strong reliability for identifying the best matches.
