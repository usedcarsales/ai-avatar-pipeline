"""Tests for the master orchestrator — approval gates, cost tracking, job management."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.config import Config
from src.orchestrator import (
    ApprovalRequired,
    CostTracker,
    Job,
    Orchestrator,
)
from src.pipeline import PipelineError


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    return tmp_path / "output"


@pytest.fixture
def config() -> Config:
    return Config(heygen_api_key="hg-test-key", fish_api_key="fish-test-key")


@pytest.fixture
def orchestrator(config: Config, tmp_output: Path) -> Orchestrator:
    return Orchestrator(
        config=config,
        require_approval=True,
        budget_usd=10.0,
        output_dir=str(tmp_output),
    )


class TestCostTracker:
    def test_record_and_total(self, tmp_output: Path) -> None:
        ct = CostTracker(tmp_output / "costs.jsonl")
        ct.record("heygen", "heygen_video")
        ct.record("fish", "fish_tts")
        assert ct.total_usd == pytest.approx(0.52, abs=0.01)

    def test_budget_check(self, tmp_output: Path) -> None:
        ct = CostTracker(tmp_output / "costs.jsonl")
        ct.set_budget(1.0)
        assert ct.check_budget(0.5) is True
        assert ct.check_budget(1.5) is False

    def test_persistence(self, tmp_output: Path) -> None:
        ct = CostTracker(tmp_output / "costs.jsonl")
        ct.record("heygen", "heygen_video", amount=1.23)
        lines = (tmp_output / "costs.jsonl").read_text().strip().split("\n")
        assert len(lines) == 1
        assert '"amount_usd": 1.23' in lines[0]


class TestJobManagement:
    def test_create_job(self, orchestrator: Orchestrator) -> None:
        job = orchestrator.create_job("Hello world", job_id="test1")
        assert job.job_id == "test1"
        assert job.status == "pending"
        assert not job.approved

    def test_approve_job(self, orchestrator: Orchestrator) -> None:
        job = orchestrator.create_job("Hello", job_id="test2")
        orchestrator.approve_job("test2")
        assert job.approved is True
        assert job.status == "approved"

    def test_platform_defaults(self, orchestrator: Orchestrator) -> None:
        job = orchestrator.create_job("Script", platform="tiktok")
        assert job.platform == "tiktok"


class TestApprovalGate:
    @pytest.mark.asyncio
    async def test_unapproved_raises(self, orchestrator: Orchestrator) -> None:
        orchestrator.create_job("Script", job_id="nope")
        with pytest.raises(ApprovalRequired):
            await orchestrator.execute_job("nope")

    @pytest.mark.asyncio
    async def test_no_approval_needed(self, config: Config, tmp_output: Path) -> None:
        orch = Orchestrator(config=config, require_approval=False, output_dir=str(tmp_output))
        orch.create_job("Script", job_id="auto")
        with patch.object(orch.pipeline, "run", new_callable=AsyncMock, return_value=Path("out.mp4")):
            job = await orch.execute_job("auto")
        assert job.status == "done"


class TestBudgetEnforcement:
    @pytest.mark.asyncio
    async def test_over_budget_fails(self, orchestrator: Orchestrator) -> None:
        orchestrator.costs.set_budget(0.01)  # tiny budget
        orchestrator.create_job("Script", job_id="broke")
        orchestrator.approve_job("broke")
        with pytest.raises(PipelineError, match="Budget exceeded"):
            await orchestrator.execute_job("broke")

    @pytest.mark.asyncio
    async def test_within_budget_succeeds(self, orchestrator: Orchestrator) -> None:
        orchestrator.create_job("Script", job_id="ok")
        orchestrator.approve_job("ok")
        with patch.object(orchestrator.pipeline, "run", new_callable=AsyncMock, return_value=Path("out.mp4")):
            job = await orchestrator.execute_job("ok")
        assert job.status == "done"
        assert job.cost_usd > 0


class TestStatusReport:
    def test_get_status(self, orchestrator: Orchestrator) -> None:
        orchestrator.create_job("A", job_id="j1")
        orchestrator.create_job("B", job_id="j2")
        orchestrator.approve_job("j2")
        status = orchestrator.get_status()
        assert status["total_jobs"] == 2
        assert status["by_status"]["pending"] == 1
        assert status["by_status"]["approved"] == 1
        assert status["budget_remaining_usd"] == 10.0
