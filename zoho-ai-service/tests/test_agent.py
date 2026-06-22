from unittest.mock import MagicMock

import pytest

from agent.agent import (
    AnomalyFlag,
    BudgetHealthReport,
    create_agent_executor,
    create_simple_llm,
)
from agent.prompts import SYSTEM_PROMPT, build_chat_prompt


class TestAgent:
    def test_agent_executor_creation(self):
        mock_ds = MagicMock()
        executor = create_agent_executor(mock_ds)
        assert executor is not None
        assert hasattr(executor, "invoke")
        assert len(executor.tools) == 6

    def test_budget_health_report_schema(self):
        report = BudgetHealthReport(
            project_name="Test Project",
            total_budget=1000000,
            total_spent=500000,
            utilization_pct=50.0,
            status="on_track",
            forecast_30d_burn=100000,
            confidence_low=80000,
            confidence_high=120000,
        )
        data = report.model_dump()
        assert data["project_name"] == "Test Project"
        assert data["total_budget"] == 1000000
        assert data["status"] == "on_track"

    def test_anomaly_flag_schema(self):
        flag = AnomalyFlag(
            project_id="p1",
            component="Foundation",
            expected_range="100000 - 150000",
            actual_value=300000,
            severity="high",
            detected_by="both",
            recommendation="Investigate overspend in Foundation",
        )
        data = flag.model_dump()
        assert data["severity"] == "high"
        assert data["detected_by"] == "both"

    def test_simple_llm_created(self):
        llm = create_simple_llm()
        assert llm.__class__.__name__ == "ChatOpenAI"

    def test_prompt_template_creation(self):
        prompt = build_chat_prompt()
        assert prompt.__class__.__name__ == "ChatPromptTemplate"

    def test_system_prompt_not_empty(self):
        assert len(SYSTEM_PROMPT) > 100
        assert "ITOTCloud" in SYSTEM_PROMPT

    def test_tools_have_descriptions(self):
        from agent.tools.budget_tools import _make_tools

        mock_ds = MagicMock()
        tools = _make_tools(mock_ds)
        assert len(tools) == 6
        for t in tools:
            assert len(t.description) > 20
