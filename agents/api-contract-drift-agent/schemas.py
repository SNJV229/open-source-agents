from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class DriftSeverity(str, Enum):
    BREAKING = "BREAKING"
    WARNING = "WARNING"
    INFO = "INFO"


class DriftType(str, Enum):
    MISSING_ENDPOINT = "MISSING_ENDPOINT"
    EXTRA_ENDPOINT = "EXTRA_ENDPOINT"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    FIELD_REMOVED = "FIELD_REMOVED"
    FIELD_ADDED = "FIELD_ADDED"
    NULLABILITY_CHANGE = "NULLABILITY_CHANGE"
    STATUS_CODE_MISMATCH = "STATUS_CODE_MISMATCH"


class ContractDriftItem(BaseModel):
    endpoint: str = Field(description="HTTP method and path, e.g., 'POST /api/v1/users'")
    drift_type: DriftType = Field(description="Classification of the contract difference")
    severity: DriftSeverity = Field(description="Impact level on downstream microservice consumers")
    spec_state: str = Field(description="Expected behavior or schema in OpenAPI spec")
    code_state: str = Field(description="Actual behavior or schema in the backend controller code")
    remediation: str = Field(description="Concrete action item to reconcile spec and implementation")


class ContractDriftReport(BaseModel):
    summary: str = Field(description="High-level assessment of API contract parity")
    has_breaking_changes: bool = Field(description="True if any breaking change is detected")
    drift_items: List[ContractDriftItem] = Field(description="List of detected drift occurrences")
    suggested_spec_patch: Optional[str] = Field(
        description="JSON or YAML snippet to patch the OpenAPI specification to match code"
    )