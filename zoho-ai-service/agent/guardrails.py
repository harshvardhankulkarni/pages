import re
from typing import Any

from pydantic import BaseModel, Field

from services.zoho_data_service import ZohoDataService

DOMAIN_KEYWORDS = [
    "budget",
    "project",
    "expense",
    "spend",
    "inventory",
    "stock",
    "procurement",
    "purchase",
    "forecast",
    "anomaly",
    "overrun",
    "utilization",
    "component",
    "vendor",
    "supplier",
    "reorder",
    "cost",
    "price",
    "material",
    "construction",
    "site",
    "contractor",
    "payment",
    "invoice",
    "gst",
    "hsn",
    "milestone",
    "retention",
    "po",
    "pr",
    "consumption",
]

FORECAST_KEYWORDS = [
    "forecast",
    "projection",
    "predict",
    "recommend",
    "reorder",
]

DISCLAIMER = (
    "AI-generated forecast, review with Finance Manager before acting"
)


class GuardrailResult(BaseModel):
    safe: bool = Field(default=True)
    warnings: list[str] = Field(default_factory=list)
    modified_response: str | None = Field(default=None)


class BudgetGuardrail:
    def __init__(self, data_service: ZohoDataService | None = None):
        self._data_service = data_service

    def reject_out_of_domain(self, query: str) -> GuardrailResult:
        q = query.lower()
        matched = any(kw in q for kw in DOMAIN_KEYWORDS)
        if not matched:
            return GuardrailResult(
                safe=False,
                warnings=[
                    "Query is outside the budget tracking domain"
                ],
                modified_response=(
                    "I can only answer questions about budget tracking, "
                    "project expenses, inventory, and procurement. "
                    "Please ask a question related to these topics."
                ),
            )
        return GuardrailResult()

    def enforce_disclaimer(
        self, response_text: str
    ) -> GuardrailResult:
        has_forecast = any(
            kw in response_text.lower() for kw in FORECAST_KEYWORDS
        )
        if has_forecast and DISCLAIMER not in response_text:
            modified = response_text + "\n\n" + DISCLAIMER
            return GuardrailResult(
                safe=True,
                warnings=["Disclaimer appended to response"],
                modified_response=modified,
            )
        return GuardrailResult(modified_response=response_text)

    def validate_budget_figures(
        self,
        response_text: str,
        data_service: ZohoDataService | None = None,
    ) -> GuardrailResult:
        ds = data_service or self._data_service
        if ds is None:
            return GuardrailResult()
        amounts = re.findall(r"₹?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)", response_text)
        if not amounts:
            return GuardrailResult()
        return GuardrailResult(
            warnings=[
                f"Found {len(amounts)} monetary values in response"
            ]
        )

    def validate_gst_rate(
        self, response_text: str
    ) -> GuardrailResult:
        known_rates = {0, 5, 12, 18, 28}
        mentioned = re.findall(r"(\d+)%\s*GST", response_text)
        issues = []
        for rate_str in mentioned:
            rate = int(rate_str)
            if rate not in known_rates:
                issues.append(
                    f"GST rate {rate}% is not a standard rate"
                )
        if issues:
            return GuardrailResult(
                safe=False, warnings=issues
            )
        return GuardrailResult()

    def validate_stock_budget(
        self, response: dict[str, Any]
    ) -> GuardrailResult:
        warnings_list = []
        current = response.get("current_stock", 0)
        recommended = response.get("recommended_qty", 0)
        if recommended > 0 and current < 0:
            warnings_list.append(
                "Stock is negative; verify physical count before reordering"
            )
        if warnings_list:
            return GuardrailResult(
                safe=False, warnings=warnings_list
            )
        return GuardrailResult()
