from abc import ABC, abstractmethod
from typing import Dict, Type, List
from pydantic import BaseModel, Field, create_model

class BaseRole(ABC):
    """Base class for role-specific configurations."""
    
    @property
    @abstractmethod
    def role_name(self) -> str:
        """Return the name of the role."""
        pass
    
    @property
    @abstractmethod
    def prompt_template(self) -> str:
        """Return the prompt template for this role."""
        pass
    
    @property
    @abstractmethod
    def analysis_model_fields(self) -> Dict[str, tuple]:
        """
        Return the fields for the analysis model.
        Each field should be a tuple of (type, Field descriptor).
        Example:
        {
            'technical_skill': (str, Field(description="Assessment of technical skills")),
            'leadership': (str, Field(description="Leadership capabilities"))
        }
        """
        pass
    
    @property
    @abstractmethod
    def dimension_weights(self) -> Dict[str, float]:
        """
        Return the scoring weights for each dimension.
        The weights should sum to 100.
        Example: {'technical_skill': 40, 'leadership': 30, 'communication': 30}
        """
        pass
    
    @property
    def common_fields(self) -> Dict[str, tuple]:
        """Return fields that are common to all roles."""
        return {
            'chinese_name': (str, Field(None, description="Chinese name from the resume")),
            'expected_salary': (str, Field(None, description="Expected salary if mentioned")),
            'years_of_experience': (str, Field(None, description="Years of experience in relevant roles")),
            'risks': (str, Field(None, description="Potential risks and lowlights")),
            'highlights': (str, Field(None, description="Notable highlights and strengths"))
        }
    
    def create_analysis_model(self) -> Type[BaseModel]:
        """Create a Pydantic model for this role's analysis results."""
        # Combine common fields with role-specific fields
        all_fields = {**self.common_fields, **self.analysis_model_fields}
        
        # Create the model dynamically
        model_name = f"{self.role_name.replace(' ', '')}AnalysisResult"
        return create_model(
            model_name,
            __base__=BaseModel,
            **all_fields
        )
    
    def get_ordered_fields(self) -> List[str]:
        """Return ordered list of fields for CSV output."""
        # Start with common non-evidence fields
        fields = ['chinese_name', 'expected_salary', 'years_of_experience']
        
        # Add role-specific fields with evidence pairs
        for field in self.analysis_model_fields.keys():
            if field.endswith('_evidence'):
                continue
            fields.append(field)
            evidence_field = f"{field}_evidence"
            if evidence_field in self.analysis_model_fields:
                fields.append(evidence_field)
        
        # Add final common fields
        fields.extend(['risks', 'highlights'])
        return fields
    
    def validate_weights(self) -> None:
        """Validate that weights sum to 100."""
        total = sum(self.dimension_weights.values())
        if not (99.5 <= total <= 100.5):  # Allow for small floating point errors
            raise ValueError(
                f"Dimension weights for {self.role_name} sum to {total}, should sum to 100"
            ) 