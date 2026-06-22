from unittest.mock import MagicMock

import pytest

from services.procurement import ProcurementEngine
from services.procurement_types import (
    ProcurementRecommendation,
    ProcurementResult,
)


class TestProcurement:
    @pytest.fixture
    def engine(self):
        mock_ds = MagicMock()
        return ProcurementEngine(
            mock_ds, ordering_cost=500.0, holding_rate=0.2
        )

    def test_eoq_calculation(self, engine):
        eoq = engine._calc_eoq(1200, 100)
        assert abs(eoq - 244.95) < 1.0

    def test_eoq_zero_demand(self, engine):
        assert engine._calc_eoq(0, 100) == 0

    def test_reorder_point(self, engine):
        rp = engine._calc_reorder_point(100, 30)
        assert rp == 100.0

    def test_determine_priority_critical(self, engine):
        assert (
            engine._determine_priority(-5, 100) == "critical"
        )

    def test_determine_priority_high(self, engine):
        assert (
            engine._determine_priority(80, 100) == "high"
        )

    def test_determine_priority_medium(self, engine):
        assert (
            engine._determine_priority(140, 100) == "medium"
        )

    def test_determine_priority_low(self, engine):
        assert (
            engine._determine_priority(200, 100) == "low"
        )

    def test_recommend_reorder_normal(self, engine):
        engine._data_service.get_inventory_status.return_value = {
            "success": True,
            "data": {
                "item_name": "Steel Rods",
                "current_stock": 50,
                "reorder_point": 100,
                "unit": "kg",
                "unit_cost": 75,
            },
        }
        engine._data_service.get_procurement_history.return_value = {
            "success": True,
            "data": {
                "total_ordered": 12000,
                "avg_monthly_consumption": 1000,
                "orders": [
                    {
                        "date": "2026-01-10",
                        "qty": 1000,
                        "amount": 75000,
                        "delivery_date": "2026-01-25",
                    }
                ],
            },
        }
        result = engine.recommend_reorder("steel-001")
        assert result.priority == "high"
        assert result.recommended_qty > 0
        assert len(result.reasoning) > 10

    def test_recommend_reorder_no_consumption(self, engine):
        engine._data_service.get_inventory_status.return_value = {
            "success": True,
            "data": {
                "item_name": "Steel",
                "current_stock": 500,
                "reorder_point": 100,
                "unit": "kg",
                "unit_cost": 75,
            },
        }
        engine._data_service.get_procurement_history.return_value = {
            "success": True,
            "data": {
                "total_ordered": 0,
                "avg_monthly_consumption": 0,
                "orders": [],
            },
        }
        result = engine.recommend_reorder("steel-001")
        assert result.priority == "low"
        assert result.recommended_qty == 0

    def test_recommend_reorder_inventory_error(self, engine):
        engine._data_service.get_inventory_status.return_value = {
            "success": False,
            "data": None,
            "error": "Zoho Creator unavailable",
        }
        with pytest.raises(ValueError):
            engine.recommend_reorder("steel-001")

    def test_procurement_recommendation_schema(self):
        rec = ProcurementRecommendation(
            item_name="Cement",
            current_stock=100,
            reorder_point=200,
            avg_consumption=150,
            lead_time_days=14,
            recommended_qty=500,
            recommended_date="2026-07-01",
            priority="high",
            reasoning="Test reasoning",
            eoq=300.0,
            unit_cost=350.0,
        )
        data = rec.model_dump()
        assert data["item_name"] == "Cement"
        assert data["priority"] == "high"
        assert data["eoq"] == 300.0

    def test_lead_time_estimation(self, engine):
        orders = [
            {
                "date": "2026-01-01",
                "delivery_date": "2026-01-15",
            },
            {
                "date": "2026-02-01",
                "delivery_date": "2026-02-20",
            },
        ]
        lt = engine._estimate_lead_time(orders)
        assert lt == 16

    def test_lead_time_default(self, engine):
        assert engine._estimate_lead_time([]) == 30
