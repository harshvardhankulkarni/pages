from unittest.mock import MagicMock

import pytest

from services.anomaly import AnomalyDetector
from services.anomaly_types import AnomalyDetectionInput, AnomalyDetectionResult, AnomalyFlag


class TestAnomaly:
    @pytest.fixture
    def detector(self):
        mock_ds = MagicMock()
        return AnomalyDetector(mock_ds, z_threshold=2.5, iqr_multiplier=1.5, window=30)

    def test_moving_zscore_normal(self, detector):
        values = [10, 12, 11, 13, 10, 12, 11, 13, 10, 12, 11, 13, 10, 12, 11]
        is_anom, z = detector._moving_zscore(values, 11)
        assert is_anom is False

    def test_moving_zscore_anomaly(self, detector):
        values = [10, 12, 11, 13, 10, 12, 11, 13, 10, 12, 11, 13, 10, 12, 11]
        is_anom, z = detector._moving_zscore(values, 50)
        assert is_anom is True
        assert abs(z) > 2.5

    def test_moving_iqr_normal(self, detector):
        values = [10, 12, 11, 13, 10, 12, 11, 13, 10, 12, 11, 13, 10, 12, 11]
        is_anom, q1, q3, iqr = detector._moving_iqr(values, 11)
        assert is_anom is False

    def test_insufficient_data(self, detector):
        values = [10, 12]
        is_anom, z = detector._moving_zscore(values, 11)
        assert is_anom is False

    def test_scan_all_projects(self, detector):
        detector._data_service.list_projects.return_value = {
            "success": True,
            "data": [
                {"id": "p1", "name": "Proj A", "status": "active", "manager_email": ""},
                {"id": "p2", "name": "Proj B", "status": "active", "manager_email": ""},
            ],
        }
        detector._data_service.get_project_expenses.return_value = {
            "success": True,
            "data": {
                "total_spent": 5000,
                "by_component": [
                    {"name": "Foundation", "total": 1000},
                    {"name": "Structure", "total": 2000},
                    {"name": "Finishing", "total": 2000},
                ],
                "transaction_count": 10,
            },
        }
        result = detector.scan(AnomalyDetectionInput())
        assert result.projects_scanned == 2

    def test_severity_filter(self, detector):
        flags = [
            AnomalyFlag(
                project_id="p1", component="A", expected_range="10-20",
                actual_value=15, severity="low", detected_by="z_score",
                recommendation="Monitor",
            ),
            AnomalyFlag(
                project_id="p1", component="B", expected_range="10-20",
                actual_value=50, severity="high", detected_by="both",
                recommendation="Investigate",
            ),
        ]
        result = AnomalyDetectionResult(
            anomalies=flags, projects_scanned=1
        )
        filtered = [f for f in result.anomalies if f.severity == "high"]
        assert len(filtered) == 1
        assert filtered[0].component == "B"

    def test_anomaly_flag_schema(self):
        flag = AnomalyFlag(
            project_id="p1",
            component="Foundation",
            expected_range="100000-150000",
            actual_value=300000,
            severity="high",
            detected_by="both",
            recommendation="Investigate",
        )
        data = flag.model_dump()
        assert "project_id" in data
        assert "severity" in data
