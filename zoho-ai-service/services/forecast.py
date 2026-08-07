import logging
from datetime import datetime, timedelta

import numpy as np
from sklearn.linear_model import LinearRegression

from config import settings
from services.forecast_types import (
    ForecastInput,
    ForecastResult,
    ForecastWarning,
)
from services.zoho_data_service import ZohoDataService

logger = logging.getLogger(__name__)


class ForecastEngine:
    def __init__(self, data_service: ZohoDataService):
        self._data_service = data_service

    def forecast(self, input_data: ForecastInput) -> ForecastResult:
        monthly = self._compute_monthly_expenses(input_data.project_id)

        if len(monthly) < settings.forecast_min_data_points:
            return ForecastResult(
                project_id=input_data.project_id,
                horizon_days=input_data.horizon_days,
                forecast_total=0.0,
                confidence_low=0.0,
                confidence_high=0.0,
                method="none",
                warning=ForecastWarning.INSUFFICIENT_DATA.value,
            )

        return self._ensemble_forecast(
            monthly, input_data.horizon_days, input_data.project_id
        )

    def _compute_monthly_expenses(
        self, project_id: str
    ) -> list[float]:
        result = self._data_service.get_project_expenses(
            project_id, "", ""
        )
        if not result["success"]:
            logger.warning(
                "Failed to fetch expenses for %s: %s",
                project_id,
                result["error"],
            )
            return []
        by_component = result["data"].get("by_component", [])
        totals = [c["total"] for c in by_component]
        return totals if totals else []

    def _linear_regression_forecast(
        self,
        monthly_expenses: list[float],
        horizon_days: int,
        project_id: str,
    ) -> ForecastResult:
        months_out = max(1, horizon_days // 30)
        n = len(monthly_expenses)
        X = np.array(range(n)).reshape(-1, 1)
        y = np.array(monthly_expenses)

        model = LinearRegression()
        model.fit(X, y)

        future_X = np.array(
            range(n, n + months_out)
        ).reshape(-1, 1)
        predictions = model.predict(future_X)

        residuals = y - model.predict(X)
        residual_std = np.std(residuals) if len(residuals) > 1 else 0

        forecast_total = float(predictions.sum())
        interval = 2 * residual_std * months_out

        return ForecastResult(
            project_id=project_id,
            horizon_days=horizon_days,
            forecast_total=round(forecast_total, 2),
            confidence_low=round(
                max(0, forecast_total - interval), 2
            ),
            confidence_high=round(forecast_total + interval, 2),
            method="linear_regression",
            monthly_breakdown=[
                {
                    "month": i + 1,
                    "predicted": round(float(p), 2),
                }
                for i, p in enumerate(predictions)
            ],
        )

    def _moving_average_forecast(
        self,
        monthly_expenses: list[float],
        horizon_days: int,
    ) -> ForecastResult:
        months_out = max(1, horizon_days // 30)
        window = min(3, len(monthly_expenses))
        avg = np.mean(monthly_expenses[-window:])

        predictions = [avg] * months_out
        forecast_total = avg * months_out

        return ForecastResult(
            project_id="",
            horizon_days=horizon_days,
            forecast_total=round(forecast_total, 2),
            confidence_low=round(
                max(0, forecast_total * 0.8), 2
            ),
            confidence_high=round(forecast_total * 1.2, 2),
            method="moving_average",
            monthly_breakdown=[
                {
                    "month": i + 1,
                    "predicted": round(avg, 2),
                }
                for i in range(months_out)
            ],
        )

    def _ensemble_forecast(
        self,
        monthly_expenses: list[float],
        horizon_days: int,
        project_id: str,
    ) -> ForecastResult:
        lr_result = self._linear_regression_forecast(
            monthly_expenses, horizon_days, project_id
        )
        ma_result = self._moving_average_forecast(
            monthly_expenses, horizon_days
        )

        avg_total = (
            lr_result.forecast_total + ma_result.forecast_total
        ) / 2
        wide_low = min(
            lr_result.confidence_low, ma_result.confidence_low
        )
        wide_high = max(
            lr_result.confidence_high, ma_result.confidence_high
        )

        warnings = self._check_warnings(project_id)
        milestone_detected = self._detect_milestone_billing(
            project_id
        )

        retention_held = None
        available_budget = None
        budget_data = self._data_service.get_project_budget(
            project_id
        )
        if budget_data["success"]:
            data = budget_data["data"]
            total_budget = data.get("total_budget", 0)
            retention_pct = data.get("retention_pct", 0)
            if retention_pct and retention_pct > 0:
                retention_held = round(
                    total_budget * retention_pct / 100, 2
                )
                available_budget = round(
                    total_budget - retention_held, 2
                )
                warnings.append(
                    f"retention_held={retention_held}"
                )

        if milestone_detected:
            warnings.append(
                ForecastWarning.MILESTONE_BILLING_DETECTED.value
            )

        return ForecastResult(
            project_id=project_id,
            horizon_days=horizon_days,
            forecast_total=round(avg_total, 2),
            confidence_low=round(wide_low, 2),
            confidence_high=round(wide_high, 2),
            method="ensemble",
            monthly_breakdown=lr_result.monthly_breakdown,
            warning="; ".join(warnings) if warnings else None,
            retention_held=retention_held,
            available_budget=available_budget,
        )

    def _check_warnings(
        self, project_id: str
    ) -> list[str]:
        warnings_list: list[str] = []
        return warnings_list

    def _detect_milestone_billing(
        self, project_id: str
    ) -> bool:
        result = self._data_service.get_project_budget(
            project_id
        )
        if not result["success"]:
            return False
        data = result["data"]
        components = data.get("components", [])
        return len(components) > 0 and any(
            c.get("name", "").lower() in [
                "milestone",
                "foundation",
                "structure",
                "finishing",
            ]
            for c in components
        )
