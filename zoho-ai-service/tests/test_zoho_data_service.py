from unittest.mock import MagicMock, patch

import pytest

from services.cache import TTLCache
from services.zoho_client import ZohoAPIError, ZohoAuthError
from services.zoho_data_service import ZohoDataService


@pytest.fixture
def mock_client():
    client = MagicMock()
    return client


@pytest.fixture
def service(mock_client):
    return ZohoDataService(mock_client)


class TestZohoDataService:
    def test_list_projects(self, service, mock_client):
        mock_client.get_records.return_value = [
            {
                "ID": "1",
                "Project_Name": "Project A",
                "Status": "active",
                "Manager_Email": "a@test.com",
            },
            {
                "ID": "2",
                "Project_Name": "Project B",
                "Status": "completed",
                "Manager_Email": "b@test.com",
            },
        ]
        result = service.list_projects()
        assert result["success"] is True
        assert len(result["data"]) == 2
        assert result["data"][0]["id"] == "1"
        assert result["data"][0]["name"] == "Project A"

    def test_list_projects_filtered(self, service, mock_client):
        mock_client.get_records.return_value = [
            {
                "ID": "1",
                "Project_Name": "A",
                "Status": "active",
                "Manager_Email": "",
            },
            {
                "ID": "2",
                "Project_Name": "B",
                "Status": "completed",
                "Manager_Email": "",
            },
        ]
        result = service.list_projects("active")
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["id"] == "1"

    def test_get_project_budget(self, service, mock_client):
        mock_client.get_records.side_effect = [
            [
                {
                    "Project_ID": "p1",
                    "Retention_Pct": 10,
                    "Retention_Amount": 0,
                }
            ],
            [
                {
                    "Component_Name": "Foundation",
                    "Allocated_Amount": 500000,
                    "Spent_Amount": 200000,
                },
                {
                    "Component_Name": "Structure",
                    "Allocated_Amount": 300000,
                    "Spent_Amount": 100000,
                },
                {
                    "Component_Name": "Finishing",
                    "Allocated_Amount": 200000,
                    "Spent_Amount": 50000,
                },
            ],
        ]
        result = service.get_project_budget("p1")
        assert result["success"] is True
        data = result["data"]
        assert data["total_budget"] == 1000000
        assert data["utilization_pct"] == 35.0
        assert len(data["components"]) == 3
        assert data["retention_pct"] == 10

    def test_caching_hit(self, service, mock_client):
        mock_client.get_records.return_value = []
        result1 = service.get_project_list()
        result2 = service.get_project_list()
        assert result1 == result2
        assert mock_client.get_records.call_count == 1

    def test_caching_expiry_bypassed(self, service, mock_client):
        mock_client.get_records.return_value = [{"ID": "1", "Project_Name": "A"}]
        service.get_project_list()
        service.get_project_list()
        # clear cache and call again
        from services.zoho_data_service import _cache

        _cache.clear()
        mock_client.get_records.return_value = [{"ID": "2", "Project_Name": "B"}]
        result = service.get_project_list()
        assert result["data"][0]["id"] == "2"
        assert mock_client.get_records.call_count == 2

    def test_error_returns_success_false(self, service, mock_client):
        mock_client.get_records.side_effect = ZohoAPIError(
            "Zoho Creator is temporarily unavailable"
        )
        result = service.list_projects()
        assert result["success"] is False
        assert result["data"] is None
        assert result["error"] is not None

    def test_get_project_expenses_aggregation(self, service, mock_client):
        mock_client.get_records.return_value = [
            {"Component_Name": "Foundation", "Amount": 100000, "Date": "2026-01-15"},
            {"Component_Name": "Foundation", "Amount": 50000, "Date": "2026-02-10"},
            {"Component_Name": "Structure", "Amount": 200000, "Date": "2026-01-20"},
            {"Component_Name": "Foundation", "Amount": 75000, "Date": "2026-03-05"},
            {"Component_Name": "Structure", "Amount": 50000, "Date": "2026-02-28"},
        ]
        result = service.get_project_expenses(
            "p1", "2026-01-01", "2026-03-31"
        )
        assert result["success"] is True
        data = result["data"]
        assert data["total_spent"] == 475000
        assert data["transaction_count"] == 5
        comps = {c["name"]: c["total"] for c in data["by_component"]}
        assert comps["Foundation"] == 225000
        assert comps["Structure"] == 250000

    def test_get_inventory_status(self, service, mock_client):
        mock_client.get_records.return_value = [
            {
                "Item_Name": "Steel Rods",
                "Current_Stock": 500,
                "Reorder_Point": 200,
                "Unit": "kg",
                "Unit_Cost": 75,
            }
        ]
        result = service.get_inventory_status("steel-001")
        assert result["success"] is True
        data = result["data"]
        assert data["item_name"] == "Steel Rods"
        assert data["current_stock"] == 500
        assert data["unit_cost"] == 75

    def test_get_procurement_history(self, service, mock_client):
        mock_client.get_records.return_value = [
            {
                "Item_ID": "steel-001",
                "Order_Date": "2026-01-10",
                "Quantity": 1000,
                "Amount": 75000,
                "Delivery_Date": "2026-01-25",
            },
            {
                "Item_ID": "steel-001",
                "Order_Date": "2026-03-15",
                "Quantity": 800,
                "Amount": 60000,
                "Delivery_Date": "2026-03-30",
            },
        ]
        result = service.get_procurement_history("steel-001", months=6)
        assert result["success"] is True
        data = result["data"]
        assert data["total_ordered"] == 1800
        assert data["avg_monthly_consumption"] == 300.0
        assert len(data["orders"]) == 2
