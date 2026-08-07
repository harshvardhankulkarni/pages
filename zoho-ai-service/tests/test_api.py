from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from config import settings


@pytest.fixture
def client():
    with (
        patch(
            "services.zoho_client.ZohoClient._refresh_token"
        ) as mock_refresh,
        patch(
            "services.zoho_client.ZohoClient._request"
        ) as mock_request,
    ):
        mock_refresh.return_value = None
        mock_request.return_value = {"data": []}
        with TestClient(app) as c:
            yield c


class TestAPI:
    def test_health_ok(self, client):
        ds = app.state.data_service
        with patch.object(
            ds, "list_projects"
        ) as mock_lp:
            mock_lp.return_value = {
                "success": True,
                "data": [],
                "error": None,
            }
            resp = client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"

    def test_health_degraded(self, client):
        ds = app.state.data_service
        with patch.object(
            ds, "list_projects"
        ) as mock_lp:
            mock_lp.side_effect = Exception("Zoho down")
            resp = client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "degraded"

    def test_chat_out_of_domain(self, client):
        resp = client.post(
            "/chat",
            json={
                "query": "What is the weather today?",
                "user_id": "test",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "budget tracking" in data["response"].lower()

    def test_chat_valid_query(self, client):
        mock_executor = MagicMock()
        mock_executor.ainvoke = AsyncMock()
        mock_executor.ainvoke.return_value = {
            "output": "Project A is on track at 50% utilization"
        }
        app.state.agent_executor = mock_executor

        with patch.object(
            app.state.guardrail, "reject_out_of_domain"
        ) as mock_domain:
            mock_domain.return_value = type(
                "GuardrailResult",
                (),
                {"safe": True, "modified_response": None, "warnings": []},
            )()
            resp = client.post(
                "/chat",
                json={
                    "query": "Which project is over budget?",
                    "user_id": "test",
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "response" in data

    def test_projects_list(self, client):
        ds = app.state.data_service
        with patch.object(
            ds, "list_projects"
        ) as mock_lp:
            mock_lp.return_value = {
                "success": True,
                "data": [
                    {
                        "id": "1",
                        "name": "Project A",
                        "status": "active",
                        "manager_email": "",
                    },
                    {
                        "id": "2",
                        "name": "Project B",
                        "status": "active",
                        "manager_email": "",
                    },
                ],
                "error": None,
            }
            resp = client.get("/projects?status=active")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data["projects"]) == 2

    def test_forecast_endpoint(self, client):
        resp = client.post(
            "/forecast",
            json={
                "project_id": "test",
                "horizon_days": 30,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "note" in data

    def test_forecast_invalid_horizon(self, client):
        resp = client.post(
            "/forecast",
            json={
                "project_id": "test",
                "horizon_days": 45,
            },
        )
        assert resp.status_code == 400

    def test_anomalies_all(self, client):
        resp = client.get("/anomalies")
        assert resp.status_code == 200
        data = resp.json()
        assert "anomalies" in data

    def test_anomalies_filtered_by_project(self, client):
        resp = client.get("/anomalies?project_id=p1")
        assert resp.status_code == 200

    def test_anomalies_filtered_by_severity(self, client):
        resp = client.get("/anomalies?severity=high")
        assert resp.status_code == 200

    def test_weekly_endpoint(self, client):
        resp = client.post("/weekly")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "not_implemented"

    def test_procurement_recommend(self, client):
        mock_rec = MagicMock()
        mock_rec.model_dump.return_value = {
            "item_name": "Steel",
            "current_stock": 50,
            "priority": "high",
        }
        with patch(
            "services.procurement.ProcurementEngine.recommend_reorder",
            return_value=mock_rec,
        ):
            resp = client.get(
                "/procurement/recommend?item_id=steel-001"
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True

    def test_procurement_recommend_error(self, client):
        with patch(
            "services.procurement.ProcurementEngine.recommend_reorder"
        ) as mock_rec:
            mock_rec.side_effect = ValueError("Item not found")
            resp = client.get(
                "/procurement/recommend?item_id=invalid"
            )
            assert resp.status_code == 502

    def test_procurement_scan(self, client):
        resp = client.get("/procurement/scan")
        assert resp.status_code == 200
        data = resp.json()
        assert "success" in data

    def test_forecast_valid_request(self, client):
        resp = client.post(
            "/forecast",
            json={
                "project_id": "test",
                "horizon_days": 30,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "forecast" in data

    def test_forecast_zoho_error(self, client):
        from services.zoho_client import ZohoAPIError

        with patch(
            "services.forecast.ForecastEngine.forecast"
        ) as mock_fc:
            mock_fc.side_effect = ZohoAPIError("Zoho down")
            resp = client.post(
                "/forecast",
                json={
                    "project_id": "test",
                    "horizon_days": 30,
                },
            )
            assert resp.status_code == 502
