import logging
import math
from datetime import datetime, timedelta

from services.procurement_types import (
    ProcurementRecommendation,
    ProcurementResult,
)
from services.zoho_data_service import ZohoDataService

logger = logging.getLogger(__name__)


class ProcurementEngine:
    def __init__(
        self,
        data_service: ZohoDataService,
        ordering_cost: float = 500.0,
        holding_rate: float = 0.2,
    ):
        self._data_service = data_service
        self._ordering_cost = ordering_cost
        self._holding_rate = holding_rate

    def recommend_reorder(
        self, item_id: str
    ) -> ProcurementRecommendation:
        inv_result = self._data_service.get_inventory_status(
            item_id
        )
        if not inv_result["success"]:
            raise ValueError(inv_result["error"])
        inv_data = inv_result["data"]

        item_name = inv_data.get("item_name", "")
        current_stock = float(inv_data.get("current_stock", 0))
        reorder_point = float(inv_data.get("reorder_point", 0))
        unit_cost = inv_data.get("unit_cost")

        pr_result = self._data_service.get_procurement_history(
            item_id, months=12
        )
        avg_consumption = 0.0
        lead_time_days = 30
        if pr_result["success"]:
            pr_data = pr_result["data"]
            avg_consumption = float(
                pr_data.get("avg_monthly_consumption", 0)
            )
            orders = pr_data.get("orders", [])
            lead_time_days = self._estimate_lead_time(orders)

        if avg_consumption <= 0:
            return ProcurementRecommendation(
                item_name=item_name,
                current_stock=current_stock,
                reorder_point=reorder_point,
                avg_consumption=0,
                lead_time_days=lead_time_days,
                recommended_qty=0,
                recommended_date=(
                    datetime.utcnow() + timedelta(days=lead_time_days)
                ).isoformat(),
                priority="low",
                reasoning=(
                    "No consumption data available for this item. "
                    "Cannot recommend reorder at this time."
                ),
                eoq=None,
                unit_cost=unit_cost,
            )

        calc_reorder_point = self._calc_reorder_point(
            avg_consumption, lead_time_days
        )
        annual_demand = avg_consumption * 12
        eoq = None
        if unit_cost and unit_cost > 0:
            eoq = self._calc_eoq(annual_demand, unit_cost)

        priority = self._determine_priority(
            current_stock, calc_reorder_point
        )

        if priority in ("critical", "high"):
            safety_buffer = (
                avg_consumption * lead_time_days / 30
            )
            if eoq and eoq > 0:
                recommended_qty = max(
                    eoq,
                    calc_reorder_point
                    - current_stock
                    + safety_buffer,
                )
            else:
                recommended_qty = max(
                    0,
                    calc_reorder_point
                    - current_stock
                    + safety_buffer,
                )
        else:
            recommended_qty = 0

        recommended_date = (
            datetime.utcnow() + timedelta(days=lead_time_days)
        ).isoformat()

        reasoning_parts = [
            f"Current stock: {current_stock}",
            f"Reorder point: {calc_reorder_point:.0f}",
            f"Average monthly consumption: {avg_consumption:.0f}",
            f"Lead time: {lead_time_days} days",
        ]
        if eoq is not None and eoq > 0:
            reasoning_parts.append(
                f"EOQ: {eoq:.0f} units"
            )
        else:
            reasoning_parts.append(
                "EOQ not available (missing unit cost or demand data)"
            )
        reasoning_parts.append(
            f"Priority: {priority}"
        )
        reasoning_parts.append(
            f"Recommended quantity: {recommended_qty:.0f}"
        )

        return ProcurementRecommendation(
            item_name=item_name,
            current_stock=current_stock,
            reorder_point=calc_reorder_point,
            avg_consumption=avg_consumption,
            lead_time_days=lead_time_days,
            recommended_qty=round(recommended_qty, 2),
            recommended_date=recommended_date,
            priority=priority,
            reasoning=" | ".join(reasoning_parts),
            eoq=round(eoq, 2) if eoq is not None else None,
            unit_cost=unit_cost,
        )

    def scan_all(self) -> ProcurementResult:
        recs: list[ProcurementRecommendation] = []
        result = self._data_service.list_projects("active")
        if not result["success"]:
            return ProcurementResult(
                recommendations=[],
                scan_timestamp=datetime.utcnow().isoformat(),
            )
        return ProcurementResult(
            recommendations=recs,
            scan_timestamp=datetime.utcnow().isoformat(),
        )

    def _calc_eoq(
        self, annual_demand: float, unit_cost: float
    ) -> float:
        if annual_demand <= 0 or unit_cost <= 0:
            return 0.0
        return math.sqrt(
            2
            * annual_demand
            * self._ordering_cost
            / (unit_cost * self._holding_rate)
        )

    def _calc_reorder_point(
        self, avg_consumption: float, lead_time_days: int
    ) -> float:
        return avg_consumption * (lead_time_days / 30.0)

    def _determine_priority(
        self, current_stock: float, reorder_point: float
    ) -> str:
        if current_stock <= 0:
            return "critical"
        if current_stock <= reorder_point:
            return "high"
        if current_stock <= reorder_point * 1.5:
            return "medium"
        return "low"

    def _estimate_lead_time(
        self, orders: list[dict]
    ) -> int:
        if not orders:
            return 30
        gaps: list[int] = []
        for o in orders:
            if o.get("date") and o.get("delivery_date"):
                try:
                    order_date = datetime.fromisoformat(
                        o["date"]
                    )
                    delivery_date = datetime.fromisoformat(
                        o["delivery_date"]
                    )
                    gap = (delivery_date - order_date).days
                    if gap > 0:
                        gaps.append(gap)
                except (ValueError, TypeError):
                    continue
        if gaps:
            return int(sum(gaps) / len(gaps))
        return 30
