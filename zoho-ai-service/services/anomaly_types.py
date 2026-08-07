from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AnomalyFlag(BaseModel):
    project_id: str
    component: str
    expected_range: str = Field(
        description="Expected normal range as string"
    )
    actual_value: float
    severity: str = Field(
        description="Severity: low, medium, or high"
    )
    detected_by: str = Field(
        description="Method: z_score, iqr, or both"
    )
    recommendation: str = Field(
        description="Suggested action for the anomaly"
    )


class AnomalyDetectionInput(BaseModel):
    project_id: str | None = Field(
        default=None,
        description="Filter by project ID",
    )
    severity: str | None = Field(
        default=None,
        description="Filter by severity level",
    )


class AnomalyDetectionResult(BaseModel):
    anomalies: list[AnomalyFlag] = Field(default_factory=list)
    scan_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    projects_scanned: int = 0
