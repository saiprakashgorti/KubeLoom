"""
Experiment definition module for KubeLoom.
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class FaultType(str, Enum):
    """Supported fault types."""

    POD_DELETION = "pod-deletion"
    # Add more fault types here as they are implemented


class Experiment(BaseModel):
    """
    Represents a chaos experiment configuration.
    """

    target_kind: str = Field(
        ...,
        description="Kind of the target resource (e.g., 'deployment', 'statefulset')",
    )
    target_name: str = Field(..., description="Name of the target resource")
    namespace: str = Field(default="default", description="Kubernetes namespace")
    fault_type: FaultType = Field(..., description="Type of fault to inject")
    fault_params: Dict[str, Any] = Field(
        default_factory=dict, description="Parameters for the fault injection"
    )
    description: Optional[str] = Field(
        None, description="Optional description of the experiment"
    )

    class Config:
        use_enum_values = True

    def validate_target(self) -> bool:
        """
        Validate that the target resource exists and is accessible.
        This is a placeholder for actual validation logic.
        """
        # TODO: Implement actual validation logic
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the experiment to a dictionary representation.
        """
        return self.model_dump()
