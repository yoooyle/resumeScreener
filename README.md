# Resume Fact Extractor

This Python program extracts structured information from PDF resumes using OpenAI's GPT-4o, scores them based on role-specific dimensions, and provides ranked results.

## Features

- PDF resume text extraction with two engines:
  - PyMuPDF (default): Optimized extraction with better handling of complex layouts
  - PyPDF (legacy): Basic extraction for simple PDFs
- Structured dimension extraction using GPT-4o
- Role-specific dimensions and scoring
- Detailed evidence-based assessments
- One-row-per-resume CSV output with paired assessment-evidence columns
- Automated scoring and ranking system
- Configurable logging levels
- Both CLI and API usage
- Centralized role configuration

## Available Roles

### IT Manager
Focuses on leadership abilities, technical breadth, and operational excellence. Key dimensions include:
- English proficiency (15%)
- US SaaS familiarity (15%)
- Technical breadth (15%)
- IT operations (12%)
- Architecture capability (10%)
- Project leadership (10%)
- Communication skills (8%)
- Drive for excellence (8%)
- Attention to detail (7%)

### Software Engineer
Focuses on technical skills, coding proficiency, and engineering practices. Key dimensions include:
- Coding proficiency (20%)
- System design (15%)
- Engineering practices (12%)
- Problem solving (10%)
- Tech stack breadth (10%)
- Backend skills (8%)
- DevOps knowledge (7%)
- English proficiency (7%)
- Team collaboration (6%)
- Learning ability (5%)

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

1. Extract dimensions from a single resume:
```bash
# Basic usage (defaults to IT Manager role and optimized PDF extraction)
python ai_resume_extractor.py path/to/resume.pdf

# Specify role
python ai_resume_extractor.py path/to/resume.pdf -r software_engineer

# Use legacy PDF extraction
python ai_resume_extractor.py path/to/resume.pdf --legacy-pdf

# Control logging verbosity
python ai_resume_extractor.py path/to/resume.pdf --log-level DEBUG  # Full debug output
python ai_resume_extractor.py path/to/resume.pdf -v                 # Verbose (same as DEBUG)
python ai_resume_extractor.py path/to/resume.pdf -q                 # Quiet (ERROR level only)
python ai_resume_extractor.py path/to/resume.pdf -l WARNING        # Custom level
```

2. Extract dimensions from multiple resumes:
```bash
# Basic usage
python resumes_extractor.py /path/to/resume/directory

# Specify role and output file
python resumes_extractor.py /path/to/resume/directory -r software_engineer -o custom_dimensions.csv --legacy-pdf
```

3. Score and rank extracted dimensions:
```bash
# Basic usage
python resumes_ranker.py extracted_dimensions.csv

# Specify output file
python resumes_ranker.py extracted_dimensions.csv -o ranked_results.csv
```

4. Complete pipeline (extract and rank in one step):
```bash
# Basic usage
python analyze_and_rank.py /path/to/resume/directory

# Specify role and output prefix
python analyze_and_rank.py -r software_engineer -p custom_prefix /path/to/resume/directory

# Force rerun all steps
python analyze_and_rank.py -f /path/to/resume/directory

# Control logging verbosity
python analyze_and_rank.py /path/to/resume/directory -v  # Verbose output
```

The analyze_and_rank.py script supports the following options:
- `-r, --role`: Role to analyze for (default: "it_manager")
- `-f, --force`: Force rerun all steps even if output files exist
- `-p PREFIX, --prefix PREFIX`: Custom prefix for output files (default: "resume")
  - Creates PREFIX_extracted.csv and PREFIX_ranked.csv
- `-v, --verbose`: Enable debug logging
- `-q, --quiet`: Only show error messages
- `-l LEVEL, --log-level LEVEL`: Set specific logging level
- `--legacy-pdf`: Use PyPDF instead of PyMuPDF for extraction

