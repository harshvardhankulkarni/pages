from unittest.mock import MagicMock

import pytest

from services.forecast import ForecastEngine
from services.forecast_types import ForecastInput, ForecastResult, ForecastWarning


class TestForecast:
    @pytest.fixture
    def engine(self):
        mock_ds = MagicMock()
        return ForecastEngine(mock_ds)

    def test_linear_regression_known_values(self, engine):
        result = engine._linear_regression_forecast(
            [100, 110, 120], 30, "p1"
        )
        assert 125 <= result.forecast_total <= 135
        assert result.method == "linear_regression"

    def test_insufficient_data(self, engine):
        engine._data_service.get_project_expenses.return_value = {
            "success": True,
            "data": {
                "total_spent": 100,
                "by_component": [{"name": "Test", "total": 100}],
                "transaction_count": 1,
            },
        }
        result = engine.forecast(
            ForecastInput(project_id="p1", horizon_days=30)
        )
        assert result.warning == ForecastWarning.INSUFFICIENT_DATA.value
        assert result.method == "none"

    def test_moving_average(self, engine):
        result = engine._moving_average_forecast([100, 110, 120], 30)
        assert 110 <= result.forecast_total <= 130
        assert result.method == "moving_average"

    def test_ensemble_returns_both_methods(self, engine):
        engine._data_service.get_project_budget.return_value = {
            "success": True,
            "data": {
                "total_budget": 1000000,
                "components": [],
                "utilization_pct": 0,
                "retention_pct": 0,
                "retention_amount": 0,
            },
        }
        result = engine._ensemble_forecast([100, 110, 120], 30, "p1")
        assert result.method == "ensemble"
        assert result.forecast_total > 0

    def test_forecast_result_schema(self):
        result = ForecastResult(
            project_id="p1",
            horizon_days=30,
            forecast_total=1000.0,
            confidence_low=800.0,
            confidence_high=1200.0,
            method="ensemble",
        )
        data = result.model_dump()
        assert data["project_id"] == "p1"
        assert "confidence_low" in data
        assert "confidence_high" in data

    def test_milestone_detection_default(self, engine):
        engine._data_service.get_project_budget.return_value = {
            "success": True,
            "data": {
                "total_budget": 500000,
                "components": [
                    {"name": "General", "allocated": 500000, "spent": 0}
                ],
                "utilization_pct": 0,
                "retention_pct": 0,
                "retention_amount": 0,
            },
        }
        assert engine._detect_milestone_billing("p1") is False

    def test_milestone_detection_found(self, engine):
        engine._data_service.get_project_budget.return_value = {
            "success": True,
            "data": {
                "total_budget": 500000,
                "components": [
                    {"name": "Foundation", "allocated": 200000, "spent": 50000}
                ],
                "utilization_pct": 25,
                "retention_pct": 0,
                "retention_amount": 0,
            },
        }
        assert engine._detect_milestone_billing("p1") is True

    def test_retention_money_computed(self, engine):
        engine._data_service.get_project_budget.return_value = {
            "success": True,
            "data": {
                "total_budget": 5000000,
                "components": [],
                "utilization_pct": 0,
                "retention_pct": 10,
                "retention_amount": 0,
            },
        }
        result = engine._ensemble_forecast([100, 110, 120], 30, "p1")
        assert result.retention_held == 500000.0
        assert result.available_budget == 4500000.0

    def test_retention_money_no_retention(self, engine):
        engine._data_service.get_project_budget.return_value = {
            "success": True,
            "data": {
                "total_budget": 5000000,
                "components": [],
                "utilization_pct": 0,
                "retention_pct": 0,
                "retention_amount": 0,
            },
        }
        result = engine._ensemble_forecast([100, 110, 120], 30, "p1")
        assert result.retention_held is None
