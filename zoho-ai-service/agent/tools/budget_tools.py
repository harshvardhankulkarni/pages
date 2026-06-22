from langchain.tools import StructuredTool

from services.procurement import ProcurementEngine
from services.zoho_data_service import ZohoDataService


def _make_tools(data_service: ZohoDataService) -> list[StructuredTool]:
    def list_projects_impl(status: str | None = None) -> str:
        result = data_service.list_projects(status)
        if not result["success"]:
            raise ValueError(result["error"])
        return str(result["data"])

    def get_project_budget_impl(project_id: str) -> str:
        result = data_service.get_project_budget(project_id)
        if not result["success"]:
            raise ValueError(result["error"])
        return str(result["data"])

    def get_project_expenses_impl(
        project_id: str, start_date: str, end_date: str
    ) -> str:
        result = data_service.get_project_expenses(
            project_id, start_date, end_date
        )
        if not result["success"]:
            raise ValueError(result["error"])
        return str(result["data"])

    def get_inventory_status_impl(item_id: str) -> str:
        result = data_service.get_inventory_status(item_id)
        if not result["success"]:
            raise ValueError(result["error"])
        return str(result["data"])

    def get_procurement_history_impl(
        item_id: str, months: int = 6
    ) -> str:
        result = data_service.get_procurement_history(item_id, months)
        if not result["success"]:
            raise ValueError(result["error"])
        return str(result["data"])

    def recommend_reorder_impl(item_id: str) -> str:
        engine = ProcurementEngine(data_service)
        result = engine.recommend_reorder(item_id)
        return str(result.model_dump())

    tools = [
        StructuredTool.from_function(
            func=recommend_reorder_impl,
            name="recommend_reorder",
            description=(
                "Recommend optimal reorder quantity and timing for an inventory item. "
                "Uses EOQ (Economic Order Quantity) and consumption history from Zoho Creator. "
                "Input: item_id (string). "
                "Returns item name, current stock, reorder point, "
                "recommended quantity, recommended date, and priority level."
            ),
            handle_tool_error=True,
        ),
        StructuredTool.from_function(
            func=list_projects_impl,
            name="list_projects",
            description=(
                "List all projects with optional status filter. "
                "Returns project IDs and names. "
                "Use when you need to find a project ID or list available projects."
            ),
            handle_tool_error=True,
        ),
        StructuredTool.from_function(
            func=get_project_budget_impl,
            name="get_project_budget",
            description=(
                "Fetch aggregated budget and utilization for a project. "
                "Input: project_id (string). "
                "Returns total_budget, utilization_pct, components list, "
                "and retention info. Use for budget health checks."
            ),
            handle_tool_error=True,
        ),
        StructuredTool.from_function(
            func=get_project_expenses_impl,
            name="get_project_expenses",
            description=(
                "Fetch expense records for a project within a date range "
                "(ISO format YYYY-MM-DD). "
                "Input: project_id, start_date, end_date. "
                "Returns aggregated totals and component breakdown."
            ),
            handle_tool_error=True,
        ),
        StructuredTool.from_function(
            func=get_inventory_status_impl,
            name="get_inventory_status",
            description=(
                "Fetch current inventory status for an item. "
                "Input: item_id (string). "
                "Returns item_name, current_stock, reorder_point, unit, unit_cost."
            ),
            handle_tool_error=True,
        ),
        StructuredTool.from_function(
            func=get_procurement_history_impl,
            name="get_procurement_history",
            description=(
                "Fetch purchase order history for an inventory item. "
                "Input: item_id (string), months (int, default=6). "
                "Returns total_ordered, avg_monthly_consumption, order list."
            ),
            handle_tool_error=True,
        ),
    ]
    return tools
