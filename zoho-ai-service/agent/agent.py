from typing import Any

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from agent.prompts import build_chat_prompt
from agent.tools.budget_tools import _make_tools
from config import settings
from services.zoho_data_service import ZohoDataService


class BudgetHealthReport(BaseModel):
    project_name: str = Field(description="Name of the project")
    total_budget: float = Field(description="Total budget in INR")
    total_spent: float = Field(description="Total amount spent in INR")
    utilization_pct: float = Field(
        description="Percentage of budget utilized"
    )
    days_remaining: int | None = Field(
        default=None, description="Days remaining in project"
    )
    status: str = Field(
        description="Budget status: on_track, warning, critical, over_budget"
    )
    forecast_30d_burn: float | None = Field(
        default=None, description="Forecast burn for next 30 days"
    )
    confidence_low: float | None = Field(
        default=None, description="Lower bound of forecast confidence"
    )
    confidence_high: float | None = Field(
        default=None, description="Upper bound of forecast confidence"
    )


class AnomalyFlag(BaseModel):
    project_id: str = Field(description="Project ID where anomaly found")
    component: str = Field(
        description="Budget component with anomaly"
    )
    expected_range: str = Field(
        description="Expected normal range as string"
    )
    actual_value: float = Field(
        description="Actual expense value that triggered anomaly"
    )
    severity: str = Field(
        description="Severity: low, medium, or high"
    )
    detected_by: str = Field(
        description="Method: z_score, iqr, or both"
    )
    recommendation: str = Field(
        description="Suggested action for the anomaly"
    )


def create_simple_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_model_simple,
        temperature=0,
        timeout=30,
        max_retries=1,
    )


def get_structured_llm(
    model: type[BaseModel] = BudgetHealthReport,
) -> ChatOpenAI:
    return create_simple_llm().with_structured_output(model)


def create_agent_executor(
    data_service: ZohoDataService,
) -> AgentExecutor:
    llm = ChatOpenAI(
        model=settings.openai_model_complex,
        temperature=0,
        max_tokens=2048,
        timeout=60,
        max_retries=2,
    )

    tools = _make_tools(data_service)
    prompt = build_chat_prompt()

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        early_stopping_method="generate",
        handle_parsing_errors=True,
    )
