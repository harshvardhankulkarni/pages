import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from langfuse.callback import CallbackHandler
from pydantic import BaseModel, Field

from agent.agent import create_agent_executor
from agent.guardrails import BudgetGuardrail
from config import settings
from services.anomaly import AnomalyDetector
from services.anomaly_types import (
    AnomalyDetectionInput,
    AnomalyDetectionResult,
)
from services.forecast import ForecastEngine
from services.forecast_types import ForecastInput
from services.procurement import ProcurementEngine
from services.procurement_types import (
    ProcurementRecommendation,
    ProcurementResult,
)
from services.zoho_client import ZohoClient, ZohoAPIError
from services.zoho_data_service import ZohoDataService

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    query: str = Field(description="Natural language query")
    chat_history: list[dict[str, str]] = Field(
        default_factory=list,
        description="Previous chat messages",
    )
    user_id: str = Field(
        default="anonymous",
        description="User identifier for tracing",
    )


class ChatResponse(BaseModel):
    response: str = Field(description="AI response text")
    sources: list[str] = Field(
        default_factory=list,
        description="Source references",
    )


class ForecastResponse(BaseModel):
    forecast: dict[str, Any] = Field(default_factory=dict)
    confidence: dict[str, Any] = Field(default_factory=dict)
    note: str = ""


class AnomaliesResponse(BaseModel):
    anomalies: list[dict[str, Any]] = Field(default_factory=list)
    scan_timestamp: str = ""
    projects_scanned: int = 0


class WeeklyResponse(BaseModel):
    status: str = "not_implemented"
    emails_sent: int = 0


class ProjectItem(BaseModel):
    id: str
    name: str


class ProjectsResponse(BaseModel):
    projects: list[ProjectItem]


class HealthResponse(BaseModel):
    status: str
    zoho_api: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    zoho_client = ZohoClient()
    data_service = ZohoDataService(zoho_client)
    guardrail = BudgetGuardrail(data_service)
    agent_executor = create_agent_executor(data_service)
    langfuse_handler = None
    if settings.langfuse_secret_key and settings.langfuse_public_key:
        langfuse_handler = CallbackHandler(
            secret_key=settings.langfuse_secret_key,
            public_key=settings.langfuse_public_key,
            host=settings.langfuse_host,
        )
    app.state.zoho_client = zoho_client
    app.state.data_service = data_service
    app.state.guardrail = guardrail
    app.state.agent_executor = agent_executor
    app.state.langfuse_handler = langfuse_handler
    yield


app = FastAPI(
    title="ITOTCloud Budget AI Service",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health(request: Request):
    try:
        request.app.state.data_service.list_projects("active")
        return HealthResponse(status="ok", zoho_api="connected")
    except Exception:
        return HealthResponse(
            status="degraded", zoho_api="unreachable"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest):
    guardrail: BudgetGuardrail = request.app.state.guardrail

    domain_check = guardrail.reject_out_of_domain(body.query)
    if not domain_check.safe:
        return ChatResponse(
            response=domain_check.modified_response or ""
        )

    agent_kwargs: dict[str, Any] = {
        "input": body.query,
    }
    langfuse_handler = request.app.state.langfuse_handler
    if langfuse_handler:
        agent_kwargs["config"] = {
            "callbacks": [langfuse_handler],
            "run_name": "nlq-budget-query",
        }

    executor = request.app.state.agent_executor
    result = await executor.ainvoke(**agent_kwargs)

    response_text = result.get("output", "")
    disclaimer_result = guardrail.enforce_disclaimer(response_text)
    final_text = (
        disclaimer_result.modified_response or response_text
    )

    return ChatResponse(response=final_text)


@app.post("/forecast", response_model=ForecastResponse)
async def forecast(request: Request, body: ForecastInput):
    if body.horizon_days not in (30, 60, 90):
        raise HTTPException(
            status_code=400,
            detail="horizon_days must be 30, 60, or 90",
        )
    try:
        engine = ForecastEngine(
            request.app.state.data_service
        )
        result = engine.forecast(body)
        return ForecastResponse(
            forecast=result.model_dump(),
            confidence={
                "low": result.confidence_low,
                "high": result.confidence_high,
            },
            note=result.warning or "",
        )
    except ZohoAPIError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Zoho Creator unavailable",
                "detail": str(e),
            },
        )


@app.get("/anomalies", response_model=AnomaliesResponse)
async def anomalies(
    request: Request,
    project_id: str | None = Query(None),
    severity: str | None = Query(None),
):
    detector = AnomalyDetector(
        request.app.state.data_service
    )
    input_data = AnomalyDetectionInput(
        project_id=project_id, severity=severity
    )
    result = detector.scan(input_data)
    return AnomaliesResponse(
        anomalies=[a.model_dump() for a in result.anomalies],
        scan_timestamp=result.scan_timestamp,
        projects_scanned=result.projects_scanned,
    )


@app.get("/projects", response_model=ProjectsResponse)
async def projects(
    request: Request,
    status: str | None = Query(None),
):
    data_service: ZohoDataService = (
        request.app.state.data_service
    )
    result = data_service.list_projects(status)
    if not result["success"]:
        raise HTTPException(
            status_code=502, detail=result["error"]
        )
    items = [
        ProjectItem(id=p["id"], name=p["name"])
        for p in result["data"]
    ]
    return ProjectsResponse(projects=items)


@app.post("/weekly", response_model=WeeklyResponse)
async def weekly(request: Request):
    return WeeklyResponse()


@app.get(
    "/procurement/recommend",
    response_model=dict[str, Any],
)
async def procurement_recommend(
    request: Request,
    item_id: str = Query(description="Inventory item ID"),
):
    try:
        engine = ProcurementEngine(
            request.app.state.data_service
        )
        result = engine.recommend_reorder(item_id)
        return {"success": True, "data": result.model_dump()}
    except ValueError as e:
        raise HTTPException(
            status_code=502,
            detail={"error": str(e)},
        )
    except ZohoAPIError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Zoho Creator unavailable",
                "detail": str(e),
            },
        )


@app.get(
    "/procurement/scan",
    response_model=dict[str, Any],
)
async def procurement_scan(
    request: Request,
):
    engine = ProcurementEngine(
        request.app.state.data_service
    )
    result = engine.scan_all()
    return {
        "success": True,
        "data": result.model_dump(),
    }
