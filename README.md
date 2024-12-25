# Resume Fact Extractor

This Python program analyzes PDF resumes using LangChain and GPT-4o to extract key facts about candidates, such as English proficiency, hunger for excellence, and technical breadth.

## Setup

1. Create a virtual environment (optional but recommended):
```bash
python -m venv myenv
source myenv/bin/activate  # On Unix/macOS
# or
myenv\Scripts\activate  # On Windows
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Place your PDF resumes in a directory
2. Run the script:
```bash
python resume_analyzer.py
```
3. When prompted, enter the path to the directory containing your PDF resumes
4. The script will process all PDF files and create a CSV file named `resume_analysis.csv` with the extracted facts

## Output Format

The output CSV file contains the following columns:
- resume_file: Name of the source PDF file
- fact_type: Type of fact extracted (e.g., "English proficiency")
- content: The extracted fact
- source_text: The exact text from the resume that supports this fact 