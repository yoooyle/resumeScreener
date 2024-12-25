from typing import Dict, Optional

# Define the order and relationships of fields
FIELD_PAIRS: Dict[str, Optional[str]] = {
    'chinese_name': None,
    'expected_salary': None,
    'years_of_experience': None,
    'english_proficiency': 'english_evidence',
    'communication_skill': 'communication_evidence',
    'us_saas_familiarity': 'us_saas_evidence',
    'technical_breadth': 'technical_breadth_evidence',
    'architecture_capability': 'architecture_evidence',
    'it_operation': 'it_operation_evidence',
    'project_leadership': 'leadership_evidence',
    'attention_to_detail': 'attention_evidence',
    'hungry_for_excellence': 'excellence_evidence',
    'risks': None,
    'highlights': None
}

# Get all assessment fields (fields without _evidence suffix)
ASSESSMENT_FIELDS = list(FIELD_PAIRS.keys())

# Get all evidence fields (fields with _evidence suffix)
EVIDENCE_FIELDS = [field for field in FIELD_PAIRS.values() if field is not None]

# Get field pairs for a specific field
def get_evidence_field(field: str) -> Optional[str]:
    """Get the evidence field name for a given assessment field."""
    return FIELD_PAIRS.get(field) 