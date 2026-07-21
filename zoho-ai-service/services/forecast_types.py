from enum import Enum

from pydantic import BaseModel, Field


class ForecastWarning(str, Enum):
    INSUFFICIENT_DATA = "insufficient_data"
    LOOKBACK_BIAS_RISK = "lookback_bias_risk"
    MILESTONE_BILLING_DETECTED = "milestone_billing_detected"
    SEASONALITY_LIMITED = "seasonality_limited"


class ForecastInput(BaseModel):
    project_id: str = Field(description="Zoho Creator project ID")
    horizon_days: int = Field(
        default=30, description="Forecast horizon: 30, 60, or 90 days"
    )


class ForecastResult(BaseModel):
    project_id: str
    horizon_days: int
    forecast_total: float = Field(
        description="Predicted total spend at horizon"
    )
    confidence_low: float = Field(
        description="Lower bound of 95% confidence interval"
    )
    confidence_high: float = Field(
        description="Upper bound of 95% confidence interval"
    )
    method: str = Field(
        description="Forecast method: linear_regression, moving_average, ensemble, or none"
    )
    monthly_breakdown: list[dict] = Field(
        default_factory=list,
        description="Monthly breakdown of forecast",
    )
    warning: str | None = Field(
        default=None,
        description="Warning code if data quality is insufficient",
    )
    retention_held: float | None = Field(
        default=None,
        description="Retention money held from budget",
    )
    available_budget: float | None = Field(
        default=None,
        description="Budget minus retention",
    )
