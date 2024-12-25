from typing import Dict, Type
from .base_role import BaseRole
from .it_manager import ITManagerRole
from .software_engineer import SoftwareEngineerRole

class RoleRegistry:
    """Registry for managing available role configurations."""
    
    _roles: Dict[str, Type[BaseRole]] = {
        'it_manager': ITManagerRole,
        'software_engineer': SoftwareEngineerRole,
    }
    
    @classmethod
    def get_role(cls, role_name: str) -> BaseRole:
        """
        Get a role configuration by name.
        
        Args:
            role_name: Name of the role (case-insensitive)
        
        Returns:
            An instance of the role configuration
        
        Raises:
            ValueError: If role_name is not found
        """
        role_key = role_name.lower().replace(' ', '_')
        if role_key not in cls._roles:
            available = ', '.join(cls._roles.keys())
            raise ValueError(
                f"Role '{role_name}' not found. Available roles: {available}"
            )
        return cls._roles[role_key]()
    
    @classmethod
    def available_roles(cls) -> list[str]:
        """Get list of available role names."""
        return list(cls._roles.keys())
    
    @classmethod
    def register_role(cls, role_key: str, role_class: Type[BaseRole]) -> None:
        """
        Register a new role configuration.
        
        Args:
            role_key: Key for the role (lowercase, underscores)
            role_class: The role configuration class
        """
        if not issubclass(role_class, BaseRole):
            raise TypeError(f"{role_class.__name__} must inherit from BaseRole")
        
        # Validate the role configuration
        role = role_class()
        role.validate_weights()
        
        cls._roles[role_key] = role_class 