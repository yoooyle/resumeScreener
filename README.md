# Resume Fact Extractor

This Python program analyzes PDF resumes using OpenAI's GPT-4o to extract structured information about candidates. It evaluates multiple dimensions including English proficiency, technical breadth, leadership experience, and more.

## Features

- PDF resume text extraction
- Structured analysis using GPT-4o
- Detailed evidence-based assessments
- CSV output for easy analysis
- Configurable logging levels
- Both CLI and API usage

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

### Command Line Interface

1. Process a single resume:
```bash
python resume_analysis_core.py path/to/resume.pdf
```

2. Process a directory of resumes:
```bash
python resume_analyzer.py
# When prompted, enter the directory path containing the PDF resumes
```

### Python API

```python
# Process a single resume
from resume_analysis_core import process_resume
result = process_resume("path/to/resume.pdf")

# Process multiple resumes
from resume_analyzer import ResumeProcessor
processor = ResumeProcessor()
processor.process_directory("path/to/resume/directory")
```

### Logging Configuration

```python
import logging
import logging_config

# Set global log level
logging_config.set_log_level(logging.DEBUG)  # For detailed output
logging_config.set_log_level(logging.INFO)   # For normal operation
```

## Analysis Dimensions

The program evaluates candidates on multiple dimensions:

- Chinese Name & Expected Salary
- Years of Experience
- English Proficiency (Proficient/OK/No signal)
- Communication Skills
- US SaaS Familiarity (High/Low/No signal)
- Technical Domain Breadth (High/Medium/Low)
- Architecture Capabilities
- IT Operations Efficiency
- Project Leadership
- Attention to Detail
- Drive for Excellence
- Risks and Highlights

## Output Format

The CSV output contains the following columns:
- resume_file: Name of the source PDF file
- dimension: The aspect being evaluated
- assessment: The evaluation result
- evidence: Supporting text from the resume

Each dimension includes both an assessment and supporting evidence from the resume text. 