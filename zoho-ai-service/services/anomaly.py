import logging
from datetime import datetime

import numpy as np

from config import settings
from services.anomaly_types import (
    AnomalyDetectionInput,
    AnomalyDetectionResult,
    AnomalyFlag,
)
from services.zoho_data_service import ZohoDataService

logger = logging.getLogger(__name__)


class AnomalyDetector:
    def __init__(
        self,
        data_service: ZohoDataService,
        z_threshold: float | None = None,
        iqr_multiplier: float | None = None,
        window: int = 30,
    ):
        self._data_service = data_service
        self._z_threshold = (
            z_threshold or settings.anomaly_z_threshold
        )
        self._iqr_multiplier = (
            iqr_multiplier or settings.anomaly_iqr_multiplier
        )
        self._window = window

    def scan(
        self, input_data: AnomalyDetectionInput
    ) -> AnomalyDetectionResult:
        result = self._data_service.list_projects("active")
        if not result["success"]:
            return AnomalyDetectionResult(
                projects_scanned=0,
                scan_timestamp=datetime.utcnow().isoformat(),
            )
        projects = result["data"]
        if input_data.project_id:
            projects = [
                p
                for p in projects
                if p["id"] == input_data.project_id
            ]

        all_flags: list[AnomalyFlag] = []
        for proj in projects:
            flags = self._check_expenses(proj["id"])
            all_flags.extend(flags)

        if input_data.severity:
            all_flags = [
                f
                for f in all_flags
                if f.severity == input_data.severity
            ]

        return AnomalyDetectionResult(
            anomalies=all_flags,
            projects_scanned=len(projects),
            scan_timestamp=datetime.utcnow().isoformat(),
        )

    def _check_expenses(
        self, project_id: str
    ) -> list[AnomalyFlag]:
        result = self._data_service.get_project_expenses(
            project_id, "", ""
        )
        if not result["success"]:
            logger.warning(
                "Failed to fetch expenses for %s", project_id
            )
            return []

        by_component = result["data"].get("by_component", [])
        if len(by_component) < 2:
            return []

        flags: list[AnomalyFlag] = []
        all_values = [c["total"] for c in by_component]

        for comp in by_component:
            name = comp["name"]
            actual = comp["total"]
            other_values = [
                v
                for i, v in enumerate(all_values)
                if by_component[i]["name"] != name
            ]

            if len(other_values) < self._window // 2:
                continue

            z_is_anom, z_score = self._moving_zscore(
                other_values, actual
            )
            iqr_is_anom, q1, q3, iqr_val = self._moving_iqr(
                other_values, actual
            )

            if not z_is_anom and not iqr_is_anom:
                continue

            detected_by = "both"
            severity = "medium"
            if z_is_anom and not iqr_is_anom:
                detected_by = "z_score"
                severity = "low"
            elif iqr_is_anom and not z_is_anom:
                detected_by = "iqr"
                severity = "low"
            else:
                if abs(z_score) > 3.5:
                    severity = "high"

            flags.append(
                AnomalyFlag(
                    project_id=project_id,
                    component=name,
                    expected_range=f"₹{q1:,.0f} - ₹{q3:,.0f}",
                    actual_value=actual,
                    severity=severity,
                    detected_by=detected_by,
                    recommendation=self._generate_recommendation(
                        name, severity, detected_by
                    ),
                )
            )

        return flags

    def _moving_zscore(
        self,
        values: list[float],
        new_value: float,
    ) -> tuple[bool, float]:
        if len(values) < self._window // 2:
            return False, 0.0
        recent = values[-self._window :]
        mean = float(np.mean(recent))
        std = float(np.std(recent))
        if std == 0:
            return False, 0.0
        z = (new_value - mean) / std
        return bool(abs(z) > self._z_threshold), z

    def _moving_iqr(
        self,
        values: list[float],
        new_value: float,
    ) -> tuple[bool, float, float, float]:
        if len(values) < self._window // 2:
            return False, 0.0, 0.0, 0.0
        recent = values[-self._window :]
        q1 = float(np.percentile(recent, 25))
        q3 = float(np.percentile(recent, 75))
        iqr_val = q3 - q1
        lower = q1 - self._iqr_multiplier * iqr_val
        upper = q3 + self._iqr_multiplier * iqr_val
        is_anom = new_value < lower or new_value > upper
        return is_anom, q1, q3, iqr_val

    def _detect_drift(self, values: list[float]) -> bool:
        if len(values) < self._window:
            return False
        first_half = np.mean(values[: self._window // 2])
        second_half = np.mean(values[-self._window // 2 :])
        if first_half == 0:
            return False
        return abs(second_half - first_half) / first_half > 0.1

    def _generate_recommendation(
        self,
        component: str,
        severity: str,
        detected_by: str,
    ) -> str:
        if severity == "high":
            return (
                f"Urgent: Investigate {component} overspend "
                f"immediately. Verify with Finance Manager."
            )
        if severity == "medium":
            return (
                f"Review {component} spending trend. "
                f"Check if this is a planned increase or miscoding."
            )
        return (
            f"Monitor {component} — minor variance detected. "
            f"Review at next weekly meeting."
        )
