from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ItemRecommendationRequest(BaseModel):
    item_id: str = Field(
        description="Zoho Creator inventory item ID"
    )


class ProcurementRecommendation(BaseModel):
    item_name: str
    current_stock: float
    reorder_point: float
    avg_consumption: float = Field(
        description="Average monthly consumption"
    )
    lead_time_days: int
    recommended_qty: float
    recommended_date: str = Field(
        description="ISO date when reorder is recommended"
    )
    priority: Literal["critical", "high", "medium", "low"]
    reasoning: str = Field(
        description="Plain English explanation of recommendation logic"
    )
    eoq: float | None = Field(
        default=None,
        description="Economic Order Quantity or None if insufficient data",
    )
    unit_cost: float | None = Field(
        default=None,
        description="Unit cost from inventory data",
    )


class ProcurementResult(BaseModel):
    recommendations: list[ProcurementRecommendation] = Field(
        default_factory=list
    )
    scan_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
