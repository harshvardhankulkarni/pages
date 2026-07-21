import functools
import logging
from typing import Any

from services.cache import TTLCache
from services.zoho_client import (
    ZohoClient,
    ZohoAPIError,
    ZohoAuthError,
    ZohoRateLimitError,
)

logger = logging.getLogger(__name__)

_cache = TTLCache()


def cached(ttl_seconds: int = 300):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = func.__name__ + str(args) + str(kwargs)
            result = _cache.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            _cache.set(key, result, ttl_seconds)
            return result

        return wrapper

    return decorator


def _safe_call(func, *args, **kwargs) -> dict[str, Any]:
    try:
        data = func(*args, **kwargs)
        return {"success": True, "data": data, "error": None}
    except ZohoAuthError:
        return {
            "success": False,
            "data": None,
            "error": "Authentication failed",
        }
    except ZohoRateLimitError:
        return {
            "success": False,
            "data": None,
            "error": "Rate limit exceeded, please wait",
        }
    except ZohoAPIError:
        return {
            "success": False,
            "data": None,
            "error": "Zoho Creator is temporarily unavailable",
        }


class ZohoDataService:
    def __init__(self, zoho_client: ZohoClient):
        self._client = zoho_client

    @cached(ttl_seconds=60)
    def list_projects(
        self, status: str | None = None
    ) -> dict[str, Any]:
        def fetch():
            records = self._client.get_records("Projects")
            projects = []
            for r in records:
                proj = {
                    "id": r.get("ID", ""),
                    "name": r.get("Project_Name", ""),
                    "status": r.get("Status", ""),
                    "manager_email": r.get("Manager_Email", ""),
                }
                projects.append(proj)
            if status:
                projects = [p for p in projects if p["status"] == status]
            return projects

        return _safe_call(fetch)

    @cached(ttl_seconds=300)
    def get_project_budget(self, project_id: str) -> dict[str, Any]:
        def fetch():
            budget_records = self._client.get_records("Budget_Plans")
            budget_plan = None
            for br in budget_records:
                if str(br.get("Project_ID", "")) == project_id:
                    budget_plan = br
                    break
            components = self._client.get_records(
                "Budget_Components",
                {"Criteria": f"Project_ID == {project_id}"},
            )
            total_allocated = 0.0
            total_spent = 0.0
            comp_list = []
            for c in components:
                alloc = float(c.get("Allocated_Amount", 0) or 0)
                spent = float(c.get("Spent_Amount", 0) or 0)
                total_allocated += alloc
                total_spent += spent
                comp_list.append(
                    {
                        "name": c.get("Component_Name", ""),
                        "allocated": alloc,
                        "spent": spent,
                    }
                )
            utilization = 0.0
            if total_allocated > 0:
                utilization = (total_spent / total_allocated) * 100
            return {
                "total_budget": total_allocated,
                "components": comp_list,
                "utilization_pct": round(utilization, 2),
                "retention_pct": float(
                    budget_plan.get("Retention_Pct", 0) or 0
                ) if budget_plan else 0.0,
                "retention_amount": float(
                    budget_plan.get("Retention_Amount", 0) or 0
                ) if budget_plan else 0.0,
            }

        return _safe_call(fetch)

    @cached(ttl_seconds=300)
    def get_project_expenses(
        self, project_id: str, start_date: str = "", end_date: str = ""
    ) -> dict[str, Any]:
        def fetch():
            criteria = f"Project_ID == {project_id}"
            if start_date and end_date:
                criteria += (
                    f" && Date >= '{start_date}' && Date <= '{end_date}'"
                )
            records = self._client.get_records(
                "Expenses", {"Criteria": criteria}
            )
            by_component: dict[str, float] = {}
            total_spent = 0.0
            for r in records:
                comp = r.get("Component_Name", "Uncategorized")
                amt = float(r.get("Amount", 0) or 0)
                by_component[comp] = by_component.get(comp, 0) + amt
                total_spent += amt
            comp_list = [
                {"name": k, "total": v}
                for k, v in sorted(by_component.items())
            ]
            return {
                "total_spent": round(total_spent, 2),
                "by_component": comp_list,
                "transaction_count": len(records),
            }

        return _safe_call(fetch)

    @cached(ttl_seconds=300)
    def get_inventory_status(self, item_id: str) -> dict[str, Any]:
        def fetch():
            records = self._client.get_records(
                "Inventory_Items",
                {"Criteria": f"Item_ID == {item_id}"},
            )
            if not records:
                return {
                    "item_name": "",
                    "current_stock": 0,
                    "reorder_point": 0,
                    "unit": "",
                    "unit_cost": None,
                }
            r = records[0]
            return {
                "item_name": r.get("Item_Name", ""),
                "current_stock": float(r.get("Current_Stock", 0) or 0),
                "reorder_point": float(r.get("Reorder_Point", 0) or 0),
                "unit": r.get("Unit", ""),
                "unit_cost": (
                    float(r["Unit_Cost"])
                    if r.get("Unit_Cost")
                    else None
                ),
            }

        return _safe_call(fetch)

    @cached(ttl_seconds=300)
    def get_procurement_history(
        self, item_id: str, months: int = 6
    ) -> dict[str, Any]:
        def fetch():
            records = self._client.get_records("Purchase_Orders")
            item_orders = []
            total_qty = 0.0
            for r in records:
                if str(r.get("Item_ID", "")) == item_id:
                    qty = float(r.get("Quantity", 0) or 0)
                    amt = float(r.get("Amount", 0) or 0)
                    item_orders.append(
                        {
                            "date": r.get("Order_Date", ""),
                            "qty": qty,
                            "amount": amt,
                            "delivery_date": r.get(
                                "Delivery_Date", ""
                            ),
                        }
                    )
                    total_qty += qty
            avg_monthly = (
                round(total_qty / months, 2) if months > 0 else 0
            )
            return {
                "total_ordered": round(total_qty, 2),
                "orders": item_orders,
                "avg_monthly_consumption": avg_monthly,
            }

        return _safe_call(fetch)

    @cached(ttl_seconds=60)
    def get_project_list(self) -> dict[str, Any]:
        def fetch():
            records = self._client.get_records("Projects")
            return [
                {"id": r.get("ID", ""), "name": r.get("Project_Name", "")}
                for r in records
            ]

        return _safe_call(fetch)