By default, the script will reuse existing output files if they exist, making it efficient for iterative analysis.

### Python API

```python
# Extract dimensions from a single resume
from ai_resume_extractor import extract_resume

# Default settings (IT Manager role, optimized PDF extraction)
result = extract_resume("path/to/resume.pdf")

# Specify role and PDF extraction method
result = extract_resume(
    "path/to/resume.pdf",
    role="software_engineer",
    use_optimized_pdf=True  # Set to False for legacy extraction
)

# Extract dimensions from multiple resumes
from resumes_extractor import ResumesExtractor

# Default settings
extractor = ResumesExtractor()

# Specify role and PDF extraction method
extractor = ResumesExtractor(
    role="software_engineer",
    use_optimized_pdf=True  # Set to False for legacy extraction
)
df = extractor.extract_from_directory("/path/to/resume/directory")

# Score and rank resumes
from resumes_ranker import score_and_rank_resumes
df = score_and_rank_resumes("extracted_dimensions.csv", "ranked_results.csv")

# Complete pipeline
from analyze_and_rank import extract_and_rank
extracted_csv, ranked_csv, df = extract_and_rank(
    "/path/to/resume/directory",
    role="software_engineer",
    output_prefix="custom_name",
    force_rerun=False,
    use_optimized_pdf=True  # Set to False for legacy extraction
)
```

### Logging Configuration

```python
import logging
import logging_config

# Set global log level
logging_config.set_log_level(logging.DEBUG)  # For detailed output
logging_config.set_log_level(logging.INFO)   # For normal operation
```

## Output Format

### Initial Extraction CSV
The first-stage output uses a one-row-per-resume format with assessment and evidence columns paired together. The exact columns depend on the role selected, but follow this pattern:

```csv
resume_file, chinese_name, expected_salary, years_of_experience,
dimension1, dimension1_evidence,
dimension2, dimension2_evidence,
...
risks, highlights
```

### Ranked Results CSV
The second-stage output adds scoring columns and ranks candidates:

```csv
rank, total_score, dimension1_score, dimension2_score, ..., [all columns from initial extraction]
```

## Adding New Roles

To add a new role:

1. Create a new role class in the `roles` directory:
```python
from typing import Dict
from pydantic import Field
from .base_role import BaseRole

class NewRole(BaseRole):
    @property
    def role_name(self) -> str:
        return "Role Name"
    
    @property
    def prompt_template(self) -> str:
        return """Role-specific prompt template"""
    
    @property
    def analysis_model_fields(self) -> Dict[str, tuple]:
        return {
            'dimension1': (str, Field(description="...")),
            'dimension1_evidence': (str, Field(description="...")),
            # Add more dimensions
        }
    
    @property
    def dimension_weights(self) -> Dict[str, float]:
        return {
            'dimension1': 30.0,  # Weights must sum to 100
            # Add more weights
        }
```

2. Register the role in `roles/registry.py`:
```python
from .new_role import NewRole

class RoleRegistry:
    _roles: Dict[str, Type[BaseRole]] = {
        'it_manager': ITManagerRole,
        'software_engineer': SoftwareEngineerRole,
        'new_role': NewRole,  # Add your new role here
    }
```

3. Export the role in `roles/__init__.py`:
```python
from .new_role import NewRole
__all__ = [..., 'NewRole']
```

## Project Structure

- `ai_resume_extractor.py`: Core AI-based dimension extraction from single resumes
- `resumes_extractor.py`: Batch processing of multiple resumes
- `resumes_ranker.py`: Scoring and ranking system
- `analyze_and_rank.py`: Combined extraction and ranking pipeline
- `roles/`: Role-specific configurations
  - `base_role.py`: Base role interface
  - `it_manager.py`: IT Manager role configuration
  - `software_engineer.py`: Software Engineer role configuration
  - `registry.py`: Role registry and management
- `logging_config.py`: Shared logging configuration