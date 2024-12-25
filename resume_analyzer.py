import os
from dotenv import load_dotenv
import pandas as pd
import glob
from resume_analysis_core import ResumeAnalyzer, ResumeAnalysisResult

# Load environment variables
load_dotenv()

class ResumeProcessor:
    def __init__(self):
        self.analyzer = ResumeAnalyzer()

    def analysis_to_dict(self, analysis: ResumeAnalysisResult, resume_file: str) -> list[dict]:
        """Convert analysis result to a list of dictionaries for CSV output."""
        result = []
        for field, value in analysis.model_dump().items():
            if field.endswith('_evidence'):
                continue
            if value is not None:
                evidence_field = field + '_evidence'
                evidence = getattr(analysis, evidence_field, None)
                result.append({
                    'resume_file': resume_file,
                    'dimension': field,
                    'assessment': value,
                    'evidence': evidence
                })
        return result

    def process_directory(self, directory_path: str, output_file: str = "resume_analysis.csv"):
        """Process all PDF resumes in a directory and save results to CSV."""
        all_results = []
        
        pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
        
        for pdf_file in pdf_files:
            try:
                print(f"Processing {pdf_file}...")
                analysis = self.analyzer.analyze_resume_file(pdf_file)
                results = self.analysis_to_dict(analysis, os.path.basename(pdf_file))
                all_results.extend(results)
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
        
        df = pd.DataFrame(all_results)
        df.to_csv(output_file, index=False)
        print(f"Analysis complete. Results saved to {output_file}")

def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        return

    processor = ResumeProcessor()
    
    directory_path = input("Enter the directory path containing the resumes: ")
    
    if not os.path.exists(directory_path):
        print("Error: Directory does not exist")
        return
    
    processor.process_directory(directory_path)

if __name__ == "__main__":
    main() 