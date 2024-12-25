# Resume Fact Extractor

This Python program analyzes PDF resumes using OpenAI's GPT-4o to extract structured information about candidates. It evaluates multiple dimensions including English proficiency, technical breadth, leadership experience, and more.

## Features

- PDF resume text extraction
- Structured analysis using GPT-4o
- Detailed evidence-based assessments
- One-row-per-resume CSV output
- Configurable logging levels
- Both CLI and API usage
- Centralized field configuration

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
python resume_analyzer.py /path/to/resume/directory
```

### Python API

```python
# Process a single resume
from resume_analysis_core import process_resume
result = process_resume("path/to/resume.pdf")

# Process multiple resumes
from resume_analyzer import ResumeProcessor
processor = ResumeProcessor()
processor.process_directory("/path/to/resume/directory")
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

The program evaluates candidates on multiple dimensions, organized into categories:

### Basic Information
- Chinese Name
- Expected Salary
- Years of Experience

### Skills Assessment
- English Proficiency (Proficient/OK/No signal)
- Communication Skills
- US SaaS Familiarity (High/Low/No signal)
- Technical Domain Breadth (High/Medium/Low)
- Architecture Capabilities
- IT Operations Efficiency

### Personal Qualities
- Project Leadership
- Attention to Detail
- Drive for Excellence

### Overall Assessment
- Risks and Lowlights
- Notable Highlights

## Output Format

The CSV output uses a one-row-per-resume format with:

1. Basic Information Columns:
   - resume_file
   - chinese_name
   - expected_salary
   - years_of_experience

2. Assessment Columns:
   - english_proficiency
   - communication_skill
   - us_saas_familiarity
   - technical_breadth
   - architecture_capability
   - it_operation
   - project_leadership
   - attention_to_detail
   - hungry_for_excellence
   - risks
   - highlights

3. Evidence Columns (at the end):
   - english_evidence
   - communication_evidence
   - us_saas_evidence
   - technical_breadth_evidence
   - architecture_evidence
   - it_operation_evidence
   - leadership_evidence
   - attention_evidence
   - excellence_evidence

## Project Structure

- `resume_analyzer.py`: Main script for batch processing directories
- `resume_analysis_core.py`: Core analysis functionality and models
- `field_config.py`: Centralized field configuration
- `logging_config.py`: Shared logging configuration
- `resume-extractor-prompt-draft.txt`: GPT analysis prompt 